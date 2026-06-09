# Identity / IAM / Active Directory / GPO / Windows Endpoint Lab Plan

This document defines the v1 closeout plan for the Identity / IAM / Active Directory / GPO / Windows Endpoint Administration domain.

## Current Status

Identity / IAM is the least developed ARIA training domain.

Completed or partially completed:

- Local AI Mentor role model exists
- Admin / instructor / student / viewer separation exists
- Student account pattern exists

Important boundary:

Local ARIA application roles are not a substitute for Active Directory, GPO, domain join, Windows endpoint administration, or enterprise IAM training.

## v1 Closeout Scope

The Identity / IAM domain is complete for v1 only when the following are implemented and tested:

- VLAN 60 LAB path is validated and documented
- Active Directory Domain Controller VM is deployed
- AD forest/domain structure is defined
- Windows client lab exists
- Windows client can join the domain
- IAM ticket workflows exist
- User / group / OU / GPO / domain join evidence templates exist
- AD/IAM mentor workflows exist
- Student can submit AD/IAM evidence
- Instructor can review and complete AD/IAM submissions
- Audit trail exists for AD/IAM lab submissions

## Network Plan

| Item | Value |
|---|---|
| VLAN | 60 |
| Name | LAB |
| Subnet | 192.168.60.0/24 |
| Gateway | 192.168.60.1 |
| Existing purpose | Schoolmate remote lab |
| Hypervisor | Proxmox |
| Remote access goal | Tailscale subnet routing for remote student access |
| Current network note | VLAN 60 is documented as active/pre-staged with LAB-ACL live and DHCP pool active; validate live switch, DHCP, ACL, trunk, and Proxmox tagging before deploying AD |

## AD Forest / Domain Plan

| Item | Value |
|---|---|
| Forest root domain | jlm.lab |
| NetBIOS name | JLM |
| Domain Controller role | AD DS + DNS |
| First DC hostname | JLM-DC01 |
| Windows client hostname | JLM-WIN01 |
| Initial lab OU root | ARIA-Lab |
| Student users OU | ARIA-Lab/Students |
| Instructor users OU | ARIA-Lab/Instructors |
| Workstations OU | ARIA-Lab/Workstations |
| Groups OU | ARIA-Lab/Groups |
| Service/admin OU | ARIA-Lab/Admins |

## VLAN 60 Validation Plan

Before deploying Active Directory, validate VLAN 60 instead of rebuilding it.

Required checks:

- Confirm 3560CX has VLAN 60 defined.
- Confirm VLAN 60 SVI exists at 192.168.60.1.
- Confirm VLAN 60 has no HSRP and uses the physical 3560CX SVI as gateway.
- Confirm LAB-ACL is present and applied as designed.
- Confirm DHCP pool for 192.168.60.0/24 exists.
- Confirm Gi0/2 trunk toward GS308EP carries VLAN 60.
- Confirm GS308EP trunk carries VLAN 60 toward the Proxmox path if needed.
- Confirm Proxmox can attach a VM NIC tagged for VLAN 60.
- Confirm a test workload on VLAN 60 can reach 192.168.60.1.
- Confirm allowed DNS/AD paths work.
- Confirm blocked inter-VLAN paths remain blocked.

Do not deploy the Domain Controller until VLAN 60 validation is complete.

## Initial VM Plan

### Domain Controller

| Item | Value |
|---|---|
| VM name | JLM-DC01 |
| OS | Windows Server 2022 Evaluation or newer available Windows Server eval |
| Network | VLAN 60 LAB |
| IP plan | Static IP inside 192.168.60.0/24 |
| Role | AD DS, DNS |
| Domain | jlm.lab |

### Windows Client

| Item | Value |
|---|---|
| VM name | JLM-WIN01 |
| OS | Windows 10/11 Evaluation or available Windows client ISO |
| Network | VLAN 60 LAB |
| IP plan | DHCP or static in 192.168.60.0/24 |
| Role | Domain-joined workstation |
| Domain | jlm.lab |

## Foundational GPOs

The first GPO labs should include:

- Password policy awareness
- Account lockout policy awareness
- Login banner
- Local administrator restriction
- Desktop/control panel restriction
- Windows security baseline setting
- Mapped resource or shortcut policy
- OU-linked policy validation

## Initial IAM Skills

Students should learn to:

- Create a user
- Disable a user
- Reset a password
- Unlock an account
- Add a user to a group
- Remove a user from a group
- Verify OU placement
- Join a Windows client to the domain
- Confirm DNS points to the domain controller
- Run `gpresult`
- Use `rsop.msc`
- Check Event Viewer for domain/GPO issues
- Document evidence safely

## Initial Ticket Workflows

The first IAM ticket workflows should include:

| Ticket | Topic |
|---|---|
| IAM-001 | New user onboarding |
| IAM-002 | Password reset and account unlock |
| IAM-003 | Group membership access request |
| IAM-004 | Computer cannot join domain |
| IAM-005 | GPO not applying |
| IAM-006 | User disabled / offboarding |
| IAM-007 | DNS misconfiguration preventing domain join |
| IAM-008 | Windows endpoint support requiring AD verification |

## Evidence Requirements

Students must provide safe evidence such as:

- ADUC user or OU state, described without exposing sensitive data
- Group membership verification
- Domain join status
- DNS configuration
- `gpresult` output
- `rsop.msc` result summary
- Event Viewer finding summary
- GPMC link or policy state summary
- Professional resolution summary

Students must not submit:

- Passwords
- Recovery keys
- API keys
- Session cookies
- Private keys
- Sensitive personal data
- Full screenshots containing unrelated private information

## Mentor Workflow Requirements

ARIA should coach students to:

- Verify identity and scope first
- Confirm affected user, computer, group, OU, and domain
- Check DNS before domain join troubleshooting
- Check OU placement before GPO troubleshooting
- Check group membership before access troubleshooting
- Gather evidence before recommending changes
- Explain risk, validation, and rollback
- Write a professional help desk or IAM resolution note

## Completion Boundary

Identity / IAM v1 is not complete until:

- The AD lab exists
- At least one Windows client can join the domain
- Student AD/IAM evidence templates exist
- IAM ticket workflows exist
- AD/IAM mentor workflows are tested
- Documentation and roadmap are updated
- The KB is rebuilt


---

## Training Asset Management Boundary

AD-based asset management is a primary learning track for this domain.

The VLAN 60 `jlm.lab` domain is allowed to manage training assets, including:

- Domain-joined Windows training clients
- Training-only Windows servers
- Training file shares
- Training printer objects
- Training application server objects
- Simulated department workstations
- Lab computer objects
- Lab OUs
- Lab security groups
- Lab GPO scopes
- Lab onboarding/offboarding workflows

The VLAN 60 training domain must not manage real production infrastructure assets in v1, including:

- Real Cisco C1111 router
- Real Catalyst 3560CX switch
- Real Proxmox host management plane
- Real Pi-hole DNS service
- Real UniFi controller
- Real CUPS/printing service
- Real household, guest, IoT, or MGMT assets
- Real credentials or secrets used to administer the home lab

Training labs may simulate enterprise asset management on VLAN 60 using training-only systems and objects.

Future production asset management, if needed, must be planned separately from the student training domain.


---

## Training Asset Management Boundary

AD-based asset management is a primary learning track for this domain.

The VLAN 60 `jlm.lab` domain is allowed to manage training assets, including:

- Domain-joined Windows training clients
- Training-only Windows servers
- Training file shares
- Training printer objects
- Training application server objects
- Simulated department workstations
- Lab computer objects
- Lab OUs
- Lab security groups
- Lab GPO scopes
- Lab onboarding/offboarding workflows

The VLAN 60 training domain must not manage real production infrastructure assets in v1, including:

- Real Cisco C1111 router
- Real Catalyst 3560CX switch
- Real Proxmox host management plane
- Real Pi-hole DNS service
- Real UniFi controller
- Real CUPS/printing service
- Real household, guest, IoT, or MGMT assets
- Real credentials or secrets used to administer the home lab

Training labs may simulate enterprise asset management on VLAN 60 using training-only systems and objects.

Future production asset management, if needed, must be planned separately from the student training domain.

