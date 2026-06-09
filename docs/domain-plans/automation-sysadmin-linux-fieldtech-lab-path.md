# Automation / SysAdmin / Linux / Field-Tech Lab Path

This document defines the completion path for the Automation / SysAdmin / Linux / Field-Tech training domain.

The domain already has strong infrastructure foundations:

- Proxmox host live
- Student Linux container model exists
- CT 102 student-linux-01 deployed
- Student SSH access validated
- Scoped sudo validated
- Ticket-003 Proxmox APT workflow
- Ticket-006 Proxmox repository hygiene workflow
- Ticket-008 Comet ATX reset validation workflow
- Existing Field-Tech Lab 001
- Existing Field-Tech Lab 002

## Current Closeout Goal

The domain must use a non-Zammad lab submission and completion model so students can submit Linux, Proxmox, field-tech, runbook, and automation evidence directly to ARIA.

## Existing Field-Tech Labs

The following completed labs must be connected to AI Mentor completion tracking:

| Lab | Status | Tracking Template |
|---|---|---|
| Field-Tech Lab 001: Endpoint Identity | Existing lab | field-tech-lab-001-endpoint-identity |
| Field-Tech Lab 002: Endpoint Health Check | Existing lab | field-tech-lab-002-endpoint-health-check |

## Minimum Complete Learning Path

Two field-tech labs are not enough to complete this domain. The learner path should include:

| Lab | Topic | Purpose |
|---|---|---|
| 001 | Endpoint Identity | Identify the endpoint, user/system context, and evidence target |
| 002 | Endpoint Health Check | Validate basic endpoint condition and document findings |
| 003 | Linux Filesystem Navigation and Evidence Collection | Teach `pwd`, `ls`, `cd`, paths, file inspection, and clean evidence capture |
| 004 | Users, Groups, and Permissions | Teach identity, ownership, groups, `chmod`, `chown`, and permission troubleshooting |
| 005 | Package Management and Repository Troubleshooting | Teach `apt`, package state, repository health, and safe update validation |
| 006 | Services and Logs | Teach `systemctl`, `journalctl`, service status, and log evidence |
| 007 | Network Checks | Teach IP, DNS, gateway, routes, and basic connectivity evidence |
| 008 | SSH Access and Scoped Sudo | Validate secure remote access and limited privilege escalation |
| 009 | Disk, Memory, CPU, and Process Health | Teach common sysadmin health checks |
| 010 | Basic Bash Automation and Script Safety | Introduce safe scripting, variables, dry runs, and rollback awareness |
| 011 | Proxmox Container Operations | Teach CT lifecycle, snapshots, resource checks, and safe operations |
| 012 | Backup / Restore / Runbook Validation | Teach documentation, restore proof, and operational handoff |

## Completion Standard

A lab is complete only when the student submits:

- Target system or endpoint identity
- Commands or checks performed
- Observations and findings
- Validation evidence
- Professional summary
- No secrets, passwords, private keys, tokens, or unrelated personal data

## Guardrail

Do not mark the Automation / SysAdmin / Linux / Field-Tech domain complete until the non-Zammad submission model supports:

- Linux labs
- Field-tech labs
- Runbook-writing labs
- Automation/IaC labs
- Ansible / Netmiko / RESTCONF training submissions
- Instructor review and completion tracking
