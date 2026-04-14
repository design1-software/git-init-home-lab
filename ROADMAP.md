# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform.
> Each phase builds on the previous one and produces portfolio-ready documentation.

---

## Current State (Baseline)

The platform is **already in production** — 3 repos, 546+ posts/week, 24/7 uptime. This roadmap focuses on hardening the infrastructure underneath it.

| Component | Current State | Target State |
|---|---|---|
| Edge router (lab) | Cisco C1111-4PWB ISR — configured, SSH-managed | Same, plus VLANs, ACLs, upgraded IOS XE |
| Network switches | GS316EP (household) + GS308EP (lab, uplinked to Cisco) | VLAN-configured dual-switch topology |
| WiFi | 4× Xfinity mesh pods (household) + 2× UniFi U6+ APs (lab, adopted) | UniFi APs cover whole house; Xfinity mesh retired |
| Network services | Pi 4B: Pi-hole (DNS), UniFi Network Application | Plus Uptime Kuma, centralized logging |
| Power protection | CyberPower CP1500PFCLCD UPS — installed | Plus USB auto-shutdown to Acer |
| Server process mgmt | Manual / scripts | Docker Compose + systemd |
| Monitoring | Email alerts via logger.error | Uptime Kuma on Pi 4B + status dashboard |
| Tunnel | Ngrok (free/paid tier) | Evaluate Cloudflare Tunnel |
| Backups | Manual (Cisco config backed up) | Automated daily w/ retention |
| Network segmentation | Dual-network via Cisco (192.168.100.0/24 isolated from 10.0.0.0/24) | Plus VLANs: Server / Trusted / IoT |
| Disaster recovery | Rebuild from git repos + Cisco config backup | One-command Ansible playbook |

---

## Phase 1: Documentation & Baseline ✅ COMPLETE

**Deliverable:** GitHub repo with interactive architecture diagram, README, and full system documentation.

- [x] Photograph all hardware (panel, switch, server, closet)
- [x] Create interactive architecture diagram (`docs/architecture.html`)
- [x] Document all 3 repos with line counts, module maps, and data flows
- [x] Write hardware inventory with connection details
- [x] Document software stack (self-hosted + cloud + APIs)
- [x] Map switch port allocations
- [x] Set up GitHub repo structure

---

## Phase 2: Network Hardening 🔄 IN PROGRESS (~70% complete)

**Goal:** Configure dual-switch VLAN topology, deploy UniFi APs, set up Raspberry Pi network services, deploy enterprise edge routing, and establish network segmentation across 25+ devices.

**Hardware status:**
- [x] Netgear GS316EP (16-port, 15 PoE+, 180W, 1 SFP) — primary switch, in service
- [x] Netgear GS308EP (8-port, 8 PoE+, 62W) — lab switch, uplinked to Cisco
- [x] **Cisco C1111-4PWB ISR — acquired, configured, in service as lab edge router**
- [x] Raspberry Pi 4B + PoE+ HAT + case — deployed, PoE-powered from GS308EP
- [x] CyberPower CP1500PFCLCD UPS — installed, charged, protecting infra
- [x] DYMO label maker — acquired
- [x] MicroSD card (32GB) — flashed with Raspberry Pi OS Lite 64-bit
- [x] 2× UniFi U6+ APs — adopted by controller, broadcasting SSID
- [ ] USB-A to USB-B cable (for UPS auto-shutdown to Acer) — pending

**Est. hours remaining:** 6-8 (VLANs, AP ceiling mount, household WiFi migration)

---

### Step 0: Edge Router Deployment ✅ COMPLETE

> This sub-phase wasn't in the original plan. The acquisition of a Cisco C1111-4PWB changed the architecture — the Cisco now serves as the lab-side edge router, isolating the production lab network from the household Xfinity network.

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Acquire Cisco C1111-4PWB ISR from reputable reseller | — | Enterprise hardware sourcing |
| Out-of-band management: USB-to-DB9 serial adapter + Cisco rollover cable to RJ-45 console | 1 | Serial console, out-of-band admin |
| Console session via PuTTY at 9600 8N1 | 0.5 | Terminal emulation, serial protocols |
| Decline setup wizard, terminate autoinstall, enter privileged mode | 0.25 | IOS XE boot handling |
| Configure WAN (GE0/0/0) as DHCP client to Xfinity XB8 | 0.5 | IOS XE interface config, DHCP client |
| Configure LAN (Vlan1 SVI): 192.168.100.1/24 | 0.5 | Layer 3 SVI, subnet planning |
| Create DHCP pool `LAN` with excluded-address range, DNS servers, 7-day lease | 0.5 | DHCP server configuration |
| Configure NAT overload (PAT): access-list + inside/outside interface marking | 1 | NAT/PAT, access control lists |
| Verified end-to-end: Acer pulls lease, loads websites through Cisco | 0.5 | Network validation |
| Security baseline: hostname, enable secret, service password-encryption | 0.5 | IOS security hardening |
| Console line hardening: password, login, exec-timeout 15, logging synchronous | 0.5 | Console access control |
| Enable SSH: ip domain name, RSA 2048 keys, local admin user with privilege 15 | 1 | SSH server setup, PKI |
| VTY configuration: transport input ssh, login local, timeout | 0.5 | Remote access hardening |
| Force SSHv2, troubleshoot legacy crypto (older IOS only supports group14-sha1 kex + ssh-rsa hostkey vs. modern Windows OpenSSH defaults) | 1.5 | Cross-vendor SSH compatibility |
| Create Windows SSH config with KexAlgorithms/HostKeyAlgorithms overrides (`ssh cisco` alias) | 0.5 | Operator ergonomics |
| DHCP reservation for Pi 4B via Client-Identifier (stable 192.168.100.17) | 0.5 | Static DHCP binding |
| Full running-config backup to timestamped text file | 0.5 | Configuration management |

**Milestones proven:**
- Cisco IOS XE CLI operated end-to-end (console + SSH)
- Enterprise-grade router isolating lab traffic from household traffic
- Full DHCP/NAT/routing path from LAN clients to internet
- SSH access with password hygiene (rotated after a captured-in-screenshot incident; credentials never committed)

---

### Step 1: Physical Infrastructure ✅ COMPLETE

| Task | Status | Skills Demonstrated |
|---|---|---|
| Install UPS, charge, connect all critical infrastructure to battery-backed outlets | ✅ | Power protection, infrastructure planning |
| Mount Cisco C1111, GS316EP, GS308EP in structured media enclosure | ✅ | Hardware installation |
| Connect GS308EP to Cisco LAN port (lab network extension) | ✅ | Switch interconnect |
| Photograph before/after for repo | 🔲 | Change documentation |
| Label all ports (patch panel, both switches, cable ends) with DYMO | 🔲 | Physical documentation |

---

### Step 2: Raspberry Pi Setup ✅ COMPLETE

| Task | Status | Skills Demonstrated |
|---|---|---|
| Flash microSD with Raspberry Pi OS Lite 64-bit (headless, SSH pre-enabled via Pi Imager customization) | ✅ | OS provisioning, headless setup |
| Boot Pi via PoE from GS308EP, verify DHCP lease from Cisco | ✅ | PoE-powered device deployment |
| Full system update (`apt update && apt upgrade`) | ✅ | Linux package management |
| Install Pi-hole (Glennr script, interactive installer, Cloudflare upstream, Show-everything privacy) | ✅ | DNS filtering, recursive resolvers |
| Configure Cisco DHCP to hand out Pi as DNS server for all LAN clients | ✅ | DHCP option 6 / DNS injection |
| Install UniFi Network Application (Glennr installer, v10.1.89, HTTPS on :8443) | ✅ | WiFi management platform |
| Deploy Uptime Kuma for monitoring | 🔲 | See Phase 4 |

---

### Step 3: WiFi Migration 🔄 IN PROGRESS

| Task | Status | Skills Demonstrated |
|---|---|---|
| Power 2× UniFi U6+ APs via PoE+ from GS308EP | ✅ | Enterprise AP deployment |
| Controller auto-discovery of APs (same L2 segment as controller via GS308EP + Cisco) | ✅ | UniFi adoption workflow |
| Firmware upgrade during adoption | ✅ | UniFi Controller operations |
| Run UniFi setup wizard, create Ubiquiti cloud account, configure server name | ✅ | UniFi site configuration |
| Configure first SSID (`Gorgeous1` for testing to avoid household conflict) | ✅ | SSID configuration |
| Test client connectivity (iPhone, Apple TV streaming validation) | ✅ | Real-world validation |
| Measure signal strength across house from APs in closet (floor case for performance) | ✅ | WiFi site survey, RSSI analysis |
| Rename SSID back to `Gorgeous` | 🔲 | Pending household migration |
| Migrate all household WiFi devices to UniFi APs | 🔲 | Network migration |
| Remove Xfinity mesh pods, put XB8 in bridge mode | 🔲 | Gateway configuration |
| Physical ceiling-mount APs (purchased mounting kits already) | 🔲 | Physical installation |

---

### Step 4: VLAN Configuration 🔲 NEXT

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Design VLAN scheme on paper (subnets, device map, ACL rules) | 1 | Network architecture |
| Configure VLANs on Cisco (subinterfaces on Vlan1 replaced with per-VLAN SVIs) | 2 | IOS 802.1Q, SVI per VLAN |
| Configure matching VLANs + trunk on GS308EP | 1 | Multi-switch VLAN consistency |
| Configure trunk between Cisco and GS308EP (allowed VLANs: 10, 20, 30) | 0.5 | 802.1Q trunking |
| Per-VLAN DHCP pools on Cisco (one per subnet) | 1 | DHCP scope management |
| Assign UniFi SSIDs to VLANs (Trusted → VLAN 20, IoT → VLAN 30) | 1 | WiFi + VLAN integration |
| Write extended ACLs for inter-VLAN firewalling (IoT cannot reach Server/Trusted) | 1.5 | Access control lists |
| Test: MCP server reachable from Railway via Ngrok | 0.5 | End-to-end validation |
| Test: IoT devices cannot reach server VLAN | 0.5 | Security verification |
| Document all configs with screenshots | 1.5 | Technical writing |

### VLAN Design (Target)

```
VLAN 1  — Management (default)
          GS308EP mgmt, GS316EP mgmt (when migrated)
          Cisco L3 gateway: 192.168.1.1 (reassign)

VLAN 10 — Servers (Production)
          Subnet: 192.168.10.0/24
          Cisco SVI: 192.168.10.1
          Ports: Acer Aspire 3 (MCP server + fb-content + Ngrok)
                 Raspberry Pi 4B (Pi-hole, UniFi Controller)
          Full internet access for API calls
          Isolated from IoT VLAN

VLAN 20 — Trusted (Personal Devices)
          Subnet: 192.168.20.0/24
          Cisco SVI: 192.168.20.1
          Ports: iMac, hardwired Apple TV
          UniFi SSID: "Gorgeous" (MacBooks, phones, tablets)
          Can reach Server VLAN (for management)
          Full internet access

VLAN 30 — IoT (Untrusted Smart Devices)
          Subnet: 192.168.30.0/24
          Cisco SVI: 192.168.30.1
          UniFi SSID: "Gorgeous-IoT"
          2× Wyze Cam v3, 4× Kasa Smart Plugs, Ecobee,
          3× Alexa, Somfy hub, Samsung TV, 2× wireless Apple TVs
          Internet only — NO access to Server or Trusted VLANs

Trunk Links:
          Cisco ↔ GS308EP: tagged VLAN 1, 10, 20, 30
          Cisco ↔ GS316EP (after migration): tagged VLAN 1, 10, 20, 30
          GS308EP ↔ UniFi APs: tagged VLAN 20, 30

PoE Power Budget (GS308EP — 62W):
          2× UniFi U6+ APs:     ~24W
          1× Raspberry Pi 4B:   ~5W
          Headroom:              ~33W
```

> Note: With the Cisco C1111 as lab edge router, full inter-VLAN routing is handled natively — no need for a separate pfSense/OPNsense firewall.

**Deliverable:** Documented VLAN configuration across Cisco and both Netgear switches, UniFi AP VLAN-tagged SSIDs, before/after diagrams, PoE power audit, and security verification screenshots.

---

## Phase 3: Server Hardening

**Goal:** Containerize the production services, implement proper process management, and create recovery procedures.

**Est. hours:** 14-16

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Install Docker & Docker Compose on Acer server | 1 | Containerization |
| Containerize `social-media-mcp` (Dockerfile + compose) | 3 | Docker multi-stage builds |
| Containerize Ngrok agent as sidecar container | 1 | Service orchestration |
| Create `docker-compose.yml` with health checks | 2 | Docker Compose patterns |
| Configure auto-restart on boot (systemd + Docker restart policy) | 1 | System administration |
| Implement `/health` endpoint on MCP server | 0.5 | API design |
| Set up log rotation (Docker logging driver) | 0.5 | Log management |
| Create automated backup script (configs + SQLite + env) | 2 | Bash scripting |
| Write runbook: server restart procedure | 1 | Operations documentation |
| Write runbook: Ngrok tunnel recovery | 1 | Incident response |
| Write runbook: full disaster recovery (bare metal → production) | 1.5 | DR planning |
| Test: full stop + restart of all services | 1 | DR validation |

### Target Docker Architecture

```yaml
# docker-compose.yml
services:
  mcp-server:
    build: ./social-media-mcp
    ports:
      - "3000:3000"
    restart: always
    env_file: .env
    volumes:
      - ./storage:/app/storage
      - ./sessions:/app/sessions
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ngrok:
    image: ngrok/ngrok:latest
    command: http mcp-server:3000
    env_file: .env.ngrok
    restart: always
    depends_on:
      mcp-server:
        condition: service_healthy

  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: always
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400
```

**Deliverable:** Dockerized services with compose stack, health checks, and 3 runbooks.

---

## Phase 4: Monitoring & Observability

**Goal:** Know when things break before they impact the 546 posts/week pipeline.

**Host:** Raspberry Pi 4B (dedicated monitoring, separate from production server)

**Est. hours:** 10-12

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Install Uptime Kuma on Pi | 1 | Monitoring tools |
| Configure monitors: MCP server, Ngrok endpoint, Railway app | 1.5 | Service monitoring |
| Monitor Meta Graph API token expiration | 1 | API lifecycle management |
| Create public status page | 0.5 | Public-facing operations |
| Write `health-check.ps1` (server + services + disk + memory) | 1.5 | PowerShell scripting |
| Write `tunnel-monitor.ps1` (auto-restart Ngrok on disconnect) | 1.5 | Automated recovery |
| Set up email/SMS alerts on service down | 1 | Alerting systems |
| Track uptime metrics over 30 days | 1 | SLA measurement |
| Document monitoring architecture | 1 | Technical writing |

### Monitoring Targets

| Service | Check | Alert Threshold | Monitor Host |
|---|---|---|---|
| social-media-mcp (:3000) | HTTP GET /health | Down > 60s | Pi (Uptime Kuma) |
| Ngrok tunnel (public URL) | HTTP GET /health | Down > 120s | Pi (Uptime Kuma) |
| meta_engagement_pipeline | Railway health check | Down > 300s | Pi (Uptime Kuma) |
| Meta Graph API token | Expiry check | < 7 days remaining | Pi (Uptime Kuma) |
| Cisco C1111 | SSH reachability + `show ip interface brief` | Down > 60s | Pi (Uptime Kuma) |
| Pi-hole DNS | Service check | Down > 30s | Pi (self-check) |
| UniFi APs | Controller check | AP offline > 60s | Pi (UniFi Controller) |
| Server disk usage | df check | > 85% | Acer (health-check.ps1) |
| Server memory | free check | > 90% | Acer (health-check.ps1) |
| Docker containers | docker ps | Any container not running | Acer (health-check.ps1) |
| UPS status | Battery check | Battery < 20% or on battery | Pi (Uptime Kuma) |

**Deliverable:** Live monitoring dashboard with alerting, watchdog scripts, and 30-day uptime report.

---

## Phase 5: Security Audit

**Goal:** Demonstrate professional security methodology — scan, document, remediate, verify.

**Est. hours:** 14-16

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Run Nmap scan of both networks (household 10.0.0.0/24 + lab 192.168.100.0/24) | 1.5 | Network reconnaissance |
| Document all open ports and services per device | 1.5 | Attack surface analysis |
| Verify IoT VLAN isolation (scan from IoT → Server) | 1 | Segmentation validation |
| Audit Ngrok configuration (auth, IP allowlist, TLS) | 1 | Tunnel security |
| Evaluate Cloudflare Tunnel as Ngrok replacement | 2 | Zero-trust networking |
| Audit MCP auth token flow (x-mcp-token verification) | 1 | Application security |
| Cisco IOS XE upgrade path (needed for modern SSH crypto) | 2 | Network device lifecycle |
| Install & configure fail2ban on server | 1 | Intrusion prevention |
| Rotate all API keys (Meta, Anthropic, Grok, ElevenLabs, Kie, Suno) | 1 | Credential hygiene |
| Implement .env encryption (SOPS or age) | 1.5 | Secrets management |
| Write security findings report (findings + mitigations) | 2 | Security documentation |
| Write incident response plan | 1.5 | Security operations |

### Security Audit Report Structure

```
1. Executive Summary
2. Scope & Methodology
3. Network Scan Results
   - Open ports per device
   - Unexpected services
4. VLAN Isolation Verification
   - Cross-VLAN reachability matrix
5. Tunnel Security Assessment
   - Ngrok config review
   - Auth token flow analysis
6. Credential Audit
   - Key rotation dates
   - Storage method verification
7. Cisco IOS Security
   - SSH algorithm negotiation
   - Line/VTY access controls
   - Privilege-level verification
8. Findings & Risk Ratings
   - Critical / High / Medium / Low
9. Remediation Actions Taken
10. Residual Risk & Recommendations
```

**Deliverable:** Professional security audit report with findings, mitigations, and incident response plan.

---

## Phase 6: Infrastructure as Code

**Goal:** Rebuild the entire stack from bare metal with one command.

**Est. hours:** 12-15

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Create Ansible playbook: base server setup (packages, Docker, users) | 3 | Configuration management |
| Create Ansible role: MCP server deployment | 2 | IaC patterns |
| Create Ansible role: Ngrok tunnel setup | 1 | Service provisioning |
| Create Ansible role: Pi deployment (Pi-hole + UniFi Controller) | 2 | Declarative config |
| Template Cisco config for pushing via Netmiko/Ansible | 2 | Network automation |
| Template all config files (.env, docker-compose, ngrok.yml) | 2 | Configuration templating |
| Create `setup.sh` bootstrap (for systems without Ansible) | 1.5 | Shell automation |
| Test: wipe server, run playbook, verify production state | 2 | DR validation |
| Document: environment variable reference | 1 | Configuration docs |
| Optional: GitHub Actions for auto-deploy on push | 2 | Continuous deployment |

### Recovery Time Target

| Scenario | Current RTO | Phase 6 RTO |
|---|---|---|
| Service crash | ~5 min (auto-restart) | ~5 min (unchanged) |
| Tunnel disconnect | ~2 min (auto-reconnect) | ~2 min (unchanged) |
| Full server reboot | ~15-20 min (manual) | ~5 min (Docker auto-start) |
| Bare metal rebuild | ~4-6 hours (manual) | ~30 min (Ansible playbook) |
| Config corruption | Unknown | ~10 min (git + Ansible) |
| Cisco config loss | ~1 hour (manual re-keying) | ~5 min (paste saved config via console) |

**Deliverable:** One-command server rebuild with Ansible playbook and documented IaC approach.

---

## Timeline Summary

| Phase | Hours | Difficulty | Status |
|---|---|---|---|
| Phase 1: Documentation ✅ | 6 | ⭐ | Complete |
| Phase 2: Network Hardening | 20 | ⭐⭐⭐ | ~70% complete |
| Phase 3: Server Hardening | 16 | ⭐⭐ | Not started |
| Phase 4: Monitoring | 12 | ⭐⭐ | Not started |
| Phase 5: Security Audit | 16 | ⭐⭐⭐ | Not started |
| Phase 6: IaC | 15 | ⭐⭐⭐ | Not started |
| **Total** | **~85 hrs** | | |

> Each phase is a standalone portfolio milestone. Complete one fully before starting the next. Commit documentation as you go.

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly — a skill most engineers lack |
| Phase 2 | Deploy enterprise network infrastructure: Cisco IOS XE edge routing, dual-switch PoE topology, Raspberry Pi services host, UniFi controller-managed APs, and VLAN segmentation |
| Phase 3 | Containerize production services and write operational runbooks |
| Phase 4 | Build monitoring and alerting for production infrastructure |
| Phase 5 | Conduct a professional security audit and write findings |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| **All** | Operate a real production system — not just build one |

---

*Phases can be completed in any order after Phase 1, but the sequence above builds skills progressively and each phase makes the next easier.*

*Last updated: April 14, 2026*
