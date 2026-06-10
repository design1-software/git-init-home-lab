# Identity/IAM AD Lab Live Milestone

Status: Completed foundation milestone  
Date: 2026-06-09  
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration

## Summary

The ARIA Identity/IAM training domain has moved from planning/scaffolding into a live working Active Directory lab.

The lab now includes:

- A Windows Server domain controller
- A live AD forest/domain
- DNS for the AD domain
- A domain-joined Windows 11 workstation
- A student test account
- ARIA training OUs and groups
- Verified domain login
- Verified domain controller discovery
- Verified Group Policy processing

This milestone establishes the foundation for hands-on Identity/IAM labs covering onboarding, group membership, domain join troubleshooting, OU placement, GPO validation, and Windows endpoint support.

## Live AD Infrastructure

### JLM-DC01

| Item | Value |
|---|---|
| VM ID | 160 |
| Hostname | JLM-DC01 |
| Role | Domain Controller / DNS |
| Domain | jlm.lab |
| NetBIOS | JLM |
| IP Address | 192.168.60.10 |
| VLAN | VLAN 60 LAB |
| Proxmox Bridge | vmbr1 |
| Network Path | vmbr1 -> nic0 -> 3560CX Gi0/6 access VLAN 60 |

### JLM-WIN01

| Item | Value |
|---|---|
| VM ID | 161 |
| Hostname | JLM-WIN01 |
| OS | Windows 11 Enterprise Evaluation |
| Role | Domain-joined training workstation |
| Domain | jlm.lab |
| Computer OU | OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab |
| Proxmox Bridge | vmbr1 |
| VLAN Tag | None - switchport is access VLAN 60 |

## Active Directory Structure

### Forest and Domain

| Item | Value |
|---|---|
| Forest | jlm.lab |
| Domain | jlm.lab |
| NetBIOS Name | JLM |
| First DC | JLM-DC01.jlm.lab |

### OU Structure

The following OU structure was created:

```text
DC=jlm,DC=lab
└── OU=ARIA-Lab
    ├── OU=Students
    ├── OU=Instructors
    ├── OU=Workstations
    ├── OU=Groups
    └── OU=Admins

q
