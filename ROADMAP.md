# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform.

---

## Phase 1: Documentation & Baseline ✅ COMPLETE

- [x] Hardware inventory, architecture diagrams, repo structure

---

## Phase 2: Network Hardening ✅ COMPLETE

**Delivered:** Enterprise-grade VLAN-segmented network with Cisco edge routing, managed switching, VLAN-tagged WiFi, DNS filtering, and inter-VLAN firewalling.

### Step 0: Edge Router Deployment ✅

- [x] Cisco branch router acquired and configured from serial console
- [x] WAN: DHCP client to ISP gateway
- [x] LAN: Vlan1 SVI, DHCP pool, NAT overload (PAT)
- [x] Security baseline: hostname, enable secret, console password, exec-timeout, SSHv2
- [x] Config backup to sanitized text file

### Step 1: Physical Infrastructure ✅

- [x] UPS installed, all critical infra on battery-backed outlets
- [x] Lab Switch connected to Cisco

### Step 2: Raspberry Pi Setup ✅

- [x] Pi flashed headless (Pi Imager, SSH pre-enabled)
- [x] Pi-hole installed — 87K+ domain blocklist, serving DNS for all VLANs
- [x] UniFi Network Application installed

### Step 3: WiFi Deployment ✅

- [x] 2× UniFi U6+ APs adopted by controller
- [x] 5 VLAN-tagged SSIDs configured and verified:
  - Personal → TRUSTED VLAN
  - Smart-Home → IOT VLAN
  - Automation → IOT-AUTO VLAN
  - Family → HOUSEHOLD VLAN
  - Guest → GUEST VLAN (client isolation)
- [x] WiFi validated across all VLANs
- [ ] Ceiling-mount APs (pending, physical task)

### Step 4: VLAN Implementation ✅

- [x] 7 VLANs designed, implemented, and verified (SERVER, TRUSTED, IOT, IOT-AUTO, HOUSEHOLD, GUEST, MGMT)
- [x] Cisco SVIs with per-VLAN DHCP pools and NAT
- [x] Lab Switch configured in Advanced 802.1Q mode (T/U/E per port, PVIDs set)
- [x] 802.1Q trunk between Cisco and Lab Switch (native VLAN MGMT, VLAN 1 tagged)
- [x] 4 extended ACLs written and applied:
  - IOT-ACL: internet only + DNS to Pi-hole
  - IOT-AUTO-ACL: MQTT + DNS to Pi only
  - HOUSEHOLD-ACL: internet only + DNS to Pi-hole
  - GUEST-ACL: internet only + client isolation
- [x] ACLs verified: IOT devices cannot reach SERVER VLAN
- [x] UniFi networks created with VLAN IDs (TRUSTED, IOT, IOT-AUTO, HOUSEHOLD, GUEST)

### Remaining cleanup tasks

- [x] Migrate IoT devices to IOT VLAN (cameras, voice, thermostat, blinds, smart TV)
- [x] Move Pi from Cisco access port to Lab Switch PoE port
- [x] Reinstall PoE HAT on Pi (GPIO fan configured)
- [x] Apple TVs on DHCP (static IPs caused app failures; AirPlay works same-VLAN without ACL rules)
- [x] Migrate household to Cisco — Household Switch trunked, ISP gateway in bridge mode, Cisco as sole router
- [x] UPS auto-shutdown via PowerPanel Personal
- [x] Console cable removed — SSH is primary management method
- [x] HOUSEHOLD-ACL simplified to internet-only (AirPlay works same-VLAN, no cross-VLAN ACL needed)
- [x] GUEST VLAN created with client isolation
- [x] TCP MSS clamping on WAN for bridge-mode compatibility
- [x] Apple domains whitelisted in Pi-hole
- [x] Tailscale installed for remote management
- [x] Troubleshooting lab completed — Apple TV connectivity, 11 CCNA topics across 4 OSI layers
- [ ] Ceiling-mount APs

### Key lessons learned

1. Netgear Basic 802.1Q "Trunk" ≠ Cisco trunk — must use Advanced 802.1Q
2. VLAN 1 must be Tagged on the switch trunk port per official documentation
3. Cisco trunk must include VLAN 1 in allowed list to match switch config
4. ACLs ending in `deny ip any any` block DHCP — permit UDP 67/68 before the deny
5. Pi-hole sets a static IP during install — don't override from the network side
6. Apple TVs need DHCP, not static IPs, to reach streaming services
7. TCP MSS clamping is required after bridge-mode cutover
8. Tailscale MagicDNS hijacks local DNS — always disable it for lab use
9. Always verify cables before assuming switch/VLAN issues
10. Always follow official vendor documentation

---

## Phase 3: Server Hardening 🔄 NEXT

**Goal:** Containerize production services, implement proper process management, and create recovery procedures.

- [ ] Docker & Docker Compose on home server
- [ ] Containerize social-media-mcp + Ngrok agent
- [ ] `docker-compose.yml` with health checks
- [ ] Auto-restart on boot (systemd + Docker restart policy)
- [ ] Log rotation
- [ ] Runbooks: server restart, tunnel recovery, disaster recovery
- [ ] Authelia for service authentication (after services are containerized)
- [x] CUPS print server deployed on Pi (USB-attached HP All-in-One, IPP Everywhere, driverless)
- [x] CUPS access hardened (print submission: SERVER/TRUSTED/HOUSEHOLD; admin: TRUSTED only)
- [x] Printer segmented — vendor cloud services on IOT VLAN, print path on SERVER VLAN

---

## Phase 4: Monitoring & Observability

**Already underway:** The [closet-monitor](https://github.com/design1-software/closet-monitor) project is a production IoT monitoring pipeline — ESP32 + BME280 → MQTT → Pi → SQLite → Streamlit dashboard. Validates the IOT-AUTO VLAN design and the MQTT cross-VLAN ACL path.

- [x] ESP32 closet sensor deployed and publishing MQTT
- [x] Mosquitto broker running on Pi
- [x] SQLite persistence + Streamlit dashboard operational
- [x] Anomaly detection via rolling z-scores
- [x] Pi migrated to Lab Switch PoE port
- [x] PoE HAT reinstalled, GPIO fan configured
- [x] IoT devices migrated to IOT VLAN
- [ ] Netdata on Pi — system + container metrics
- [ ] NetAlertX on Pi — network device presence, new-device alerts
- [ ] Alert routing (ntfy or similar)

---

## Phase 5: Security Audit & SIEM

- [ ] Nmap scan of lab network + cross-VLAN reachability matrix
- [ ] Tunnel security audit
- [ ] Cisco IOS XE upgrade (modern SSH crypto — blocked on SmartNet)
- [ ] Wazuh manager on home server
- [ ] Wazuh agents on Pi, home server, laptop
- [ ] Log sources: Cisco syslog, Pi-hole, Mosquitto, Docker, CUPS
- [ ] File integrity monitoring on critical configs
- [ ] Vulnerability detection + CIS benchmark compliance
- [ ] API key rotation
- [ ] Security findings report

---

## Phase 6: Infrastructure as Code

- [ ] Ansible playbook for base server setup
- [ ] Ansible roles: MCP server, Ngrok, Pi deployment, CUPS config, Wazuh agent, Netdata agent
- [ ] Cisco config templating via Netmiko/Ansible
- [ ] One-command bare-metal rebuild
- [ ] Optional: GitHub Actions CI/CD

---

## Phase 7: Portfolio & Documentation

- [ ] Structured build labs on builtwithpurpose.dev
  - [ ] VLAN segmentation walkthrough
  - [ ] ACL troubleshooting (DHCP fix)
  - [ ] Bridge-mode cutover + MSS clamping
  - [ ] Tailscale + Pi-hole coexistence
  - [ ] CUPS print server deployment (USB + WiFi dual-path)
- [ ] closet-monitor data-engineering case study
- [ ] Cisco config hardening write-up
- [ ] Print-server VLAN-segmentation case study — enterprise pattern at home-lab scale

---

## Ongoing / Blocked

- [ ] Cisco Smart Account registration (waiting on seller info; eval mode counting down)
- [ ] IOS XE upgrade (blocked without SmartNet contract)
- [ ] A couple of smart plugs still on the default SSID (app issue)
- [ ] Ceiling-mount APs (physical task)
- [ ] Garage automation (ESP32 + reed switch + relay + cam)
- [ ] CCNA study labs: OSPF, IPv6, NTP, syslog, SNMP, STP, port security
- [ ] Second HP printer — either bring online via CUPS or remove from cloud subscription

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly |
| Phase 2 | Design and implement enterprise network segmentation: Cisco IOS XE routing, 802.1Q trunking, VLANs, ACLs, DHCP, NAT, UniFi WiFi, DNS filtering |
| Phase 3 | Containerize production services, deploy auth, operate a CUPS print server, write operational runbooks |
| Phase 4 | Build monitoring and alerting for production infrastructure |
| Phase 5 | Deploy a real SIEM and conduct a professional security audit |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| Phase 7 | Turn lived operational experience into written engineering artifacts |
| **All** | Operate a real production system — not just build one |

---

*Last updated: April 24, 2026*
