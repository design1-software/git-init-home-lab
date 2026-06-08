# ARIA Mentor and Zammad Native AI Boundaries

> **Status:** Architecture guardrail  
> **Scope:** ARIA AI Mentor, Zammad Help Desk, native AI provider features  
> **Purpose:** Prevent duplicate AI functionality, maintenance debt, and user confusion while preserving ARIA Mentor as a platform-wide training coach.

---

## 1. Purpose

Zammad includes native AI provider support and AI-powered productivity features such as ticket summaries, writing assistance, AI agents, and provider-based model configuration.

ARIA Mentor must not compete with those native Zammad features.

ARIA Mentor is a platform-wide educational coaching layer for the ARIA training environment. It must support help desk, Active Directory, Windows, Linux, networking, cybersecurity, documentation, escalation, and lab workflows without duplicating the native AI functionality of the tools it integrates with.

---

## 2. Design Principle

```text
Native application AI = app-specific productivity.
ARIA Mentor = education, evidence coaching, troubleshooting discipline, and lab guidance.
```

ARIA Mentor should teach students how to use tools correctly, including native AI features where appropriate, but it should not replace those native features.

---

## 3. Zammad Native AI Ownership

The following functions belong to Zammad's native AI feature set when configured through Zammad AI Providers:

- Ticket state summaries
- Problem summaries
- Conversation summaries
- Open-question summaries
- Upcoming-event summaries
- Customer sentiment assessment
- Writing assistant actions
- Spelling and grammar correction
- Draft expansion
- Simplification of complex text
- Translation to English
- AI agents triggered or scheduled inside Zammad
- OCR behavior configured through Zammad's provider settings

ARIA Mentor should not rebuild these functions as separate Zammad-specific features.

---

## 4. ARIA Mentor Ownership

ARIA Mentor owns the training and coaching layer:

- Evidence-first troubleshooting guidance
- Student question prompts
- Ticket discipline coaching
- Lab objective alignment
- Instructor-facing draft guidance
- Escalation coaching
- Documentation quality coaching
- Portfolio-output coaching
- Safety boundaries for beginner students
- Cross-platform learning guidance across Zammad, Active Directory, Windows, Linux, Cisco networking, cybersecurity, monitoring, and documentation systems

ARIA Mentor should guide students toward correct process, not simply generate answers.

---

## 5. How ARIA Mentor Should Use Zammad Native AI

ARIA Mentor may recommend native Zammad AI features when they are the right tool for the task.

Examples:

| Student or Instructor Need | Preferred Tool |
|---|---|
| Summarize a long ticket conversation | Zammad Ticket Summary |
| Clean up spelling and grammar | Zammad Writing Assistant |
| Expand a rough response draft | Zammad Writing Assistant |
| Simplify a complex written response | Zammad Writing Assistant |
| Translate a ticket response to English | Zammad Writing Assistant |
| Determine what evidence a student still needs | ARIA Mentor |
| Coach a student through a troubleshooting workflow | ARIA Mentor |
| Teach escalation criteria | ARIA Mentor |
| Connect a ticket to a lab objective | ARIA Mentor |
| Create portfolio-ready learning output | ARIA Mentor |

---

## 6. Zammad API Integration Boundary

Initial Zammad integration must remain read-only.

Allowed in v1:

- Fetch ticket metadata
- Fetch ticket articles/comments
- Fetch users/groups needed for display context
- Generate instructor-facing draft guidance
- Log mentor sessions inside ARIA Mentor

Not allowed in v1:

- Posting public replies
- Posting internal notes
- Closing tickets
- Changing priority
- Changing ownership
- Changing groups
- Running Zammad AI Agents automatically
- Triggering Zammad automations

Writeback may be considered later only after instructor approval workflows are implemented.

---

## 7. Provider Configuration Boundary

Zammad may connect directly to Anthropic or OpenAI through its own AI Provider settings.

ARIA Mentor may also use Anthropic or OpenAI later, but it must remain independently governed.

Do not share raw provider tokens in documentation, tickets, screenshots, or chat transcripts.

Token storage rules:

| System | Token Storage |
|---|---|
| Zammad native AI provider | Zammad Provider settings |
| ARIA Mentor backend | `/opt/aria-ai-mentor/.env` on CT 120 |
| GitHub repository | `.env.example` only, no secrets |

---

## 8. Platform-Wide Mentor Scope

ARIA Mentor is not limited to Zammad.

Future mentor domains include:

- Help desk ticketing
- Active Directory
- Windows endpoint administration
- Linux endpoint administration
- Cisco networking
- VLAN troubleshooting
- DNS/DHCP workflows
- Cybersecurity triage
- Monitoring and alert response
- Documentation and change-control discipline
- Portfolio and student progress tracking

Each domain should respect native tool boundaries.

Examples:

- If Windows/AD tools provide native reporting, ARIA Mentor should teach students how to interpret the report instead of duplicating it.
- If a cybersecurity tool provides built-in alert summaries, ARIA Mentor should coach triage, evidence, severity, and escalation rather than generating a competing summary.
- If Zammad provides writing assistance, ARIA Mentor should coach when and how to use it professionally.

---

## 9. Recommended Integration Path

1. Keep Zammad native AI features available for app-specific productivity.
2. Build ARIA Mentor as a separate training service on CT 120.
3. Implement Zammad read-only API integration first.
4. Generate instructor-facing mentor guidance from real ticket context.
5. Add a basic instructor draft panel.
6. Add LLM provider integration behind ARIA Mentor's evidence-first guardrails.
7. Consider Zammad internal-note writeback only after instructor approval workflows exist.
8. Do not enable autonomous Zammad AI Agents from ARIA Mentor until a later governance review.

---

## 10. Final Guardrail

ARIA Mentor should never become a confusing second version of Zammad's built-in AI.

It should be the training brain across the ARIA environment: a coach, guide, instructor assistant, and evidence-first mentor that teaches students how to use enterprise tools correctly.
