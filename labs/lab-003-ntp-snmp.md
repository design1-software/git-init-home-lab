# Lab: NTP Hierarchy & SNMP Configuration
# lab-003-ntp-snmp.md
# JLM Home Lab — git-init-home-lab
# Completed: May 21, 2026

---

## Overview

This lab documents the NTP (Network Time Protocol) hierarchy and SNMP (Simple Network Management Protocol) configuration across the JLM home lab infrastructure. Both are CCNA exam topics under Domain 4 — IP Services (10% of exam).

**Devices configured:**
- Cisco C1111-4PWB (JLM-LAB-R1) — NTP master + SNMP server
- Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — NTP client
- Raspberry Pi 4B (jlm-lab-pi) — NTP client
- Acer Server (jmg-server) — NTP client

---

## Part 1 — NTP

### Background

NTP synchronizes clocks across network devices. Accurate time is critical for:
- Log correlation across devices (syslog, SNMP traps)
- Certificate validity checking (SSL/TLS)
- Kerberos authentication (Active Directory — planned Phase D)
- CCNA exam: NTP stratum hierarchy, `ntp master`, `ntp server`, verification commands

### NTP Stratum Model

Stratum indicates how many hops a device is from a reference clock:

| Stratum | Device | Source |
|---|---|---|
| 0 | Atomic/GPS reference clock | Hardware |
| 1 | Google Public NTP (216.239.35.0, 216.239.35.4) | Stratum 0 |
| 2 | C1111 JLM-LAB-R1 | Google NTP |
| 3 | 3560CX JLM-LAB-SW1 | C1111 |
| 3 | Pi 4B jlm-lab-pi | C1111 |
| 3 | Acer jmg-server | C1111 |

Lower stratum = closer to reference clock = more accurate.

---

### Configuration

#### C1111 — NTP Master (Stratum 2)

```
ntp server 216.239.35.0
ntp server 216.239.35.4
ntp master 3
```

**`ntp master 3`** — configures the C1111 as an authoritative NTP source at stratum 3 for internal devices. If upstream Google NTP is unreachable, the C1111 falls back to its local clock at stratum 3 so downstream devices don't lose time sync.

**Note:** `ntp update-calendar` is not supported on the C1111-4PWB — this command requires a hardware calendar chip not present on this model.

#### 3560CX — NTP Client (Stratum 3)

```
ntp server 192.168.10.1
```

Originally configured to sync from Google NTP directly (216.239.35.0). Updated to sync from C1111 to maintain proper hierarchy — C1111 is the single internal time source.

#### Pi 4B — NTP Client (Stratum 3)

Configured via `/etc/systemd/timesyncd.conf`:

```
[Time]
NTP=192.168.10.1
FallbackNTP=216.239.35.0
```

Restart command:
```bash
sudo systemctl restart systemd-timesyncd
```

#### Acer Server (Windows 11) — NTP Client (Stratum 3)

Configured via PowerShell (run as Administrator):

```powershell
w32tm /config /manualpeerlist:"192.168.10.1" /syncfromflags:manual /reliable:YES /update
w32tm /resync
```

---

### Verification

#### C1111 — verify sync status

```
show ntp status
show ntp associations
```

Expected output indicators:
- `Clock is synchronized` — router is synced to upstream
- `stratum 2` — correct position in hierarchy
- `*` next to peer = active sync source
- `+` next to peer = candidate (backup)

Sample output from lab:
```
Clock is unsynchronized, stratum 2, reference is 216.239.35.4
```
Note: "unsynchronized" briefly appears during initial sync — resolves within 5 minutes.

```
show ntp associations

  address         ref clock    st  when  poll reach  delay  offset  disp
+~216.239.35.0   .GOOG.        1     7    64     1  27.000   4.417  188.48
*~216.239.35.4   .GOOG.        1     7    64     1  18.000  -0.479  188.48
 ~127.127.1.1    .LOCL.        2     2    16     1   0.000   0.000  7937.9
```

Key symbols:
- `*` = current sync source
- `+` = candidate peer
- `~` = configured peer
- `.GOOG.` = Google reference clock identifier
- `.LOCL.` = local clock fallback

#### Pi — verify sync

```bash
timedatectl status
timedatectl show-timesync --all | grep ServerName
```

Expected:
```
System clock synchronized: yes
NTP service: active
ServerName=192.168.10.1
```

#### Acer — verify sync

```powershell
w32tm /query /status
```

Expected:
```
Stratum: 3
Source: 192.168.10.1
ReferenceId: 0xC0A80A01
```

`0xC0A80A01` is 192.168.10.1 in hexadecimal — standard Windows time service output format.

---

### CCNA Exam Topics Covered

| Topic | How It Applies |
|---|---|
| NTP stratum hierarchy | 5-level hierarchy built and verified in lab |
| `ntp server` command | Configured on C1111, 3560CX |
| `ntp master` command | C1111 as internal authoritative source |
| `show ntp status` | Verified sync state and stratum |
| `show ntp associations` | Identified active peer vs candidate |
| NTP peer symbols (* + ~) | Observed and explained in live output |
| NTP on Linux clients | systemd-timesyncd configuration |
| NTP on Windows clients | w32tm configuration and verification |

---

## Part 2 — SNMP

### Background

SNMP (Simple Network Management Protocol) allows network management systems to monitor and manage network devices. The C1111 is configured as an SNMP agent. Version 2c is used (community-string based authentication — exam covers v2c and v3).

**CCNA exam:** SNMP components (manager, agent, MIB, OID), versions (v1/v2c/v3), community strings, traps vs polling.

### Current Configuration (C1111)

```
snmp-server community closet-ro RO
snmp-server location JLM-Home-Lab-Closet
snmp-server contact julius
```

**`closet-ro`** — read-only community string (actual value redacted in repo)
**`RO`** — read-only access; no write (RW) community configured — correct for monitoring use case
**`snmp-server location`** — physical location metadata embedded in MIB
**`snmp-server contact`** — admin contact embedded in MIB

### SNMP Architecture in This Lab

```
SNMP Manager (future — Netdata/Wazuh)
    │
    │ UDP 161 (polling) / UDP 162 (traps)
    ▼
SNMP Agent: C1111 JLM-LAB-R1 (192.168.10.1)
    Community: closet-ro (RO)
    MIB: standard IOS XE MIBs
```

### Verification Commands

```
show snmp
show snmp community
show snmp location
show snmp contact
```

### SNMP Versions — CCNA Reference

| Version | Auth | Encryption | Notes |
|---|---|---|---|
| v1 | Community string | None | Legacy, avoid |
| v2c | Community string | None | Most common in labs |
| v3 | Username + auth | Optional (AES/DES) | Enterprise standard |

Current lab uses v2c. SNMPv3 configuration is a Phase 6 hardening task.

### CCNA Exam Topics Covered

| Topic | How It Applies |
|---|---|
| SNMP agent vs manager | C1111 is agent; future monitoring stack is manager |
| Community strings | `closet-ro` RO configured on C1111 |
| Read-only vs read-write | RO only — no write access configured |
| OID / MIB | Standard IOS XE MIBs accessible via community string |
| UDP 161/162 | Polling on 161, traps on 162 |
| SNMPv2c | Version in use; v3 planned for Phase 6 |

---

## Lessons Learned

1. **`ntp update-calendar` is model-specific.** Only works on routers with hardware calendar chips (ISR 4000 series, some older platforms). C1111 does not have a hardware calendar — command fails silently on some IOS versions, returns error on others.

2. **`ntp master` stratum value matters.** Setting `ntp master 3` means the local clock fallback is stratum 3. If you set it to `ntp master 1`, your router claims to be stratum 1 (same as atomic clocks) which is inaccurate and can cause upstream NTP servers to reject your advertisements.

3. **systemd-timesyncd vs ntpd on Linux.** Modern Raspberry Pi OS uses `systemd-timesyncd` by default, not the traditional `ntpd` daemon. Configuration file is `/etc/systemd/timesyncd.conf`. The `timedatectl` command is the primary management interface.

4. **Windows w32tm ReferenceId is hex.** The output `0xC0A80A01` is the NTP source IP in hexadecimal — `C0=192, A8=168, 0A=10, 01=1` → 192.168.10.1. Understanding hex-to-IP conversion is relevant for CCNA.

5. **SNMP community strings are cleartext.** SNMPv2c community strings are transmitted unencrypted. For a production environment, SNMPv3 with auth and encryption is required. The `closet-ro` community string is read-only which limits exposure.

---

*Lab completed: May 21, 2026*
*Devices: C1111 JLM-LAB-R1, 3560CX JLM-LAB-SW1, Pi 4B jlm-lab-pi, Acer jmg-server*
*CCNA domains: Domain 4 — IP Services*
