# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform — and expand into a multi-service enterprise-grade home lab.

---

## Phase 1: Documentation & Baseline ✅ COMPLETE

- [x] Hardware inventory, architecture diagrams, repo structure

---

## Phase 2: Network Hardening ✅ COMPLETE

**Delivered:** Enterprise-grade VLAN-segmented network with Cisco edge routing, managed switching, VLAN-tagged WiFi, DNS filtering, and inter-VLAN firewalling.

### Step 0: Edge Router Deployment ✅

- [x] Cisco C1111-4PWB acquired and configured from serial console
- [x] WAN: DHCP client to Xfinity XB8 (bridge mode)
- [x] LAN: VLAN SVIs, DHCP pools, NAT overload (PAT)
- [x] Security baseline: hostname, enable secret, console password, exec-timeout, SSHv2
- [x] Config backup to sanitized text file
- [x] Cisco Smart Licensing registered — EngageMea.com Smart Account (May 16, 2026)
  - Status: REGISTERED, OUT OF COMPLIANCE (Cisco backend entitlement pending)
  - Export-Controlled Functionality: ALLOWED
  - No enforcement until Aug 14, 2026 — auto-resolves on daily check-in
- [x] Catalyst 3560CX-8PC-S acquired (from LoneStar Networks / Whaley Communications)
- [x] 3560CX baseline hardened from console (hostname JLM-LAB-SW1, SSHv2, Type 9 creds, VTP transparent, RTU perpetual licensing)
- [x] 3560CX staged offline — awaiting Phase B cutover

### Step 1: Physical Infrastructure ✅

- [x] CyberPower CP1500PFCLCD UPS installed, all critical infra on battery-backed outlets
- [x] GS308EP connected to Cisco as lab switch
- [x] GS316EP trunked to Cisco GE0/1/2 for household wired devices

### Step 2: Raspberry Pi Setup ✅

- [x] Pi 4B flashed headless (Pi Imager, SSH pre-enabled)
- [x] Pi-hole installed — 87K+ domain blocklist, serving DNS for all VLANs
- [x] UniFi Network Application v10.1.89 installed

### Step 3: WiFi Deployment ✅

- [x] 2× UniFi U6+ APs adopted by controller
- [x] 5 VLAN-tagged SSIDs configured and verified:
  - Gorgeous → VLAN 20 (TRUSTED)
  - Gorgeous-IoT → VLAN 30 (IOT)
  - Gorgeous-Auto → VLAN 31 (IOT-AUTO)
  - Gorgeous-Home → VLAN 40 (HOUSEHOLD)
  - JM&G-GUEST → VLAN 50 (JM&G-GUEST)
- [x] WiFi validated on phone and MacBook
- [ ] Ceiling-mount APs (pending, physical task)

### Step 4: VLAN Implementation ✅

- [x] 7 VLANs implemented and verified (1, 10, 20, 30, 31, 40, 50, 99)
- [x] Cisco SVIs with per-VLAN DHCP pools and NAT
- [x] GS308EP configured in Advanced 802.1Q mode
- [x] VLAN 99 as native/management VLAN on all trunks (192.168.99.0/24)
- [x] 802.1Q trunks: Cisco GE0/1/1 → GS308EP, Cisco GE0/1/2 → GS316EP
- [x] 4 extended ACLs written and applied:
  - IOT-ACL: internet only + DNS to Pi-hole
  - IOT-AUTO-ACL: MQTT + DNS to Pi only
  - HOUSEHOLD-ACL: internet only + DNS to Pi-hole
  - GUEST-ACL: internet only + DNS to Pi-hole, client isolation
- [x] ACLs verified: IOT/HOUSEHOLD/GUEST cannot reach SERVER or internal VLANs
- [x] UniFi networks created with VLAN IDs, all SSIDs broadcasting

### Remaining cleanup tasks

- [ ] Migrate Kasa EP10 plugs to VLAN 30 (blocked by app issue)
- [ ] Ceiling-mount APs (physical task)
- [ ] IOS rollback on C1111 to pre-16.10.1 (C1111-specific image required — not the 3560CX image)

### Phase 2 — Open Decisions (blocking Phase B cutover)

- [ ] Keep or remove `cisco_support` user on C1111
- [ ] Confirm VLAN 1 (192.168.100.0/24) retirement at cutover
- [ ] Confirm disabling HTTP/HTTPS on C1111 at cutover

---

## Phase 3: Server Hardening ✅ MOSTLY COMPLETE

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
- [ ] Authelia for service authentication (deferred to Phase 7)

---

## Phase 4: Monitoring & Observability 🔄 PARTIALLY COMPLETE

**Already in production:** The [closet-monitor](https://github.com/design1-software/closet-monitor) project is a production IoT monitoring pipeline — ESP32 + BME280 → MQTT → Pi → SQLite → Streamlit dashboard.

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
- [ ] Alert routing via ntfy (self-hosted)
- [ ] 30-day uptime tracking

---

## Phase 5: 3560CX Cutover & New Server Deployment ❌ NOT STARTED

**Goal:** Promote 3560CX to L3 core, retire C1111 as edge-only, bring up custom Proxmox server on VLAN 70.

### Phase A — Pre-stage 3560CX offline (zero production impact)
- [ ] Build VLAN database on 3560CX (VLANs 1,10,20,30,31,40,50,60,70,99,199)
- [ ] Configure SVIs with IP addresses for all VLANs
- [ ] Configure DHCP pools for all VLANs
- [ ] Write and apply inter-VLAN ACLs (mirror C1111 ACLs + new VLANs 60/70)
- [ ] Configure trunk ports (uplink to GS308EP, GS316EP, C1111 TRANSIT)
- [ ] Save and verify config offline

### Phase B — Light cutover (~5 min WiFi outage, schedule off-peak)
- [ ] Cable 3560CX into production
- [ ] Configure TRANSIT VLAN 199 (192.168.199.0/30) between C1111 and 3560CX
- [ ] Move default route — C1111 points to 3560CX, 3560CX points to C1111 for WAN
- [ ] Verify all VLANs routing through 3560CX
- [ ] Verify internet access on all VLANs
- [ ] Roll back plan documented and saved before cutover begins

### Phase C — Proxmox server bring-up
- [ ] Assemble custom ATX server (Ryzen 9 7900X, B650, PA120 SE, SAMA V40, SL-650G)
- [ ] Set PPT power cap to 88W in BIOS for server efficiency
- [ ] Install Proxmox VE bare metal
- [ ] Assign static IP on VLAN 70 (SERVER, 192.168.70.0/24)
- [ ] Trunk both NICs to GS308EP — management on VLAN 70, VM traffic on VLANs 60/70
- [ ] Add as 7th Tailscale node
- [ ] Enable Tailscale subnet routing for VLAN 60 (LAB) → Ohio schoolmate access
- [ ] Deploy Wazuh SIEM as LXC container on Proxmox
- [ ] Install Wazuh agents on Acer, Pi 4B, and Proxmox host
- [ ] Deploy Netdata, NetAlertX, ntfy (completing Phase 4)

### Phase D — VLAN 60 schoolmate lab
- [ ] Build VLAN 60 (LAB, 192.168.60.0/24) on 3560CX
- [ ] Deploy Active Directory VM on Proxmox (VLAN 60)
- [ ] Deploy osTicket help desk VM on Proxmox (VLAN 60)
- [ ] Deploy M365 admin sandbox (VLAN 60)
- [ ] Configure Tailscale subnet routing for Ohio schoolmate access
- [ ] Define AD forest name (jlm.lab vs corp.builtwithpurpose.dev — TBD)

---

## Phase 6: Security Audit & SIEM ❌ NOT STARTED

- [ ] Wazuh log sources: Cisco syslog, Pi-hole query log, Mosquitto, Docker, CUPS
- [ ] File integrity monitoring on critical configs
- [ ] Vulnerability detection + CIS benchmark compliance
- [ ] Custom dashboards for lab-specific events
- [ ] VLAN isolation verification (cross-VLAN reachability matrix)
- [ ] API key rotation
- [ ] Security findings report
- [ ] Authelia for service authentication
- [ ] Vaultwarden for secrets management

---

## Phase 7: Infrastructure as Code ❌ NOT STARTED

- [ ] Ansible playbook for base server setup
- [ ] Ansible roles: MCP server, Ngrok, Pi deployment, CUPS config, Wazuh agent, Netdata agent
- [ ] Cisco config templating via Netmiko/Ansible
- [ ] One-command bare metal rebuild
- [ ] Optional: GitHub Actions CI/CD

---

## Phase 8: Portfolio & Documentation ❌ NOT STARTED

- [ ] Structured build labs on builtwithpurpose.dev
  - [ ] VLAN segmentation walkthrough
  - [ ] ACL troubleshooting (DHCP fix — IOT-AUTO-ACL lesson learned)
  - [ ] Bridge mode cutover + MSS clamping
  - [ ] Tailscale + Pi-hole coexistence
  - [ ] CUPS print server deployment (USB + WiFi dual-path architecture)
  - [ ] 3560CX L3 cutover walkthrough
  - [ ] Proxmox server build and deployment
- [ ] closet-monitor data engineering case study
- [ ] Printer VLAN segmentation case study
- [ ] Cisco licensing writeup (Smart Licensing vs RTU, EVAL vs OUT OF COMPLIANCE)
- [ ] Custom server build writeup (Ryzen 9 7900X, Proxmox, VLAN 70 integration)

---

## Ongoing / Blocked

- [ ] IOS rollback on C1111 to pre-16.10.1 (C1111-specific image required)
- [ ] Kasa EP10 smart plugs → VLAN 30 (app issue blocking migration)
- [ ] Ceiling-mount UniFi U6+ APs (physical task)
- [ ] Garage automation: ESP32 + reed switch + relay + Wyze Cam v3 + Frigate NVR
- [ ] HP ENVY 5640 — bring online via CUPS or remove from Instant Ink subscription
- [ ] Algo VPN — planned, not started
- [ ] Add phone and Android 7.0 tablet to Tailscale tailnet
- [ ] RAM + NVMe pricing — watching for DDR5 price drop before purchasing

---

## Hardware Status

| Device | Status | Notes |
|---|---|---|
| Cisco C1111-4PWB (JLM-LAB-R1) | ✅ Production | Smart Licensing REGISTERED, OUT OF COMPLIANCE (no enforcement until Aug 2026) |
| Catalyst 3560CX-8PC-S (JLM-LAB-SW1) | 🔄 Staged | Baselined, awaiting Phase B cutover |
| NETGEAR GS308EP | ✅ Production | L2 lab switch, VLAN 99 management |
| NETGEAR GS316EP | ✅ Production | L2 household switch |
| UniFi U6+ APs (×2) | ✅ Production | 5 SSIDs, desk-mounted pending ceiling mount |
| Raspberry Pi 4B | ✅ Production | Pi-hole, UniFi Controller, Mosquitto, CUPS |
| Acer Server | ✅ Production | Docker: social-media-mcp + Ngrok, Streamlit |
| Custom ATX Server (Proxmox) | 🔄 In build | Ryzen 9 7900X, B650, PA120 SE, SAMA V40, SL-650G — RAM + NVMe pending |

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly |
| Phase 2 | Design and implement enterprise network segmentation: Cisco IOS XE routing, 802.1Q trunking, VLANs, ACLs, DHCP, NAT, UniFi WiFi, DNS filtering |
| Phase 3 | Containerize production services, deploy print infrastructure, harden service access, write operational runbooks |
| Phase 4 | Build end-to-end IoT monitoring pipelines and production observability |
| Phase 5 | Execute a zero-downtime L3 network cutover and deploy a hypervisor platform |
| Phase 6 | Deploy and operate a SIEM for continuous security monitoring |
| Phase 7 | Implement Infrastructure as Code for repeatable deployments |
| Phase 8 | Communicate technical work through structured labs and case studies |
| **All** | Operate a real production system — not just build one |

---

*Last updated: May 19, 2026*