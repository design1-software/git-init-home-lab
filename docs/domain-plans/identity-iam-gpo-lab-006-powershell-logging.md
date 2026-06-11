# Identity/IAM GPO Lab 006 - PowerShell Logging

Status: Validated by administrator
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration / Security Monitoring
Lab System: jlm.lab
Validated Artifact: C:\Users\student01\Desktop\lab6-gpresult.html

## Lab Objective

Create and validate a workstation-level Group Policy Object that enables PowerShell logging for security visibility, audit review, troubleshooting, and incident response.

This lab teaches:

* Computer Configuration GPO targeting
* Workstations OU policy scope
* PowerShell Module Logging
* PowerShell Script Block Logging
* PowerShell Transcription
* Event Viewer validation
* PowerShell transcript validation
* Difference between User Settings and Computer Settings in gpresult
* GUI validation using Group Policy Management Console and Event Viewer
* PowerShell validation using gpresult, Get-WinEvent, and transcript review
* Why PowerShell logging matters in enterprise security operations

## Environment

| Component             | Value                                         |
| --------------------- | --------------------------------------------- |
| Domain                | jlm.lab                                       |
| Domain Controller     | JLM-DC01                                      |
| Domain Controller IP  | 192.168.60.10                                 |
| Workstation           | JLM-WIN01                                     |
| Student User          | JLM\student01                                 |
| Student User OU       | OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab         |
| Target Workstation OU | OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab     |
| GPO Name              | ARIA - Student Workstation PowerShell Logging |
| GPO Link Target       | Workstations OU                               |
| Policy Type           | Computer Configuration                        |
| Transcript Folder     | C:\ARIA-Logs\PowerShellTranscripts            |
| gpresult Artifact     | C:\Users\student01\Desktop\lab6-gpresult.html |

## Important Design Note

This lab is a workstation security logging lab.

The GPO is linked to the Workstations OU because the policy is configured under Computer Configuration.

Correct target:

```text
OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

Incorrect target for this lab:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

Core rule:

```text
Computer Configuration follows computer objects.
User Configuration follows user objects.
```

PowerShell logging is a computer-side control. It should apply to the workstation regardless of which user opens PowerShell.

## Relationship to Previous Labs

Previous IAM/GPO labs included both user-side and computer-side policies:

```text
Lab 001 - Login Banner
Scope: Workstations OU
Policy Type: Computer Configuration

Lab 002 - Idle Screen Lock
Scope: Students OU
Policy Type: User Configuration

Lab 003 - Mapped Drives by Security Group
Scope: Students OU
Policy Type: User Configuration

Lab 004 - Password Policy + Weak Password Failure
Scope: Domain root
Policy Type: Domain account password policy

Lab 005 - Account Lockout Policy + Unlock Workflow
Scope: Domain root
Policy Type: Domain account lockout policy

Lab 006 - PowerShell Logging
Scope: Workstations OU
Policy Type: Computer Configuration
```

Lab 006 is intentionally scoped to the Workstations OU because PowerShell logging should follow the computer, not only the user.

## Security Purpose

PowerShell is a legitimate administrative tool, but it is also commonly abused by attackers.

This lab introduces a core enterprise security principle:

```text
PowerShell activity should be logged so administrators and security teams can review what happened.
```

PowerShell logging helps with:

* Troubleshooting
* Audit review
* Help desk escalation
* Incident response
* Detection engineering
* Security operations center investigation
* Accountability for administrative activity

## Logging Features Enabled

This lab enables three PowerShell logging controls:

```text
PowerShell Module Logging
PowerShell Script Block Logging
PowerShell Transcription
```

### Module Logging

Module Logging records PowerShell module and command activity.

This is useful for identifying commands run from PowerShell modules.

### Script Block Logging

Script Block Logging records PowerShell script blocks and command content.

This is useful for detecting suspicious PowerShell activity and reviewing what was executed.

### Transcription

Transcription creates text-based records of PowerShell sessions.

This is useful for reconstructing command-line activity during troubleshooting or investigation.

## Transcript Storage Design

For this beginner lab, transcripts are stored locally on JLM-WIN01.

Transcript path:

```text
C:\ARIA-Logs\PowerShellTranscripts
```

This is intentionally simple for student validation.

Future production design should use a secured central logging location, such as:

```text
\\JLM-DC01\SecurityLogs\PowerShellTranscripts
```

Important production note:

```text
Transcript folders may contain sensitive command output.
Access should be restricted.
```

## Create Transcript Folder

On JLM-WIN01, log in as a local administrator or domain administrator.

Open PowerShell as Administrator and run:

```powershell
New-Item -Path "C:\ARIA-Logs\PowerShellTranscripts" -ItemType Directory -Force
```

Set permissions:

```powershell
icacls "C:\ARIA-Logs\PowerShellTranscripts" /grant "Users:(OI)(CI)(M)"
icacls "C:\ARIA-Logs\PowerShellTranscripts" /grant "Administrators:(OI)(CI)(F)"
icacls "C:\ARIA-Logs\PowerShellTranscripts" /grant "SYSTEM:(OI)(CI)(F)"
```

For this lab, `Users` are granted modify access so student sessions can generate transcript files.

Production environments should use a more restrictive design.

## GPO Creation

On JLM-DC01, open Group Policy Management.

GUI path:

```text
Server Manager
  -> Tools
    -> Group Policy Management
```

Navigate to:

```text
Forest: jlm.lab
  -> Domains
    -> jlm.lab
      -> ARIA-Lab
        -> Workstations
```

Right-click:

```text
Workstations
```

Select:

```text
Create a GPO in this domain, and Link it here...
```

Name the GPO:

```text
ARIA - Student Workstation PowerShell Logging
```

## GPO Link Target

The GPO must be linked to:

```text
OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

This is required because the settings are under Computer Configuration.

## Policy Path

Edit the GPO and navigate to:

```text
Computer Configuration
  -> Policies
    -> Administrative Templates
      -> Windows Components
        -> Windows PowerShell
```

## Enable Module Logging

Open:

```text
Turn on Module Logging
```

Set:

```text
Enabled
```

Click:

```text
Show...
```

Add:

```text
*
```

This logs all PowerShell modules for lab visibility.

Final setting:

```text
Turn on Module Logging: Enabled
Module Names: *
```

## Enable Script Block Logging

Open:

```text
Turn on PowerShell Script Block Logging
```

Set:

```text
Enabled
```

If available, enable:

```text
Log script block invocation start / stop events
```

Final setting:

```text
Turn on PowerShell Script Block Logging: Enabled
```

## Enable PowerShell Transcription

Open:

```text
Turn on PowerShell Transcription
```

Set:

```text
Enabled
```

Configure:

```text
Transcript output directory: C:\ARIA-Logs\PowerShellTranscripts
Include invocation headers: Enabled
```

Final setting:

```text
Turn on PowerShell Transcription: Enabled
Transcript output directory: C:\ARIA-Logs\PowerShellTranscripts
Include invocation headers: Enabled
```

## Confirm JLM-WIN01 Is in the Correct OU

On JLM-DC01, run:

```powershell
Get-ADComputer JLM-WIN01 -Properties DistinguishedName |
Select-Object Name,DistinguishedName
```

Expected result:

```text
Name      DistinguishedName
----      -----------------
JLM-WIN01 CN=JLM-WIN01,OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

If JLM-WIN01 is not in the Workstations OU, move it before continuing.

## Confirm GPO Link

On JLM-DC01, run:

```powershell
Get-GPInheritance -Target "OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab"
```

Expected result should include:

```text
ARIA - Student Workstation PowerShell Logging
```

## Confirm GPO Status

On JLM-DC01, run:

```powershell
Get-GPO -Name "ARIA - Student Workstation PowerShell Logging" |
Select-Object DisplayName,GpoStatus
```

Expected result:

```text
DisplayName                                      GpoStatus
-----------                                      ---------
ARIA - Student Workstation PowerShell Logging    AllSettingsEnabled
```

## Apply Computer Policy

On JLM-WIN01, open Command Prompt or PowerShell as Administrator and run:

```cmd
gpupdate /target:computer /force
```

Expected result:

```text
Computer Policy update has completed successfully.
```

Restart JLM-WIN01 if needed:

```cmd
shutdown /r /t 0
```

After reboot, log back in as:

```text
JLM\student01
```

## Important gpresult Validation Note

A standard `gpresult /r` run as `student01` may show only the User Settings section.

That does not prove the PowerShell Logging GPO failed.

Lab 006 is a Computer Configuration policy, so it must be validated under:

```text
COMPUTER SETTINGS
Applied Group Policy Objects
```

not only:

```text
USER SETTINGS
Applied Group Policy Objects
```

Correct command:

```cmd
gpresult /scope computer /r
```

Expected computer-side applied GPO:

```text
ARIA - Student Workstation PowerShell Logging
```

## Generate gpresult HTML Report

On JLM-WIN01, generate the lab report:

```cmd
gpresult /h C:\Users\student01\Desktop\lab6-gpresult.html /f
```

If the report does not include Computer Details, run from an elevated prompt:

```cmd
gpresult /h C:\Users\Public\Desktop\lab6-computer-gpresult.html /scope computer /f
```

Expected evidence:

```text
Computer Details section is populated.
Applied Computer GPOs include ARIA - Student Workstation PowerShell Logging.
```

If the HTML report only shows User Details, the report is not sufficient for Lab 006 validation.

## Generate PowerShell Activity

On JLM-WIN01, log in as:

```text
JLM\student01
```

Open Windows PowerShell.

Run:

```powershell
whoami
Get-Date
Get-ComputerInfo | Select-Object CsName,WindowsProductName,OsVersion
Get-Process | Select-Object -First 5
$LabName = "ARIA PowerShell Logging Lab"
$LabName
```

Close PowerShell after running the commands.

This creates activity for transcript and event log validation.

## Validate Transcript File

On JLM-WIN01, run:

```powershell
Get-ChildItem "C:\ARIA-Logs\PowerShellTranscripts" -Recurse
```

Expected result:

```text
At least one transcript .txt file exists.
```

Open the transcript file and confirm it contains commands such as:

```text
whoami
Get-Date
Get-ComputerInfo
Get-Process
$LabName
```

## Validate PowerShell Event Logs Using GUI

On JLM-WIN01, open Event Viewer.

GUI path:

```text
Event Viewer
  -> Applications and Services Logs
    -> Microsoft
      -> Windows
        -> PowerShell
          -> Operational
```

Look for PowerShell logging events.

Useful event IDs:

```text
4103 = Module logging
4104 = Script block logging
```

Also check:

```text
Event Viewer
  -> Windows Logs
    -> Windows PowerShell
```

Module Logging may appear in the Windows PowerShell log.

## Validate PowerShell Event Logs Using PowerShell

On JLM-WIN01, run:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 20 |
Select-Object TimeCreated, Id, ProviderName, Message
```

To focus on Script Block Logging:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" |
Where-Object {$_.Id -eq 4104} |
Select-Object -First 10 TimeCreated, Id, Message
```

To focus on Module Logging:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" |
Where-Object {$_.Id -eq 4103} |
Select-Object -First 10 TimeCreated, Id, Message
```

Also check the classic Windows PowerShell log:

```powershell
Get-WinEvent -LogName "Windows PowerShell" -MaxEvents 20 |
Select-Object TimeCreated, Id, ProviderName, Message
```

## GUI Workflow Summary

The GUI workflow is appropriate for beginner students and help desk/security analyst familiarity.

Students should use GUI tools to:

```text
Create and link the GPO
Enable PowerShell logging settings
Review Group Policy Management
Review Event Viewer
Open transcript files
Confirm visible evidence
```

GUI workflow:

```text
1. Open Group Policy Management.
2. Create the PowerShell Logging GPO.
3. Link it to the Workstations OU.
4. Edit the GPO.
5. Enable Module Logging.
6. Enable Script Block Logging.
7. Enable Transcription.
8. Run gpupdate on JLM-WIN01.
9. Open Event Viewer.
10. Review PowerShell Operational logs.
11. Open the transcript folder.
12. Confirm transcript file creation.
```

## PowerShell Workflow Summary

The PowerShell workflow is appropriate for validation, evidence collection, repeatability, audit review, and security operations.

PowerShell validation commands:

```powershell
Get-ADComputer JLM-WIN01 -Properties DistinguishedName |
Select-Object Name,DistinguishedName

Get-GPO -Name "ARIA - Student Workstation PowerShell Logging" |
Select-Object DisplayName,GpoStatus

gpupdate /target:computer /force

gpresult /scope computer /r

Get-ChildItem "C:\ARIA-Logs\PowerShellTranscripts" -Recurse

Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 20 |
Select-Object TimeCreated, Id, ProviderName, Message
```

## When to Use GUI vs PowerShell

Use the GUI when:

```text
The student is learning where settings live.
The goal is visual familiarity with Group Policy Management.
The task is a one-off configuration.
The student is learning Event Viewer navigation.
The student needs to inspect transcript files manually.
```

Use PowerShell when:

```text
The task needs repeatable evidence.
The task needs filtering.
The task needs audit output.
The task is part of security operations.
The task may eventually be automated.
The student is preparing for system administration, IAM, or SOC workflows.
```

Professional pattern:

```text
GUI for configuration familiarity.
PowerShell for validation, evidence, and scale.
```

## Required Evidence

The student must submit:

* Screenshot of GPO linked to the Workstations OU
* Screenshot of Module Logging enabled
* Screenshot of Script Block Logging enabled
* Screenshot of Transcription enabled
* Screenshot or output confirming JLM-WIN01 is in the Workstations OU
* Screenshot or output of `gpupdate /target:computer /force`
* Screenshot or output of `gpresult /scope computer /r`
* HTML report saved as `lab6-gpresult.html`
* Screenshot showing PowerShell commands executed by `student01`
* Screenshot of transcript folder
* Screenshot of transcript file contents showing PowerShell commands
* Screenshot of Event Viewer showing PowerShell Operational events
* Screenshot or output showing Event ID 4103 or 4104
* Short written explanation of why PowerShell logging matters

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated results:

```text
[x] Transcript folder created
[x] PowerShell logging GPO created
[x] GPO linked to Workstations OU
[x] Module Logging configured
[x] Script Block Logging configured
[x] PowerShell Transcription configured
[x] JLM-WIN01 received computer policy
[x] gpresult evidence collected
[x] PowerShell activity generated
[x] Transcript file created
[x] Transcript content reviewed
[x] Event Viewer PowerShell logs reviewed
[x] Lab validated by administrator
```

## Troubleshooting Path

If the PowerShell Logging GPO does not appear:

1. Confirm JLM-WIN01 is in the Workstations OU.
2. Confirm the GPO is linked to the Workstations OU.
3. Confirm the GPO status is AllSettingsEnabled.
4. Confirm the settings are under Computer Configuration.
5. Confirm the GPO was not accidentally linked only to the Students OU.
6. Run `gpupdate /target:computer /force`.
7. Reboot JLM-WIN01 if needed.
8. Run `gpresult /scope computer /r`.
9. Generate a computer-scope HTML report.
10. Check Event Viewer -> Microsoft -> Windows -> GroupPolicy -> Operational.
11. Confirm the transcript folder exists.
12. Confirm users have permission to write transcript files.
13. Open PowerShell and generate activity.
14. Re-check transcript files.
15. Re-check PowerShell Operational logs.

## Common Issues

### Only User GPOs Appear in gpresult

If `gpresult /r` only shows:

```text
ARIA - Student Mapped Drive
ARIA - Student Workstation Idle Screen Lock
```

that is likely the User Settings section.

Lab 006 must be checked under Computer Settings.

Run:

```cmd
gpresult /scope computer /r
```

### Computer Details Shows No Data Available

If the HTML report shows:

```text
Computer Details: No data available
```

the report is not sufficient for Lab 006.

Run gpresult from an elevated prompt:

```cmd
gpresult /h C:\Users\Public\Desktop\lab6-computer-gpresult.html /scope computer /f
```

### GPO Linked to Wrong OU

If the GPO is linked to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

it may not apply as expected because the policy is computer-scoped.

Correct link:

```text
OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab
```

### Transcript File Is Not Created

Check:

```text
C:\ARIA-Logs\PowerShellTranscripts exists.
student01 has write permission.
PowerShell was opened after policy applied.
Computer policy was refreshed.
The workstation was rebooted if needed.
```

Validate permissions:

```powershell
icacls "C:\ARIA-Logs\PowerShellTranscripts"
```

### Event ID 4104 Not Found

If 4104 is not visible:

1. Confirm Script Block Logging is enabled.
2. Run new PowerShell commands.
3. Close and reopen PowerShell.
4. Refresh Event Viewer.
5. Use `Get-WinEvent`.
6. Confirm you are checking `Microsoft-Windows-PowerShell/Operational`.

### Event ID 4103 Not Found

If 4103 is not visible:

1. Confirm Module Logging is enabled.
2. Confirm `*` is entered under module names.
3. Run PowerShell commands again.
4. Check both:

   * Microsoft-Windows-PowerShell/Operational
   * Windows PowerShell

## Security Considerations

PowerShell logs and transcripts may contain sensitive information.

Examples:

```text
Command history
File paths
Script content
Usernames
System information
Command output
Potential secrets accidentally typed into the shell
```

For a production environment:

```text
Use restricted transcript folders.
Do not allow standard users to read other users' transcripts.
Forward logs to a SIEM or log collector.
Monitor for suspicious PowerShell behavior.
Protect event logs from tampering.
Consider Protected Event Logging for sensitive environments.
```

## ARIA AI Mentor Role

ARIA should coach students through investigation instead of simply giving answers.

ARIA should ask:

* Is this a User Configuration or Computer Configuration policy?
* Which OU contains JLM-WIN01?
* Is the GPO linked to the Workstations OU?
* Did you run `gpupdate /target:computer /force`?
* Did you check Computer Settings or only User Settings?
* Does `gpresult /scope computer /r` show the logging GPO?
* Does the transcript folder exist?
* Can the student user write to the transcript folder?
* Did you run PowerShell commands after the policy applied?
* Did a transcript file get created?
* Which commands appear in the transcript?
* Which Event Viewer log stores Script Block Logging?
* Did you find Event ID 4104?
* Did you find Event ID 4103?
* Why is PowerShell logging important for enterprise security?

## Ticketing / Security Documentation Practice

Students should write a short security validation note after completing the lab.

Example:

```text
Validated PowerShell logging on JLM-WIN01. Confirmed the PowerShell Logging GPO is linked to the Workstations OU and applied through computer policy. Generated PowerShell activity as JLM\student01, reviewed transcript output under C:\ARIA-Logs\PowerShellTranscripts, and confirmed PowerShell event log evidence in Event Viewer. Logging is active and ready for audit/security monitoring practice.
```

## Key Lesson

This lab reinforces a core security operations principle:

```text
Administrative activity should be observable.
```

A professional validation workflow requires:

```text
1. Confirm the computer is in the correct OU.
2. Confirm the GPO is linked correctly.
3. Confirm the correct policy scope.
4. Refresh computer policy.
5. Generate real PowerShell activity.
6. Validate transcript output.
7. Validate event log output.
8. Collect evidence.
9. Document the result.
```

## Completion Status

Completed:

* PowerShell logging GPO created
* GPO linked to Workstations OU
* Module Logging enabled
* Script Block Logging enabled
* Transcription enabled
* JLM-WIN01 policy refreshed
* PowerShell activity generated
* Transcript evidence validated
* Event log evidence validated
* gpresult evidence collected
* Lab ready for documentation and student assignment

Next related lab:

* Identity/IAM GPO Lab 007 - Event Log Review + Security Monitoring Basics
