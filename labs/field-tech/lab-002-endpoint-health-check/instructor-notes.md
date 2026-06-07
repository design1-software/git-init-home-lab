# Field Tech Lab 002 — Instructor Notes

**Lab Series:** ARIA Field-to-Cyber Lab Series
**Track:** Field Tech Foundation Labs

## Lab
Field Tech Lab 002: Perform a Basic Linux Endpoint Health Check

## Student
Sha-Neal Prather

## Lab Host
student-linux-01

## Student Username
sprather

## Remote Access

```bash
ssh sprather@100.125.65.78
```

---

## Real-World Framing

In the field, you do not start fixing until you know the current state. A technician who jumps straight to changes without assessing the system first makes unpredictable changes. This lab teaches the habit of running a health check before anything else.

Connect this to her internship: when she picked up a Chromebook, she checked its screen, battery, and update status before wiping it. Same discipline here — inspect before you act.

---

## Commands and Expected Outputs

### uptime

```bash
uptime
```

Expected format:
```text
 10:34:21 up 1 day,  3:12,  1 user,  load average: 0.00, 0.01, 0.00
```

What to look for:
- How long the system has been running
- Load averages — 1-minute, 5-minute, 15-minute. Near 0 is healthy on a lightly loaded container.
- A very recent uptime (seconds or minutes) may indicate a recent reboot or crash

### df -h

```bash
df -h
```

Expected format:
```text
Filesystem      Size  Used Avail Use% Mounted on
overlay         100G   1.2G   99G   2% /
```

What to look for:
- `/` (root filesystem) — is it near full? Above 80% Use% warrants attention
- `/boot` if present
- Student should identify which filesystem is the main storage

### free -h

```bash
free -h
```

Expected format:
```text
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       210Mi       3.4Gi       660Ki       230Mi       3.5Gi
Swap:          511Mi          0B       511Mi
```

What to look for:
- Total and available memory
- Swap usage — if swap is heavily used, the system may be under memory pressure
- Student should be able to state how much RAM is available

### who

```bash
who
```

Expected output (will show sprather logged in):
```text
sprather pts/0        2026-06-07 10:30 (100.125.65.78)
```

What to look for:
- Who is currently logged in
- From what address they connected
- Multiple concurrent sessions may be normal or may be worth investigating
- Security relevance: unexpected sessions would be a red flag

### uname -a

```bash
uname -a
```

Expected format:
```text
Linux student-linux-01 6.1.0-21-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.90-1 (2024-05-03) x86_64 GNU/Linux
```

What to look for:
- Kernel version
- Architecture (x86_64 = 64-bit)
- Build date — very old kernels on internet-facing systems are a security concern

### cat /etc/os-release

```bash
cat /etc/os-release
```

Expected output:
```text
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
```

What to look for:
- OS name and version
- Student should be able to state what OS the endpoint is running

### systemctl status

```bash
systemctl status
```

What to look for:
- Overall system state: `running` is healthy; `degraded` means at least one unit has failed
- Student should identify whether the system state is clean

### ip addr

```bash
ip addr
```

What to look for:
- All network interfaces and their addresses
- eth0 (lab network, VLAN 70) — should show 192.168.70.12/24
- tailscale0 — should show 100.125.65.78/32
- lo (loopback) — should show 127.0.0.1/8

This is the verbose version of what was seen in Lab 001. Student should recognize the interfaces.

### ss -tulnp

```bash
ss -tulnp
```

Expected output includes at minimum:
```text
tcp   LISTEN  0  128  0.0.0.0:22   0.0.0.0:*   users:(("sshd",pid=...))
```

What to look for:
- Port 22 (SSH) should be listening — expected
- Any other listening ports should be noted and explained
- Student should be able to identify which service is behind each port

---

## Completion Criteria

Student must submit:

1. System uptime and load averages
2. Root filesystem disk usage (size, used, available, percent)
3. Available RAM
4. Who is currently logged in (besides themselves)
5. Kernel version and architecture
6. OS name and version
7. System state from systemctl status (running or degraded)
8. All network interfaces and their IP addresses
9. All listening ports from ss -tulnp with service names
10. A 3–5 sentence health summary: is this endpoint healthy?

---

## Coaching Notes

Do not give the answer first. Ask:

- What does the load average number tell you?
- If the disk was 95% full, what would you do?
- What is the difference between `free` memory and `available` memory?
- Why would you want to know who else is logged in?
- What service is listening on port 22, and why is it there?
- If you saw a port you did not recognize, what would be your next step?

---

## Common Mistakes

- Reading `free` output and confusing `free` with `available` (available is the usable number)
- Not explaining what the load averages represent
- Listing `ss` output without identifying which service is behind each port
- Saying "the system looks healthy" without citing specific evidence
- Skipping `who` because "I know I'm the only one logged in"

---

## Instructor Decision

This lab is passed when the student can:

1. Run all 9 commands without prompting
2. Explain what each command reveals and why it matters
3. Produce a health summary that cites specific numbers from the output
4. Identify at minimum the SSH listening port and name the service behind it

---

## Connection to Security

This lab introduces the commands that security analysts and sysadmins use during incident first response:

- `uptime` — did the system reboot unexpectedly? (post-incident indicator)
- `who` — are there unexpected active sessions?
- `ss -tulnp` — are there unexpected open ports or listening services?
- `free` — is memory under unusual pressure?

Plant this: "Everything you ran today is also what an analyst runs in the first 60 seconds of investigating a suspicious system."

---

## Next Lab

Field Tech Lab 003: Create a Professional Damaged Device Ticket
