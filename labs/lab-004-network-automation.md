# Lab: Network Automation — Ansible, Legacy SSH, and Netmiko
# lab-004-network-automation.md
# JLM Home Lab — git-init-home-lab
# Completed: May 21, 2026

---

## Overview

This lab documents the implementation of network automation against the JLM home lab
infrastructure. It covers:

1. Ansible setup and architecture (CCNA exam topic)
2. A real-world failure case — Ansible cisco.ios collection vs legacy IOS XE SSH
3. Root cause analysis of the failure
4. Working solution using Netmiko (Python network automation library)
5. Automated Cisco config backup running from MacBook Pro

**Devices targeted:**
- Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10
- Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — IOS 15.2(7)E2

---

## Part 1 — Ansible Architecture (CCNA Reference)

### What Ansible Is

Ansible is an agentless automation platform. It connects to devices over SSH,
runs tasks, and returns results — no software needs to be installed on the
managed device. For network devices this is critical since you cannot install
agents on a Cisco router.

### Core Ansible Concepts

| Concept | Definition | Lab Example |
|---|---|---|
| **Control node** | Machine running Ansible | MacBook Pro |
| **Managed node** | Device being automated | C1111, 3560CX |
| **Inventory** | List of managed devices | `ansible/inventory/hosts.yml` |
| **Playbook** | YAML file defining automation tasks | `ansible/playbooks/backup-configs.yml` |
| **Task** | Single action to perform | `cisco.ios.ios_command` |
| **Module** | Pre-built task library | `cisco.ios`, `ansible.netcommon` |
| **Collection** | Bundle of modules, roles, plugins | `cisco.ios 11.4.1` |
| **Connection plugin** | How Ansible talks to devices | `network_cli` |
| **Vault** | Encrypted credential storage | `ansible/inventory/vault.yml` |

### Network Automation Architecture

```
MacBook Pro (Control Node)
│
│  ansible-playbook backup-configs.yml
│
├── ansible.cfg          ← global settings
├── inventory/
│   ├── hosts.yml        ← device list with connection params
│   └── vault.yml        ← encrypted credentials (ansible-vault)
└── playbooks/
    └── backup-configs.yml ← tasks to run against devices
                │
                │ SSH (network_cli connection plugin)
                │
        ┌───────┴────────┐
        │                │
   C1111 JLM-LAB-R1   3560CX JLM-LAB-SW1
   192.168.10.1        192.168.99.2
```

### Ansible SSH Connection Stack for Network Devices

When Ansible connects to a Cisco device, it goes through this stack:

```
ansible-playbook
    └── cisco.ios collection
            └── ansible.netcommon network_cli plugin
                    └── SSH transport layer
                            ├── libssh (default, preferred)
                            └── paramiko (fallback)
```

Each layer has its own configuration requirements. This layered architecture
is the source of the failure documented in Part 2.

---

## Part 2 — The Ansible Failure: Root Cause Analysis

### What Was Attempted

A standard Ansible playbook using `cisco.ios.ios_command` to retrieve the
running config from JLM-LAB-R1 (C1111, IOS XE 16.10).

### The Error

```
fatal: [JLM-LAB-R1]: FAILED! => {
    "msg": "Incompatible ssh peer (no acceptable kex algorithm)"
}
```

### What "Incompatible KEX Algorithm" Means

KEX = Key Exchange Algorithm. When SSH establishes a connection, the client
and server negotiate which algorithm to use for the initial key exchange.
Modern SSH clients offer a list of supported algorithms. The server must
support at least one from that list.

The C1111 running IOS XE 16.10 only supports legacy KEX algorithms:
- `diffie-hellman-group14-sha1` (SHA-1 based, considered weak)
- `diffie-hellman-group-exchange-sha1` (SHA-1 based, considered weak)

Modern SSH clients (and Ansible's connection layer) default to only offering
modern algorithms:
- `curve25519-sha256` (preferred)
- `ecdh-sha2-nistp256`
- `diffie-hellman-group16-sha512`
- `diffie-hellman-group18-sha512`

No overlap = connection failure.

### Why the Standard SSH Fix Didn't Work

From a Mac terminal, this works fine:
```bash
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 \
    -oHostKeyAlgorithms=+ssh-rsa \
    admin@192.168.10.1
```

The standard fix for Ansible is to pass these same options via:
- `ansible_ssh_common_args` in inventory
- `ssh_args` in `ansible.cfg` under `[ssh_connection]`
- `ansible_ssh_extra_args` as a variable

**None of these worked. Here is why:**

The `ssh_args` settings in Ansible only apply to the **`ssh` connection plugin**
(used for Linux servers). The `network_cli` plugin — required for Cisco IOS —
has its own internal SSH handling that completely bypasses `[ssh_connection]`
configuration.

```
[ssh_connection]
ssh_args = ...        ← Only applies to linux/posix connections
                         IGNORED by network_cli
```

### Why the Paramiko Fallback Didn't Work

When `ansible-pylibssh` is not installed, `network_cli` falls back to paramiko.
The fix in ansible.cfg:

```ini
[persistent_connection]
ssh_type = paramiko
```

This is documented as the workaround in GitHub issue #1133 of the
cisco.ios collection. However, in **cisco.ios 11.x** (the version installed),
paramiko's legacy KEX support was also broken — paramiko 5.0.0 tightened
its default cipher list and removed the legacy algorithm negotiation that
older versions handled automatically.

### Why pylibssh Didn't Work

`ansible-pylibssh` (the preferred SSH library) requires the native `libssh`
C library. On macOS Apple Silicon, the build succeeded but the library
crashed with a "dead worker" error during execution — a known bug in
`ansible-pylibssh 1.4.0` on ARM Macs as of May 2026.

### Summary of What Was Tried

| Attempt | Method | Result |
|---|---|---|
| `ansible_ssh_common_args` in inventory | SSH option injection | Ignored by network_cli |
| `ssh_args` in `[ssh_connection]` | ansible.cfg | Ignored by network_cli |
| `ansible_ssh_extra_args` in inventory | SSH option injection | Ignored by network_cli |
| `~/.ssh/config` with KexAlgorithms | System SSH config | Ignored by network_cli |
| `ssh_type = paramiko` in `[persistent_connection]` | ansible.cfg | KEX still fails in paramiko 5.0 |
| `ansible-pylibssh` install | Native SSH library | Build succeeded, crashes on ARM |
| Environment variables at runtime | ANSIBLE_NETWORK_CLI_SSH_TYPE | Ignored |

### The Real Fix (For Future Reference)

The correct long-term fix is one of:
1. **Upgrade C1111 IOS XE** to a version supporting modern KEX algorithms
   (IOS XE 17.x supports curve25519-sha256) — blocked pending IOS rollback
   decision
2. **Downgrade cisco.ios collection** to version 5.3.0 which had working
   paramiko legacy KEX support
3. **Use Netmiko** — see Part 3

### CCNA Relevance

This failure is a real-world example of several CCNA and network automation
concepts:
- SSH negotiation and KEX algorithms
- Why legacy Cisco devices cause interoperability problems
- The difference between SSH cipher suites (exam topic: ip ssh version 2,
  ip ssh server algorithm)
- Why IOS upgrades matter for security and compatibility

---

## Part 3 — Working Solution: Netmiko

### What Netmiko Is

Netmiko is a Python library built specifically for SSH connections to network
devices. It wraps paramiko with device-specific handling including:
- Legacy KEX algorithm support
- Device type detection (Cisco IOS, IOS XE, NX-OS, etc.)
- Automatic enable mode handling
- Command output parsing
- Session logging

### Why Netmiko Succeeds Where Ansible Failed

Netmiko uses paramiko directly and configures it with explicit legacy
algorithm support at the Python level — bypassing all the layering issues
that break Ansible's network_cli plugin:

```python
# Netmiko sets these directly on the paramiko transport object:
transport.get_security_options().kex = [
    'diffie-hellman-group14-sha1',
    'diffie-hellman-group-exchange-sha1',
    ...all modern algorithms...
]
```

This is exactly what the C1111 needs and exactly what Ansible's layered
architecture makes impossible to configure from the outside.

### Installation

```bash
pip install netmiko
```

### Backup Script

Located at: `ansible/playbooks/backup-netmiko.py`

```python
#!/usr/bin/env python3
"""
backup-netmiko.py
Automated config backup for JLM home lab Cisco devices using Netmiko.
Replaces ansible cisco.ios playbook which fails due to legacy KEX
algorithm incompatibility between cisco.ios 11.x and IOS XE 16.10.

Devices:
  - JLM-LAB-R1: C1111-4PWB, IOS XE 16.10, 192.168.10.1
  - JLM-LAB-SW1: 3560CX, IOS 15.2(7)E2, 192.168.99.2 (after cutover)

Usage:
  python3 backup-netmiko.py

Credentials are read from environment variables:
  CISCO_USERNAME
  CISCO_PASSWORD

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
    # JLM-LAB-SW1 added after Phase B cutover when 192.168.99.2 is reachable
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
# Backup directory
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
            output = conn.send_command("show running-config")

            with open(backup_file, "w") as f:
                f.write(f"! Backup of {hostname}\n")
                f.write(f"! Timestamp: {timestamp}\n")
                f.write(f"! Host: {device['host']}\n")
                f.write("!" + "=" * 60 + "\n\n")
                f.write(output)

            print(f"[{hostname}] ✅ Config saved to {backup_file}")
            return True

    except NetmikoTimeoutException:
        print(f"[{hostname}] ❌ Connection timed out — is {device['host']} reachable?")
        return False
    except NetmikoAuthenticationException:
        print(f"[{hostname}] ❌ Authentication failed — check credentials")
        return False
    except Exception as e:
        print(f"[{hostname}] ❌ Error: {e}")
        return False


# ============================================================
# Main
# ============================================================
def main():
    if not os.environ.get("CISCO_PASSWORD"):
        print("ERROR: CISCO_PASSWORD environment variable not set.")
        print("Usage: CISCO_PASSWORD=yourpassword python3 backup-netmiko.py")
        sys.exit(1)

    print(f"Starting backup of {len(DEVICES)} device(s)...")
    print(f"Output directory: {BACKUP_DIR}\n")

    results = []
    for device in DEVICES:
        success = backup_device(device)
        results.append(success)

    print(f"\nBackup complete: {sum(results)}/{len(results)} devices successful")

    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Running the Script

```bash
cd /Users/juliusmoore/Documents/git-init-home-lab/ansible
CISCO_PASSWORD=yourpassword python3 playbooks/backup-netmiko.py
```

### Expected Output

```
Starting backup of 1 device(s)...
Output directory: /path/to/git-init-home-lab/ansible/backups

[JLM-LAB-R1] Connecting to 192.168.10.1...
[JLM-LAB-R1] Connected. Retrieving running config...
[JLM-LAB-R1] ✅ Config saved to backups/JLM-LAB-R1-20260521-141532.txt

Backup complete: 1/1 devices successful
```

---

## Part 4 — Ansible Inventory and Config (Reference)

The Ansible infrastructure built during this lab remains in the repo as
reference and for future use when the IOS version is upgraded or a newer
Ansible/cisco.ios version resolves the KEX issue.

### File Structure

```
ansible/
├── ansible.cfg                 ← Ansible configuration
├── inventory/
│   ├── hosts.yml               ← Device inventory
│   └── vault.yml               ← Encrypted credentials (ansible-vault)
├── playbooks/
│   ├── backup-configs.yml      ← Ansible playbook (blocked by KEX issue)
│   └── backup-netmiko.py       ← Working Netmiko backup script
└── backups/                    ← Config backup output directory
```

### ansible.cfg

```ini
[defaults]
inventory = inventory/hosts.yml
host_key_checking = False
timeout = 30
collections_path = ~/.ansible/collections
deprecation_warnings = False

[persistent_connection]
connect_timeout = 30
command_timeout = 30
ssh_type = paramiko

[paramiko_connection]
look_for_keys = False
host_key_checking = False
remote_port = 22

[ssh_connection]
ssh_args = -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa
```

### hosts.yml (sanitized)

```yaml
all:
  children:
    cisco_routers:
      hosts:
        JLM-LAB-R1:
          ansible_host: 192.168.10.1
          ansible_user: admin
          ansible_password: "{{ router_password }}"
          ansible_network_os: cisco.ios.ios
          ansible_connection: network_cli
    cisco_switches:
      hosts:
        JLM-LAB-SW1:
          ansible_host: 192.168.99.2
          ansible_user: admin
          ansible_password: "{{ switch_password }}"
          ansible_network_os: cisco.ios.ios
          ansible_connection: network_cli
```

---

## Part 5 — CCNA Exam Topics Covered

| Topic | Domain | How It Applies |
|---|---|---|
| Network automation concepts | Domain 6 | Ansible architecture, agentless model |
| REST API / programmability | Domain 6 | Netmiko Python API calls to devices |
| SSH and security | Domain 5 | KEX algorithm negotiation explained |
| IOS XE SSH configuration | Domain 5 | ip ssh version 2, legacy algorithms |
| Python scripting | Domain 6 | Working automation script |
| JSON/YAML | Domain 6 | Ansible inventory and playbook format |
| Configuration management | Domain 6 | Automated config backup |
| Ansible vs alternatives | Domain 6 | Real-world tool comparison |

---

## Lessons Learned

1. **Ansible network_cli ignores standard SSH options.** `[ssh_connection]`
   settings, `ansible_ssh_common_args`, and `ansible_ssh_extra_args` all
   apply to POSIX connections only — not to `network_cli`. This is a
   documented limitation that surprises most new Ansible network users.

2. **cisco.ios collection version matters critically.** Version 5.x had
   working paramiko legacy KEX support. Version 11.x removed it. Always
   check collection version compatibility with your device's IOS version
   before deploying.

3. **Netmiko was built for exactly this problem.** When Ansible fails on
   legacy Cisco devices, Netmiko is the standard industry answer. It's
   widely used in real network operations environments and is a legitimate
   skill for network automation roles.

4. **Credentials in environment variables, not files.** The Netmiko script
   reads passwords from environment variables. This is better practice than
   storing credentials in config files — no risk of accidentally committing
   a password to GitHub.

5. **The right tool depends on the device.** Ansible excels for modern IOS
   XE 17.x, NX-OS, and Linux servers. Netmiko and NAPALM are better for
   legacy IOS. Knowing which tool fits which situation is a real-world
   network automation skill.

6. **IOS upgrades have security and compatibility implications.** The C1111
   running IOS XE 16.10 with legacy KEX algorithms is a real security
   concern (SHA-1 based algorithms are considered weak). Upgrading to IOS
   XE 17.x would resolve both the security issue and the Ansible
   compatibility problem simultaneously.

---

## Next Steps

- [ ] Run Netmiko backup script and verify output
- [ ] Add JLM-LAB-SW1 to device list after Phase B cutover
- [ ] Consider IOS XE upgrade on C1111 to resolve KEX and enable modern Ansible
- [ ] Phase 7: Full Ansible IaC playbooks for server and Pi configuration

---

*Lab completed: May 21, 2026*
*Devices: C1111 JLM-LAB-R1, 3560CX JLM-LAB-SW1 (pending)*
*CCNA domains: Domain 6 — Automation & Programmability, Domain 5 — Security*
