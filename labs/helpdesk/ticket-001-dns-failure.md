# Helpdesk Ticket 001 — DNS Resolution Failing

**Domain:** DNS / Pi-hole
**Difficulty:** Beginner
**Estimated time:** 20–30 minutes
**CCNA domain:** IP Services (Domain 4)

---

## Scenario

A student reports: *"I'm connected to WiFi but websites aren't loading. I can't browse anything."*

The student is on VLAN 20 (TRUSTED, SSID: Gorgeous). Ping to 8.8.8.8 works. Ping to google.com fails.

---

## Ticket Details

**Reported by:** Lab user
**Affected system:** Client device, DNS
**Priority:** Medium
**Category:** Network — DNS

---

## AI Mentor Opening Questions

The mentor does not jump to a solution. It asks:

```
1. What network are you connected to?
2. Can you ping 8.8.8.8?
3. Can you ping google.com?
4. What DNS server is your device configured to use?
   (Windows: ipconfig /all | MacOS: networksetup -getdnsservers Wi-Fi | Linux: resolvectl status)
5. Can you reach http://192.168.10.16/admin?
```

---

## Evidence Required

The student must provide:

```
- Output of: ping 8.8.8.8 (success or failure)
- Output of: ping google.com (success or failure)
- DNS server assigned to client (from ipconfig/networksetup/resolvectl)
- Pi-hole admin UI reachable? (yes/no)
- nslookup google.com (from client)
```

---

## Diagnostic Path

```
If ping 8.8.8.8 works but ping google.com fails:
  → DNS issue confirmed
  → Check assigned DNS server
  → If not 192.168.10.16: DHCP issue or client override
  → If 192.168.10.16: Pi-hole may be blocking or down
  → Check Pi-hole admin at http://192.168.10.16/admin
  → Check: is the domain being blocked? (query log)
  → Check: is Pi-hole running? (ssh admin@192.168.10.16 → pihole status)

If Pi-hole is blocking the domain:
  → Is it a false positive? Check blocklist and whitelist if needed
  → Domains to whitelist if needed: gsa.apple.com, apps.apple.com, configuration.apple.com

If ping 8.8.8.8 also fails:
  → Routing issue, not DNS → escalate to VLAN/routing ticket
```

---

## Expected Root Causes

| Root cause | Likelihood | Verification |
|---|---|---|
| Pi-hole blocking domain | High | Query log in Pi-hole admin UI |
| Pi-hole service down | Medium | `pihole status` via SSH |
| Client using wrong DNS server | Medium | `ipconfig /all` or `resolvectl` |
| DHCP not assigning correct DNS | Low | Check DHCP lease on router/switch |
| VLAN routing failure | Low | Ping to gateway fails |

---

## Resolution Path

1. Identify whether Pi-hole is running (`pihole status`)
2. If running, check query log for blocked domains
3. Whitelist if false positive, or advise student the domain is blocked by policy
4. If Pi-hole is down: `sudo systemctl restart pihole-FTL`
5. Verify resolution: `nslookup google.com 192.168.10.16`

---

## Documentation Prompt

After resolution, the mentor asks:

```
Write a one-paragraph incident summary covering:
- What was the reported symptom
- What commands you ran to isolate the cause
- What you found
- What you did to fix it
- How you confirmed it worked
```

---

## Learning Objectives

- Distinguish between connectivity failure and DNS failure using ping
- Identify the DNS server from client network config
- Navigate Pi-hole admin UI to inspect query logs
- Understand the role of Pi-hole as a recursive DNS resolver and blocker
- Practice structured troubleshooting before escalating
