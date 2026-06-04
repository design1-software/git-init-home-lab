# AI Mentor — Knowledge Base Plan

> **Status:** Design phase only. No deployment until ARIA VLAN 70 cutover and ATX control board are complete.

---

## Purpose

The AI Mentor must know enough to guide effectively, but not so much that it leaks sensitive information, gives unvetted advice, or answers outside its defined scope. This document defines what the AI Mentor is allowed to know, how documents are categorized for retrieval, and how the knowledge base stays current.

The AI Mentor is **not** a general-purpose AI assistant. It is a domain-specific training tool grounded in documentation from this lab. The knowledge base is the boundary of its authority.

---

## Approved Knowledge Sources

These files feed the AI Mentor knowledge base. All are from this repository.

### Network Foundation

| File | Content | Purpose |
|---|---|---|
| `README.md` | Architecture overview, system inventory, operational state | System-level context |
| `ROADMAP.md` | Phase status, what is done vs pending | Scope awareness — mentor knows what is live vs planned |
| `docs/vlan-design.md` | VLAN assignments, ACL rules, switch configs, lessons learned | Primary network reference |
| `docs/network-quick-reference.md` | Device IPs, port maps, key commands | Quick lookup reference |
| `docs/physical-cabling-diagram.md` | Physical cabling layout | Physical topology context |
| `configs/cisco-c1111-*.txt` | C1111 running config snapshots | Cisco verification reference |
| `configs/cisco-3560cx-*.txt` | 3560CX running config snapshots (when committed) | Cisco verification reference |

### ARIA / Proxmox

| File | Content | Purpose |
|---|---|---|
| `docs/proxmox-server-build.md` | ARIA hardware, OS, NIC, WoL, Comet KVM, cutover checklist | ARIA-specific reference |
| `docs/runbooks/proxmox/apt-repo-cleanup.md` | Repo fix procedure | Lab runbook |
| `docs/runbooks/proxmox/wol-comet-kvm.md` | WoL and KVM recovery procedures | Lab runbook |

### Help Desk Training

| File | Content | Purpose |
|---|---|---|
| `labs/helpdesk/ticket-001-dns-failure.md` | DNS troubleshooting scenario | Training ticket |
| `labs/helpdesk/ticket-002-vlan-misassignment.md` | VLAN assignment scenario | Training ticket |
| `labs/helpdesk/ticket-003-proxmox-apt-egress-failure.md` | Linux/apt troubleshooting scenario | Training ticket |
| `labs/helpdesk/ticket-004-ssh-legacy-kex.md` | SSH algorithm negotiation scenario | Training ticket |
| `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` | Asymmetric routing / transitional topology scenario | Training ticket |

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

### AI Mentor Self-Reference

| File | Content | Purpose |
|---|---|---|
| `docs/ai-mentor-architecture.md` | Mentor behavior, guardrails, operating model | Scope awareness |
| `docs/ai-mentor-knowledge-base-plan.md` | This document | Source boundary definition |

---

## Excluded Sources

These are explicitly NOT included in the AI Mentor knowledge base.

| Excluded | Reason |
|---|---|
| Production API keys, tokens, secrets | Security — never in knowledge base |
| `.env` files, credentials | Security |
| Production Facebook page data or content | Out of scope for IT training |
| `social-media-mcp` source code | Not relevant to IT training platform |
| `meta_engagement_pipeline` source code | Not relevant to IT training platform |
| External URLs or live web content | Mentor is grounded in lab docs only |
| Ansible vault encrypted files | Security |
| Personal identifiers beyond lab context | Privacy |

---

## Document Categories

Each document in the knowledge base is tagged with one or more categories. These tags inform how the retrieval system surfaces documents during a session.

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
| Recovery | `recovery` | Disaster recovery, rollback, WoL, KVM |

---

## Metadata Tags (per document)

Each knowledge base document should carry structured metadata for retrieval quality.

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

This metadata is not required for the design phase — it is defined here for the deployment phase. The vector DB will use it for filtered retrieval (e.g., "only surface runbooks tagged `cisco` for this ticket category").

---

## Retrieval Behavior

When a student submits a ticket or asks a question, the retrieval system should surface documents in this priority order:

1. **Exact ticket match** — is there a `labs/helpdesk/ticket-*.md` that matches the reported symptom?
2. **Runbook match** — is there a `docs/runbooks/` document for this failure type?
3. **Lab match** — is there a `labs/lab-*.md` that covers this technology?
4. **Reference match** — is there a `docs/` reference document that contains the relevant config or topology?

The retrieval system does not surface the full document — it surfaces the relevant sections, with enough context for the mentor to guide without exposing the full answer.

---

## Student-Facing vs Mentor-Only Documents

Not all knowledge base content should be surfaced to students directly.

| Document type | Student can see | Mentor uses internally |
|---|---|---|
| Ticket scenarios (`labs/helpdesk/`) | Scenario description only | Full diagnostic path, root causes, resolution |
| Runbooks | Summary only | Full procedure |
| Cisco configs | Reference commands | Full running config |
| Architecture docs | Overview | Full detail |
| ROADMAP.md | Phase status | Full detail |

The AI Mentor does not recite full runbooks to students. It uses them internally to know what correct resolution looks like, and guides the student toward it step by step.

---

## Ticket-to-Runbook Mapping

| Ticket | Related Runbook | Related Lab |
|---|---|---|
| 001 — DNS failure | (Pi-hole service management) | — |
| 002 — Wrong VLAN | `docs/vlan-design.md` lessons | — |
| 003 — Proxmox apt failure | `docs/runbooks/proxmox/apt-repo-cleanup.md` | — |
| 004 — SSH legacy KEX | `docs/runbooks/ssh-key-collision.md` | `labs/lab-004-network-automation.md` |
| 005 — VLAN 1 return path | `docs/runbooks/cisco/vlan1-transitional-routing.md` | `labs/lab-010-ospfv2.md` |

---

## Update Workflow

The knowledge base is updated when repo documentation is updated — not on a live crawl.

```
1. Documentation change committed to repo
2. Affected file re-chunked and re-embedded into vector DB
3. Existing embeddings for that file replaced (not appended)
4. No re-embedding of unchanged files
5. Mentor tested on related ticket scenarios after major doc updates
```

Manual trigger for rebuild: after any commit that updates `docs/`, `labs/helpdesk/`, or `docs/runbooks/`.

---

## Deployment Gate

The knowledge base deployment is blocked on:

```
[ ] ATX control board installed and Comet hard reset validated
[ ] ARIA on VLAN 70 (192.168.70.10/24)
[ ] Proxmox vmbr0 bridge configured and stable
[ ] Vector DB service (ChromaDB or similar) deployed as LXC on ARIA
[ ] Knowledge base ingestion pipeline tested
[ ] Retrieval accuracy validated against ticket-001 through ticket-005
```

Knowledge base design and source curation (this document) can proceed without ARIA being ready. Ingestion and embedding require the ARIA VLAN 70 deployment to be complete.

---

*Document created: Jun 4, 2026*
*Status: Design phase — no deployment*
