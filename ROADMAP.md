# 🗺️ Project Roadmap

> Phased plan to harden, secure, and professionalize the infrastructure behind a 78K-line production AI content platform.
> Each phase builds on the previous one and produces portfolio-ready documentation.

---

## Current State (Baseline)

The platform is **already in production** — 3 repos, 546+ posts/week, 24/7 uptime. This roadmap focuses on hardening the infrastructure underneath it.

| Component | Current State | Target State |
|---|---|---|
| Network switch | TP-Link TL-SG108 (unmanaged) | TP-Link TL-SG108E (managed, VLANs) |
| Server process mgmt | Manual / scripts | Docker Compose + systemd |
| Monitoring | Email alerts via logger.error | Uptime Kuma + status dashboard |
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

**Goal:** Replace unmanaged switch, implement VLANs, establish network segmentation.

**Hardware:** TP-Link TL-SG108E (~$30)

**Est. hours:** 10-12

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Purchase & install TL-SG108E (direct swap in panel) | 1 | Hardware installation |
| Access switch web GUI, change default credentials | 0.5 | Device management, first-login security |
| Design VLAN scheme | 1 | Network architecture |
| Configure VLAN 10 — Servers (port 2: Acer MCP server) | 1 | 802.1Q VLAN configuration |
| Configure VLAN 20 — Trusted (ports 3-5: personal devices) | 1 | Network segmentation |
| Configure VLAN 30 — IoT (ports 6-8: Somfy, smart TVs, consoles) | 1 | IoT isolation |
| Configure trunk port to Xfinity gateway (port 1) | 1 | 802.1Q trunking |
| Test: MCP server reachable from Railway via Ngrok | 0.5 | End-to-end validation |
| Test: IoT devices cannot reach server VLAN | 0.5 | Security verification |
| Set up QoS — prioritize port 2 (server) traffic | 1 | Traffic management |
| Enable port mirroring → server for traffic analysis | 0.5 | Network forensics |
| Document all configs with screenshots | 1.5 | Technical writing |

### VLAN Design

```
VLAN 1  — Management
          Switch mgmt: 192.168.1.2
          Gateway: 192.168.1.1
          Admin access only

VLAN 10 — Servers
          Subnet: 192.168.10.0/24
          Port 2: Acer Aspire 3 (social-media-mcp + fb-content-system + Ngrok)
          Full internet access for API calls
          Isolated from IoT VLAN

VLAN 20 — Trusted
          Subnet: 192.168.20.0/24
          Ports 3-5: Personal laptops, phones (via WiFi bridge)
          Can reach Server VLAN (for management)
          Full internet access

VLAN 30 — IoT
          Subnet: 192.168.30.0/24
          Ports 6-8: Somfy hub, smart TVs, game consoles
          Internet only — NO access to Server or Trusted VLANs
```

> ⚠️ **Xfinity Gateway Limitation:** The xFi gateway may not support inter-VLAN routing natively. If it can't, Phase 2 focuses on port-level isolation via the managed switch, and a future phase adds a dedicated firewall (pfSense/OPNsense) for full VLAN routing.

**Deliverable:** Documented VLAN configuration with before/after diagrams and security verification screenshots.

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

**Est. hours:** 10-12

| Task | Hours | Skills Demonstrated |
|---|---|---|
| Deploy Uptime Kuma (Docker container) | 1 | Monitoring tools |
| Configure monitors: MCP server, Ngrok endpoint, Railway app | 1.5 | Service monitoring |
| Monitor Meta Graph API token expiration | 1 | API lifecycle management |
| Create public status page | 0.5 | Public-facing operations |
| Write `health-check.sh` (server + services + disk + memory) | 1.5 | Bash scripting |
| Write `tunnel-monitor.sh` (auto-restart Ngrok on disconnect) | 1.5 | Automated recovery |
| Set up email/SMS alerts on service down | 1 | Alerting systems |
| Track uptime metrics over 30 days | 1 | SLA measurement |
| Document monitoring architecture | 1 | Technical writing |

### Monitoring Targets

| Service | Check | Alert Threshold |
|---|---|---|
| social-media-mcp (:3000) | HTTP GET /health | Down > 60s |
| Ngrok tunnel (public URL) | HTTP GET /health | Down > 120s |
| meta_engagement_pipeline | Railway health check | Down > 300s |
| Meta Graph API token | Expiry check | < 7 days remaining |
| Server disk usage | df check | > 85% |
| Server memory | free check | > 90% |
| Docker containers | docker ps | Any container not running |

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
| Phase 2: Network Hardening | 12 | ⭐⭐ | TL-SG108E (~$30) |
| Phase 3: Server Hardening | 16 | ⭐⭐ | Phase 2 |
| Phase 4: Monitoring | 12 | ⭐⭐ | Phase 3 |
| Phase 5: Security Audit | 16 | ⭐⭐⭐ | Phase 2 + 3 |
| Phase 6: IaC | 15 | ⭐⭐⭐ | Phase 3 |
| **Total** | **~77 hrs** | | |

> Each phase is a standalone portfolio milestone. Complete one fully before starting the next. Commit documentation as you go.

---

## What This Proves to Employers

| Phase | Proves You Can... |
|---|---|
| Phase 1 | Document complex systems clearly — a skill most engineers lack |
| Phase 2 | Design and implement network segmentation from scratch |
| Phase 3 | Containerize production services and write operational runbooks |
| Phase 4 | Build monitoring and alerting for production infrastructure |
| Phase 5 | Conduct a professional security audit and write findings |
| Phase 6 | Implement Infrastructure as Code for repeatable deployments |
| **All** | Operate a real production system — not just build one |

---

*Phases can be completed in any order after Phase 1, but the sequence above builds skills progressively and each phase makes the next easier.*
