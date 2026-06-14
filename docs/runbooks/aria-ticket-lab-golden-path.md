# ARIA Ticket Lab Golden Path

Validated on: 2026-06-14

This runbook documents the confirmed end-to-end workflow for ARIA help desk ticket labs.

## Purpose

ARIA ticket labs train students through real help desk behavior:

- Read the assigned ticket in Zammad.
- Use ARIA AI Mentor for coaching, evidence requirements, and validation.
- Troubleshoot from the assigned lab target system.
- Collect real command output or observable evidence.
- Draft a professional ticket note.
- Submit the work for instructor review.
- Have the instructor approve one final note to Zammad.

Zammad remains the official ticket record. ARIA remains the evidence validator, coaching layer, and instructor review system.

## Confirmed System Roles

| System | Role |
| --- | --- |
| Zammad | Official ticket record and student-facing help desk queue |
| ARIA AI Mentor | Evidence-first training coach and validation engine |
| Instructor UI | Review queue, instructor approval, and final note submission |
| Student Linux container | Assigned troubleshooting target for Linux/help desk labs |
| GitHub repository | Source of truth for lab templates, runbooks, and app code |

## Confirmed Golden Path

1. Instructor creates a lab ticket from an ARIA template.
2. ARIA creates the Zammad ticket and links it to a local ARIA assignment.
3. Student opens Zammad and reviews the assigned ticket.
4. Student opens ARIA AI Mentor and loads the ticket/lab workflow.
5. ARIA shows the student what evidence is required.
6. Student connects to the assigned lab target and runs real troubleshooting commands.
7. Student pastes real evidence into ARIA AI Mentor.
8. ARIA validates the evidence.
9. Student drafts the final Zammad note in ARIA.
10. Instructor reviews the student work in the Instructor Review Queue.
11. Instructor prepares the selected assignment for final note submission.
12. Instructor pastes the approved final note.
13. Instructor approves the final note.
14. ARIA adds the approved note to Zammad.
15. ARIA marks the local assignment completed.
16. Zammad ticket state, priority, and closure status remain unchanged by ARIA.

## Confirmed Phase Status

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 6: Instructor-approved Zammad note submission | PASS | Approved note appears in Zammad without changing ticket state |
| Phase 7: Instructor-created Zammad lab ticket | PASS | Script creates Zammad ticket and linked ARIA assignment |
| Instructor UI approval button | PASS | Prepare Writeback and Approve & Write to Zammad confirmed |
| Student evidence validation | PASS | Student evidence reaches validation_complete |
| Zammad ticket state protection | PASS | Ticket state did not change after approved note submission |

## Create a Lab Ticket

Run inside CT 120 from the repository path:

```bash
cd /opt/aria-ai-mentor/source/git-init-home-lab

python3 services/ai-mentor/scripts/create_lab_ticket.py \
  --student student02 \
  --template ticket-001 \
  --created-by instructor
```

Expected output includes:

```text
Zammad ticket created and ARIA assignment linked.
Zammad customer lookup: student02@jlm.lab
Zammad ticket number: <ticket_number>
Zammad ticket id: <zammad_ticket_id>
Zammad URL: http://100.71.47.90:8080/#ticket/zoom/<zammad_ticket_id>
Assignment ID: <assignment_id>
Student: student02
Lab ticket ID: 001
```

## Student Workflow

The student should open:

1. Zammad
2. ARIA AI Mentor
3. Assigned lab target system

For student02, the confirmed target is:

```bash
ssh student02@100.91.190.9
```

For Ticket-001, the required evidence categories are:

- Client identity and host
- Client IP configuration
- Client route table
- Client DNS resolver configuration
- DNS query result
- External IP connectivity test

Example command set:

```bash
whoami
hostname
ip addr
ip route
cat /etc/resolv.conf
ping -c 4 8.8.8.8
nslookup google.com
```

## Instructor Review Queue Workflow

Open the Instructor UI:

```text
http://192.168.70.30:8081/instructor
```

Workflow:

1. Click Refresh Review Queue.
2. Find the correct Zammad ticket number and student assignment.
3. Confirm review state is ready_for_instructor_review.
4. Click Prepare Writeback.
5. Paste the instructor-approved note.
6. Click Approve & Write to Zammad.
7. Verify the success message.
8. Open the Zammad ticket and confirm the approved note is present.
9. Confirm Zammad ticket state did not change.

## Safety Rules

The instructor-approved final note workflow must remain limited:

- Adds one approved note only.
- Requires instructor/admin role.
- Requires a linked assignment.
- Blocks duplicate approval after an assignment is already approved and completed.
- Does not close the Zammad ticket.
- Does not change Zammad ticket state.
- Does not change Zammad priority.
- Stores a payload hash for the approved text.
- Marks the local assignment completed after successful approval.

## Known Good Test Case

Tested with student02 and Ticket-001 DNS Failure.

Confirmed evidence showed:

- student02 on student-linux-02
- eth0 UP with 192.168.70.13/24
- tailscale0 with 100.91.190.9/32
- default route through 192.168.70.1
- DNS resolvers 192.168.10.16 and 1.1.1.1
- nslookup google.com succeeded through 192.168.10.16
- ping -c 4 8.8.8.8 succeeded after container ping permissions were corrected
- ARIA Mentor returned validation_complete
- Instructor-approved note appeared in Zammad
- Zammad ticket state did not change

## Completion Criteria for This Training Domain

The Help Desk / Ticketing training domain is not complete until the following are true:

- Every active help desk ticket lab has a matching ARIA lab template.
- Every template can create a linked Zammad ticket.
- Every student-facing ticket clearly states what to open, where to work, and what evidence to collect.
- ARIA validates real evidence and blocks placeholder evidence.
- Instructor review queue shows the assignment and progress clearly.
- Instructor can approve and submit the final note to Zammad from the UI.
- Zammad ticket state remains under instructor/manual control.
- The workflow is documented enough for the next student to complete without ad hoc instructions.

## Next Work

To complete the Help Desk / Ticketing domain, continue with:

1. Verify all 10 ticket templates create Zammad tickets successfully.
2. Run at least one more student through a different ticket lab.
3. Add any missing evidence rules to templates.
4. Confirm final-note drafting does not leave placeholders.
5. Create an instructor checklist for grading each ticket lab.
6. Create a student-facing quick-start page for ticket labs.
7. Add a short troubleshooting section for common lab environment issues.
