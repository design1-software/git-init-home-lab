# ARIA Student Onboarding Guide

Welcome to ARIA, the hands-on IT Enterprise Training Platform.

ARIA is designed to give you realistic practice with help desk operations, Windows domain administration, Linux systems, networking, documentation, ticketing, troubleshooting, and guided learning through the ARIA AI Mentor.

This document gives you the access information and reference instructions you need to begin training. Keep this document somewhere safe and refer back to it when you need to access your training tools.

> Instructor note: Fill in the password blanks manually before sending this document to each student. Do not commit passwords to GitHub.

---

## 1. Your ARIA Training Identity

Each ARIA student receives three main identities:

1. **Windows / Active Directory account** — used for Windows domain labs.
2. **Zammad help desk account** — used for ticketing and support workflow labs.
3. **Linux container account** — used for Linux command-line, troubleshooting, automation, and sysadmin labs.

Your usernames are intentionally matched across systems as much as possible so that training stays simple.

---

## 2. Student Access Summary

### Sha Neal Prather

| System | Value |
|---|---|
| ARIA Student ID | `student01` |
| Windows / AD Username | `student01` |
| Domain Login Format | `JLM\student01` |
| Domain UPN | `student01@jlm.lab` |
| Temporary Windows Password | ______________________________ |
| Zammad Login | `student01` |
| Zammad Password | ______________________________ |
| Linux Hostname | `student-linux-01` |
| Linux Username | `student01` |
| Linux Password | ______________________________ |
| Tailscale IP | `100.76.81.39` |
| Local Lab IP | ______________________________ |

### Dominique Davis

| System | Value |
|---|---|
| ARIA Student ID | `student02` |
| Windows / AD Username | `student02` |
| Domain Login Format | `JLM\student02` |
| Domain UPN | `student02@jlm.lab` |
| Temporary Windows Password | ______________________________ |
| Zammad Login | `student02` |
| Zammad Password | ______________________________ |
| Linux Hostname | `student-linux-02` |
| Linux Username | `student02` |
| Linux Password | ______________________________ |
| Tailscale IP | `100.91.190.9` |
| Local Lab IP | ______________________________ |

---

## 3. ARIA Training Domains

ARIA is organized into training domains. These domains are designed to feel like real IT work instead of isolated practice exercises.

### Help Desk / Ticketing

You will use Zammad to practice receiving, reading, updating, and documenting support tickets. You will learn how to communicate clearly, collect evidence, write useful notes, escalate when needed, and close tickets correctly.

Skills you will practice:

- Reading ticket details.
- Asking the right troubleshooting questions.
- Adding clear ticket notes.
- Documenting what changed.
- Knowing when to escalate.
- Writing professional user-facing responses.

### Windows / Active Directory / Identity

You will use the `jlm.lab` Windows domain to practice enterprise identity concepts. This includes domain login, user accounts, groups, workstations, Group Policy, password behavior, account lockouts, and Windows endpoint troubleshooting.

Skills you will practice:

- Logging into a Windows domain workstation.
- Understanding domain usernames and UPNs.
- Checking group membership.
- Understanding Group Policy behavior.
- Recognizing account lockouts and password issues.
- Using Windows troubleshooting commands.

### Linux / SysAdmin

Each student has a dedicated Linux container. This gives you a safe place to practice Linux commands, permissions, files, services, networking tools, SSH, logs, package management, and basic automation.

Skills you will practice:

- Logging into Linux with SSH.
- Using the command line safely.
- Navigating files and directories.
- Checking services and logs.
- Using sudo properly.
- Running basic network tests.
- Writing beginner shell commands.

### Networking / DNS / VLAN / Troubleshooting

You will learn how devices communicate across the ARIA lab network. The early labs focus on Windows network troubleshooting, DNS, gateway testing, reachability, and evidence collection. Cisco switching labs will be added later as dedicated hardware becomes available.

Skills you will practice:

- Reading IP address information.
- Understanding gateways and DNS servers.
- Using `ping`, `tracert`, `nslookup`, and related tools.
- Distinguishing DNS problems from routing or firewall problems.
- Documenting network evidence for escalation.

### Security / SOC / Monitoring

Security labs will introduce basic monitoring, alert review, evidence collection, and incident response thinking. The goal is not just to click through alerts, but to understand what happened and how to explain it clearly.

Skills you will practice:

- Reading security alerts.
- Collecting basic evidence.
- Identifying suspicious behavior.
- Writing incident notes.
- Understanding escalation paths.

### ARIA AI Mentor

The ARIA AI Mentor is your guided learning assistant. It is designed to help you reason through problems, explain concepts, and ask better troubleshooting questions. It should guide your thinking, not simply give you the answer.

Use the AI Mentor to:

- Ask what a command means.
- Understand an error message.
- Review your troubleshooting notes.
- Practice explaining a fix.
- Prepare for the next step in a lab.

---

## 4. How to Log Into Windows Domain Labs

When you are assigned a Windows lab workstation, use your ARIA domain login.

### Login format

Use one of the following formats:

```text
JLM\studentXX
```

or:

```text
studentXX@jlm.lab
```

Replace `studentXX` with your assigned student ID.

Examples:

```text
JLM\student01
JLM\student02
```

### First login password behavior

Your instructor may require you to change your password at first login. If prompted, create a strong password and store it securely.

Do not share your password with other students.

---

## 5. How to Log Into Zammad

Zammad is the help desk ticketing system used in ARIA.

Use Zammad to review assigned tickets, add troubleshooting notes, and practice help desk documentation.

### Zammad access

| Item | Value |
|---|---|
| Zammad URL | ______________________________ |
| Username | Your ARIA student ID, such as `student01` or `student02` |
| Password | Provided by instructor |

### Zammad expectations

When working a ticket:

1. Read the full ticket before responding.
2. Identify the reported issue.
3. Add internal notes with your troubleshooting steps.
4. Avoid guessing; document what you tested.
5. Escalate when you cannot prove the root cause.
6. Keep responses professional and clear.

---

## 6. How to Log Into Your Linux Container

Each student has a dedicated Linux container. You can connect by SSH using your Linux username and the container IP address.

### SSH format

```bash
ssh your-username@your-linux-ip
```

Examples:

```bash
ssh student01@100.76.81.39
ssh student02@100.91.190.9
```

When prompted, enter your Linux password.

### First commands to run after login

After logging in, run:

```bash
whoami
hostname
hostname -I
sudo -l
```

Expected results:

- `whoami` should show your Linux username.
- `hostname` should show your assigned Linux container name.
- `hostname -I` should show your IP addresses.
- `sudo -l` should show whether you can run admin commands with sudo.

---

## 7. Your Linux Container Reference

### Sha Neal Prather

```text
Student ID: student01
Linux Hostname: student-linux-01
Linux Username: student01
Tailscale IP: 100.76.81.39
SSH Command: ssh student01@100.76.81.39
```

### Dominique Davis

```text
Student ID: student02
Linux Hostname: student-linux-02
Linux Username: student02
Tailscale IP: 100.91.190.9
SSH Command: ssh student02@100.91.190.9
```

---

## 8. Basic Troubleshooting Commands

These commands are safe beginner commands that you will use often.

### Windows commands

```cmd
whoami
hostname
ipconfig /all
ping 192.168.60.1
ping 192.168.60.10
ping 1.1.1.1
nslookup jlm.lab
nslookup google.com
tracert 1.1.1.1
gpresult /r
```

### Linux commands

```bash
whoami
hostname
hostname -I
ip addr
ip route
ping -c 4 1.1.1.1
ping -c 4 google.com
systemctl status ssh --no-pager
sudo -l
```

### What to document when something fails

When you have an issue, collect:

```text
1. What system were you using?
2. What username were you logged in with?
3. What command did you run?
4. What result did you expect?
5. What error or output did you actually get?
6. What troubleshooting steps did you already try?
```

This is how real help desk and sysadmin work is documented.

---

## 9. Training Rules and Expectations

1. Do not share passwords.
2. Do not use another student account.
3. Do not delete files, users, tickets, or services unless a lab specifically tells you to.
4. Document your work clearly.
5. Ask questions when you are unsure.
6. Treat each lab like a real IT ticket.
7. Learn the reason behind each command, not just the command itself.

---

## 10. First-Day Checklist

Use this checklist during your first ARIA session.

```text
[ ] I can log into my Windows/domain account.
[ ] I know my ARIA student ID.
[ ] I can log into Zammad.
[ ] I can find or view a ticket in Zammad.
[ ] I can SSH into my Linux container.
[ ] I ran whoami on Windows and Linux.
[ ] I ran hostname on Windows and Linux.
[ ] I know where to write down troubleshooting evidence.
[ ] I know how to ask the ARIA AI Mentor for help.
```

---

## 11. Who to Contact for Help

| Need | Contact / Location |
|---|---|
| Password reset | ______________________________ |
| Zammad access issue | ______________________________ |
| Linux SSH issue | ______________________________ |
| Lab question | ______________________________ |
| ARIA AI Mentor issue | ______________________________ |

---

## 12. Instructor Notes

Before sending this document to a student:

```text
[ ] Fill in the student's temporary Windows password.
[ ] Fill in the student's Zammad password.
[ ] Fill in the student's Linux password.
[ ] Fill in the Zammad URL.
[ ] Fill in support/contact blanks.
[ ] Remove the other student's access section if sending individualized copies.
[ ] Confirm no private phone numbers or personal email addresses are included unless intentionally added outside the repo copy.
```
