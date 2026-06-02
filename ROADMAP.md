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
- [x] 3560CX Phase A pre-staging complete — VLANs, SVIs, DHCP pools, ACLs, trunk configs offline
- [x] HTTP/HTTPS management disabled on C1111 (hardening — May 19, 2026)
- [x] NTP hierarchy configured — C1111 stratum 2, Pi/Acer/3560CX stratum 3 (May 21, 2026)
- [x] OSPFv2 configured on C1111 — process 1, router-ID 10.0.0.1, all VLANs in area 0 (May 21, 2026)
- [x] IPv6 dual-stack on VLAN 10 and VLAN 20 (2001:db8:10::/64, 2001:db8:20::/64) (May 21, 2026)
- [x] RESTCONF enabled on C1111 — Python REST API queries verified (May 21, 2026)
- [x] AAA configured on C1111 — aaa new-model, local authentication, exec authorization (May 25, 2026)
- [x] OSPFv3 configured on C1111 — process 1, router-ID 10.0.0.1, Loopback0/Vlan10/Vlan20 (May 25, 2026)


### Step 1: Physical Infrastructure ✅

- [x] CyberPower CP1500PFCLCD UPS installed, all critical infra on battery-backed outlets
- [x] CyberPower SX950U (950VA/510W) — office UPS added; currently protecting office Tailscale nodes, not yet on network infra
- [x] GS308EP connected to Cisco as lab switch — VLAN 50 corrected on Port 4 (May 19, 2026)
- [x] GS316EP trunked to Cisco GE0/1/2 for household wired devices — VLAN 50 added (May 19, 2026)
- [x] GS308EP management IP locked to 192.168.100.95 via DHCP reservation (confirmed May 31, 2026)

### Step 2: Raspberry Pi Setup ✅

- [x] Pi 4B flashed headless (Pi Imager, SSH pre-enabled)
- [x] Pi-hole installed — 87K+ domain blocklist, serving DNS for all VLANs
- [x] UniFi Network Application v10.1.89 installed
- [x] NTP client configured — syncing from C1111 (192.168.10.1) (May 21, 2026)

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

- [x] 8 VLANs implemented and verified (1, 10, 20, 30, 31, 40, 50, 99)
- [x] Cisco SVIs with per-VLAN DHCP pools and NAT
- [x] GS308EP configured in Advanced 802.1Q mode — all 8 VLANs verified
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
- [ ] IOS rollback on C1111 to pre-16.10.1 (C1111-specific image required)

### Phase 2 — Open Decisions (resolved May 19, 2026)

- [x] Keep `cisco_support` user on C1111 — decision: keep
- [x] VLAN 1 retirement — decision: keep as legacy/switch management
- [x] HTTP/HTTPS on C1111 — decision: disabled (hardened), RESTCONF re-enables HTTPS only

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
- [x] Acer NTP client configured — syncing from C1111 (May 21, 2026)
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

## Phase 5: 3560CX Cutover & New Server Deployment 🔄 IN PROGRESS

**Goal:** Promote 3560CX to L3 core, retire C1111 as edge-only, bring up custom Proxmox server on VLAN 70.

> Proxmox server ✅ live (192.168.100.10, Tailscale pve 100.71.239.21) — Phase C base install complete. VLAN 70 cabling and VM workloads pending Phase B/C cutover.

### Phase A — Pre-stage 3560CX offline ✅ COMPLETE (May 19, 2026)
- [x] Build VLAN database on 3560CX (VLANs 1,10,20,30,31,40,50,60,70,99,199)
- [x] Configure SVIs with IP addresses for all VLANs
- [x] Configure DHCP pools for all VLANs + GS308EP reservation
- [x] Write and apply inter-VLAN ACLs (IOT, IOT-AUTO, HOUSEHOLD, GUEST, LAB)
- [x] Configure trunk ports (Gi0/2 → GS308EP, Gi0/3 → GS316EP, Gi0/4 → Proxmox)
- [x] Configure Gi0/1 as L3 TRANSIT port (192.168.199.2/30)
- [x] DHCP snooping on VLANs 30,31,40,50,60 (May 19, 2026)
- [x] DAI on VLANs 30,31,40,50,60 (May 19, 2026)
- [x] Rapid-PVST+ configured, STP documented (May 21, 2026)
- [x] NTP client configured — syncing from C1111 (May 21, 2026)
- [x] Config saved and committed to repo
- [x] IP Source Guard configured on Gi0/5-Gi0/8 — activates at Phase B (May 25, 2026)


### Phase B — Light cutover (~5 min WiFi outage, schedule off-peak) 🔄 In Progress
> **Current state (Jun 1, 2026):** Stable hybrid. C1111 still owns active production VLAN gateways and switch trunks. 3560CX has live routed TRANSIT adjacency via VLAN 199. OSPFv2 is FULL both ways. HSRP is staged on the 3560CX only for gateway IP preservation — it is not true gateway redundancy because the C1111 is not configured as an HSRP peer and will not remain Layer-2 adjacent to the production VLANs after the Phase B trunk move. Role split: C1111 = WAN edge / NAT / default route originator / OSPF neighbor; 3560CX = LAN L3 core / VLAN gateways / inter-VLAN ACLs / DHCP post-cutover; GS308EP + GS316EP = access-layer switches.
>
> ⚠️ **IP conflict risk:** C1111 currently owns `.1` as physical SVI addresses on all production VLANs. 3560CX has staged HSRP virtual `.1` addresses for those same VLANs. These must not be active on the same L2 segment simultaneously. The trunk migration must be **break-before-make**: disconnect C1111 trunks before connecting 3560CX trunks.
- [x] GS308EP Port 2: PVID→10, VLAN 10 member, Acer cabled in — verified 192.168.10.11 + IPv6 GUA on VLAN 10 (May 31, 2026)
- [x] GE0/1/0 confirmed down/notconnect — Acer fully off C1111, port free for TRANSIT repurpose (May 31, 2026) ← **Step 1.1 COMPLETE**
- [x] C1111 TRANSIT configured via SVI (NIM-ES2 ports are L2-only — no switchport unavailable): VLAN 199, GE0/1/0 access VLAN 199, Vlan199 SVI 192.168.199.1/30, ip nat inside — config saved to NVRAM (May 31, 2026) ← **Step 1.2 COMPLETE**
- [x] C1111 OSPFv2 extended (process 1 pre-existed from lab work): added Vlan199 to area 0, default-information originate, no passive-interface Vlan199 — config saved to NVRAM (May 31, 2026) ← **Step 1.3 COMPLETE** — see lab-010-ospfv2.md
- [x] NAT-INSIDE ACL updated: added `permit 192.168.199.0 0.0.0.3` so TRANSIT /30 is covered by PAT overload rule — config saved (May 31, 2026) ← **Step 1.4 COMPLETE**
- [x] Step 1.5 skipped — no static default route exists on C1111; WAN default is DHCP-learned from Comcast (AD 254, IOS displays as "static" — this is normal IOS behavior). default-information originate will propagate it to 3560CX via OSPF once adjacency forms. ← **Step 1.5 N/A**
- **Stage 1 COMPLETE — no outage. All changes additive. Production traffic unaffected.** ✅
- [x] Cable 1 (TRANSIT) plugged in — C1111 GE0/1/0 up/up, Vlan199 up/up, 3560CX Gi0/1 up/up (May 31, 2026)
- [x] OSPFv2 configured on 3560CX (process 1, router-id 2.2.2.2, passive-interface default, no passive Gi0/1, all VLAN network statements) — config saved (May 31, 2026)
- [x] OSPF adjacency FULL both ways: C1111 (DR, 1.1.1.1) ↔ 3560CX (BDR, 2.2.2.2), Dead timers ~33-34s, hellos every 10s — **Stage 2 Step 2.1 COMPLETE** ✅ — see lab-010-ospfv2.md
- 🔧 Cleanup (separate from cutover): GS308EP DHCP reservation for .100 stuck in Selecting — switch reachable at .95 via regular DHCP. Investigate reservation client-identifier after Stage 2.
**Outage-window steps — COMPLETE ✅ (Jun 1, 2026)**
- [x] HSRP staged on 3560CX only for gateway IP preservation — C1111 is not an HSRP peer and will not remain L2-adjacent to production VLANs after trunk move (Jun 1, 2026) ← **Step 3 COMPLETE**
- [x] Cable 3560CX Gi0/2 → GS308EP Port 1 (replaced C1111 GE0/1/1 trunk) (Jun 1, 2026)
- [x] Cable 3560CX Gi0/3 → GS316EP Port 15 (replaced C1111 GE0/1/2 trunk) (Jun 1, 2026)
- [x] 3560CX trunks active (Jun 1, 2026) ✅
- [x] 3560CX SVIs up/up (Jun 1, 2026) ✅
- [x] HSRP virtual gateways active on 3560CX (Jun 1, 2026) ✅
- [x] C1111 learns LAN routes over OSPF (Jun 1, 2026) ✅
- [x] Client internet works by IP (Jun 1, 2026) ✅
- [x] Pi-hole DNS works from VLAN 20 (Jun 1, 2026) ✅
- [x] Pi renewed DHCP — gateway now 192.168.10.1 (3560CX HSRP VIP) (Jun 1, 2026) ✅
- [x] OSPFv2 adjacency between C1111 and 3560CX — FULL both ways (May 31, 2026) ✅
- [x] STP root: 3560CX confirmed as root bridge (Jun 1, 2026) ✅
- [x] Default route to C1111 via OSPF: STABLE (Jun 1, 2026) ✅
- [x] SSH to 3560CX: works with legacy algorithm flags AND `ssh jlm-lab-sw1` alias (Jun 1, 2026) ✅
- **3560CX IS NOW THE ACTIVE L3 CORE. Phase B trunk cutover complete.** ✅

**Post-cutover cleanup (no outage):**
- [ ] Remove production VLAN SVIs and DHCP pools from C1111 (C1111 becomes edge-only) — VLAN 1 retained temporarily for ISR AP / legacy VLAN 1 segment; it is not part of the migrated production trunk path
- [ ] Remove 3560CX static default once OSPF-learned `O*E2 0.0.0.0/0` is stable
- [ ] True HSRP redundancy (future): requires a second L3-capable device L2-adjacent to production VLANs — not achievable with current topology post-cutover

### Phase C — Proxmox server bring-up 🔄 IN PROGRESS
- [x] Assemble custom ATX server (Ryzen 9 7900X, B650, PA120 SE, SAMA V40, SL-650G)
  - [x] RAM (DDR5 UDIMM 64GB) — installed
  - [x] NVMe (WD Black SN770 2TB) — installed
- [x] Install Proxmox VE bare metal — live at 192.168.100.10 :8006
- [x] Set PPT power cap in motherboard BIOS settings for server efficiency
- [ ] Assign static IP on VLAN 70 (SERVER, 192.168.70.0/24) — pending Phase B cable cutover
- [ ] Trunk both NICs to GS308EP — management on VLAN 70, VM traffic on VLANs 60/70
- [x] Add to Tailscale mesh — pve (100.71.239.21) ✅ online
- [ ] Enable Tailscale subnet routing for VLAN 60 (LAB) → Ohio schoolmate access
- [ ] Deploy Wazuh SIEM as LXC container on Proxmox
- [ ] Install Wazuh agents on Acer, Pi 4B, and Proxmox host
- [ ] Deploy Netdata, NetAlertX, ntfy (completing Phase 4)


### Phase C.1 — Out-of-Band KVM Management 🔄 PLANNED

- [ ] Add Comet GL-RM1PE KVM
- [ ] Install ATX board integration for custom Proxmox server
- [ ] Validate BIOS-level remote console access
- [ ] Validate Proxmox console access through KVM
- [ ] Document recovery workflow for failed VLAN cutover or unreachable Proxmox host
- [ ] Add KVM access notes to the custom Proxmox server build writeup

### Phase D — VLAN 60 schoolmate lab ❌
- [ ] Build VLAN 60 (LAB, 192.168.60.0/24) on 3560CX
- [ ] Deploy Active Directory VM on Proxmox — forest: jlm.lab
- [ ] Deploy osTicket help desk VM on Proxmox (VLAN 60)
- [ ] Deploy M365 admin sandbox (VLAN 60)
- [ ] Configure Tailscale subnet routing for Ohio schoolmate access

### Phase E — AWS Site-to-Site VPN ❌
> **Decision note:** AWS Free Tier for training adds less ground than the physical lab already covers — Free Tier EC2 doesn't go meaningfully further. The Site-to-Site VPN is genuinely useful but belongs here in Phase 5, not before.

- [ ] Create AWS VPC with public subnet
- [ ] Provision Virtual Private Gateway and Customer Gateway (C1111 WAN IP)
- [ ] Configure IKEv2 / IPsec Site-to-Site VPN tunnel on C1111
- [ ] Verify bidirectional routing between home lab subnets and AWS VPC
- [ ] Document tunnel config and BGP/static route options

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

- [x] Ansible project structure built (ansible.cfg, inventory, vault, playbook)
- [x] Netmiko config backup working — C1111 backup verified (May 21, 2026)
- [x] RESTCONF Python API script — 5 live queries verified (May 21, 2026)
- [ ] Ansible roles: MCP server, Ngrok, Pi deployment, CUPS config, Wazuh agent, Netdata agent
- [ ] Cisco config templating via Netmiko (extend to 3560CX after Phase B)
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

## CCNA Lab Progress 🎓

Labs completed and documented in `labs/`:

| Lab | Topic | CCNA Domain |
|---|---|---|
| lab-003-ntp-snmp.md | NTP hierarchy + SNMP | Domain 4 — IP Services |
| lab-004-network-automation.md | Ansible, Netmiko, legacy SSH | Domain 6 — Automation |
| lab-005-restconf.md | RESTCONF REST API + Python | Domain 6 — Automation |
| lab-006-stp-rstp.md | STP/RSTP, Rapid-PVST+ | Domain 2 — Network Access |
| lab-007-ospfv3.md | OSPFv3 IPv6 routing | Domain 3 — IP Connectivity |
| lab-008-aaa.md | AAA local authentication | Domain 5 — Security |
| lab-009-ip-source-guard.md | IP Source Guard | Domain 5 — Security |

Live configurations:
- [x] OSPFv2 — process 1, router-ID 10.0.0.1, 9 networks area 0
- [x] OSPFv3 — process 1, router-ID 10.0.0.1, Lo0 / Vlan10 / Vlan20 in area 0
- [x] IPv6 dual-stack — VLAN 10 (2001:db8:10::/64), VLAN 20 (2001:db8:20::/64)
- [x] DHCP snooping + DAI — VLANs 30,31,40,50,60 on 3560CX
- [x] IP Source Guard — 3560CX Gi0/5–Gi0/8 configured, activates at Phase B
- [x] AAA — aaa new-model, local auth + exec authorization, console + vty hardened, login on-success log
- [x] NTP — C1111 stratum 2, all devices stratum 3
- [x] RESTCONF — enabled on C1111, Python queries verified
- [ ] OSPFv2 adjacency C1111 ↔ 3560CX — pending Phase B
- [ ] HSRP — pending Phase B
- [ ] EtherChannel — pending Phase B
- [x] STP root bridge — 3560CX confirmed root (Jun 1, 2026)
- [ ] PortFast + BPDU Guard on access ports — pending

---

## Ongoing / Blocked

- [ ] IOS rollback on C1111 to pre-16.10.1 (C1111-specific image required)
- [ ] Kasa EP10 smart plugs → VLAN 30 (app issue blocking migration)
- [ ] Ceiling-mount UniFi U6+ APs (physical task)
- [ ] Garage automation: ESP32 + reed switch + relay + Wyze Cam v3 + Frigate NVR
- [ ] HP ENVY 5640 — bring online via CUPS or remove from Instant Ink subscription
- [ ] Algo VPN — planned, not started
- [ ] Add phone and Android 7.0 tablet to Tailscale tailnet

---

## Hardware Status

| Device | Status | Notes |
|---|---|---|
| Cisco C1111-4PWB (JLM-LAB-R1) | ✅ Production | OSPF, IPv6, NTP, RESTCONF live |
| Catalyst 3560CX-8PC-S (JLM-LAB-SW1) | 🔄 Phase A complete | VLANs, SVIs, ACLs, DHCP snooping, DAI staged |
| NETGEAR GS308EP | ✅ Production | VLAN 50 corrected, mgmt IP locked |
| NETGEAR GS316EP | ✅ Production | VLAN 50 added May 19 |
| UniFi U6+ APs (×2) | ✅ Production | 5 SSIDs, desk-mounted pending ceiling mount |
| Raspberry Pi 4B | ✅ Production | Pi-hole, UniFi, Mosquitto, CUPS, NTP client |
| Acer Server | ✅ Production | Docker: MCP + Ngrok, Streamlit, NTP client |
| Proxmox Server (pve) | ✅ Live | Proxmox VE · 192.168.100.10 · SN770 2TB NVMe vmstore · Samsung 860 EVO OS + backup vault · Tailscale 100.71.239.21 · VLAN 70 cabling pending |

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
| Phase 7 | Implement Infrastructure as Code — Ansible, Netmiko, RESTCONF Python API |
| Phase 8 | Communicate technical work through structured labs and case studies |
| **All** | Operate a real production system — not just build one |

---

*Last updated: May 30, 2026 (SX950U added)*