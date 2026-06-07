# 🏠 Production AI Content Platform — Home Lab Infrastructure

> 78,000+ lines of production code running 24/7 on self-hosted infrastructure, powering automated content creation across 3 Facebook pages with 546+ posts per week.

[![Status](https://img.shields.io/badge/status-production-brightgreen)]()
[![Server](https://img.shields.io/badge/server-24%2F7-blue)]()
[![Posts](https://img.shields.io/badge/output-546%2B_posts%2Fweek-orange)]()
[![Code](https://img.shields.io/badge/codebase-78K%2B_lines-purple)]()

---

## Overview

This repository documents the infrastructure behind a **production AI content platform** — a system that generates, renders, scores, schedules, and publishes social media content at scale across 3 Facebook pages, entirely automated.

The platform spans **3 interconnected repositories**, a **self-hosted MCP server** running on home lab hardware, **cloud orchestration** on Railway, and **8 external API integrations** — all connected through a secure Ngrok tunnel.

**This is not a tutorial.** This is a live production system managing real pages, real audiences, and real API traffic.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                │
│  Meta Graph API  ·  Anthropic Claude  ·  xAI Grok  ·  OpenAI          │
│  ElevenLabs TTS  ·  Kie.ai Images    ·  Suno Music ·  Perplexity      │
└──────────────┬───────────────────────────────────────┬──────────────────┘
               │ Webhooks                              │ HTTPS
┌──────────────┴──────────────────┐    ┌───────────────┴──────────────┐
│   RAILWAY (Cloud)               │    │   NGROK TUNNEL               │
│   meta_engagement_pipeline      │    │   Public HTTPS → :3000       │
│   36,475 lines · Express+Worker │◄──►│   Fixed domain: mea.ngrok.app│
│   PM2: mlx-poster, feed-engager │    │   Docker sidecar container   │
│   Postgres · Cron · Scoring     │    └───────────────┬──────────────┘
└─────────────────────────────────┘                    │
                                                       │
┌──────────────────────────────────────────────────────┴──────────────────┐
│   NETWORK LAYER — VLAN-Segmented Lab Topology                           │
│                                                                         │
│   Xfinity XB8 (Bridge Mode — modem only)                               │
│     └─ Cisco C1111-4PWB WAN (DHCP client, public IP from Comcast)      │
│            │                                                            │
│   Cisco C1111-4PWB (JLM-LAB-R1) — WAN Edge                             │
│   NAT · DHCP · ACLs · SSH · OSPFv2 neighbor · Smart Licensing REGISTERED│
│            │ GE0/1/0 → TRANSIT (192.168.199.0/30, VLAN 199)             │
│            │                                                            │
│   Catalyst 3560CX-8PC-S (JLM-LAB-SW1) — Active L3 Core                 │
│   VLAN gateways · HSRP VIPs · Inter-VLAN routing · OSPFv2 · STP root   │
│            │                                                            │
│     ┌──────┴───────────────────────────────────────────────┐           │
│     │  Gi0/2 → GS308EP (8-port PoE+, Advanced 802.1Q)      │           │
│     │    Port 2: Acer Server (VLAN 10, 192.168.10.11)       │           │
│     │    Port 3: Pi 4B (VLAN 10, PoE, 192.168.10.16)       │           │
│     │    Port 4: UniFi U6+ AP #1 (VLANs 20,30,31,40,50,99)│           │
│     │    Port 5: UniFi U6+ AP #2 (VLANs 20,30,31,40,50,99)│           │
│     │    Mgmt IP: 192.168.100.95 (DHCP reserved)           │           │
│     │                                                       │           │
│     │  Gi0/3 → GS316EP (16-port PoE+, household)           │           │
│     │    Ports 2-4: Apple TVs (VLAN 20)                    │           │
│     │    Port 15: Trunk to 3560CX Gi0/3                    │           │
│     │    Mgmt IP: 192.168.100.96                           │           │
│     │                                                       │           │
│     │  Gi0/4 → ARIA Proxmox (VLAN 70, 192.168.70.10)        │           │
│     │  Gi0/5 → Comet GL-RM1PE KVM (PoE, VLAN 10 MGMT)     │           │
│     └───────────────────────────────────────────────────────┘           │
│                                                                         │
│   WiFi SSIDs (5 active):                                                │
│     Gorgeous        → VLAN 20 (TRUSTED)                                 │
│     Gorgeous-IoT    → VLAN 30 (IOT)                                     │
│     Gorgeous-Auto   → VLAN 31 (IOT-AUTO)                                │
│     Gorgeous-Home   → VLAN 40 (HOUSEHOLD)                               │
│     JM&G-GUEST      → VLAN 50 (JM&G-GUEST, client isolation)            │
│                                                                         │
│   DNS: Pi-hole (192.168.10.16) serving all VLANs                        │
│   UPS #1: CyberPower CP1500PFCLCD — critical infra (auto-shutdown)     │
│   UPS #2: CyberPower SX950U — office Tailscale nodes (950VA/510W)      │
│   Remote: Tailscale mesh VPN (8 nodes — see table below)               │
│   No port forwarding — all ingress via Ngrok tunnel                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                   │ Ethernet
┌──────────────────────────────────┴──────────────────────────────────────┐
│   HOME SERVER — Acer Aspire 3 15 (192.168.10.11) — 24/7               │
│                                                                         │
│   ┌─── Docker Compose Stack ───────────────────────────────┐           │
│   │  mcp-server    (social-media-mcp, :3000)               │           │
│   │  ngrok-tunnel  (fixed domain, depends_on: healthy)     │           │
│   │  Health checks · Auto-restart · Log rotation           │           │
│   └────────────────────────────────────────────────────────┘           │
│   closet-monitor subscriber + Streamlit dashboard (:8501)              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│   RASPBERRY PI 4B (192.168.10.16) — PoE powered                        │
│   Pi-hole · UniFi Controller · Mosquitto MQTT · CUPS Print Server      │
│   └─ USB → HP ENVY Inspire 7200e (print queue: HP_Envy_Lab)           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│   MACBOOK PRO — Development                                             │
│   fb-content-system  (22,067 lines · 182 posts/wk × 3 pages)          │
│   └─ Weekly bulk content creation + real-time comment response          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Current Operational State

| System | Status | Details |
|---|---|---|
| Cisco C1111-4PWB (JLM-LAB-R1) | ✅ Online | WAN edge, NAT, OSPF neighbor — VLAN 1 retained for ISR AP/legacy segment; remaining SVIs/DHCP pending cleanup |
| Catalyst 3560CX-8PC-S (JLM-LAB-SW1) | ✅ Production | Active L3 core — VLAN gateways, HSRP VIPs, inter-VLAN ACLs, OSPF, trunks to GS308EP + GS316EP |
| GS308EP (Lab Switch) | ✅ Production | Advanced 802.1Q, 8 VLANs, trunk → 3560CX Gi0/2, mgmt IP 192.168.100.95 |
| GS316EP (Household Switch) | ✅ Production | Advanced 802.1Q, trunk port 15 → 3560CX Gi0/3 |
| Pi 4B | ✅ Multi-service | Pi-hole, UniFi Controller, Mosquitto MQTT, CUPS |
| UniFi Controller | ✅ Active | v10.1.89 on Pi, 2 APs adopted |
| UniFi U6+ APs (×2) | ✅ Broadcasting | 5 SSIDs on 5 VLANs, pending ceiling mount |
| VLAN segmentation | ✅ Implemented | 8 VLANs active, 4 ACLs enforcing isolation |
| CyberPower CP1500PFCLCD (UPS #1) | ✅ Protecting infra | Auto-shutdown via PowerPanel Personal (USB-B to Acer) |
| CyberPower SX950U (UPS #2) | ✅ Active | 950VA/510W · 12 outlets · 890J surge · currently protecting office Tailscale nodes — not yet on network infra |
| Acer Server | ✅ Dockerized | social-media-mcp + Ngrok in Docker Compose, auto-restart |
| CUPS Print Server | ✅ Serving | Pi → USB → HP ENVY 7200e |
| Xfinity bridge mode | ✅ Active | Cisco sole router, public IP via DHCP from Comcast |
| Tailscale | ✅ Connected | 8 nodes on mesh VPN (see table below) |
| closet-monitor | ✅ Production | ESP32 → MQTT → Pi → SQLite → Streamlit dashboard |
| Proxmox Server (pve) | ✅ Production | Proxmox VE · 192.168.70.10 · web UI :8006 · Tailscale: pve / 100.71.239.21 · BIOS PPT power cap completed in motherboard settings · VLAN 70 active |
| Comet GL-RM1PE KVM | ✅ Active | VLAN 10 MGMT · 192.168.10.12 · PoE from 3560CX Gi0/5 (15.4W) · KVM video + keyboard + BIOS access PASS · WoL power-on PASS · ATX control board pending (defective returned) |
| IoT device migration | 🔄 Mostly done | Ring, Alexa, Ecobee, Somfy, Samsung TV migrated · Kasa plugs pending |

---

## Tailscale Nodes

| Hostname | Tailscale IP | Device | OS |
|---|---|---|---|
| juliuss-macbook-pro | 100.111.203.45 | MacBook Pro | macOS |
| jmg-server | 100.113.164.125 | Acer Server | Windows 11 25H2 |
| jlm-lab-pi | 100.122.55.14 | Raspberry Pi 4B | Linux |
| juliuss-imac | 100.75.3.82 | iMac | macOS |
| desktop-opm9863 | 100.87.58.10 | Desktop | Windows 10 |
| macbook-air | 100.102.47.66 | MacBook Air | macOS |
| pve | 100.71.239.21 | Proxmox Server | Linux (Proxmox VE) |
| jm-swe | 100.74.46.90 | Desktop (Windows) | Windows |

> Phone and Android 7.0 tablet pending addition.

---

## Hardware Inventory

### Network Infrastructure

| Device | Model | Role | Status |
|---|---|---|---|
| ISP Gateway | Xfinity XB8 | Modem only (bridge mode) | ✅ Active |
| Edge Router | Cisco C1111-4PWB ISR | NAT, VLANs, ACLs, DHCP, SSH | ✅ Active |
| Core Switch | Catalyst 3560CX-8PC-S | Active L3 core — VLAN gateways, HSRP VIPs, OSPFv2, STP root | ✅ Production |
| Lab Switch | Netgear GS308EP | 8-port PoE+, Advanced 802.1Q | ✅ Active |
| Household Switch | Netgear GS316EP | 16-port PoE+, Advanced 802.1Q | ✅ Active |
| UPS #1 | CyberPower CP1500PFCLCD | Battery backup, auto-shutdown (USB-B → Acer) | ✅ Active |
| UPS #2 | CyberPower SX950U | 950VA/510W · 12 outlets · 890J surge · office Tailscale nodes — not yet on network infra | ✅ Active |
| WiFi | 2× Ubiquiti UniFi U6+ | 5 VLAN-tagged SSIDs | ✅ Active |

### Compute

| Device | Model | Role | Status |
|---|---|---|---|
| Home Server | Acer Aspire 3 15 | Docker: MCP Server + Ngrok (24/7) · VLAN 10 | ✅ Active |
| Network Services | Raspberry Pi 4B + PoE HAT | Pi-hole, UniFi, MQTT, CUPS · VLAN 10 | ✅ Active |
| Proxmox Server | Custom ATX (Ryzen 9 7900X) | Hypervisor — Proxmox VE · BIOS PPT power cap completed in motherboard settings · OS: Samsung 860 EVO (/dev/sda) · vmstore: WD Black SN770 2TB NVMe (LVM-thin, 1.8TB) · backup vault: Samsung 860 EVO (458GB) · NICs: Intel I225V (mgmt) · Realtek RTL8125 (future VM trunk) · IP: 192.168.70.10 · web :8006 · Tailscale: pve / 100.71.239.21 · VLAN 70 active | ✅ Production |
| Out-of-Band KVM | Comet GL-RM1PE KVM | KVM-over-IP — VLAN 10 MGMT · 192.168.10.12 · PoE from 3560CX Gi0/5 · video + keyboard + BIOS access PASS · WoL power-on PASS · ATX control board pending (defective returned) | ✅ Active |
| Printer | HP ENVY Inspire 7200e | USB to Pi (CUPS) · WiFi on VLAN 30 | ✅ Active |
| Laptop | MacBook Pro | Development + fb-content-system | ✅ Active |

---

## VLAN Scheme

| VLAN | Name | Subnet | SSID | ACL | Status |
|---|---|---|---|---|---|
| 1 | DEFAULT | 192.168.100.0/24 | — | None | ✅ Active (legacy, retirement planned) |
| 10 | MGMT | 192.168.10.0/24 | (wired) | None | ✅ Active |
| 20 | TRUSTED | 192.168.20.0/24 | Gorgeous | None | ✅ Active |
| 30 | IOT | 192.168.30.0/24 | Gorgeous-IoT | IOT-ACL | ✅ Active |
| 31 | IOT-AUTO | 192.168.31.0/24 | Gorgeous-Auto | IOT-AUTO-ACL | ✅ Active |
| 40 | HOUSEHOLD | 192.168.40.0/24 | Gorgeous-Home | HOUSEHOLD-ACL | ✅ Active |
| 50 | JM&G-GUEST | 192.168.50.0/24 | JM&G-GUEST | GUEST-ACL | ✅ Active |
| 99 | MGMT/NATIVE | 192.168.99.0/24 | — | None | ✅ Active (native on trunks) |
| 60 | LAB | 192.168.60.0/24 | — | TBD | ❌ Pending Phase D |
| 70 | SERVER | 192.168.70.0/24 | — | TBD | ✅ Active |
| 199 | TRANSIT | 192.168.199.0/30 | — | None | ✅ Active Phase B |

> 📄 See [docs/vlan-design.md](docs/vlan-design.md) for the full VLAN design with ACL rules, switch configs, and lessons learned.

---

## Security

- **Zero port forwarding** — all ingress via Ngrok tunnel (fixed domain, Docker sidecar)
- **VLAN segmentation** — 8 VLANs with inter-VLAN ACLs enforcing isolation
- **ACLs** — IOT: internet-only; IOT-AUTO: MQTT-only to Pi; HOUSEHOLD: internet-only; GUEST: internet-only with client isolation
- **Containerized services** — Docker Compose with health checks, auto-restart, log rotation
- **CUPS access control** — print from VLAN 10/20/40; admin restricted to VLAN 20
- **Printer hardening** — Wi-Fi Direct disabled, HP marketing data disabled, admin password changed
- **Remote access** — Tailscale mesh VPN (8 nodes, jbm0674@gmail.com)
- **UPS auto-shutdown** — CyberPower CP1500PFCLCD (primary), graceful shutdown at 20% battery · CyberPower SX950U (office, 950VA/510W — currently protecting Tailscale nodes, not yet on network infra)
- **TCP MSS clamping** — `ip tcp adjust-mss 1380` on WAN interface (verified)
- **Cisco IOS hardening** — enable secret (Type 9), console timeout, service password-encryption, SSHv2, local auth
- **AAA** — `aaa new-model`, local authentication + exec authorization, console + vty hardened, `login on-success log`
- **Rapid-PVST+** — JLM-LAB-SW1 (3560CX): Extended system ID enabled, Bridge Assurance configured
- **DNS filtering** — Pi-hole blocking 87K+ domains, serving all VLANs
- **Smart Licensing** — C1111 REGISTERED to EngageMea.com Smart Account

---

## The Three Repositories

### [`social-media-mcp`](https://github.com/design1-software/social-media-mcp) — The MCP Server

**19,753 lines · TypeScript · Self-hosted 24/7**

MCP (Model Context Protocol) server exposing AI-powered content creation tools over SSE. Runs on the Acer server, tunneled to the internet via Ngrok.

### [`meta_engagement_pipeline`](https://github.com/design1-software/meta_engagement_pipeline) — The Cloud Orchestrator

**36,475 lines · JavaScript · Railway**

Dual-engine engagement system — Graph API Engine for official page actions, Sidecar Engine for browser-automated profile actions via MCP bridge.

### [`fb-content-system`](https://github.com/design1-software/fb-content-system) — The Content Factory

**22,067 lines · JS/TS/Python · MacBook Pro**

Produces 182 posts per week per page across 3 Facebook pages.

---

## Skills Demonstrated

| Domain | Implementation |
|---|---|
| **Enterprise Networking** | Cisco IOS XE: 8 VLANs, SVIs, inter-VLAN routing, extended ACLs, NAT/PAT, DHCP (8 pools), 802.1Q trunking, SSH, Smart Licensing, OSPFv3 (IPv6), IP Source Guard, AAA |
| **Network Infrastructure** | Dual managed switch topology, Netgear Advanced 802.1Q, enterprise PoE+ AP deployment, VLAN-tagged WiFi (5 SSIDs) |
| **L3 Switching** | Catalyst 3560CX-8PC-S active as production L3 core — VLAN gateways, HSRP VIPs, OSPFv2, STP root, trunks to GS308EP + GS316EP (Phase B complete Jun 1, 2026) |
| **Linux Server Admin** | Headless Raspberry Pi OS, Pi-hole DNS, UniFi Controller, Mosquitto MQTT, CUPS |
| **Containerization** | Docker multi-stage builds, Docker Compose with health checks, Ngrok sidecar, auto-restart, log rotation |
| **Software Engineering** | 78K+ lines across 3 repos; MCP protocol server; multi-API orchestration |
| **IoT / Automation** | ESP32 sensor pipeline (BME280 → MQTT → SQLite → Streamlit), VLAN-isolated IoT network |
| **Hypervisor Platform** | Proxmox VE live (Ryzen 9 7900X) — BIOS PPT power cap completed · 192.168.70.10 · Tailscale reachable as pve / 100.71.239.21 · SN770 2TB NVMe vmstore — Wazuh SIEM, AD lab, schoolmate remote lab planned |
| **Out-of-Band Management** | Comet GL-RM1PE KVM active — PoE from 3560CX Gi0/5 · KVM video + keyboard + BIOS access confirmed · WoL power-on path via Magic Packet · ATX board pending for hard power/reset relay |
| **Remote Access** | Tailscale mesh VPN (8 nodes), Ngrok fixed-domain tunnel, zero port forwarding |
| **Security** | Zero port forwarding; VLAN isolation with ACLs; CUPS access control; credential encryption; DNS filtering |

---

## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan:

- **Phase 1** ✅ Documentation & baseline
- **Phase 2** ✅ Network hardening (Cisco, VLANs, ACLs, Pi-hole, UniFi — complete)
- **Phase 3** ✅ Server hardening (Docker, CUPS, print infrastructure — complete)
- **Phase 4** 🔄 Monitoring & observability (closet-monitor live · Netdata/NetAlertX/ntfy pending)
- **Phase 5** ✅ 3560CX Phase B cutover complete (Jun 1, 2026) · Proxmox deployment ✅
- **Phase 6** ❌ Security audit & SIEM (Wazuh)
- **Phase 7** ❌ Infrastructure as Code (Ansible)
- **Phase 8** ❌ Portfolio & documentation (builtwithpurpose.dev)

---

## Related Repositories

| Repository | Lines | Stack | Deployment |
|---|---|---|---|
| [social-media-mcp](https://github.com/design1-software/social-media-mcp) | 19,753 | TypeScript | Docker on Acer |
| [meta_engagement_pipeline](https://github.com/design1-software/meta_engagement_pipeline) | 36,475 | JavaScript | Railway |
| [fb-content-system](https://github.com/design1-software/fb-content-system) | 22,067 | JS/TS/Python | MacBook Pro |
| [closet-monitor](https://github.com/design1-software/closet-monitor) | — | Python/C++ | ESP32 + Pi + Acer |

---

*Last updated: May 30, 2026*