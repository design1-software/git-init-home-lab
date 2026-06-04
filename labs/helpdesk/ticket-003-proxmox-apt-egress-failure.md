# Helpdesk Ticket 003 — Proxmox Host Cannot Run apt update

**Domain:** Linux / Networking / Package Management
**Difficulty:** Beginner–Intermediate
**Estimated time:** 30–45 minutes
**Based on:** Real ARIA incident (Jun 4, 2026)

---

## Scenario

A student reports: *"I'm trying to update packages on the Proxmox server but apt update keeps failing with network errors. I can ping the gateway."*

The Proxmox host is ARIA, temporarily on VLAN 1 (192.168.100.10). IPv4 connectivity is working. Package updates are failing.

---

## Ticket Details

**Reported by:** Lab user / sysadmin
**Affected system:** ARIA Proxmox host
**Priority:** Medium
**Category:** Linux — Package Management / Networking

---

## AI Mentor Opening Questions

```
1. What is the exact error message from apt update?
2. Can you ping 8.8.8.8 from the host?
3. Can you ping download.proxmox.com from the host?
4. What does your /etc/apt/sources.list.d/ contain?
   (ls /etc/apt/sources.list.d/)
5. Are there any enterprise repository entries configured?
```

---

## Evidence Required

```
- Full output of: apt update (with errors)
- Output of: ping -c 3 8.8.8.8
- Output of: ping -c 3 download.proxmox.com
- Output of: ls /etc/apt/sources.list.d/
- Output of: cat /etc/apt/sources.list.d/pve-enterprise.list (if it exists)
- Output of: cat /etc/apt/sources.list.d/pve-no-subscription.list (if it exists)
```

---

## Diagnostic Path

```
Error: "Network is unreachable" on apt update, ping 8.8.8.8 works
  → apt is trying to connect via IPv6 first
  → IPv6 is enabled or preferred, but host has no working IPv6 internet routing
  → Fix: force apt to use IPv4 only
  → echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

Error: "401 Unauthorized" on enterprise.proxmox.com
  → Enterprise repository is configured but no valid subscription key exists
  → Homelab hosts use pve-no-subscription repository, not enterprise
  → Fix: disable or remove the enterprise repo entry
  → Comment out or delete: /etc/apt/sources.list.d/pve-enterprise.list

Error: "404 Not Found" or suite mismatch
  → Repository points to wrong Debian suite (bookworm vs trixie)
  → ARIA runs Proxmox VE 9.x on Debian 13 (trixie) — not bookworm (Debian 12)
  → Fix: correct the suite in the no-subscription repo file to trixie
  → deb http://download.proxmox.com/debian/pve trixie pve-no-subscription
```

---

## Real Incident Summary (Jun 4, 2026)

This ticket is based on a real ARIA incident. All three issues were found and resolved:

| Issue | Root Cause | Resolution |
|---|---|---|
| "Network is unreachable" on apt | IPv6 preferred, no IPv6 internet routing on ARIA | `/etc/apt/apt.conf.d/99force-ipv4` created |
| "401 Unauthorized" | Enterprise repo (`pve-enterprise.list`) was active without a subscription key | Enterprise repo removed |
| Repo suite mismatch | Some entries pointed to `bookworm` instead of `trixie` | Corrected to `trixie` throughout |

After fixes, `apt update` completed successfully. Package upgrades were **deferred** until the Comet GL-ATXPC ATX control board is installed — a kernel update that renders ARIA unreachable cannot be recovered by WoL alone.

---

## Commands Used in Resolution

```bash
# Force apt to use IPv4
echo 'Acquire::ForceIPv4 "true";' > /etc/apt/apt.conf.d/99force-ipv4

# Verify sources
cat /etc/apt/sources.list.d/pve-no-subscription.list
# Should contain: deb http://download.proxmox.com/debian/pve trixie pve-no-subscription

# Check for enterprise repo
cat /etc/apt/sources.list.d/pve-enterprise.list
# If present and causing 401: comment out or remove

# Verify OS version
cat /etc/os-release
# Should show: VERSION_CODENAME=trixie (Debian 13 = Proxmox VE 9.x)

# Test
apt update
```

---

## Expected Root Causes

| Root Cause | How to Identify | How to Fix |
|---|---|---|
| IPv6 preferred, no IPv6 routing | "Network is unreachable" errors in apt output | Create `/etc/apt/apt.conf.d/99force-ipv4` |
| Enterprise repo 401 | "401 Unauthorized" for enterprise.proxmox.com | Remove/comment `pve-enterprise.list` |
| Wrong Debian suite | 404 or suite mismatch error | Correct suite to `trixie` in sources.list |
| No internet egress | Ping to 8.8.8.8 fails too | Routing/gateway issue — escalate |

---

## Documentation Prompt

```
Write a short incident summary:
- What the reported symptom was
- How you identified whether it was a connectivity issue or a configuration issue
- Which source files contained errors
- What changes you made to each file
- How you confirmed apt update worked after fixes
- Why package upgrades were deferred (if applicable)
```

---

## Learning Objectives

- Distinguish between network-level failure and apt-configuration failure
- Understand IPv6/IPv4 preference behavior in Debian apt
- Understand the difference between `pve-enterprise` and `pve-no-subscription` repositories
- Know which Debian codename corresponds to which Proxmox VE version (trixie = PVE 9.x, bookworm = PVE 8.x)
- Practice deliberate deferral: some fixes should wait for a recovery path to exist before proceeding
