# AI Mentor — Knowledge Base Plan

> **Status:** Implemented v1 as of Jun 8, 2026. The approved repository documents are ingested into JSONL chunks on CT 120. ChromaDB/vector DB remains deferred.

> **Source of truth for implementation status:** `docs/ai-mentor-implementation-status.md`

---

## Purpose

The AI Mentor must know enough to guide effectively, but not so much that it leaks sensitive information, gives unvetted advice, or answers outside its defined scope. This document defines what the AI Mentor is allowed to know, how documents are categorized for retrieval, and how the knowledge base stays current.

The AI Mentor is **not** a general-purpose AI assistant. It is a domain-specific training tool grounded in documentation from this lab. The knowledge base is the boundary of its authority.

---

## Current v1 Implementation

Current retrieval implementation:

```text
Repository docs/labs/runbooks
        |
        v
scripts/ingest_docs.py
        |
        v
data/kb/chunks.jsonl
        |
        v
FastAPI retrieval service
```

The deployed v1 retrieval layer is JSONL lexical/scored retrieval. ChromaDB/vector DB is intentionally deferred.

### Why JSONL Retrieval Is Accepted for v1

| Reason | Explanation |
|---|---|
| Inspectability | Chunks are readable and easy to debug |
| Low operational burden | No separate vector DB service to deploy or maintain |
| Adequate corpus size | Current repo corpus is small enough for JSONL retrieval |
| Safety | Retrieval behavior is easier to inspect before student-facing rollout |
| Cost | No embedding API or local embedding service required |

### ChromaDB Future Path

ChromaDB or another vector database should be reconsidered when:

```text
[ ] Retrieval quality drops as the corpus grows
[ ] Metadata-filtered retrieval becomes mandatory
[ ] Cross-domain mentor workflows require semantic matching
[ ] Student-facing responses need stronger source separation
[ ] The JSONL retrieval implementation becomes difficult to tune
```

---

## Approved Knowledge Sources

These files feed the AI Mentor knowledge base. All are from this repository.

### Network Foundation

| File | Content | Purpose |
|---|---|---|
| `README.md` | Architecture overview, system inventory, operational state | System-level context |
| `ROADMAP.md` | Phase status, what is done vs pending | Scope awareness |
| `docs/vlan-design.md` | VLAN assignments, ACL rules, switch configs, lessons learned | Primary network reference |
| `docs/network-quick-reference.md` | Device IPs, port maps, key commands | Quick lookup reference |
| `docs/physical-cabling-diagram.md` | Physical cabling layout | Physical topology context |
| `configs/cisco-c1111-*.txt` | C1111 running config snapshots | Cisco verification reference |
| `configs/cisco-3560cx-*.txt` | 3560CX running config snapshots when committed | Cisco verification reference |

### ARIA / Proxmox

| File | Content | Purpose |
|---|---|---|
| `docs/proxmox-server-build.md` | ARIA hardware, OS, NIC, WoL, Comet KVM, cutover checklist | ARIA-specific reference |
| `docs/runbooks/proxmox/apt-repo-cleanup.md` | Repo fix procedure | Lab runbook |
| `docs/runbooks/proxmox/wol-comet-kvm.md` | WoL and KVM recovery procedures | Lab runbook |
| `docs/runbooks/zammad/zammad-lxc-deployment.md` | Zammad deployment and operations | Ticketing platform runbook |

### Help Desk Training

| File | Content | Purpose |
|---|---|---|
| `labs/helpdesk/ticket-001-dns-failure.md` | DNS troubleshooting scenario | Training ticket |
| `labs/helpdesk/ticket-002-vlan-misassignment.md` | VLAN assignment scenario | Training ticket |
| `labs/helpdesk/ticket-003-proxmox-apt-egress-failure.md` | Linux/apt troubleshooting scenario | Training ticket |
| `labs/helpdesk/ticket-004-ssh-legacy-kex.md` | SSH algorithm negotiation scenario | Training ticket |
| `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` | Asymmetric routing / transitional topology scenario | Training ticket |
| `labs/helpdesk/ticket-006-proxmox-repo-hygiene.md` | Package/repo hygiene scenario | Training ticket |
| `labs/helpdesk/ticket-007-proxmox-vlan70-migration.md` | ARIA VLAN 70 migration scenario | Training ticket |
| `labs/helpdesk/ticket-008-comet-atx-hard-reset-validation.md` | Hardware validation scenario | Training ticket |
| `labs/helpdesk/ticket-009-zammad-ticket-triage.md` | ITSM/Zammad workflow scenario | Training ticket |
| `labs/helpdesk/ticket-010-wazuh-alert-investigation.md` | SIEM/Wazuh investigation scenario | Training ticket |

### CCNA Labs

| File | Content | Purpose |
|---|---|---|
| `labs/lab-003-ntp-snmp.md` | NTP, SNMP | Lab reference |
| `labs/lab-004-network-automation.md` | Ansible, Netmiko | Lab reference |
| `labs/lab-005-restconf.md` | RESTCONF API | Lab reference |
| `labs/lab-006-stp-rstp.md` | STP, Rapid-PVST+ | Lab reference |
| `labs/lab-007-ospfv3.md` | OSPFv3 IPv6 | Lab reference |
| `labs/lab-008-aaa.md` | AAA authentication | Lab reference |
| `labs/lab-009-ip-source-guard.md` | IP Source Guard | Lab reference |
| `labs/lab-010-ospfv2.md` | OSPFv2, TRANSIT, OSPF adjacency | Lab reference |

### Runbooks

| File | Content | Purpose |
|---|---|---|
| `docs/runbooks/ssh-key-collision.md` | SSH host key conflict resolution | Troubleshooting runbook |
| `docs/runbooks/disaster-recovery.md` | Bare-metal recovery procedure | Recovery reference |
| `docs/runbooks/server-restart.md` | Docker/MCP server restart procedure | Runbook |
| `docs/runbooks/ngrok-recovery.md` | Ngrok tunnel recovery | Runbook |
| `docs/runbooks/config-backup.md` | Netmiko backup procedure | Runbook |
| `docs/runbooks/cisco/vlan1-temporary-host-routes.md` | VLAN 1 host route rationale | Cisco runbook |

### ARIA Training Platform

| File | Content | Purpose |
|---|---|---|
| `docs/runbooks/aria-student-container-provisioning.md` | Student container provisioning standard | Instructor operations reference |
| `docs/monitoring-architecture.md` | Monitoring architecture | Platform context |
| `labs/field-tech/sha-neal-roadmap.md` | Student lab progression | Training context |
| `labs/field-tech/**/instructor-notes.md` | Field Tech lab instructor notes | Instructor reference |

> **Note on student PII:** The AI Mentor must never surface individual student personal data in responses. It may reference the process and account model, not filled-in personal records.

### AI Mentor Self-Reference

| File | Content | Purpose |
|---|---|---|
| `docs/ai-mentor-architecture.md` | Mentor behavior, guardrails, operating model | Scope awareness |
| `docs/ai-mentor-knowledge-base-plan.md` | KB source boundary | Source boundary definition |
| `docs/ai-mentor-ticketing-integration.md` | Ticket integration model | Workflow reference |
| `docs/ai-mentor-implementation-status.md` | Current deployed state | Implementation source of truth |

---

## Excluded Sources

These are explicitly NOT included in the AI Mentor knowledge base.

| Excluded | Reason |
|---|---|
| Production API keys, tokens, secrets | Security |
| `.env` files, credentials | Security |
| Production social-media platform data | Out of scope for IT training |
| External URLs or live web content | Mentor is grounded in lab docs only |
| Ansible vault encrypted files | Security |
| Personal identifiers beyond lab context | Privacy |
| Student-facing answer keys that would spoil discovery | Training integrity |

---

## Document Categories

Each document in the knowledge base is tagged into one or more retrieval categories.

| Category | Tag | Description |
|---|---|---|
| Topology | `topology` | Physical and logical network layout |
| VLAN | `vlan` | VLAN design, assignments, switch config |
| Routing | `routing` | OSPF, static routes, inter-VLAN |
| Switching | `switching` | STP, trunking, port config |
| Security | `security` | ACLs, AAA, DHCP snooping, IP Source Guard |
| DNS | `dns` | Pi-hole, DNS resolution, blocklists |
| SSH | `ssh` | SSH access, key exchange, host key management |
| Linux | `linux` | Proxmox host OS, services, package management |
| Proxmox | `proxmox` | Hypervisor, networking, storage, KVM |
| Cisco | `cisco` | C1111, 3560CX, IOS commands |
| Training | `training` | Helpdesk ticket scenarios, CCNA labs |
| Runbook | `runbook` | Operational procedures |
| Help Desk Lab | `helpdesk_lab` | Zammad/help desk workflows |
| AI Mentor | `ai_mentor` | Mentor design, guardrails, implementation status |
| Recovery | `recovery` | Disaster recovery, rollback, WoL, KVM |

---

## Metadata Tags

Structured metadata remains the future retrieval target. JSONL v1 currently uses simpler categorization and scored matching.

```yaml
---
kb_category: [vlan, switching]
kb_devices: [GS308EP, 3560CX]
kb_difficulty: beginner
kb_ticket_ids: [002]
kb_last_verified: 2026-06-01
kb_status: active   # active | outdated | draft
---
```

---

## Retrieval Behavior

When a student submits a ticket or asks for guidance, the retrieval system should surface documents in this priority order:

1. Exact ticket match — matching `labs/helpdesk/ticket-*.md`
2. Runbook match — matching `docs/runbooks/`
3. Lab match — matching `labs/lab-*.md`
4. Reference match — matching `docs/` reference documents

The retrieval system does not surface full documents to students. It surfaces relevant sections with enough context for the mentor to guide without exposing the full answer.

---

## Student-Facing vs Mentor-Only Documents

| Document type | Student can see | Mentor uses internally |
|---|---|---|
| Ticket scenarios (`labs/helpdesk/`) | Scenario description only | Full diagnostic path, root causes, resolution |
| Runbooks | Summary only | Full procedure |
| Cisco configs | Reference commands | Full running config |
| Architecture docs | Overview | Full detail |
| ROADMAP.md | Phase status | Full detail |
| Field-tech instructor notes | Coaching prompts only | Expected outputs and common mistakes |

The AI Mentor does not recite full runbooks to students. It uses them internally to know what correct resolution looks like and guides the student toward it step by step.

---

## Ticket-to-Runbook Mapping

| Ticket | Related Runbook / Source | Related Lab |
|---|---|---|
| 001 — DNS failure | Pi-hole / network reference | — |
| 002 — Wrong VLAN | `docs/vlan-design.md` | — |
| 003 — Proxmox apt failure | `docs/runbooks/proxmox/apt-repo-cleanup.md` | — |
| 004 — SSH legacy KEX | `docs/runbooks/ssh-key-collision.md` | `labs/lab-004-network-automation.md` |
| 005 — VLAN 1 return path | Cisco runbook / VLAN design | `labs/lab-010-ospfv2.md` |
| 006 — Proxmox repo hygiene | Proxmox runbook | — |
| 007 — VLAN 70 migration | Proxmox + VLAN docs | — |
| 008 — Comet ATX validation | Proxmox build + KVM docs | — |
| 009 — Zammad triage | Zammad runbook | — |
| 010 — Wazuh alert | Wazuh docs once deployed | — |

---

## Update Workflow

The knowledge base is updated when repo documentation is updated — not on a live crawl.

```text
1. Documentation change committed to repo
2. CT 120 repo clone pulls latest main
3. `scripts/ingest_docs.py` rebuilds JSONL chunks
4. `/kb/status` confirms ready state
5. Mentor tested on related ticket scenarios after major doc updates
6. CT 120 backup taken after successful validation
```

Manual trigger for rebuild: after any commit that updates `docs/`, `labs/helpdesk/`, `docs/runbooks/`, or AI Mentor service files that the mentor should understand.

---

## Deployment Gate Status

Original gate items:

```text
[x] ATX control board installed and Comet power control validated
[x] ARIA on VLAN 70 (192.168.70.10/24)
[x] Proxmox vmbr0 bridge configured and stable
[x] Knowledge base ingestion pipeline tested
[x] JSONL retrieval validated against Ticket-009
[ ] Retrieval accuracy validated against ticket-001 through ticket-010
[ ] ChromaDB/vector DB deployed, if still required
```

ChromaDB is no longer a v1 blocker. It is deferred until retrieval quality or scale requires it.

---

*Document reconciled: Jun 8, 2026*
