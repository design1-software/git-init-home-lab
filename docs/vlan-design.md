# VLAN Design — JLM Home Lab

> Network segmentation scheme for the home lab. This document reflects the implemented and verified state as of April 19, 2026.

---

## Design Goals

1. **Isolate production workloads** (MCP server, content system) from household and IoT traffic
2. **Prevent IoT lateral movement** — compromised smart devices cannot reach servers or personal devices
3. **Enable controlled cross-VLAN access** for the garage automation system (MQTT + relay control)
4. **Separate management plane** so switch/AP/router admin interfaces aren't on the same broadcast domain as user traffic
5. **Support VLAN-tagged WiFi** via UniFi APs — one AP broadcasts multiple SSIDs, each mapped to a different VLAN
6. **Household isolation** — family devices get internet but cannot reach lab infrastructure

---

## VLAN Assignments

| VLAN ID | Name | Subnet | Gateway (Cisco SVI) | DHCP Range | Purpose |
|---|---|---|---|---|---|
| 1 | DEFAULT | 192.168.100.0/24 | 192.168.100.1 | .11–.254 | Legacy flat network (being phased out) |
| 10 | SERVER | 192.168.10.0/24 | 192.168.10.1 | .11–.254 | Production servers and network services |
| 20 | TRUSTED | 192.168.20.0/24 | 192.168.20.1 | .11–.254 | Personal devices |
| 30 | IOT | 192.168.30.0/24 | 192.168.30.1 | .11–.254 | General smart home devices (cloud-dependent, untrusted) |
| 31 | IOT-AUTO | 192.168.31.0/24 | 192.168.31.1 | .11–.254 | Home automation sensors/actuators (local MQTT, no cloud) |
| 40 | HOUSEHOLD | 192.168.40.0/24 | 192.168.40.1 | .11–.254 | Family devices (internet + AirPlay only) |
| 99 | MGMT | 192.168.99.0/24 | 192.168.99.1 | .11–.50 | Network infrastructure management interfaces |

---

## Device-to-VLAN Mapping

### VLAN 10 — SERVER

| Device | IP | Connection | Notes |
|---|---|---|---|
| Acer Aspire 3 (MCP server) | 192.168.10.17 | Cisco GE0/1/0 (access VLAN 10) | Production 24/7 |
| Raspberry Pi 4B | 192.168.10.16 | GS308EP Port 3 (PoE, access VLAN 10) | Pi-hole + UniFi Controller |
| Future NAS | TBD | GS308EP or GS316EP | Backup storage |

### VLAN 20 — TRUSTED

| Device | IP | Connection | Notes |
|---|---|---|---|
| iMac | DHCP | WiFi (Gorgeous) | Development |
| MacBook Air | DHCP | WiFi (Gorgeous) | Development |
| MacBook Pro | DHCP | WiFi (Gorgeous) | Development |
| iPhones | DHCP | WiFi (Gorgeous) | Personal |
| Apple TV ×3 | Static .101-.103 (planned) | Wired or WiFi (Gorgeous) | AirPlay ACL targets |
| ESP32 closet sensor | DHCP | WiFi (Gorgeous) | Temporary — moves to IOT-AUTO when Mosquitto migrates to Pi |

### VLAN 30 — IOT

| Device | IP | Connection | Notes |
|---|---|---|---|
| Ring cameras + doorbell | DHCP | WiFi (Gorgeous-IoT) | Pending migration from Gorgeous |
| Kasa Smart Plugs | DHCP | WiFi (Gorgeous-IoT) | Pending migration |
| Ecobee thermostat | DHCP | WiFi (Gorgeous-IoT) | ✅ Migrated |
| Amazon Alexa devices | DHCP | WiFi (Gorgeous-IoT) | Pending migration |
| Somfy Hub | DHCP | WiFi (Gorgeous-IoT) | Pending migration |
| Samsung Smart TV | DHCP | WiFi (Gorgeous-IoT) | Pending migration |
| Wyze Cam v3 ×2 | DHCP | WiFi (Gorgeous-IoT) | Stock firmware, Wyze cloud |

### VLAN 31 — IOT-AUTO

| Device | IP | Connection | Notes |
|---|---|---|---|
| ESP32 garage (reed switch + relay) | DHCP | WiFi (Gorgeous-Auto) | Future — door state sensor + closer |
| ESP32 closet sensor | DHCP | WiFi (Gorgeous-Auto) | Future — after Mosquitto migrates to Pi |

### VLAN 40 — HOUSEHOLD

| Device | IP | Connection | Notes |
|---|---|---|---|
| Family phones/tablets/laptops | DHCP | WiFi (Gorgeous-Home) | Internet + AirPlay only |

### VLAN 99 — MGMT

| Device | IP | Connection | Notes |
|---|---|---|---|
| Cisco C1111-4PWB | 192.168.99.1 | SVI (gateway) | Also reachable via console |
| Netgear GS308EP | Floats (no configurable mgmt VLAN) | GS308EP Port 1 trunk, native VLAN 99 | Switch management accessible from any VLAN (hardware limitation) |
| UniFi U6+ AP #1 | DHCP on VLAN 99 | GS308EP Port 4, untagged VLAN 99 | AP management interface |
| UniFi U6+ AP #2 | DHCP on VLAN 99 | GS308EP Port 5, untagged VLAN 99 | AP management interface |

---

## WiFi SSID-to-VLAN Mapping

| SSID | VLAN | Security | Status |
|---|---|---|---|
| `Gorgeous` | 20 (TRUSTED) | WPA2/WPA3 | ✅ Live, tested |
| `Gorgeous-IoT` | 30 (IOT) | WPA2-PSK | ✅ Live, tested |
| `Gorgeous-Auto` | 31 (IOT-AUTO) | WPA2-PSK | ✅ Live, tested |
| `Gorgeous-Home` | 40 (HOUSEHOLD) | WPA2/WPA3 | ✅ Live, tested |

All four SSIDs broadcast on both 2.4 GHz and 5 GHz from both UniFi U6+ APs.

---

## Inter-VLAN Access Control (ACL Matrix)

| From ↓ / To → | SERVER (10) | TRUSTED (20) | IOT (30) | IOT-AUTO (31) | HOUSEHOLD (40) | MGMT (99) | INTERNET |
|---|---|---|---|---|---|---|---|
| **SERVER (10)** | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TRUSTED (20)** | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| **IOT (30)** | DNS only | ❌ | — | ❌ | ❌ | ❌ | ✅ |
| **IOT-AUTO (31)** | DNS + MQTT only | ❌ | ❌ | — | ❌ | ❌ | ❌ |
| **HOUSEHOLD (40)** | DNS only | AirPlay to Apple TV IPs only | ❌ | ❌ | — | ❌ | ✅ |
| **MGMT (99)** | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |

### Implemented ACLs (applied to Cisco SVIs)

**IOT-ACL** (applied inbound on Vlan30):
- Permit DNS (UDP/TCP 53) to Pi-hole (192.168.10.16)
- Deny all private subnets (192.168.x.x)
- Permit all other (internet)

**IOT-AUTO-ACL** (applied inbound on Vlan31):
- Permit DNS (UDP/TCP 53) to Pi-hole (192.168.10.16)
- Permit MQTT (TCP 1883, 8883) to Pi (192.168.10.16)
- Deny all other traffic

**HOUSEHOLD-ACL** (applied inbound on Vlan40):
- Permit DNS to Pi-hole
- Permit AirPlay (mDNS 5353, TCP 7000-7100, TCP 49152-65535) to Apple TV IPs (.101, .102, .103)
- Deny all private subnets
- Permit all other (internet)

SERVER, TRUSTED, and MGMT have no restrictive ACLs — full access by design.

---

## GS308EP Switch Configuration (Advanced 802.1Q)

**Firmware:** V2.0.0.5
**MAC:** 28:94:01:84:2D:8A
**Serial:** 6V665C53A4801

### VLAN Membership Table

| VLAN | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 |
|------|----|----|----|----|----|----|----|----|
| 1    | T  | U  | E  | E  | E  | U  | U  | U  |
| 10   | T  | E  | U  | E  | E  | E  | E  | E  |
| 20   | T  | E  | E  | T  | T  | E  | E  | E  |
| 30   | T  | E  | E  | T  | T  | E  | E  | E  |
| 31   | T  | E  | E  | T  | T  | E  | E  | E  |
| 40   | T  | E  | E  | T  | T  | E  | E  | E  |
| 99   | U  | E  | E  | U  | U  | E  | E  | E  |

### Port PVIDs

| Port | PVID | Role |
|---|---|---|
| 1 | 99 | Trunk to Cisco GE0/1/1 |
| 2 | 1 | Spare access port |
| 3 | 10 | Pi 4B (SERVER) — PoE powered, active |
| 4 | 99 | UniFi U6+ AP #1 (trunk + MGMT native) |
| 5 | 99 | UniFi U6+ AP #2 (trunk + MGMT native) |
| 6 | 1 | Spare access port |
| 7 | 1 | Spare access port |
| 8 | 1 | Spare access port |

### Critical Configuration Notes

1. **VLAN 1 MUST be Tagged (T) on Port 1 (trunk).** Excluding VLAN 1 from the trunk breaks the switch's internal MAC forwarding table. This is per official Netgear documentation — every Netgear example shows the trunk port Tagged in VLAN 1.
2. **The GS308EP has no configurable management VLAN.** Its management interface floats across all VLANs. This is a documented hardware limitation of the Netgear Plus series.
3. **The Cisco trunk must include VLAN 1 in the allowed list** to match: `switchport trunk allowed vlan 1,10,20,30,31,40,99`

---

## Cisco Trunk Configuration

```
interface GigabitEthernet0/1/1
 switchport mode trunk
 switchport trunk allowed vlan 1,10,20,30,31,40,99
 switchport trunk native vlan 99
```

---

## DNS Strategy

All VLANs receive **Pi-hole (192.168.10.16)** as primary DNS via DHCP, with **1.1.1.1 (Cloudflare)** as fallback.

IOT and IOT-AUTO ACLs explicitly permit DNS traffic to the Pi across VLAN boundaries.

---

## Lessons Learned During Implementation

1. **Netgear Basic 802.1Q "Trunk" ≠ Cisco trunk.** Basic mode only forwards switch management frames, not device traffic. Must use Advanced 802.1Q with manual T/U/E assignments.
2. **VLAN 1 must be Tagged on the trunk port** in Netgear Advanced 802.1Q. Excluding it breaks internal MAC learning/forwarding.
3. **Cisco trunk must allow VLAN 1** even if no devices use it, because the Netgear tags VLAN 1 on the trunk.
4. **Pi-hole sets a static IP during installation.** Never override from the network side (DHCP reservation) without changing the Pi's own config first. This caused a multi-hour debugging session.
5. **Always verify cables.** A bad Ethernet cable caused the Pi's MAC to never appear in the Cisco's MAC table, mimicking a switch forwarding failure.
6. **Always follow official documentation.** Community shortcuts and assumptions cost more time than reading the manual.

---

*Implemented and verified: April 19, 2026*
