# ARIA Training Lab Inventory

> **Purpose:** Prevent existing ARIA labs, completed student work, and their training domains from being lost as new mentor workflows are added.
>
> **Status:** Working inventory created during Phase 10.

---

## Governance Rule

Existing production student labs must not be overwritten, renamed, moved, or reclassified without explicit approval.

New AI Mentor work must map into the existing ARIA training domains. Do not create a new domain when the work belongs under an existing operational track.

---

## Fixed Training Domains

ARIA currently tracks training under these domains:

1. Help Desk / Ticketing
2. Networking
3. Security / SOC
4. Automation / SysAdmin / Linux Field-Tech
5. Identity / IAM

The Field-Tech labs belong under **Automation / SysAdmin / Linux Field-Tech**.

---

## Completed / Production Student Training History

### Sha-Neal Prather / `sprather`

These records are production student training history and must be preserved.

| Lab | Path | Domain | Status | Notes |
|---|---|---|---|---|
| Field Tech Lab 001 — Verify Endpoint Identity and Network Connectivity | `labs/field-tech/lab-001-endpoint-identity/` | Automation / SysAdmin / Linux Field-Tech | First session complete | Student worked on `student-linux-01` using account `sprather`; lab validates SSH access, identity, hostname, IP, gateway, DNS, and connectivity evidence. |
| Field Tech Lab 002 — Perform a Basic Linux Endpoint Health Check | `labs/field-tech/lab-002-endpoint-health-check/` | Automation / SysAdmin / Linux Field-Tech | Lab file ready / production training history | Student health-check workflow for uptime, disk, memory, active sessions, OS/kernel, system state, interfaces, and listening ports. |

### Related roadmap

| Path | Purpose |
|---|---|
| `labs/field-tech/sha-neal-roadmap.md` | Tracks the ARIA Field-to-Cyber progression for Sha-Neal Prather. |

---

## Field-Tech Lab Series Roadmap

The existing roadmap defines this progression:

| Lab Range | Phase | Focus |
|---|---|---|
| 001-002 | Field Tech Foundation Labs | Endpoint access, identity, health verification |
| 003-005 | Help Desk Documentation Labs | Ticket quality, device documentation, troubleshooting process |
| 006-008 | Linux & Security Foundation Labs | Filesystem, permissions, authentication |
| 009 | Network Troubleshooting Labs | Open ports, services, network exposure |
| 010 | Cybersecurity Readiness Labs | Communication, KB writing, professional documentation |

Only Labs 001 and 002 currently have production lab content in the repo. Labs 003-010 are roadmap items unless later files are added and reviewed.

---

## Help Desk / Ticketing Labs

These are the current ticket-based mentor workflow labs under `labs/helpdesk/`.

| Ticket | Path | Domain |
|---|---|---|
| Ticket-001 — DNS Resolution Failing | `labs/helpdesk/ticket-001-dns-failure.md` | Help Desk / Ticketing + Networking / DNS |
| Ticket-002 — Device on Wrong VLAN | `labs/helpdesk/ticket-002-vlan-misassignment.md` | Help Desk / Ticketing + Networking / Switching / DHCP |
| Ticket-003 — Proxmox Host Cannot Run `apt update` | `labs/helpdesk/ticket-003-proxmox-apt-egress-failure.md` | Help Desk / Ticketing + Automation / SysAdmin / Linux Field-Tech |
| Ticket-004 — Cannot SSH Into Switch | `labs/helpdesk/ticket-004-ssh-legacy-kex.md` | Help Desk / Ticketing + Networking / Security |
| Ticket-005 — VLAN 1 Return Path Failure | `labs/helpdesk/ticket-005-vlan1-return-path-failure.md` | Help Desk / Ticketing + Networking |
| Ticket-006 — Proxmox Repo Hygiene | `labs/helpdesk/ticket-006-proxmox-repo-hygiene.md` | Help Desk / Ticketing + Automation / SysAdmin / Linux Field-Tech |
| Ticket-007 — Proxmox VLAN 70 Migration | `labs/helpdesk/ticket-007-proxmox-vlan70-migration.md` | Help Desk / Ticketing + Automation / SysAdmin / Networking |
| Ticket-008 — Comet ATX Hard Reset Validation | `labs/helpdesk/ticket-008-comet-atx-hard-reset-validation.md` | Help Desk / Ticketing + Automation / SysAdmin / Hardware Recovery |
| Ticket-009 — Zammad Ticket Triage | `labs/helpdesk/ticket-009-zammad-ticket-triage.md` | Help Desk / Ticketing |
| Ticket-010 — Wazuh Alert Investigation | `labs/helpdesk/ticket-010-wazuh-alert-investigation.md` | Security / SOC |

---

## CCNA / Networking Labs

These labs remain part of ARIA's Networking training corpus and should not be collapsed into help desk tickets.

| Lab | Path | Domain |
|---|---|---|
| Lab 003 — NTP / SNMP | `labs/lab-003-ntp-snmp.md` | Networking |
| Lab 004 — Network Automation | `labs/lab-004-network-automation.md` | Networking / Automation |
| Lab 005 — RESTCONF | `labs/lab-005-restconf.md` | Networking / Automation |
| Lab 006 — STP / RSTP | `labs/lab-006-stp-rstp.md` | Networking |
| Lab 007 — OSPFv3 | `labs/lab-007-ospfv3.md` | Networking |
| Lab 008 — AAA | `labs/lab-008-aaa.md` | Identity / IAM + Networking Security |
| Lab 009 — IP Source Guard | `labs/lab-009-ip-source-guard.md` | Networking Security |
| Lab 010 — OSPFv2 | `labs/lab-010-ospfv2.md` | Networking |

---

## Troubleshooting Labs

| Lab | Path | Domain |
|---|---|---|
| Troubleshooting Lab Report | `labs/troubleshooting-lab-report.md` | Help Desk / Troubleshooting Documentation |
| Troubleshooting Lab 002 — Tailscale | `labs/troubleshooting-lab-002-tailscale.md` | Networking / Remote Access / Field-Tech |

---

## Phase 10 Implication

Phase 10 only implements mentor workflow behavior for Help Desk Tickets 001-005.

It must not erase or de-prioritize Field-Tech Labs 001-002. Those labs are already part of production student training history and will be integrated into the active mentor training map during the Field-Tech / Linux integration phase.

---

## Protection Checklist Before Future Mentor Changes

Before adding or modifying mentor workflow logic, verify:

```text
[ ] Existing field-tech student history remains intact
[ ] Sha-Neal's completed Lab 001 status is preserved
[ ] Field Tech Lab 002 remains visible as production training content
[ ] Helpdesk tickets remain separate from field-tech labs
[ ] CCNA/networking labs remain visible in the KB/training map
[ ] New templates use existing domains, not new domain sprawl
[ ] Student-facing output does not expose private student details unnecessarily
```
