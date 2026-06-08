# AI Mentor — Implementation Status

> **Status:** Current source of truth as of Jun 8, 2026. This document reconciles the original AI Mentor design plan with the deployed ARIA implementation.

---

## Governance Rule

The documented plan must be followed.

Any ad hoc change must be explicitly approved before implementation and must include:

1. Reason for the deviation
2. Risk introduced by the deviation
3. Expected benefit
4. Rollback path
5. Required repository documentation update

No implementation change that alters the AI Mentor architecture, security model, retrieval model, Zammad integration model, or training workflow should be treated as informal or undocumented.

---

## Executive Summary

The AI Mentor is the coaching layer for all ARIA training, not only help desk ticketing. The long-term scope includes Field Tech Foundation, Help Desk Documentation, Linux and Security Foundation, Network Troubleshooting, Cybersecurity Readiness Labs, Active Directory, Windows support, Cisco, Proxmox, SIEM, documentation coaching, and interview preparation.

Current reality:

- The AI Mentor platform foundation is live on ARIA.
- The first working domain is Zammad/help desk ticketing.
- The service uses repo-grounded knowledge retrieval from JSONL chunks.
- ChromaDB/vector DB is deferred and not blocking v1.
- Zammad integration is read-only and instructor-mediated.
- LLM integration is implemented as an assistive layer, but the provider is disabled until explicitly enabled.
- Auth and role separation v1 are implemented.
- Cross-environment mentor workflows are not yet implemented beyond the help desk/Zammad foundation.

---

## Designed and Documented

| Phase | Document / Area | Status |
|---|---|---|
| AI-1 | `docs/ai-mentor-architecture.md` | Complete |
| AI-2 | `docs/ai-mentor-knowledge-base-plan.md` | Complete |
| AI-3 | `docs/ai-mentor-ticketing-integration.md` | Complete |
| AI-4 | `docs/ai-mentor-model-decision.md` | Complete |
| AI-5 | `docs/ai-mentor-guardrails-expanded.md` | Complete |
| AI-6 | `labs/helpdesk/ticket-001` through `ticket-010` | Complete as written scenarios |

---

## Deployed on ARIA

| Component | Status | Notes |
|---|---|---|
| Zammad | Live | CT 110 `aria-zammad-01`; Docker Compose; `helpdesk.aria.local`; admin/student workflow validated |
| AI Mentor backend | Live | CT 120 `aria-ai-mentor-01`; FastAPI; systemd service; Swagger UI; health and mentor endpoints |
| KB ingestion | Live | `scripts/ingest_docs.py`; approved repo docs chunked to `data/kb/chunks.jsonl` |
| Retrieval layer | Live v1 | JSONL lexical/scored retrieval; ChromaDB deferred |
| Session logging | Live | Local JSON session records tied to mentor requests |
| Zammad read-only API | Live | Ticket read, article read, ticket lookup by visible ticket number |
| Instructor panel | Live | `/instructor`; protected by local auth; read-only review of Zammad ticket + mentor guidance |
| Assistive LLM layer | Built, disabled | `/llm/status` and LLM guidance endpoints exist; provider remains disabled until explicitly enabled |
| Auth + role separation | Live v1 | Local users, signed HTTP-only cookie, admin/instructor protected routes |

---

## Intentionally Deferred

| Item | Status | Reason |
|---|---|---|
| ChromaDB / vector DB | Deferred | JSONL retrieval is sufficient for v1 validation; vector DB will return when retrieval complexity requires it |
| Zammad webhook automation | Deferred | Current model is read-only/instructor-mediated to reduce risk |
| Zammad writeback | Deferred | No AI-generated comments should be posted without instructor approval and audit logging |
| LLM live provider use | Disabled | Provider switch remains off even if an API key exists; deterministic mentor output remains authoritative |
| Student-facing panel | Pending | Should follow audit/event logging and reusable lab workflow templates |
| Field-to-Cyber lab submission model | Pending | Needs a lab completion review workflow distinct from break/fix help desk tickets |
| AD/Windows mentor workflows | Pending | Planned domain, not yet implemented |
| SIEM/Wazuh mentor workflows | Pending | Planned domain, not yet implemented |

---

## Current AI Mentor Phases

| Phase | Name | Status |
|---|---|---|
| 1 | Backend foundation | Complete |
| 2 | KB ingestion/retrieval | Complete with JSONL v1 retrieval |
| 3 | Zammad read-only integration | Complete |
| 4 | Ticket-009 completion detection | Complete |
| 5 | Instructor draft panel | Complete |
| 6 | Assistive LLM foundation/display | Complete, provider disabled |
| 7 | Auth + role separation v1 | Complete |
| 8 | Audit/event logging | Pending |
| 9 | Ticket lab template system | Pending |
| 10 | Implement Ticket-001 through Ticket-005 mentor workflows | Pending |
| 11 | Student-facing mentor panel v1 | Pending |
| 12 | Implement Ticket-006 through Ticket-010 mentor workflows | Pending |
| 13 | Instructor review queue | Pending |
| 14 | Controlled Zammad writeback / instructor approval workflow | Pending |
| 15 | Operational hardening | Pending |

---

## Cross-Environment Coverage Status

| Training Environment / Domain | Current Status | Next Required Work |
|---|---|---|
| Help Desk / Zammad | Operational v1 foundation | Add audit logging and reusable ticket templates |
| DNS / Pi-hole | Scenario written, not implemented as workflow | Implement Ticket-001 mentor workflow |
| VLAN / Switching | Scenario written, not implemented as workflow | Implement Ticket-002 mentor workflow |
| Linux / Proxmox | Scenario written, not implemented as workflow | Implement Ticket-003 and Proxmox evidence rules |
| Cisco / SSH / Switching | Scenario written, not implemented as workflow | Implement Ticket-004 and Cisco guardrail path |
| WiFi / UniFi | Scenario written, not implemented as workflow | Validate Ticket-005 or revise scenario mapping |
| Proxmox recovery | Scenario written, live validation partial | Implement Ticket-007 workflow after evidence model is finalized |
| SIEM / Wazuh | Planned | Deploy Wazuh workload, then implement Ticket-010 workflow |
| Active Directory / Windows | Planned | Deploy AD/Windows lab, define evidence model and ticket workflow |
| Field Tech Foundation Labs | Instructor notes exist | Design lab completion ticket/submission workflow |
| Cybersecurity Readiness Labs | Planned | Requires Wazuh/SIEM workload and incident-review templates |

---

## Current Discrepancy Decisions

### JSONL Retrieval Instead of ChromaDB

Original design called for ChromaDB or similar vector DB as the retrieval layer. Implementation currently uses JSONL chunk retrieval.

Decision: JSONL retrieval is accepted for v1 because it is simple, inspectable, cheap, and adequate for the current documented corpus.

Risk: Lexical retrieval may degrade as document count and domain complexity increase.

Rollback / future path: Deploy ChromaDB and re-index approved chunks when retrieval quality requires semantic search or metadata-filtered retrieval.

### Read-Only Zammad Integration Instead of Webhook Automation

Original design described ticket-based interaction with future webhook automation.

Decision: Current v1 uses read-only API access plus instructor panel review.

Risk: Workflow is less automated and requires instructor action.

Benefit: Prevents AI from writing into the official ticket record before audit logging, approval workflow, and safety validation exist.

### Assistive LLM Disabled by Default

Decision: The LLM layer is implemented but disabled through `ARIA_LLM_PROVIDER=disabled`.

Risk: Outputs are deterministic and less conversational until provider is enabled.

Benefit: No token spend, no external inference dependency, and deterministic mentor logic remains authoritative.

---

## Required Before Phase 8

Before Phase 8 begins, the repo must reflect the deployed state. This document is the baseline. Architecture, KB, ticketing, and roadmap docs should point here when their original design status is superseded by implementation reality.

Phase 8 should begin with audit/event logging for:

- login and logout
- protected endpoint access
- mentor guidance requests
- ticket number reviewed
- user role
- request outcome
- LLM provider state
- Zammad read-only access events
