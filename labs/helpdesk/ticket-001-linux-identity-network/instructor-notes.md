# Instructor Notes — Ticket 001

## Ticket
Verify Linux System Identity and Network Connectivity

## Student
Sha-Neal Prather

## Lab Host
student-linux-01

## Student Username
sprather

## Remote Access
Student connects over Tailscale.

Current SSH target:

```bash
ssh sprather@100.125.65.78
```

Do not commit passwords to the repo.

## Skills Practiced

* SSH login
* User identity verification
* Hostname verification
* IP address discovery
* Default gateway discovery
* DNS configuration review
* Gateway connectivity testing
* DNS server reachability testing
* Internet connectivity testing
* Evidence-based documentation

## Expected Key Outputs

Username:

```bash
whoami
```

Expected:

```text
sprather
```

Hostname:

```bash
hostname
```

Expected:

```text
student-linux-01
```

Network:

```bash
ip -br addr
```

Expected:

```text
eth0 ... 192.168.70.x/24
tailscale0 ... 100.x.x.x/32
```

Route:

```bash
ip route
```

Expected:

```text
default via 192.168.70.1 dev eth0
```

DNS:

```bash
cat /etc/resolv.conf
```

Expected DNS server:

```text
192.168.10.16
```

## Completion Criteria

Student must submit:

1. Logged-in username.
2. Hostname.
3. IP address.
4. Default gateway.
5. DNS server.
6. Gateway ping result.
7. DNS server ping result.
8. Internet-by-IP result.
9. Public DNS name result.
10. 3–5 sentence summary explaining what was proven.

## Coaching Notes

Do not give the answer first. Ask:

* What command did you run?
* What did you expect?
* What did you get?
* What does that prove?
* What would you test next?

## Common Mistakes

* Confusing hostname with username.
* Thinking pinging `8.8.8.8` proves DNS.
* Forgetting to document packet loss.
* Running commands with sudo when not needed.
* Saying "it works" without evidence.

## Instructor Decision

This lab is passed when the student can explain the difference between:

* local identity
* system identity
* IP connectivity
* DNS resolution
* internet reachability
