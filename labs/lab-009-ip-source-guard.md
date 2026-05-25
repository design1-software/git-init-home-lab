# Lab: IP Source Guard — Layer 2 Source Address Validation

# lab-009-ip-source-guard.md

# JLM Home Lab — git-init-home-lab

# Completed: May 25, 2026

-----

## Overview

This lab documents the configuration of IP Source Guard on the JLM
home lab Catalyst 3560CX-8PC-S switch. IP Source Guard is a Layer 2
security feature that validates source IP addresses against the DHCP
snooping binding table, preventing IP address spoofing attacks on
access ports.

**CCNA Domain:** Domain 5 — Security Fundamentals (15% of exam)

**Device:** Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — IOS 15.2(7)E2

**Status:** Configured offline — switch is pre-staged, not yet in
production. IP Source Guard will activate automatically at Phase B
cutover when devices connect and obtain DHCP leases.

**Prerequisites:**

- DHCP snooping enabled on VLANs 30,31,40,50,60 (lab completed May 19, 2026)
- DAI (Dynamic ARP Inspection) enabled on same VLANs (lab completed May 19, 2026)
- IP Source Guard requires DHCP snooping to be active — it validates
  packets against the snooping binding table

-----

## Part 1 — What IP Source Guard Does

### The Problem It Solves

Without IP Source Guard, any device on an access port can configure
any source IP address it wants — bypassing DHCP and potentially:

- Spoofing another device’s IP to intercept traffic
- Evading ACLs that are based on source IP
- Causing IP address conflicts that disrupt legitimate devices
- Performing man-in-the-middle attacks by claiming a trusted device’s IP

**Example attack scenario without IP Source Guard:**

```
Legitimate Ring camera → DHCP → assigned 192.168.30.11
Attacker IoT device   → manually sets static IP 192.168.30.11
                      → pretends to be the Ring camera
                      → intercepts traffic meant for Ring camera
                      → ACLs based on 192.168.30.11 now trust attacker
```

### How IP Source Guard Stops It

IP Source Guard intercepts every packet on an untrusted access port
and validates the source IP against the DHCP snooping binding table:

```
Device sends packet with src IP 192.168.30.11
    │
    ▼
IP Source Guard checks binding table:
  192.168.30.11 → MAC aa:bb:cc:dd:ee:ff → Gi0/5 → VLAN 30
    │
    ├── Source IP matches binding AND source MAC matches → FORWARD ✅
    └── Source IP doesn't match binding OR wrong MAC    → DROP ❌
```

If a device manually sets a static IP that doesn’t match a valid DHCP
lease in the binding table — the packet is dropped silently.

### IP Source Guard + DHCP Snooping + DAI — The Layer 2 Security Stack

These three features work together as a complete Layer 2 security stack:

|Feature               |What It Validates         |Protects Against      |
|----------------------|--------------------------|----------------------|
|DHCP Snooping         |DHCP server legitimacy    |Rogue DHCP servers    |
|Dynamic ARP Inspection|ARP packet correctness    |ARP spoofing/poisoning|
|IP Source Guard       |Source IP + MAC per packet|IP address spoofing   |

All three are configured on the 3560CX on the same VLANs (30, 31,
40, 50, 60). Each layer adds an additional validation that the previous
layer doesn’t cover.

-----

## Part 2 — How IP Source Guard Works with DHCP Snooping

### The Dependency Chain

```
Device requests DHCP
    │
    ▼
DHCP Snooping intercepts and validates DHCP transaction
    │
    ▼
DHCP lease granted → Snooping binding table updated:
  IP: 192.168.30.11
  MAC: aa:bb:cc:dd:ee:ff
  Port: Gi0/5
  VLAN: 30
  Lease: 7 days
    │
    ▼
IP Source Guard uses binding table to validate all subsequent traffic
  from Gi0/5 — only 192.168.30.11 from aa:bb:cc:dd:ee:ff allowed
```

Without a DHCP snooping binding entry, IP Source Guard blocks ALL
traffic from that port (except DHCP discovery packets, which are
allowed through to obtain a lease).

### Filter Modes

IP Source Guard supports two filter modes:

|Mode    |Command                         |What It Validates        |
|--------|--------------------------------|-------------------------|
|IP only |`ip verify source`              |Source IP address only   |
|IP + MAC|`ip verify source port-security`|Source IP AND MAC address|

**This lab uses IP-only mode** (`ip verify source`) which is the
standard configuration. IP + MAC mode requires port security to also
be configured and is more complex to manage.

-----

## Part 3 — Pre-Configuration State

### Baseline (before IP Source Guard)

```
JLM-LAB-SW1#show ip verify source
Interface  Filter-type  Filter-mode  IP-address  Mac-address  Vlan  Log
---------  -----------  -----------  ----------  -----------  ----  ---
(empty — no IP Source Guard configured)

JLM-LAB-SW1#show ip dhcp snooping binding
MacAddress          IpAddress   Lease(sec)  Type  VLAN  Interface
------------------  ----------  ----------  ----  ----  ---------
Total number of bindings: 0
```

DHCP snooping was already configured from the previous lab session
(May 19, 2026) but the binding table is empty — correct since the
switch is not yet in production and no devices have connected.

-----

## Part 4 — Configuration

### Ports Configured

IP Source Guard is applied to **access ports only** — the ports where
end devices connect. Trunk ports (Gi0/1, Gi0/2, Gi0/3) and the
Proxmox server port (Gi0/4) are excluded because:

- Trunk ports carry tagged traffic from multiple VLANs and multiple
  legitimate sources — IP Source Guard would block all of it
- Proxmox server will have a static IP, not DHCP — handled differently
  (static binding or exemption)

```
interface GigabitEthernet0/5
 ip verify source

interface GigabitEthernet0/6
 ip verify source

interface GigabitEthernet0/7
 ip verify source

interface GigabitEthernet0/8
 ip verify source
```

One command per access port. IP Source Guard piggybacks entirely on
the existing DHCP snooping infrastructure — no additional database
or configuration required.

-----

## Part 5 — Verification (Live Output — May 25, 2026)

### show ip verify source

```
JLM-LAB-SW1#show ip verify source
Interface  Filter-type  Filter-mode          IP-address  Mac-address  Vlan  Log
---------  -----------  -----------          ----------  -----------  ----  ---
Gi0/5      ip           inactive-no-snooping-vlan
Gi0/6      ip           inactive-no-snooping-vlan
Gi0/7      ip           inactive-no-snooping-vlan
Gi0/8      ip           inactive-no-snooping-vlan
```

**Filter-type: ip** — IP-only validation mode (not IP+MAC) ✅

**Filter-mode: inactive-no-snooping-vlan** — this is the correct
offline state. It means:

- IP Source Guard is configured ✅
- DHCP snooping is enabled but has no active bindings on these ports ✅
- IP Source Guard is waiting for devices to connect and get DHCP leases ✅
- Will activate automatically when binding table populates ✅

This is not an error. It is the expected state for a pre-staged switch
with no connected devices.

-----

## Part 6 — Expected State at Phase B

When the 3560CX is cabled into production and devices connect:

### Step 1 — Device connects and gets DHCP lease

```
Device plugs into Gi0/5
    └── DHCP request → DHCP snooping validates → lease granted
        → Binding table: 192.168.30.11 / aa:bb:cc / Gi0/5 / VLAN 30
```

### Step 2 — IP Source Guard activates automatically

```
JLM-LAB-SW1#show ip verify source
Interface  Filter-type  Filter-mode  IP-address      Mac-address  Vlan
---------  -----------  -----------  --------------- -----------  ----
Gi0/5      ip           active       192.168.30.11   ---          30
```

Filter-mode changes from `inactive-no-snooping-vlan` to `active` ✅

### Step 3 — Attack attempt is blocked

```
Attacker manually sets IP 192.168.30.15 on a device connected to Gi0/5
    └── Packet arrives at Gi0/5 with src IP 192.168.30.15
        └── IP Source Guard checks binding table
            └── Gi0/5 binding = 192.168.30.11, not 192.168.30.15
                └── PACKET DROPPED ✅
```

### Proxmox Server (Gi0/4) — Static IP Handling

The Proxmox server will use a static IP (192.168.70.x), not DHCP.
IP Source Guard is not configured on Gi0/4, so static IPs are allowed
on that port. If IP Source Guard were needed on Gi0/4, a static binding
would be added:

```
ip source binding <MAC> vlan 70 <IP> interface GigabitEthernet0/4
```

This manually adds a binding entry without requiring DHCP.

-----

## Part 7 — Complete Layer 2 Security Stack Summary

All three features are now configured on the 3560CX:

```
JLM-LAB-SW1 — Layer 2 Security Stack (VLANs 30,31,40,50,60)

┌─────────────────────────────────────────────────────┐
│  DHCP Snooping                                      │
│  Validates DHCP servers — only trusted ports        │
│  (Gi0/2, Gi0/3, Gi0/4) can respond to DHCP         │
│  Builds binding table: IP+MAC+Port+VLAN             │
├─────────────────────────────────────────────────────┤
│  Dynamic ARP Inspection                             │
│  Validates ARP packets against binding table        │
│  Prevents ARP spoofing/poisoning attacks            │
├─────────────────────────────────────────────────────┤
│  IP Source Guard                                    │
│  Validates source IP per packet against binding     │
│  Prevents IP address spoofing on access ports       │
│  Configured on: Gi0/5, Gi0/6, Gi0/7, Gi0/8         │
└─────────────────────────────────────────────────────┘
```

Each layer addresses a different attack vector. Together they make
the IoT and guest VLANs significantly more resistant to Layer 2
attacks from compromised devices.

-----

## Part 8 — CCNA Exam Topics Covered

|Topic                       |Coverage                                    |
|----------------------------|--------------------------------------------|
|IP Source Guard purpose     |IP spoofing prevention                      |
|DHCP snooping dependency    |Binding table relationship explained        |
|`ip verify source` command  |Configured on Gi0/5-Gi0/8                   |
|IP-only vs IP+MAC modes     |Both documented                             |
|Filter-mode states          |inactive vs active explained                |
|Layer 2 security stack      |DHCP snooping + DAI + IP Source Guard       |
|Static IP exception handling|`ip source binding` documented              |
|Trusted vs untrusted ports  |Trunk ports excluded, access ports protected|

-----

## Phase B Verification Checklist

- [ ] Verify `show ip verify source` shows `active` on ports with connected devices
- [ ] Verify legitimate DHCP devices pass traffic normally
- [ ] Test static IP rejection — connect a device with manual IP, confirm drop
- [ ] Add static binding for Proxmox server if IP Source Guard needed on Gi0/4
- [ ] Document binding table entries in `show ip dhcp snooping binding`

-----

## Lessons Learned

1. **IP Source Guard requires DHCP snooping to be active first.**
   Without snooping, there is no binding table to validate against.
   The `inactive-no-snooping-vlan` status means snooping is enabled
   but has no bindings yet — not that snooping is missing.
1. **Never apply IP Source Guard to trunk ports.** Trunk ports carry
   traffic from many legitimate sources. IP Source Guard on a trunk
   would drop all traffic that doesn’t match a binding entry.
1. **Static IP devices need manual binding entries.** Devices with
   static IPs never get a DHCP lease, so they never appear in the
   snooping binding table. Either exclude their port from IP Source
   Guard or add a manual `ip source binding` entry.
1. **IP Source Guard activates automatically** when the binding table
   populates. No additional commands needed at Phase B — the feature
   is fully pre-staged.
1. **The Layer 2 security stack (snooping + DAI + IP Source Guard)
   is a CCNA exam topic cluster.** Understanding how all three work
   together and depend on each other is more valuable than knowing
   each in isolation.

-----

*Lab completed: May 25, 2026*
*Device: Catalyst 3560CX-8PC-S JLM-LAB-SW1, IOS 15.2(7)E2*
*Status: Pre-staged offline, activates automatically at Phase B*
*CCNA domain: Domain 5 — Security Fundamentals*