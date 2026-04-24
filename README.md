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
│  ElevenLabs TTS  ·  Kie.ai Images    ·  Suno Music ·  Perplexity     │
└──────────────┬───────────────────────────────────────┬──────────────────┘
               │ Webhooks                              │ HTTPS
┌──────────────┴──────────────────┐    ┌───────────────┴──────────────┐
│   RAILWAY (Cloud)               │    │   NGROK TUNNEL               │
│   meta_engagement_pipeline      │    │   Public HTTPS → :3000       │
│   36,475 lines · Express+Worker │    │   Fixed domain: mea.ngrok.app│
│   PM2: mlx-poster, feed-engager │◄──►│   Docker sidecar container   │
│   Postgres · Cron automation    │    └───────────────┬──────────────┘
│   Greetings · Scoring · Healing │                    │
└─────────────────────────────────┘                    │
                                                       │
┌──────────────────────────────────────────────────────┴──────────────────┐
│   NETWORK LAYER — VLAN-Segmented Lab Topology                           │
│                                                                         │
│   Xfinity XB8 (Bridge Mode — modem only)                               │
│     └─ Cisco C1111-4PWB WAN (DHCP client, public IP from Comcast)      │
│            │                                                            │
│   Cisco C1111-4PWB (JLM-LAB-R1)                                        │
│   IOS XE · 7 VLANs · Inter-VLAN routing · NAT · 4 ACLs · SSH          │
│            │                                                            │
│     ┌──────┴───────────────────────────────────────────────┐            │
│     │                                                       │            │
│     │  GE0/1/0: Acer Server (VLAN 10, 192.168.10.17)       │            │
│     │  GE0/1/1: TRUNK → GS308EP (VLANs 1,10,20,30,31,40,  │            │
│     │                             50,99)                    │            │
│     │  GE0/1/2: TRUNK → GS316EP (VLANs 1,10,20,30,31,40,  │            │
│     │                             50,99) via port 15        │            │
│     │                                                       │            │
│     │  GS308EP (8-port PoE+, Advanced 802.1Q, FW V2.0.0.5) │            │
│     │    Port 3: Pi 4B (VLAN 10, PoE, 192.168.10.16)       │            │
│     │    Port 4: UniFi U6+ AP #1 (trunk: 20,30,31,40,50)   │            │
│     │    Port 5: UniFi U6+ AP #2 (trunk: 20,30,31,40,50)   │            │
│     │                                                       │            │
│     │  GS316EP (16-port PoE+, household wired devices)      │            │
│     │    Ports 2-4: Apple TVs (VLAN 20)                     │            │
│     │    Port 15: Trunk to Cisco GE0/1/2                    │            │
│     │    Port 16: SFP (fiber only, not RJ-45)               │            │
│     └───────────────────────────────────────────────────────┘            │
│                                                                         │
│   WiFi SSIDs (5 active):                                                │
│     Gorgeous      → VLAN 20 (TRUSTED)                                   │
│     Gorgeous-IoT  → VLAN 30 (IOT)                                       │
│     Gorgeous-Auto → VLAN 31 (IOT-AUTO)                                  │
│     Gorgeous-Home → VLAN 40 (HOUSEHOLD)                                 │
│     JM&G-GUEST    → VLAN 50 (GUEST, client isolation)                   │
│                                                                         │
│   DNS: Pi-hole (192.168.10.16) serving all VLANs                        │
│   UPS: CyberPower CP1500PFCLCD protecting all critical infra            │
│   Remote: Tailscale mesh VPN (MacBook + Acer)                           │
│   No port forwarding — all ingress via Ngrok tunnel                     │
└─────────────────────────────────────────────────────────────────────────┘
                                   │ Ethernet
┌──────────────────────────────────┴──────────────────────────────────────┐
│   HOME SERVER — Acer Aspire 3 15 (AMD Ryzen) — 24/7                    │
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
│   MACBOOK PRO — Always-on                                               │
│   fb-content-system  (22,067 lines · 182 posts/wk × 3 pages)          │
│   └─ Weekly bulk content creation + real-time comment response          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Current Operational State

| System | Status | Details |
|---|---|---|
| Cisco C1111-4PWB | ✅ Online | 7 VLANs, inter-VLAN routing, 4 ACLs, NAT, SSH |
| GS308EP (Lab Switch) | ✅ Trunking | Advanced 802.1Q, 8 VLANs, trunk to Cisco verified |
| GS316EP (Household) | ✅ Trunked to Cisco | Advanced 802.1Q, trunk port 15 → Cisco GE0/1/2 |
| Pi 4B | ✅ Multi-service | Pi-hole, UniFi Controller, Mosquitto MQTT, CUPS print server |
| UniFi Controller | ✅ Active | v10.1.89 on Pi, 2 APs adopted |
| UniFi U6+ APs (×2) | ✅ Broadcasting | 5 SSIDs on 5 VLANs, desk-mounted |
| VLAN segmentation | ✅ Implemented | 7 VLANs active, 4 ACLs enforcing isolation |
| CyberPower UPS | ✅ Protecting infra | Auto-shutdown via PowerPanel Personal (USB-B to Acer) |
| Acer Server | ✅ Dockerized | social-media-mcp + Ngrok in Docker Compose, auto-restart |
| CUPS Print Server | ✅ Serving | Pi → USB → HP ENVY 7200e, print from VLAN 10/20/40 |
| HP Instant Ink | ✅ Active | Printer WiFi on VLAN 30 for HP cloud monitoring |
| Xfinity bridge mode | ✅ Active | Cisco sole router, public IP via DHCP from Comcast |
| Tailscale | ✅ Connected | MacBook + Acer on mesh VPN, MagicDNS disabled |
| closet-monitor | ✅ Production | ESP32 → MQTT → Pi → SQLite → Streamlit dashboard |
| IoT device migration | ✅ Mostly done | Ring, Alexa, Ecobee, Somfy, Samsung TV migrated. Kasa plugs pending (app issue) |
---

## The Three Repositories

### [`social-media-mcp`](https://github.com/design1-software/social-media-mcp) — The MCP Server

**19,753 lines · TypeScript · Self-hosted 24/7**

The brain of the platform. An MCP (Model Context Protocol) server exposing AI-powered content creation tools over SSE. Runs on the home server, tunneled to the internet via Ngrok.

| Module | Purpose |
|---|---|
| `src/lib/kie.ts` | Kie.ai image generation |
| `src/lib/elevenlabs.ts` | Text-to-speech voiceover |
| `src/lib/suno.ts` | AI music generation for reels |
| `src/lib/remotion.ts` | Programmatic video rendering (20+ templates) |
| `src/lib/facebook.ts` | Puppeteer-based Facebook browser automation |
| `src/lib/ffmpeg.ts` | Media stitching, quote image rendering |
| `src/lib/grok.ts` | xAI Grok for content direction & image analysis |
| `src/lib/perplexity.ts` | Web research & trend identification |
| `src/lib/storyArc.ts` | Multi-part story series generation |
| `src/lib/commentBait.ts` | Engagement-optimized post generation |
| `src/lib/identity.ts` | Brand identity profile management |
| `src/lib/sessions.ts` | MCP session state persistence |

### [`meta_engagement_pipeline`](https://github.com/design1-software/meta_engagement_pipeline) — The Cloud Orchestrator

**36,475 lines · JavaScript · Railway**

Engagement engine with a dual-engine architecture:
- **Graph API Engine**: Official page posts, comment replies, webhook processing
- **Sidecar Engine**: Browser-automated profile actions via MCP bridge to home server

### [`fb-content-system`](https://github.com/design1-software/fb-content-system) — The Content Factory

**22,067 lines · JS/TS/Python · Local**

Produces **182 posts per week per page** across 3 Facebook pages.

---

## Hardware Inventory

### Network Infrastructure

| Device | Model | Role | Connection |
|---|---|---|---|
| ISP Gateway | Xfinity XB8 | Modem only (bridge mode) | WAN: Coax |
| Lab Edge Router | Cisco C1111-4PWB ISR | Enterprise router: 6 VLANs, ACLs, DHCP, NAT, SSH | WAN: Ethernet ← XB8 |
| Household Switch | Netgear GS316EP | 16-port PoE+ Managed (180W) + 1 SFP | Ethernet ← XB8 |
| Lab Switch | Netgear GS308EP | 8-port PoE+ Managed (62W), Advanced 802.1Q, FW V2.0.0.5 | Trunk ← Cisco GE0/1/1 |
| UPS | CyberPower CP1500PFCLCD | Battery backup for all infrastructure | Power |
| WiFi (lab) | 2× Ubiquiti UniFi U6+ | Enterprise APs, 4 VLAN-tagged SSIDs | PoE ← GS308EP |

### Compute

| Device | Model | Role | Connection |
|---|---|---|---|
| Home Server | Acer Aspire 3 15 (AMD Ryzen) | Docker: MCP Server + Ngrok sidecar (24/7) | Cisco GE0/1/0, VLAN 10 |
| Network Services | Raspberry Pi 4B + PoE HAT | Pi-hole, UniFi Controller, Mosquitto MQTT, CUPS | GS308EP Port 3 (PoE), VLAN 10 |
| Printer | HP ENVY Inspire 7200e | USB to Pi (CUPS), WiFi on VLAN 30 (Instant Ink) | USB + WiFi (Gorgeous-IoT) |
| Laptop | MacBook Pro | Development + fb-content-system (always-on) | WiFi (Gorgeous, VLAN 20) |

### IoT / Smart Home

| Device | Model | Current SSID | Status |
|---|---|---|---|
| Ring cameras + doorbell | Ring LLC | Gorgeous-IoT | ✅ Migrated |
| Kasa Smart Plugs ×4 | EP10 | Gorgeous | Pending (app issue) |
| Ecobee thermostat | Ecobee | Gorgeous-IoT | ✅ Migrated |
| Amazon Alexa ×3 | Amazon | Gorgeous-IoT | ✅ Migrated |
| Somfy Hub | Somfy | Gorgeous-IoT | ✅ Migrated |
| ESP32 closet sensor | ESP32 + BME280 | Gorgeous-Auto | ✅ On VLAN 31, publishing MQTT |
| HP ENVY Inspire 7200e | HP Inc. | Gorgeous-IoT | ✅ WiFi for Instant Ink only; prints via USB/CUPS |

**Total devices on network: ~25+**

---

## VLAN Scheme

| VLAN | Name | Subnet | SSID | ACL |
|---|---|---|---|---|
| 10 | SERVER | 192.168.10.0/24 | (wired only) | No restrictions |
| 20 | TRUSTED | 192.168.20.0/24 | Gorgeous | No restrictions |
| 30 | IOT | 192.168.30.0/24 | Gorgeous-IoT | Internet only + DNS to Pi-hole |
| 31 | IOT-AUTO | 192.168.31.0/24 | Gorgeous-Auto | MQTT + DNS to Pi only |
| 40 | HOUSEHOLD | 192.168.40.0/24 | Gorgeous-Home | Internet only + DNS to Pi-hole |
| 50 | GUEST | 192.168.50.0/24 | JM&G-GUEST | Internet only + DNS to Pi-hole, client isolation |
| 99 | MGMT | 192.168.99.0/24 | (none) | No restrictions |

> 📄 See [docs/vlan-design.md](docs/vlan-design.md) for the full VLAN design with ACL rules, switch config, and lessons learned.

---

## Security

- **Zero port forwarding** — all ingress via Ngrok tunnel (fixed domain, Docker sidecar)
- **VLAN segmentation** — 7 VLANs with inter-VLAN ACLs enforcing isolation
- **ACLs** — IOT: internet-only; IOT-AUTO: MQTT-only to Pi; HOUSEHOLD: internet-only; GUEST: internet-only with client isolation
- **Containerized services** — Docker Compose with health checks, auto-restart, log rotation
- **CUPS access control** — print submission from VLAN 10/20/40; admin restricted to VLAN 20
- **Printer hardening** — Wi-Fi Direct disabled, HP marketing data disabled, admin password changed
- **Remote access** — Tailscale mesh VPN for cross-VLAN and remote management (MagicDNS disabled)
- **UPS auto-shutdown** — CyberPower CP1500PFCLCD with PowerPanel Personal, graceful shutdown at 20% battery
- **TCP MSS clamping** — `ip tcp adjust-mss 1452` on WAN interface for bridge mode compatibility
- **Cisco IOS hardening** — enable secret, console password + timeout, service password-encryption, SSHv2, local user auth
- **DNS filtering** — Pi-hole blocking 87K+ domains, serving all VLANs
- **MCP auth tokens** — Sidecar callbacks secured via `x-mcp-token` / `x-internal-key`
- **Credential management** — API keys in `.env` (gitignored), Railway encrypted env store

---

## Skills Demonstrated

| Domain | Implementation |
|---|---|
| **Enterprise Networking** | Cisco IOS XE: 7 VLANs, SVIs, inter-VLAN routing, extended ACLs, NAT/PAT, DHCP (8 pools), 802.1Q trunking, SSH |
| **Network Infrastructure** | Dual managed switch topology, Netgear Advanced 802.1Q configuration, enterprise PoE+ AP deployment, VLAN-tagged WiFi (5 SSIDs) |
| **Linux Server Admin** | Headless Raspberry Pi OS, SSH, Pi-hole DNS, UniFi Controller, Mosquitto MQTT, CUPS print server |
| **Containerization** | Docker multi-stage builds, Docker Compose with health checks, Ngrok sidecar, auto-restart, log rotation |
| **Software Engineering** | 78K+ lines across 3 repos; MCP protocol server; multi-API orchestration |
| **IoT / Automation** | ESP32 sensor pipeline (BME280 → MQTT → SQLite → Streamlit), VLAN-isolated IoT network |
| **Print Infrastructure** | CUPS print server, USB-attached printer with dual-path architecture (USB for printing, WiFi for vendor cloud) |
| **Cloud Architecture** | Hybrid self-hosted + Railway; dual-engine pattern; webhook event processing |
| **Security** | Zero port forwarding; VLAN isolation with ACLs; CUPS access control; credential encryption; DNS filtering |

---

## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan covering:
- **Phase 1** ✅ Documentation & baseline
- **Phase 2** ✅ Network hardening (Cisco, VLANs, ACLs, Pi-hole, UniFi APs — complete)
- **Phase 3** ✅ Server hardening (Docker, CUPS, print infrastructure — mostly complete)
- **Phase 4** 🔄 Monitoring & observability (closet-monitor in production, Netdata/NetAlertX next)
- **Phase 5** Security audit & SIEM (Wazuh)
- **Phase 6** Infrastructure as Code (Ansible)
- **Phase 7** Portfolio & documentation

---

## Related Repositories

| Repository | Lines | Stack | Deployment |
|---|---|---|---|
| [social-media-mcp](https://github.com/design1-software/social-media-mcp) | 19,753 | TypeScript | Docker on Acer (Home Server) |
| [meta_engagement_pipeline](https://github.com/design1-software/meta_engagement_pipeline) | 36,475 | JavaScript | Railway (Cloud) |
| [fb-content-system](https://github.com/design1-software/fb-content-system) | 22,067 | JS/TS/Python | MacBook Pro (always-on) |
| [closet-monitor](https://github.com/design1-software/closet-monitor) | — | Python/C++ | ESP32 + Pi + Acer |

---



*Last updated: April 24, 2026*
