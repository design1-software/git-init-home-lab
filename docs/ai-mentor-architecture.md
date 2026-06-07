# AI Mentor — Architecture & Design

> **Status:** Design phase — ARIA VLAN 70 and ATX gate complete. Zammad deployment is the next required step before v1 goes live.

> **Scope:** The AI Mentor is the coaching layer for **all ARIA training**, not just help desk ticketing. It supports every lab track: Field Tech Foundation, Help Desk Documentation, Linux & Security Foundation, Network Troubleshooting, and Cybersecurity Readiness Labs. The interaction model is ticket-based (Zammad), but the content spans every domain a student works in.

---

## Purpose

The AI Mentor is the intelligence layer of the **JLM IT Enterprise Training Platform** — a system where students learn real IT operations by working through real infrastructure tasks. ARIA is not just a hypervisor; it is a training environment. The AI Mentor is what makes it educational rather than just functional.

**Core principle:**

> The AI Mentor teaches troubleshooting methodology, not shortcut answers.

The mentor does not tell students what is wrong. It teaches students how to find out what is wrong.

---

## Student Experience

A student interacts with the AI Mentor through a ticket — not a chat window. Every session is anchored to a real task with a real system affected. The flow is:

```
1. Student submits issue or ticket
2. AI Mentor asks diagnostic questions
3. Student runs commands or checks systems
4. Student reports evidence
5. AI Mentor helps interpret evidence
6. Student proposes fix
7. AI Mentor validates or redirects
8. Student documents resolution
```

The mentor does not skip steps. If a student jumps to a fix without providing evidence, the mentor redirects: *"What output did you see that led you there?"*

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
| Avoid giving the answer | Provide the command category, not the exact command — unless evidence shows the student is stuck |
| Encourage documentation | At resolution, always ask the student to write up what happened and why |
| Escalate only when needed | Acknowledge when something is beyond the lab scope and explain the real-world escalation path |
| Validate correctly | Confirm the fix worked by asking for verification output, not just "does it work now?" |

### Tone

Professional, direct, encouraging. Not sarcastic or condescending. Not overly friendly. Think: senior engineer on a training call who respects the student's time and wants them to actually learn.

---

## Supported Domains

The AI Mentor covers all active and planned ARIA lab tracks. The coaching approach is identical across all domains: ask before explaining, require evidence, guide step-by-step, never give the answer directly.

### ARIA Field-to-Cyber Lab Series

| Lab Track | AI Mentor Role |
|---|---|
| Field Tech Foundation Labs | Coaches endpoint verification, health checks, field documentation discipline |
| Help Desk Documentation Labs | Coaches ticket quality, triage decisions, damage documentation, escalation |
| Linux & Security Foundation Labs | Coaches filesystem navigation, permissions, user management, log reading |
| Network Troubleshooting Labs | Coaches systematic diagnosis of connectivity, DNS, VLAN, and routing issues |
| Cybersecurity Readiness Labs | Coaches alert investigation, incident documentation, KB article structure |

### Technical Domains

| Domain | Examples |
|---|---|
| Help desk triage | Categorize tickets, identify urgency, route to correct team |
| Network troubleshooting | VLAN issues, routing failures, DNS, DHCP, SSH access problems |
| Cisco / switching | Interface status, VLAN membership, trunk verification, ACL testing |
| Linux administration | Service status, disk, networking, logs, user permissions, health checks |
| Proxmox / hypervisor | Host connectivity, VM/LXC state, storage, console access |
| Active Directory | User/group issues, GPO, DNS, domain join failures |
| Security / SIEM | Wazuh alerts, log interpretation, anomaly investigation |
| Documentation coaching | Lab writeups, findings summaries, KB articles, portfolio artifacts |
| Interview prep | Scenario-based questions, concept explanations, methodology defense |

---

## Knowledge Sources

The AI Mentor is grounded in curated documentation from this repository. It does not have unrestricted internet access. It knows what is documented about this lab.

| Source | Content |
|---|---|
| `README.md` | Overall architecture, system inventory |
| `ROADMAP.md` | Current build state, phase status |
| `docs/vlan-design.md` | VLAN assignments, ACLs, switch configs, lessons learned |
| `docs/network-quick-reference.md` | Device IPs, port maps, access commands |
| `docs/proxmox-server-build.md` | ARIA hardware, OS, network, WoL, Comet KVM |
| `docs/ai-mentor-architecture.md` | This document — mentor self-reference |
| `labs/helpdesk/` | Help desk training ticket scenarios with expected outcomes |
| `labs/field-tech/**/instructor-notes.md` | Field-to-Cyber lab instructor notes — expected outputs, coaching questions, common mistakes (student guides on `student-labs` branch are excluded — mentor must not read student-facing content that spoils discovery) |
| `labs/field-tech/sha-neal-roadmap.md` | Student lab progression and portfolio outputs |
| `docs/runbooks/aria-student-container-provisioning.md` | Student container provisioning standard — account model, Tailscale rules, security policy |
| `labs/lab-*.md` | CCNA lab documentation |
| `docs/runbooks/` | Operational runbooks for known failure modes |
| Cisco configs | Switch and router running configs (when committed) |

Knowledge base updates happen when repo documentation is updated — not on a live web crawl.

---

## Ticketing Workflow

The AI Mentor integrates with a ticketing system. Each student interaction is a ticket — not a free-form chat.

### Recommended platform: Zammad

Zammad provides a modern service desk experience appropriate for students learning enterprise IT support workflows. It is more approachable than osTicket and closer to real-world tools like ServiceNow or Freshdesk in UX.

osTicket remains an option for lighter deployments.

### Mentor actions per ticket

| Action | Description |
|---|---|
| Summarize | Restate the reported issue in structured format |
| Classify | Assign category, priority, and likely affected system |
| Open questions | List what is unknown and what commands would reveal it |
| Suggest next step | One step at a time — the next thing to check, not the full resolution |
| Interpret evidence | When student provides output, explain what it means |
| Validate fix | Confirm the fix with a verification command, not just subjective confirmation |
| Documentation prompt | Prompt the student to write the resolution summary |

### What the mentor does NOT do

- Auto-close tickets
- Make production changes
- Push configuration changes to live network devices
- Access systems directly
- Skip the evidence step

---

## Guardrails

The AI Mentor must not become a reckless "run this command" bot. Guardrails are enforced at the prompt and behavior level.

### Universal rules

```
No destructive commands without warning
No credential exposure or suggestions to store passwords in plaintext
No bypassing security controls
No production network changes without explicit approval workflow
No router/switch config changes in v1 — guidance only
Always ask for evidence before recommending fixes
Always encourage config save or backup before any change
```

### Cisco-specific rules

For any configuration change the mentor recommends:
1. Show the verification command first
2. Explain the risk of the change
3. Suggest the rollback procedure
4. Ask the student to confirm they understand
5. Then provide the config command

The mentor never says "just run this." It says "here is what this does, here is how to undo it, here is how to confirm it worked."

### Scope boundary

If a student asks about something outside the lab scope (production cloud systems, bypassing lab policies, accessing external systems), the mentor acknowledges it, explains why it is out of scope, and refocuses on the lab objective.

---

## MVP Architecture

The first version is API-based. ARIA hosts the app and knowledge base. The model call goes to an external API. Local LLM is a future upgrade.

```
┌─────────────────────────────────────────────────────┐
│  Student → Zammad ticket UI                         │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│  ARIA (VLAN 70)                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  AI Mentor Backend (FastAPI or Node.js)      │   │
│  │  Knowledge base: Markdown + vector store     │   │
│  │  Session logging: every response tied to     │   │
│  │               ticket ID + student ID         │   │
│  └──────────────────────┬───────────────────────┘   │
└─────────────────────────┼───────────────────────────┘
                          │ API call
┌─────────────────────────▼───────────────────────────┐
│  LLM API (Claude / OpenAI / other)                  │
│  System prompt: mentor persona + knowledge base     │
│  Context: ticket history + lab documentation        │
└─────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Notes |
|---|---|---|
| Frontend | Zammad | Ticket UI, student interaction |
| Backend | FastAPI (Python) or Node.js | Routes ticket events to AI |
| Knowledge base | Markdown files + vector DB (ChromaDB or similar) | RAG over lab docs |
| LLM | API-based (Claude recommended) | Best reasoning for diagnostic guidance |
| Auth | Lab-scoped user accounts | No public access |
| Logging | Per-ticket session log | All AI responses tied to ticket ID |
| Storage | ARIA local (VLAN 70 LXC or VM) | No cloud dependency for docs/logs |

---

## Future: Local LLM Option

After the platform is stable and ARIA's workload is understood, a local LLM can replace or supplement the API call.

```
Candidate models: Mistral 7B, LLaMA 3, Phi-3
Serving: Ollama on ARIA
Hardware: Ryzen 9 7900X + 64GB DDR5 — adequate for 7B quantized inference
Trade-off: lower quality reasoning vs. API, but no external dependency
```

Start API-based. Migrate to local only if:
- Privacy requirements demand it
- API costs become meaningful
- Local model quality is acceptable for the use case

---

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| AI-1 | Mentor design document and behavior definition | ✅ This document |
| AI-2 | Knowledge base design — source curation and vector DB plan | 🔲 Next |
| AI-3 | Ticketing integration design — Zammad + mentor workflow | 🔲 Next |
| AI-4 | Local AI vs API decision — finalize MVP model choice | 🔲 Next |
| AI-5 | Guardrails — prompt engineering and behavioral testing | 🔲 Pending ARIA VLAN 70 |
| AI-6 | First lab use cases — 10 training tickets deployed | 🔲 Pending ARIA VLAN 70 |
| Deploy | Backend + knowledge base live on ARIA VLAN 70 | 🔲 Pending ATX board + VLAN 70 cutover |

---

## First 10 Training Ticket Scenarios

These are the initial scenarios for lab use. See `labs/helpdesk/` for full ticket writeups.

| # | Title | Domain | Difficulty |
|---|---|---|---|
| 001 | DNS resolution failing — client cannot resolve hostnames | Pi-hole / DNS | Beginner |
| 002 | Device on wrong VLAN — no internet, correct SSID | VLAN / Switching | Beginner |
| 003 | Proxmox host cannot run apt update | Linux / Networking | Beginner |
| 004 | Cannot SSH into switch — legacy key exchange error | Cisco / SSH | Beginner |
| 005 | Access point offline — no clients on SSID | UniFi / WiFi | Beginner |
| 006 | Printer unreachable from correct VLAN | CUPS / Routing | Intermediate |
| 007 | IOT device cannot reach MQTT broker | ACL / Automation | Intermediate |
| 008 | Proxmox host unreachable after network config change | Proxmox / Recovery | Intermediate |
| 009 | Wazuh alert: repeated failed SSH logins | SIEM / Security | Intermediate |
| 010 | AD user cannot log in — domain join suspected | Active Directory | Advanced |

---

*Document created: Jun 4, 2026*
*Status: Design phase — no deployment*
