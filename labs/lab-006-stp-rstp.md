# Lab: Spanning Tree Protocol — STP & RSTP
# lab-006-stp-rstp.md
# JLM Home Lab — git-init-home-lab
# Documented: May 21, 2026

---

## Overview

This lab documents Spanning Tree Protocol (STP) and Rapid Spanning Tree
Protocol (RSTP) as configured and observed on JLM home lab hardware.

**Current lab state:** Both the C1111 and 3560CX are running Rapid-PVST
but show no active STP instances — correct behavior for a topology with
no redundant Layer 2 paths. Full STP adjacency will be observable at
Phase B cutover when the 3560CX is cabled into production alongside the
C1111 and Netgear switches.

**CCNA Domain:** Domain 2 — Network Access (20% of exam)

**Devices:**
- Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10
- Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — IOS 15.2(7)E2

---

## Part 1 — Why STP Exists

### The Layer 2 Loop Problem

Ethernet networks have no TTL (Time To Live) field in the frame header
— unlike IP packets which expire after a set number of hops, Ethernet
frames can loop forever. In a network with redundant switch paths, a
broadcast frame (like a DHCP request or ARP) can enter an infinite loop:

```
Switch A → Switch B → Switch C → Switch A → Switch B → Switch C → ...
```

This causes a **broadcast storm** — CPU utilization on all switches
reaches 100%, the network becomes unusable, and the loop must be broken
manually by unplugging cables.

### STP Solution

STP (IEEE 802.1D) automatically detects redundant paths and logically
blocks one path to eliminate loops — while keeping it available as a
backup if the primary path fails.

```
Switch A ──── Switch B
    │               │
    └──── Switch C ─┘

Without STP: loop exists, broadcast storm possible
With STP:    one port blocked, loop eliminated, redundancy preserved
```

---

## Part 2 — STP Versions

| Version | Standard | Convergence | Notes |
|---|---|---|---|
| STP | IEEE 802.1D (1998) | 30–50 seconds | Original, obsolete |
| RSTP | IEEE 802.1w (2001) | 1–6 seconds | Faster convergence |
| PVST+ | Cisco proprietary | 30–50 seconds | Per-VLAN STP (one instance per VLAN) |
| Rapid-PVST+ | Cisco proprietary | 1–6 seconds | Per-VLAN RSTP — **current lab config** |
| MSTP | IEEE 802.1s | 1–6 seconds | Multiple VLANs per instance |

**JLM lab uses Rapid-PVST+** — the current Cisco recommended default.
This means one independent STP instance runs per VLAN, each with its own
root bridge election and port roles.

---

## Part 3 — STP Key Concepts

### Bridge ID

Every switch has a unique Bridge ID consisting of:
```
Bridge ID = Priority (2 bytes) + MAC Address (6 bytes)
```

Default priority is **32768**. With Extended System ID enabled (as in
this lab), the VLAN ID is added to the priority:
```
Bridge ID = Priority + VLAN ID + MAC Address
Example:   32768 + 10 + AC:4A:56:80:87:00 = 32778 for VLAN 10
```

### Root Bridge Election

The switch with the **lowest Bridge ID** becomes the root bridge for
that VLAN. Since priority is the most significant part of the Bridge ID,
the switch with the lowest priority wins. If priorities are equal, the
lowest MAC address wins.

**To control root bridge placement** (always do this in a real network):
```
spanning-tree vlan 10 priority 4096    ← makes this switch root for VLAN 10
spanning-tree vlan 10 root primary     ← shortcut command, sets priority to 24576
```

### Port Roles (RSTP)

| Role | Description |
|---|---|
| **Root Port** | Best path toward the root bridge (one per non-root switch) |
| **Designated Port** | Best port on each segment (forwards traffic) |
| **Alternate Port** | Backup path to root (replaces blocked port in legacy STP) |
| **Backup Port** | Backup to a designated port on same segment |

### Port States (RSTP)

| State | Forwards Data? | Learns MACs? | Description |
|---|---|---|---|
| **Discarding** | No | No | Blocking or listening equivalent |
| **Learning** | No | Yes | Building MAC table |
| **Forwarding** | Yes | Yes | Normal operation |

RSTP reduced legacy STP's 5 states (Disabled, Blocking, Listening,
Learning, Forwarding) to 3 states by combining Disabled/Blocking/
Listening into Discarding.

### Convergence

Legacy STP convergence = **30–50 seconds** (15s listening + 15s learning)
RSTP convergence = **1–6 seconds** via proposal/agreement mechanism

This is why Rapid-PVST+ replaced PVST+ — a 30-second outage every time
a link flapped was unacceptable in modern networks.

---

## Part 4 — Current Lab State

### Verified Configuration (May 21, 2026)

#### C1111 JLM-LAB-R1
```
show spanning-tree summary

Switch is in rapid-pvst mode
Root bridge for: none
Extended system ID: enabled
Bridge Assurance:   enabled
Portfast Default:   disabled
Total STP instances: 0 (no active instances)
```

#### 3560CX JLM-LAB-SW1
```
show spanning-tree summary

Switch is in rapid-pvst mode
Root bridge for: none
Extended system ID: enabled
Bridge Assurance:   enabled
Portfast Default:   disabled
Total STP instances: 0 (no active instances)
```

### Why No STP Instances Exist

**STP instances only form when VLANs have active Layer 2 ports.**

Current topology has a single uplink path from each device — there are
no redundant Layer 2 links, therefore no loops to prevent. STP has
nothing to do.

```
C1111 (JLM-LAB-R1)
    │
    │ single trunk uplink
    │
GS308EP ──── GS316EP
    │
UniFi APs
```

With only one path between any two switches, even if STP were disabled,
no broadcast storm could occur. STP is configured and ready — it just
has no work to do.

**This changes at Phase B cutover** when the 3560CX is added as L3 core
with uplinks to both the C1111 (TRANSIT) and GS308EP. At that point
STP instances will form for each active VLAN.

### Why the C1111 Shows No STP Instances

The C1111-4PWB is an ISR router with an integrated Layer 2 switch module
(ports GE0/1/0 through GE0/1/3). STP runs on these switchport interfaces,
but STP instances only form when redundant paths exist. Since each VLAN
has only one path through the C1111's switch module to the GS308EP,
STP has no loops to prevent.

---

## Part 5 — Expected STP State After Phase B Cutover

When the 3560CX is cabled into production as L3 core, the topology
becomes:

```
C1111 (JLM-LAB-R1)
    │ TRANSIT (L3 routed — not subject to STP)
    │
3560CX (JLM-LAB-SW1) ← L3 core, L2 switch for VLANs
    │
    ├── Gi0/2 → GS308EP Port 1 (trunk)
    └── Gi0/3 → GS316EP Port 15 (trunk)
```

The TRANSIT link (Gi0/1 on 3560CX, GE0/1/0 on C1111) is a **routed
L3 port** — it has no switchport configuration and does not participate
in STP. STP only runs on Layer 2 switch ports.

The 3560CX will become the **STP root bridge** for all VLANs because:
1. It's the central L3 core switch
2. We will explicitly set its priority lower than the Netgear switches
3. Netgear switches don't support STP priority configuration — the
   3560CX must win the election by configuration

**Phase B STP configuration to apply:**
```
spanning-tree vlan 1,10,20,30,31,40,50,60,70,99 priority 4096
```

This sets the 3560CX as root bridge for all VLANs (priority 4096 beats
default 32768 on Netgear switches).

---

## Part 6 — STP Features Configured on 3560CX

### Bridge Assurance
```
spanning-tree bridge-assurance
```
Enabled by default on 3560CX. Sends BPDUs on all network ports
(point-to-point links between switches). If BPDUs stop being received,
the port is put into inconsistent state — prevents a unidirectional
link failure from creating a loop.

### PortFast (to be configured at Phase B)
PortFast should be enabled on access ports connected to end devices
(not other switches). It skips the learning state and moves directly
to forwarding — reducing connection delay from ~6 seconds to immediate.

```
interface GigabitEthernet0/5
 spanning-tree portfast
```

Or enable globally for all access ports:
```
spanning-tree portfast default
```

**Never enable PortFast on trunk ports** — connecting a switch to a
PortFast port creates an instant loop.

### BPDU Guard (to be configured at Phase B)
BPDU Guard disables a PortFast port if it receives a BPDU — preventing
a rogue switch from being plugged into an access port and disrupting STP.

```
spanning-tree portfast bpduguard default
```

---

## Part 7 — Verification Commands Reference

```
show spanning-tree summary
```
Overview of STP mode, root bridge status, and instance count.

```
show spanning-tree
```
All STP instances with port roles and states.

```
show spanning-tree vlan <id>
```
STP detail for a specific VLAN — root bridge, local bridge ID, ports.

```
show spanning-tree vlan <id> detail
```
Full detail including timers, port costs, and BPDU counts.

```
show spanning-tree interface <intf> detail
```
STP state for a specific port.

```
show spanning-tree inconsistentports
```
Ports in STP inconsistent state (BPDU Guard, Loop Guard violations).

---

## Part 8 — CCNA Exam Topics Covered

| Topic | Coverage |
|---|---|
| Why STP exists | Broadcast storm prevention explained |
| STP versions (802.1D, 802.1w, PVST+, Rapid-PVST+) | All four documented |
| Bridge ID and root bridge election | Priority + Extended System ID |
| Port roles (Root, Designated, Alternate, Backup) | All four defined |
| Port states (Discarding, Learning, Forwarding) | RSTP 3-state model |
| STP convergence times | Legacy 30–50s vs RSTP 1–6s |
| PortFast | Access port configuration |
| BPDU Guard | Rogue switch protection |
| Bridge Assurance | Unidirectional link protection |
| `show spanning-tree` commands | Full reference |

---

## Phase B Lab Exercises (pending cutover)

These exercises become available once the 3560CX is in production:

- [ ] Observe STP instances forming per VLAN when 3560CX is cabled
- [ ] Verify 3560CX is root bridge for all VLANs after priority set
- [ ] Configure PortFast on access ports (Gi0/5–Gi0/8)
- [ ] Configure BPDU Guard globally
- [ ] Simulate a link failure — observe STP reconvergence
- [ ] Document port roles on each active interface

---

## Lessons Learned

1. **STP instances only exist when active Layer 2 ports are present.**
   A perfectly configured switch shows zero STP instances if nothing
   is plugged in. This is normal and expected — not a misconfiguration.

2. **Routed ports (no switchport) do not participate in STP.** The
   TRANSIT link between C1111 and 3560CX is a Layer 3 routed port.
   STP only runs on Layer 2 switch ports. This is why the TRANSIT
   link doesn't affect STP topology.

3. **ISR routers with integrated switch modules run STP.** The C1111's
   GE0/1/x ports are switch ports and participate in STP. However,
   with no redundant paths, no instances form.

4. **Always set root bridge explicitly.** Never rely on MAC address
   tiebreaking to determine the root bridge. The switch you want as
   root should have the lowest priority configured explicitly.

5. **Netgear Plus series switches have limited STP configuration.**
   GS308EP and GS316EP support STP enable/disable but not priority
   configuration. The 3560CX must win root election by having a lower
   priority than the Netgear default (32768).

---

*Documented: May 21, 2026*
*Devices: C1111 JLM-LAB-R1, Catalyst 3560CX JLM-LAB-SW1*
*Phase B exercises pending cutover*
*CCNA domain: Domain 2 — Network Access*
