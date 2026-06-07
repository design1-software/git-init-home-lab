# ARIA Field-to-Cyber Lab Series

## Field Tech Lab 002: Perform a Basic Linux Endpoint Health Check

**Student:** Sha-Neal Prather
**Lab Account:** `sprather`
**Assigned System:** `student-linux-01`
**Training Level:** Beginner
**Prerequisite:** Field Tech Lab 001 complete

---

## Welcome to Linux System Administration

Welcome to the world of Linux system administration.

What you are about to do is a standard **health check** — a structured set of commands a technician or analyst runs to understand the current condition of a Linux server before doing anything else. Not to fix it. Not to change it. Just to know what it is, what it is doing, and whether it is healthy.

Every IT role you encounter — field tech, help desk, Linux admin, security analyst, cloud engineer — has some version of this routine. The commands differ slightly. The discipline is identical: **inspect before you act.**

You already know how to connect and confirm your identity. Now you learn how to read the system.

---

## 1. Purpose of This Exercise

In Lab 001 you proved you could connect to the system and verify its identity. Now you go one step further: prove you can assess whether the system is healthy.

A field technician or help desk analyst does not start changing things on a system they have never inspected. Before you fix anything, you need to know:

- How long has the system been running?
- Is storage nearly full?
- Is memory under pressure?
- Who else is logged in?
- What OS is this, and what kernel version?
- Are the right services running?
- What network interfaces and open ports are present?

These are not advanced questions. They are the first questions any competent technician asks. This lab teaches you to ask them systematically and document the answers.

---

## 2. Real-World Connection

When you picked up a Chromebook at your internship, you checked it before you wiped it. You looked at the screen, the battery state, whether it would power on. You assessed condition first.

This lab is the same discipline applied to a Linux server. Connect first. Inspect before you touch.

---

## 3. Connect to Your System

```bash
ssh sprather@100.125.65.78
```

Confirm your prompt shows:

```bash
sprather@student-linux-01:~$
```

---

## 4. The Health Check Commands

Run each command in order. For each one: read the output, understand what it tells you, and record the key values.

---

### Command 1 — How long has this system been running?

```bash
uptime
```

Example output:

```text
18:51:02 up 1 day,  5:41,  1 user,  load average: 0.17, 0.24, 0.26
```

**What each part means:**

- **18:51:02** — The current system clock time.
- **up 1 day, 5:41** — This server has been running continuously for 1 day, 5 hours, and 41 minutes without a reboot. A system that rebooted seconds or minutes ago might have done so unexpectedly — that is worth noting.
- **1 user** — How many users are currently logged in.
- **load average: 0.17, 0.24, 0.26** — These three numbers measure CPU demand over the last 1 minute, 5 minutes, and 15 minutes. Think of it as how busy the CPU has been. Numbers close to 0 mean the server is essentially idling and doing almost no work. High numbers (above the number of CPU cores) mean the system is under heavy load.

**Document this:**

```text
System uptime:
Load average (1/5/15 min):
```

---

### Command 2 — How much disk space is available?

```bash
df -h
```

The `-h` flag stands for **human-readable** — it shows sizes in gigabytes and megabytes instead of raw block numbers that would require a calculator to understand.

Look for the line that shows `/` — that is the root filesystem, the main storage where the entire operating system and all files live.

Example output:

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/mapper/...  16G  881M   14G   6% /
tmpfs           ...
udev            ...
```

**What each part means:**

- **Size** — The total capacity of the storage.
- **Used** — How much is currently occupied.
- **Avail** — How much free space remains.
- **Use%** — The percentage of storage used. Under 80% is healthy. Above 80% warrants attention. Above 95% is a crisis — log files stop writing, services crash, the system becomes unpredictable.
- **tmpfs and udev** entries are virtual, memory-based filesystems. They are not real disk storage. Focus on the `/` line.

**Document this:**

```text
Root filesystem size:
Used:
Available:
Use%:
```

---

### Command 3 — How much memory is available?

```bash
free -h
```

Example output:

```text
               total        used        free      shared  buff/cache   available
Mem:           2.0Gi        46Mi       1.5Gi         ...        ...       1.9Gi
Swap:          512Mi          0B       512Mi
```

**What each part means:**

The output has two rows: `Mem` (your RAM) and `Swap`.

For the `Mem` row:
- **total** — How much RAM the system has installed.
- **used** — How much RAM is currently in use.
- **available** — How much RAM is realistically available for new work right now.

> Important: `free` and `available` are different numbers. Use `available` — not `free` — to assess usable memory. Linux intentionally uses spare RAM as a disk cache, which makes `free` look low even on a healthy system. `available` accounts for this and gives the real picture.

For the `Swap` row:
- **Swap is emergency overflow memory** — disk space the OS borrows when RAM fills up. Think of it as a backup that is much slower than real RAM. Seeing 0 bytes used in swap is ideal. It means the system has plenty of real RAM and is not struggling.

**Document this:**

```text
Total RAM:
Available RAM:
Swap used:
```

---

### Command 4 — Who else is logged in?

```bash
who
```

Example output:

```text
sprather   pts/3    2026-06-07 18:06 (100.111.203.45)
```

**What each part means:**

- **sprather** — The logged-in username.
- **pts/3** — The terminal session number. `pts` stands for pseudo-terminal — a remote session over SSH.
- **2026-06-07 18:06** — The date and time this user logged in.
- **(100.111.203.45)** — The IP address they connected from. This is your Tailscale IP — the address your computer uses on the Tailscale network.

**Why this matters:** In a real environment, unexpected active sessions are a security concern. If you see a username or IP address you do not recognize, that is worth investigating. Security analysts always run `who` early when checking a suspicious system. It answers: *is someone else in here right now?*

**Document this:**

```text
Users currently logged in:
Their source addresses:
```

---

### Command 5 — What kernel and architecture is this?

```bash
uname -a
```

Example output:

```text
Linux student-linux-01 7.0.2-6-pve #1 SMP PREEMPT_DYNAMIC ... x86_64 GNU/Linux
```

**What each part means:**

- **Linux** — The operating system type.
- **student-linux-01** — The hostname of this machine.
- **7.0.2-6-pve** — The Linux kernel version. The `-pve` suffix tells you this kernel was built for **Proxmox Virtual Environment** — the hypervisor platform ARIA runs on. This is normal and expected for a container or VM hosted on Proxmox.
- **x86_64** — The processor architecture. This means 64-bit. Almost all modern servers and workstations are 64-bit.
- **GNU/Linux** — Confirms this is a standard Linux system.

**Document this:**

```text
Kernel version:
Architecture:
```

---

### Command 6 — What operating system is installed?

```bash
cat /etc/os-release
```

Example output:

```text
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
```

**What each part means:**

- **PRETTY_NAME** — The full, human-readable name of the OS. This is what you would say if someone asked "what OS is this running?"
- **VERSION_ID** — The version number. This system is running Debian 13.
- **trixie** — Every major Debian release has a codename. Version 13 is called "trixie." This is how Linux distributions distinguish releases — similar to how Windows uses names like "Server 2022" or "11."

Knowing the exact OS and version matters when looking up whether a security patch applies, whether a package is supported, or how to troubleshoot a specific issue.

**Document this:**

```text
Operating system:
Version:
```

---

### Command 7 — Are services running correctly?

```bash
systemctl status
```

Example output (top portion):

```text
           State: running
            Jobs: 0 queued
          Failed: 0 units
```

**What each part means:**

- **State: running** — The system is healthy and all expected services are active.
- **State: degraded** — At least one service or system unit has failed. This does not mean the system is completely broken, but something deserves attention.
- **Failed: 0 units** — No background services have crashed. This is what you want to see.

Below the state summary, you may see a tree of running processes (called a CGroup tree). Common entries you might recognize:
- `cron.service` — the scheduled task runner
- `ssh.service` or `sshd` — the service that accepted your SSH connection
- `networking.service` — manages network interfaces
- `postfix.service` — a mail relay service

**Document this:**

```text
System state (running / degraded):
Failed units:
```

---

### Command 8 — What network interfaces are active?

```bash
ip addr
```

You saw `ip -br addr` in Lab 001, which is the compact version. This is the full version with more detail per interface.

**What to look for:**

- **lo** — The loopback interface. Always present. Address is always 127.0.0.1. The system uses this to talk to itself internally.
- **eth0** — Your primary network interface connected to the lab network (VLAN 70). Should show 192.168.70.12.
- **tailscale0** — Your Tailscale tunnel interface. Should show your Tailscale IP (100.x.x.x).

Each interface entry shows the state (`UP` or `DOWN`) and the IP address(es) assigned.

**Document this:**

```text
eth0 IP address:
tailscale0 IP address:
```

---

### Command 9 — What ports and services are listening?

```bash
ss -tulnp
```

This shows every open network port on the system — every door that is currently open and waiting for a connection.

**What the flags mean:**

- `-t` — Show TCP connections
- `-u` — Show UDP connections
- `-l` — Show only listening ports (waiting for connections, not already connected)
- `-n` — Show port numbers, not service names
- `-p` — Show which process owns each port

**How to read the output:**

Look at the **Local Address:Port** column. The number after the colon is the port.

- **Port 22** — SSH. This should be listening. It is the port you used to connect.
- Any other port — note what it is and try to identify the service. Common ones: 25 (mail), 53 (DNS), 80 (web), 443 (HTTPS).

If you see a port you do not recognize and cannot explain, that is worth investigating. Unexpected open ports are a common indicator of unauthorized services or compromised systems.

**Document this:**

```text
Port 22: SSH — listening (expected)
Any other listening ports:
```

---

## 5. Evidence Collection

Your full output from all 9 commands should be copied into your notes.

Commands in order:

```bash
uptime
df -h
free -h
who
uname -a
cat /etc/os-release
systemctl status
ip addr
ss -tulnp
```

---

## 6. Student Response Template

```text
Field Tech Lab 002 — Linux Endpoint Health Check

Student Name:
Date:
System: student-linux-01

SYSTEM STATE
Uptime:
Load average (1/5/15 min):
System service state (from systemctl):
Failed units:

STORAGE
Root filesystem size:
Used:
Available:
Use%:
Assessment (healthy / warning / critical):

MEMORY
Total RAM:
Available RAM:
Swap used:
Assessment (healthy / warning / critical):

ACTIVE SESSIONS
Users logged in:
Source addresses:
Anything unexpected:

OS AND KERNEL
Operating system:
Version:
Kernel:
Architecture:

NETWORK
eth0 IP:
tailscale0 IP:

OPEN PORTS
Port 22 — SSH: listening (expected)
Other ports found:

HEALTH SUMMARY
In 3–5 sentences, assess whether this endpoint is healthy.
Cite specific numbers. Do not say "it looks fine" — explain why.
```

---

## 7. Help Rules

Same as Lab 001. Before asking for help:

1. What command did I run?
2. What did I expect?
3. What did I actually get?
4. What do I think it means?

---

## 8. Completion Criteria

This lab is complete when you have:

- Run all 9 commands
- Recorded the key output values for each
- Completed the response template
- Written a health summary that cites actual numbers

---

## 9. Final Learning Point

Every command in this lab is also used in security operations.

When an analyst is called to investigate a suspicious system, the first 60 seconds look like this:

```text
uptime         → Did it reboot recently or unexpectedly?
who            → Is someone else logged in right now?
ss -tulnp      → Are there ports open that should not be?
free           → Is memory being drained by something?
```

You are not just learning field tech. You are building the foundation for every IT role that comes after this.
