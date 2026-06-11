# Identity/IAM GPO Lab 005 - Account Lockout Policy + Unlock Workflow

Status: Validated by administrator
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
Lab System: jlm.lab
Validated Artifact: C:\Users\student01\Documents\lab5-gpresult.html

## Lab Objective

Create and validate a domain-level account lockout policy that locks a user account after repeated failed sign-in attempts, then complete a proper unlock workflow using both the Active Directory GUI and PowerShell validation.

This lab teaches:

* Domain-level account lockout policy enforcement
* Failed sign-in behavior
* Account lockout detection
* Active Directory Users and Computers unlock workflow
* PowerShell validation workflow
* Security event review
* Difference between help desk GUI operations and administrative PowerShell workflows
* Safe remediation after account lockout
* Evidence collection for IAM support tickets

## Environment

| Component            | Value                                 |
| -------------------- | ------------------------------------- |
| Domain               | jlm.lab                               |
| Domain Controller    | JLM-DC01                              |
| Domain Controller IP | 192.168.60.10                         |
| Workstation          | JLM-WIN01                             |
| Test User            | JLM\student01                         |
| Test User OU         | OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab |
| GPO Name             | ARIA - Domain Account Lockout Policy  |
| GPO Link Target      | Domain root: jlm.lab                  |
| Policy Type          | Domain account lockout policy         |

## Important Design Note

This lab builds on Lab 004 but focuses on a different IAM control.

```text
Lab 004 - Password Policy + Weak Password Failure
Purpose: Prevent weak passwords.

Lab 005 - Account Lockout Policy + Unlock Workflow
Purpose: Lock accounts after repeated failed sign-in attempts and practice safe unlock workflows.
```

For standard Active Directory domain users, account lockout policy is a domain-level account policy.

Correct target:

```text
DC=jlm,DC=lab
```

Incorrect target for this lab:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

Core rule:

```text
Domain account lockout policy belongs at the domain root, not only inside a user OU.
```

## Final Account Lockout Policy Baseline

The final validated lockout baseline is:

```text
Account lockout threshold: 5 invalid logon attempts
Account lockout duration: 15 minutes
Reset account lockout counter after: 15 minutes
```

The existing Lab 004 password policy values remained intact:

```text
Minimum password age: 0 days
Maximum password age: 90 days
Minimum password length: 12 characters
Password history maintained: 24 passwords remembered
Password must meet complexity requirements: Enabled
Store passwords using reversible encryption: Disabled
```

## Why This Lab Uses 5 Attempts

A threshold of 5 invalid attempts is strict enough to demonstrate account lockout clearly but not so aggressive that the lab environment becomes difficult to manage.

This setting is appropriate for training because it allows students to:

* Trigger lockout intentionally
* Observe failed authentication behavior
* Confirm the account lockout state
* Practice unlock workflow
* Document the incident like a help desk or IAM ticket

## GPO Configuration

Create and link a GPO named:

```text
ARIA - Domain Account Lockout Policy
```

Link it to the domain root:

```text
jlm.lab
```

Equivalent LDAP target:

```text
DC=jlm,DC=lab
```

## Policy Path

Edit the GPO and navigate to:

```text
Computer Configuration
  -> Policies
    -> Windows Settings
      -> Security Settings
        -> Account Policies
          -> Account Lockout Policy
```

## Configured Policy Settings

Configure the following:

```text
Account lockout threshold: 5 invalid logon attempts
Account lockout duration: 15 minutes
Reset account lockout counter after: 15 minutes
```

If Windows prompts that related values will be adjusted automatically, accept the prompt as long as the final values remain:

```text
Threshold = 5
Duration = 15
Reset counter = 15
```

## Domain Root Link Validation

Run on JLM-DC01:

```powershell
Get-GPInheritance -Target "DC=jlm,DC=lab"
```

Expected result should include:

```text
ARIA - Domain Account Lockout Policy
ARIA - Domain Password Policy Baseline
Default Domain Policy
```

The account lockout GPO should be linked at the domain root.

## GPO Precedence

The account lockout policy GPO should have proper precedence at the domain root.

Run on JLM-DC01 if needed:

```powershell
Set-GPLink -Name "ARIA - Domain Account Lockout Policy" -Target "DC=jlm,DC=lab" -Order 1
```

Then verify:

```powershell
Get-GPInheritance -Target "DC=jlm,DC=lab"
```

Important:

The lockout GPO should only contain Account Lockout Policy settings.

Do not configure Password Policy settings inside this GPO unless the lab specifically requires it.

This prevents Lab 005 from accidentally overriding Lab 004.

## GPO Status Validation

Run on JLM-DC01:

```powershell
Get-GPO -Name "ARIA - Domain Account Lockout Policy" | Select-Object DisplayName,GpoStatus
```

Expected result:

```text
DisplayName                           GpoStatus
-----------                           ---------
ARIA - Domain Account Lockout Policy  AllSettingsEnabled
```

## Apply Computer Policy

Account lockout policy settings are under Computer Configuration.

Run on JLM-DC01:

```powershell
gpupdate /target:computer /force
```

Expected output:

```text
Computer Policy update has completed successfully.
```

## Policy Validation After Change

Run on JLM-DC01:

```powershell
net accounts
```

Expected output:

```text
Minimum password age (days): 0
Maximum password age (days): 90
Minimum password length: 12
Length of password history maintained: 24
Lockout threshold: 5
Lockout duration (minutes): 15
Lockout observation window (minutes): 15
Computer role: PRIMARY
```

Run:

```powershell
Get-ADDefaultDomainPasswordPolicy
```

Expected output:

```text
ComplexityEnabled: True
LockoutDuration: 00:15:00
LockoutObservationWindow: 00:15:00
LockoutThreshold: 5
MaxPasswordAge: 90.00:00:00
MinPasswordAge: 00:00:00
MinPasswordLength: 12
PasswordHistoryCount: 24
ReversibleEncryptionEnabled: False
```

## Confirm student01 Starts Clean

Before triggering lockout, confirm `student01` is enabled and not already locked.

Run on JLM-DC01:

```powershell
Unlock-ADAccount -Identity student01

Get-ADUser student01 -Properties Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt,PasswordExpired |
Select-Object SamAccountName,Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt,PasswordExpired
```

Expected:

```text
Enabled: True
LockedOut: False
PasswordExpired: False
```

## Trigger Account Lockout

On JLM-WIN01, sign out of `student01`.

At the Windows sign-in screen, attempt to sign in as:

```text
JLM\student01
```

Use an intentionally wrong password 5 times.

Example wrong password:

```text
WrongPass123!
```

After the fifth failed attempt, stop.

Do not continue attempting to sign in after the account locks.

## Confirm Lockout Using the GUI

On JLM-DC01, open Active Directory Users and Computers.

GUI path:

```text
Server Manager
  -> Tools
    -> Active Directory Users and Computers
```

Alternative launch method:

```text
Windows + R
dsa.msc
```

Navigate to:

```text
jlm.lab
  -> ARIA-Lab
    -> Students
      -> student01
```

Right-click:

```text
student01
```

Select:

```text
Properties
```

Go to:

```text
Account tab
```

Expected GUI evidence:

```text
Unlock account. This account is currently locked out on this Active Directory Domain Controller.
```

This is the beginner/help desk workflow for confirming a locked account.

## Confirm Lockout Using PowerShell

Run on JLM-DC01:

```powershell
Get-ADUser student01 -Properties Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt |
Select-Object SamAccountName,Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt
```

Expected:

```text
Enabled: True
LockedOut: True
BadLogonCount: 5 or higher
LastBadPasswordAttempt: Recent timestamp
```

Also run:

```powershell
Search-ADAccount -LockedOut
```

Expected result:

```text
student01
```

This is the administrative validation workflow.

## Review Security Event Evidence

On JLM-DC01, open Event Viewer.

GUI path:

```text
Event Viewer
  -> Windows Logs
    -> Security
```

Look for common account lockout and failed sign-in event IDs:

```text
4625 = Failed logon
4740 = User account locked out
```

PowerShell option:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4740} -MaxEvents 5 |
Select-Object TimeCreated, Id, ProviderName, Message
```

If Event ID 4740 is not immediately visible, check failed logons:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 10 |
Select-Object TimeCreated, Id, ProviderName, Message
```

## Unlock Account Using the GUI

In Active Directory Users and Computers:

```text
student01
  -> Properties
    -> Account tab
```

Check:

```text
Unlock account. This account is currently locked out on this Active Directory Domain Controller.
```

Then click:

```text
Apply
OK
```

This is the primary beginner/help desk unlock method.

## Validate Unlock Using PowerShell

Run on JLM-DC01:

```powershell
Get-ADUser student01 -Properties Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt |
Select-Object SamAccountName,Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt
```

Expected:

```text
Enabled: True
LockedOut: False
```

If the GUI unlock does not clear the lockout, use the PowerShell fallback:

```powershell
Unlock-ADAccount -Identity student01
```

Then verify again:

```powershell
Get-ADUser student01 -Properties Enabled,LockedOut |
Select-Object SamAccountName,Enabled,LockedOut
```

Expected:

```text
student01   True   False
```

## Validate Successful Login After Unlock

On JLM-WIN01, log in as:

```text
JLM\student01
```

Use the correct compliant password.

Once logged in, run:

```cmd
whoami
```

Expected:

```text
jlm\student01
```

Generate supporting workstation evidence:

```cmd
gpresult /h C:\Users\student01\Documents\lab5-gpresult.html /f
```

Important note:

For this lab, the strongest evidence is collected on the domain controller:

```text
net accounts
Get-ADDefaultDomainPasswordPolicy
Get-ADUser LockedOut=True
Search-ADAccount -LockedOut
ADUC lockout confirmation
Event Viewer / Security log evidence
Get-ADUser LockedOut=False after unlock
```

The workstation `gpresult` report is supporting evidence only.

## GUI Workflow Summary

The GUI workflow is appropriate for beginner students and help desk realism.

Use Active Directory Users and Computers for:

```text
Account status checks
Password resets
Unlocking locked accounts
Disabling accounts
Enabling accounts
Viewing group membership
Basic user object review
```

For Lab 005, the GUI workflow is:

```text
1. Open Active Directory Users and Computers.
2. Browse to ARIA-Lab -> Students.
3. Open student01 properties.
4. Go to the Account tab.
5. Confirm the account is locked.
6. Check Unlock account.
7. Click Apply.
8. Click OK.
```

## PowerShell Workflow Summary

PowerShell is appropriate for validation, evidence collection, bulk administration, automation, and escalation-level troubleshooting.

Use PowerShell for:

```text
Finding locked accounts
Checking account properties
Auditing failed login states
Unlocking accounts at scale
Creating evidence for tickets
Repeating administrative workflows consistently
```

For Lab 005, the PowerShell workflow is:

```powershell
Get-ADUser student01 -Properties Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt |
Select-Object SamAccountName,Enabled,LockedOut,BadLogonCount,LastBadPasswordAttempt

Search-ADAccount -LockedOut

Unlock-ADAccount -Identity student01

Get-ADUser student01 -Properties Enabled,LockedOut |
Select-Object SamAccountName,Enabled,LockedOut
```

## When to Use GUI vs PowerShell

Use the GUI when:

```text
The task is a one-off help desk action.
The student is learning AD object navigation.
The goal is visual familiarity with Active Directory.
The task is password reset, unlock, enable, disable, or group review for one user.
```

Use PowerShell when:

```text
The task needs evidence.
The task must be repeated.
The task affects multiple users.
The task needs audit output.
The issue requires fast filtering or reporting.
The student is preparing for sysadmin, IAM analyst, or automation work.
```

ARIA should teach both paths.

The correct professional pattern is:

```text
GUI for action familiarity.
PowerShell for verification and operational scale.
```

## Required Evidence

The student must submit:

* Screenshot or output of `net accounts` before lockout policy change
* Screenshot or output of `Get-ADDefaultDomainPasswordPolicy` before lockout policy change
* Screenshot of `ARIA - Domain Account Lockout Policy` linked to the domain root
* Screenshot of Account Lockout Policy settings
* Screenshot or output of `gpupdate /target:computer /force`
* Screenshot or output of `net accounts` after policy change
* Screenshot or output of `Get-ADDefaultDomainPasswordPolicy` after policy change
* Screenshot of failed sign-in attempt behavior on JLM-WIN01
* Screenshot of ADUC showing `student01` locked out
* Screenshot or output of `Get-ADUser` showing `LockedOut = True`
* Screenshot or output of `Search-ADAccount -LockedOut` showing `student01`
* Screenshot or output of Security log evidence, preferably Event ID 4740 or 4625
* Screenshot of ADUC unlock action or confirmation
* Screenshot or output of `Get-ADUser` showing `LockedOut = False`
* Screenshot or output of successful `whoami` after unlock
* `lab5-gpresult.html` saved under `C:\Users\student01\Documents`

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated results:

```text
[x] Account lockout policy GPO created
[x] GPO linked to domain root
[x] Account lockout threshold set to 5
[x] Lockout duration set to 15 minutes
[x] Lockout observation/reset window set to 15 minutes
[x] Lab 004 password policy values remained intact
[x] Computer policy update completed successfully
[x] net accounts confirmed threshold = 5
[x] Get-ADDefaultDomainPasswordPolicy confirmed lockout values
[x] student01 was intentionally locked out
[x] ADUC GUI workflow confirmed locked status
[x] PowerShell confirmed LockedOut = True
[x] Search-ADAccount -LockedOut confirmed student01
[x] Security event evidence reviewed
[x] student01 was unlocked
[x] PowerShell confirmed LockedOut = False
[x] student01 was ready for continued labs
```

## Troubleshooting Path

If the account does not lock out:

1. Confirm the GPO is linked to the domain root.
2. Confirm the target is `DC=jlm,DC=lab`.
3. Confirm the GPO is not only linked to the Students OU.
4. Confirm the settings are under Computer Configuration.
5. Confirm the path is Account Policies -> Account Lockout Policy.
6. Confirm the GPO status is AllSettingsEnabled.
7. Confirm GPO precedence at the domain root.
8. Run `gpupdate /target:computer /force` on JLM-DC01.
9. Re-run `net accounts`.
10. Confirm lockout threshold is 5.
11. Confirm observation window is 15.
12. Confirm you are testing against `JLM\student01`.
13. Confirm you are using the wrong password exactly 5 times.
14. Stop testing after lockout occurs.
15. Verify with ADUC and PowerShell.

## Common Issues

### Testing Against the Wrong Account

Do not test lockout against:

```text
JLM\Administrator
```

Use only:

```text
JLM\student01
```

### GPO Linked to Students OU

If the GPO is linked only to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

the domain account lockout policy will not behave as expected for normal domain account policy.

Correct link:

```text
DC=jlm,DC=lab
```

### Only User Policy Updates

If `gpupdate` only reports:

```text
User Policy update has completed successfully.
```

That is not enough for this lab.

Account lockout policy is under Computer Configuration.

Run:

```powershell
gpupdate /target:computer /force
```

Expected:

```text
Computer Policy update has completed successfully.
```

### Password Policy Values Accidentally Changed

Lab 005 should not undo Lab 004.

After applying Lab 005, confirm:

```text
Minimum password length: 12
Password history: 24
Maximum password age: 90
Minimum password age: 0
Complexity enabled: True
Reversible encryption: False
```

If those values revert, check whether the lockout GPO accidentally contains Password Policy settings or has unexpected precedence behavior.

### Account Does Not Unlock in GUI

If ADUC does not clear the lockout, use:

```powershell
Unlock-ADAccount -Identity student01
```

Then verify:

```powershell
Get-ADUser student01 -Properties LockedOut
```

### Event 4740 Not Found Immediately

If Event ID 4740 is not immediately visible, check Event ID 4625 failed logons:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 10 |
Select-Object TimeCreated, Id, ProviderName, Message
```

## ARIA AI Mentor Role

ARIA should coach students through investigation, not simply give the answer.

ARIA should ask:

* What is the account lockout threshold?
* Where should domain account lockout policy be linked?
* Is this a Computer Configuration or User Configuration policy?
* Did you confirm `net accounts` after applying the GPO?
* Which account are you testing against?
* How many failed sign-in attempts did you perform?
* Did the account show as locked in ADUC?
* Did PowerShell confirm `LockedOut = True`?
* Did `Search-ADAccount -LockedOut` find the account?
* Did you review Event Viewer?
* Did you unlock the account using the GUI or PowerShell?
* Did you validate successful login after unlock?
* What evidence would you attach to a help desk ticket?

## Ticketing / Help Desk Documentation Practice

Students should write a short ticket resolution note after completing the lab.

Example:

```text
User reported being unable to sign in. Verified account lockout in Active Directory Users and Computers and confirmed LockedOut=True using PowerShell. Reviewed failed logon evidence. Unlocked the account through ADUC, validated account status changed to LockedOut=False, and confirmed the user could sign in successfully. No password reset was required.
```

This connects the IAM lab to real help desk workflow.

## Key Lesson

This lab reinforces a core IAM principle:

```text
Account lockout is both a security control and a support workflow.
```

A professional workflow requires:

```text
1. Confirm the policy.
2. Trigger or identify the lockout.
3. Validate the locked state.
4. Review evidence.
5. Unlock safely.
6. Confirm successful access.
7. Document the resolution.
```

## Completion Status

Completed:

* Account lockout policy baseline created
* Domain-level GPO linked to jlm.lab
* Lockout threshold configured
* Lockout duration configured
* Lockout observation window configured
* Lab 004 password policy preserved
* student01 lockout tested
* GUI lockout workflow validated
* PowerShell lockout workflow validated
* student01 unlocked
* Lab ready for documentation and student assignment

Next related lab:

* Identity/IAM GPO Lab 006 - PowerShell Logging











