# Lab: OSPFv3 — IPv6 Dynamic Routing on Cisco IOS XE
# lab-007-ospfv3.md
# JLM Home Lab — git-init-home-lab
# Completed: May 21, 2026

---

## Overview

This lab documents the configuration and verification of OSPFv3 (OSPF
for IPv6) on the JLM home lab C1111 router. OSPFv3 provides dynamic
routing for IPv6 networks the same way OSPFv2 provides dynamic routing
for IPv4.

**Lab scope:** Single-router OSPFv3 on C1111 JLM-LAB-R1. A second
physical router is not present in this lab and is not planned — the
single-router configuration demonstrates all relevant CCNA exam topics
for OSPFv3 including process configuration, interface assignment, area
design, router-ID, and verification commands.

**CCNA Domain:** Domain 3 — IP Connectivity (25% of exam)

**Device:** Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10

**Prerequisites completed:**
- IPv6 unicast-routing enabled (lab-002)
- IPv6 addresses on Vlan10 (2001:DB8:10::1/64) and Vlan20 (2001:DB8:20::1/64)
- Loopback0 IPv6 address (2001:DB8::1/128)
- OSPFv2 process 1 already running for IPv4 (same process ID reused for OSPFv3)

---

## Part 1 — OSPFv3 vs OSPFv2

### What Changed

OSPFv3 (RFC 5340) is the IPv6 version of OSPF. It is not simply OSPFv2
with IPv6 addresses — it is a redesigned protocol with key differences:

| Feature | OSPFv2 | OSPFv3 |
|---|---|---|
| Protocol | IPv4 | IPv6 |
| Network layer | Runs over IPv4 | Runs over IPv6 |
| Router-ID | IPv4 address | Still a 32-bit number (can be IPv4 format) |
| Interface config | `network` command under `router ospf` | `ipv6 ospf` command per interface |
| Authentication | MD5/plain text | IPsec (AH/ESP) |
| Addressing in LSAs | IPv4 prefixes | IPv6 prefixes |
| Link-local | Not used | Used for neighbor adjacency |
| Multicast | 224.0.0.5 / 224.0.0.6 | FF02::5 / FF02::6 |

### Key Architecture Difference — Interface Configuration

**OSPFv2 (IPv4):** Networks are added centrally under the router process:
```
router ospf 1
 network 192.168.10.0 0.0.0.255 area 0
 network 192.168.20.0 0.0.0.255 area 0
```

**OSPFv3 (IPv6):** OSPF is enabled per interface directly:
```
interface Vlan10
 ipv6 ospf 1 area 0
interface Vlan20
 ipv6 ospf 1 area 0
```

This per-interface model is cleaner and maps directly to how modern
network automation tools configure routing protocols.

### Router-ID Requirement

OSPFv3 still requires a 32-bit router-ID even though it runs over IPv6.
If no IPv4 addresses exist on the router, the router-ID must be set
manually. In this lab, the router-ID is set to `10.0.0.1` — matching
the OSPFv2 router-ID for consistency and matching the Loopback0 IPv4
address.

---

## Part 2 — Pre-Configuration State

### Baseline IPv6 routing table (before OSPFv3)

```
JLM-LAB-R1#show ipv6 protocols
IPv6 Routing Protocol is "connected"
IPv6 Routing Protocol is "application"
IPv6 Routing Protocol is "ND"

JLM-LAB-R1#show ipv6 route
IPv6 Routing Table - default - 6 entries

LC  2001:DB8::1/128 [0/0]
     via Loopback0, receive
C   2001:DB8:10::/64 [0/0]
     via Vlan10, directly connected
L   2001:DB8:10::1/128 [0/0]
     via Vlan10, receive
C   2001:DB8:20::/64 [0/0]
     via Vlan20, directly connected
L   2001:DB8:20::1/128 [0/0]
     via Vlan20, receive
L   FF00::/8 [0/0]
     via Null0, receive
```

**Observation:** Only `C` (connected) and `L` (local) routes present.
No dynamic routing protocol active for IPv6. This is the baseline we
are adding OSPFv3 on top of.

---

## Part 3 — Configuration

### Step 1 — Create the OSPFv3 process

```
ipv6 router ospf 1
 router-id 10.0.0.1
 passive-interface default
 no passive-interface Loopback0
```

**`ipv6 router ospf 1`** — creates OSPFv3 process 1. Note the command
is `ipv6 router ospf` not `router ospfv3` — IOS XE uses the same process
number space for both OSPFv2 and OSPFv3.

**`router-id 10.0.0.1`** — explicitly sets the 32-bit router-ID.
This matches the OSPFv2 router-ID for consistency. Without this, IOS
would attempt to use an IPv4 address from an active interface.

**`passive-interface default`** — suppresses OSPFv3 hello packets on
all interfaces by default. With a single router, no neighbors can form
anyway, but this is best practice and matches the OSPFv2 configuration.

**`no passive-interface Loopback0`** — re-enables OSPFv3 hellos on
Loopback0 so the interface is advertised into OSPF. Loopbacks are
virtual interfaces — enabling OSPFv3 here makes the router-ID reachable
via the protocol.

### Step 2 — Enable OSPFv3 per interface

```
interface Loopback0
 ipv6 ospf 1 area 0

interface Vlan10
 ipv6 ospf 1 area 0

interface Vlan20
 ipv6 ospf 1 area 0
```

**`ipv6 ospf 1 area 0`** — enables OSPFv3 process 1 on this interface
and places it in Area 0 (backbone area). This is the key difference
from OSPFv2 — no `network` commands under the process, interfaces are
configured directly.

### Complete configuration block

```
ipv6 router ospf 1
 router-id 10.0.0.1
 passive-interface default
 no passive-interface Loopback0
!
interface Loopback0
 ipv6 ospf 1 area 0
!
interface Vlan10
 ipv6 ospf 1 area 0
!
interface Vlan20
 ipv6 ospf 1 area 0
```

---

## Part 4 — Verification (Live Output — May 21, 2026)

### show ipv6 protocols

```
JLM-LAB-R1#show ipv6 protocols
IPv6 Routing Protocol is "connected"
IPv6 Routing Protocol is "application"
IPv6 Routing Protocol is "ND"
IPv6 Routing Protocol is "ospf 1"
  Router ID 10.0.0.1
  Number of areas: 1 normal, 0 stub, 0 nssa
  Interfaces (Area 0):
    Loopback0
    Vlan20
    Vlan10
  Redistribution:
    None
```

**What this confirms:**
- OSPFv3 process 1 is active ✅
- Router-ID 10.0.0.1 confirmed ✅
- 1 area (Area 0 backbone) ✅
- 3 interfaces participating: Loopback0, Vlan10, Vlan20 ✅

### show ipv6 ospf

```
JLM-LAB-R1#show ipv6 ospf
 Routing Process "ospfv3 1" with ID 10.0.0.1
 Supports NSSA (compatible with RFC 3101)
 Event-log enabled, Maximum number of events: 1000, Mode: cyclic
 Router is not originating router-LSAs with maximum metric
 Initial SPF schedule delay 50 msecs
 Minimum hold time between two consecutive SPFs 200 msecs
 Maximum wait time between two consecutive SPFs 5000 msecs
 Number of external LSA 0. Checksum Sum 0x000000
 Number of areas in this router is 1. 1 normal 0 stub 0 nssa
 Graceful restart helper support enabled
 Reference bandwidth unit is 100 mbps
 RFC1583 compatibility enabled
    Area BACKBONE(0) (Inactive)
```

**Key observations:**
- Process labeled `ospfv3 1` — IOS XE distinguishes OSPFv2 (`ospf 1`)
  from OSPFv3 (`ospfv3 1`) in show output even though they share process
  number space
- `Area BACKBONE(0) (Inactive)` — correct for single router with no
  neighbors. Area becomes Active when at least one adjacency forms.
- SPF timers identical to OSPFv2 — 50ms initial, 200ms hold, 5000ms max

### show ipv6 ospf interface brief

```
JLM-LAB-R1#show ipv6 ospf interface brief
Interface    PID   Area            Intf ID    Cost  State Nbrs F/C
Lo0          1     0               21         1     LOOP  0/0
Vl20         1     0               15         1     DR    0/0
Vl10         1     0               14         1     DR    0/0
```

**What each column means:**

| Column | Value | Meaning |
|---|---|---|
| PID | 1 | OSPF process ID |
| Area | 0 | Backbone area |
| Intf ID | 21/15/14 | Internal OSPFv3 interface identifier |
| Cost | 1 | Interface cost (100Mbps reference ÷ link speed) |
| State | LOOP/DR | Interface role in OSPF |
| Nbrs F/C | 0/0 | Full/Total neighbors — zero, expected |

**Interface states explained:**
- `LOOP` — Loopback interface. Always stable, never sends hellos to
  neighbors. Used as router-ID anchor.
- `DR` — Designated Router. On each multi-access segment, one router
  is elected DR. With only one router, it is automatically DR on
  every segment.

### show ipv6 route ospf

```
JLM-LAB-R1#show ipv6 route ospf
IPv6 Routing Table - default - 6 entries
(no OSPFv3 routes present)
```

**Why no OSPFv3 routes:** With a single router, there are no neighbors
to exchange LSAs with. OSPFv3 builds its routing table from LSAs
(Link State Advertisements) received from other routers. No neighbors
= no LSAs = no OSPF routes. This is correct and expected behavior.

The routing table will show `O` (OSPF intra-area) routes when the
3560CX joins as a neighbor after Phase B cutover.

---

## Part 5 — OSPFv2 vs OSPFv3 Side-by-Side Comparison

Both OSPFv2 and OSPFv3 are now running simultaneously on JLM-LAB-R1,
which makes a direct comparison possible.

### show ip protocols (OSPFv2)

```
IPv6 Routing Protocol is "ospf 1"        ← labeled "ospf" for v2
  Router ID 10.0.0.1
  Interfaces (Area 0):
    Loopback0, Vlan99, Vlan50, Vlan40,
    Vlan31, Vlan30, Vlan20, Vlan10, Vlan1
```

OSPFv2 advertises ALL 9 IPv4 VLAN subnets — configured via `network`
commands under `router ospf 1`.

### show ipv6 protocols (OSPFv3)

```
IPv6 Routing Protocol is "ospf 1"        ← labeled "ospf" for v3 too
  Router ID 10.0.0.1
  Interfaces (Area 0):
    Loopback0, Vlan20, Vlan10
```

OSPFv3 only advertises the 3 interfaces with IPv6 addresses configured.
VLANs 30, 31, 40, 50, 99 have no IPv6 addresses, so they are not
in OSPFv3.

### Configuration Method Comparison

| | OSPFv2 | OSPFv3 |
|---|---|---|
| Enable routing | `ip routing` | `ipv6 unicast-routing` |
| Create process | `router ospf 1` | `ipv6 router ospf 1` |
| Set router-ID | `router-id 10.0.0.1` | `router-id 10.0.0.1` (same) |
| Add networks | `network x.x.x.x wildcard area 0` | Per interface: `ipv6 ospf 1 area 0` |
| Passive interface | Under `router ospf` | Under `ipv6 router ospf` |
| Verify process | `show ip ospf` | `show ipv6 ospf` |
| Verify interfaces | `show ip ospf interface brief` | `show ipv6 ospf interface brief` |
| Verify routes | `show ip route ospf` | `show ipv6 route ospf` |
| Neighbor table | `show ip ospf neighbor` | `show ipv6 ospf neighbor` |

---

## Part 6 — LSA Types (CCNA Reference)

OSPFv3 uses similar LSA types to OSPFv2 but with renamed/restructured types:

| LSA Type | OSPFv2 Name | OSPFv3 Name | Purpose |
|---|---|---|---|
| Type 1 | Router LSA | Router LSA | Router's directly connected links |
| Type 2 | Network LSA | Network LSA | Multi-access segment (DR generates) |
| Type 3 | Summary LSA | Inter-Area Prefix LSA | Routes between areas |
| Type 4 | ASBR Summary LSA | Inter-Area Router LSA | ASBR location |
| Type 5 | AS External LSA | AS External LSA | External routes |
| Type 8 | N/A | Link LSA | Link-local address + options per link |
| Type 9 | N/A | Intra-Area Prefix LSA | IPv6 prefixes for router/network LSAs |

Types 8 and 9 are new in OSPFv3 — they separate IPv6 prefix information
from topology information, which is a key architectural improvement.

---

## Part 7 — What Changes at Phase B Cutover

When the 3560CX (JLM-LAB-SW1) is cabled into production via the
TRANSIT link (192.168.199.0/30), OSPFv3 can be extended across the
link if IPv6 is configured on both TRANSIT interfaces.

**To extend OSPFv3 to the 3560CX at Phase B:**

On C1111:
```
interface GigabitEthernet0/1/0
 ipv6 address 2001:DB8:199::1/64
 ipv6 ospf 1 area 0
```

On 3560CX:
```
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 10.0.0.2
interface GigabitEthernet0/1
 ipv6 address 2001:DB8:199::2/64
 ipv6 ospf 1 area 0
```

At that point, an OSPFv3 adjacency forms across the TRANSIT link,
both routers exchange LSAs, and OSPFv3 routes (`O`) appear in the
IPv6 routing tables — closing the multi-router OSPFv3 gap entirely.

---

## Part 8 — CCNA Exam Topics Covered

| Topic | Coverage |
|---|---|
| OSPFv3 vs OSPFv2 differences | Full comparison table |
| `ipv6 router ospf` configuration | Configured on C1111 |
| Per-interface OSPF enablement | All three interfaces configured |
| Router-ID in OSPFv3 | Explicitly set to 10.0.0.1 |
| Area 0 backbone | Single area design |
| `passive-interface default` | Configured, matching OSPFv2 |
| DR election | Observed — C1111 is DR on all segments |
| OSPFv3 LSA types | Reference table (types 1-5, 8-9) |
| OSPFv3 multicast addresses | FF02::5 (AllSPFRouters), FF02::6 (AllDRRouters) |
| `show ipv6 ospf` | Live output documented |
| `show ipv6 ospf interface brief` | Live output with column explanation |
| `show ipv6 route ospf` | Live output with explanation |
| `show ipv6 protocols` | Live output documented |
| Dual-stack OSPF | Both OSPFv2 and OSPFv3 running simultaneously |

---

## Lessons Learned

1. **OSPFv3 uses per-interface configuration, not `network` statements.**
   This is the most common mistake when transitioning from OSPFv2 to
   OSPFv3. The `network` command under `ipv6 router ospf` does not
   exist in IOS XE.

2. **Router-ID is still 32-bit in OSPFv3.** Despite running over IPv6,
   the router-ID format remains a 32-bit dotted-decimal number. If no
   IPv4 addresses exist, it must be set manually or the process will
   not start.

3. **OSPFv3 Area 0 shows (Inactive) with no neighbors.** This is not
   an error — it means no adjacencies have formed. The area becomes
   Active when at least one neighbor relationship exists.

4. **IOS XE labels both OSPFv2 and OSPFv3 as "ospf" in show output.**
   The distinction appears in `show ipv6 ospf` which labels the process
   `ospfv3 1` vs `show ip ospf` which labels it `ospf 1`. Both use
   process ID 1 in this lab.

5. **Only interfaces with IPv6 addresses participate in OSPFv3.**
   VLANs 30, 31, 40, 50, and 99 have no IPv6 addresses configured,
   so they are absent from OSPFv3 even though they participate in
   OSPFv2. Dual-stack requires both IPv4 and IPv6 addresses per
   interface to participate in both routing protocols.

6. **`passive-interface default` is critical security practice.**
   Even with a single router, enabling it establishes the correct
   habit — OSPF hellos should only be sent on links where neighbors
   are expected. This prevents a device plugged into an access port
   from receiving OSPF hellos and attempting to form an adjacency.

---

## Verification Command Reference

```
show ipv6 protocols
```
Lists all active IPv6 routing protocols, router-ID, areas, and interfaces.

```
show ipv6 ospf
```
OSPFv3 process detail — SPF timers, LSA counts, area status.

```
show ipv6 ospf interface brief
```
Per-interface OSPFv3 state — PID, area, cost, state, neighbor count.

```
show ipv6 ospf interface <intf>
```
Full detail for a specific interface including hello/dead timers.

```
show ipv6 ospf neighbor
```
Neighbor table — empty until Phase B cutover adds a second router.

```
show ipv6 ospf database
```
Link State Database — LSAs known to this router.

```
show ipv6 route ospf
```
IPv6 routes learned via OSPFv3 — empty until neighbors exist.

```
debug ipv6 ospf events
```
Real-time OSPFv3 event logging — use carefully, generates significant output.

---

*Lab completed: May 21, 2026*
*Device: Cisco C1111-4PWB JLM-LAB-R1, IOS XE 16.10*
*Phase B extension: OSPFv3 adjacency with 3560CX documented in Part 7*
*CCNA domain: Domain 3 — IP Connectivity*
