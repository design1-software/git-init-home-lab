# ARIA Field-to-Cyber Lab Series

## Field Tech Lab 001: Verify Endpoint Identity and Network Connectivity

**Student:** Sha-Neal Prather
**Lab Account:** `sprather`
**Assigned System:** `student-linux-01`
**Training Level:** Beginner / First Linux Lab
**Instructor:** Julius Moore
**Lab Platform:** ARIA Proxmox Training Environment

---

## 1. Purpose of This Exercise

Welcome to your first JLM Lab Linux troubleshooting exercise.

In this lab, you will learn how to log into a remote Linux system, confirm who you are logged in as, identify the system you are working on, check the system's network configuration, and verify basic connectivity.

This is a foundational help desk and systems administration skill. Before a technician can fix a problem, they must first prove where they are, what account they are using, what network the system is on, and whether the system can communicate.

The goal is not to memorize commands. The goal is to learn how to collect evidence.

---

## 2. What You Are Practicing

By the end of this exercise, you should be able to:

1. Log into a remote Linux system using SSH.
2. Confirm your current username.
3. Confirm the hostname of the system.
4. Identify the system's IP address.
5. Identify the default gateway.
6. Identify the DNS server.
7. Test local network connectivity.
8. Test internet connectivity.
9. Test public DNS name resolution.
10. Document your findings clearly.

---

## 3. Tools You Need Installed on Your Computer

Before starting this lab, your computer must have:

### Required

* Tailscale installed and connected to the JLM Lab network.
* A terminal application:

  * Windows: Windows Terminal or PowerShell
  * macOS: Terminal
  * Linux: Terminal
* SSH client:

  * Windows 10/11 usually has SSH built in.
  * macOS and Linux include SSH by default.

### Optional

* Notepad, OneNote, Word, or Google Docs for taking notes.
* VS Code later, but it is not required for this first exercise.

---

## 4. Login Information

You will be given the correct SSH address by the instructor.

Your Linux username is:

```bash
sprather
```

Your assigned Linux system is:

```bash
student-linux-01
```

Your instructor will provide the temporary password securely.

Do not share your password with anyone else.

---

## 5. Important Safety Rule

You are logging in as a normal trainee user, not as root.

This is intentional.

In Linux, `root` is the full administrator account. Root can change or destroy anything on the system. A trainee should not work as root by default.

Your account, `sprather`, is a normal user account. If an exercise requires administrative permission, you may be asked to use:

```bash
sudo
```

`sudo` means "run this one command with administrator privileges."

Only use `sudo` when the lab instructions tell you to or when your instructor approves it.

---

## 6. Step 1 — Connect to the Linux System

Open your terminal and connect to the assigned system with SSH.

Your command will look like this:

```bash
ssh sprather@<lab-address>
```

The instructor will provide the correct lab address.

The first time you connect, you may see a message like:

```text
The authenticity of host can't be established.
Are you sure you want to continue connecting?
```

Type:

```bash
yes
```

Then press Enter.

When prompted, enter your password.

If login is successful, your prompt should look similar to:

```bash
sprather@student-linux-01:~$
```

That means you are logged in as `sprather` on the system named `student-linux-01`.

---

## 7. Step 2 — Confirm Who You Are Logged In As

Run:

```bash
whoami
```

Expected result:

```bash
sprather
```

### What this tells you

This confirms the account you are currently using.

### Document this

Write down:

```text
Logged-in user:
```

---

## 8. Step 3 — Confirm the Hostname

Run:

```bash
hostname
```

Expected result:

```bash
student-linux-01
```

### What this tells you

This confirms which Linux machine you are working on.

### Document this

Write down:

```text
Hostname:
```

---

## 9. Step 4 — Identify the IP Address

Run:

```bash
ip -br addr
```

Look for the line that starts with:

```bash
eth0
```

You should see an IP address similar to:

```text
192.168.70.x/24
```

The `/24` tells you the size of the network.

### What this tells you

This shows the IP address assigned to the Linux system.

### Document this

Write down:

```text
IP address:
Network interface:
```

---

## 10. Step 5 — Identify the Default Gateway

Run:

```bash
ip route
```

Look for a line that starts with:

```bash
default via
```

It may look like:

```text
default via 192.168.70.1 dev eth0
```

### What this tells you

The default gateway is where the system sends traffic when it needs to reach another network or the internet.

### Document this

Write down:

```text
Default gateway:
```

---

## 11. Step 6 — Check DNS Configuration

Run:

```bash
cat /etc/resolv.conf
```

Look for a line that starts with:

```text
nameserver
```

You may see something like:

```text
nameserver 192.168.10.16
```

### What this tells you

This shows which DNS server the system uses to resolve names like `debian.org` into IP addresses.

### Document this

Write down:

```text
DNS server:
```

---

## 12. Step 7 — Test Gateway Connectivity

Run:

```bash
ping -c 4 192.168.70.1
```

### What success looks like

You should see replies like:

```text
64 bytes from 192.168.70.1
```

At the end, you want to see:

```text
0% packet loss
```

### What this tells you

This proves the Linux system can reach its local network gateway.

### Document this

Write down:

```text
Gateway test result:
Packet loss:
```

---

## 13. Step 8 — Test DNS Server Connectivity

Run:

```bash
ping -c 4 192.168.10.16
```

### What success looks like

You should see replies and `0% packet loss`.

### What this tells you

This proves the Linux system can reach the DNS server.

### Document this

Write down:

```text
DNS server reachability:
Packet loss:
```

---

## 14. Step 9 — Test Internet Connectivity by IP

Run:

```bash
ping -c 4 8.8.8.8
```

### What success looks like

You should see replies and `0% packet loss`.

### What this tells you

This proves the system can reach the internet by IP address.

Important: this does not prove DNS works. It only proves internet reachability by IP.

### Document this

Write down:

```text
Internet by IP test:
Packet loss:
```

---

## 15. Step 10 — Test DNS Name Resolution and Internet Access

Run:

```bash
ping -c 4 deb.debian.org
```

### What success looks like

The system should first translate `deb.debian.org` into an IP address, then receive ping replies.

### What this tells you

This proves two things:

1. DNS name resolution is working.
2. The system can reach an internet host by name.

### Document this

Write down:

```text
Public DNS name test:
Resolved name:
Packet loss:
```

---

## 16. Evidence Collection

For this lab, your evidence should include the output of these commands:

```bash
whoami
hostname
ip -br addr
ip route
cat /etc/resolv.conf
ping -c 4 192.168.70.1
ping -c 4 192.168.10.16
ping -c 4 8.8.8.8
ping -c 4 deb.debian.org
```

You can copy and paste the command output into your notes.

If you cannot copy and paste, take screenshots.

---

## 17. Student Response Template

Use this format when submitting your completed lab:

```text
Field Tech Lab 001 — Verify Endpoint Identity and Network Connectivity

Student Name:
Date:

1. Logged-in user:
2. Hostname:
3. IP address:
4. Network interface:
5. Default gateway:
6. DNS server:

Connectivity Tests:

1. Gateway ping result:
2. DNS server ping result:
3. Internet by IP result:
4. Public DNS name result:

Questions:

1. What command showed your username?
2. What command showed the hostname?
3. What command showed your IP address?
4. What command showed the default gateway?
5. What is the difference between pinging 8.8.8.8 and pinging deb.debian.org?
6. Did anything fail? If yes, what failed?

Summary:

In 3–5 sentences, explain what you proved in this lab.
```

---

## 18. Help Rules

Before asking for help, try to answer these questions:

1. What command did I run?
2. What result did I expect?
3. What result did I actually get?
4. What changed?
5. What evidence do I have?

When asking for help, do not just say:

```text
It does not work.
```

Instead, say:

```text
I ran this command:
[paste command]

I expected this:
[describe expected result]

I got this:
[paste output]

I think the issue might be:
[write your best guess]
```

This is how real technical escalation works.

---

## 19. Completion Criteria

This lab is complete when:

* You successfully log into `student-linux-01`.
* You confirm your username.
* You confirm the hostname.
* You identify the system IP address.
* You identify the default gateway.
* You identify the DNS server.
* You test gateway connectivity.
* You test DNS server connectivity.
* You test internet connectivity.
* You test DNS name resolution.
* You submit your notes using the response template.

---

## 20. Final Learning Point

A good technician does not guess first.

A good technician verifies.

This lab teaches the basic verification pattern:

```text
Who am I?
Where am I?
What network am I on?
Can I reach the gateway?
Can I reach DNS?
Can I reach the internet?
Can I prove it?
```

That pattern will show up again in every networking, Linux, help desk, cybersecurity, and cloud environment you work in.
