# Identity/IAM Future Labs Roadmap

Status: Future roadmap
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
Lab System: jlm.lab
Current Foundational Block: Complete
Active Build Count: 6 completed labs

## Purpose

This document captures future Identity/IAM, Active Directory, Group Policy, Windows endpoint administration, and security monitoring labs for ARIA.

These labs are documented as future roadmap items only.

They are not part of the current completed six-lab foundational build.

## Current Completed Foundation

The first Identity/IAM GPO training block is complete.

Completed labs:

```text
[x] Identity/IAM GPO Lab 001 - Login Banner
[x] Identity/IAM GPO Lab 002 - Idle Screen Lock Policy
[x] Identity/IAM GPO Lab 003 - Mapped Drives by Security Group
[x] Identity/IAM GPO Lab 004 - Password Policy + Weak Password Failure
[x] Identity/IAM GPO Lab 005 - Account Lockout Policy + Unlock Workflow
[x] Identity/IAM GPO Lab 006 - PowerShell Logging
```

This foundational block teaches:

* Active Directory OU structure
* Domain user authentication
* Computer-side GPOs
* User-side GPOs
* Domain-level password policy
* Domain-level account lockout policy
* GUI-based Active Directory administration
* PowerShell-based validation
* gpresult evidence collection
* Event Viewer evidence review
* Security logging basics
* Help desk documentation practices
* ARIA AI Mentor troubleshooting prompts

## Current Live Environment

Current Identity/IAM environment:

```text
Domain: jlm.lab
NetBIOS: JLM
Domain Controller: JLM-DC01
Domain Controller IP: 192.168.60.10
Workstation: JLM-WIN01
Student User: JLM\student01
Student Group: ARIA-Students
Primary Student OU: OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
Primary Workstation OU: OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

Current AD structure:

```text
DC=jlm,DC=lab
└── OU=ARIA-Lab
    ├── OU=Students
    ├── OU=Instructors
    ├── OU=Workstations
    ├── OU=Groups
    └── OU=Admins
```

## Guardrail

No future Identity/IAM lab should be built until the current completed six-lab foundation is reviewed, committed, and considered stable.

Future labs should follow the same documentation standard:

```text
1. Build the lab.
2. Validate it manually.
3. Capture evidence.
4. Document the lab.
5. Commit and push.
6. Only then move to the next lab.
```

## Future Lab Categories

The future roadmap is grouped into six categories:

```text
1. User and Account Administration
2. Group Policy Expansion
3. Access Control and Permissions
4. Security Hardening
5. Monitoring and Incident Review
6. Advanced AD / IAM Troubleshooting
```

---

# Category 1 - User and Account Administration

## Future Lab - User Creation + Group Assignment Workflow

### Purpose

Teach students how to create domain users, place them in the correct OU, assign group membership, and validate login access.

### Concepts

* ADUC user creation
* PowerShell user creation
* OU placement
* UPN and SAM account naming
* Group assignment
* Initial password handling
* Temporary password workflows
* Login validation

### GUI Workflow

Students use Active Directory Users and Computers to:

```text
1. Create a new user.
2. Place the user in the Students OU.
3. Set a temporary password.
4. Add the user to ARIA-Students.
5. Confirm group membership.
6. Validate workstation login.
```

### PowerShell Workflow

Future PowerShell commands may include:

```powershell
New-ADUser
Set-ADAccountPassword
Enable-ADAccount
Add-ADGroupMember
Get-ADUser
Get-ADGroupMember
```

### Evidence

* Screenshot of user object in Students OU
* Screenshot of group membership
* PowerShell validation output
* Successful `whoami` from JLM-WIN01

---

## Future Lab - Password Reset Workflow

### Purpose

Teach students how to reset a user password using both ADUC and PowerShell.

### Concepts

* Help desk password reset
* Temporary password assignment
* “User must change password at next logon”
* Password policy compliance
* Login validation after reset
* Ticket documentation

### GUI Workflow

Use Active Directory Users and Computers:

```text
Right-click user
Reset Password
Enter compliant temporary password
Choose whether user must change password at next logon
Confirm login behavior
```

### PowerShell Workflow

Future commands may include:

```powershell
Set-ADAccountPassword
Set-ADUser -ChangePasswordAtLogon
Unlock-ADAccount
Get-ADUser
```

### Evidence

* Screenshot of reset workflow
* PowerShell validation
* Successful student login
* Ticket-style resolution note

---

## Future Lab - Disabled Account Investigation

### Purpose

Teach students how to identify, investigate, enable, and validate disabled user accounts.

### Concepts

* Disabled account status
* ADUC Account tab
* PowerShell account status
* Help desk escalation logic
* Security caution before enabling accounts
* Ticket documentation

### GUI Workflow

Use ADUC to:

```text
1. Locate the disabled account.
2. Review account status.
3. Enable the account if authorized.
4. Confirm the user can log in.
```

### PowerShell Workflow

Future commands may include:

```powershell
Get-ADUser -Properties Enabled
Enable-ADAccount
Disable-ADAccount
Search-ADAccount -AccountDisabled
```

### Evidence

* ADUC screenshot showing disabled account
* PowerShell output showing `Enabled = False`
* PowerShell output showing `Enabled = True`
* Successful login validation

---

# Category 2 - Group Policy Expansion

## Future Lab - Lock Screen and Desktop Wallpaper

### Purpose

Teach students how to apply branding and security notices to domain workstations.

### Concepts

* Computer Configuration vs User Configuration
* Desktop personalization policy
* Lock screen policy
* File path distribution
* Workstation OU targeting
* gpresult validation

### Possible GPO Name

```text
ARIA - Student Workstation Branding
```

### Target

```text
OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

### Evidence

* Screenshot of configured GPO
* Screenshot of applied wallpaper or lock screen
* gpresult HTML report

---

## Future Lab - Restrict Control Panel Items

### Purpose

Teach students how to limit access to Control Panel settings on training workstations.

### Concepts

* User Configuration policies
* Control Panel restrictions
* Standard user limitations
* Policy-driven user experience
* Troubleshooting blocked settings

### Possible GPO Name

```text
ARIA - Student Control Panel Restrictions
```

### Target

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

### Evidence

* Screenshot of blocked Control Panel item
* gpresult report
* Written explanation of why the setting is restricted

---

## Future Lab - Pin Specific Apps to Taskbar

### Purpose

Teach students how enterprises standardize common workstation access.

### Concepts

* Start menu/taskbar layout
* XML layout files
* User experience standardization
* Workstation readiness
* Policy deployment

### Possible Apps

```text
Microsoft Edge
File Explorer
Windows Terminal
PowerShell
Active support portal shortcut
```

### Evidence

* Screenshot of taskbar layout
* GPO configuration screenshot
* gpresult HTML report

---

## Future Lab - Power Management

### Purpose

Teach students how workstation power settings can be standardized through GPO.

### Concepts

* Power plan enforcement
* Sleep settings
* Display timeout
* Energy management
* Lab workstation consistency

### Possible GPO Name

```text
ARIA - Student Workstation Power Management
```

### Evidence

* Screenshot of configured power policy
* Power settings validation from workstation
* gpresult report

---

## Future Lab - Default Browser Homepage / Start Pages

### Purpose

Teach students how enterprises set default browser start pages for support, training, or intranet resources.

### Concepts

* Browser policy
* User Configuration
* Homepage setting
* Start page enforcement
* Help desk portal access

### Possible Homepage

```text
ARIA student portal
ARIA help desk portal
Internal documentation portal
```

### Evidence

* Browser opens expected start page
* GPO setting screenshot
* gpresult report

---

# Category 3 - Access Control and Permissions

## Future Lab - Shared Folder Permission Audit

### Purpose

Teach students how to review SMB share permissions and NTFS permissions.

### Concepts

* Share permissions
* NTFS permissions
* Effective access
* Least privilege
* Group-based access
* Permission troubleshooting

### Builds From

```text
Lab 003 - Mapped Drives by Security Group
```

### GUI Workflow

Use:

```text
File Explorer
Folder Properties
Security tab
Advanced Security
Effective Access
Computer Management -> Shared Folders
```

### PowerShell Workflow

Future commands may include:

```powershell
Get-SmbShare
Get-SmbShareAccess
icacls
Get-Acl
```

### Evidence

* Share permission screenshot
* NTFS permission screenshot
* PowerShell output
* Access test as student01

---

## Future Lab - Folder Redirection

### Purpose

Teach students how enterprises redirect user folders to network storage.

### Concepts

* Folder Redirection GPO
* User data centralization
* Documents/Desktop redirection
* Offline files considerations
* Storage permissions
* User profile behavior

### Possible GPO Name

```text
ARIA - Student Folder Redirection
```

### Evidence

* Folder redirected to network location
* gpresult report
* File created in redirected folder
* Permission validation

---

## Future Lab - Printer Mapping via GPO Preferences

### Purpose

Teach students how printers are deployed to users or workstations through GPO.

### Concepts

* Shared printer deployment
* Group Policy Preferences
* Item-level targeting
* User vs computer printer mapping
* Help desk printer troubleshooting

### Evidence

* Printer appears for student01
* GPO Preferences screenshot
* gpresult report

---

## Future Lab - Restricted Groups

### Purpose

Teach students how local group membership can be controlled by domain policy.

### Concepts

* Local Administrators group management
* Restricted Groups
* Least privilege
* Workstation admin control
* Privilege drift prevention

### Evidence

* Local Administrators membership before policy
* Local Administrators membership after policy
* gpresult report

---

# Category 4 - Security Hardening

## Future Lab - Windows Defender Baseline

### Purpose

Teach students how endpoint protection settings are managed by GPO.

### Concepts

* Defender policy
* Real-time protection
* Cloud-delivered protection
* Exclusions
* Security baseline management

### Evidence

* Defender policy settings
* Workstation validation
* Event Viewer or Windows Security screenshot

---

## Future Lab - Disable SMBv1

### Purpose

Teach students why legacy protocols are security risks and how to disable SMBv1.

### Concepts

* Legacy protocol risk
* SMBv1 removal
* Windows Features
* PowerShell validation
* Security baseline enforcement

### PowerShell Validation

Future commands may include:

```powershell
Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol
```

### Evidence

* SMBv1 disabled output
* GPO/security baseline reference
* Written explanation of risk

---

## Future Lab - Disable LLMNR and NetBIOS over TCP/IP

### Purpose

Teach students how name resolution protocols can create security exposure.

### Concepts

* LLMNR
* NetBIOS over TCP/IP
* Poisoning attacks
* Windows name resolution
* GPO hardening

### Evidence

* GPO setting screenshot
* Workstation validation
* Written explanation of attack reduction

---

## Future Lab - Disable USB Storage Write Access

### Purpose

Teach students how organizations reduce data exfiltration risk through removable storage controls.

### Concepts

* Removable storage policy
* Read vs write restrictions
* Endpoint data protection
* User impact
* Security exceptions

### Evidence

* USB write restriction policy
* Workstation test
* gpresult report

---

## Future Lab - Office Macro Restrictions

### Purpose

Teach students how enterprises reduce phishing and malware risk by restricting Office macros.

### Concepts

* Macro security
* Phishing risk
* Office administrative templates
* Trusted locations
* Security baseline enforcement

### Evidence

* Macro restriction policy
* Office behavior test
* Written explanation

---

## Future Lab - AppLocker

### Purpose

Teach students application control fundamentals.

### Concepts

* Application allowlisting
* Publisher rules
* Path rules
* Executable rules
* Audit mode vs enforce mode
* Security operations impact

### Evidence

* AppLocker policy
* Blocked application test
* Event Viewer evidence

---

## Future Lab - Windows Firewall via GPO

### Purpose

Teach students how host firewall settings are centrally managed.

### Concepts

* Domain profile
* Private profile
* Public profile
* Inbound rules
* Outbound rules
* Remote administration
* Security posture

### Evidence

* Firewall policy screenshot
* Workstation firewall validation
* gpresult report

---

## Future Lab - Disable NTLMv1 / Restrict NTLM

### Purpose

Teach students why legacy authentication protocols create enterprise risk.

### Concepts

* NTLM
* NTLMv1
* Kerberos preference
* Authentication hardening
* Compatibility risk
* Audit before enforcement

### Evidence

* Policy screenshot
* Event log review
* Written explanation of compatibility considerations

---

## Future Lab - LAPS

### Purpose

Teach students how local administrator passwords are managed securely.

### Concepts

* Local Administrator Password Solution
* Local admin risk
* Password rotation
* Attribute-based password storage
* Delegated retrieval
* Least privilege

### Evidence

* LAPS policy configured
* Local admin password rotated
* Authorized retrieval validated

---

# Category 5 - Monitoring and Incident Review

## Future Lab - Event Log Review + Security Monitoring Basics

### Purpose

Teach students how to review common Windows security events.

### Concepts

* Event Viewer navigation
* Security log
* Failed logons
* Account lockouts
* PowerShell events
* Basic incident review
* Evidence screenshots

### Builds From

```text
Lab 005 - Account Lockout Policy + Unlock Workflow
Lab 006 - PowerShell Logging
```

### Event IDs

```text
4625 = Failed logon
4740 = User account locked out
4103 = PowerShell Module Logging
4104 = PowerShell Script Block Logging
```

### Evidence

* Screenshot of failed logon event
* Screenshot of account lockout event
* Screenshot of PowerShell event
* Student-written incident summary

---

## Future Lab - Help Desk Ticket Intake + AD Account Triage

### Purpose

Connect AD troubleshooting to help desk ticket workflow.

### Concepts

* Ticket intake
* User identity verification
* Account status review
* Lockout triage
* Password reset decision tree
* Escalation
* Resolution note writing

### Workflow

```text
1. Read the ticket.
2. Identify the account.
3. Confirm account status in ADUC.
4. Validate with PowerShell.
5. Resolve using approved method.
6. Document evidence.
7. Write closure note.
```

### Evidence

* Completed ticket note
* Screenshot of account validation
* Resolution confirmation

---

## Future Lab - Centralized PowerShell Transcript Share

### Purpose

Extend Lab 006 by moving transcripts from local workstation storage to a secured central share.

### Concepts

* Central logging
* Secure share permissions
* Transcript security
* Least privilege
* Audit workflow
* Security operations review

### Possible Share

```text
\\JLM-DC01\SecurityLogs\PowerShellTranscripts
```

### Evidence

* Central transcript file created
* Share permissions validated
* Event logs reviewed
* Access control documented

---

## Future Lab - Basic SIEM / Log Forwarding Integration

### Purpose

Prepare students for SOC concepts by forwarding Windows security and PowerShell logs into a monitoring platform.

### Possible Platforms

```text
Wazuh
Graylog
Elastic
Splunk Free
Windows Event Forwarding
```

### Concepts

* Log sources
* Event forwarding
* Alerting
* Dashboards
* Detection basics
* Incident review

### Evidence

* Event visible in monitoring platform
* Screenshot of alert or dashboard
* Student incident summary

---

# Category 6 - Advanced AD / IAM Troubleshooting

## Future Lab - GPO Precedence Failure

### Purpose

Teach students how GPO link order and precedence affect final policy results.

### Concepts

* Link order
* Enforced GPOs
* Block inheritance
* Winning GPO
* gpresult analysis
* Troubleshooting conflicting settings

### Evidence

* Conflicting GPOs created
* gpresult showing winning policy
* Student explains why the winning policy applied

---

## Future Lab - Wrong OU Failure Lab

### Purpose

Teach students how policies fail when linked to the wrong OU.

### Concepts

* User object location
* Computer object location
* OU targeting
* gpresult troubleshooting
* AD object movement

### Evidence

* GPO fails when linked incorrectly
* GPO applies after correct OU link
* Student explanation

---

## Future Lab - Loopback Processing Failure Lab

### Purpose

Teach students how loopback processing changes user policy behavior on specific computers.

### Concepts

* Loopback processing
* Merge mode
* Replace mode
* User settings applied by computer location
* Training kiosk or lab workstation scenarios

### Evidence

* Loopback policy configured
* gpresult validation
* Student explanation of merge vs replace

---

## Future Lab - Broken Secure Channel Failure Lab

### Purpose

Teach students how workstation trust relationship failures occur and how to repair them.

### Concepts

* Domain trust relationship
* Computer account password
* Secure channel
* Test-ComputerSecureChannel
* Domain rejoin
* Help desk escalation

### PowerShell Commands

Future commands may include:

```powershell
Test-ComputerSecureChannel
Test-ComputerSecureChannel -Repair
Reset-ComputerMachinePassword
```

### Evidence

* Failed secure channel validation
* Repair action
* Successful domain authentication

---

## Future Lab - GPO Refresh Interval Lab

### Purpose

Teach students that Group Policy does not always apply instantly and how refresh timing works.

### Concepts

* Background refresh
* Manual gpupdate
* Logoff/logon requirements
* Reboot requirements
* Computer vs user policy timing

### Evidence

* Policy not applied before refresh
* Policy applied after gpupdate/logoff/reboot
* Student explanation

---

## Future Lab - Replication Delay Lab

### Purpose

Prepare for multi-domain-controller environments by teaching AD/GPO replication concepts.

### Concepts

* SYSVOL replication
* AD replication
* DFSR
* Domain controller consistency
* Repadmin basics
* Time-based troubleshooting

### Future Requirement

This lab requires a second domain controller before it can be built.

### Evidence

* Replication status output
* GPO version comparison
* Student explanation

---

## Future Lab - Fine-Grained Password Policies

### Purpose

Teach students how password policy can differ for specific users or groups.

### Concepts

* Password Settings Objects
* Fine-grained password policies
* Precedence
* Group targeting
* Domain password policy comparison

### Future Use Case

```text
Standard students use baseline policy.
Privileged admin accounts use stricter policy.
```

### Evidence

* PSO created
* Group assigned
* Resultant password policy validated

---

## Future Lab - Kerberos Policy Review

### Purpose

Teach students the basics of Kerberos domain authentication settings.

### Concepts

* Ticket lifetime
* Renewal lifetime
* Kerberos authentication
* Domain account policy
* Security tradeoffs

### Evidence

* Kerberos policy screenshot
* Student explanation of ticket lifetime

---

## Future Lab - Microsoft Security Compliance Toolkit Baseline Import

### Purpose

Teach students how Microsoft security baselines can be imported and reviewed.

### Concepts

* Microsoft Security Compliance Toolkit
* Security baselines
* GPO backup/import
* Baseline comparison
* Production caution
* Change control

### Evidence

* Baseline imported into test GPO
* Settings reviewed
* Student identifies high-impact controls

---

# Future Documentation Standards

Every future lab should include:

```text
Lab objective
Environment
Scope
GPO name
OU or domain link target
GUI workflow
PowerShell workflow
Validation commands
Required evidence
Troubleshooting path
ARIA AI Mentor questions
Ticketing or documentation practice
Completion status
```

## GUI and PowerShell Standard

All future AD/IAM labs should clearly include both:

```text
GUI Method
PowerShell Method
```

The GUI method supports beginner confidence and real help desk workflows.

The PowerShell method supports evidence, automation, reporting, troubleshooting, and career progression into sysadmin, IAM analyst, and SOC roles.

Core teaching standard:

```text
GUI for action familiarity.
PowerShell for validation, evidence, and operational scale.
```

## ARIA AI Mentor Standard

ARIA should not simply give students answers.

ARIA should coach students using questions such as:

```text
What object are you troubleshooting?
Is this a user-side or computer-side policy?
Which OU contains the target object?
Where is the GPO linked?
What does gpresult show?
What evidence supports your conclusion?
What would you write in the ticket?
What would you escalate?
What would you check next?
```

## Current Identity/IAM Domain Status

```text
Status: Foundational six-lab block complete
Next action: Preserve completed state, document future labs, and avoid uncontrolled scope expansion
```

Completed foundational labs:

```text
[x] Lab 001 - Login Banner
[x] Lab 002 - Idle Screen Lock Policy
[x] Lab 003 - Mapped Drives by Security Group
[x] Lab 004 - Password Policy + Weak Password Failure
[x] Lab 005 - Account Lockout Policy + Unlock Workflow
[x] Lab 006 - PowerShell Logging
```

Future labs:

```text
Documented only.
Not currently built.
```
