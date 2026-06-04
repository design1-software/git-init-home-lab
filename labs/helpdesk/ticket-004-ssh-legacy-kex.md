# Helpdesk Ticket 004 — Cannot SSH Into Switch (Legacy Key Exchange)

**Domain:** Cisco / SSH / Cryptography
**Difficulty:** Beginner
**Estimated time:** 20–30 minutes
**Based on:** Real lab incident (May 31, 2026) — see also `docs/runbooks/ssh-key-collision.md`

---

## Scenario

A student reports: *"I'm trying to SSH into the 3560CX switch but I keep getting an error. I can ping it."*

The error looks like:

```
Unable to negotiate with 192.168.199.2 port 22: no matching key exchange method found.
Their offer: diffie-hellman-group1-sha1,diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1
```

Or alternatively when connecting to C1111:

```
Unable to negotiate with 192.168.199.1 port 22: no matching key exchange method found.
Their offer: diffie-hellman-group14-sha1
```

---

## Ticket Details

**Reported by:** Lab user / network admin student
**Affected system:** Cisco C1111 or Catalyst 3560CX
**Priority:** Low–Medium
**Category:** Network — SSH / Access

---

## AI Mentor Opening Questions

```
1. Which device are you trying to reach? (C1111 or 3560CX)
2. What is the exact error message?
3. What IP are you connecting to?
4. What SSH client are you using? (macOS Terminal, PuTTY, other)
5. Has this worked before?
6. Are you getting a key exchange error or a host key verification error?
   (These are two different problems)
```

---

## Evidence Required

```
- Exact error message (copy-paste)
- Which device (C1111 at 192.168.199.1 or 3560CX at 192.168.199.2)
- What command was used to connect
- Output of: ssh -v <ip> (verbose mode — shows negotiation failure)
```

---

## Diagnostic Path

```
Key exchange negotiation failure (no matching KEX method):
  → Modern OpenSSH clients have removed support for legacy algorithms
  → The Cisco device only offers older algorithms
  → Fix: pass the algorithm flags to the SSH client

  For C1111 (192.168.199.1):
    ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 \
        -oHostKeyAlgorithms=+ssh-rsa \
        admin@192.168.199.1

  For 3560CX (192.168.199.2):
    ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1 \
        -oHostKeyAlgorithms=+ssh-rsa \
        admin@192.168.199.2

  Or use the alias (if configured):
    ssh jlm-lab-sw1

Host key verification failed (different error):
  → The device at that IP has changed (HSRP failover, IP moved to different device)
  → Fix: remove stale key with ssh-keygen -R <ip>
  → See: docs/runbooks/ssh-key-collision.md
```

---

## Background: Why This Happens

Modern OpenSSH (8.8+, default on macOS and recent Linux) has disabled `diffie-hellman-group14-sha1` and `ssh-rsa` by default due to cryptographic weaknesses. Cisco IOS XE devices that have not been upgraded to support modern algorithms (ecdh, ed25519) still offer only the older set.

This is not a connectivity failure. The switch is reachable — SSH is up. The two ends cannot agree on an encryption method.

The `-o` flags are an override that says: "allow these legacy algorithms for this connection." This is acceptable for a controlled lab environment.

---

## Real Incident Summary (May 31, 2026)

During Phase B cutover, the SSH connection to the 3560CX at 192.168.199.2 failed with the key exchange error. The C1111 at 192.168.199.1 had a different requirement (only `group14-sha1`, not `group-exchange-sha1`).

Additionally, after HSRP VIPs became active on the 3560CX, 192.168.10.1 started being answered by the 3560CX rather than the C1111 — causing a host key collision error for anyone who had previously SSH'd to 192.168.10.1 as the C1111.

Both issues were documented and the C1111 is now accessed at 192.168.199.1 (TRANSIT SVI) to avoid the IP conflict.

---

## Commands

```bash
# Connect to C1111 (requires group14-sha1 only)
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 \
    -oHostKeyAlgorithms=+ssh-rsa \
    admin@192.168.199.1

# Connect to 3560CX (requires both group14 and group-exchange)
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1 \
    -oHostKeyAlgorithms=+ssh-rsa \
    admin@192.168.199.2

# Or use the SSH alias (if ~/.ssh/config is configured)
ssh jlm-lab-sw1

# Fix host key collision
ssh-keygen -R 192.168.10.1
```

---

## Documentation Prompt

```
Write a short incident summary:
- What the student was trying to do
- What the error indicated (negotiation failure vs. host key failure)
- How the student identified which device had which algorithm requirement
- What command was used to connect successfully
- Why the legacy algorithm flags are needed in this lab
```

---

## Learning Objectives

- Distinguish between key exchange negotiation failure and host key verification failure
- Understand why modern SSH clients reject legacy algorithms by default
- Know how to pass explicit algorithm flags with `-oKexAlgorithms` and `-oHostKeyAlgorithms`
- Understand the HSRP IP ownership shift and why C1111 is reached at a different IP post-cutover
- Practice reading SSH verbose output (`-v`) to diagnose negotiation failures
