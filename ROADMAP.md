# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform.
> Each phase builds on the previous one and produces portfolio-ready documentation.

---

## Current State (Baseline)

The platform is **already in production** — 3 repos, 546+ posts/week, 24/7 uptime. This roadmap focuses on hardening the infrastructure underneath it.

| Component | Current State | Target State |
|---|---|---|
| Network switches | Netgear GS316EP (16-port, 180W) + GS308EP (8-port, 62W) | VLAN-configured dual-switch topology |
| WiFi | 4× Xfinity XE1-S mesh pods (no VLAN support) | 2× UniFi U6+ APs (VLAN-tagged SSIDs) |
| Network services | None | Raspberry Pi 4B: Pi-hole, UniFi Controller, Uptime Kuma |
| Power protection | None | CyberPower CP1500PFCLCD UPS |
| Server process mgmt | Manual / scripts | Docker Compose + systemd |
| Monitoring | Email alerts via logger.error | Uptime Kuma on Pi 4B + status dashboard |
| Tunnel | Ngrok (free/paid tier) | Evaluate Cloudflare Tunnel |
| Backups | Manual | Automated daily w/ retention |
| Network segmentation | Flat network (all VLAN 1) | Server / Trusted / IoT VLANs |
| Disaster recovery | Rebuild from git repos | One-command Ansible playbook |

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

## Phase 2: Network Hardening 🔄 NEXT

**Goal:** Configure dual-switch VLAN topology, deploy UniFi APs, set up Raspberry Pi network services, and establish network segmentation across 25+ devices.

**Hardware acquired:**
- ✅ Netgear GS316EP (16-port, 15 PoE+, 180W, 1 SFP) — primary switch
- ✅ Netgear GS308EP (8-port, 8 PoE+, 62W) — secondary switch
- ✅ Raspberry Pi 4B + PoE+ HAT + case
- ✅ CyberPower CP1500PFCLCD UPS
- ✅ DYMO label maker
- 🔄 MicroSD card (32GB) — needed for Pi
- 🔲 2× UniFi U6+ APs — replacing 4× Xfinity XE1-S mesh pods

**Est. hours:** 18-22

### Step 1: Physical Infrastructure

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Install UPS, charge 4-6 hours, connect all infra to battery-backed outlets | 1 | Power protection, infrastructure planning |
| Label all ports (patch panel, both switches, cable ends) with DYMO | 1 | Physical documentation, cable management |
| Photograph before/after for repo | 0.5 | Change documentation |
| Install GS316EP as primary switch in panel | 1 | Hardware installation |
| Connect GS308EP as secondary switch via trunk link from GS316EP | 0.5 | Switch interconnect |

### Step 2: Raspberry Pi Setup

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Flash microSD with Raspberry Pi OS Lite (headless, SSH enabled) | 0.5 | OS provisioning |
| Boot Pi via PoE from GS316EP, verify connectivity | 0.5 | PoE-powered device deployment |
| Install Docker on Pi | 0.5 | Containerization |
| Deploy Pi-hole (DNS-level ad blocking + network visibility) | 1 | DNS management |
| Deploy UniFi Network Controller | 1 | WiFi management platform |
| Deploy Uptime Kuma (monitoring — see Phase 4) | 0.5 | Service monitoring |

### Step 3: WiFi Migration

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Install 2× UniFi U6+ APs (PoE from GS316EP, ceiling-mounted) | 1 | Enterprise AP deployment |
| Configure UniFi Controller: create SSIDs per VLAN | 1.5 | VLAN-tagged WiFi |
| Migrate all WiFi devices to new APs | 1 | Network migration |
| Remove Xfinity mesh pods, put gateway in bridge mode | 0.5 | Gateway configuration |
| Verify coverage across 2,800 sq ft single-story home | 0.5 | WiFi site survey |

### Step 4: VLAN Configuration

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Design VLAN scheme across both switches | 1 | Network architecture |
| Configure VLANs on GS316EP (primary) | 1.5 | 802.1Q VLAN configuration |
| Configure matching VLANs on GS308EP (secondary) | 1 | Multi-switch VLAN consistency |
| Configure trunk port between switches | 0.5 | 802.1Q trunking |
| Assign UniFi SSIDs to VLANs (Server, Trusted, IoT) | 1 | WiFi + VLAN integration |
| Set up QoS — prioritize server traffic | 0.5 | Traffic management |
| Test: MCP server reachable from Railway via Ngrok | 0.5 | End-to-end validation |
| Test: IoT devices cannot reach server VLAN | 0.5 | Security verification |
| Document all configs with screenshots | 1.5 | Technical writing |

### VLAN Design (Dual-Switch)

```
VLAN 1  — Management
          GS316EP mgmt: 192.168.1.2
          GS308EP mgmt: 192.168.1.3
          Pi-hole: 192.168.1.4
          Gateway: 192.168.1.1
          Admin access only

VLAN 10 — Servers (Production)
          Subnet: 192.168.10.0/24
          GS316EP port: Acer Aspire 3 (MCP server + fb-content + Ngrok)
          GS316EP port: Raspberry Pi 4B (Pi-hole, UniFi Controller, Uptime Kuma)
          Full internet access for API calls
          Isolated from IoT VLAN

VLAN 20 — Trusted (Personal Devices)
          Subnet: 192.168.20.0/24
          GS308EP ports: iMac, hardwired Apple TV
          UniFi SSID: "Home-Trusted" (MacBooks, phones, tablets)
          Can reach Server VLAN (for management)
          Full internet access

VLAN 30 — IoT (Untrusted Smart Devices)
          Subnet: 192.168.30.0/24
          UniFi SSID: "Home-IoT"
          2× Wyze Cam v3, 4× Kasa Smart Plugs, Ecobee thermostat,
          3× Alexa, Somfy hub, Samsung TV, 2× wireless Apple TVs
          Internet only — NO access to Server or Trusted VLANs

Trunk Links:
          Gateway ↔ GS316EP (port 1): tagged VLAN 1, 10, 20, 30
          GS316EP ↔ GS308EP: tagged VLAN 1, 20, 30
          GS316EP ↔ UniFi APs: tagged VLAN 20, 30

PoE Power Budget (GS316EP — 180W):
          2× UniFi U6+ APs:     ~24W
          1× Raspberry Pi 4B:   ~5W
          Headroom:              ~151W
```

> ⚠️ **Xfinity Gateway Limitation:** The xFi gateway may not support inter-VLAN routing natively. If it can't, Phase 2 focuses on port-level isolation via the managed switches, and a future phase adds a dedicated firewall (pfSense/OPNsense) for full VLAN routing.

**Deliverable:** Documented dual-switch VLAN configuration with UniFi AP deployment, before/after diagrams, PoE power audit, and security verification screenshots.

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
| Configure Uptime Kuma on Pi (deployed in Phase 2) | 1 | Monitoring tools |
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
| Run Nmap scan of home network (all ports, all devices) | 1 | Network reconnaissance |
| Document all open ports and services per device | 1.5 | Attack surface analysis |
| Verify IoT VLAN isolation (scan from IoT → Server) | 1 | Segmentation validation |
| Audit Ngrok configuration (auth, IP allowlist, TLS) | 1 | Tunnel security |
| Evaluate Cloudflare Tunnel as Ngrok replacement | 2 | Zero-trust networking |
| Audit MCP auth token flow (x-mcp-token verification) | 1 | Application security |
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
7. Findings & Risk Ratings
   - Critical / High / Medium / Low
8. Remediation Actions Taken
9. Residual Risk & Recommendations
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

**Deliverable:** One-command server rebuild with Ansible playbook and documented IaC approach.

---

## Timeline Summary

| Phase | Hours | Difficulty | Prereq |
|---|---|---|---|
| Phase 1: Documentation ✅ | 6 | ⭐ | None |
| Phase 2: Network Hardening | 20 | ⭐⭐⭐ | GS316EP, GS308EP, Pi 4B, UPS, UniFi APs, microSD |
| Phase 3: Server Hardening | 16 | ⭐⭐ | Phase 2 |
| Phase 4: Monitoring | 12 | ⭐⭐ | Phase 2 (Uptime Kuma on Pi) |
| Phase 5: Security Audit | 16 | ⭐⭐⭐ | Phase 2 + 3 |
| Phase 6: IaC | 15 | ⭐⭐⭐ | Phase 3 |
| **Total** | **~85 hrs** | | |

> Each phase is a standalone portfolio milestone. Complete one fully before starting the next. Commit documentation as you go.

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly — a skill most engineers lack |
| Phase 2 | Design and implement network segmentation with dual-switch VLAN topology, enterprise WiFi APs, and dedicated network services host |
| Phase 3 | Containerize production services and write operational runbooks |
| Phase 4 | Build monitoring and alerting for production infrastructure |
| Phase 5 | Conduct a professional security audit and write findings |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| **All** | Operate a real production system — not just build one |

---

*Phases can be completed in any order after Phase 1, but the sequence above builds skills progressively and each phase makes the next easier.*
