# AI Mentor — Ticketing Integration Design

> **Status:** Design phase only. No deployment until ATX board installed, Comet hard reset validated, and ARIA on VLAN 70.

---

## Zammad Role in the Training Platform

Zammad is the entry point for every student interaction. It is not just a ticket tracker — it is the structured interface through which students report problems, submit evidence, receive guidance, and document resolutions.

The AI Mentor does not exist in a chat window. It exists inside the ticket. Every mentor response is attached to a ticket and tied to a session record. This is intentional: it mirrors real enterprise IT support workflows, not a consumer chatbot.

**Zammad's role:**
- Receives student-submitted tickets
- Maintains ticket history, evidence submissions, and resolution notes
- Surfaces AI Mentor responses as internal notes or draft comments (not auto-posted in v1)
- Tracks ticket state through the learning workflow
- Provides instructor/admin visibility into all sessions

---

## Ticket Lifecycle

```
[1] Student opens ticket
        ↓
[2] AI Mentor reads ticket + surfaces relevant repo docs internally
        ↓
[3] AI Mentor produces clarifying questions + evidence checklist
        ↓
[4] Mentor response presented in draft panel (not auto-posted in v1)
        ↓
[5] Student reviews, approves, sees guidance
        ↓
[6] Student performs work (runs commands, checks systems)
        ↓
[7] Student updates ticket with evidence output
        ↓
[8] AI Mentor reviews evidence, guides next step or validates fix
        ↓
[9] Student applies fix, confirms resolution
        ↓
[10] AI Mentor prompts documentation writeup
        ↓
[11] Student writes closure summary
        ↓
[12] Ticket closed — session log retained
```

The mentor does not skip steps. If a student attempts to jump from step 6 to step 9 without providing evidence, the mentor redirects at step 8.

---

## AI Mentor Interaction Points

The AI Mentor acts at four defined points in the lifecycle:

| Point | Trigger | AI Action |
|---|---|---|
| Ticket opened | New ticket submitted | Read ticket, surface relevant docs, generate clarifying questions + evidence checklist |
| Evidence submitted | Student updates ticket with command output | Interpret evidence, guide next step or identify root cause |
| Fix proposed | Student states intended fix | Validate logic, surface risk warnings, prompt rollback consideration |
| Ticket closed | Student submits closure summary | Review summary quality, prompt missing sections if incomplete |

The AI Mentor does not respond unprompted between these points.

---

## Student Workflow

```
1. Open Zammad account (lab credentials)
2. Submit a ticket describing the reported issue
   - What is affected
   - What the symptom is
   - What has already been tried (if anything)
3. Read the AI Mentor's clarifying questions
4. Run the requested commands or checks
5. Update the ticket with exact command output (not summaries — paste the output)
6. Read the AI Mentor's interpretation
7. Propose a fix based on the guidance
8. Apply the fix
9. Run verification commands
10. Update the ticket with verification output
11. Write the closure summary when prompted
12. Close the ticket
```

Students are expected to paste raw command output, not summaries. "It worked" is not evidence. "Success rate is 100 percent (5/5)" is evidence.

---

## Instructor / Admin Workflow

| Task | How |
|---|---|
| Create training tickets | Pre-load from `labs/helpdesk/ticket-*.md` scenarios |
| Assign tickets to students | Zammad assignment rules or manual |
| Review session logs | Every AI response stored with ticket ID + timestamp |
| Monitor mentor behavior | Audit log shows what docs were retrieved and what guidance was given |
| Override AI guidance | Admin can post a direct comment overriding the mentor response |
| Mark a ticket as training complete | Separate status field from "resolved" |
| Export session data | For student progress tracking |

The instructor has read access to full mentor reasoning — including the internal doc retrieval that the student cannot see.

---

## Ticket Metadata Fields

Each ticket in Zammad carries structured metadata used by the AI Mentor for retrieval and response scoping.

| Field | Values | Purpose |
|---|---|---|
| `ticket_type` | training / incident / lab | Determines AI behavior mode |
| `domain` | dns / vlan / cisco / linux / proxmox / ad / siem / other | Scopes doc retrieval |
| `difficulty` | beginner / intermediate / advanced | Adjusts mentor verbosity |
| `lab_ticket_id` | 001–010+ or null | Links to `labs/helpdesk/ticket-*.md` scenario |
| `student_id` | lab username | Session scoping |
| `evidence_submitted` | yes / no | Tracks whether student has provided output |
| `mentor_session_id` | UUID | Ties all AI responses to one session log |

---

## AI Response Format

Every AI Mentor response follows a consistent structure. Students learn to read this format quickly.

```
--- AI Mentor ---

[Situation summary]
One sentence confirming what was reported.

[What I need to see]
Numbered list of commands to run and output to paste.

[Why this matters]
Brief explanation of what the requested output reveals.

[Risk notice] (if applicable)
Any risk the student should know before proceeding.

[Documentation reminder] (at closure)
Prompt to write the incident summary.

--- End ---
```

The AI Mentor does not write paragraphs of explanation before asking for evidence. It asks first, explains after the student provides output.

---

## Escalation Rules

The AI Mentor recognizes when a ticket is outside its scope and routes accordingly.

| Condition | AI Response |
|---|---|
| Issue involves a system not in the lab | Acknowledge, explain it is out of scope, redirect to the lab boundary |
| Student is stuck after 3 rounds of guidance | Suggest instructor review; do not give the full answer |
| Issue requires production change approval | State the approval requirement; do not provide the config |
| Student reports a safety concern (physical, power, data loss risk) | Escalate immediately to instructor; suspend guidance |
| Ticket is ambiguous after two clarification rounds | Request a fresh ticket with more specific symptom description |

---

## What the AI Can and Cannot Write Back to Zammad

### v1 — Draft Panel Model (no auto-post)

In v1, the AI Mentor does not post directly into the ticket thread. It produces a response in a mentor draft panel, which the student sees after it has been generated. This prevents unreviewed AI text from becoming part of the official ticket record.

| AI can | AI cannot |
|---|---|
| Generate clarifying questions | Auto-post into ticket comments |
| Produce evidence checklists | Change ticket priority |
| Interpret command output | Close tickets |
| Surface risk warnings | Assign tickets to other users |
| Prompt closure summaries | Perform actions on lab systems |
| Log session data internally | Expose mentor-only solution notes to students |

### Future v2 — Webhook Model

After v1 is validated, the AI Mentor can post structured responses directly as internal notes via the Zammad API. Students see the note in the ticket thread. Instructors retain the ability to edit or retract.

This requires:
- Zammad API token scoped to the AI Mentor service account
- Rate limiting and audit logging on every API write
- Rollback procedure for incorrect AI responses

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│  ARIA (VLAN 70 — 192.168.70.x)                      │
│                                                     │
│  ┌─────────────────┐   ┌─────────────────────────┐  │
│  │  Zammad LXC     │   │  AI Mentor Backend LXC  │  │
│  │  Port 443 (TLS) │   │  FastAPI — Port 8080    │  │
│  │  PostgreSQL     │──►│  ChromaDB vector store  │  │
│  │  Ticket data    │   │  Session log store      │  │
│  └─────────────────┘   └──────────┬──────────────┘  │
│                                   │ API call         │
└───────────────────────────────────┼─────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  LLM API             │
                         │  (Claude recommended)│
                         └──────────────────────┘
```

Both Zammad and the AI Mentor backend run as separate LXC containers on ARIA VLAN 70. They communicate internally on the ARIA host network. The only external connection is the outbound API call to the LLM provider.

Student access to Zammad is restricted to VLAN 10 (MGMT) and VLAN 60 (LAB) by ACL. No public exposure.

---

## Security Notes

| Control | Implementation |
|---|---|
| Zammad access | Lab credentials only — no public registration |
| AI Mentor API calls | Outbound only via C1111 NAT — no inbound exposure |
| LLM API key | Stored in ARIA environment — not in repo, not in knowledge base |
| Session logs | Stored on ARIA local storage — not synced to cloud |
| Student cannot see mentor-only content | Enforced at retrieval layer — not just prompt instructions |
| Zammad DB | Local PostgreSQL on ARIA — no cloud backup of ticket data in v1 |

---

## Future: API/Webhook Plan (v2)

When v1 is validated and the draft panel model has been tested with real students:

1. Enable Zammad webhook on ticket update events
2. AI Mentor backend subscribes to the webhook
3. On new evidence submission, AI Mentor generates response and posts via Zammad API as internal note
4. Instructor review period before student sees response (optional, configurable)
5. Full audit log of every API write

This eliminates the manual step of students requesting mentor review, making the workflow closer to a real service desk AI assist.

---

## Deployment Gate

This design is blocked on the same gates as all ARIA workloads:

```
[ ] Replacement ATX control board installed
[ ] Comet hard power/reset validated
[ ] ARIA migrated to VLAN 70 (192.168.70.10/24)
[ ] Proxmox vmbr0 bridge configured and stable
[ ] Baseline package state clean (apt upgrade completed safely)
[ ] Zammad LXC deployed and accessible from VLAN 10/60
[ ] AI Mentor backend LXC deployed with ChromaDB
[ ] Knowledge base ingested and retrieval tested
[ ] v1 draft panel validated before any webhook integration
```

---

*Document created: Jun 4, 2026*
*Status: Design phase — no deployment*
