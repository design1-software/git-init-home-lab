# ARIA Student Onboarding Guide — Dominique Davis

Welcome to ARIA, the hands-on IT Enterprise Training Platform.

ARIA is designed to give you realistic practice with help desk operations, Windows domain administration, Linux systems, networking, documentation, ticketing, troubleshooting, and guided learning through the ARIA AI Mentor.

Keep this document somewhere safe. It is your reference for accessing ARIA and understanding where each training tool fits.

> Instructor note: Fill in password blanks manually before sending. Do not commit passwords to GitHub.

---

## 1. Student Identity

| Item | Value |
|---|---|
| Student Name | Dominique Davis |
| ARIA Student ID | `student02` |
| Windows / AD Username | `student02` |
| Domain Login Format | `JLM\student02` |
| Domain UPN | `student02@jlm.lab` |
| Zammad Login | `student02` |
| Linux Username | `student02` |
| Linux Container | `student-linux-02` |
| Linux Tailscale IP | `100.91.190.9` |

---

## 2. Passwords

Fill these in manually before sending the document.

| System | Username | Password |
|---|---|---|
| Windows / Active Directory | `student02` | ______________________________ |
| Zammad Help Desk | `student02` | ______________________________ |
| ARIA AI Mentor | `student02` | ______________________________ |
| Linux Container | `student02` | ______________________________ |

---

## 3. ARIA Systems You Will Use

ARIA uses multiple systems because real enterprise IT work uses multiple systems.

| System | Purpose |
|---|---|
| Windows / Active Directory | Windows domain login, identity, groups, GPO, endpoint labs |
| Zammad | Help desk ticketing and support workflow labs |
| ARIA AI Mentor | Guided troubleshooting coach and lab mentor |
| Linux Container | Linux command line, sysadmin, SSH, service, log, and automation practice |
| Tailscale | Secure remote/private network path to lab systems |

---

## 4. ARIA AI Mentor Access

The ARIA AI Mentor is the guided training assistant. It helps you work through tickets and labs by asking questions, requiring evidence, and helping you understand command output.

### AI Mentor URL

```text
http://192.168.70.30:8081/student
```

If you are redirected to login, use:

```text
http://192.168.70.30:8081/login
```

### AI Mentor login

| Item | Value |
|---|---|
| Username | `student02` |
| Password | ______________________________ |
| Role | `student` |

### How to use the AI Mentor

Use the AI Mentor when you need help understanding a ticket, lab step, command output, or troubleshooting direction.

The AI Mentor is not meant to simply give you the answer. It is designed to help you think like an IT professional.

When asking for help, include:

```text
1. The ticket or lab you are working on.
2. The system you are using.
3. The command you ran.
4. The output or error you received.
5. What you think the issue might be.
```

---

## 5. Windows / Active Directory Access

Use your ARIA domain account when logging into Windows lab workstations.

### Login formats

```text
JLM\student02
```

or:

```text
student02@jlm.lab
```

### First login

Your instructor may require you to change your password at first login. Choose a strong password and store it securely.

Do not share your password with another student.

### Useful Windows commands

```cmd
whoami
hostname
ipconfig /all
gpresult /r
ping 192.168.60.1
ping 192.168.60.10
ping 1.1.1.1
nslookup jlm.lab
nslookup google.com
tracert 1.1.1.1
```

---

## 6. Zammad Help Desk Access

Zammad is the ticketing platform used for help desk workflow practice.

| Item | Value |
|---|---|
| Zammad URL | ______________________________ |
| Username | `student02` |
| Password | ______________________________ |

### Zammad expectations

When working a ticket:

1. Read the entire ticket first.
2. Identify what the user is reporting.
3. Collect evidence before guessing.
4. Add clear notes about what you checked.
5. Ask for help when you cannot prove the root cause.
6. Write a professional resolution summary.

---

## 7. Linux Container Access

Your dedicated Linux container is:

```text
student-linux-02
```

Your Linux username is:

```text
student02
```

### SSH command

```bash
ssh student02@100.91.190.9
```

### First commands after login

```bash
whoami
hostname
hostname -I
sudo -l
```

Expected results:

```text
whoami should show student02
hostname should show student-linux-02
sudo -l should show your sudo permissions
```

### Useful Linux commands

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

---

## 8. ARIA Training Domains

### Help Desk / Ticketing

You will practice reading tickets, asking the right questions, collecting evidence, writing notes, and documenting resolutions.

### Windows / Active Directory / Identity

You will practice domain login, user accounts, groups, Group Policy, account lockouts, password behavior, and endpoint troubleshooting.

### Linux / SysAdmin

You will practice SSH, Linux commands, files, permissions, services, logs, networking commands, and basic automation.

### Networking / DNS / VLAN / Troubleshooting

You will practice IP checks, gateway testing, DNS testing, reachability, traceroute, and escalation documentation.

### Security / SOC / Monitoring

You will practice reading alerts, collecting evidence, documenting incident notes, and understanding escalation paths as this domain expands.

### ARIA AI Mentor

You will use the Mentor to explain commands, understand errors, review your troubleshooting notes, and guide your next step.

---

## 9. First-Day Checklist

```text
[ ] I can log into my Windows/domain account.
[ ] I know my ARIA student ID: student02.
[ ] I can log into Zammad.
[ ] I can access the ARIA AI Mentor student page.
[ ] I can SSH into student-linux-02.
[ ] I ran whoami on Windows and Linux.
[ ] I ran hostname on Windows and Linux.
[ ] I know how to collect troubleshooting evidence.
[ ] I know where to ask the AI Mentor for guidance.
```

---

## 10. Help / Support

| Need | Contact / Location |
|---|---|
| Password reset | ______________________________ |
| Zammad access issue | ______________________________ |
| AI Mentor access issue | ______________________________ |
| Linux SSH issue | ______________________________ |
| Lab question | ______________________________ |

---

## 11. Important Rules

1. Do not share passwords.
2. Do not use another student's account.
3. Do not delete users, tickets, services, or files unless a lab tells you to.
4. Document what you did.
5. Collect evidence before guessing.
6. Treat each lab like real IT work.
