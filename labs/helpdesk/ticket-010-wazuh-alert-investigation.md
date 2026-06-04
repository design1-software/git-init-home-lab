# Helpdesk Ticket 010 — Wazuh Alert Investigation

**Domain:** Security / SIEM / Log Analysis
**Difficulty:** Intermediate–Advanced
**Estimated time:** 45–60 minutes
**Status:** Documented only — live validation pending Wazuh deployment on ARIA VLAN 70

---

## Scenario

A student receives a Wazuh alert and must investigate it using the Wazuh dashboard and corroborating system logs. The goal is to determine whether the alert is a true positive (real incident) or false positive (benign activity that triggered a rule), document the investigation, and recommend a response.

This ticket is the entry point to the security operations domain. It is not about fixing a network problem — it is about interpreting evidence from a monitoring system and making a judgment call.

---

## Ticket Details

**Reported by:** Wazuh automated alert → Zammad integration
**Affected system:** JLM-LAB-R1 (C1111) or ARIA Proxmox host — SSH
**Priority:** P2 (security alert — escalate if confirmed external threat)
**Category:** Security — SIEM / SSH Brute Force

---

## The Alert

```
Alert ID:    WZ-2026-0604-001
Timestamp:   2026-06-04 22:14:33 UTC
Rule ID:     5763
Rule Desc:   Multiple authentication failures followed by a success
Severity:    High (level 10)
Agent:       ARIA (192.168.70.10)
Source IP:   192.168.10.11
Source Port: 49832
Destination: 192.168.70.10:22
User:        root
Count:       7 failures, 1 success
```

---

## AI Mentor Opening Questions

```
1. Have you opened the alert in the Wazuh dashboard?
2. What is the source IP — is it internal or external?
3. What does 192.168.10.11 correspond to in this lab?
4. Rule 5763 describes "authentication failures followed by success" — what
   does that combination suggest vs. failures alone?
5. What other evidence would you want to see before deciding if this is real?
```

---

## Evidence Required

```
From Wazuh dashboard:
- Full alert detail for WZ-2026-0604-001
- Related alerts in the same time window from the same source IP
- Rule 5763 description and context

From ARIA (if accessible):
- /var/log/auth.log around 22:14 UTC
  (grep "sshd" /var/log/auth.log | grep "2026-06-04T22:1")
- Who is currently logged in: who / w
- Recent login history: last | head -20

From Acer Server (192.168.10.11):
- Is there any automated SSH process running to ARIA?
- Check: any cron jobs, Ansible playbooks, or backup scripts configured?
```

---

## Diagnostic Path

```
Step 1: Identify the source

  Source IP 192.168.10.11 = Acer Server (VLAN 10 MGMT)
  → This is an internal device on the management VLAN
  → External attacker cannot reach 192.168.70.10:22 (no port forwarding)
  → This narrows to: automated process on Acer, misconfigured SSH key,
    or someone manually testing SSH from Acer

Step 2: Interpret the pattern

  7 failures followed by 1 success is not typical brute force behavior.
  A successful brute force would show hundreds or thousands of attempts.
  7 failures + 1 success suggests:
    - Wrong SSH key being tried first (key agent cycling through keys)
    - Wrong username attempted before the correct one
    - Script with incorrect first attempt configuration
    - SSH client trying multiple host keys before the right one

Step 3: Check auth.log on ARIA

  Look for: which usernames were tried (root? admin? pve?)
  Look for: authentication method (password? publickey?)
  Look for: what succeeded (key-based auth? password auth?)

Step 4: Check Acer for automation

  Is there a script that SSHs to ARIA?
  - Netmiko backup script (scripts/netmiko_backup.py) → targets Cisco, not ARIA
  - Any cron job? (crontab -l on Acer)
  - Any Ansible playbook that runs against ARIA?

Step 5: Make a determination

  True positive indicators:
    - Source is external (not 192.168.10.11)
    - Username is generic (root, admin, ubuntu, pi)
    - High attempt count (>20) in short time window
    - Success came after many failures with randomized usernames

  False positive indicators:
    - Source is internal known device (Acer = 192.168.10.11)
    - Low attempt count (7)
    - Success is expected (authorized admin logging in)
    - Pattern matches known automation behavior

  Most likely outcome for this scenario:
    Internal automation or misconfigured SSH client on the Acer.
    Not a security incident — but document why and fix the misconfiguration.

Step 6: Recommended response

  If false positive:
    - Document the investigation and the benign explanation
    - Identify and fix the misconfigured SSH process on Acer
    - Consider creating a Wazuh rule exception for this specific authorized pattern
    - Close as false positive with full investigation notes

  If true positive (would require external source):
    - Isolate: block source IP on C1111 ACL
    - Preserve: capture /var/log/auth.log before any changes
    - Escalate: notify lab instructor immediately
    - Investigate: how did external traffic reach SSH port? (no port forwarding should exist)
    - Review: check for any unauthorized changes made during the successful login
```

---

## Wazuh Rule Reference

| Rule ID | Description | Severity |
|---|---|---|
| 5710 | SSH authentication failure | Medium (level 5) |
| 5712 | SSH brute force — multiple failures | High (level 10) |
| 5763 | SSH failures followed by success | High (level 10) |
| 5715 | SSH authentication success | Info (level 3) |

Rule 5763 is more serious than 5712 alone because the eventual success means access was gained. This is why it is always at least P2 — even when the source is internal.

---

## Key Security Principles This Ticket Teaches

**1. Source IP is the first filter**
Internal source ≠ no threat, but it dramatically changes the investigation path. An external source that bypassed NAT with no port forwarding is a far more serious finding.

**2. Pattern matters more than count**
7 failures + 1 success is different from 500 failures + 0 success. The pattern determines the likely cause.

**3. Never close a security alert without documentation**
Even a false positive must be documented: what was investigated, what was found, why it was determined benign. If the same pattern recurs, the prior investigation is the baseline.

**4. Fix the root cause, not just the alert**
If the Acer has a misconfigured SSH process, it should be fixed — not just suppressed in Wazuh. Suppressing alerts without fixing root causes creates blind spots.

---

## Documentation Prompt

```
Write a security investigation report:
- Alert summary (who, what, when, where)
- Investigation steps taken and evidence examined
- Determination: true positive or false positive
- Reasoning: why you reached that determination
- Response taken or recommended
- Proposed fix for root cause (if false positive)
- Proposed escalation path (if true positive)
- Whether a Wazuh exception or tuning is recommended
```

---

## Learning Objectives

- Navigate a Wazuh SIEM dashboard and read alert detail
- Distinguish between alert severity levels and actual incident severity
- Use auth.log to corroborate or contradict a SIEM alert
- Apply the internal vs external source filter as the first triage step
- Interpret SSH authentication patterns (failures vs failures + success)
- Write a structured security investigation report
- Understand when to escalate vs close as false positive
- Understand that false positives still require documentation and root cause fixes
