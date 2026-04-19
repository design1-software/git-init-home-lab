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
│   Xfinity XB8 (10.0.0.0/24)                                            │
│     ├─ Household WiFi (renamed, being phased out)                       │
│     ├─ GS316EP (16-port PoE+ · household wired devices)                │
│     └─ Cisco C1111-4PWB WAN (DHCP client)                               │
│            │                                                            │
│   Cisco C1111-4PWB (JLM-LAB-R1)                                        │
│   IOS XE · 6 VLANs · Inter-VLAN routing · NAT · ACLs · SSH             │
│            │                                                            │
│     ┌──────┴───────────────────────────────────────────────┐            │
│     │                                                       │            │
│     │  GE0/1/0: Acer Server (VLAN 10, 192.168.10.17)       │            │
│     │  GE0/1/1: TRUNK → GS308EP (VLANs 1,10,20,30,31,40,99)│           │
│     │  GE0/1/2: Pi 4B (VLAN 10, 192.168.10.16)             │            │
│     │                                                       │            │
│     │  GS308EP (8-port PoE+, Advanced 802.1Q, FW V2.0.0.5) │            │
│     │    Port 3: Pi 4B access (VLAN 10) — pending move      │            │
│     │    Port 4: UniFi U6+ AP #1 (trunk: 20,30,31,40)      │            │
│     │    Port 5: UniFi U6+ AP #2 (trunk: 20,30,31,40)      │            │
│     └───────────────────────────────────────────────────────┘            │
│                                                                         │
│   WiFi SSIDs (4 active):                                                │
│     Gorgeous      → VLAN 20 (TRUSTED)                                   │
│     Gorgeous-IoT  → VLAN 30 (IOT)                                       │
│     Gorgeous-Auto → VLAN 31 (IOT-AUTO)                                  │
│     Gorgeous-Home → VLAN 40 (HOUSEHOLD)                                 │
│                                                                         │
│   DNS: Pi-hole (192.168.10.16) serving all VLANs                        │
│   UPS: CyberPower CP1500PFCLCD protecting all critical infra            │
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
| Cisco C1111-4PWB | ✅ Online | 6 VLANs, inter-VLAN routing, 3 ACLs, NAT, SSH |
| GS308EP (Lab Switch) | ✅ Trunking | Advanced 802.1Q, 7 VLANs, trunk to Cisco verified |
| Pi 4B + Pi-hole | ✅ Serving DNS | 192.168.10.16, DNS for all VLANs |
| UniFi Controller | ✅ Active | v10.1.89 on Pi, 2 APs adopted |
| UniFi U6+ APs (×2) | ✅ Broadcasting | 4 SSIDs on 4 VLANs, desk-mounted |
| VLAN segmentation | ✅ Implemented | 6 VLANs active, ACLs enforcing isolation |
| CyberPower UPS | ✅ Protecting infra | Auto-shutdown pending USB cable |
| Acer Server | ✅ 24/7 production | VLAN 10 (SERVER) |
| GS316EP (Household) | ✅ In service | Still on Xfinity side; migration planned |
| Xfinity bridge mode | 🔲 Planned | After household device migration |
| IoT device migration | 🔄 Pending | Ring, Alexa, Ecobee need to move to Gorgeous-IoT |

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
| ISP Gateway | Xfinity XB8 | Modem + Household Router (10.0.0.0/24) | WAN: Coax |
| Lab Edge Router | Cisco C1111-4PWB ISR | Enterprise router: 6 VLANs, ACLs, DHCP, NAT, SSH | WAN: Ethernet ← XB8 |
| Household Switch | Netgear GS316EP | 16-port PoE+ Managed (180W) + 1 SFP | Ethernet ← XB8 |
| Lab Switch | Netgear GS308EP | 8-port PoE+ Managed (62W), Advanced 802.1Q, FW V2.0.0.5 | Trunk ← Cisco GE0/1/1 |
| UPS | CyberPower CP1500PFCLCD | Battery backup for all infrastructure | Power |
| WiFi (lab) | 2× Ubiquiti UniFi U6+ | Enterprise APs, 4 VLAN-tagged SSIDs | PoE ← GS308EP |

### Compute

| Device | Model | Role | Connection |
|---|---|---|---|
| Home Server | Acer Aspire 3 15 (AMD Ryzen) | MCP Server + Content System (24/7) | Cisco GE0/1/0, VLAN 10 |
| Network Services | Raspberry Pi 4B | Pi-hole, UniFi Controller | Cisco GE0/1/2, VLAN 10 |
| Laptop | MacBook Pro | Development / personal | WiFi (Gorgeous, VLAN 20) |

### IoT / Smart Home

| Device | Model | Current SSID | Target SSID |
|---|---|---|---|
| Ring cameras + doorbell | Ring LLC | Gorgeous | Gorgeous-IoT |
| Kasa Smart Plugs ×4 | EP10 | Gorgeous | Gorgeous-IoT |
| Ecobee thermostat | Ecobee | Gorgeous | Gorgeous-IoT |
| Amazon Alexa ×3 | Amazon | Gorgeous | Gorgeous-IoT |
| Somfy Hub | Somfy | Gorgeous | Gorgeous-IoT |
| ESP32 closet sensor | ESP32 + BME280 | Gorgeous | Gorgeous-Auto (pending) |

**Total devices on network: ~25+**

---

## VLAN Scheme

| VLAN | Name | Subnet | SSID | ACL |
|---|---|---|---|---|
| 10 | SERVER | 192.168.10.0/24 | (wired only) | No restrictions |
| 20 | TRUSTED | 192.168.20.0/24 | Gorgeous | No restrictions |
| 30 | IOT | 192.168.30.0/24 | Gorgeous-IoT | Internet only + DNS to Pi-hole |
| 31 | IOT-AUTO | 192.168.31.0/24 | Gorgeous-Auto | MQTT + DNS to Pi only |
| 40 | HOUSEHOLD | 192.168.40.0/24 | Gorgeous-Home | Internet + AirPlay to Apple TVs |
| 99 | MGMT | 192.168.99.0/24 | (none) | No restrictions |

> 📄 See [docs/vlan-design.md](docs/vlan-design.md) for the full VLAN design with ACL rules, switch config, and lessons learned.

---

## Security

- **Zero port forwarding** — all ingress via Ngrok tunnel
- **VLAN segmentation** — 6 VLANs with inter-VLAN ACLs enforcing isolation
- **ACLs** — IOT: internet-only; IOT-AUTO: MQTT-only to Pi; HOUSEHOLD: internet + AirPlay exceptions
- **Cisco IOS hardening** — enable secret, console password + timeout, service password-encryption, SSHv2, local user auth
- **DNS filtering** — Pi-hole blocking 87K+ domains, serving all VLANs
- **MCP auth tokens** — Sidecar callbacks secured via `x-mcp-token` / `x-internal-key`
- **Credential management** — API keys in `.env` (gitignored), Railway encrypted env store
- **UPS protection** — CyberPower CP1500PFCLCD battery backup

---

## Skills Demonstrated

| Domain | Implementation |
|---|---|
| **Enterprise Networking** | Cisco IOS XE: 6 VLANs, SVIs, inter-VLAN routing, extended ACLs, NAT/PAT, DHCP (7 pools + static reservation), 802.1Q trunking, SSH |
| **Network Infrastructure** | Dual managed switch topology, Netgear Advanced 802.1Q configuration, enterprise PoE+ AP deployment, VLAN-tagged WiFi (4 SSIDs) |
| **Linux Server Admin** | Headless Raspberry Pi OS, SSH, Pi-hole DNS, UniFi Controller |
| **Software Engineering** | 78K+ lines across 3 repos; MCP protocol server; multi-API orchestration |
| **IoT / Automation** | ESP32 sensor pipeline (BME280 → MQTT → SQLite → Streamlit), VLAN-isolated IoT network |
| **Cloud Architecture** | Hybrid self-hosted + Railway; dual-engine pattern; webhook event processing |
| **Security** | Zero port forwarding; VLAN isolation with ACLs; credential encryption; DNS filtering |

---

## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan covering:
- **Phase 1** ✅ Documentation & baseline
- **Phase 2** ✅ Network hardening (Cisco, VLANs, ACLs, Pi-hole, UniFi APs — complete)
- **Phase 3** Server hardening (Docker, process management)
- **Phase 4** Monitoring & observability
- **Phase 5** Security audit
- **Phase 6** Infrastructure as Code

---

## Related Repositories

| Repository | Lines | Stack | Deployment |
|---|---|---|---|
| [social-media-mcp](https://github.com/design1-software/social-media-mcp) | 19,753 | TypeScript | Self-hosted (Home Server) |
| [meta_engagement_pipeline](https://github.com/design1-software/meta_engagement_pipeline) | 36,475 | JavaScript | Railway (Cloud) |
| [fb-content-system](https://github.com/design1-software/fb-content-system) | 22,067 | JS/TS/Python | Self-hosted (Home Server) |

---

Related Infrastructure
This sensor is one node in a broader home lab network documented at git-init-home-lab.
The ESP32 currently connects via the Gorgeous SSID (VLAN 20, TRUSTED) and publishes MQTT to a Mosquitto broker on the MacBook Pro. When Mosquitto migrates to the Raspberry Pi 4B (192.168.10.16, VLAN 10, SERVER), the ESP32 will move to the Gorgeous-Auto SSID (VLAN 31, IOT-AUTO) — a dedicated automation VLAN that permits only MQTT and DNS traffic to the Pi via Cisco ACLs.

*Last updated: April 19, 2026*
