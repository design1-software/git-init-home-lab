# VLAN Design — JLM Home Lab

> Network segmentation scheme for the home lab. This document reflects the implemented and verified state as of May 19, 2026.

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

### Planned (pending 3560CX cutover)

| VLAN ID | Name | Subnet | Gateway | Purpose |
|---|---|---|---|---|
| 60 | LAB | 192.168.60.0/24 | 192.168.60.1 | Schoolmate remote lab — AD, osTicket, M365 sandbox |
| 70 | SERVER | 192.168.70.0/24 | 192.168.70.1 | Proxmox hypervisor host + VM/LXC traffic |
| 199 | TRANSIT | 192.168.199.0/30 | — | Point-to-point L3 link between C1111 and 3560CX |

---

## Device-to-VLAN Mapping

### VLAN 1 — DEFAULT (Legacy / Switch Management)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Cisco C1111 SVI | 192.168.100.1 | Vlan1 SVI | Legacy gateway — retirement planned at cutover |
| NETGEAR GS308EP | 192.168.100.100 | DHCP reserved (MAC 28:94:01:84:2D:8A) | Web UI: http://192.168.100.100 |
| NETGEAR GS316EP | 192.168.100.96 | DHCP (MAC 28:94:01:7F:A7:F7) | Web UI: http://192.168.100.96 |

### VLAN 10 — MGMT (Production Servers)

| Device | IP | Connection | Notes |
|---|---|---|---|
| Acer Server | 192.168.10.11 | Cisco GE0/1/0 (access VLAN 10) | Docker: social-media-mcp + Ngrok sidecar, Streamlit (:8501) |
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
**Management IP:** 192.168.100.100 (DHCP reserved on C1111)
**Management VLAN:** VLAN 1 (DEFAULT) — hardware limitation, no configurable management VLAN

### VLAN Membership Table (verified May 19, 2026)

| VLAN | Name | Port Members |
|---|---|---|
| 1 | DEFAULT | 1, 2, 6, 7, 8 |
| 10 | SERVER | 1, 3 |
| 20 | TRUSTED | 1, 4, 5 |
| 30 | IOT | 1, 4, 5 |
| 31 | IOT-AUTO | 1, 4, 5 |
| 40 | HOUSEHOLD | 1, 4, 5 |
| 50 | JM&G-GUEST | 1, 4, 5 |
| 99 | MGMT | 1, 4, 5 |

### Port PVID Table (verified May 19, 2026)

| Port | PVID | VLANs | Role |
|---|---|---|---|
| 1 | 99 | 1,10,20,30,31,40,50,99 | Trunk to Cisco GE0/1/1 |
| 2 | 1 | 1 | Spare |
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
4. **GS308EP management IP is DHCP-reserved at 192.168.100.100** via C1111 DHCP pool (client-identifier 2894.0184.2d8a). IP locked permanently.

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

### ⚠️ Known Gap — VLAN 50 Missing from GS316EP

VLAN 50 (JM&G-GUEST) is not present in the GS316EP VLAN membership table and is not carried on Port 15 trunk. This means no wired guest access is possible through the GS316EP. Currently not an issue since JM&G-GUEST is WiFi only, but must be added before any wired guest port is needed.

**Fix required:** Add VLAN 50 to GS316EP VLAN membership table and to Port 15 as Tagged.

---

## Cisco Trunk Configuration (verified May 19, 2026)

```
interface GigabitEthernet0/1/1
 switchport trunk native vlan 99
 switchport trunk allowed vlan 1,10,20,30,31,40,50,99
 switchport mode trunk

interface GigabitEthernet0/1/2
 switchport trunk native vlan 99
 switchport trunk allowed vlan 1,10,20,30,31,40,50,99
 switchport mode trunk
```

> At Phase B cutover, GE0/1/1 will trunk to the 3560CX uplink. GE0/1/2 trunk to GS316EP remains unchanged.

---

## DNS Strategy

All VLANs receive **Pi-hole (192.168.10.16)** as primary DNS via DHCP, with **1.1.1.1 (Cloudflare)** as fallback. IOT, IOT-AUTO, HOUSEHOLD, and GUEST ACLs explicitly permit DNS traffic to the Pi across VLAN boundaries. At 3560CX cutover, DHCP pools and DNS assignments migrate to the 3560CX — Pi-hole IP does not change.

---

## Lessons Learned During Implementation

1. **Netgear Basic 802.1Q ≠ Cisco trunk.** Must use Advanced 802.1Q with manual T/U/E assignments.
2. **VLAN 1 must be present on the trunk port** in Netgear Advanced 802.1Q or internal MAC learning breaks.
3. **Cisco trunk must allow VLAN 1** to match Netgear tagging behavior.
4. **VLAN 50 must be explicitly added to all AP ports.** Missing from Port 4 caused guest SSID to broadcast from only one AP. Corrected May 19, 2026.
5. **GS308EP management IP floats on VLAN 1.** Lock it with a DHCP reservation on the C1111 to prevent it changing on reboot.
6. **Pi-hole sets a static IP during installation.** Never override from the network side without changing the Pi config first.
7. **Apple TVs require DHCP, not static IPs.** Static IP configuration causes app connectivity failures.
8. **Pi-hole blocks Apple service domains by default.** Whitelist: gsa.apple.com, configuration.apple.com, apps.apple.com.
9. **TCP MSS clamping value is 1380** (`ip tcp adjust-mss 1380`) on C1111 WAN interface — verified from live config. Earlier docs incorrectly stated 1452.
10. **IOT-AUTO-ACL deny-all must come after DHCP permits.** Missing `permit udp any any eq 67/68` before deny caused 169.254.x.x addresses on VLAN 31.

---

*Implemented and verified: May 19, 2026*