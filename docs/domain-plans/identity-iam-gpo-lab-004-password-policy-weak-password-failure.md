# Identity/IAM GPO Lab 004 - Password Policy + Weak Password Failure

Status: Validated by administrator
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
Lab System: jlm.lab
Validated Artifact: C:\Users\student01\Documents\lab4-gpresult.html

## Lab Objective

Create and validate a domain-level password policy baseline that prevents weak passwords from being assigned to Active Directory users.

This lab teaches:

* Domain-level password policy enforcement
* Difference between OU-linked GPOs and domain account policy
* Computer Configuration policy scope
* Password complexity requirements
* Minimum password length enforcement
* Password history retention
* Weak password failure validation
* Safe student account recovery after password policy testing
* Evidence collection using `net accounts`, `Get-ADDefaultDomainPasswordPolicy`, and `gpresult`

## Environment

| Component            | Value                                  |
| -------------------- | -------------------------------------- |
| Domain               | jlm.lab                                |
| Domain Controller    | JLM-DC01                               |
| Domain Controller IP | 192.168.60.10                          |
| Workstation          | JLM-WIN01                              |
| Test User            | JLM\student01                          |
| Test User OU         | OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab  |
| GPO Name             | ARIA - Domain Password Policy Baseline |
| GPO Link Target      | Domain root: jlm.lab                   |
| Policy Type          | Domain account password policy         |

## Important Design Note

This lab is different from the previous GPO labs.

Labs 001, 002, and 003 used OU-linked GPOs:

```text
Lab 001 - Login Banner: linked to Workstations OU
Lab 002 - Idle Screen Lock: linked to Students OU
Lab 003 - Mapped Drive: linked to Students OU
```

Lab 004 uses a domain-level account policy.

For standard Active Directory domain users, the effective domain password policy must be configured at the domain level.

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
Domain password policy belongs at the domain root, not only inside a user OU.
```

## Initial Baseline Before Change

The existing domain password policy was checked before applying the ARIA baseline.

Commands run on JLM-DC01:

```powershell
net accounts
Get-ADDefaultDomainPasswordPolicy
```

Initial observed baseline:

```text
Minimum password age: 1 day
Maximum password age: 42 days
Minimum password length: 7
Password history maintained: 24
Complexity enabled: True
Reversible encryption enabled: False
Lockout threshold: Never / 0
Lockout duration: 30 minutes
Lockout observation window: 30 minutes
```

## Final ARIA Password Policy Baseline

The final validated domain password policy baseline is:

```text
Minimum password age: 0 days
Maximum password age: 90 days
Minimum password length: 12 characters
Password history maintained: 24 passwords remembered
Password must meet complexity requirements: Enabled
Store passwords using reversible encryption: Disabled
Lockout threshold: Never / 0
Lockout duration: 30 minutes
Lockout observation window: 30 minutes
```

## Why Password History Stayed at 24

The initial recommendation was to use 5 passwords remembered.

During baseline review, the existing domain policy already had:

```text
Password history maintained: 24
```

Because 24 is stronger than 5, the administrator preserved the stronger existing value instead of weakening the policy.

Final decision:

```text
Keep password history at 24.
```

## Why Lockout Was Not Changed

Account lockout settings were intentionally left unchanged.

Current lockout setting:

```text
Lockout threshold: Never / 0
```

Lockout policy will be handled separately in:

```text
Identity/IAM GPO Lab 005 - Account Lockout Policy + Unlock Workflow
```

This prevents Lab 004 from overlapping with Lab 005.

## GPO Configuration

Create and link a GPO named:

```text
ARIA - Domain Password Policy Baseline
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
          -> Password Policy
```

## Configured Policy Settings

Configure the following:

```text
Enforce password history: 24 passwords remembered
Maximum password age: 90 days
Minimum password age: 0 days
Minimum password length: 12 characters
Password must meet complexity requirements: Enabled
Store passwords using reversible encryption: Disabled
```

## Domain Root Link Validation

Run on JLM-DC01:

```powershell
Get-GPInheritance -Target "DC=jlm,DC=lab"
```

Expected result:

```text
ARIA - Domain Password Policy Baseline
Default Domain Policy
```

The ARIA password baseline GPO should be linked at the domain root.

## GPO Precedence

The ARIA password policy GPO should have higher precedence than the Default Domain Policy for this lab.

Run on JLM-DC01 if needed:

```powershell
Set-GPLink -Name "ARIA - Domain Password Policy Baseline" -Target "DC=jlm,DC=lab" -Order 1
```

Then verify:

```powershell
Get-GPInheritance -Target "DC=jlm,DC=lab"
```

## GPO Status Validation

Run on JLM-DC01:

```powershell
Get-GPO -Name "ARIA - Domain Password Policy Baseline" | Select-Object DisplayName,GpoStatus
```

Expected result:

```text
DisplayName                            GpoStatus
-----------                            ---------
ARIA - Domain Password Policy Baseline AllSettingsEnabled
```

## Apply Computer Policy

Password policy settings are under Computer Configuration.

Run on JLM-DC01:

```powershell
gpupdate /target:computer /force
```

Expected output:

```text
Computer Policy update has completed successfully.
```

## Post-Change Validation

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
Lockout threshold: Never
Lockout duration (minutes): 30
Lockout observation window (minutes): 30
Computer role: PRIMARY
```

Run:

```powershell
Get-ADDefaultDomainPasswordPolicy
```

Expected output:

```text
ComplexityEnabled: True
MaxPasswordAge: 90.00:00:00
MinPasswordAge: 00:00:00
MinPasswordLength: 12
PasswordHistoryCount: 24
ReversibleEncryptionEnabled: False
LockoutThreshold: 0
```

## Weak Password Failure Test

The administrator validated that weak passwords were rejected.

Run on JLM-DC01:

```powershell
Set-ADAccountPassword -Identity student01 -Reset -NewPassword (ConvertTo-SecureString "password" -AsPlainText -Force)
```

Expected result:

```text
The password does not meet the length, complexity, or history requirement of the domain.
```

Run a second weak password test:

```powershell
Set-ADAccountPassword -Identity student01 -Reset -NewPassword (ConvertTo-SecureString "Student1" -AsPlainText -Force)
```

Expected result:

```text
The password does not meet the length, complexity, or history requirement of the domain.
```

Both weak password failures were confirmed during administrator validation.

## Student Account Safety Check

The administrator confirmed that `student01` already had a compliant password.

The existing password met the hardened policy requirements:

```text
15 characters
Uppercase letters
Lowercase letters
Numbers
Two special characters
```

Because the account already had a compliant password, the administrator did not reset `student01`.

This preserved the working student login state.

## Optional Recovery Command

If a future student account needs to be reset after testing, use a compliant password.

Example:

```powershell
Set-ADAccountPassword -Identity student01 -Reset -NewPassword (ConvertTo-SecureString "StudentPass123!" -AsPlainText -Force)
Set-ADUser -Identity student01 -ChangePasswordAtLogon $false
Unlock-ADAccount -Identity student01
Enable-ADAccount -Identity student01
```

Verify:

```powershell
Get-ADUser student01 -Properties Enabled,LockedOut,PasswordExpired,PasswordLastSet |
Select-Object SamAccountName,Enabled,LockedOut,PasswordExpired,PasswordLastSet
```

Expected:

```text
student01   True   False   False
```

## Workstation Validation

Log in to JLM-WIN01 as:

```text
JLM\student01
```

Run:

```cmd
whoami
```

Expected:

```text
jlm\student01
```

Generate a Group Policy report:

```cmd
gpresult /h C:\Users\student01\Documents\lab4-gpresult.html /f
```

Important note:

The workstation `gpresult` report is supporting evidence only.

The strongest evidence for this lab is collected on the domain controller:

```text
net accounts
Get-ADDefaultDomainPasswordPolicy
Weak password rejection errors
Successful student01 login after policy hardening
```

## Required Evidence

The student must submit:

* Screenshot or output of `net accounts` before the policy change
* Screenshot or output of `Get-ADDefaultDomainPasswordPolicy` before the policy change
* Screenshot of `ARIA - Domain Password Policy Baseline` linked to the domain root
* Screenshot of the configured Password Policy settings
* Screenshot or output of `gpupdate /target:computer /force`
* Screenshot or output of `net accounts` after the policy change
* Screenshot or output of `Get-ADDefaultDomainPasswordPolicy` after the policy change
* Screenshot or output showing weak password `"password"` rejected
* Screenshot or output showing weak password `"Student1"` rejected
* Confirmation that `student01` still has a compliant working password
* Screenshot or output of `whoami` from JLM-WIN01 showing `jlm\student01`
* `lab4-gpresult.html` saved under `C:\Users\student01\Documents`

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated results:

```text
[x] Initial domain password policy captured
[x] ARIA - Domain Password Policy Baseline created
[x] GPO linked to domain root
[x] GPO configured under Computer Configuration
[x] Computer policy update completed successfully
[x] Minimum password length changed from 7 to 12
[x] Maximum password age changed from 42 days to 90 days
[x] Minimum password age changed from 1 day to 0 days
[x] Password history preserved at 24
[x] Complexity remained enabled
[x] Reversible encryption remained disabled
[x] Lockout threshold remained unchanged for Lab 005
[x] Weak password "password" rejected
[x] Weak password "Student1" rejected
[x] student01 confirmed to already have a compliant password
```

## Troubleshooting Path

If the password policy does not update:

1. Confirm the GPO is linked to the domain root.
2. Confirm the target is `DC=jlm,DC=lab`.
3. Confirm the GPO is not only linked to the Students OU.
4. Confirm the settings are under Computer Configuration.
5. Confirm the path is Account Policies -> Password Policy.
6. Confirm the GPO status is AllSettingsEnabled.
7. Confirm the ARIA password policy GPO has higher precedence than Default Domain Policy.
8. Run `gpupdate /target:computer /force` on JLM-DC01.
9. Re-run `net accounts`.
10. Re-run `Get-ADDefaultDomainPasswordPolicy`.
11. Confirm the domain controller is the primary domain controller.
12. Check Group Policy Management for link order and inheritance.

## Common Issues

### Only User Policy Updates

If `gpupdate` only reports:

```text
User Policy update has completed successfully.
```

That is not enough for this lab.

Password policy is under Computer Configuration.

Run:

```powershell
gpupdate /target:computer /force
```

Expected:

```text
Computer Policy update has completed successfully.
```

### GPO Linked to Students OU

If the GPO is linked only to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

the domain password policy will not behave as expected for normal domain account policy.

Correct link:

```text
DC=jlm,DC=lab
```

### Default Domain Policy Still Winning

If `net accounts` still shows the old values:

```text
Minimum password age: 1
Maximum password age: 42
Minimum password length: 7
```

then Default Domain Policy may still be winning.

Set the ARIA password GPO to link order 1:

```powershell
Set-GPLink -Name "ARIA - Domain Password Policy Baseline" -Target "DC=jlm,DC=lab" -Order 1
```

Then run:

```powershell
gpupdate /target:computer /force
net accounts
Get-ADDefaultDomainPasswordPolicy
```

### Weak Password Unexpectedly Works

If a weak password is accepted, verify:

```text
Minimum password length is 12
ComplexityEnabled is True
The GPO is linked to the domain root
Computer policy was updated
The command was run against the correct domain user
```

## ARIA AI Mentor Role

ARIA should coach the student through validation and troubleshooting instead of simply giving answers.

ARIA should ask:

* Where should a domain password policy be linked?
* Is this a domain-level account policy or a normal OU-linked user policy?
* Is the setting under Computer Configuration or User Configuration?
* What does `net accounts` show before the change?
* What does `Get-ADDefaultDomainPasswordPolicy` show before the change?
* Did the student preserve stronger existing settings instead of weakening them?
* Did `gpupdate` update computer policy?
* What does `net accounts` show after the change?
* Was the weak password rejected?
* Does `student01` still have a compliant working password?
* Why are lockout settings reserved for the next lab?

## Key Lesson

This lab reinforces a critical Active Directory principle:

```text
Domain account password policy is not the same as a normal OU-linked user GPO.
```

For normal domain users, the effective password policy is controlled at the domain level.

A correct validation path is:

```text
1. Capture current domain password policy.
2. Link password policy GPO at the domain root.
3. Configure the password baseline under Computer Configuration.
4. Force computer policy update.
5. Validate with net accounts.
6. Validate with Get-ADDefaultDomainPasswordPolicy.
7. Attempt weak password and confirm failure.
8. Confirm student account still works with a compliant password.
```

## Completion Status

Completed:

* Baseline password policy reviewed
* Domain-level password policy GPO created
* GPO linked to domain root
* Password policy configured
* Computer policy updated
* Domain password policy hardened
* Weak password failure validated
* student01 preserved with compliant password

Next related lab:

* Identity/IAM GPO Lab 005 - Account Lockout Policy + Unlock Workflow
