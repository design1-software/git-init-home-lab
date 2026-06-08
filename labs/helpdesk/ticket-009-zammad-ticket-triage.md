# Ticket-009: Zammad Ticket Triage

> **Lab Track:** Help Desk Documentation  
> **Difficulty:** Beginner  
> **Status:** Live validation passed 2026-06-07  
> **Platform:** ARIA Help Desk / Zammad  
> **Service URL:** `http://helpdesk.aria.local:8080`  
> **Related Runbook:** `docs/runbooks/zammad/zammad-lxc-deployment.md`

---

## 1. Scenario

A student is practicing basic help desk ticket handling inside the ARIA training environment. The goal is not to troubleshoot a broken server or network device yet. The goal is to prove that the student can use the ticketing system correctly.

The student must open or respond to a training ticket, describe the issue clearly, add evidence, communicate professionally, and complete a closure summary.

This ticket validates the Zammad platform before AI Mentor integration.

---

## 2. Student Objective

By the end of this exercise, the student should be able to:

1. Log in to the ARIA Help Desk.
2. View an assigned training ticket.
3. Understand the ticket title, description, and requested action.
4. Add a professional ticket comment.
5. Provide evidence that they completed the requested step.
6. Participate in ticket closure.
7. Write a short closure summary.

---

## 3. Environment

| Item | Value |
|---|---|
| Ticketing platform | Zammad |
| Host container | CT 110 `aria-zammad-01` |
| Service FQDN | `helpdesk.aria.local` |
| Service IP | `192.168.70.20` |
| Port | `8080` |
| Organization | `JLM Lab Trainees` |
| Ticket group | `ARIA Help Desk` |
| Student account model | Email-based Zammad login with Linux username documented separately |

---

## 4. Account Model

Zammad uses email-based login identifiers in this deployment. ARIA Linux/container usernames are not forced into the Zammad login field.

Use this mapping standard:

| System | Identifier |
|---|---|
| Linux/container username | Short username, for example `sprather` |
| Zammad login | Student email address |
| Zammad display name | Student real name |
| Zammad note/reference | Linux/container username |

Example:

```text
Linux/container username: sprather
Zammad login: sprath11@wgu.edu
Zammad display name: Sha Neal Prather
Zammad organization: JLM Lab Trainees
Zammad role: Customer
```

---

## 5. Ticket Setup

Create a ticket with the following values:

```text
Title: Ticket-009: Zammad Ticket Triage
Group: ARIA Help Desk
Customer/User: student account
Priority: Normal
State: New/Open
```

Suggested ticket body:

```text
A student is practicing basic help desk ticket handling in the ARIA training environment.

Objective:
Confirm that the student can open a ticket, describe an issue, add evidence, update the ticket, and write a closure summary.

This is a platform validation ticket for Zammad before AI Mentor integration.
```

---

## 6. Required Student Actions

The student must complete the following:

1. Log in to Zammad.
2. Open Ticket-009.
3. Read the ticket description.
4. Add a comment confirming access.
5. Describe what they can see in the ticket.
6. Confirm they can add an update.
7. Provide a short closure statement.

Suggested student comment:

```text
I can access the ARIA Help Desk ticket, view the original request, and submit an update. This confirms the basic student ticket workflow is functional.
```

---

## 7. Required Evidence

Acceptable evidence includes:

| Evidence | Required |
|---|---|
| Student can log in | Yes |
| Student can view Ticket-009 | Yes |
| Student can add a comment | Yes |
| Instructor/admin can see the comment | Yes |
| Instructor/admin can close the ticket | Yes |
| Ticket history shows the workflow | Yes |

The student should not simply say, “It worked.” They must provide a clear update that documents what was verified.

---

## 8. Instructor Workflow

Instructor should verify:

1. Student account exists and is active.
2. Student belongs to `JLM Lab Trainees`.
3. Student has customer/student-level permissions only.
4. Ticket is assigned to `ARIA Help Desk`.
5. Student can access and comment on the ticket.
6. Instructor/admin can respond and close the ticket.

Suggested instructor note:

```text
Ticket received. For this validation test, confirm that you can view the ticket, add a comment, and provide a short closure summary explaining what was tested.
```

Suggested closure summary:

```text
Zammad v1 platform validation passed. The ARIA Help Desk is reachable internally at helpdesk.aria.local:8080, the admin account can manage tickets, the student account can access and update tickets, and Ticket-009 confirms the basic training-ticket workflow.
```

---

## 9. Completion Criteria

This lab is complete when:

- The student successfully logs in.
- The student views Ticket-009.
- The student posts a comment.
- The instructor/admin confirms the comment is visible.
- The instructor/admin closes the ticket.
- The ticket contains a short closure summary.

---

## 10. Common Mistakes

| Mistake | Correction |
|---|---|
| Student says only “done” | Require a professional status update |
| Student cannot find the ticket | Confirm customer assignment and organization |
| Student logs in with Linux username | Zammad uses email-based login in this deployment |
| Instructor gives admin role to student | Keep student as customer-level user |
| Ticket is closed without closure notes | Reopen or add closure summary before marking complete |

---

## 11. AI Mentor Behavior Rules

When the AI Mentor is later attached to this ticket type, it should not troubleshoot infrastructure. It should coach ticket discipline.

The AI Mentor should:

1. Ask the student what they see in the ticket.
2. Require a professional update, not a one-word response.
3. Explain why evidence matters in help desk work.
4. Prompt the student to write a closure summary.
5. Reinforce that ticket history is part of the operational record.

The AI Mentor should not:

1. Close the ticket.
2. Change ticket priority.
3. Assign the ticket.
4. Modify ticket metadata.
5. Give unrelated technical troubleshooting steps.

Suggested AI Mentor response:

```text
--- ARIA Mentor ---

Situation Summary:
You are validating that you can use the ARIA Help Desk ticketing workflow.

What I need to see:
1. Confirm that you can open this ticket.
2. Add a comment describing what the ticket is asking you to do.
3. Add one sentence explaining what evidence proves the workflow is working.

Why this matters:
In real help desk work, the ticket is the operational record. A good update helps the next technician, the instructor, and the customer understand what happened.

Next Step:
Post a short professional update in the ticket. Do not just write “done.”

--- End ---
```

---

## 12. Portfolio Output

The student may document this lab as:

```text
Completed a basic help desk ticket workflow in Zammad, including ticket review, professional comment updates, evidence-based status reporting, and closure summary.
```

This is a beginner-level portfolio artifact showing exposure to ITSM workflow fundamentals.

---

## 13. Validation Status

Live validation completed successfully on ARIA:

| Validation Item | Result |
|---|---|
| Zammad stack running | PASS |
| `helpdesk.aria.local:8080` reachable | PASS |
| Admin login tested | PASS |
| Student login tested | PASS |
| Ticket opened | PASS |
| Comments added | PASS |
| Ticket closed | PASS |
| Proxmox baseline backup completed | PASS |
| Docker-level app backup completed | PASS |

---

*Updated after live Zammad validation: 2026-06-08*
