#!/usr/bin/env python3
"""
netmiko_backup.py
Automated running-config backup for JLM home lab Cisco devices.

Devices:
  JLM-LAB-R1  — C1111-4PWB at 192.168.199.1 (TRANSIT SVI, post-Phase B)
  JLM-LAB-SW1 — 3560CX at 192.168.199.2 (TRANSIT SVI, post-Phase B)

NOTE: 192.168.10.1 is now the 3560CX HSRP VIP. Do not use it for SSH.
      Reach C1111 at 192.168.199.1, 3560CX at 192.168.199.2.

Output:
  backups/network-configs/<HOSTNAME>-<YYYYMMDD-HHMMSS>.txt  (timestamped)
  configs/<filename>.txt                                      (--update-configs)

Usage — per-device credentials (recommended):
  R1_PASSWORD='mypassword' SW1_PASSWORD='otherpass' python3 scripts/netmiko_backup.py
  R1_PASSWORD='mypassword' SW1_PASSWORD='otherpass' python3 scripts/netmiko_backup.py --update-configs

Usage — same password for both devices:
  CISCO_PASSWORD='mypassword' python3 scripts/netmiko_backup.py

IMPORTANT — special characters in passwords:
  Always use single quotes around passwords in the shell.
  Single quotes prevent bash from interpreting !, $, &, etc.
  Example: R1_PASSWORD='p@ss!w0rd#'    (correct)
           R1_PASSWORD=p@ss!w0rd#       (WRONG — shell will mangle it)

Environment variables:
  R1_USERNAME    login username for C1111     (default: admin)
  R1_PASSWORD    login + enable for C1111     (required if SW1_PASSWORD not covering both)
  SW1_USERNAME   login username for 3560CX    (default: admin)
  SW1_PASSWORD   login + enable for 3560CX    (required if R1_PASSWORD not covering both)
  CISCO_USERNAME  fallback username            (default: admin)
  CISCO_PASSWORD  fallback password            (used if per-device vars not set)

--update-configs:
  After a successful backup, overwrites configs/cisco-c1111-running.txt
  and configs/cisco-3560cx-baseline.txt with the latest output.
  Commit those files to capture a known-good snapshot in git.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# ── Repo root (two levels up from scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = REPO_ROOT / "backups" / "network-configs"
CONFIGS_DIR = REPO_ROOT / "configs"

# ── Per-device credential resolution
# Per-device vars take precedence; fall back to shared CISCO_* vars.
_fallback_user = os.environ.get("CISCO_USERNAME", "admin")
_fallback_pass = os.environ.get("CISCO_PASSWORD", "")

DEVICES = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.199.1",
        "username": os.environ.get("R1_USERNAME", _fallback_user),
        "password": os.environ.get("R1_PASSWORD", _fallback_pass),
        "secret":   os.environ.get("R1_PASSWORD", _fallback_pass),
        "hostname": "JLM-LAB-R1",
        "configs_file": "cisco-c1111-running.txt",
    },
    {
        "device_type": "cisco_ios",
        "host": "192.168.199.2",
        "username": os.environ.get("SW1_USERNAME", _fallback_user),
        "password": os.environ.get("SW1_PASSWORD", _fallback_pass),
        "secret":   os.environ.get("SW1_PASSWORD", _fallback_pass),
        "hostname": "JLM-LAB-SW1",
        "configs_file": "cisco-3560cx-baseline.txt",
    },
]


def backup_device(device: dict, update_configs: bool) -> tuple[bool, Path | None]:
    hostname = device["hostname"]
    configs_file = device["configs_file"]
    conn_args = {k: v for k, v in device.items()
                 if k not in ("hostname", "configs_file")}

    if not conn_args.get("password"):
        print(f"[{hostname}] SKIPPED — no password set")
        return False, None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"{hostname}-{timestamp}.txt"

    print(f"[{hostname}] Connecting to {conn_args['host']} ...")

    try:
        with ConnectHandler(**conn_args) as conn:
            conn.enable()
            print(f"[{hostname}] Connected. Pulling running-config ...")
            output = conn.send_command("show running-config", read_timeout=60)

        header = (
            f"! Backup: {hostname}\n"
            f"! Host:   {conn_args['host']}\n"
            f"! Time:   {timestamp}\n"
            f"! {'=' * 58}\n\n"
        )
        full = header + output

        backup_file.write_text(full)
        print(f"[{hostname}] Saved → {backup_file.relative_to(REPO_ROOT)}")

        if update_configs:
            dest = CONFIGS_DIR / configs_file
            dest.write_text(full)
            print(f"[{hostname}] Updated → {dest.relative_to(REPO_ROOT)}")

        return True, backup_file

    except NetmikoTimeoutException:
        print(f"[{hostname}] TIMEOUT — is {conn_args['host']} reachable?")
        return False, None
    except NetmikoAuthenticationException:
        print(f"[{hostname}] AUTH FAILED — check password for this device")
        return False, None
    except Exception as e:
        print(f"[{hostname}] ERROR — {e}")
        return False, None


def main():
    parser = argparse.ArgumentParser(description="JLM home lab Cisco config backup")
    parser.add_argument(
        "--update-configs",
        action="store_true",
        help="Also overwrite configs/ snapshots (commit those to git)",
    )
    args = parser.parse_args()

    # Require at least one credential to be set
    has_r1  = bool(os.environ.get("R1_PASSWORD")  or os.environ.get("CISCO_PASSWORD"))
    has_sw1 = bool(os.environ.get("SW1_PASSWORD") or os.environ.get("CISCO_PASSWORD"))
    if not (has_r1 or has_sw1):
        print("ERROR: No passwords set.")
        print()
        print("Per-device (recommended):")
        print("  R1_PASSWORD='pass1' SW1_PASSWORD='pass2' python3 scripts/netmiko_backup.py")
        print()
        print("Same password for both:")
        print("  CISCO_PASSWORD='pass' python3 scripts/netmiko_backup.py")
        print()
        print("Always use single quotes — prevents shell from mangling special characters.")
        sys.exit(1)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    print("JLM Home Lab — Cisco Config Backup")
    print(f"Devices : {len(DEVICES)}")
    print(f"Output  : backups/network-configs/")
    if args.update_configs:
        print("Configs : will update configs/ snapshots")
    print()

    results = []
    for device in DEVICES:
        ok, _ = backup_device(device, args.update_configs)
        results.append(ok)

    succeeded = sum(results)
    total = len(results)
    print(f"\nDone: {succeeded}/{total} devices backed up successfully.")

    if args.update_configs and succeeded > 0:
        print("\nNext step: review configs/ and commit if the output looks correct:")
        print("  git diff configs/")
        print("  git add configs/")
        print('  git commit -m "configs: capture known-good running config <date>"')

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
