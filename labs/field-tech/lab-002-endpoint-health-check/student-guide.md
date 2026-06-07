# ARIA Field-to-Cyber Lab Series

## Field Tech Lab 002: Perform a Basic Linux Endpoint Health Check

**Student:** Sha-Neal Prather
**Lab Account:** `sprather`
**Assigned System:** `student-linux-01`
**Training Level:** Beginner
**Prerequisite:** Field Tech Lab 001 complete

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

You will see output similar to:

```text
 10:34:21 up 1 day,  3:12,  1 user,  load average: 0.00, 0.01, 0.00
```

**Read it:**
- The time after `up` tells you how long the system has been running since its last boot.
- The three numbers at the end are the **load averages** — the average workload over the last 1 minute, 5 minutes, and 15 minutes. On a lightly used system, these should be close to 0.

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

The `-h` flag means "human readable" — it shows sizes in GB instead of raw block counts.

Look for the line that shows `/` (the root filesystem). That is the main storage for the operating system.

**Read it:**
- `Size` — total disk size
- `Used` — how much is occupied
- `Avail` — how much is free
- `Use%` — percentage used

A system with `Use%` above 80% is approaching a problem. Above 95% is a crisis — log files stop writing, services can crash.

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

**Read it:**

The output has two rows: `Mem` (RAM) and `Swap`.

Focus on the `Mem` row:
- `total` — how much RAM the system has
- `used` — how much is currently in use
- `available` — how much is realistically usable right now

> Note: `free` and `available` are different. Use `available`, not `free`, to assess how much memory the system actually has to work with.

`Swap` is disk space the OS uses when RAM runs out. If swap is heavily used, the system is under memory pressure and will run slowly.

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

This shows every user currently logged into the system and where they connected from.

You will likely see your own session. Note the IP address shown — it should match your Tailscale IP.

**Why this matters:** In a real environment, unexpected active sessions are a security concern. An analyst checking a suspicious system always runs `who` early in their investigation.

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

This shows the Linux kernel version, the hostname, the build date, and the architecture.

Look for:
- The kernel version number (e.g., `6.1.0-21-amd64`)
- The architecture at the end (`x86_64` means 64-bit)

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

This file contains the official OS identification. Look for:
- `PRETTY_NAME` — the full OS name and version
- `VERSION_ID` — the version number

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

This gives a summary of the overall system state. Look at the first line:

- `State: running` — the system is healthy
- `State: degraded` — at least one service or unit has failed

If you see `degraded`, it does not mean the system is broken. It means something is worth investigating. For this lab, just note the state.

**Document this:**

```text
System state:
```

---

### Command 8 — What network interfaces are active?

```bash
ip addr
```

You saw a version of this in Lab 001 (`ip -br addr`). This is the full version with more detail.

Look for:
- `eth0` — your local lab network interface (should show 192.168.70.12)
- `tailscale0` — your Tailscale tunnel interface
- `lo` — the loopback interface (127.0.0.1, always present)

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

This shows every open network port on the system. The flags mean:
- `-t` TCP connections
- `-u` UDP connections
- `-l` Listening ports only
- `-n` Show port numbers, not service names
- `-p` Show which process is using each port

Look at the output and find port 22. That is SSH — the service you used to connect. It should be listed as listening.

Note any other ports that are listening and try to identify what service they belong to.

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
uptime         → Did it reboot recently?
who            → Who is logged in right now?
ss -tulnp      → Are there unexpected open ports?
free           → Is memory being drained by something?
```

You are not just learning field tech. You are building the foundation for every IT role that comes after this.
