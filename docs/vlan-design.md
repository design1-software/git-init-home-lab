# VLAN Design — JLM Home Lab

> Network segmentation scheme for the home lab. This document captures the final design decisions. Implementation details (Cisco commands, switch config, UniFi settings) will be documented separately during the implementation session.

---

## Design Goals

1. **Isolate production workloads** (MCP server, content system) from household and IoT traffic
2. **Prevent IoT lateral movement** — compromised smart devices cannot reach servers or personal devices
3. **Enable controlled cross-VLAN access** for the garage automation system (MQTT + relay control)
4. **Separate management plane** so switch/AP/router admin interfaces aren't on the same broadcast domain as user traffic
5. **Support VLAN-tagged WiFi** via UniFi APs — one AP broadcasts multiple SSIDs, each mapped to a different VLAN

---

## VLAN Assignments

| VLAN ID | Name | Subnet | Gateway (Cisco SVI) | DHCP Range | Purpose |
|---|---|---|---|---|---|
| 10 | SERVER | 192.168.10.0/24 | 192.168.10.1 | .11–.254 | Production servers and network services |
| 20 | TRUSTED | 192.168.20.0/24 | 192.168.20.1 | .11–.254 | Personal devices + household devices |
| 30 | IOT | 192.168.30.0/24 | 192.168.30.1 | .11–.254 | General smart home devices (cloud-dependent, untrusted) |
| 31 | IOT-AUTO | 192.168.31.0/24 | 192.168.31.1 | .11–.254 | Home automation sensors/actuators (local MQTT, no cloud) |
| 99 | MGMT | 192.168.99.0/24 | 192.168.99.1 | .11–.50 | Network infrastructure management interfaces |

All VLANs use /24 subnets. Addresses .1–.10 reserved per VLAN for static assignments (gateways, critical infrastructure).

---

## Device-to-VLAN Mapping

### VLAN 10 — SERVER

| Device | IP (static/reserved) | Connection | Notes |
|---|---|---|---|
| Acer Aspire 3 (MCP server) | 192.168.10.12 | Wired → Cisco or GS308EP | Production 24/7, runs social-media-mcp + fb-content-system + Ngrok |
| Raspberry Pi 4B | 192.168.10.17 | PoE → GS308EP | Pi-hole, UniFi Controller, future Mosquitto + Node-RED |
| Future NAS | TBD | Wired → GS308EP or GS316EP | Backup storage, media |
| Future Pi 5 + AI HAT+ | TBD | PoE → GS308EP | Only if camera-based detection is added later |

### VLAN 20 — TRUSTED

| Device | IP | Connection | Notes |
|---|---|---|---|
| iMac | DHCP | Wired or WiFi (`Gorgeous`) | Development / personal |
| MacBook Air | DHCP | WiFi (`Gorgeous`) | Development / personal |
| MacBook Pro | DHCP | WiFi (`Gorgeous`) | Development / personal |
| iPhones | DHCP | WiFi (`Gorgeous`) | Personal |
| iPads / tablets | DHCP | WiFi (`Gorgeous`) | Personal |
| Apple TV ×3 | DHCP | Wired or WiFi (`Gorgeous`) | Streaming; needs AirPlay/HomeKit to phones |
| Dell Monitor | N/A | HDMI to Acer | Display only, no network |

### VLAN 30 — IOT

| Device | IP | Connection | Notes |
|---|---|---|---|
| Kasa Smart Plug EP10 ×4 | DHCP | WiFi (`Gorgeous-IoT`) | Remote power management |
| Ecobee thermostat | DHCP | WiFi (`Gorgeous-IoT`) | Climate control |
| Amazon Alexa ×3 | DHCP | WiFi (`Gorgeous-IoT`) | Voice control |
| Somfy Hub | DHCP | WiFi (`Gorgeous-IoT`) | Blind/shade automation |
| Samsung Smart TV | DHCP | WiFi (`Gorgeous-IoT`) | Display (streaming via Apple TV, not direct) |
| Wyze Cam v3 ×2 | DHCP | WiFi (`Gorgeous-IoT`) | Stock firmware, Wyze cloud, general security |

### VLAN 31 — IOT-AUTO

| Device | IP | Connection | Notes |
|---|---|---|---|
| ESP32 (garage reed switch + relay) | DHCP or static | WiFi (`Gorgeous-Auto`) | Door state sensor + closer actuator; MQTT only |
| Future automation actuators | DHCP | WiFi (`Gorgeous-Auto`) | Additional ESP32 sensors/relays as needed |

### VLAN 99 — MGMT

| Device | IP (static) | Connection | Notes |
|---|---|---|---|
| Cisco C1111-4PWB | 192.168.99.1 | SVI (gateway) | Also reachable via console for recovery |
| Netgear GS308EP | 192.168.99.2 | Wired (native VLAN 99) | Switch management UI |
| Netgear GS316EP | 192.168.99.3 | Wired (native VLAN 99) | Switch management UI (after migration to Cisco) |
| UniFi U6+ AP #1 | 192.168.99.11 | PoE → GS308EP (mgmt on VLAN 99) | AP management interface |
| UniFi U6+ AP #2 | 192.168.99.12 | PoE → GS308EP (mgmt on VLAN 99) | AP management interface |

---

## WiFi SSID-to-VLAN Mapping

| SSID | VLAN | Security | Devices |
|---|---|---|---|
| `Gorgeous` | 20 (TRUSTED) | WPA3/WPA2 Transition | Phones, laptops, tablets, Apple TVs |
| `Gorgeous-IoT` | 30 (IOT) | WPA2-PSK | Smart home devices (older IoT often can't do WPA3) |
| `Gorgeous-Auto` | 31 (IOT-AUTO) | WPA2-PSK | ESP32 automation devices |

Three SSIDs is the target. Both UniFi U6+ APs broadcast all three simultaneously on both 2.4 GHz and 5 GHz bands. The VLAN tag is applied at the AP based on which SSID the client joins.

---

## Inter-VLAN Access Control (ACL Matrix)

| From ↓ / To → | SERVER (10) | TRUSTED (20) | IOT (30) | IOT-AUTO (31) | MGMT (99) | INTERNET |
|---|---|---|---|---|---|---|
| **SERVER (10)** | — | ✅ Allow | ❌ Deny | ✅ Specific (RTSP pull, MQTT response) | ❌ Deny | ✅ Allow |
| **TRUSTED (20)** | ✅ Allow | — | ✅ Allow | ✅ Allow | ✅ Allow | ✅ Allow |
| **IOT (30)** | ❌ Deny | ❌ Deny | — | ❌ Deny | ❌ Deny | ✅ Allow |
| **IOT-AUTO (31)** | ✅ Specific (MQTT publish only) | ❌ Deny | ❌ Deny | — | ❌ Deny | ⚠️ Limited / Deny |
| **MGMT (99)** | ✅ Allow | ✅ Allow | ✅ Allow | ✅ Allow | — | ✅ Allow |

### Specific ACL rules for SERVER ↔ IOT-AUTO

**IOT-AUTO (31) → SERVER (10):**
- PERMIT TCP to 192.168.10.17 port 1883 (MQTT plaintext) — ESP32 publishes door state, subscribes for commands
- PERMIT TCP to 192.168.10.17 port 8883 (MQTT/TLS) — if TLS is configured on Mosquitto
- DENY all other traffic to SERVER subnet

**SERVER (10) → IOT-AUTO (31):**
- PERMIT TCP port 554 (RTSP) — future camera stream pull by Frigate
- PERMIT TCP port 80/443 (HTTP/HTTPS) — admin access to devices if needed
- PERMIT ICMP — monitoring/ping
- DENY all other traffic

**IOT (30) → INTERNET:**
- PERMIT — general internet access (cloud-dependent devices need it)
- DNS queries go to Pi-hole (192.168.10.17) via DHCP option

**IOT-AUTO (31) → INTERNET:**
- DENY by default — ESP32 firmware is flashed locally, no cloud dependency
- If a device temporarily needs internet (OTA firmware update), manually permit and then re-deny

---

## DNS Strategy

All VLANs receive **Pi-hole (192.168.10.17)** as their primary DNS server via DHCP, with **1.1.1.1 (Cloudflare)** as fallback.

This means:
- All DNS queries from every VLAN flow through Pi-hole for filtering and logging
- Pi-hole sees which devices are making which queries (useful for identifying rogue IoT traffic)
- If Pi-hole is down, clients fall back to Cloudflare directly (no outage, just no filtering)

> **Note:** IOT-AUTO VLAN needs a cross-VLAN ACL to reach Pi-hole on the SERVER VLAN. This is intentional and covered by the "PERMIT TCP to 192.168.10.17 port 53 (DNS)" rule that should be added to the IOT-AUTO → SERVER ACL.

---

## Trunk Port Configuration

### Cisco C1111-4PWB ↔ GS308EP

| Setting | Value |
|---|---|
| Cisco port | GE0/1/1 (or whichever LAN port is used for the uplink) |
| GS308EP port | Port 8 (or designated uplink port) |
| Trunk type | 802.1Q tagged |
| Allowed VLANs | 10, 20, 30, 31, 99 |
| Native VLAN | 99 (management) |

### Cisco C1111-4PWB ↔ GS316EP (after household migration)

| Setting | Value |
|---|---|
| Cisco port | GE0/1/2 |
| GS316EP port | Port 16 (or designated uplink port) |
| Trunk type | 802.1Q tagged |
| Allowed VLANs | 10, 20, 30, 31, 99 |
| Native VLAN | 99 (management) |

### GS308EP → UniFi APs

| Setting | Value |
|---|---|
| GS308EP ports | Ports 4, 5 (currently used by APs) |
| Trunk type | 802.1Q tagged |
| Allowed VLANs | 20, 30, 31 (the SSIDs they broadcast) |
| Native VLAN | 99 (AP management traffic) |

---

## DHCP Pools (Cisco)

One pool per VLAN, configured on the Cisco as the L3 gateway.

| Pool Name | Network | Gateway | DNS | Lease |
|---|---|---|---|---|
| SERVER | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.17, 1.1.1.1 | 7 days |
| TRUSTED | 192.168.20.0/24 | 192.168.20.1 | 192.168.10.17, 1.1.1.1 | 7 days |
| IOT | 192.168.30.0/24 | 192.168.30.1 | 192.168.10.17, 1.1.1.1 | 1 day |
| IOT-AUTO | 192.168.31.0/24 | 192.168.31.1 | 192.168.10.17, 1.1.1.1 | 1 day |
| MGMT | 192.168.99.0/24 | 192.168.99.1 | 192.168.10.17, 1.1.1.1 | 7 days |

Shorter lease on IOT and IOT-AUTO because devices come and go. SERVER and TRUSTED get longer leases for stability.

Static reservations will be configured for:
- Acer server (SERVER VLAN)
- Pi 4B (SERVER VLAN)
- Both switches (MGMT VLAN)
- Both APs (MGMT VLAN)

---

## PoE Power Budget

### GS308EP (62W total)

| Device | Port | Est. Power | VLAN |
|---|---|---|---|
| UniFi U6+ AP #1 | 4 | ~12W | Trunk (20, 30, 31 + native 99) |
| UniFi U6+ AP #2 | 5 | ~12W | Trunk (20, 30, 31 + native 99) |
| Raspberry Pi 4B | 3 (or similar) | ~5W | 10 (SERVER) |
| **Total used** | | **~29W** | |
| **Headroom** | | **~33W** | |

Headroom is sufficient for 1-2 more PoE devices (future cameras, additional Pi, etc.)

### GS316EP (180W total, after migration to Cisco)

Future allocation — will be planned during household migration phase.

---

## Implementation Order

When ready to implement, execute in this order to minimize disruption:

1. **Create VLANs on Cisco** (SVIs with IP addresses, no shutdown)
2. **Create per-VLAN DHCP pools on Cisco** (excluded addresses, DNS, lease)
3. **Configure trunk port on Cisco side** (GE0/1/1 → GS308EP)
4. **Configure matching VLANs on GS308EP** (via switch web UI)
5. **Configure trunk port on GS308EP side** (port 8 → Cisco)
6. **Configure AP ports as trunks** on GS308EP (ports 4, 5)
7. **Configure access ports** on GS308EP for Pi (SERVER) and Acer (SERVER)
8. **Create additional SSIDs in UniFi Controller** (`Gorgeous-IoT`, `Gorgeous-Auto`) with VLAN tags
9. **Rename `Gorgeous1` to `Gorgeous`** and tag it VLAN 20
10. **Write ACLs on Cisco** (extended ACLs applied to SVIs)
11. **Test each VLAN**: client gets correct IP, can reach internet, cross-VLAN rules enforced
12. **Migrate household devices** — connect GS316EP to Cisco, move XB8 to bridge mode

> Steps 1–10 can be done without disrupting any currently-working device. Step 12 is the "big bang" migration that takes the household off the XB8 and onto the Cisco.

---

## Future Expansion

| Addition | VLAN | Notes |
|---|---|---|
| Guest WiFi (`Gorgeous-Guest`) | 40 (192.168.40.0/24) | Internet-only, client isolation enabled, bandwidth-limited |
| NAS (Synology/TrueNAS) | 10 (SERVER) | Backup target for Acer, media storage |
| Pi 5 + AI HAT+ | 10 (SERVER) | Frigate NVR if camera-based detection is added |
| Additional security cameras | 31 (IOT-AUTO) | RTSP to Frigate, no cloud |
| Dedicated NVR | 10 (SERVER) | If camera count exceeds Pi 5 capacity |

---

*Design finalized: April 15, 2026*
*Implementation: pending dedicated session (est. 2-3 hours)*
