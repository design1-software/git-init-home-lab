# ARIA Student Lab Workflow Standard

This document defines the minimum workflow that every ARIA student-facing lab must include.

## Why This Exists

New IT trainees should never have to guess which systems to open, where the ticket lives, where commands are run, or where final documentation goes.

Every student lab must clearly separate these roles:

| Tool / System | Purpose |
|---|---|
| Zammad | The official ticket record and final ticket documentation location |
| ARIA AI Mentor | Coaching, evidence review, and troubleshooting guidance |
| Lab Target System | The Windows, Linux, network, or security system where the student performs the actual work |
| Student Notes | Temporary scratch notes before the final Zammad update |

## Required Student Workflow Section

Every lab must include a section named:

```text
Student Workflow: What to Open
```

That section must list exactly what the student needs before starting.

Template:

```text
Before starting this lab, open:

1. Zammad
   - Purpose: Read the assigned ticket and write the final ticket note.
   - What to capture: Ticket number, title, user-reported issue, and any comments.

2. ARIA AI Mentor
   - Purpose: Ask for guidance and validate whether your evidence is complete.
   - URL: http://100.90.114.40:8081/student
   - What to enter: Ticket/Lab ID, title, scenario, and collected evidence.

3. Lab Target System
   - Purpose: Run the actual commands and collect real evidence.
   - Example: JLM-WIN01, student-linux-02, Cisco switch, Proxmox host, or Wazuh dashboard.

4. Student Notes
   - Purpose: Keep temporary notes while testing.
   - Do not paste passwords, tokens, or unrelated personal information.
```

## Required Evidence Instructions

Every lab must explain that the AI Mentor evidence box is not a free-form chat box.

Required wording:

```text
The Evidence You Collected box is for actual evidence, not guesses or plans.
Paste command output, screenshots summarized in text, observed errors, or test results.
Do not paste passwords, API keys, private tokens, or unrelated personal information.
```

## Required Lab Flow

Every lab must include this student-facing flow:

```text
1. Read the Zammad ticket.
2. Open ARIA AI Mentor.
3. Enter the ticket/lab information into ARIA.
4. Ask ARIA what evidence is required if you are unsure.
5. Go to the lab target system and run the required checks.
6. Paste real command output or observations into ARIA.
7. Use ARIA's feedback to determine what evidence is still missing.
8. Repeat until the evidence is complete.
9. Write the final ticket note in Zammad.
10. Submit or notify the instructor for review.
```

## Required Final Ticket Note Format

Every ticket-style lab must require a final note in Zammad using this structure:

```text
Summary:

Evidence Collected:

Root Cause or Finding:

Action Taken or Recommended:

Verification:

Escalation Needed: Yes/No
```

## Domain-Specific Target System Examples

| Domain | Typical Target System |
|---|---|
| Help Desk / Ticketing | Zammad plus the affected system named in the ticket |
| Windows / AD / GPO | JLM-WIN01, JLM-DC01, ADUC, GPMC, Event Viewer |
| Linux / SysAdmin | Assigned student Linux container, Proxmox host, or lab service |
| Networking / DNS / VLAN | Windows client, DNS server, gateway, Cisco switch, or router |
| Security / SOC | Wazuh dashboard, endpoint logs, alert details, affected host |

## Blocking Rule

A lab is not student-ready unless it tells the trainee:

```text
What to open
Where the ticket is
Where to run commands
What evidence to collect
Where to paste evidence
Where to document the final answer
How the instructor will review it
```

If any of those items are missing, the lab should be marked as instructor draft only, not student-ready.
