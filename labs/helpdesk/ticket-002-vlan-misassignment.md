# Helpdesk Ticket 002 — Device on Wrong VLAN

**Domain:** VLAN / Switching / DHCP
**Difficulty:** Beginner
**Estimated time:** 25–35 minutes
**CCNA domain:** Network Access (Domain 2)

---

## Scenario

A student reports: *"My device is connected to Gorgeous-IoT WiFi and it shows connected, but there's no internet. Other IoT devices on the same SSID are working fine."*

The device is receiving a 192.168.100.x address instead of the expected 192.168.30.x (VLAN 30 IOT range).

---

## Ticket Details

**Reported by:** Lab user
**Affected system:** Client device, switch port VLAN assignment
**Priority:** Medium
**Category:** Network — VLAN / DHCP

---

## AI Mentor Opening Questions

```
1. What IP address does the device have? (Settings → WiFi → network details, or ipconfig/ip addr)
2. What subnet is it on? (expected: 192.168.30.x)
3. What gateway is it showing?
4. Can the device ping its gateway?
5. What SSID is it connected to?
6. Has this device worked on this SSID before?
```

---

## Evidence Required

```
- IP address and subnet mask on affected device
- Default gateway shown to device
- SSID connected to
- Can it ping gateway? (yes/no)
- Nearby working device IP address on same SSID (for comparison)
```

---

## Diagnostic Path

```
If device has 192.168.100.x IP:
  → Device is on VLAN 1 (DEFAULT) instead of VLAN 30 (IOT)
  → This means the WiFi frame is arriving untagged or with wrong VLAN tag
  → Check: is the AP port correctly configured? (GS308EP Ports 4/5)
  → Check: is VLAN 30 in the port's membership with correct T/U assignment?
  → Check UniFi controller: is Gorgeous-IoT network mapped to VLAN 30?

If device has 169.254.x.x IP:
  → DHCP not responding for the assigned VLAN
  → Check DHCP pool for VLAN 30 on the switch/router
  → Check VLAN 30 SVI is up/up

If device has correct 192.168.30.x IP but no internet:
  → ACL issue — IOT-ACL applied inbound on Vlan30
  → Verify ACL permits DNS to Pi-hole and internet
  → Check: does the device need a specific port that IOT-ACL blocks?
```

---

## Expected Root Causes

| Root cause | Likelihood | Verification |
|---|---|---|
| AP port missing VLAN 30 membership | High | GS308EP VLAN membership table |
| UniFi SSID VLAN mapping wrong | Medium | UniFi controller → Networks → Gorgeous-IoT |
| VLAN 30 DHCP pool not running | Low | `show ip dhcp pool` on switch/router |
| IOT-ACL blocking needed traffic | Low | `show ip access-lists` on router |

---

## Lab Reference

GS308EP required VLAN membership for AP ports (4, 5):
```
VLAN 20 (TRUSTED): Tagged
VLAN 30 (IOT): Tagged
VLAN 31 (IOT-AUTO): Tagged
VLAN 40 (HOUSEHOLD): Tagged
VLAN 50 (JM&G-GUEST): Tagged
VLAN 99 (NATIVE): Untagged (PVID)
```

If VLAN 30 is missing from Ports 4 or 5, IoT devices land on VLAN 1 instead.

---

## Resolution Path

1. Confirm device IP and identify the wrong VLAN
2. Check GS308EP VLAN membership for AP ports (4, 5)
3. If VLAN 30 missing: add it as Tagged in the Advanced 802.1Q UI
4. Force device to reconnect (disconnect/reconnect WiFi)
5. Verify new IP is in 192.168.30.x range
6. Confirm internet access

---

## Documentation Prompt

```
Write a short incident summary:
- Reported symptom
- What indicated the device was on the wrong VLAN (which IP)
- Where the misconfiguration was found
- What was changed to fix it
- How you verified the device received the correct IP after the fix
```

---

## Learning Objectives

- Use IP address range to identify which VLAN a device is on
- Understand relationship between SSID, VLAN tag, and switch port configuration
- Navigate Netgear GS308EP Advanced 802.1Q VLAN membership table
- Understand that removing a VLAN from an AP port causes devices to land on the untagged/default VLAN
- Practice confirming fix by re-checking DHCP lease, not just "does it work"
