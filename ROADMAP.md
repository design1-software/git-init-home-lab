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
- [x] Reinstall PoE HAT on Pi (GPIO fan at 55°C, pins 4/6 reserved for PoE HAT)
- [x] Apple TVs on DHCP (static IPs caused app failures; AirPlay works same-VLAN without ACL rules)
- [x] Migrate household to Cisco — GS316EP trunked to GE0/1/2, XB8 bridge mode, Cisco sole router
- [x] UPS auto-shutdown via PowerPanel Personal (USB-B to Acer, shutdown at 20%)
- [x] Console cable removed — SSH is primary management method
- [x] HOUSEHOLD-ACL simplified to internet-only (AirPlay works same-VLAN, no cross-VLAN ACL needed)
- [x] VLAN 50 (GUEST) created — JM&G-GUEST SSID with client isolation, GUEST-ACL internet-only
- [x] TCP MSS clamping on WAN (`ip tcp adjust-mss 1452`) for bridge mode
- [x] Apple domains whitelisted in Pi-hole (gsa.apple.com, configuration.apple.com, etc.)
- [x] Tailscale installed on MacBook Pro and Acer for remote management
- [x] Troubleshooting lab completed — Apple TV connectivity, 11 CCNA topics across 4 OSI layers
- [ ] Ceiling-mount APs

### Key lessons learned

1. Netgear Basic 802.1Q "Trunk" ≠ Cisco trunk — must use Advanced 802.1Q
2. VLAN 1 must be Tagged (T) on the Netgear trunk port per official documentation
3. Cisco trunk must include VLAN 1 in allowed list to match Netgear config
4. Pi-hole sets a static IP during install — don't override from the network side
5. Always verify cables before assuming switch/VLAN issues
6. Always follow official vendor documentation

---

## Phase 3: Server Hardening ✅ MOSTLY COMPLETE

**Goal:** Containerize production services, implement proper process management, create recovery procedures.

**Delivered:** Docker Compose stack with multi-stage build, Ngrok sidecar, health checks, auto-restart, and log rotation. CUPS print server deployed on Pi with enterprise-grade access controls.

- [x] Docker & Docker Compose on Acer (Docker Desktop v29.1.3, Compose v2.40.3)
- [x] Containerize social-media-mcp (multi-stage Dockerfile: Node 20, ffmpeg, Chromium, Remotion)
- [x] Containerize Ngrok agent as sidecar (official `ngrok/ngrok` image, fixed domain `mea.ngrok.app`)
- [x] docker-compose.yml with health checks (`/health` endpoint, 30s interval)
- [x] Auto-restart on boot (Docker Desktop auto-start + `restart: always`)
- [x] Log rotation (json-file driver, 10MB × 3 files)
- [x] CUPS print server deployed on Pi (USB-attached HP ENVY Inspire 7200e, IPP Everywhere)
- [x] CUPS access hardened (print: VLAN 10/20/40; admin: VLAN 20 only)
- [x] Printer segmented — HP cloud services on VLAN 30, print path via VLAN 10
- [x] Printer hardening — Wi-Fi Direct disabled, HP marketing data disabled
- [ ] Runbooks: update for Docker (server restart, tunnel recovery)
- [ ] Runbook: disaster recovery (bare metal → production)
- [ ] Authelia for service authentication (after remaining Phase 3 items)

---

## Phase 4: Monitoring & Observability 🔄 PARTIALLY COMPLETE

**Already in production:** The [closet-monitor](https://github.com/design1-software/closet-monitor) project is a production IoT monitoring pipeline — ESP32 + BME280 → MQTT → Pi → SQLite → Streamlit dashboard, with anomaly detection via rolling z-scores. This validates the IOT-AUTO VLAN design and the MQTT cross-VLAN ACL path.

- [x] ESP32 closet sensor deployed on Gorgeous-Auto (VLAN 31), publishing MQTT
- [x] Mosquitto broker migrated to Pi (192.168.10.16)
- [x] SQLite persistence + Streamlit dashboard operational on Acer (:8501)
- [x] Anomaly detection with rolling z-scores
- [x] Pi migrated to GS308EP port 3 (PoE powered, trunk verified)
- [x] PoE HAT reinstalled, GPIO fan configured (55°C threshold)
- [x] IoT devices migrated to Gorgeous-IoT (Ring, Alexa, Ecobee, Somfy, Samsung TV)
- [x] Health check scripts (PowerShell) written
- [ ] Netdata on Pi — system + container metrics, per-host dashboards
- [ ] NetAlertX on Pi — network device presence, new-device alerts
- [ ] Alert routing via ntfy
- [ ] 30-day uptime tracking

---

## Phase 5: Security Audit & SIEM

**Approach updated:** Replaced one-time Nmap scan with continuous SIEM deployment per cybersecurity specialist review.

- [ ] Wazuh manager on Acer (Docker)
- [ ] Wazuh agents on Pi, Acer, MacBook
- [ ] Log sources: Cisco syslog, Pi-hole query log, Mosquitto, Docker, CUPS
- [ ] File integrity monitoring on critical configs
- [ ] Vulnerability detection + CIS benchmark compliance
- [ ] Custom dashboards for lab-specific events
- [ ] VLAN isolation verification (cross-VLAN reachability matrix)
- [ ] API key rotation
- [ ] Security findings report

---

## Phase 6: Infrastructure as Code

- [ ] Ansible playbook for base server setup
- [ ] Ansible roles: MCP server, Ngrok, Pi deployment, CUPS config, Wazuh agent, Netdata agent
- [ ] Cisco config templating via Netmiko/Ansible
- [ ] One-command bare metal rebuild
- [ ] Optional: GitHub Actions CI/CD

---

## Phase 7: Portfolio & Documentation

- [ ] Structured build labs on builtwithpurpose.dev
  - [ ] VLAN segmentation walkthrough
  - [ ] ACL troubleshooting (DHCP fix)
  - [ ] Bridge mode cutover + MSS clamping
  - [ ] Tailscale + Pi-hole coexistence
  - [ ] CUPS print server deployment (USB + WiFi dual-path architecture)
- [ ] closet-monitor data engineering case study
- [ ] Printer VLAN segmentation case study
- [ ] Cisco config hardening writeup

---

## Ongoing / Blocked

- [ ] Cisco Smart Account registration (waiting on seller info, eval period active)
- [ ] IOS XE upgrade (blocked without SmartNet contract)
- [ ] Kasa smart plugs → Gorgeous-IoT (app issue)
- [ ] Ceiling-mount APs (physical task)
- [ ] Garage automation (ESP32 + reed switch + relay + Wyze Cam v3)
- [ ] CCNA study labs: OSPF, IPv6, NTP, syslog, SNMP, STP, port security
- [ ] HP ENVY 5640 — bring online via CUPS or remove from Instant Ink subscription

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly |
| Phase 2 | Design and implement enterprise network segmentation: Cisco IOS XE routing, 802.1Q trunking, VLANs, ACLs, DHCP, NAT, UniFi WiFi, DNS filtering |
| Phase 3 | Containerize production services, deploy print infrastructure, harden service access, and write operational runbooks |
| Phase 4 | Build end-to-end IoT monitoring pipelines and production observability |
| Phase 5 | Deploy and operate a SIEM for continuous security monitoring |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| Phase 7 | Communicate technical work through structured labs and case studies |
| **All** | Operate a real production system — not just build one |

---

*Last updated: April 24, 2026*
