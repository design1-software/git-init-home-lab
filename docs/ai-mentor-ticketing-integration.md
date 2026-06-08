# AI Mentor — Ticketing Integration Design

> **Status:** Implemented as read-only instructor-mediated v1 on Jun 8, 2026. Zammad and AI Mentor are connected through read-only API calls and the instructor panel. Webhook automation and Zammad writeback remain deferred.

> **Source of truth for implementation status:** `docs/ai-mentor-implementation-status.md`

---

## Zammad Role in the Training Platform

Zammad is the entry point for help desk and ticket-based student interactions. It is not just a ticket tracker — it is the structured interface through which students report problems, submit evidence, and document resolutions.

The AI Mentor is intentionally aligned to ticket workflow because this mirrors real enterprise IT support operations.

**Zammad's role:**

- Receives student-submitted tickets
- Maintains ticket history, evidence submissions, and resolution notes
- Provides instructor/admin visibility into student work
- Tracks ticket state through the learning workflow
- Serves as the system of record for the help desk/ticketing track

**AI Mentor's current v1 role:**

- Reads Zammad ticket metadata through the API
- Reads ticket articles/comments through the API
- Looks up tickets by visible Zammad ticket number
- Generates deterministic mentor guidance in the instructor panel
- Optionally displays assistive LLM wording when provider is enabled
- Logs mentor sessions locally
- Does not write back to Zammad

---

## Current v1 Integration Model

Current v1 is **read-only and instructor-mediated**.

```text
Instructor / Admin
       |
       v
/instructor panel
       |
       v
AI Mentor Backend CT 120
       |
       | read-only Zammad API
       v
Zammad CT 110
```

Implemented endpoints include:

| Endpoint | Purpose |
|---|---|
| `GET /zammad/tickets/by-number/{ticket_number}` | Resolve visible Zammad ticket number to ticket data |
| `GET /zammad/tickets/{ticket_id}` | Read Zammad ticket by internal ID |
| `GET /zammad/tickets/{ticket_id}/articles` | Read ticket articles |
| `POST /mentor/zammad/ticket-number/{ticket_number}/draft-guidance` | Generate deterministic guidance from a Zammad ticket |
| `POST /mentor/zammad/ticket-number/{ticket_number}/llm-guidance` | Generate assistive LLM-enhanced wording if provider is enabled |

---

## Ticket Lifecycle

The target training lifecycle remains:

```text
[1] Student opens ticket
        ↓
[2] AI Mentor reads ticket + surfaces relevant repo docs internally
        ↓
[3] AI Mentor produces clarifying questions + evidence checklist
        ↓
[4] Mentor response presented in draft panel / instructor panel
        ↓
[5] Student performs work (runs commands, checks systems)
        ↓
[6] Student updates ticket with evidence output
        ↓
[7] AI Mentor reviews evidence, guides next step or validates fix
        ↓
[8] Student applies fix or completes lab requirement
        ↓
[9] Student runs verification commands
        ↓
[10] AI Mentor prompts documentation writeup
        ↓
[11] Student writes closure summary
        ↓
[12] Instructor validates training completion
```

The mentor does not skip steps. If a student attempts to jump to resolution without evidence, the mentor redirects to evidence collection.

---

## AI Mentor Interaction Points

The AI Mentor acts at four defined points in the lifecycle:

| Point | Trigger | AI Action | v1 Status |
|---|---|---|---|
| Ticket opened | New ticket submitted | Read ticket, surface relevant docs, generate clarifying questions + evidence checklist | Manual via instructor panel |
| Evidence submitted | Student updates ticket with command output | Interpret evidence, guide next step or identify root cause | Manual via instructor panel |
| Fix proposed | Student states intended fix | Validate logic, surface risk warnings, prompt rollback consideration | Planned |
| Ticket closed / completed | Student submits closure summary | Review summary quality, prompt missing sections if incomplete | Implemented for Ticket-009 completion detection |

The AI Mentor does not respond unprompted between these points in v1.

---

## Student Workflow

Target help desk workflow:

```text
1. Open Zammad account using lab credentials
2. Submit or receive a training ticket
3. Read instructor/mentor guidance when provided
4. Run requested commands or checks
5. Update ticket with exact command output or evidence
6. Read mentor interpretation or instructor feedback
7. Propose a fix or completion summary
8. Apply approved fix or complete lab task
9. Run verification commands/checks
10. Update ticket with verification output
11. Write closure summary when prompted
12. Instructor validates completion
```

Students are expected to paste raw evidence, not summaries. "It worked" is not evidence. "Success rate is 100 percent (5/5)" is evidence.

---

## Instructor / Admin Workflow

| Task | Current v1 Method |
|---|---|
| Create training tickets | Pre-load or manually create from `labs/helpdesk/ticket-*.md` scenarios |
| Assign tickets to students | Zammad assignment or manual process |
| Review mentor guidance | `/instructor` panel |
| Review session logs | Local session records; audit/event logging pending |
| Monitor mentor behavior | Retrieved sources and guidance shown in panel |
| Override AI guidance | Instructor posts direct Zammad comment manually |
| Mark training complete | Instructor decision; AI Mentor can indicate `validation_complete` |
| Export progress | Pending instructor review queue / reporting phase |

The instructor has access to mentor context and retrieved sources. Students should not receive mentor-only diagnostic paths or full runbook answers.

---

## Ticket Metadata Fields

The planned structured metadata model remains useful for future workflow expansion.

| Field | Values | Purpose | v1 Status |
|---|---|---|---|
| `ticket_type` | training / incident / lab | Determines AI behavior mode | Planned |
| `domain` | dns / vlan / cisco / linux / proxmox / ad / siem / other | Scopes doc retrieval | Inferred from content for now |
| `difficulty` | beginner / intermediate / advanced | Adjusts mentor verbosity | Passed in request model |
| `lab_ticket_id` | 001–010+ or null | Links to scenario file | Manual/inferred |
| `student_id` | lab username | Session scoping | Partial |
| `evidence_submitted` | yes / no | Tracks whether student has provided output | Planned |
| `mentor_session_id` | UUID | Ties AI responses to a session log | Implemented |

---

## AI Response Format

Every AI Mentor response follows a consistent structure:

```text
--- ARIA Mentor ---

Situation Summary:
[One sentence confirming what was reported or validated]

Source Context Used:
[Retrieved docs/chunks]

What I need to see / Validation Observed:
[Evidence checklist or completion observations]

Why this matters:
[Brief explanation if needed]

Next Step:
[One specific next action]

--- End ---
```

The AI Mentor asks for evidence before explanation. It does not write long explanations before establishing what the student has actually observed.

---

## Escalation Rules

| Condition | AI Response |
|---|---|
| Issue involves a system not in the lab | Acknowledge, explain out of scope, redirect to lab boundary |
| Student is stuck after repeated guidance | Suggest instructor review; do not give the full answer |
| Issue requires production change approval | State approval requirement; do not provide unsafe config path |
| Student reports safety concern | Escalate immediately to instructor; suspend guidance |
| Ticket is ambiguous after clarification | Request a more specific symptom/evidence update |

---

## What the AI Can and Cannot Write Back to Zammad

### v1 — Read-Only Instructor Panel Model

In v1, the AI Mentor does not post directly into the ticket thread. It produces guidance in the instructor panel. The instructor may manually copy approved guidance into Zammad if appropriate.

| AI can | AI cannot |
|---|---|
| Read ticket data | Auto-post into ticket comments |
| Read ticket articles | Change ticket priority |
| Generate clarifying questions | Close tickets |
| Produce evidence checklists | Assign tickets to users |
| Interpret evidence | Perform actions on lab systems |
| Surface risk warnings | Expose mentor-only solution notes to students |
| Prompt closure summaries | Bypass instructor review |
| Log session data internally | Write to Zammad without approval/audit |

### Future v2 — Webhook / Writeback Model

After v1 is validated, the AI Mentor may post structured responses as internal notes through the Zammad API, but only after audit logging, rate limiting, and instructor approval workflow exist.

Required before v2:

- Audit/event logging
- Zammad API write token scoped to an AI Mentor service account
- Rate limiting on every write-capable endpoint
- Instructor approval flow
- Rollback procedure for incorrect AI responses
- Validation against all guardrail deployment tests

---

## Deployment Architecture

Current deployment:

```text
ARIA VLAN 70

CT 110: Zammad
  - Docker Compose
  - PostgreSQL
  - Internal HTTP v1
  - helpdesk.aria.local

CT 120: AI Mentor Backend
  - FastAPI
  - systemd service
  - JSONL KB retrieval
  - Local auth/roles
  - Session logging
  - Instructor panel
  - Assistive LLM layer disabled by default
```

Zammad and the AI Mentor backend run as separate LXC containers on ARIA VLAN 70. They communicate internally across the ARIA network. No public exposure is intended.

---

## Security Notes

| Control | Implementation |
|---|---|
| Zammad access | Lab credentials only; internal-only access |
| AI Mentor panel | Local auth + role separation v1 |
| AI Mentor API calls | Protected by role dependencies for Zammad/LLM endpoints |
| LLM API key | Stored in `.env`; not committed; provider disabled until explicitly enabled |
| Session logs | Stored locally on ARIA |
| Student cannot see mentor-only content | Enforced by workflow and future retrieval separation; student panel pending |
| Zammad DB | Local PostgreSQL on ARIA; app-level backup exists separately |

---

## Deployment Gate Status

Original gate items have changed status:

```text
[x] ATX board installed and validated
[x] ARIA migrated to VLAN 70
[x] Proxmox vmbr0 stable
[x] Zammad LXC deployed
[x] AI Mentor backend LXC deployed
[x] KB ingestion tested with JSONL retrieval
[x] Read-only Zammad integration tested
[x] Instructor panel deployed
[x] Auth + role separation v1 deployed
[ ] Audit/event logging
[ ] Full 8-test guardrail deployment validation recorded
[ ] Ticket-001 through Ticket-010 workflows implemented and validated
[ ] Webhook/writeback approval workflow, if approved later
```

---

*Document reconciled: Jun 8, 2026*
