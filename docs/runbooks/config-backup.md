# Runbook — Cisco Config Backup (Netmiko)

## Purpose

Capture running configs from JLM-LAB-R1 (C1111) and JLM-LAB-SW1 (3560CX) before and after any configuration change. This is the safety net before Phase B cleanup, switch-side VLAN additions, or any other config work.

---

## Devices

| Device | Hostname | SSH IP | Why this IP |
|---|---|---|---|
| Cisco C1111-4PWB | JLM-LAB-R1 | 192.168.199.1 | TRANSIT SVI — 192.168.10.1 is now the 3560CX HSRP VIP |
| Catalyst 3560CX | JLM-LAB-SW1 | 192.168.199.2 | TRANSIT SVI — primary SSH address post-Phase B |

---

## Prerequisites

```bash
pip install netmiko
```

Run from Mac on VLAN 20 (TRUSTED) or any VLAN with routing to 192.168.199.0/30.

---

## Run a Backup (timestamped, no git change)

```bash
cd /path/to/git-init-home-lab
CISCO_PASSWORD=yourpassword python3 scripts/netmiko_backup.py
```

Output lands in `backups/network-configs/`:
```
backups/network-configs/JLM-LAB-R1-20260604-143022.txt
backups/network-configs/JLM-LAB-SW1-20260604-143028.txt
```

These files are gitignored — they are local-only archives.

---

## Capture a Known-Good Snapshot (commit to git)

Use `--update-configs` to also overwrite the committed files in `configs/`:

```bash
CISCO_PASSWORD=yourpassword python3 scripts/netmiko_backup.py --update-configs
```

Then review and commit:

```bash
git diff configs/
git add configs/
git commit -m "configs: capture known-good running config <YYYY-MM-DD>"
```

The `configs/` files are the authoritative committed snapshots. `backups/` holds local timestamped copies for rollback reference.

---

## When to Run

| Trigger | Action |
|---|---|
| Before any config change | Run backup, verify output, then proceed |
| After any config change | Run `--update-configs`, review diff, commit |
| Before Phase B cleanup (C1111 SVI removal) | Mandatory — capture known-good before removing SVIs |
| After 3560CX switch-side VLAN additions | Run `--update-configs`, commit |
| Routine (weekly or before any lab session) | Run timestamped backup, no commit required |

---

## What Gets Captured

`show running-config` from each device. This includes:

- Interfaces and IP assignments
- VLAN database (3560CX)
- Routing config (OSPF, static routes)
- ACLs
- DHCP pools
- HSRP config
- NAT rules (C1111)
- SSH and AAA config
- Spanning tree config

It does NOT include:
- `show startup-config` (NVRAM) — run `write memory` on the device before backup if you want NVRAM to match running
- Interface counters or operational state

---

## Committed Config Files

| File | Device | Last updated |
|---|---|---|
| `configs/cisco-c1111-running.txt` | JLM-LAB-R1 (C1111) | May 21, 2026 — **pre-Phase B, stale** |
| `configs/cisco-3560cx-baseline.txt` | JLM-LAB-SW1 (3560CX) | May 25, 2026 — **pre-Phase B, stale** |

> Both files are significantly stale as of Jun 4, 2026. Run `--update-configs` and commit before any further config changes.

---

## Troubleshooting

**Connection timeout:**
```
[JLM-LAB-R1] TIMEOUT — is 192.168.199.1 reachable?
```
- Confirm you are on a VLAN with routing to 192.168.199.0/30
- Test: `ping 192.168.199.1` and `ping 192.168.199.2`
- SSH test: `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.199.1`

**Authentication failed:**
```
[JLM-LAB-R1] AUTH FAILED — check CISCO_PASSWORD
```
- Verify `CISCO_PASSWORD` is set correctly
- Netmiko uses the same password for login and enable

**Legacy SSH (Netmiko handles this automatically):**
Netmiko uses paramiko, which supports the legacy algorithms IOS XE requires. You do not need to pass `-oKexAlgorithms` when using this script — that is only needed for the OpenSSH CLI client.

---

## Rollback

If a config change breaks connectivity:

1. Open Comet GL-RM1PE console (for ARIA / Proxmox) or physical console (for Cisco)
2. For Cisco: console cable to the device
3. Review the last known-good backup in `backups/network-configs/` or `configs/`
4. Restore via `configure terminal` → paste config sections
5. Run `write memory` after restoring

See also: `docs/runbooks/disaster-recovery.md`
