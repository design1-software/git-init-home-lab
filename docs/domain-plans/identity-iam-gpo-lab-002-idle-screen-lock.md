# Identity/IAM GPO Lab 002 - Idle Screen Lock Policy

Status: Validated by administrator
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
Lab System: jlm.lab
Validated Artifact: C:\Users\student01\Documents\lab2-gpresult.html

## Lab Objective

Create and validate a Group Policy Object that automatically locks a student workstation after a defined idle period.

This lab teaches:

* User Configuration policy scope
* OU-linked GPO behavior
* Screen saver lock enforcement
* Difference between user-side and computer-side GPO settings
* gpupdate validation
* gpresult evidence collection
* Basic GPO troubleshooting

## Environment

| Component            | Value                                       |
| -------------------- | ------------------------------------------- |
| Domain               | jlm.lab                                     |
| Domain Controller    | JLM-DC01                                    |
| Domain Controller IP | 192.168.60.10                               |
| Workstation          | JLM-WIN01                                   |
| Student User         | JLM\student01                               |
| Student User OU      | OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab       |
| Student Group        | ARIA-Students                               |
| GPO Name             | ARIA - Student Workstation Idle Screen Lock |

## Policy Scope

This GPO is linked to:

```text
OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab
```

This scope is required because the screen saver lock settings are configured under User Configuration.

Lab 001 used Computer Configuration and applied through the Workstations OU.

Lab 002 uses User Configuration and applies through the Students OU.

Core rule:

```text
Computer Configuration follows computer objects.
User Configuration follows user objects.
```

## GPO Name

```text
ARIA - Student Workstation Idle Screen Lock
```

## Policy Path

```text
User Configuration
  -> Policies
    -> Administrative Templates
      -> Control Panel
        -> Personalization
```

## Configured Policy Settings

```text
Enable screen saver: Enabled
Password protect the screen saver: Enabled
Screen saver timeout: Enabled
Screen saver timeout value: 300 seconds
Force specific screen saver: Enabled
Screen saver executable name: scrnsave.scr
```

The timeout value of 300 seconds equals 5 minutes.

## Student Instructions

1. Log in to JLM-DC01 as a domain administrator.
2. Open Group Policy Management.
3. Navigate to Forest: jlm.lab -> Domains -> jlm.lab -> ARIA-Lab -> Students.
4. Create and link a new GPO named ARIA - Student Workstation Idle Screen Lock.
5. Edit the GPO.
6. Navigate to User Configuration -> Policies -> Administrative Templates -> Control Panel -> Personalization.
7. Enable screen saver.
8. Enable password protection for the screen saver.
9. Enable screen saver timeout and set the timeout to 300 seconds.
10. Enable Force specific screen saver and set the executable to scrnsave.scr.
11. Log in to JLM-WIN01 as JLM\student01.
12. Run gpupdate /force.
13. Log off and log back in, or reboot the workstation.
14. Run gpresult /r.
15. Generate a gpresult HTML report.
16. Wait 5 minutes without moving the mouse or touching the keyboard.
17. Confirm that the workstation locks.

## Validation Commands

Run on JLM-WIN01 as JLM\student01:

```cmd
whoami
gpresult /r
gpresult /h C:\Users\student01\Documents\lab2-gpresult.html /f
```

## Expected whoami Result

```text
jlm\student01
```

## Expected gpresult Result

The idle screen lock GPO should appear under User Settings.

Expected applied GPO:

```text
Applied Group Policy Objects
-----------------------------
ARIA - Student Workstation Idle Screen Lock
```

## Expected User Experience

After 300 seconds of inactivity, JLM-WIN01 locks and requires the student password to resume.

## Required Evidence

The student must submit:

* Screenshot of the GPO linked to the Students OU
* Screenshot of the configured Personalization policy settings
* whoami output showing jlm\student01
* gpresult /r showing the idle screen lock GPO applied
* gpresult HTML report saved as lab2-gpresult.html
* Written confirmation that the workstation locked after 5 minutes

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated results:

```text
[x] student01 authenticated successfully
[x] GPO applied under USER SETTINGS
[x] ARIA-Students membership confirmed
[x] lab2-gpresult.html artifact saved
[x] Workstation locked after idle timeout
```

## Troubleshooting Path

If the workstation does not lock:

1. Confirm student01 is in OU=Students,OU=ARIA-Lab,DC=jlm,DC=lab.
2. Confirm the GPO is linked to the Students OU.
3. Confirm User Configuration settings are enabled on the GPO.
4. Confirm the settings are under User Configuration, not Computer Configuration.
5. Confirm Security Filtering includes Authenticated Users, Domain Users, or ARIA-Students.
6. Run gpupdate /force.
7. Log off and log back in.
8. Run gpresult /r.
9. Confirm the GPO appears under Applied Group Policy Objects.
10. Generate gpresult /h.
11. Save the gpresult HTML file somewhere the student can write to, such as C:\Users\student01\Documents.
12. Wait the full 5 minutes with no mouse or keyboard activity.
13. Confirm the workstation locks.

## Common Issues

### GPO Does Not Appear in gpresult

Likely causes:

* GPO is linked to the wrong OU.
* GPO is linked to Workstations instead of Students.
* User Configuration is disabled.
* Security Filtering does not include the student user or a group the student belongs to.
* The student did not log off and log back in after policy refresh.

### gpresult HTML Access Denied

If this command fails:

```cmd
gpresult /h C:\Users\Public\Desktop\lab2-gpresult.html
```

Use a student-writable location instead:

```cmd
gpresult /h C:\Users\student01\Documents\lab2-gpresult.html /f
```

The /f option forces overwrite if the file already exists.

### Workstation Does Not Lock

Likely causes:

* Policy has not refreshed.
* User has not logged off and back in.
* Wrong GPO path was configured.
* Screen saver timeout was not set to 300 seconds.
* Mouse or keyboard input occurred during the waiting period.
* Another local or domain policy conflicts with the setting.

## ARIA AI Mentor Role

ARIA should coach the student through validation and troubleshooting instead of simply giving answers.

ARIA should ask:

* Is this setting under User Configuration or Computer Configuration?
* Which OU contains student01?
* Which OU contains JLM-WIN01?
* Where is the GPO linked?
* Did gpresult /r show the GPO under Applied Group Policy Objects?
* Did you run gpupdate /force?
* Did you log off or reboot after gpupdate?
* How long did you wait before testing the lock?
* Did you save the gpresult HTML artifact in a location the student can write to?
* Did you confirm that the workstation required a password after locking?

## Key Lesson

This lab reinforces one of the most important enterprise Group Policy rules:

```text
Computer Configuration settings apply based on where the computer object lives.
User Configuration settings apply based on where the user object lives.
```

The login banner lab used Computer Configuration, so it applied through the Workstations OU.

The idle screen lock lab uses User Configuration, so it applies through the Students OU.

## Completion Status

Completed:

* GPO created
* GPO linked to Students OU
* User-side screen saver lock settings configured
* JLM-WIN01 received policy for student01
* gpresult validation completed
* HTML artifact generated
* Workstation locked after idle timeout

Next related lab:

* Identity/IAM GPO Lab 003 - Mapped Drives by Security Group

