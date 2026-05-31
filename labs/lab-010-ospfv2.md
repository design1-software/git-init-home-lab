# Lab: OSPFv2 — IPv4 Dynamic Routing, Two-Router Design (Phase B Cutover)
# lab-010-ospfv2.md
# JLM Home Lab — git-init-home-lab
# Started: May 31, 2026 | Status: In Progress

---

## Overview

This lab documents the design rationale, configuration, and verification of OSPFv2 (OSPF for IPv4) across the TRANSIT link between the C1111 ISR and the Catalyst 3560CX-8PC-S. It is the routing foundation for Phase B cutover — the step that makes the 3560CX the L3 core and eliminates the need for per-VLAN static routes on the C1111.

**Lab scope:** Two-router OSPFv2, single area (area 0). TRANSIT link = VLAN 199 (192.168.199.0/30). C1111 is WAN edge and default-route originator; 3560CX owns all VLAN SVIs.

**CCNA Domain:** Domain 3 — IP Connectivity (25% of exam)

**Devices:**
- Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10 — router ID 1.1.1.1
- Cisco Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — router ID 2.2.2.2

**Prerequisites:**
- TRANSIT VLAN 199 configured on C1111: GE0/1/0 access VLAN 199, Vlan199 SVI 192.168.199.1/30 (Step 1.2 complete)
- TRANSIT port configured on 3560CX: Gi0/1 routed port 192.168.199.2/30 (baseline config)
- Physical cable between C1111 GE0/1/0 and 3560CX Gi0/1 (Step 1.3 — cable run)

---

## Part 1 — What OSPF Is

OSPF (Open Shortest Path First) is a dynamic routing protocol — specifically a link-state interior gateway protocol (IGP).

Routers need to know how to reach networks that aren't directly connected to them. Two approaches:

| Approach | Mechanism | Failure behavior | Scalability |
|---|---|---|---|
| Static routes | Manually configured per destination | Silent blackhole on link failure | Breaks at scale |
| Dynamic routing (OSPF) | Routers exchange topology, calculate independently | Reconverges within seconds | Scales to enterprise |

With OSPF, every router builds a complete map of the network in its link-state database and runs **Dijkstra's algorithm** (the literal Shortest Path First algorithm) to compute the best path to every known destination. When a link fails or a new network appears, routers exchange updates and reconverge in seconds.

---

## Part 2 — How OSPF Works Mechanically

Three things happen on every OSPF-enabled interface:

**1. Hello packets**
Each router sends a multicast hello out every OSPF interface every 10 seconds (on Ethernet). When two routers exchange hellos and agree on key parameters (area ID, timers, authentication), they become **neighbors**.

**2. Database exchange**
Neighbors exchange **Link-State Advertisements (LSAs)** describing every network they know about. Each router builds an identical link-state database (LSDB).

**3. SPF calculation**
Each router independently runs Dijkstra against the LSDB and installs the resulting best paths into its routing table. `O` routes in `show ip route` = OSPF-learned paths.

**Areas:** OSPF uses areas to scale. Area 0 is the backbone. In this lab, everything runs in area 0.

---

## Part 3 — Why OSPF on This Network

### The static route problem

After Phase B without OSPF, you need static routes both ways:

**On the 3560CX** (already in baseline config):
```
ip route 0.0.0.0 0.0.0.0 192.168.199.1
```

**On the C1111** — one per VLAN SVI on the 3560CX:
```
ip route 192.168.10.0  255.255.255.0 192.168.199.2
ip route 192.168.20.0  255.255.255.0 192.168.199.2
ip route 192.168.30.0  255.255.255.0 192.168.199.2
ip route 192.168.31.0  255.255.255.0 192.168.199.2
ip route 192.168.40.0  255.255.255.0 192.168.199.2
ip route 192.168.50.0  255.255.255.0 192.168.199.2
ip route 192.168.60.0  255.255.255.0 192.168.199.2  ! LAB (future)
ip route 192.168.70.0  255.255.255.0 192.168.199.2  ! SERVER (future)
ip route 192.168.99.0  255.255.255.0 192.168.199.2
```

That's 9 static routes now, more as VLANs are added. Every new subnet on the 3560CX requires a matching static on the C1111 — miss one and the network silently breaks.

### With OSPF

- The 3560CX announces all its VLAN SVIs into OSPF automatically
- The C1111 installs all of them with next-hop 192.168.199.2 — no manual config
- New VLAN on the 3560CX? Its SVI comes up, OSPF redistributes it, the C1111 learns it within seconds — zero touch on the C1111
- The C1111 uses `default-information originate` to push its default route into OSPF — the 3560CX's static default can be replaced by an OSPF-learned default (O*E2 in `show ip route`)

### CCNA exam relevance

OSPFv2 in a single area is a significant portion of the CCNA 200-301 v1.1 exam (Domain 3 — IP Connectivity, 25%). This lab covers:
- Process configuration and router-ID assignment
- Interface-level OSPF participation (`network` statement or `ip ospf area` per-interface)
- Passive interfaces (VLAN SVIs that shouldn't send hellos)
- `default-information originate` for default route injection
- Verification: `show ip ospf neighbor`, `show ip ospf database`, `show ip route ospf`
- Troubleshooting: mismatched area IDs, timers, network types, MTU

---

## Part 4 — Topology

```
                    192.168.199.0/30
C1111 Vlan199 SVI ──────────────────── 3560CX Gi0/1
192.168.199.1                          192.168.199.2
(router-id 1.1.1.1)                    (router-id 2.2.2.2)
      │                                       │
  WAN/NAT                          VLAN SVIs (all subnets)
  default route                    VLAN 10:  192.168.10.1/24
                                   VLAN 20:  192.168.20.1/24
                                   VLAN 30:  192.168.30.1/24
                                   VLAN 31:  192.168.31.1/24
                                   VLAN 40:  192.168.40.1/24
                                   VLAN 50:  192.168.50.1/24
                                   VLAN 99:  192.168.99.1/24
                                   VLAN 60:  192.168.60.1/24 (planned)
                                   VLAN 70:  192.168.70.1/24 (planned)
```

**Physical path:** C1111 GE0/1/0 (access VLAN 199) → cable → 3560CX Gi0/1 (routed port)

**Asymmetry note:** C1111 side is a VLAN 199 SVI (required — NIM-ES2 ports are L2-only; see Lesson 11 in vlan-design.md). 3560CX side is a native routed port (`no switchport`). This is functionally identical — a single L2 segment with one /30 IP on each end. OSPF doesn't care about the interface type, only the IP adjacency.

---

## Part 5 — Configuration

### Step 1.2 — C1111 TRANSIT setup (complete)

```
vlan 199
 name TRANSIT

interface GigabitEthernet0/1/0
 description TRANSIT-TO-3560CX
 switchport mode access
 switchport access vlan 199
 no shutdown

interface Vlan199
 ip address 192.168.199.1 255.255.255.252
 ip nat inside
 no shutdown
```

### Step 1.3 — C1111 OSPFv2 (complete — May 31, 2026)

#### Pre-existing state discovered

Before any changes, `show ip ospf` and `show running-config | section router ospf` revealed OSPF process 1 was already running from prior lab work:

```
router ospf 1
 router-id 1.1.1.1
 passive-interface default
 no passive-interface Loopback0
 network 10.0.0.1 0.0.0.0 area 0       ! Loopback0 — stable router identity
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
 network 192.168.30.0 0.0.0.255 area 0
 network 192.168.31.0 0.0.0.255 area 0
 network 192.168.40.0 0.0.0.255 area 0
 network 192.168.50.0 0.0.0.255 area 0
 network 192.168.99.0 0.0.0.255 area 0
 network 192.168.100.0 0.0.0.255 area 0
```

Key points about the pre-existing config:
- `passive-interface default` — hellos suppressed on ALL interfaces by default; only interfaces with explicit `no passive-interface` send hellos. This is the correct design for a router whose VLAN SVIs have no OSPF neighbors.
- `no passive-interface Loopback0` — only Loopback0 was active for hellos (a no-op on a loopback, but establishes the pattern).
- All VLAN SVIs already advertised as stub networks — their subnets propagate via LSAs even though hellos are suppressed.
- Router ID 1.1.1.1 already set.

**Initial misread (corrected):** `show ip ospf interface brief` showed all VLAN SVIs in DR state, which was initially flagged as OSPF hellos broadcasting onto every VLAN. That is wrong — the SVIs are advertised as stub networks (subnets propagate) but `passive-interface default` prevents hello transmission. The DR state is a local election artifact on a segment with no other OSPF speakers — it is harmless.

#### Plan deviations

The original Step 1.3 plan had two errors:

| Issue | Original plan | Reality |
|---|---|---|
| Assumed clean slate | `router-id 1.1.1.1` (new assignment) | Process 1 + router-id already existed — re-issuing is a no-op or could cause adjacency reset |
| Wrong interface for passive | `no passive-interface GigabitEthernet0/1/0` | NIM-ES2 physical ports have no OSPF state; OSPF runs on Vlan199 SVI — correct command is `no passive-interface Vlan199` |

#### Commands actually executed

```
configure terminal
router ospf 1
 network 192.168.199.0 0.0.0.3 area 0   ! NEW — brings Vlan199 into OSPF
 default-information originate           ! NEW — C1111 advertises default route to 3560CX
 no passive-interface Vlan199            ! NEW — allows hellos out TRANSIT SVI
 exit
exit
write memory
```

Only three additive changes to the existing process. Router ID 1.1.1.1 confirmed unchanged.

#### Verification results

```
! ASBR status confirms default-information originate is active
C1111# show ip ospf
 Routing Process "ospf 1" with ID 1.1.1.1
 It is an autonomous system boundary router
 Number of external LSA 1               ! default route advertised as Type-5 external LSA

! Vlan199 in OSPF, state DOWN (expected — no cable, no neighbor possible yet)
C1111# show ip ospf interface brief
Interface    PID   Area    IP Address/Mask    Cost  State  Nbrs F/C
Vl199          1      0    192.168.199.1/30      1  DOWN     0/0

! Confirms Vlan199 is actively sending hellos (no "Passive interface" marker)
C1111# show ip ospf interface Vlan199 | include passive|Hello
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
```

**End state:** C1111 is fully prepared. The moment Cable 1 (C1111 GE0/1/0 → 3560CX Gi0/1) is plugged in and OSPF is configured on the 3560CX, the adjacency will form automatically. The C1111 will learn all VLAN routes from the 3560CX; the 3560CX will learn the default route from the C1111 via OSPF (replacing its static default).

### Step 2.x — 3560CX OSPFv2 (pending — after cable run)

The 3560CX baseline has no OSPF process configured — this is a clean-slate configuration. The preferred pattern mirrors the C1111: `passive-interface default` to suppress hellos everywhere, then selectively re-enable on the TRANSIT interface only.

```
router ospf 1
 router-id 2.2.2.2
 passive-interface default              ! suppress hellos on all SVIs
 no passive-interface GigabitEthernet0/1   ! TRANSIT port — must send hellos to C1111
 network 192.168.199.0 0.0.0.3 area 0
 network 192.168.10.0  0.0.0.255 area 0
 network 192.168.20.0  0.0.0.255 area 0
 network 192.168.30.0  0.0.0.255 area 0
 network 192.168.31.0  0.0.0.255 area 0
 network 192.168.40.0  0.0.0.255 area 0
 network 192.168.50.0  0.0.0.255 area 0
 network 192.168.99.0  0.0.0.255 area 0
```

> On the 3560CX, Gi0/1 is a native routed port (no SVI involved), so `no passive-interface GigabitEthernet0/1` is correct — unlike the C1111 where the physical port is L2-only and OSPF runs on the SVI.

> Once adjacency is confirmed stable, the 3560CX static default (`ip route 0.0.0.0 0.0.0.0 192.168.199.1`) can be removed — it will be replaced by the OSPF-learned `O*E2 0.0.0.0/0` from the C1111.

---

## Part 6 — Verification (pending — after cable run and OSPF configured both sides)

### Expected neighbor state

```
C1111# show ip ospf neighbor

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           1   FULL/DR         00:00:38    192.168.199.2   Vlan199
```

### Expected routes on C1111

```
C1111# show ip route ospf

O     192.168.10.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.20.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.30.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.31.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.40.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.50.0/24  [110/2] via 192.168.199.2, Vlan199
O     192.168.99.0/24  [110/2] via 192.168.199.2, Vlan199
```

### Expected routes on 3560CX

```
3560CX# show ip route ospf

O*E2  0.0.0.0/0        [110/1] via 192.168.199.1, GigabitEthernet0/1
```

> `O*E2` = OSPF external type 2, candidate default route — this is the C1111's default injected via `default-information originate`. The 3560CX static default (`ip route 0.0.0.0 0.0.0.0 192.168.199.1`) can be removed once OSPF adjacency is confirmed stable.

---

## Part 7 — Troubleshooting Reference

| Symptom | Likely cause | Check |
|---|---|---|
| No neighbor formed | Cable not in / interface down | `show interfaces GE0/1/0` (C1111), `show interfaces Gi0/1` (3560CX) |
| Neighbor stuck in INIT | Hello received but not replied | MTU mismatch — `show ip ospf interface` on both sides |
| Neighbor stuck in EXSTART | DBD exchange failing | MTU mismatch — `ip ospf mtu-ignore` as workaround or fix MTU |
| Adjacency forms then drops | Dead timer mismatch | `show ip ospf interface` — hello/dead timers must match |
| Routes not appearing | `network` statement wrong | Verify wildcard mask covers the interface IP |
| VLAN routes missing | 3560CX SVI not up | `show ip interface brief` — SVI must be up/up |
| Default not on 3560CX | `default-information originate` missing or C1111 has no default | C1111 must have a default route in its table for originate to work |
