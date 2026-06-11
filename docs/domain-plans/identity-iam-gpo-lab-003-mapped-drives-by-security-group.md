# Identity/IAM GPO Lab 003 - Mapped Drives by Security Group

Status: Validated by administrator
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
Lab System: jlm.lab
Validated Artifact: C:\Users\student01\Documents\lab3-gpresult.html

## Lab Objective

Create and validate a Group Policy Object that maps a shared network drive for student users based on Active Directory access control.

This lab teaches:

* SMB shared folder creation
* NTFS permission design
* Share permission design
* Active Directory group-based access
* Group Policy Preferences Drive Maps
* User Configuration policy scope
* Difference between manual UNC access and GPO-based drive mapping
* gpresult evidence collection
* Troubleshooting mapped drive failures

## Environment

| Component            | Value                                 |
| -------------------- | ------------------------------------- |
| Domain               | jlm.lab                               |
| Domain Controller    | JLM-DC01                              |
| Domain Controller IP | 192.168.60.10                         |
| Workstation          | JLM-WIN01                             |
| Student User         | JLM\student01                         |
| Student User OU      | OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab |
| Student Group        | ARIA-Students                         |
| Share Server         | JLM-DC01                              |
| Local Folder Path    | C:\Shares\StudentShare                |
| Share Name           | StudentShare                          |
| UNC Path             | \JLM-DC01\StudentShare                |
| Drive Letter         | S:                                    |
| GPO Name             | ARIA - Student Mapped Drive           |

## Policy Scope

This GPO is linked to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

This scope is required because the mapped drive is configured under User Configuration.

Core rule:

```text
Computer Configuration follows computer objects.
User Configuration follows user objects.
```

Since the mapped drive is assigned to a user at logon, the GPO follows the `student01` user object in the Students OU.

## Shared Folder Design

The shared folder is hosted on JLM-DC01.

```text
Local folder: C:\Shares\StudentShare
Share name: StudentShare
UNC path: \\JLM-DC01\StudentShare
Mapped drive letter: S:
```

A test file was created in the share:

```text
welcome.txt
```

## PowerShell Build Commands

Run on JLM-DC01 as a domain administrator.

### Create the folder

```powershell
New-Item -Path "C:\Shares\StudentShare" -ItemType Directory -Force
```

### Create a test file

```powershell
Set-Content -Path "C:\Shares\StudentShare\welcome.txt" -Value "Welcome to the ARIA student shared drive."
```

### Create the SMB share

```powershell
New-SmbShare -Name "StudentShare" -Path "C:\Shares\StudentShare" -ChangeAccess "JLM\ARIA-Students" -FullAccess "JLM\Domain Admins"
```

### Verify SMB share access

```powershell
Get-SmbShare -Name "StudentShare"
Get-SmbShareAccess -Name "StudentShare"
```

Expected share access:

```text
JLM\ARIA-Students    Change
JLM\Domain Admins    Full
```

### Configure NTFS permissions

```powershell
icacls "C:\Shares\StudentShare" /inheritance:r
icacls "C:\Shares\StudentShare" /grant "JLM\Domain Admins:(OI)(CI)(F)"
icacls "C:\Shares\StudentShare" /grant "JLM\ARIA-Students:(OI)(CI)(M)"
icacls "C:\Shares\StudentShare" /grant "SYSTEM:(OI)(CI)(F)"
```

### Verify NTFS permissions

```powershell
icacls "C:\Shares\StudentShare"
```

Expected NTFS access:

```text
JLM\ARIA-Students:(OI)(CI)(M)
JLM\Domain Admins:(OI)(CI)(F)
SYSTEM:(OI)(CI)(F)
```

## Confirm Student Group Membership

Run on JLM-DC01:

```powershell
Get-ADGroupMember "ARIA-Students"
```

Expected result:

```text
student01
```

If student01 is missing, add the user:

```powershell
Add-ADGroupMember -Identity "ARIA-Students" -Members "student01"
```

## Manual Share Validation

Before creating the mapped drive GPO, validate the share manually from JLM-WIN01.

Log in to JLM-WIN01 as:

```text
JLM\student01
```

Run:

```cmd
whoami
net use \\JLM-DC01\StudentShare
dir \\JLM-DC01\StudentShare
```

Expected result:

```text
whoami = jlm\student01
net use \\JLM-DC01\StudentShare = The command completed successfully.
dir \\JLM-DC01\StudentShare = welcome.txt is visible.
```

This proves SMB permissions and NTFS permissions are working before testing Group Policy.

## GPO Configuration

Create and link a GPO named:

```text
ARIA - Student Mapped Drive
```

Link it to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

Edit the GPO and navigate to:

```text
User Configuration
  -> Preferences
    -> Windows Settings
      -> Drive Maps
```

Create a new mapped drive.

## Drive Map Settings

General tab:

```text
Action: Update
Location: \\JLM-DC01\StudentShare
Reconnect: Checked
Label as: ARIA Student Share
Drive Letter: S:
```

Common tab:

```text
Run in logged-on user's security context: Checked
Item-level targeting: Optional after baseline validation
```

For baseline validation, item-level targeting may be left unchecked because the GPO is already linked to the Students OU.

After baseline validation, item-level targeting can be reintroduced:

```text
New Item -> Security Group
Group: JLM\ARIA-Students
User in group: selected
```

## GPO Permissions

The GPO must allow the student user to read and apply the policy.

Recommended simple baseline:

```text
Security Filtering: Authenticated Users
Drive Map Item-Level Targeting: JLM\ARIA-Students
```

Run on JLM-DC01:

```powershell
Set-GPPermission -Name "ARIA - Student Mapped Drive" -TargetName "Authenticated Users" -TargetType Group -PermissionLevel GpoApply
```

Confirm GPO status:

```powershell
Get-GPO -Name "ARIA - Student Mapped Drive" | Select-Object DisplayName,GpoStatus
```

Expected:

```text
AllSettingsEnabled
```

## Validation Commands

Run on JLM-WIN01 as JLM\student01.

First delete any manual S: drive mapping to ensure a clean GPO test:

```cmd
net use S: /delete
```

Force user policy:

```cmd
gpupdate /target:user /force
```

Log off:

```cmd
logoff
```

Log back in as:

```text
JLM\student01
```

Then validate:

```cmd
whoami
net use
dir S:\
```

Expected results:

```text
whoami = jlm\student01
S: maps to \\JLM-DC01\StudentShare
dir S:\ shows welcome.txt
```

Generate the HTML Group Policy report:

```cmd
gpresult /h C:\Users\student01\Documents\lab3-gpresult.html /f
```

## Expected gpresult HTML Evidence

The HTML report should show:

```text
Drive Map (Drive: S:)
Result: Success
Winning GPO: ARIA - Student Mapped Drive
Location: \\JLM-DC01\StudentShare
Drive Letter: S:
Reconnect: Enabled
Label as: ARIA Student Share
```

The report should also show the user context:

```text
User name: JLM\student01
Domain: jlm.lab
Organizational Unit: jlm.lab/ARIA-Lab/Students
```

## Required Evidence

The student must submit:

* Screenshot of successful manual access to \JLM-DC01\StudentShare
* Screenshot or command output showing `whoami = jlm\student01`
* Screenshot or command output showing `net use`
* Screenshot or command output showing `S:` mapped to \JLM-DC01\StudentShare
* Screenshot or command output showing `dir S:\` with welcome.txt visible
* gpresult HTML report saved as lab3-gpresult.html
* Screenshot from gpresult HTML showing `Drive Map (Drive: S:)`
* Screenshot from gpresult HTML showing `Result: Success`
* Screenshot from gpresult HTML showing `Winning GPO: ARIA - Student Mapped Drive`

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated results:

```text
[x] Shared folder created on JLM-DC01
[x] SMB share created
[x] NTFS permissions configured
[x] ARIA-Students group validated
[x] student01 manually accessed \\JLM-DC01\StudentShare
[x] welcome.txt was visible through UNC path
[x] GPO created and linked to Students OU
[x] S: drive mapped successfully
[x] gpresult HTML artifact generated
[x] Drive Map result showed Success
[x] Winning GPO correctly showed ARIA - Student Mapped Drive
```

## Troubleshooting Path

If the S: drive does not map:

1. Confirm student01 is in OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab.
2. Confirm the GPO is linked to the Students OU.
3. Confirm the GPO status is AllSettingsEnabled.
4. Confirm the GPO is under User Configuration, not Computer Configuration.
5. Confirm the Drive Map item is inside the correct GPO.
6. Confirm the Drive Map item is not disabled.
7. Confirm the UNC path is exactly \JLM-DC01\StudentShare.
8. Confirm Run in logged-on user's security context is checked.
9. Temporarily remove item-level targeting for baseline validation.
10. Confirm Security Filtering includes Authenticated Users or another group that can apply the GPO.
11. Run gpupdate /target:user /force.
12. Log off and log back in.
13. Run net use.
14. Run dir S:.
15. Generate gpresult HTML and inspect the Drive Maps section.
16. Check Event Viewer -> Applications and Services Logs -> Microsoft -> Windows -> GroupPolicy -> Operational.

## Common Issues

### Manual UNC Works but S: Does Not Map

This means SMB and NTFS permissions are working, but the Group Policy Preference item is failing.

Likely causes:

```text
GPO not applying
Drive Map item disabled
Wrong GPO edited
Wrong GPO linked
User Configuration disabled
Security Filtering blocks the user
Item-level targeting filters out the user
Drive letter conflict
Policy not refreshed after logon
```

### S: Maps but gpresult Shows the Wrong Winning GPO

This means the Drive Map preference item was created in the wrong GPO.

In this lab, this issue occurred during administrator validation.

The Drive Map was initially found under:

```text
ARIA - Student Workstation Idle Screen Lock
```

It was corrected by removing the Drive Map item from the idle screen lock GPO and placing it under:

```text
ARIA - Student Mapped Drive
```

Correct final result:

```text
Drive Map (Drive: S:)
Result: Success
Winning GPO: ARIA - Student Mapped Drive
```

### Yellow Triangle on the Drive Map Item

A yellow overlay on a Group Policy Preference item may appear when item-level targeting is enabled.

This does not automatically mean the item is broken.

Check the item status panel:

```text
Disabled directly: No
Run in user's context: Yes
Filtered directly: Yes
```

If troubleshooting, temporarily remove item-level targeting, validate the drive mapping, then reintroduce targeting after baseline success.

### gpresult /r Does Not Clearly Show Drive Maps

Group Policy Preferences may be easier to validate in the HTML report.

Use:

```cmd
gpresult /h C:\Users\student01\Documents\lab3-gpresult.html /f
```

Then inspect:

```text
User Details
  -> Preferences
    -> Windows Settings
      -> Drive Maps
```

## ARIA AI Mentor Role

ARIA should coach the student through validation and troubleshooting instead of simply giving answers.

ARIA should ask:

* Can you access \JLM-DC01\StudentShare manually?
* Does `dir \\JLM-DC01\StudentShare` show welcome.txt?
* Is student01 a member of ARIA-Students?
* Is the GPO linked to the Students OU?
* Is the Drive Map under User Configuration?
* Is the Drive Map item inside the correct GPO?
* Does gpresult HTML show the Drive Maps extension?
* What does the HTML report list as the Winning GPO?
* Is the failure a permissions problem, a GPO application problem, or a Drive Map preference problem?
* Did you delete any manual S: mapping before testing the GPO?
* Did you log off and log back in after gpupdate?

## Key Lesson

This lab reinforces an enterprise IAM principle:

```text
Access to a resource and automatic mapping of that resource are separate controls.
```

Manual UNC access proves that permissions work.

The mapped drive proves that Group Policy Preferences successfully delivered the resource to the user.

The clean validation path is:

```text
1. Prove the share works manually.
2. Prove the GPO applies.
3. Prove the mapped drive appears.
4. Prove gpresult shows the correct winning GPO.
```

## Completion Status

Completed:

* Shared folder created
* SMB share configured
* NTFS permissions configured
* ARIA-Students access validated
* Manual UNC access validated
* GPO created
* GPO linked to Students OU
* Drive Map preference configured
* S: drive mapped successfully
* gpresult HTML generated
* Correct Winning GPO validated

Next related lab:

* Identity/IAM GPO Lab 004 - Password Policy + Weak Password Failure
