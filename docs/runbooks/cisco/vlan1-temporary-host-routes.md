# Runbook — VLAN 1 Temporary Host Routes on C1111

**Status:** Active intentional technical debt — do not remove until removal conditions are met.

---

## What These Routes Are

Three `/32` static host routes configured on JLM-LAB-R1 (C1111):

```cisco
ip route 192.168.100.2  255.255.255.255 192.168.199.2
ip route 192.168.100.10 255.255.255.255 192.168.199.2
ip route 192.168.100.11 255.255.255.255 192.168.199.2
```

| Route | Device | Why it exists |
|---|---|---|
| 192.168.100.2/32 | 3560CX VLAN 1 SVI (physical) | Return path for 3560CX VLAN 1 management traffic |
| 192.168.100.10/32 | ARIA Proxmox (temp VLAN 1) | Return path for ARIA internet egress |
| 192.168.100.11/32 | Comet GL-RM1PE KVM (temp VLAN 1) | Return path for Comet internet egress |

All three point via `192.168.199.2` — the 3560CX TRANSIT SVI — which has the correct L2 path to reach VLAN 1 devices.

---

## Why They Exist (Root Cause)

After Phase B trunk cutover, the C1111 no longer has a physical L2 path to VLAN 1 devices. The production trunks moved to the 3560CX (Gi0/2 → GS308EP, Gi0/3 → GS316EP). However:

- C1111 still has its VLAN 1 SVI configured (`interface Vlan1 ip address 192.168.100.1`) — pending post-cutover cleanup
- C1111's routing table shows `192.168.100.0/24` as **directly connected** via Vlan1
- When internet return traffic arrives at C1111 destined for a VLAN 1 device, C1111 follows this directly-connected route and attempts to ARP on its own Vlan1 interface
- No L2 path exists — ARP fails — packet is dropped
- Result: ARIA and Comet can send traffic out (via 3560CX → TRANSIT → C1111 → NAT) but cannot receive replies

The `/32` host routes fix this via **longest-prefix match**: a `/32` always beats a `/24`. C1111 now routes return traffic for these specific hosts via the TRANSIT link to 3560CX, which has the correct L2 path.

This is the asymmetric routing failure documented in `labs/helpdesk/ticket-005-vlan1-return-path-failure.md`.

---

## Verification

Confirm the routes are present on C1111:

```cisco
show ip route 192.168.100.10
show ip route 192.168.100.11
show ip route 192.168.100.2
```

Expected output for each:
```
Routing entry for 192.168.100.10/32
  Known via "static", distance 1, metric 0
  Routing Descriptor Blocks:
  * 192.168.199.2
```

Confirm ARIA internet egress is working:

```bash
# From ARIA
ping -c 3 8.8.8.8

# From 3560CX
ping 8.8.8.8 source vlan 1
```

Both should succeed. If either fails, check that the routes are present and that `192.168.199.2` is reachable from C1111.

---

## Removal Conditions

**Remove ALL three routes only when ALL of the following are true:**

```
[ ] ARIA has moved from VLAN 1 (192.168.100.10) to VLAN 70 (192.168.70.10)
[ ] Comet has moved from VLAN 1 (192.168.100.11) to VLAN 10 MGMT
[ ] C1111 Vlan1 SVI has been removed (post-cutover cleanup complete)
[ ] No remaining devices on VLAN 1 require internet egress through C1111 NAT
```

Do not remove individual routes piecemeal as devices move. Remove all three together after the C1111 VLAN 1 SVI is gone — at that point the directly-connected `/24` route disappears from C1111's table and the `/32` overrides are no longer needed.

---

## Removal Procedure

Run a config backup first:

```bash
R1_PASSWORD='<password>' python3 scripts/netmiko_backup.py
```

Then on C1111:

```cisco
configure terminal
no ip route 192.168.100.2  255.255.255.255 192.168.199.2
no ip route 192.168.100.10 255.255.255.255 192.168.199.2
no ip route 192.168.100.11 255.255.255.255 192.168.199.2
end
write memory
```

Verify the routes are gone:

```cisco
show ip route static
```

Verify internet still works from VLAN 10 and VLAN 20 (the production VLANs that should be unaffected):

```cisco
ping 8.8.8.8 source vlan 10
ping 8.8.8.8 source vlan 20
```

---

## Related

- `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` — full diagnostic walkthrough of why this failure occurs
- `docs/vlan-design.md` — Phase B HSRP status, C1111 VLAN 1 SVI cleanup backlog
- `docs/proxmox-server-build.md` — ARIA VLAN 1 temporary state, Phase C cutover plan
- `ROADMAP.md` — Phase B post-cutover cleanup, Phase C ARIA VLAN 70 migration

---

*Created: Jun 4, 2026*
*Remove after: ARIA → VLAN 70, Comet → VLAN 10, C1111 Vlan1 SVI removed*
