# AI Mentor — Architecture & Design

> **Status:** Implemented foundation on ARIA as of Jun 8, 2026. Zammad and the AI Mentor backend are deployed. JSONL retrieval is live for v1. ChromaDB/vector DB, webhook automation, Zammad writeback, and cross-domain mentor workflows remain deferred.

> **Source of truth for implementation status:** `docs/ai-mentor-implementation-status.md`

> **Scope:** The AI Mentor is the coaching layer for **all ARIA training**, not just help desk ticketing. It supports every lab track: Field Tech Foundation, Help Desk Documentation, Linux & Security Foundation, Network Troubleshooting, and Cybersecurity Readiness Labs. The current working implementation is ticket-based through Zammad, but the long-term content scope spans every domain a student works in.

---

## Governance Rule

The documented plan must be followed.

Any ad hoc change must be explicitly approved before implementation and must include:

1. Reason for the deviation
2. Risk introduced by the deviation
3. Expected benefit
4. Rollback path
5. Required repository documentation update

---

## Purpose

The AI Mentor is the intelligence layer of the **JLM IT Enterprise Training Platform** — a system where students learn real IT operations by working through real infrastructure tasks. ARIA is not just a hypervisor; it is a training environment. The AI Mentor is what makes it educational rather than just functional.

**Core principle:**

> The AI Mentor teaches troubleshooting methodology, not shortcut answers.

The mentor does not tell students what is wrong. It teaches students how to find out what is wrong.

---

## Current Implementation State

| Component | Status | Notes |
|---|---|---|
| Zammad | Live | CT 110 `aria-zammad-01`; Docker Compose; `helpdesk.aria.local`; admin/student workflow validated |
| AI Mentor backend | Live | CT 120 `aria-ai-mentor-01`; FastAPI; systemd; local session logging |
| Knowledge base ingestion | Live | Approved repo docs chunked to JSONL |
| Retrieval layer | Live v1 | JSONL lexical/scored retrieval; ChromaDB deferred |
| Instructor panel | Live | `/instructor`; protected by auth; read-only Zammad review |
| Zammad integration | Live read-only | Ticket lookup, article fetch, visible ticket-number lookup |
| LLM layer | Built, disabled | Assistive-only; deterministic mentor output remains authoritative |
| Auth/roles | Live v1 | Admin/instructor protected routes via local auth |

---

## Student Experience

A student interacts with the AI Mentor through a ticket or training submission — not an unrestricted chat window. Every session is anchored to a real task with a real system affected.

The core flow is:

```text
1. Student submits issue, lab evidence, or ticket
2. AI Mentor asks diagnostic or completion-review questions
3. Student runs commands or checks systems
4. Student reports evidence
5. AI Mentor helps interpret evidence
6. Student proposes fix or completion summary
7. AI Mentor validates or redirects
8. Student documents resolution or portfolio output
```

The mentor does not skip steps. If a student jumps to a fix without providing evidence, the mentor redirects: "What output did you see that led you there?"

---

## Mentor Behavior

The AI Mentor behaves as a virtual senior engineer running a training session — patient, precise, and unwilling to hand-hold beyond what develops skill.

| Behavior | Description |
|---|---|
| Ask before explaining | Always ask what the student has already tried before offering guidance |
| Require evidence | Never accept "I think it's X" — ask for the command output that shows X |
| Guide step-by-step | Break problems into one step at a time, not full resolution paths |
| Explain concepts | When a command is needed, explain why, not just what |
| Challenge assumptions | If the student is headed the wrong direction, ask a question that surfaces the gap |
| Avoid giving the answer | Provide guidance and reasoning prompts, not shortcut answers |
| Encourage documentation | At resolution, always ask the student to write up what happened and why |
| Escalate only when needed | Acknowledge when something is beyond the lab scope and explain the real-world escalation path |
| Validate correctly | Confirm the fix worked by asking for verification output, not just "does it work now?" |

### Tone

Professional, direct, encouraging. Not sarcastic or condescending. Think: senior engineer on a training call who respects the student's time and wants them to actually learn.

---

## Supported Domains

The AI Mentor covers all active and planned ARIA lab tracks. The coaching approach is identical across all domains: ask before explaining, require evidence, guide step-by-step, never give the answer directly.

### ARIA Field-to-Cyber Lab Series

| Lab Track | AI Mentor Role | Current Implementation Status |
|---|---|---|
| Field Tech Foundation Labs | Coaches endpoint verification, health checks, field documentation discipline | Planned; needs lab submission template |
| Help Desk Documentation Labs | Coaches ticket quality, triage decisions, damage documentation, escalation | Operational v1 foundation |
| Linux & Security Foundation Labs | Coaches filesystem navigation, permissions, user management, log reading | Planned via ticket workflows |
| Network Troubleshooting Labs | Coaches systematic diagnosis of connectivity, DNS, VLAN, and routing issues | Planned via ticket workflows |
| Cybersecurity Readiness Labs | Coaches alert investigation, incident documentation, KB article structure | Planned after SIEM/Wazuh workload |

### Technical Domains

| Domain | Examples | Current Status |
|---|---|---|
| Help desk triage | Categorize tickets, identify urgency, route to correct team | Operational foundation |
| Network troubleshooting | VLAN issues, routing failures, DNS, DHCP, SSH access problems | Planned workflows |
| Cisco / switching | Interface status, VLAN membership, trunk verification, ACL testing | Planned workflows |
| Linux administration | Service status, disk, networking, logs, user permissions, health checks | Planned workflows |
| Proxmox / hypervisor | Host connectivity, VM/LXC state, storage, console access | Planned workflows |
| Active Directory | User/group issues, GPO, DNS, domain join failures | Planned; AD lab not deployed |
| Security / SIEM | Wazuh alerts, log interpretation, anomaly investigation | Planned; Wazuh not deployed |
| Documentation coaching | Lab writeups, findings summaries, KB articles, portfolio artifacts | Planned for student panel |
| Interview prep | Scenario-based questions, concept explanations, methodology defense | Future |

---

## Knowledge Sources

The AI Mentor is grounded in curated documentation from this repository. It does not use unrestricted internet access. It knows what is documented about this lab.

Approved knowledge source categories include:

| Source Area | Content |
|---|---|
| `README.md` | Overall architecture, system inventory |
| `ROADMAP.md` | Current build state, phase status |
| `docs/vlan-design.md` | VLAN assignments, ACLs, switch configs, lessons learned |
| `docs/network-quick-reference.md` | Device IPs, port maps, access commands |
| `docs/proxmox-server-build.md` | ARIA hardware, OS, network, WoL, Comet KVM |
| `docs/ai-mentor-*.md` | Mentor behavior, status, guardrails, scope, retrieval rules |
| `labs/helpdesk/` | Help desk training ticket scenarios with expected outcomes |
| `labs/field-tech/**/instructor-notes.md` | Field-to-Cyber lab instructor notes |
| `docs/runbooks/` | Operational runbooks for known failure modes |
| Cisco configs | Switch and router running configs when committed |

Knowledge base updates happen when repo documentation is updated — not on a live web crawl.

---

## Ticketing Workflow

The AI Mentor integrates with Zammad. Each help desk interaction is ticket-based, not free-form chat.

Current v1 implementation is **read-only and instructor-mediated**:

| Implemented | Deferred |
|---|---|
| Read Zammad tickets | Webhook automation |
| Read Zammad articles | Auto-post AI comments |
| Lookup by visible ticket number | Close tickets |
| Generate mentor guidance in instructor panel | Change priority or assignment |
| Record local session logs | Perform actions on lab systems |

### Mentor actions per ticket

| Action | Description |
|---|---|
| Summarize | Restate the reported issue in structured format |
| Classify | Assign category, priority, and likely affected system |
| Open questions | List what is unknown and what evidence would reveal it |
| Suggest next step | One step at a time — the next thing to check, not the full resolution |
| Interpret evidence | When student provides output, explain what it means |
| Validate fix | Confirm the fix with verification evidence |
| Documentation prompt | Prompt the student to write the resolution summary |

### What the mentor does NOT do

- Auto-close tickets
- Make production changes
- Push configuration changes to live network devices
- Access systems directly
- Skip the evidence step
- Override instructor judgment

---

## Guardrails

The AI Mentor must not become a reckless "run this command" bot.

### Universal rules

```text
No destructive commands without warning
No credential exposure or suggestions to store passwords in plaintext
No bypassing security controls
No production network changes without explicit approval workflow
No router/switch config changes without verification, risk, rollback, and confirmation
Always ask for evidence before recommending fixes
Always encourage config save or backup before any change
```

### Cisco-specific rules

For any configuration change the mentor recommends:

1. Show the verification command first
2. Explain the risk of the change
3. Suggest the rollback procedure
4. Ask the student to confirm they understand
5. Then provide the config command only if appropriate for the lab and role

The mentor never says "just run this." It says "here is what this does, here is how to undo it, here is how to confirm it worked."

### Scope boundary

If a student asks about something outside the lab scope, the mentor acknowledges it, explains why it is out of scope, and refocuses on the lab objective.

---

## MVP Architecture

Current v1 architecture:

```text
Student / Instructor
        |
        v
Zammad ticket UI  <----read-only API----  AI Mentor Backend (CT 120)
                                           | FastAPI
                                           | JSONL KB retrieval
                                           | Local session logs
                                           | Auth + role separation
                                           v
                                     Optional LLM API
                                     disabled by default
```

Original design called for ChromaDB. Current implementation uses JSONL retrieval for v1. ChromaDB remains a future upgrade.

### Components

| Component | Technology | Notes |
|---|---|---|
| Ticket UI | Zammad | CT 110, internal-only |
| Backend | FastAPI | CT 120, systemd service |
| Knowledge base | Markdown files + JSONL chunks | ChromaDB deferred |
| LLM | Assistive API layer | Disabled by default; deterministic output authoritative |
| Auth | Local users + signed cookie | Admin/instructor protected routes |
| Logging | Per-session JSON records | Audit/event logging pending |
| Storage | ARIA local | No public exposure |

---

## Future: Local LLM Option

After the platform is stable and ARIA's workload is understood, a local LLM can replace or supplement the API call.

```text
Candidate models: Mistral 7B, LLaMA 3.x 8B, Phi, Qwen
Serving: Ollama on ARIA
Hardware: Ryzen 9 7900X + 64GB DDR5 — adequate for small quantized inference
Trade-off: lower quality reasoning vs. API, but no external dependency
```

Start API-based/assistive. Migrate to local only if privacy, cost, or offline requirements justify the complexity and the model passes guardrail testing.

---

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| AI-1 | Mentor design document and behavior definition | Complete |
| AI-2 | Knowledge base design — source curation and retrieval plan | Complete |
| AI-3 | Ticketing integration design — Zammad + mentor workflow | Complete |
| AI-4 | Local AI vs API decision — finalize MVP model choice | Complete |
| AI-5 | Guardrails — prompt engineering and behavioral testing | Complete |
| AI-6 | First lab use cases — 10 training tickets written | Complete as written scenarios |
| Deploy-1 | Zammad live on ARIA | Complete |
| Deploy-2 | AI Mentor backend live on ARIA | Complete |
| Deploy-3 | KB ingestion and JSONL retrieval | Complete |
| Deploy-4 | Zammad read-only integration + instructor panel | Complete |
| Deploy-5 | Auth + role separation v1 | Complete |
| Next | Audit/event logging | Pending |
| Next | Ticket lab template system | Pending |
| Next | Cross-domain mentor workflows | Pending |

---

## First 10 Training Ticket Scenarios

These are the initial scenarios for lab use. See `labs/helpdesk/` for full ticket writeups.

| # | Title | Domain | Difficulty | Implementation Status |
|---|---|---|---|---|
| 001 | DNS resolution failing — client cannot resolve hostnames | Pi-hole / DNS | Beginner | Scenario written; workflow pending |
| 002 | Device on wrong VLAN — no internet, correct SSID | VLAN / Switching | Beginner | Scenario written; workflow pending |
| 003 | Proxmox host cannot run apt update | Linux / Networking | Beginner | Scenario written; workflow pending |
| 004 | Cannot SSH into switch — legacy key exchange error | Cisco / SSH | Beginner | Scenario written; workflow pending |
| 005 | Access point offline — no clients on SSID | UniFi / WiFi | Beginner | Scenario written; workflow pending |
| 006 | Printer unreachable from correct VLAN | CUPS / Routing | Intermediate | Scenario written; workflow pending |
| 007 | IOT device cannot reach MQTT broker | ACL / Automation | Intermediate | Scenario written; live validation pending |
| 008 | Proxmox host unreachable after network config change | Proxmox / Recovery | Intermediate | Scenario written; live validation pending |
| 009 | Zammad ticket triage / workflow validation | ITSM / Help Desk | Beginner | Implemented and validated |
| 010 | Wazuh alert investigation | SIEM / Security | Intermediate | Scenario written; Wazuh workload pending |

---

*Document reconciled: Jun 8, 2026*
