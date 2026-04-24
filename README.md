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
│   36,475 lines · Express+Worker │    │   SSE transport for MCP      │
│   PM2: mlx-poster, feed-engager │◄──►│   Secure, encrypted          │
│   Postgres · Cron automation    │    └───────────────┬──────────────┘
│   Greetings · Scoring · Healing │                    │
└─────────────────────────────────┘                    │
                                                       │
┌──────────────────────────────────────────────────────┴──────────────────┐
│   NETWORK LAYER — VLAN-Segmented Lab Topology                           │
│                                                                         │
│   ISP Gateway (bridge mode)                                             │
│     └─ Cisco branch router (WAN: DHCP from ISP)                         │
│            │                                                            │
│   Cisco branch router                                                   │
│   IOS XE · 7 VLANs · Inter-VLAN routing · NAT · ACLs · SSH             │
│            │                                                            │
│     ┌──────┴───────────────────────────────────────────────┐            │
│     │                                                       │            │
│     │  Access   → Home Server          (SERVER VLAN)       │            │
│     │  Trunk    → 8-port managed PoE+ switch (all VLANs)   │            │
│     │  Trunk    → 16-port managed PoE+ switch              │            │
│     │                                                       │            │
│     │  Lab Switch (managed PoE+, 802.1Q)                    │            │
│     │    ├─ Pi (SERVER VLAN, PoE)                           │            │
│     │    │    ├─ Pi-hole DNS (:53)                          │            │
│     │    │    ├─ UniFi Controller (:8443)                   │            │
│     │    │    ├─ Mosquitto MQTT (:1883)                     │            │
│     │    │    └─ CUPS Print Server (:631)                   │            │
│     │    │         └─ USB → HP All-in-One (print path)      │            │
│     │    └─ 2× UniFi APs (trunk: TRUSTED/IOT/AUTO/HOME)     │            │
│     └───────────────────────────────────────────────────────┘            │
│                                                                         │
│   WiFi SSIDs (5 active):                                                │
│     Personal     → TRUSTED   VLAN                                       │
│     Smart-Home   → IOT       VLAN                                       │
│     Automation   → IOT-AUTO  VLAN                                       │
│     Family       → HOUSEHOLD VLAN                                       │
│     Guest        → GUEST     VLAN (client isolation)                    │
│                                                                         │
│   DNS: Pi-hole serving all VLANs (~87K-domain blocklist)                │
│   UPS: CyberPower battery backup protecting critical infra             │
│   No port forwarding — all ingress via Ngrok tunnel                     │
└─────────────────────────────────────────────────────────────────────────┘
                                   │ Ethernet
┌──────────────────────────────────┴──────────────────────────────────────┐
│   HOME SERVER — Acer Aspire 3 15 (AMD Ryzen) — 24/7                    │
│                                                                         │
│   ┌─────────────────────────┐  ┌─────────────────────────────┐         │
│   │  social-media-mcp       │  │  fb-content-system           │         │
│   │  19,753 lines · TS      │  │  22,067 lines · JS/TS/Py    │         │
│   │  MCP Server on :3000    │  │  182 posts/wk × 3 pages     │         │
│   │  22 lib modules         │  │  Claude copy · Playwright    │         │
│   │  Remotion · Puppeteer   │  │  Remotion reels · Graph API  │         │
│   │  Kie · Suno · ElevenLabs│  │  Engagement tracking/recycle │         │
│   └─────────────────────────┘  └─────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Current Operational State

| System | Status | Details |
|---|---|---|
| Cisco branch router | ✅ Online | 7 VLANs, inter-VLAN routing, 4 ACLs, NAT, SSH |
| Lab Switch | ✅ Trunking | Managed PoE+, 802.1Q, 7 VLANs, trunk to Cisco verified |
| Pi + Pi-hole | ✅ Serving DNS | Pi-hole resolver for all VLANs |
| UniFi Controller | ✅ Active | Running on Pi, 2 APs adopted |
| UniFi U6+ APs (×2) | ✅ Broadcasting | 5 SSIDs on 5 VLANs |
| VLAN segmentation | ✅ Implemented | 7 VLANs active, ACLs enforcing isolation |
| CyberPower UPS | ✅ Protecting infra | Auto-shutdown via PowerPanel Personal |
| Home Server | ✅ 24/7 production | SERVER VLAN |
| Household Switch | ✅ Trunked to Cisco | Managed 802.1Q, trunk uplink |
| ISP bridge mode | ✅ Active | Cisco sole router with public ISP-assigned IP |
| IoT device migration | ✅ Mostly done | Cameras, voice assistants, thermostat, blinds, smart TV migrated. A couple of plugs pending (app issue) |
| Print server | ✅ Operational | CUPS on Pi, USB-attached HP All-in-One, IPP Everywhere |
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

| Device | Role | Connection |
|---|---|---|
| ISP Gateway | Modem + bridge mode | WAN: ISP circuit |
| Lab Edge Router | Cisco branch router: 7 VLANs, ACLs, DHCP, NAT, SSH | WAN: Ethernet ← ISP gateway |
| Household Switch | 16-port managed PoE+ (SFP uplink) | Trunked ← Cisco |
| Lab Switch | 8-port managed PoE+ (802.1Q) | Trunked ← Cisco |
| UPS | Battery backup for all infrastructure | Power |
| WiFi (lab) | 2× Enterprise APs, 5 VLAN-tagged SSIDs | PoE ← Lab Switch |

### Compute

| Device | Role | Connection |
|---|---|---|
| Home Server | MCP Server + Content System (24/7) | Cisco access port, SERVER VLAN |
| Network Services (Pi) | Pi-hole, UniFi Controller, Mosquitto MQTT, CUPS | Lab Switch (PoE), SERVER VLAN |
| Laptop | Development / personal | WiFi on TRUSTED VLAN |

### Peripherals

| Device | Role | Connection |
|---|---|---|
| HP All-in-One | Print/scan for the lab | USB → Pi (CUPS); WiFi on IOT VLAN for vendor cloud features |

### IoT / Smart Home

| Device Class | Network |
|---|---|
| Cameras + doorbell | IOT VLAN |
| Smart plugs | IOT VLAN |
| Thermostat | IOT VLAN |
| Voice assistants | IOT VLAN |
| Smart blinds hub | IOT VLAN |
| ESP32 sensors | IOT-AUTO VLAN (MQTT-only policy) |

**Total devices on network: ~25+**

---

## VLAN Scheme

> Subnets shown below are illustrative examples — the production lab uses a different RFC1918 range, and the VLAN IDs and SSID names have been abstracted for public documentation.

| VLAN | Name | Example Subnet | SSID Role | ACL Policy |
|---|---|---|---|---|
| 10 | SERVER | 10.0.10.0/24 | (wired only) | No restrictions |
| 20 | TRUSTED | 10.0.20.0/24 | Personal | No restrictions |
| 30 | IOT | 10.0.30.0/24 | Smart-Home | Internet only + DNS to Pi-hole |
| 31 | IOT-AUTO | 10.0.31.0/24 | Automation | MQTT + DNS to Pi only |
| 40 | HOUSEHOLD | 10.0.40.0/24 | Family | Internet only + DNS to Pi-hole |
| 50 | GUEST | 10.0.50.0/24 | Guest | Internet only + DNS to Pi-hole, client isolation |
| 99 | MGMT | 10.0.99.0/24 | (none) | No restrictions |

> 📄 See [docs/vlan-design.md](docs/vlan-design.md) for the full VLAN design with ACL rules, switch config, and lessons learned.

---

## Security

- **Zero port forwarding** — all ingress via Ngrok tunnel
- **VLAN segmentation** — 7 VLANs with inter-VLAN ACLs enforcing isolation
- **ACLs** — IOT: internet-only; IOT-AUTO: MQTT-only to Pi; HOUSEHOLD: internet-only; GUEST: internet-only with client isolation
- **Remote access** — Tailscale mesh VPN for cross-VLAN and remote management
- **UPS auto-shutdown** — battery-backed graceful shutdown at low-battery threshold
- **TCP MSS clamping** — `ip tcp adjust-mss` on WAN interface for bridge-mode compatibility
- **Cisco IOS hardening** — enable secret, console password + timeout, service password-encryption, SSHv2, local user auth
- **DNS filtering** — Pi-hole blocking 87K+ domains, serving all VLANs
- **Print server hardening** — CUPS admin restricted to TRUSTED VLAN; print submission restricted to SERVER/TRUSTED/HOUSEHOLD; printer Wi-Fi Direct and vendor telemetry disabled
- **MCP auth tokens** — Sidecar callbacks secured via `x-mcp-token` / `x-internal-key`
- **Credential management** — API keys in `.env` (gitignored), Railway encrypted env store

---

## Skills Demonstrated

| Domain | Implementation |
|---|---|
| **Enterprise Networking** | Cisco IOS XE: 7 VLANs, SVIs, inter-VLAN routing, 4 extended ACLs, NAT/PAT, DHCP, 802.1Q trunking, SSH |
| **Network Infrastructure** | Dual managed-switch topology, Advanced 802.1Q configuration, enterprise PoE+ AP deployment, VLAN-tagged WiFi (5 SSIDs) |
| **Linux Server Admin** | Headless Raspberry Pi OS, SSH, Pi-hole DNS, UniFi Controller, CUPS print server (IPP Everywhere) |
| **Software Engineering** | 78K+ lines across 3 repos; MCP protocol server; multi-API orchestration |
| **IoT / Automation** | ESP32 sensor pipeline (BME280 → MQTT → SQLite → Streamlit), VLAN-isolated IoT network |
| **Cloud Architecture** | Hybrid self-hosted + Railway; dual-engine pattern; webhook event processing |
| **Security** | Zero port forwarding; VLAN isolation with ACLs; credential encryption; DNS filtering |

---

## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan covering:
- **Phase 1** ✅ Documentation & baseline
- **Phase 2** ✅ Network hardening (Cisco, VLANs, ACLs, Pi-hole, UniFi APs)
- **Phase 3** Server hardening (Docker, auth, runbooks) — CUPS print server complete
- **Phase 4** Monitoring & observability
- **Phase 5** Security audit & SIEM
- **Phase 6** Infrastructure as Code
- **Phase 7** Portfolio & documentation

---

## Related Repositories

| Repository | Lines | Stack | Deployment |
|---|---|---|---|
| [social-media-mcp](https://github.com/design1-software/social-media-mcp) | 19,753 | TypeScript | Self-hosted (Home Server) |
| [meta_engagement_pipeline](https://github.com/design1-software/meta_engagement_pipeline) | 36,475 | JavaScript | Railway (Cloud) |
| [fb-content-system](https://github.com/design1-software/fb-content-system) | 22,067 | JS/TS/Python | Self-hosted (Home Server) |
| closet-monitor | — | Python/C++ | Self-hosted (ESP32 + Pi) |

---



*Last updated: April 24, 2026*
