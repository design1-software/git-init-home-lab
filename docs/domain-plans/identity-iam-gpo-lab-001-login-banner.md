# Identity/IAM GPO Lab 001 - Login Banner

Status: Validated by administrator  
Domain: Identity / IAM / Active Directory / GPO / Windows Endpoint Administration  
Lab System: jlm.lab  
Validated Artifact: C:\Users\Public\Desktop\lab1-gpresult.html

## Lab Objective

Create and validate a Group Policy Object that displays an interactive logon message on the domain-joined Windows workstation.

This lab teaches:

- Group Policy Management Console basics
- Computer Configuration policy scope
- OU-linked GPOs
- Workstation OU targeting
- gpupdate validation
- gpresult evidence collection
- Basic GPO troubleshooting

## Environment

| Component | Value |
|---|---|
| Domain | jlm.lab |
| Domain Controller | JLM-DC01 |
| Workstation | JLM-WIN01 |
| Student User | JLM\student01 |
| Target OU | OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab |
| GPO Name | ARIA - Student Workstation Login Banner |

## Policy Settings

GPO path:

Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Local Policies -> Security Options

Configured settings:

Interactive logon: Message title for users attempting to log on

ARIA Training Lab Notice

Interactive logon: Message text for users attempting to log on

This system is part of the ARIA IT training lab. Authorized lab users only. Activity may be monitored for training, troubleshooting, and security education purposes.

## Student Instructions

1. Log in to JLM-DC01 as a domain administrator.
2. Open Group Policy Management.
3. Navigate to Forest: jlm.lab -> Domains -> jlm.lab -> ARIA-Lab -> Workstations.
4. Create and link a new GPO named ARIA - Student Workstation Login Banner.
5. Edit the GPO and configure the interactive logon title and message.
6. Log in to JLM-WIN01.
7. Run gpupdate /force.
8. Reboot the workstation.
9. Confirm that the login banner appears.
10. Log in as JLM\student01.
11. Generate validation evidence.

## Required Evidence

The student must submit:

- Screenshot of the GPO linked to the Workstations OU
- Screenshot of the login banner on JLM-WIN01
- whoami output showing jlm\student01
- gpresult /r showing the login banner GPO applied
- gpresult /h HTML report saved as lab1-gpresult.html
- Short written explanation of what the GPO does

## Expected Results

Expected whoami result:

jlm\student01

Expected gpresult /r evidence:

Applied Group Policy Objects:
ARIA - Student Workstation Login Banner

Expected user experience:

Before login, JLM-WIN01 displays the ARIA Training Lab Notice.

## ARIA AI Mentor Role

ARIA should coach the student through validation and troubleshooting instead of simply giving answers.

ARIA should ask:

- What OU is JLM-WIN01 located in?
- Is the GPO linked to the correct OU?
- Is this a Computer Configuration policy or a User Configuration policy?
- Did you run gpupdate /force?
- Did you reboot after applying the policy?
- What does gpresult /r show?
- Did you generate a gpresult HTML report?

## Troubleshooting Path

If the banner does not appear:

1. Confirm JLM-WIN01 is in OU=Workstations,OU=ARIA-Lab,DC=jlm,DC=lab.
2. Confirm the GPO is linked to the Workstations OU.
3. Confirm the GPO is enabled.
4. Confirm the settings are under Computer Configuration.
5. Run gpupdate /force.
6. Reboot JLM-WIN01.
7. Run gpresult /r.
8. Generate gpresult /h C:\Users\Public\Desktop\lab1-gpresult.html.
9. Check Event Viewer if needed.

## Administrator Validation

This lab was walked end to end by the administrator before being assigned to students.

Validated artifact location:

C:\Users\Public\Desktop\lab1-gpresult.html

## Completion Status

Completed:

- GPO created
- GPO linked to Workstations OU
- JLM-WIN01 received policy
- Login banner displayed
- gpresult HTML artifact generated

Next related lab:

- Identity/IAM GPO Lab 002 - Idle Screen Lock Policy
