# Helpdesk Ticket 006 — Proxmox Repository Hygiene (Layered apt Failure)

**Domain:** Linux / Package Management / Repository Configuration
**Difficulty:** Intermediate
**Estimated time:** 35–50 minutes
**Based on:** Real ARIA incident (Jun 4, 2026)

---

## Scenario

A student reports: *"I fixed the internet on the Proxmox server — it can reach the gateway and ping 8.8.8.8 now. But apt update is still failing. I thought fixing the network would fix apt."*

This is the follow-on ticket after ticket-003. Internet egress is now working. The student assumes that was the only problem. It was not.

---

## Why This Ticket Is Valuable

This ticket teaches a critical enterprise principle: **fixing one layer does not fix all layers.**

A student who conflates "network works" with "apt works" has not internalized the OSI model as a troubleshooting framework. Each layer can fail independently:

```
Layer 3 — IP reachability        (can you ping the server?)
Layer 4 — TCP reachability       (can you reach port 443?)
Layer 7 — Repository auth        (does the server accept your credentials?)
Layer 7 — Repository config      (does the package index match your OS?)
Policy   — Upgrade gates         (should you upgrade right now?)
```

Fixing Layer 3 (routing) does not fix Layer 7 (repository auth or config mismatch). Students who stop at "network is up" will be confused when apt still fails.

---

## Ticket Details

**Reported by:** Lab sysadmin / student
**Affected system:** ARIA Proxmox host — package management
**Priority:** Low
**Category:** Linux — Package Management / Repository Config

---

## AI Mentor Opening Questions

```
1. What is the exact error message from apt update now?
2. Can you ping 8.8.8.8? (confirm layer 3 is working)
3. Can you reach port 443 on download.proxmox.com?
   (curl -I https://download.proxmox.com)
4. What repositories are configured?
   (ls /etc/apt/sources.list.d/ && cat each file)
5. Is there an enterprise repository entry? What does it say?
6. What Debian version is this host running?
   (cat /etc/os-release | grep VERSION_CODENAME)
```

---

## Evidence Required

```
- Full output of: apt update (with current errors)
- Output of: ping -c 3 8.8.8.8
- Output of: curl -I https://download.proxmox.com (HTTP status code)
- Output of: cat /etc/apt/sources.list.d/pve-no-subscription.list
- Output of: cat /etc/apt/sources.list.d/pve-enterprise.list (if present)
- Output of: cat /etc/os-release | grep -E "VERSION_CODENAME|VERSION_ID"
```

---

## Diagnostic Path: Each Layer

### Layer 3 — IP Reachability
```
ping -c 3 8.8.8.8
→ If this fails: not a repo problem, routing is still broken — see ticket-005
→ If this succeeds: routing is not the issue, continue to next layer
```

### Layer 4 — TCP Reachability to Repository
```
curl -I https://download.proxmox.com
→ HTTP 200 or redirect: server is reachable over TCP
→ Connection refused or timeout: firewall or NAT issue blocking outbound HTTPS
→ Certificate error: clock sync problem (check: date && timedatectl)
```

### Layer 7 — Repository Authentication (Enterprise Repo)
```
cat /etc/apt/sources.list.d/pve-enterprise.list

If present and active:
  deb https://enterprise.proxmox.com/debian/pve trixie pve-enterprise
  → This requires a paid Proxmox subscription key
  → Without a key: apt returns "401 Unauthorized" for every enterprise update
  → Fix: comment out or delete pve-enterprise.list
  → Homelab hosts use pve-no-subscription only

After disabling enterprise repo, re-run apt update and check for next error
```

### Layer 7 — Repository Config (Distribution Codename Mismatch)
```
cat /etc/apt/sources.list.d/pve-no-subscription.list

Should contain:
  deb http://download.proxmox.com/debian/pve trixie pve-no-subscription

If it contains "bookworm" instead of "trixie":
  → ARIA runs Proxmox VE 9.x on Debian 13 (trixie)
  → bookworm = Debian 12, used by Proxmox VE 8.x
  → Mismatch causes: "404 Not Found" or "Release file is not valid yet"
  → Fix: replace "bookworm" with "trixie" in the file

Verify OS codename:
  cat /etc/os-release | grep VERSION_CODENAME
  → Should output: trixie
```

### Policy Layer — Safe Upgrade Gates
```
apt update succeeded?
  → Do not immediately run apt upgrade

Ask: is there a hard reset recovery path?
  → Is the ATX control board installed?
  → Can Comet perform a hard power cycle if the kernel update fails?
  → If no: defer apt upgrade until recovery path exists

Reason: a kernel upgrade that renders the host unresponsive cannot be
recovered by Wake-on-LAN alone. WoL only works if the NIC stack is functional.
A kernel panic or failed upgrade requires a hard reset.

Document the deferral decision in the ticket.
```

---

## Proxmox Version Reference

| Proxmox VE | Debian | Codename | Repository suite |
|---|---|---|---|
| 9.x | 13 | trixie | trixie |
| 8.x | 12 | bookworm | bookworm |
| 7.x | 11 | bullseye | bullseye |

When in doubt: `cat /etc/os-release` reveals the installed Debian version.

---

## Commands Used in Resolution

```bash
# Confirm Layer 3
ping -c 3 8.8.8.8

# Force apt to IPv4 (if not already done)
echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

# Disable enterprise repo (if present)
# Option A: comment it out
sed -i 's/^deb /#deb /' /etc/apt/sources.list.d/pve-enterprise.list

# Option B: delete it
rm /etc/apt/sources.list.d/pve-enterprise.list

# Verify no-subscription repo has correct codename
cat /etc/apt/sources.list.d/pve-no-subscription.list
# Should show: deb http://download.proxmox.com/debian/pve trixie pve-no-subscription

# Test
apt update

# Do NOT run apt upgrade yet — verify recovery path first
```

---

## Real Incident Summary (Jun 4, 2026)

This ticket is based on the actual ARIA resolution sequence:

| Order | Issue found | Root cause | Fix |
|---|---|---|---|
| 1 | internet egress broken | Asymmetric routing (VLAN 1 return path) | /32 static host routes on C1111 (ticket-005) |
| 2 | apt fails: "Network is unreachable" | IPv6 preferred, no IPv6 internet routing | `/etc/apt/apt.conf.d/99force-ipv4` |
| 3 | apt fails: "401 Unauthorized" | Enterprise repo active, no subscription key | Enterprise repo removed |
| 4 | apt still fails: suite mismatch | No-subscription repo pointed to wrong suite | Corrected to trixie |
| 5 | apt update succeeds | — | — |
| 6 | apt upgrade deferred | ATX board not yet installed — no hard reset path | Documented in repo, deferred to after ATX board |

Each issue was a separate, independent failure. Fixing issue 1 did not expose issue 2 until the next apt run. This layered discovery is normal and expected.

---

## Documentation Prompt

```
Write a structured incident summary:
- What the original symptom was after internet egress was fixed
- How you identified which layer of the apt problem was failing at each step
- What the difference is between a repository authentication failure and a
  distribution codename mismatch
- Why you deferred the package upgrade
- What condition must be met before the upgrade proceeds
```

---

## Learning Objectives

- Understand that network connectivity and package management are independent layers
- Apply a layered diagnostic approach (L3 → L4 → L7 auth → L7 config → policy)
- Know the Proxmox version-to-Debian-codename mapping
- Distinguish `pve-enterprise` from `pve-no-subscription` and know when each applies
- Understand deliberate deferral as a professional decision, not procrastination
- Practice documenting a multi-root-cause incident as a single coherent sequence
