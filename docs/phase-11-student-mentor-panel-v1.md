# Phase 11 — Student-Facing Mentor Panel v1

> **Purpose:** Give students a safe, simple interface to interact with ARIA Mentor without exposing instructor-only controls, raw backend internals, Zammad metadata, or administrative workflows.
>
> **Status:** Planning baseline created after Phase 10 completion.

---

## Phase 10 Dependency

Phase 11 begins only after Phase 10 validation is complete.

Phase 10 completed and validated:

```text
[x] Ticket-001 DNS Failure
[x] Ticket-002 VLAN Misassignment
[x] Ticket-003 Proxmox APT Egress Failure
[x] Ticket-004 SSH Legacy KEX
[x] Ticket-005 VLAN 1 Return Path Failure
```

Reference:

```text
docs/phase-10-ticket-001-005-validation.md
```

---

## Existing Foundation

The current backend already includes:

```text
[x] Local auth with signed HTTP-only cookie
[x] Supported roles: admin, instructor, student, viewer
[x] Instructor panel route: /instructor
[x] Instructor-only Zammad review workflow
[x] Deterministic mentor endpoint: /mentor/analyze-ticket
[x] Template-aware mentor guidance
[x] Session logging
[x] Audit/event logging utilities
[x] Lab templates for Ticket-001 through Ticket-010
```

---

## Phase 11 Scope

Phase 11 will add a student-safe interface and student-safe API workflow.

### Student route

```text
GET /student
```

Allowed roles:

```text
admin
instructor
student
```

Purpose:

- Display a student-facing mentor panel
- Hide instructor-only controls
- Hide raw Zammad JSON
- Hide customer metadata
- Hide internal ticket IDs unless needed for learning
- Hide LLM controls for v1
- Hide Zammad writeback or closure actions

### Student mentor endpoint

```text
POST /mentor/student/analyze-ticket
```

Allowed roles:

```text
admin
instructor
student
```

Purpose:

- Accept a student-entered ticket/lab prompt
- Use existing deterministic mentor workflow
- Return student-safe fields only
- Write a student mentor access audit event

---

## Student-Safe Response Contract

The student endpoint should return only:

```json
{
  "session_id": "...",
  "next_action": "request_more_evidence | validation_complete | manual_review | ...",
  "risk_level": "low | medium | high",
  "mentor_response": "student-safe guidance text",
  "lab_template": {
    "matched": true,
    "template_id": "ticket-001",
    "title": "DNS Failure",
    "domain": "dns",
    "difficulty": "beginner",
    "mentor_mode": "guided_troubleshooting",
    "required_evidence": []
  },
  "retrieved_sources": [
    "labs/helpdesk/ticket-001-dns-failure.md",
    "lab_template:ticket-001"
  ],
  "timestamp_utc": "..."
}
```

Do not return:

```text
[ ] Zammad customer metadata
[ ] Raw Zammad articles
[ ] Internal ticket database IDs unless explicitly needed
[ ] Admin-only audit data
[ ] Instructor-only review notes
[ ] LLM controls or hidden deterministic internals
[ ] Credentials, tokens, secrets, or private student records
```

---

## Student Panel UI Requirements

The student panel should include:

```text
[ ] Login-required access
[ ] Current signed-in user display
[ ] Ticket/lab ID field
[ ] Ticket/lab title field
[ ] Ticket/lab body field
[ ] Evidence text area
[ ] Submit button
[ ] Mentor guidance output
[ ] Next action badge
[ ] Risk level badge
[ ] Matched template summary
[ ] Required evidence checklist
[ ] Retrieved source path list without raw chunks
[ ] Clear reminder: ARIA guides; it does not do the work for the student
```

The student panel should not include:

```text
[ ] Fetch Zammad ticket button
[ ] Assistive LLM button
[ ] Internal ticket ID field
[ ] Customer metadata
[ ] Zammad articles
[ ] Admin routes
[ ] Instructor review controls
[ ] Writeback or closure controls
```

---

## Audit Requirements

Student access must write audit events for:

```text
[ ] student panel access
[ ] student mentor guidance request
[ ] matched lab_template_id
[ ] matched lab_template_domain
[ ] next_action
[ ] risk_level
[ ] username
[ ] role
[ ] request outcome
```

Suggested event names:

```text
panel.student_access
panel.student_access_denied
mentor.student_guidance_requested
```

---

## Implementation Plan

### Step 1 — Add student panel route

Modify:

```text
services/ai-mentor/app/main.py
```

Add:

```text
GET /student
```

Behavior:

```text
- If not logged in, redirect to /login
- If role is not admin, instructor, or student, return 403
- Write audit event
- Serve /opt/aria-ai-mentor/app/static/student.html
```

### Step 2 — Add student mentor endpoint

Modify:

```text
services/ai-mentor/app/main.py
```

Add:

```text
POST /mentor/student/analyze-ticket
```

Behavior:

```text
- Require admin, instructor, or student role
- Call existing deterministic mentor_analyze_ticket logic
- Write audit event with template metadata
- Return student-safe response payload
```

### Step 3 — Add student static UI

Create:

```text
services/ai-mentor/app/static/student.html
```

Behavior:

```text
- Call /auth/me to show signed-in student
- Submit to /mentor/student/analyze-ticket
- Render mentor_response, next_action, risk_level, template summary, required evidence, and source list
- Do not expose instructor panel or Zammad internals
```

### Step 4 — Validate locally on CT 120

Deploy:

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab
git pull origin main

cp services/ai-mentor/app/main.py /opt/aria-ai-mentor/app/main.py
cp services/ai-mentor/app/static/student.html /opt/aria-ai-mentor/app/static/student.html

systemctl restart aria-ai-mentor
systemctl status aria-ai-mentor --no-pager
```

Health:

```bash
curl -s http://127.0.0.1:8081/health | jq
```

### Step 5 — Validate authenticated student workflow

Required checks:

```text
[ ] Student user can open /student
[ ] Viewer cannot open /student
[ ] Unauthenticated user redirects to /login
[ ] Student can submit Ticket-001 scenario and receive guidance
[ ] Student response hides Zammad metadata
[ ] Required evidence checklist appears
[ ] Audit event is written for panel access
[ ] Audit event is written for mentor request
```

---

## Completion Gate

Phase 11 is complete only when:

```text
[ ] /student route exists and is protected
[ ] /mentor/student/analyze-ticket exists and is protected
[ ] Student-safe UI renders successfully
[ ] Student-safe response payload excludes Zammad/admin-only data
[ ] Template-aware guidance works from the student panel
[ ] Required evidence is visible to student
[ ] next_action is visible to student
[ ] Audit logging captures student panel access
[ ] Audit logging captures student guidance requests
[ ] Instructor panel remains unchanged
[ ] Phase 10 workflows still pass after Phase 11 changes
```

---

## Next Phase

After Phase 11 completion, proceed to:

```text
Phase 12 — Ticket-006 through Ticket-010 workflow integration
```
