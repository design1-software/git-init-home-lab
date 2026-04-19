# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform.

---

## Phase 1: Documentation & Baseline ✅ COMPLETE

- [x] Hardware inventory, architecture diagrams, repo structure

---

## Phase 2: Network Hardening ✅ COMPLETE

**Delivered:** Enterprise-grade VLAN-segmented network with Cisco edge routing, managed switching, VLAN-tagged WiFi, DNS filtering, and inter-VLAN firewalling.

### Step 0: Edge Router Deployment ✅

- [x] Cisco C1111-4PWB acquired and configured from serial console
- [x] WAN: DHCP client to Xfinity XB8
- [x] LAN: Vlan1 SVI, DHCP pool, NAT overload (PAT)
- [x] Security baseline: hostname, enable secret, console password, exec-timeout, SSHv2
- [x] Config backup to sanitized text file

### Step 1: Physical Infrastructure ✅

- [x] CyberPower CP1500PFCLCD UPS installed, all critical infra on battery-backed outlets
- [x] GS308EP connected to Cisco as lab switch

### Step 2: Raspberry Pi Setup ✅

- [x] Pi 4B flashed headless (Pi Imager, SSH pre-enabled)
- [x] Pi-hole installed — 87K+ domain blocklist, serving DNS for all VLANs
- [x] UniFi Network Application v10.1.89 installed

### Step 3: WiFi Deployment ✅

- [x] 2× UniFi U6+ APs adopted by controller
- [x] 4 VLAN-tagged SSIDs configured and verified:
  - Gorgeous → VLAN 20 (TRUSTED)
  - Gorgeous-IoT → VLAN 30 (IOT)
  - Gorgeous-Auto → VLAN 31 (IOT-AUTO)
  - Gorgeous-Home → VLAN 40 (HOUSEHOLD)
- [x] WiFi validated on phone and MacBook
- [ ] Ceiling-mount APs (pending, physical task)

### Step 4: VLAN Implementation ✅

- [x] 6 VLANs designed, implemented, and verified (10, 20, 30, 31, 40, 99)
- [x] Cisco SVIs with per-VLAN DHCP pools and NAT
- [x] GS308EP configured in Advanced 802.1Q mode (T/U/E per port, PVIDs set)
- [x] 802.1Q trunk between Cisco and GS308EP (native VLAN 99, VLAN 1 tagged)
- [x] 3 extended ACLs written and applied:
  - IOT-ACL: internet only + DNS to Pi-hole
  - IOT-AUTO-ACL: MQTT + DNS to Pi only
  - HOUSEHOLD-ACL: internet + AirPlay to Apple TV IPs
- [x] ACLs verified: IOT devices cannot reach SERVER VLAN
- [x] UniFi networks created with VLAN IDs (TRUSTED, IOT, IOT-AUTO, HOUSEHOLD)

### Remaining cleanup tasks

- [ ] Migrate IoT devices to correct SSIDs (Ring, Alexa, Ecobee → Gorgeous-IoT)
- [ ] Move Pi from Cisco GE0/1/2 to GS308EP port 3
- [ ] Reinstall PoE HAT on Pi
- [ ] Apple TV static IPs (.101, .102, .103) for AirPlay ACL
- [ ] Migrate household to Cisco (move GS316EP, flip XB8 to bridge mode)
- [ ] Ceiling-mount APs

### Key lessons learned

1. Netgear Basic 802.1Q "Trunk" ≠ Cisco trunk — must use Advanced 802.1Q
2. VLAN 1 must be Tagged (T) on the Netgear trunk port per official documentation
3. Cisco trunk must include VLAN 1 in allowed list to match Netgear config
4. Pi-hole sets a static IP during install — don't override from the network side
5. Always verify cables before assuming switch/VLAN issues
6. Always follow official vendor documentation

---

## Phase 3: Server Hardening 🔲 NEXT

**Goal:** Containerize production services, implement proper process management, create recovery procedures.

- [ ] Docker & Docker Compose on Acer
- [ ] Containerize social-media-mcp + Ngrok agent
- [ ] docker-compose.yml with health checks
- [ ] Auto-restart on boot (systemd + Docker restart policy)
- [ ] Log rotation
- [ ] Runbooks: server restart, tunnel recovery, disaster recovery

---

## Phase 4: Monitoring & Observability

Phase 4: Monitoring & Observability 🔄 IN PROGRESS
Already underway: The closet-monitor project is a production IoT monitoring pipeline running on the lab network — an ESP32 with a BME280 sensor publishing temperature, humidity, and pressure data via MQTT, with a Python subscriber persisting to SQLite, anomaly detection via rolling z-scores, and a Streamlit dashboard. This represents Phase 4 work already in production, validating the IOT-AUTO VLAN design and the MQTT cross-VLAN ACL path.

 ESP32 closet sensor deployed and publishing MQTT (currently on VLAN 20, pending move to VLAN 31)
 Mosquitto broker running (currently on MacBook Pro, pending migration to Pi)
 SQLite persistence + Streamlit dashboard operational
 Anomaly detection with rolling z-scores identifying real-world events
 5,600+ readings logged with zero packet loss
 Uptime Kuma on Pi
 Monitors: MCP server, Ngrok endpoint, Railway app, Cisco, Pi-hole, APs
 Health check scripts (PowerShell)
 Email/SMS alerts via ntfy
 30-day uptime tracking
 Migrate Mosquitto to Pi (192.168.10.16)
 Move ESP32 to Gorgeous-Auto (VLAN 31)

---

## Phase 5: Security Audit

- [ ] Nmap scan of both networks
- [ ] VLAN isolation verification (cross-VLAN reachability matrix)
- [ ] Tunnel security audit
- [ ] Cisco IOS XE upgrade (modern SSH crypto)
- [ ] API key rotation
- [ ] Security findings report

---

## Phase 6: Infrastructure as Code

- [ ] Ansible playbook for base server setup
- [ ] Ansible roles: MCP server, Ngrok, Pi deployment
- [ ] Cisco config templating via Netmiko/Ansible
- [ ] One-command bare metal rebuild
- [ ] Optional: GitHub Actions CI/CD

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly |
| Phase 2 | Design and implement enterprise network segmentation: Cisco IOS XE routing, 802.1Q trunking, VLANs, ACLs, DHCP, NAT, UniFi WiFi, DNS filtering |
| Phase 3 | Containerize production services and write operational runbooks |
| Phase 4 | Build monitoring and alerting for production infrastructure |
| Phase 5 | Conduct a professional security audit |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| **All** | Operate a real production system — not just build one |

---

*Last updated: April 19, 2026*
