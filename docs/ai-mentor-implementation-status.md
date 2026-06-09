# AI Mentor — Implementation Status

> **Status:** Current source of truth as of Jun 9, 2026. This document reconciles the original AI Mentor design plan with the deployed ARIA implementation after Phase 13.

---

## Governance Rule

The documented plan must be followed.

Any ad hoc change must be explicitly approved before implementation and must include:

1. Reason for the deviation
2. Risk introduced by the deviation
3. Expected benefit
4. Rollback path
5. Required repository documentation update

No implementation change that alters the AI Mentor architecture, security model, retrieval model, Zammad integration model, training workflow, or training-domain roadmap should be treated as informal or undocumented.

---

## Documentation Accuracy Rule

After every implementation session, ARIA documentation must be updated before starting the next build phase.

No new build phase begins until:

1. The source-of-truth AI Mentor status document reflects the deployed state.
2. `ROADMAP.md` reflects the current phase status.
3. Any workflow/domain distinction is clearly documented.
4. Any future ideas are placed in markdown planning docs instead of being implemented ad hoc.
5. Any knowledge-base source documentation change is followed by KB rebuild validation when appropriate.

---

## Domain Balance Rule

ARIA must continue building across all five training domains:

1. Help Desk / Ticketing
2. Networking / Cisco / DNS / VLAN / Switching
3. Security / SOC / Wazuh / Incident Review
4. Automation / SysAdmin / Linux / Proxmox / Field-Tech
5. Identity / IAM / Active Directory / GPO / Windows Endpoint Administration

No new phase should deepen only one domain at the expense of the others.

Any improvement, suggestion, or future enhancement that is not part of the active approved phase must be documented in a markdown planning document instead of being implemented immediately.

The purpose of ARIA is to build a training platform. Infrastructure, services, and mentor features should exist to support directed, mentored, hands-on learning across the five domains.

---

## Executive Summary

The AI Mentor is the coaching layer for all ARIA training, not only help desk ticketing.

The long-term scope includes Field Tech Foundation, Help Desk Documentation, Linux and Security Foundation, Network Troubleshooting, Cybersecurity Readiness Labs, Active Directory, GPO, Windows endpoint administration, Cisco, Proxmox, SIEM, documentation coaching, and interview preparation.

Current reality after Phase 13:

- The AI Mentor platform foundation is live on ARIA.
- Help Desk / Ticketing is complete for v1.
- Zammad/help desk ticketing is the strongest current domain.
- Ticket-001 through Ticket-010 mentor workflows are implemented.
- The student-facing mentor panel is implemented.
- Instructor progress summary API is implemented.
- Audit/event logging is implemented.
- Ticket lab template system is implemented.
- Student assignment model is implemented.
- Instructor review queue is implemented.
- Controlled one-time Zammad writeback is implemented with instructor approval, duplicate-writeback blocking, local completion, and audit hash logging.
- The service uses repo-grounded knowledge retrieval from JSONL chunks.
- ChromaDB/vector DB is deferred and not blocking v1.
- Zammad integration remains read-only and instructor-mediated.
- LLM integration is implemented as an assistive layer, but the provider is disabled until explicitly enabled.
- Auth and role separation v1 are implemented.
- Not all underlying domain infrastructure is operational yet.

Important distinction:

> Workflow implemented does not always mean the full domain is operational.

Example:

> Ticket-010 Wazuh Alert Investigation workflow exists, but Wazuh infrastructure is not deployed yet.

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
| Audit/event logging | Live | Login, protected access, mentor usage, student/instructor panel access, and related events are recorded |
| Zammad read-only API | Live | Ticket read, article read, ticket lookup by visible ticket number |
| Instructor panel | Live | `/instructor`; protected by local auth; read-only review of Zammad ticket + mentor guidance |
| Student panel | Live | `/student`; protected by local auth; student-facing mentor guidance |
| Progress summary API | Live | `/progress/summary`; admin/instructor only; summarizes latest student status by ticket |
| Ticket lab template system | Live | Template matching and required-evidence guidance for Ticket-001 through Ticket-010 |
| Assistive LLM layer | Built, disabled | `/llm/status` and LLM guidance endpoints exist; provider remains disabled until explicitly enabled |
| Auth + role separation | Live v1 | Local users, signed HTTP-only cookie, admin/instructor/student/viewer role separation |

---

## Intentionally Deferred

| Item | Status | Reason |
|---|---|---|
| ChromaDB / vector DB | Deferred | JSONL retrieval is sufficient for v1 validation; vector DB will return when retrieval complexity requires it |
| Zammad webhook automation | Deferred | Current model is read-only/instructor-mediated to reduce risk |
| Controlled Zammad writeback | Complete | Instructor-approved one-time note writeback is implemented. ARIA does not auto-post, auto-close, change priority, or change Zammad ticket state. Duplicate writeback is blocked locally. |
| LLM live provider use | Disabled | Provider switch remains off even if an API key exists; deterministic mentor output remains authoritative |
| Field-to-Cyber lab submission model | Pending | Needs a lab completion review workflow distinct from break/fix help desk tickets |
| Active Directory / GPO / Windows endpoint mentor workflows | Pending | Core training domain; simple VM-based AD/GPO lab must be built |
| Full SIEM/Wazuh infrastructure | Pending | Ticket-010 workflow exists, but Wazuh LXC and agents are not deployed yet |

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
| 8 | Audit/event logging | Complete |
| 9 | Ticket lab template system | Complete |
| 10 | Implement Ticket-001 through Ticket-005 mentor workflows | Complete |
| 11 | Student-facing mentor panel v1 | Complete |
| 12 | Implement Ticket-006 through Ticket-010 mentor workflows | Complete |
| 13 | Instructor progress summary API | Complete |
| 14 | Controlled Zammad writeback / instructor approval workflow | Complete |
| 15 | Operational hardening | Pending |

---

## Training Domain Status

| Training Domain | Current Status | Implemented So Far | Next Required Work |
|---|---|---|---|
| Help Desk / Ticketing | Complete v1 | Zammad, help desk workflow, instructor panel, student panel, Ticket-009 workflow, session logging, audit logging, progress summary API, read-only Zammad integration, student assignment model, instructor review queue, controlled one-time Zammad writeback | Domain complete for v1. Do not add more Help Desk features until other domains catch up unless the work is shared platform infrastructure. |
| Networking / Cisco / DNS / VLAN / Switching | Workflow coverage started; infrastructure is mature | Ticket-001 DNS, Ticket-002 VLAN, Ticket-004 Cisco SSH, Ticket-005 return path/routing, Ticket-007 VLAN 70 migration | Create dedicated network lab path with show-command evidence, risk, rollback, and Cisco guardrail enforcement |
| Security / SOC / Wazuh / Incident Review | Workflow prepared; infrastructure pending | Ticket-010 Wazuh Alert Investigation workflow and security-triage evidence model | Deploy Wazuh LXC, agents, alert sources, and real SOC lab events |
| Automation / SysAdmin / Linux / Proxmox / Field-Tech | Complete v1 | Proxmox, student Linux container, Ticket-003, Ticket-006, Ticket-008, Linux lab submissions, Field-Tech Lab 001/002 submissions, Automation/IaC submissions, Ansible/Netmiko submissions, RESTCONF submissions, runbook-writing submissions, instructor review, audit logging | Domain complete for v1. Keep stable and avoid adding new scope until the remaining domains catch up. |
| Identity / IAM / Active Directory / GPO / Windows Endpoint Administration | Core domain; not implemented yet | Planning only; local app roles are not a substitute for AD/GPO training | Build simple VM-based AD/GPO lab: Windows Server DC, Windows client, domain join, users, groups, OUs, GPOs, and troubleshooting labs |

---

## Cross-Environment Coverage Status

| Training Environment / Domain | Current Status | Next Required Work |
|---|---|---|
| Help Desk / Zammad | Complete v1 | Keep stable. Controlled writeback is limited to one instructor-approved note. No auto-close, priority change, or ticket-state change by ARIA. |
| DNS / Pi-hole | Ticket workflow implemented | Add real student lab evidence path and domain-specific progress tracking |
| VLAN / Switching | Ticket workflow implemented | Add Cisco/switching lab evidence model |
| Linux / Proxmox | Complete v1 foundation | Non-Zammad Linux lab submission and instructor completion tracking are implemented. Future expansion should follow the documented lab path. |
| Cisco / SSH / Switching | Ticket workflow implemented | Add strict Cisco config-change guardrail workflow |
| WiFi / UniFi | Ticket workflow implemented where mapped | Validate AP/SSID evidence model when WiFi labs expand |
| Proxmox recovery / hardware operations | Ticket workflows implemented | Expand into field-tech and operational recovery labs |
| SIEM / Wazuh | Ticket workflow implemented; infrastructure pending | Deploy Wazuh workload, agents, and real alert-generation labs |
| Active Directory / GPO / Windows Endpoint Administration | Planned core domain; not implemented | Deploy simple AD/GPO VM lab and create evidence templates |
| Field Tech Foundation Labs | Instructor notes exist | Design lab completion ticket/submission workflow distinct from break/fix tickets |
| Cybersecurity Readiness Labs | Planned | Requires Wazuh/SIEM workload and incident-review templates |

---

## Active Directory / GPO Domain Requirement

Active Directory and GPO are part of the original ARIA training mission and must remain visible in the core plan.

This domain can begin with a simple VM-based lab:

- One Windows Server VM as the Domain Controller
- One Windows client VM joined to the domain
- A test domain such as `jlm.lab`
- OUs for Students, Workstations, Help Desk, Disabled Users, and Admin Testing
- Test users, groups, and security roles
- Foundational GPOs for password policy, account lockout, login banner, mapped resources, local administrator restrictions, desktop controls, and Windows security settings

Initial AD/GPO training scenarios should include:

- User cannot log in
- Account locked out
- Password expired or reset required
- User placed in wrong group
- User missing access due to group membership
- Computer cannot join the domain
- DNS misconfiguration preventing domain join
- GPO not applying
- Wrong OU placement
- Local admin rights incorrectly assigned
- Login banner or desktop policy not applying
- Basic Windows endpoint support ticket requiring AD verification

The AI Mentor should guide AD/GPO troubleshooting by requiring evidence such as screenshots, ADUC state, Group Policy Management state, `gpresult`, `rsop.msc`, Event Viewer logs, DNS checks, and professional resolution summaries.

---

## Help Desk / Ticketing Domain Closeout

Help Desk / Ticketing is complete for v1.

Completed capabilities:

- Zammad deployed on CT 110
- Help desk ticketing workflow validated
- Instructor panel live
- Student-facing mentor panel live
- Ticket-009 Zammad triage workflow validated
- Session logging
- Audit logging
- Progress summary API
- Read-only Zammad integration
- Student assignment model
- Instructor review queue
- Controlled Zammad writeback / instructor approval workflow
- Local assignment completion after successful writeback
- Duplicate writeback protection
- Audit event with payload hash
- No Zammad ticket closure, priority change, or state change by ARIA

Controlled writeback boundary:

- ARIA may write one instructor-approved note/article to the linked Zammad ticket.
- ARIA must not automatically post AI-generated comments.
- ARIA must not close tickets.
- ARIA must not change ticket priority.
- ARIA must not change Zammad ticket state.
- ARIA must mark the local assignment completed after successful writeback so the instructor review job is not repeated.
- ARIA must block duplicate writeback for already approved/completed assignments.
- ARIA must log instructor identity, assignment ID, ticket ID, timestamp, Zammad article ID, and payload hash.

Assessment:

Help Desk / Ticketing is ahead of the other domains and should not receive another major build phase until the other domains catch up, unless the work is shared platform infrastructure.


---

## Automation / SysAdmin / Linux / Proxmox / Field-Tech Domain Closeout

Automation / SysAdmin / Linux / Proxmox / Field-Tech is complete for v1.

Completed capabilities:

- Proxmox host live
- Student Linux container model exists
- CT 102 student-linux-01 deployed
- Student SSH access validated
- Scoped sudo validated
- Ticket-003 Proxmox APT workflow
- Ticket-006 Proxmox repository hygiene workflow
- Ticket-008 Comet ATX reset validation workflow
- Non-Zammad lab submission model
- Linux Foundation lab submission template
- Field-Tech Lab 001 endpoint identity submission template
- Field-Tech Lab 002 endpoint health check submission template
- Automation/IaC foundation submission template
- Automation script review submission template
- Network Automation Lab 004 Ansible/Netmiko submission template
- Network Automation Lab 005 RESTCONF submission template
- Runbook Writing Foundation submission template
- Existing Runbook Review submission template
- Student lab submission endpoint
- Student personal lab submission history endpoint
- Instructor lab submission review endpoint
- Instructor lab completion/status update endpoint
- Audit events for lab submission creation
- Audit events for lab submission status updates

Validated v1 submission categories:

- Linux
- Field-Tech
- Automation/IaC
- Network Automation
- Ansible / Netmiko
- RESTCONF
- Runbook-writing
- Existing runbook review

Completion boundary:

- This domain is complete for v1 because students can submit direct non-Zammad evidence and instructors can review, complete, and audit Linux, Field-Tech, Automation/IaC, Ansible/Netmiko/RESTCONF, and runbook-writing work.
- Future expansion should add deeper labs from `docs/domain-plans/automation-sysadmin-linux-fieldtech-lab-path.md`.
- Do not add additional Automation / SysAdmin / Linux / Field-Tech scope until the remaining domains catch up unless the work is shared platform infrastructure.


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

## Next Domain Priority

Before any Help Desk-only enhancement, choose the next missing-domain milestone.

Recommended next-domain priorities:

1. Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
   - Build simple VM-based AD/GPO lab.
   - Create initial evidence templates.
   - Add AD/GPO mentor workflows after the lab exists.

2. Security / SOC / Wazuh / Incident Review
   - Deploy Wazuh LXC and agents.
   - Generate real alert examples.
   - Connect Ticket-010 workflow to real evidence.

3. Automation / SysAdmin / Linux / Proxmox / Field-Tech
   - Complete v1.
   - Non-Zammad lab submission model implemented.
   - Linux, Field-Tech, Automation/IaC, Ansible/Netmiko/RESTCONF, and runbook-writing submissions are connected to progress tracking.

No next build phase should proceed until the roadmap is reviewed against the Domain Balance Rule.

---

## Required Before Next Build Phase

Before the next implementation phase begins:

- Confirm Phase 13 is complete and documented.
- Confirm `ROADMAP.md` Phase AI status is updated.
- Rebuild the AI Mentor KB if documentation changes are intended to be available to mentor retrieval.
- Select the next phase based on domain balance, not convenience.
- Document any out-of-scope ideas in markdown instead of implementing them ad hoc.

