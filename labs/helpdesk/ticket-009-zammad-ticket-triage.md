# Helpdesk Ticket 009 — Zammad Ticket Triage

**Domain:** Help Desk / ITSM / Ticket Management
**Difficulty:** Beginner
**Estimated time:** 30–45 minutes
**Status:** Documented only — live validation pending Zammad deployment on ARIA VLAN 70

---

## Scenario

A student logs into Zammad and finds a queue of 6 unassigned tickets with no priority or category set. The student must triage each ticket: assign a priority, assign a category, route to the correct team or owner, and write a one-sentence triage note explaining the decision.

This is not a break/fix exercise. It is a service desk workflow exercise. The goal is structured thinking about impact, urgency, and escalation — not technical troubleshooting.

---

## Ticket Details

**Reported by:** Lab instructor (queue management task)
**Affected system:** Zammad ticket queue
**Priority:** Low (training exercise)
**Category:** ITSM — Triage / Queue Management

---

## Why This Ticket Is Valuable

In real enterprise environments, L1 help desk analysts spend a significant portion of their time triaging — not fixing. Incorrect triage (wrong priority, wrong category, wrong owner) delays resolution and distorts SLA metrics. Students who have never done structured triage often underestimate urgency or mis-categorize tickets.

This ticket teaches:
- The difference between urgency and impact
- How to assign priority without knowing the full root cause
- How to write a triage note that helps the next person
- How ticket routing decisions affect response time

---

## AI Mentor Opening Questions

```
1. Do you have access to the Zammad ticket queue?
2. Can you see the 6 unassigned tickets?
3. Before we triage anything — what is your definition of a P1 ticket?
   (The mentor will not proceed until the student demonstrates they understand
   priority levels. This is not a trick — it's the foundation.)
```

---

## Priority Framework

The student must apply this framework consistently:

| Priority | Definition | SLA target |
|---|---|---|
| P1 — Critical | Production down, all users affected, no workaround | Immediate response |
| P2 — High | Production degraded or major service affected, workaround exists | < 1 hour |
| P3 — Medium | Non-critical service affected, single user or department impacted | < 4 hours |
| P4 — Low | Minor issue, cosmetic, or training task | < 24 hours |

---

## The 6 Training Tickets

These are fictional tickets from a simulated lab environment. The student reads each one and assigns priority, category, and routing.

---

### Triage Ticket A

> *"Hi, I can't get on the internet. My laptop says it's connected to Gorgeous WiFi but nothing loads."*

**Expected triage:**
- Priority: P3 — single user, workaround (switch to wired) exists
- Category: Network — VLAN / DNS
- Route to: L1 analyst
- Note: "Single user, VLAN 20 suspected. Check Pi-hole and DHCP lease before escalating."

---

### Triage Ticket B

> *"Proxmox web UI is down. I can't manage any VMs. The server was online 10 minutes ago."*

**Expected triage:**
- Priority: P2 — infrastructure service affected, no workaround for VM management
- Category: Proxmox — Host Connectivity
- Route to: L2 sysadmin
- Note: "Proxmox UI unreachable. Check ARIA network state and Tailscale fallback before escalating to console."

---

### Triage Ticket C

> *"The printer in the lab isn't printing. I keep getting an error."*

**Expected triage:**
- Priority: P4 — single device, not critical to operations
- Category: Printing — CUPS / Network
- Route to: L1 analyst
- Note: "CUPS print queue suspected. Check Pi-hole DNS and printer VLAN 30 connectivity."

---

### Triage Ticket D

> *"ALL WiFi SSIDs are down. Nobody can connect to anything. Even the guest network."*

**Expected triage:**
- Priority: P1 — all users affected, all wireless services down, no workaround for wireless users
- Category: Network — WiFi / UniFi
- Route to: L2 network engineer, immediate escalation
- Note: "All SSIDs down simultaneously suggests AP or UniFi controller failure. Check GS308EP Port 4/5 and UniFi controller status immediately."

---

### Triage Ticket E

> *"I got a Wazuh alert that says 'Multiple failed SSH login attempts' on the Acer server. Not sure if it's real."*

**Expected triage:**
- Priority: P2 — potential security incident, requires investigation before determining severity
- Category: Security — SIEM Alert / SSH
- Route to: L2 security analyst
- Note: "Possible brute force or misconfigured automation. Investigate source IP and frequency before closing. Escalate to P1 if source is external."

---

### Triage Ticket F

> *"Can you add me to the lab training environment? I just started."*

**Expected triage:**
- Priority: P4 — no service impact, onboarding request
- Category: Access — User Provisioning
- Route to: Lab admin
- Note: "New user provisioning. No urgency. Verify identity and assign lab credentials."

---

## AI Mentor Guidance Notes

The mentor does not give the expected triage answers. It asks questions:

For each ticket:
```
"Before you assign a priority — who is affected and is there a workaround?"
"How many users does this impact?"
"Is this a production service or a training resource?"
"What category best describes what's broken?"
"Who on the team has the skills to handle this?"
```

If the student assigns P1 to the printer ticket:
> *"Walk me through your reasoning. A P1 means immediate response — would you page someone at 2am for this?"*

If the student assigns P4 to the all-SSIDs-down ticket:
> *"All wireless users are affected and there is no workaround for WiFi-only devices. Does that change your priority assessment?"*

---

## Documentation Prompt

```
Complete a triage log for all 6 tickets:

| Ticket | Priority | Category | Assigned To | Triage Note |
|---|---|---|---|---|
| A | | | | |
| B | | | | |
| C | | | | |
| D | | | | |
| E | | | | |
| F | | | | |

After the table, write two sentences explaining what criteria you used
to distinguish between P1 and P2 tickets.
```

---

## Learning Objectives

- Apply a structured priority framework (P1–P4) consistently
- Distinguish between urgency (how fast) and impact (how many)
- Write a triage note that gives the next person actionable context
- Recognize when a ticket should be escalated versus handled at L1
- Understand that a security alert is always at least P2 until investigated
- Practice the discipline of triaging before troubleshooting
