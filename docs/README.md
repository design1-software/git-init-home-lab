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
└──────────────┬───────────────────────────────────┬──────────────────────┘
               │ Webhooks                          │ HTTPS
┌──────────────┴──────────────────┐    ┌───────────┴──────────────┐
│   RAILWAY (Cloud)               │    │   NGROK TUNNEL           │
│   meta_engagement_pipeline      │    │   Public HTTPS → :3000   │
│   36,475 lines · Express+Worker │    │   SSE transport for MCP  │
│   PM2: mlx-poster, feed-engager │◄──►│   Secure, encrypted      │
│   Postgres · Cron automation    │    └───────────┬──────────────┘
│   Greetings · Scoring · Healing │                │
└─────────────────────────────────┘                │
                                                   │
┌──────────────────────────────────────────────────┴──────────────────┐
│   XFINITY GATEWAY  →  PATCH PANEL  →  TP-LINK TL-SG108 (8-port)   │
│   No port forwarding — all ingress via Ngrok tunnel                │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ Ethernet
┌──────────────────────────────────┴──────────────────────────────────┐
│   HOME SERVER — Acer Aspire 3 15 (AMD Ryzen) — 24/7                │
│                                                                     │
│   ┌─────────────────────────┐  ┌─────────────────────────────┐     │
│   │  social-media-mcp       │  │  fb-content-system           │     │
│   │  19,753 lines · TS      │  │  22,067 lines · JS/TS/Py    │     │
│   │  MCP Server on :3000    │  │  182 posts/wk × 3 pages     │     │
│   │  22 lib modules         │  │  Claude copy · Playwright    │     │
│   │  Remotion · Puppeteer   │  │  Remotion reels · Graph API  │     │
│   │  Kie · Suno · ElevenLabs│  │  Engagement tracking/recycle │     │
│   └─────────────────────────┘  └─────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

> 📄 See [docs/architecture.html](docs/architecture.html) for the full interactive diagram.

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

Runs 3 PM2 processes: `mlx-poster`, `feed-engager`, `worker` with cron jobs for:
- Automated greetings (6:30 AM / 9:30 PM)
- Strategic content drafts (5×/day)
- Engagement scoring & content analysis
- Follower tracking & cross-page engagement
- Self-healing recovery from failures

| Module | Purpose |
|---|---|
| `server.js` | Express API: 12 route files (webhooks, viral, inbox, lab, etc.) |
| `worker.js` | Cron engine with greeting, draft, and maintenance automation |
| `lib/publisher.js` | Meta Graph API posting with error recovery |
| `lib/mcpClient.js` | MCP client calling home server via Ngrok |
| `lib/greetingService.js` | Zero-touch morning/night greeting automation |
| `lib/viralContentService.js` | Viral content pipeline with async media gen |
| `lib/contentAnalyzer.js` | LLM-based quality scoring (threshold: 8.0) |
| `lib/selfHealingService.js` | Auto-recovery without manual intervention |
| `lib/cohortManager.js` | Cross-page engagement strategies |
| `models/index.js` | Sequelize ORM: 10+ models → Postgres |

### [`fb-content-system`](https://github.com/design1-software/fb-content-system) — The Content Factory

**22,067 lines · JS/TS/Python · Local**

Produces **182 posts per week per page** across 3 Facebook pages through a 6-phase pipeline:

```
Phase 1          Phase 2           Phase 3              Phase 4         Phase 5          Phase 6
PAGE DISCOVERY → VISUAL SYSTEM →  CONTENT PRODUCTION → POSTING       → REELS          → ENGAGEMENT
Scan page        Build HTML        Claude API copy      Graph API       Remotion video    Track performance
Extract identity templates         Playwright PNG       SQLite ledger   7 reels/week      Recycle top posts
Define pillars   (per pillar)      (175 static/wk)      crash-safe     ElevenLabs TTS    Optimize mix
```

**Pages under management:**

| Page | Niche | Weekly Output |
|---|---|---|
| MEA (My Engagement Assistant) | Social media automation education | 182 posts |
| Runnin From A2B | Running & fitness community | 182 posts |
| After The Uniform (ATU) | Veteran transition content | 182 posts |

Each page has: `page_brand.json` (identity), topic banks, performance data, branded HTML templates, and pillar-specific content strategies.

---

## Hardware Inventory

| Device | Model | Role | Connection |
|---|---|---|---|
| ISP Gateway | Xfinity xFi Gateway | Modem + Router + WiFi | WAN: Coax |
| Network Switch | TP-Link TL-SG108 | 8-port Gigabit distribution | Ethernet ← Gateway |
| Home Server | Acer Aspire 3 15 (AMD Ryzen) | MCP Server + Content System (24/7) | Ethernet via wall jack |
| Display | Dell Monitor | Server management | HDMI ← Acer |
| Smart Home | Somfy Hub | Blind/shade automation | WiFi |
| Wiring Panel | Structured Media Enclosure | Patch panel + coax distribution | Cat5e/6 runs |

---

## Technology Stack

**Languages:** TypeScript, JavaScript, Python, HTML/CSS, SQL

**Frameworks:** Node.js, Express, Remotion, React, Playwright, Puppeteer

**Protocols:** MCP (SSE transport), Meta Graph API, REST, Webhooks, OAuth 2.0

**AI Services:** Anthropic Claude, xAI Grok, OpenAI, ElevenLabs, Kie.ai, Suno

**Data:** PostgreSQL (Railway), SQLite (local ledger), Sequelize ORM, JSON stores

**Infrastructure:** Railway (PaaS), Ngrok (tunnel), PM2 (process management), FFmpeg

---

## Security

- **Zero port forwarding** — no ports open on the Xfinity gateway; all ingress via Ngrok tunnel
- **MCP auth tokens** — Sidecar callbacks secured via `x-mcp-token` / `x-internal-key` verification
- **Credential management** — API keys in `.env` (gitignored), Railway encrypted env store, Sequelize field-level encryption
- **Self-healing** — `selfHealingService.js` provides automatic recovery; email alerts on critical failures
- **Network segmentation** — planned VLAN implementation with managed switch upgrade

---

## Repository Structure

```
home-lab/
├── README.md                    # This file
├── ROADMAP.md                   # Phased improvement plan
├── CHANGELOG.md                 # What changed and when
├── docs/
│   ├── architecture.html        # Interactive architecture diagram
│   ├── network-diagram.md       # Network topology
│   ├── vlan-design.md           # VLAN plan (Phase 2)
│   ├── security-hardening.md    # Security checklist
│   ├── server-setup.md          # Server provisioning guide
│   └── runbooks/
│       ├── ngrok-recovery.md    # Tunnel drop recovery
│       ├── server-restart.md    # Full restart procedure
│       └── backup-restore.md    # Backup & DR
├── configs/
│   ├── switch/                  # Switch configuration docs
│   ├── ngrok/                   # Tunnel config (sanitized)
│   ├── pm2/                     # Process management
│   └── firewall/                # Firewall rules
├── scripts/
│   ├── health-check.sh          # Service health monitoring
│   ├── backup.sh                # Automated backup
│   ├── tunnel-monitor.sh        # Ngrok watchdog
│   └── setup.sh                 # Fresh server setup
├── monitoring/                  # Uptime monitoring configs
└── photos/                      # Hardware documentation photos
```

---

## Skills Demonstrated

| Domain | Implementation |
|---|---|
| **Software Engineering** | 78K+ lines across 3 repos; MCP protocol server; multi-API orchestration |
| **Networking** | Structured wiring; switch configuration; VLAN design; network segmentation |
| **Cloud Architecture** | Hybrid self-hosted + Railway; dual-engine pattern; webhook event processing |
| **DevOps** | PM2 process management; Docker (planned); automated health checks; CI/CD |
| **Security** | Zero port forwarding; token auth; credential encryption; self-healing |
| **API Integration** | Meta Graph API, 3 AI providers, 3 media generation APIs, MCP protocol |
| **Database Design** | PostgreSQL (cloud), SQLite (local), Sequelize ORM, 10+ data models |
| **Server Administration** | 24/7 server management; Ngrok tunnel; process monitoring; backup |

---

## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan covering:
- **Phase 1** ✅ Documentation & baseline
- **Phase 2** 🔄 Network hardening (managed switch, VLANs)
- **Phase 3** Server hardening (Docker, process management)
- **Phase 4** Monitoring & observability (Uptime Kuma, dashboards)
- **Phase 5** Security audit (Nmap, Cloudflare Tunnel evaluation)
- **Phase 6** Infrastructure as Code (Ansible, one-command rebuild)

---

## Related Repositories

| Repository | Lines | Stack | Deployment |
|---|---|---|---|
| [social-media-mcp](https://github.com/design1-software/social-media-mcp) | 19,753 | TypeScript | Self-hosted (Home Server) |
| [meta_engagement_pipeline](https://github.com/design1-software/meta_engagement_pipeline) | 36,475 | JavaScript | Railway (Cloud) |
| [fb-content-system](https://github.com/design1-software/fb-content-system) | 22,067 | JS/TS/Python | Self-hosted (Home Server) |

---

*Last updated: April 2026*
