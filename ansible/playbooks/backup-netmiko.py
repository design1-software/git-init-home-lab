#!/usr/bin/env python3
"""
backup-netmiko.py
Automated config backup for JLM home lab Cisco devices using Netmiko.

Replaces ansible cisco.ios playbook which fails due to legacy KEX
algorithm incompatibility between cisco.ios 11.x and IOS XE 16.10.

Devices:
  - JLM-LAB-R1: C1111-4PWB, IOS XE 16.10, 192.168.10.1
  - JLM-LAB-SW1: 3560CX, IOS 15.2(7)E2, 192.168.99.2 (after Phase B cutover)

Usage:
  CISCO_PASSWORD=yourpassword python3 backup-netmiko.py

Credentials are read from environment variables:
  CISCO_USERNAME  (default: admin)
  CISCO_PASSWORD  (required)

Output:
  ../backups/<hostname>-<timestamp>.txt
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException


# ============================================================
# Device definitions
# ============================================================
DEVICES = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.10.1",
        "username": os.environ.get("CISCO_USERNAME", "admin"),
        "password": os.environ.get("CISCO_PASSWORD"),
        "secret": os.environ.get("CISCO_PASSWORD"),
        "hostname": "JLM-LAB-R1",
    },
    # Uncomment after Phase B cutover when 3560CX is in production
    # {
    #     "device_type": "cisco_ios",
    #     "host": "192.168.99.2",
    #     "username": os.environ.get("CISCO_USERNAME", "admin"),
    #     "password": os.environ.get("CISCO_PASSWORD"),
    #     "secret": os.environ.get("CISCO_PASSWORD"),
    #     "hostname": "JLM-LAB-SW1",
    # },
]


# ============================================================
# Backup directory — relative to this script's location
# ============================================================
BACKUP_DIR = Path(__file__).parent.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


# ============================================================
# Backup function
# ============================================================
def backup_device(device: dict) -> bool:
    """Connect to a device and save its running config."""
    hostname = device.pop("hostname")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_file = BACKUP_DIR / f"{hostname}-{timestamp}.txt"

    print(f"[{hostname}] Connecting to {device['host']}...")

    try:
        with ConnectHandler(**device) as conn:
            print(f"[{hostname}] Connected. Retrieving running config...")
            output = conn.send_command(
                "show running-config",
                read_timeout=60
            )

            with open(backup_file, "w") as f:
                f.write(f"! Backup of {hostname}\n")
                f.write(f"! Timestamp: {timestamp}\n")
                f.write(f"! Host: {device['host']}\n")
                f.write("!" + "=" * 60 + "\n\n")
                f.write(output)

            print(f"[{hostname}] Config saved to {backup_file}")
            return True

    except NetmikoTimeoutException:
        print(f"[{hostname}] Connection timed out — is {device['host']} reachable?")
        return False
    except NetmikoAuthenticationException:
        print(f"[{hostname}] Authentication failed — check credentials")
        return False
    except Exception as e:
        print(f"[{hostname}] Error: {e}")
        return False


# ============================================================
# Main
# ============================================================
def main():
    if not os.environ.get("CISCO_PASSWORD"):
        print("ERROR: CISCO_PASSWORD environment variable not set.")
        print("Usage: CISCO_PASSWORD=yourpassword python3 backup-netmiko.py")
        sys.exit(1)

    print(f"JLM Home Lab — Cisco Config Backup")
    print(f"Devices: {len(DEVICES)}")
    print(f"Output:  {BACKUP_DIR}\n")

    results = []
    for device in DEVICES:
        success = backup_device(device)
        results.append(success)

    print(f"\nBackup complete: {sum(results)}/{len(results)} devices successful")

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
