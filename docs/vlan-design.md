# VLAN Design — JLM Home Lab

> Network segmentation scheme for the home lab. This document reflects the implemented and verified state as of May 31, 2026.

---

## Design Goals

1. **Isolate production workloads** (MCP server, content system) from household and IoT traffic
2. **Prevent IoT lateral movement** — compromised smart devices cannot reach servers or personal devices
3. **Enable controlled cross-VLAN access** for the garage automation system (MQTT + relay control)
4. **Separate management plane** — VLAN 99 is the native/management VLAN on all trunks; AP and switch management interfaces live here
5. **Support VLAN-tagged WiFi** via UniFi APs — one AP broadcasts multiple SSIDs, each mapped to a different VLAN
6. **Household isolation** — family devices get internet but cannot reach lab infrastructure
7. **Future server isolation** — VLAN 70 (SERVER) reserved for Proxmox host; VLAN 60 (LAB) reserved for schoolmate remote lab

---

## VLAN Assignments

### Currently Active

| VLAN ID | Name | Subnet | Gateway (Cisco SVI) | DHCP Range | Purpose |
|---|---|---|---|---|---|
| 1 | DEFAULT | 192.168.100.0/24 | 192.168.100.1 | .11–.254 | Legacy flat network — switch management floats here; retirement planned at 3560CX cutover |
| 10 | MGMT | 192.168.10.0/24 | 192.168.10.1 | .11–.254 | Production servers and network services (Pi, Acer) |
| 20 | TRUSTED | 192.168.20.0/24 | 192.168.20.1 | .11–.254 | Personal devices (MacBooks, iPhones) |
| 30 | IOT | 192.168.30.0/24 | 192.168.30.1 | .11–.254 | General smart home devices (cloud-dependent, untrusted) |
| 31 | IOT-AUTO | 192.168.31.0/24 | 192.168.31.1 | .11–.254 | Home automation sensors/actuators (local MQTT, no cloud) |
| 40 | HOUSEHOLD | 192.168.40.0/24 | 192.168.40.1 | .11–.254 | Family devices (internet only) |
| 50 | JM&G-GUEST | 192.168.50.0/24 | 192.168.50.1 | .11–.254 | Guest internet access, client isolation |
| 99 | MGMT/NATIVE | 192.168.99.0/24 | 192.168.99.1 | .11–.50 | Native VLAN on all trunks — AP management |

### Currently Active (continued)

| VLAN ID | Name | Subnet | Gateway | Purpose |
|---|---|---|---|---|
| 199 | TRANSIT | 192.168.199.0/30 | — | Active Phase B routed transit between C1111 and 3560CX — OSPFv2 adjacency FULL (May 31, 2026) |

### Planned (pending 3560CX cutover)

| VLAN ID | Name | Subnet | Gateway | Purpose |
|---|---|---|---|---|
| 60 | LAB | 192.168.60.0/24 | 192.168.60.1 | Schoolmate remote lab — AD, osTicket, M365 sandbox |
| 70 | SERVER | 192.168.70.0/24 | 192.168.70.1 | Proxmox hypervisor host + VM/LXC traffic |

---

## Device-to-VLAN Mapping

### VLAN 1 — DEFAULT (Legacy / Switch Management)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Cisco C1111 SVI | 192.168.100.1 | Vlan1 SVI | Legacy gateway — retirement planned at cutover |
| NETGEAR GS308EP | 192.168.100.95 | DHCP reserved (MAC 28:94:01:84:2D:8A) | Web UI: http://192.168.100.95 |
| NETGEAR GS316EP | 192.168.100.96 | DHCP (MAC 28:94:01:7F:A7:F7) | Web UI: http://192.168.100.96 |

### VLAN 10 — MGMT (Production Servers)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Acer Server | 192.168.10.11 | GS308EP Port 2 (VLAN 10, moved May 31, 2026) | Docker: social-media-mcp + Ngrok sidecar, Streamlit (:8501) |
| Raspberry Pi 4B | 192.168.10.16 | GS308EP Port 3 (PoE, access VLAN 10) | Pi-hole, UniFi Controller, Mosquitto MQTT, CUPS |
| HP ENVY Inspire 7200e | — | USB to Pi 4B | Print queue via CUPS (USB path only; WiFi on VLAN 30) |

### VLAN 20 — TRUSTED

| Device | IP | Connection | Notes |
|---|---|---|---|
| MacBook Pro | DHCP | WiFi (Gorgeous) | Development + fb-content-system |
| MacBook Air | DHCP | WiFi (Gorgeous) | Development |
| iMac | DHCP | WiFi (Gorgeous) | Development |
| iPhones | DHCP | WiFi (Gorgeous) | Personal |
| Apple TV ×3 | DHCP | GS316EP Ports 2–4 (wired, VLAN 20) | DHCP required — static IPs cause app failures |

### VLAN 30 — IOT

| Device | IP | Connection | Notes |
|---|---|---|---|
| HP ENVY Inspire 7200e | DHCP | WiFi (Gorgeous-IoT) | WiFi for HP Instant Ink only; printing via USB/CUPS on VLAN 10 |
| Ring cameras + doorbell | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Kasa EP10 Smart Plugs ×4 | DHCP | WiFi (Gorgeous-IoT) | ⏳ Pending — app issue blocking migration |
| Ecobee thermostat | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Amazon Alexa devices ×3 | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Somfy Hub | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Samsung Smart TV | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Wyze Cam v3 ×2 | DHCP | WiFi (Gorgeous-IoT) | Stock firmware, Wyze cloud |

### VLAN 31 — IOT-AUTO

| Device | IP | Connection | Notes |
|---|---|---|---|
| ESP32 closet sensor | DHCP | WiFi (Gorgeous-Auto) | ✅ Active — BME280, MQTT to Pi (192.168.10.16:1883) |
| ESP32 garage (reed switch + relay) | DHCP | WiFi (Gorgeous-Auto) | Planned — door state sensor + closer |

### VLAN 40 — HOUSEHOLD

| Device | IP | Connection | Notes |
|---|---|---|---|
| Family phones/tablets/laptops | DHCP | WiFi (Gorgeous-Home) | Internet only |

### VLAN 50 — JM&G-GUEST

| Device | IP | Connection | Notes |
|---|---|---|---|
| Guest devices | DHCP | WiFi (JM&G-GUEST) | Internet only, client isolation enforced in UniFi |

### VLAN 99 — MGMT/NATIVE

| Device | IP | Connection | Notes |
|---|---|---|---|
| Cisco C1111 SVI | 192.168.99.1 | Vlan99 SVI | Also reachable via console |
| UniFi U6+ AP #1 | 192.168.99.12 | GS308EP Port 4, native VLAN 99 | AP management interface |
| UniFi U6+ AP #2 | 192.168.99.11 | GS308EP Port 5, native VLAN 99 | AP management interface |

### VLAN 70 — SERVER (planned)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Custom Proxmox Server | Static TBD | Trunk to GS308EP | Ryzen 9 7900X, dual NIC — mgmt on VLAN 70, VM traffic on VLANs 60/70 |

### VLAN 60 — LAB (planned)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Active Directory VM | DHCP or static | Proxmox, VLAN 60 | Windows Server 2022 Eval |
| osTicket VM | DHCP or static | Proxmox, VLAN 60 | Help desk ticketing for schoolmate lab |
| M365 admin sandbox | DHCP or static | Proxmox, VLAN 60 | Remote access via Tailscale subnet routing |

---

## WiFi SSID-to-VLAN Mapping

| SSID | VLAN | Security | Band | Status |
|---|---|---|---|---|
| Gorgeous | 20 (TRUSTED) | WPA2/WPA3 | 2.4 + 5 GHz | ✅ Live |
| Gorgeous-IoT | 30 (IOT) | WPA2-PSK | 2.4 GHz | ✅ Live |
| Gorgeous-Auto | 31 (IOT-AUTO) | WPA2-PSK | 2.4 GHz | ✅ Live |
| Gorgeous-Home | 40 (HOUSEHOLD) | WPA2/WPA3 | 2.4 + 5 GHz | ✅ Live |
| JM&G-GUEST | 50 (JM&G-GUEST) | WPA2/WPA3, client isolation | 5 GHz | ✅ Live |

---

## Inter-VLAN Access Control (ACL Matrix)

### Current (active on C1111)

| From ↓ / To → | MGMT (10) | TRUSTED (20) | IOT (30) | IOT-AUTO (31) | HOUSEHOLD (40) | GUEST (50) | NATIVE (99) | INTERNET |
|---|---|---|---|---|---|---|---|---|
| **MGMT (10)** | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TRUSTED (20)** | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **IOT (30)** | DNS only | ❌ | — | ❌ | ❌ | ❌ | ❌ | ✅ |
| **IOT-AUTO (31)** | DNS+MQTT only | ❌ | ❌ | — | ❌ | ❌ | ❌ | ❌ |
| **HOUSEHOLD (40)** | DNS only | ❌ | ❌ | ❌ | — | ❌ | ❌ | ✅ |
| **GUEST (50)** | DNS only | ❌ | ❌ | ❌ | ❌ | — | ❌ | ✅ |
| **NATIVE (99)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |

### Planned additions at 3560CX cutover

| From ↓ / To → | SERVER (70) | LAB (60) |
|---|---|---|
| **SERVER (70)** | — | ✅ |
| **LAB (60)** | DNS + AD services only | — |
| **MGMT (10)** | ✅ | ✅ |
| **TRUSTED (20)** | ✅ | ❌ |
| **All others** | ❌ | ❌ |

---

## Implemented ACLs (applied to Cisco C1111 SVIs)

**IOT-ACL** (applied inbound on Vlan30):
```
permit udp any host 192.168.10.16 eq 53
permit tcp any host 192.168.10.16 eq 53
deny   ip any 192.168.10.0 0.0.0.255
deny   ip any 192.168.20.0 0.0.0.255
deny   ip any 192.168.30.0 0.0.0.255
deny   ip any 192.168.31.0 0.0.0.255
deny   ip any 192.168.40.0 0.0.0.255
deny   ip any 192.168.99.0 0.0.0.255
deny   ip any 192.168.100.0 0.0.0.255
permit ip any any
```

**IOT-AUTO-ACL** (applied inbound on Vlan31):
```
permit udp any host 192.168.10.16 eq 53
permit tcp any host 192.168.10.16 eq 53
permit tcp any host 192.168.10.16 eq 1883
permit tcp any host 192.168.10.16 eq 8883
permit udp any any eq 67
permit udp any any eq 68
deny   ip any any
```

**HOUSEHOLD-ACL** (applied inbound on Vlan40):
```
permit udp any host 192.168.10.16 eq 53
permit tcp any host 192.168.10.16 eq 53
deny   ip any 192.168.10.0 0.0.0.255
deny   ip any 192.168.20.0 0.0.0.255
deny   ip any 192.168.30.0 0.0.0.255
deny   ip any 192.168.31.0 0.0.0.255
deny   ip any 192.168.40.0 0.0.0.255
deny   ip any 192.168.99.0 0.0.0.255
deny   ip any 192.168.100.0 0.0.0.255
permit ip any any
```

**GUEST-ACL** (applied inbound on Vlan50):
```
permit udp any host 192.168.10.16 eq 53
permit tcp any host 192.168.10.16 eq 53
deny   ip any 192.168.10.0 0.0.0.255
deny   ip any 192.168.20.0 0.0.0.255
deny   ip any 192.168.30.0 0.0.0.255
deny   ip any 192.168.31.0 0.0.0.255
deny   ip any 192.168.40.0 0.0.0.255
deny   ip any 192.168.50.0 0.0.0.255
deny   ip any 192.168.99.0 0.0.0.255
deny   ip any 192.168.100.0 0.0.0.255
permit ip any any
```

> ⚠️ All ACLs migrate to the 3560CX at cutover. New ACLs for VLANs 60 and 70 added at that time.

---

## GS308EP Switch Configuration (Advanced 802.1Q)

**Model:** NETGEAR GS308EP
**Firmware:** V2.0.0.5
**MAC:** 28:94:01:84:2D:8A
**Serial:** 6V665C53A4801
**Management IP:** 192.168.100.95 (DHCP reserved on C1111)
**Management VLAN:** VLAN 1 (DEFAULT) — hardware limitation, no configurable management VLAN

### VLAN Membership Table (verified May 31, 2026)

| VLAN | Name | Port Members |
|---|---|---|
| 1 | DEFAULT | 1, 6, 7, 8 |
| 10 | SERVER | 1, 2, 3 |
| 20 | TRUSTED | 1, 4, 5 |
| 30 | IOT | 1, 4, 5 |
| 31 | IOT-AUTO | 1, 4, 5 |
| 40 | HOUSEHOLD | 1, 4, 5 |
| 50 | JM&G-GUEST | 1, 4, 5 |
| 99 | MGMT | 1, 4, 5 |

### Port PVID Table (verified May 31, 2026)

| Port | PVID | VLANs | Role |
|---|---|---|---|
| 1 | 99 | 1,10,20,30,31,40,50,99 | Trunk to Cisco GE0/1/1 |
| 2 | 10 | 10 | Acer Server (192.168.10.11) |
| 3 | 10 | 10 | Pi 4B (PoE, VLAN 10) |
| 4 | 99 | 20,30,31,40,50,99 | UniFi AP #1 |
| 5 | 99 | 20,30,31,40,50,99 | UniFi AP #2 |
| 6 | 1 | 1 | Spare |
| 7 | 1 | 1 | Spare |
| 8 | 1 | 1 | Spare |

### Critical Configuration Notes

1. **VLAN 1 must be present on Port 1 (trunk).** Excluding VLAN 1 breaks the switch's internal MAC forwarding table. Per official Netgear documentation.
2. **VLAN 50 must be on both AP ports (4 and 5).** Required for JM&G-GUEST SSID to broadcast from both APs. Corrected May 19, 2026 — Port 4 was missing VLAN 50.
3. **GS308EP has no configurable management VLAN.** Management interface floats on VLAN 1 (DEFAULT). This is a documented hardware limitation.
4. **GS308EP management IP is 192.168.100.95** — acquired via regular DHCP. The C1111 DHCP reservation for .100 (client-identifier 2894.0184.2d8a) is stuck in Selecting state; reservation is not functioning. Switch will float to whatever DHCP assigns. Cleanup task: investigate reservation after Stage 2 cutover.

---

## GS316EP Switch Configuration (Advanced 802.1Q)

**Model:** NETGEAR GS316EP
**MAC:** 28:94:01:7F:A7:F7
**Management IP:** 192.168.100.96 (DHCP, floats — no reservation set)
**Management VLAN:** VLAN 1 (DEFAULT) — hardware limitation

### VLAN Membership Table (verified May 19, 2026)

| VLAN | Name | Port Members |
|---|---|---|
| 1 | DEFAULT | 1,5,6,7,8,9,10,11,12,13,14,15,16 |
| 10 | SERVER | 15 |
| 20 | TRUSTED | 2,3,4,15 |
| 30 | IOT | 15 |
| 31 | IOT-AUTO | 15 |
| 40 | HOUSEHOLD | 15 |
| 99 | MGMT | 15 |

### Port Assignments

| Port | PVID | Role |
|---|---|---|
| 1 | 1 | Spare |
| 2 | 20 | Apple TV (Front Bedroom) |
| 3 | 20 | Apple TV (Living Room) |
| 4 | 20 | Apple TV (Master Bedroom) |
| 5–14 | 1 | Wall outlets (spare) |
| 15 | 1 | Trunk to Cisco GE0/1/2 — carries VLANs 1,10,20,30,31,40,99 |
| 16 | — | SFP (fiber only, not RJ-45 — do not use) |

### VLAN 50 on GS316EP — Resolved May 19, 2026

VLAN 50 (JM&G-GUEST) added to GS316EP membership table and Port 15 as Tagged.

**Fix required:** Add VLAN 50 to GS316EP VLAN membership table and to Port 15 as Tagged.

---

## Cisco C1111 Port Configuration (updated May 31, 2026)

```
! Trunk to GS308EP (unchanged)
interface GigabitEthernet0/1/1
 switchport trunk native vlan 99
 switchport trunk allowed vlan 1,10,20,30,31,40,50,99
 switchport mode trunk

! Trunk to GS316EP (unchanged)
interface GigabitEthernet0/1/2
 switchport trunk native vlan 99
 switchport trunk allowed vlan 1,10,20,30,31,40,50,99
 switchport mode trunk

! TRANSIT to 3560CX — access port in VLAN 199 (NIM-ES2 is L2-only; routed via SVI)
vlan 199
 name TRANSIT
interface GigabitEthernet0/1/0
 description TRANSIT-TO-3560CX
 switchport mode access
 switchport access vlan 199
 no shutdown

! TRANSIT SVI — C1111 side of /30
interface Vlan199
 ip address 192.168.199.1 255.255.255.252
 ip nat inside
 no shutdown

! OSPFv2 — additive to pre-existing process 1 (Step 1.3, May 31, 2026)
! Note: router-id 1.1.1.1, passive-interface default, Loopback0, and all VLAN
! network statements were already present from prior lab work.
router ospf 1
 network 192.168.199.0 0.0.0.3 area 0   ! brings Vlan199 into OSPF
 default-information originate           ! advertises default route to 3560CX as O*E2
 no passive-interface Vlan199            ! allows hellos on TRANSIT SVI only
```

> **Hardware constraint:** C1111-4PWB GE0/1/0–0/1/3 are on the NIM-ES2 module — Layer 2 only. `no switchport` is unavailable on these ports. TRANSIT L3 is implemented on Vlan199 SVI; the physical port is an access port in VLAN 199. OSPF runs on the SVI, not the physical port — `no passive-interface Vlan199` (not GigabitEthernet0/1/0) is the correct command.

> GE0/1/1 will become the uplink to the 3560CX at Phase B cabling. GE0/1/2 trunk to GS316EP remains unchanged.

---

## Phase B HSRP Status (Jun 1, 2026)

HSRP is currently staged on the Cisco Catalyst 3560CX only.

The 3560CX uses physical SVI addresses ending in `.2` and staged HSRP virtual gateway addresses ending in `.1` for the active production VLANs. This preserves the existing client default-gateway convention after the Phase B cutover — no client reconfiguration required.

### HSRP groups configured on 3560CX

| VLAN | Name | 3560CX Physical SVI | HSRP Virtual Gateway (VIP) |
|---|---|---|---|
| 1 | DEFAULT | 192.168.100.2 | 192.168.100.1 |
| 10 | MGMT | 192.168.10.2 | 192.168.10.1 |
| 20 | TRUSTED | 192.168.20.2 | 192.168.20.1 |
| 30 | IOT | 192.168.30.2 | 192.168.30.1 |
| 31 | IOT-AUTO | 192.168.31.2 | 192.168.31.1 |
| 40 | HOUSEHOLD | 192.168.40.2 | 192.168.40.1 |
| 50 | JM&G-GUEST | 192.168.50.2 | 192.168.50.1 |
| 99 | MGMT/NATIVE | 192.168.99.2 | 192.168.99.1 |

### Current status

- C1111 is **not** configured as an HSRP peer.
- This is **not** true gateway redundancy — it is gateway IP preservation during ownership transfer from C1111 to 3560CX.
- After the Phase B trunk move, the C1111 will no longer be Layer-2 adjacent to the production VLANs and cannot participate in HSRP for those segments.

### Role split post-cutover

| Device | Role |
|---|---|
| C1111 | WAN edge, NAT/PAT, default route originator, OSPF neighbor over VLAN 199 |
| 3560CX | LAN L3 core, VLAN gateways (via HSRP VIPs), inter-VLAN ACLs, DHCP |
| GS308EP / GS316EP | Access-layer switches |

### ⚠️ Critical cutover risk — IP conflict

The C1111 currently owns `.1` as **physical SVI addresses** on all production VLANs. The 3560CX has **staged HSRP virtual `.1` addresses** for those same VLANs. These must not be active on the same Layer-2 segment simultaneously — doing so would create an IP conflict and disrupt all VLAN gateways.

**The Phase B trunk migration must be break-before-make:**
1. Disconnect production trunks from C1111 (GE0/1/1 from GS308EP Port 1, GE0/1/2 from GS316EP Port 15)
2. Connect production trunks to 3560CX (Gi0/2 to GS308EP Port 1, Gi0/3 to GS316EP Port 15)

### True HSRP redundancy — deferred

True redundancy requires both devices to share Layer-2 adjacency on the routed VLANs, with unique physical SVI addresses and a shared virtual gateway address. After Phase B, the C1111 will not be L2-adjacent to the production VLANs, making it ineligible as an HSRP peer for those segments. Deferred to a later design phase.

---

## DNS Strategy

All VLANs receive **Pi-hole (192.168.10.16)** as primary DNS via DHCP, with **1.1.1.1 (Cloudflare)** as fallback. IOT, IOT-AUTO, HOUSEHOLD, and GUEST ACLs explicitly permit DNS traffic to the Pi across VLAN boundaries. At 3560CX cutover, DHCP pools and DNS assignments migrate to the 3560CX — Pi-hole IP does not change.

---

## Lessons Learned During Implementation

1. **Netgear Basic 802.1Q ≠ Cisco trunk.** Must use Advanced 802.1Q with manual T/U/E assignments.
2. **VLAN 1 must be present on the trunk port** in Netgear Advanced 802.1Q or internal MAC learning breaks.
3. **Cisco trunk must allow VLAN 1** to match Netgear tagging behavior.
4. **VLAN 50 must be explicitly added to all AP ports.** Missing from Port 4 caused guest SSID to broadcast from only one AP. Corrected May 19, 2026.
5. **GS308EP management IP floats on VLAN 1.** DHCP reservation for .100 is not functioning (stuck in Selecting). IP is currently .95. Cleanup task post-Stage 2.
6. **Pi-hole sets a static IP during installation.** Never override from the network side without changing the Pi config first.
7. **Apple TVs require DHCP, not static IPs.** Static IP configuration causes app connectivity failures.
8. **Pi-hole blocks Apple service domains by default.** Whitelist: gsa.apple.com, configuration.apple.com, apps.apple.com.
9. **TCP MSS clamping value is 1380** (`ip tcp adjust-mss 1380`) on C1111 WAN interface — verified from live config. Earlier docs incorrectly stated 1452.
10. **IOT-AUTO-ACL deny-all must come after DHCP permits.** Missing `permit udp any any eq 67/68` before deny caused 169.254.x.x addresses on VLAN 31.
11. **C1111-4PWB GE0/1/0–0/1/3 are L2-only (NIM-ES2 module).** `no switchport` fails on these ports — you cannot create a routed L3 interface directly. TRANSIT L3 requires placing an SVI on a dedicated VLAN and putting the physical port in access mode for that VLAN. Confirmed May 31, 2026 against Cisco IOS XE docs and community examples for this exact platform.
12. **IOS labels DHCP-learned default routes as "static" in `show ip route`.** The AD 254 (vs. 1 for true static) is the distinguishing marker. AD 254 is intentionally low-priority so any dynamic routing protocol (OSPF 110, EIGRP 90, BGP 20) wins automatically. The C1111's WAN default (174.53.x.x from Comcast) is DHCP-learned — correct, self-healing behavior.
13. **NAT-INSIDE ACL must include every `ip nat inside` subnet.** When Vlan199 (TRANSIT) was given `ip nat inside`, `permit 192.168.199.0 0.0.0.3` was added to the NAT-INSIDE ACL to match. Missing this causes asymmetric NAT failures for traffic originating from the TRANSIT segment.

---

*Implemented and verified: May 31, 2026*