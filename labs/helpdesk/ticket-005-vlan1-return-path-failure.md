# Helpdesk Ticket 005 — VLAN 1 Return Path Failure (Asymmetric Routing)

**Domain:** Routing / NAT / Transitional Network Architecture
**Difficulty:** Intermediate–Advanced
**Estimated time:** 45–60 minutes
**Based on:** Real ARIA incident (Jun 4, 2026) — post-Phase B cutover transitional topology

---

## Scenario

A student reports: *"The Proxmox server can reach the gateway and DNS works, but it can't get to the internet. Pings to 8.8.8.8 fail. Nothing in NAT should be blocking it — VLAN 1 is in the NAT ACL."*

ARIA (192.168.100.10) is on VLAN 1, temporarily, during the Phase B to Phase C transition.

---

## Ticket Details

**Reported by:** Lab sysadmin / student
**Affected system:** ARIA Proxmox host — internet egress
**Priority:** Medium
**Category:** Network — Routing / NAT / Asymmetric Path

---

## Why This Ticket Is Valuable

This scenario is a high-value enterprise troubleshooting case because:

- DNS works and the gateway is reachable — the two most common quick checks both pass
- The NAT ACL exists and includes VLAN 1 — the next common check also passes
- The actual failure is invisible to basic tools: a routing asymmetry introduced by a transitional topology where one device (C1111) still has a directly connected route for a VLAN whose L2 path has been physically removed

Students who stop at "gateway reachable, DNS works, NAT ACL exists" will be stuck. This ticket teaches them to prove the return path, not just the forward path.

---

## AI Mentor Opening Questions

```
1. Can ARIA ping its default gateway (192.168.100.1)?
2. Can ARIA resolve a public hostname like google.com?
3. Can ARIA ping 8.8.8.8?
4. What route does ARIA use to reach 8.8.8.8?
   (ip route get 8.8.8.8)
5. From the 3560CX, can you ping 8.8.8.8 sourced from VLAN 1?
   (ping 8.8.8.8 source vlan 1)
6. From the 3560CX, can you ping 8.8.8.8 sourced from VLAN 10?
   (ping 8.8.8.8 source vlan 10)
7. Does C1111 still have a Vlan1 SVI configured?
   (show ip interface brief | include Vlan1)
8. Does C1111 have a route for 192.168.100.0/24?
   (show ip route 192.168.100.0)
```

---

## Evidence Required

```
From ARIA:
- ping -c 3 192.168.100.1 (gateway reachable?)
- nslookup google.com (DNS resolves?)
- ping -c 3 8.8.8.8 (internet reachable?)
- ip route get 8.8.8.8 (egress path)

From 3560CX:
- ping 8.8.8.8 source vlan 1 (VLAN 1 internet path works?)
- ping 8.8.8.8 source vlan 10 (VLAN 10 internet path works?)
- show ip route 0.0.0.0 (default route — where does 3560CX send internet traffic?)

From C1111:
- show ip interface brief | include Vlan1 (does C1111 still have VLAN 1 SVI?)
- show ip route 192.168.100.0 (how does C1111 route back to VLAN 1 devices?)
- show ip nat translations (any translations for 192.168.100.10?)
```

---

## Diagnostic Path

```
Step 1: Confirm it is not a forward-path failure
  ARIA pings gateway (192.168.100.1) → success
  ARIA resolves DNS → success
  → Forward path from ARIA is working

Step 2: Confirm it is not a NAT ACL failure
  C1111 NAT-INSIDE ACL includes permit 192.168.100.0 0.0.0.255
  → NAT should translate traffic from ARIA

Step 3: Test from the router directly
  3560CX: ping 8.8.8.8 source vlan 10 → success
  3560CX: ping 8.8.8.8 source vlan 1  → FAIL
  → Internet works from VLAN 10, fails from VLAN 1
  → Problem is in the VLAN 1 path specifically

Step 4: Identify the routing asymmetry
  C1111: show ip interface brief | include Vlan1
  → Vlan1 SVI exists on C1111 at 192.168.100.1 (still configured, pending cleanup)
  → C1111 shows 192.168.100.0/24 as directly connected via Vlan1

  BUT: GS308EP Port 1 now trunks to 3560CX Gi0/2, not C1111 GE0/1/1
       C1111 has no physical L2 path to reach VLAN 1 devices anymore

  Result:
    OUTBOUND: ARIA → 3560CX (192.168.100.1 HSRP) → TRANSIT → C1111 → NAT → internet (works)
    INBOUND:  internet → C1111 (WAN) → routing lookup for 192.168.100.10
              → C1111 finds 192.168.100.0/24 directly connected via Vlan1
              → C1111 tries to ARP on Vlan1 for 192.168.100.10
              → No L2 path — ARP fails — packet dropped
              → ARIA never receives reply

  This is asymmetric routing: outbound succeeds, return path is broken.

Step 5: Apply temporary fix
  Add /32 static host routes on C1111 pointing ARIA and Comet
  via the TRANSIT link to 3560CX:

  ip route 192.168.100.10 255.255.255.255 192.168.199.2
  ip route 192.168.100.11 255.255.255.255 192.168.199.2

  This overrides the directly-connected route for specific hosts,
  forcing C1111 to route return traffic via TRANSIT to 3560CX,
  which has the correct L2 path to reach them.

Step 6: Verify
  ARIA: ping 8.8.8.8 → success
  3560CX: ping 8.8.8.8 source vlan 1 → success
  C1111: show ip nat translations → entries appear for 192.168.100.10
```

---

## Root Cause Explanation

This is a **transitional topology asymmetric routing failure**.

After Phase B trunk cutover:
- 3560CX owns the L2 segment for VLAN 1 (trunks to GS308EP and GS316EP)
- C1111 still has its VLAN 1 SVI configured (pending cleanup)
- C1111's routing table shows VLAN 1 (192.168.100.0/24) as directly connected
- But C1111 has no physical L2 path to devices on that subnet anymore

When internet return traffic arrives at C1111:
- C1111 looks up the destination (192.168.100.10) in its routing table
- Finds: directly connected via Vlan1
- Tries to ARP for 192.168.100.10 on its own Vlan1 interface
- Gets no response — the physical trunk to GS308EP is gone
- Drops the packet

The student who only checks forward-path will never see this. The return path must be proven separately.

---

## Temporary Fix

```cisco
! On C1111 — add /32 host routes for VLAN 1 devices that need internet
! Route return traffic via TRANSIT (192.168.199.2 = 3560CX Gi0/1)

ip route 192.168.100.10 255.255.255.255 192.168.199.2
ip route 192.168.100.11 255.255.255.255 192.168.199.2

write memory
```

This is explicitly temporary. It solves the return path by bypassing the stale directly-connected route for specific hosts. It is removed when ARIA and Comet move to their permanent VLANs and the C1111 VLAN 1 SVI is removed.

---

## Permanent Fix (Phase C)

```
1. Move ARIA from VLAN 1 to VLAN 70 (192.168.70.10)
2. Move Comet from VLAN 1 to VLAN 10 (permanent IP TBD)
3. Remove C1111 Vlan1 SVI (post-cutover cleanup)
4. Remove /32 static routes — no longer needed
5. 192.168.100.0/24 no longer present on C1111 routing table
```

After Phase C, C1111's routing table will only contain the TRANSIT network and the WAN — the asymmetry problem disappears.

---

## Documentation Prompt

```
Write a structured incident summary:
- Reported symptom and initial findings
- What the two most common checks showed (gateway reachable, DNS working) and why they did not identify the problem
- What test revealed the failure was VLAN-specific (source VLAN 1 vs VLAN 10 ping test)
- How the routing asymmetry was identified on C1111
- What the temporary fix does and why /32 host routes work here
- Why this fix is temporary and what the permanent resolution is
- What would prevent this class of problem in a clean production topology
```

---

## Learning Objectives

- Understand that a working forward path does not guarantee a working return path
- Identify asymmetric routing caused by stale directly-connected routes
- Use source-interface pings from a Cisco device to isolate VLAN-specific failures
- Understand the difference between a directly-connected route and an administratively injected static route (longest-match wins)
- Recognize transitional topology risk during Layer 3 cutover migrations
- Document a temporary fix with its scope and removal conditions
- Understand why `/32 host routes` override `/24 directly-connected routes` via longest-prefix match

---

## Related Resources

- `docs/vlan-design.md` — Phase B HSRP status, role split, C1111 VLAN 1 SVI cleanup backlog
- `labs/lab-010-ospfv2.md` — TRANSIT VLAN 199 design and OSPF adjacency context
- `docs/proxmox-server-build.md` — ARIA current network state (temporary VLAN 1)
- `docs/runbooks/cisco/vlan1-transitional-routing.md` — operational runbook for this scenario

---

*Based on real incident: Jun 4, 2026*
*ARIA internet egress restored via /32 static host routes on C1111*
