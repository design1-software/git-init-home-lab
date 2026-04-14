# Enterprise Scale Design

> How this platform would evolve from a single-server home lab to a production enterprise deployment — and what that tells you about the engineering decisions behind it.

---

## Purpose of This Document

This system is currently a **working production platform** running on home lab infrastructure: one server, one tunnel, one database. It produces 546+ posts per week across 3 Facebook pages with 24/7 uptime.

This document maps every component to its enterprise equivalent — not because the home lab needs Kubernetes, but because **understanding the path from prototype to production at scale is the difference between building something that works and building something that can grow.**

---

## Current Architecture Summary

```
┌─────────────────────────────────────────────┐
│  Home Server (Acer Aspire 3)                │
│  ├── social-media-mcp    (MCP Server)       │
│  ├── fb-content-system   (Content Factory)  │
│  └── Ngrok Agent         (Tunnel)           │
└──────────────────┬──────────────────────────┘
                   │ Ethernet (192.168.100.12)
┌──────────────────┴──────────────────────────┐
│  Cisco C1111-4PWB (Lab Edge Router)         │
│  ├── IOS XE · SSH · DHCP · NAT overload    │
│  ├── WAN: 10.0.0.119 (DHCP from XB8)       │
│  └── LAN: 192.168.100.0/24                 │
└──────────────────┬──────────────────────────┘
                   │ Ethernet (Vlan1)
┌──────────────────┴──────────────────────────┐
│  Netgear GS308EP (Lab Switch, 62W PoE+)    │
│  ├── Raspberry Pi 4B (Pi-hole, UniFi CTRL)  │
│  ├── 2× UniFi U6+ APs (broadcasting SSID)   │
│  └── Expansion ports available              │
│                                             │
│  Netgear GS316EP (still on household XB8)   │
│  └── Planned: migrate to Cisco + VLAN trunk │
│                                             │
│  UPS: CyberPower CP1500PFCLCD              │
│  VLANs: Server (10) / Trusted (20) / IoT (30) — PLANNED │
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

### 1. Compute

| | Current | Enterprise |
|---|---|---|
| **Server** | Single laptop (Acer Aspire 3, AMD Ryzen) | Kubernetes cluster or AWS ECS (3+ nodes across availability zones) |
| **Process model** | One Node.js process per service | Containerized microservices with horizontal pod autoscaling |
| **Deployment** | Manual `git pull` + `npm start` | CI/CD pipeline → Docker image → rolling deploy with canary |
| **Scaling** | Vertical only (add RAM) | Horizontal (add pods/containers based on CPU/memory/queue depth) |
| **Failure mode** | Laptop dies = total outage | Pod dies = scheduler restarts on healthy node in seconds |

**What I'd change at scale:** The MCP server and content system would become separate Docker services behind a load balancer. Each scales independently — the MCP server scales on concurrent connections, the content renderer scales on queue depth. A Helm chart or ECS task definition would codify the desired state.

**What stays the same:** The service boundaries are already correct. `social-media-mcp` handles tool execution, `meta_engagement_pipeline` handles orchestration, `fb-content-system` handles content production. These are naturally separate scaling units. No refactoring needed — just containerization and orchestration.

---

### 2. Networking

| | Current | Enterprise |
|---|---|---|
| **Ingress** | Ngrok tunnel (single TCP connection) | Application Load Balancer + WAF + CloudFront CDN |
| **Internal routing** | Direct HTTP between services | Service mesh (Istio) or internal ALB with service discovery |
| **Edge router** | Cisco C1111-4PWB ISR (IOS XE, SSH-managed, DHCP + NAT + PAT) | AWS Transit Gateway + NAT Gateway + Direct Connect |
| **Network segmentation** | Dual-network topology: lab (192.168.100.0/24) isolated from household (10.0.0.0/24) via Cisco; dual-switch (GS316EP + GS308EP); VLANs planned (Server/Trusted/IoT) | VPC with private subnets, security groups, NACLs |
| **WiFi** | 2× UniFi U6+ APs adopted, broadcasting SSID, managed via UniFi Controller on Pi | Enterprise APs with RADIUS auth, 802.1X |
| **DNS** | Pi-hole on Raspberry Pi 4B (87K-domain blocklist) serving all lab clients | Route 53 + internal DNS with split-horizon |
| **DDoS protection** | None | CloudFlare or AWS Shield |
| **TLS** | Ngrok provides TLS termination | ACM certificates, TLS 1.3, end-to-end encryption |
| **Power** | CyberPower CP1500PFCLCD UPS | Redundant power feeds + generator |

**What I'd change at scale:** Ngrok is a development convenience, not a production ingress. At enterprise scale, the MCP server would sit behind an ALB in a private subnet with no public IP. Meta webhooks would hit a public-facing API Gateway that validates signatures before forwarding to the private orchestrator. Rate limiting would be enforced at the WAF layer, not in application code.

**What stays the same:** The zero-port-forwarding philosophy carries forward — enterprise deployments also avoid exposing services directly. The MCP auth token pattern (`x-mcp-token` header verification) maps directly to API Gateway authorization. The planned VLAN segmentation (Server/Trusted/IoT) mirrors enterprise VPC subnet design — production workloads isolated from user devices and untrusted IoT. The UniFi AP deployment (soon VLAN-tagged SSIDs) is the same pattern enterprises use with Cisco Meraki or Aruba. Pi-hole as a DNS sinkhole maps to enterprise DNS filtering (Cisco Umbrella, Zscaler). The Cisco C1111 performing NAT and routing is architecturally the same pattern as an AWS NAT Gateway + VGW — just smaller scale.

---

### 3. Data Layer

| | Current | Enterprise |
|---|---|---|
| **Primary database** | Single Postgres instance (Railway) | RDS Multi-AZ with automated failover |
| **Local storage** | SQLite ledger (crash recovery) | Redis or DynamoDB for distributed state |
| **Read scaling** | Single instance handles reads + writes | Read replicas for analytics, primary for writes |
| **Backups** | Daily PowerShell script → local zip; Cisco config backed up to text file | Automated point-in-time recovery (35-day retention) |
| **Caching** | None | Redis/ElastiCache for hot data (page tokens, brand configs) |

**What I'd change at scale:** The SQLite ledger in `fb-content-system` (which provides crash-safe post tracking) would become a Redis-backed queue with at-least-once delivery. The Sequelize models in `meta_engagement_pipeline` already define the schema correctly for Postgres — the migration to RDS would be a connection string change, not a rewrite. Page brand configs (`page_brand.json`) would move to a config service or DynamoDB table.

**What stays the same:** The data model is already normalized and uses proper relationships (Users → Pages → ScheduledPosts → Interactions). The `BIGINT` choice for follower counts, UUID primary keys, and encrypted token fields all indicate enterprise-grade schema design. No schema changes needed at scale.

---

### 4. Observability

| | Current | Enterprise |
|---|---|---|
| **Logging** | Winston logger → daily log files | Structured JSON → CloudWatch/ELK/Datadog |
| **Alerting** | Email via `logger.error` + nodemailer | PagerDuty with escalation policies |
| **Health checks** | PowerShell script every 5 min | Kubernetes liveness/readiness probes + ALB health checks |
| **Metrics** | Uptime Kuma on dedicated Pi 4B (planned, Phase 4) | Prometheus/Grafana or Datadog with custom dashboards |
| **Tracing** | None | OpenTelemetry distributed traces across services |

**What I'd change at scale:** Every service would emit structured JSON logs with correlation IDs that trace a request from webhook ingestion through MCP tool execution to Graph API publish. The `selfHealingService.js` pattern would evolve into a circuit breaker (Hystrix/resilience4js pattern) with metrics. SLO dashboards would track: post publish success rate (target: 99.5%), MCP tool response time (p99 < 5s), greeting delivery on-time rate (target: 100%).

**What stays the same:** The self-healing architecture is already production-grade. The `selfHealingService.js`, `cronHealth.js`, `dbWriteHealth.js`, and email alerting form a monitoring stack that most startups don't have. The error classification and recovery patterns map directly to enterprise incident response.

---

### 5. CI/CD and Reliability

| | Current | Enterprise |
|---|---|---|
| **Deployment** | Manual git pull + restart | GitHub Actions → build → test → staging → canary → prod |
| **Testing** | Jest unit tests | Unit + integration + E2E + load tests in pipeline |
| **Rollback** | Manual git revert | Automated rollback on health check failure |
| **Recovery time** | ~4-6 hours (bare metal rebuild) | < 5 minutes (container restart or failover) |
| **Recovery point** | Last daily backup | < 1 minute (continuous replication) |
| **Availability target** | Best effort (~99%) | 99.9% (8.7 hours downtime/year) |

**What I'd change at scale:** A GitHub Actions pipeline would: run linting and type checks, execute the Jest test suite, build Docker images, push to ECR, deploy to a staging environment, run smoke tests, then promote to production via blue/green deployment. The Ngrok tunnel watchdog logic would be replaced by Kubernetes self-healing (pod restart on liveness probe failure). Infrastructure would be defined in Terraform.

**What stays the same:** The PM2 ecosystem config in `meta_engagement_pipeline` already defines multi-process management with memory limits and auto-restart — this maps directly to Kubernetes resource limits and restart policies. The worker/server separation is the exact pattern ECS uses (web service + worker service).

---

### 6. Security

| | Current | Enterprise |
|---|---|---|
| **Secrets** | `.env` files (gitignored) | AWS Secrets Manager or HashiCorp Vault |
| **Authentication** | MCP auth tokens, session-based UI auth | OAuth 2.0 + JWT with refresh rotation |
| **Network security** | Ngrok TLS + token verification; Cisco IOS with hardened baseline (SSH v2, enable secret, VTY login local, service password-encryption) | VPC + security groups + WAF rules |
| **Data encryption** | Sequelize field-level encryption | At-rest (KMS) + in-transit (TLS) + field-level |
| **Audit** | Logger captures auth events | CloudTrail + audit log table with immutable writes |
| **Compliance** | N/A | SOC 2 Type II controls mapped |

**What I'd change at scale:** Secrets would live in AWS SSM Parameter Store or Secrets Manager, injected at runtime via IAM roles — never in environment variables on disk. The Meta page access tokens (which require periodic refresh) would use a token rotation service. The `x-mcp-token` verification would be replaced with mutual TLS between services.

**What stays the same:** The security posture is already thoughtful. Token encryption in Sequelize models, the zero-port-forwarding policy, callback authentication on all Sidecar endpoints, PII utilities (`piiUtils.js`), and the Cisco IOS security baseline show security-first design. These patterns don't change at enterprise scale — they get formalized into policies.

---

## What This Architecture Proves

### Already Enterprise-Grade
- **Service boundaries** — Three repos with clear responsibilities is a microservices architecture
- **Dual-engine pattern** — Graph API + Sidecar shows creative problem-solving around platform constraints
- **Self-healing** — Automatic recovery from failures without manual intervention
- **Quality gates** — LLM-based content scoring with configurable thresholds
- **Data model** — Normalized Postgres schema with proper types, relationships, and encryption
- **Persona guardrails** — Configurable content policies stored in DB, not hardcoded
- **Network edge** — Cisco IOS XE edge router with hardened baseline, same CLI that runs enterprise networks

### Gaps Acknowledged (With Mitigation Path)
- **Single point of failure** → Docker Compose (immediate), K8s (future)
- **No horizontal scaling** → Container orchestration enables this without code changes
- **No CI/CD pipeline** → GitHub Actions workflow (planned Phase 6)
- **No centralized logging** → Structured logs already emitted, need aggregation layer
- **Manual deployment** → Ansible playbook (planned Phase 6)

### Gaps Already Closed
- ~~**No network segmentation**~~ → Dual-network topology via Cisco C1111, with VLAN plan for next layer of segmentation
- ~~**No enterprise edge router**~~ → Cisco C1111-4PWB ISR configured via console and SSH
- ~~**No power protection**~~ → CyberPower CP1500PFCLCD UPS protecting all infrastructure
- ~~**No dedicated monitoring host**~~ → Raspberry Pi 4B running Pi-hole and UniFi Controller (Uptime Kuma planned Phase 4)
- ~~**Consumer WiFi**~~ → 2× UniFi U6+ APs adopted and broadcasting on the lab network
- ~~**No network-wide DNS filtering**~~ → Pi-hole with 87K-domain blocklist serving all lab clients

### The Key Insight

The hardest part of scaling a system isn't the infrastructure — it's the **architecture decisions that were made at the beginning**. Service boundaries, data models, error handling patterns, and authentication flows are expensive to change later.

This system's architecture was designed for a single server but **built with patterns that scale without refactoring**:
- Services communicate over HTTP/SSE, not shared memory
- State lives in Postgres, not in-process
- Configuration is database-driven (`PagePromptTemplate`), not hardcoded
- Media generation is asynchronous with callback-based completion
- The worker and server are separate processes with separate scaling characteristics
- The lab network is routed through an enterprise router — same CLI and patterns as production networks

The infrastructure can grow from one laptop to a cluster. The code doesn't need to change.

---

## If I Had to Deploy This to AWS Tomorrow

```
                         ┌──────────────┐
                         │ Route 53 DNS │
                         └──────┬───────┘
                                │
                         ┌──────┴───────┐
                         │ CloudFront   │
                         │ + WAF        │
                         └──────┬───────┘
                                │
              ┌─────────────────┴─────────────────┐
              │         Application Load Balancer   │
              │         (public subnet)             │
              └────────┬──────────────┬────────────┘
                       │              │
            ┌──────────┴───┐  ┌───────┴──────────┐
            │ ECS Service: │  │ ECS Service:      │
            │ API + Webhooks│  │ MCP Server        │
            │ (2 tasks)    │  │ (2 tasks)         │
            └──────┬───────┘  └───────┬───────────┘
                   │                  │
            ┌──────┴──────────────────┴───────────┐
            │           Private Subnet             │
            │  ┌─────────┐  ┌──────────────────┐  │
            │  │ RDS      │  │ ECS Service:     │  │
            │  │ Postgres │  │ Worker (1 task)  │  │
            │  │ Multi-AZ │  │ Crons + Queues   │  │
            │  └─────────┘  └──────────────────┘  │
            │  ┌─────────┐  ┌──────────────────┐  │
            │  │ Redis    │  │ S3: Media Assets │  │
            │  │ (cache)  │  │ + CloudFront CDN │  │
            │  └─────────┘  └──────────────────┘  │
            └─────────────────────────────────────┘

Estimated monthly cost: ~$150-250 (ECS Fargate + RDS t3.micro + Redis t3.micro + S3)
```

This isn't hypothetical architecture — every service maps 1:1 from the current deployment. The Railway app becomes the ECS API service. The home server MCP becomes the ECS MCP service. The PM2 worker becomes the ECS worker service. The Postgres database stays Postgres. The Cisco-based network segmentation becomes VPC subnets and security groups.

---

*This document demonstrates that the current system was built with enterprise patterns from day one. The infrastructure is home lab scale. The engineering is not.*

*Last updated: April 14, 2026*
