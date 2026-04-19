# Enterprise Scale Design

> How this platform would evolve from a single-server home lab to a production enterprise deployment — and what that tells you about the engineering decisions behind it.

---

## Current Architecture Summary

```
┌─────────────────────────────────────────────┐
│  Home Server (Acer Aspire 3)                │
│  ├── social-media-mcp    (MCP Server)       │
│  ├── fb-content-system   (Content Factory)  │
│  └── Ngrok Agent         (Tunnel)           │
└──────────────────┬──────────────────────────┘
                   │ Ethernet (VLAN 10, 192.168.10.17)
┌──────────────────┴──────────────────────────┐
│  Cisco C1111-4PWB (Lab Edge Router)         │
│  ├── IOS XE · 6 VLANs · ACLs · NAT · SSH   │
│  ├── WAN: DHCP from XB8 (10.0.0.x)         │
│  └── Inter-VLAN routing for all subnets     │
└──────────────────┬──────────────────────────┘
                   │ 802.1Q Trunk (VLANs 1,10,20,30,31,40,99)
┌──────────────────┴──────────────────────────┐
│  Netgear GS308EP (Lab Switch, 62W PoE+)    │
│  ├── Advanced 802.1Q, FW V2.0.0.5          │
│  ├── 2× UniFi U6+ APs (4 VLAN-tagged SSIDs)│
│  └── Expansion ports available              │
│                                             │
│  Raspberry Pi 4B (192.168.10.16, VLAN 10)   │
│  ├── Pi-hole (DNS filtering, 87K domains)   │
│  └── UniFi Network Application 10.1.89     │
│                                             │
│  UPS: CyberPower CP1500PFCLCD              │
│  VLANs: SERVER(10) / TRUSTED(20) / IOT(30) │
│          IOT-AUTO(31) / HOUSEHOLD(40) / MGMT(99) │
└──────────────────┬──────────────────────────┘
                   │ Ngrok Tunnel
┌──────────────────┴──────────────────────────┐
│  Railway                                     │
│  └── meta_engagement_pipeline (Orchestrator) │
│      ├── server.js  (API + Webhooks)         │
│      ├── worker.js  (Cron + Automation)      │
│      └── Postgres   (Primary Database)       │
└──────────────────────────────────────────────┘
```

**Scale:** 78K lines, 8 external APIs, 3 Facebook pages, 546 posts/week

---

## Component-by-Component Scale Analysis

### 2. Networking

| | Current | Enterprise |
|---|---|---|
| **Ingress** | Ngrok tunnel | ALB + WAF + CloudFront |
| **Edge router** | Cisco C1111-4PWB (IOS XE, 6 VLANs, ACLs, NAT, SSH) | AWS Transit Gateway + NAT Gateway |
| **Network segmentation** | 6 VLANs with inter-VLAN ACLs: SERVER, TRUSTED, IOT, IOT-AUTO, HOUSEHOLD, MGMT | VPC with private subnets, security groups, NACLs |
| **WiFi** | 2× UniFi U6+ APs, 4 VLAN-tagged SSIDs | Enterprise APs with RADIUS, 802.1X |
| **Switching** | Netgear GS308EP, Advanced 802.1Q, trunk to Cisco | Enterprise managed switches (Cisco Catalyst, Aruba) |
| **DNS** | Pi-hole on Pi 4B, serving all VLANs via cross-VLAN ACL permits | Route 53 + internal DNS |
| **Firewall** | Cisco extended ACLs per SVI (IOT-ACL, IOT-AUTO-ACL, HOUSEHOLD-ACL) | AWS WAF + security groups + NACLs |
| **Power** | CyberPower CP1500PFCLCD UPS | Redundant power + generator |

**What stays the same:** The zero-port-forwarding philosophy, the VLAN segmentation pattern (production isolated from IoT isolated from household), the DNS filtering approach, and the ACL-based inter-VLAN firewalling all map directly to enterprise equivalents. The Cisco C1111 performing NAT and inter-VLAN routing with ACLs is architecturally the same pattern as an AWS NAT Gateway + security groups — just smaller scale.

---

## What This Architecture Proves

### Already Enterprise-Grade
- **Service boundaries** — Three repos with clear responsibilities
- **Network segmentation** — 6 VLANs with ACL-enforced isolation, same pattern as VPC subnets
- **Inter-VLAN firewalling** — Extended ACLs restricting IoT to internet-only, automation to MQTT-only
- **Edge routing** — Cisco IOS XE with hardened security baseline, same CLI as enterprise networks
- **DNS filtering** — Pi-hole serving all VLANs, cross-VLAN ACL permits for DNS traffic
- **VLAN-tagged WiFi** — 4 SSIDs mapping to 4 VLANs, same pattern as enterprise Meraki/Aruba
- **Self-healing** — Automatic recovery from failures without manual intervention
- **Data model** — Normalized Postgres schema with proper types, relationships, and encryption

### Gaps Already Closed
- ~~**No network segmentation**~~ → 6 VLANs with ACLs enforcing isolation
- ~~**No enterprise edge router**~~ → Cisco C1111-4PWB configured via console and SSH
- ~~**No inter-VLAN firewalling**~~ → 3 extended ACLs applied to SVI interfaces
- ~~**No power protection**~~ → CyberPower CP1500PFCLCD UPS
- ~~**No dedicated services host**~~ → Raspberry Pi 4B running Pi-hole and UniFi Controller
- ~~**Consumer WiFi**~~ → 2× UniFi U6+ APs with 4 VLAN-tagged SSIDs
- ~~**No network-wide DNS filtering**~~ → Pi-hole serving all VLANs

### Gaps Acknowledged (With Mitigation Path)
- **Single point of failure** → Docker Compose (Phase 3)
- **No horizontal scaling** → Container orchestration (future)
- **No CI/CD pipeline** → GitHub Actions (Phase 6)
- **No centralized logging** → Structured logs need aggregation layer
- **Manual deployment** → Ansible playbook (Phase 6)

---

*I built a network that uses the same patterns as enterprise infrastructure — not because I needed to at this scale, but because I'm learning to think at that scale.*

*Last updated: April 19, 2026*
