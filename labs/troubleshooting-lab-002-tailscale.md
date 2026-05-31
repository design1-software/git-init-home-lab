# Troubleshooting Lab 002 — Tailscale DNS Hijack & TCP Socket Corruption

> Date: April 21, 2026
> Duration: ~45 minutes
> Severity: Total loss of TCP connectivity on MacBook Pro
> Root Cause: Tailscale MagicDNS + stale tunnel interface corrupting TCP socket state

---

## Scenario Summary

After installing Tailscale on the MacBook Pro and Acer server for remote management, the MacBook lost the ability to load websites, SSH into the Cisco, or establish any TCP connection. ICMP (ping) continued to work normally. The Acer (wired, same VLAN) was unaffected.

---

## Symptom Presentation

- Websites returned `ERR_ADDRESS_INVALID` in the browser
- `curl -I https://github.com` → `Failed to connect to github.com port 443: Couldn't connect to server`
- `ssh admin@192.168.10.1` → `Can't assign requested address`
- `nc -zv 140.82.112.3 443` → `Can't assign requested address`
- `ping 8.8.8.8` → 100% success, ~20ms
- `ping 192.168.20.1` (gateway) → 100% success
- `ping 192.168.10.16` (Pi-hole, cross-VLAN) → 100% success

**Key observation:** ICMP worked perfectly. All TCP connections failed with "Can't assign requested address" — a local socket error, not a network timeout.

---

## Step-by-Step Troubleshooting

### Step 1: Identify the Symptom Pattern
**What you observed:** Websites wouldn't load on the MacBook. SSH to the Cisco failed. But ping to all destinations worked fine.

**CCNA Skill:** Recognizing the difference between Layer 3 reachability (ICMP) and Layer 4 connectivity (TCP). When ping works but applications fail, the issue is above Layer 3. Maps to: *IP connectivity troubleshooting, TCP/IP transport layer*.

---

### Step 2: Verify Layer 3 Path
**What you did:**
```
ping -c 3 192.168.20.1   → success (gateway)
ping -c 3 192.168.10.16  → success (cross-VLAN to Pi-hole)
ping -c 3 8.8.8.8        → success (internet)
```

**Result:** Full Layer 3 reachability confirmed across VLANs and to the internet. Routing table showed correct default gateway (192.168.20.1). IP address was correct (192.168.20.25 on VLAN 20).

**CCNA Skill:** Systematic Layer 3 verification — local gateway, cross-VLAN, internet. Maps to: *IP connectivity, inter-VLAN routing verification*.

---

### Step 3: Test TCP Independently
**What you did:**
```
curl -I --connect-timeout 5 https://8.8.8.8    → Failed to connect
nc -zv 140.82.112.3 443 -w 5                   → Can't assign requested address
```

**Result:** TCP connections failed even when bypassing DNS (using raw IPs). This proved the issue was not DNS-related — it was a TCP socket-level failure on the MacBook itself.

**CCNA Skill:** Isolating transport layer (Layer 4) failures from application layer issues. Using `nc` (netcat) for raw TCP testing. Maps to: *TCP/IP troubleshooting, transport layer operations*.

---

### Step 4: Investigate DNS Configuration
**What you did:**
```
scutil --dns | head -20
```

**Discovery:** Tailscale had inserted itself as the primary DNS resolver:
```
resolver #1
  nameserver[0] : 100.100.100.100      ← Tailscale's internal DNS
  search domain[0] : tail19880b.ts.net  ← Tailscale's MagicDNS
  if_index : 26 (utun8)                ← Tailscale's VPN tunnel interface
  order : 101200                        ← Higher priority than Pi-hole

resolver #2
  nameserver[0] : 192.168.10.16        ← Pi-hole (should be primary)
  order : 200000                        ← Lower priority
```

Tailscale's MagicDNS (100.100.100.100) was intercepting all DNS queries before they reached Pi-hole, and routing them through the utun8 tunnel interface.

**CCNA Skill:** Understanding DNS resolver priority, VPN split-tunnel vs full-tunnel DNS behavior, interface-specific DNS resolution. Maps to: *DNS operations, VPN concepts, network services*.

---

### Step 5: Disable MagicDNS
**What you did:** Opened Tailscale preferences, disabled MagicDNS.

**Result:** DNS resolver changed to Pi-hole as primary. Some websites started loading. But the fix was intermittent — connections continued failing.

**CCNA Skill:** Understanding that VPN overlay networks modify the host's DNS and routing configuration. Maps to: *VPN fundamentals, DNS troubleshooting*.

---

### Step 6: Quit Tailscale Entirely
**What you did:** Quit Tailscale from the menu bar, flushed DNS cache.
```
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Result:** Websites loaded briefly, then TCP failures returned. The `curl` and `nc` commands continued showing "Can't assign requested address" — indicating the problem persisted even after Tailscale was no longer running.

**CCNA Skill:** Understanding that stopping a VPN client doesn't always clean up network state (routes, DNS, socket bindings). Maps to: *VPN troubleshooting, network state management*.

---

### Step 7: Diagnose Socket-Level Failure
**What you observed:** The error "Can't assign requested address" is a local operating system error (EADDRNOTAVAIL), not a network error. It means the OS cannot bind a local TCP socket to send the connection request. This is not a firewall block, not a routing issue, and not a DNS issue — it's the TCP/IP stack on the MacBook itself that is broken.

**Analysis:** Tailscale creates a virtual tunnel interface (utun8) and modifies the OS routing table and socket bindings to intercept traffic. When Tailscale was quit, the utun8 interface was removed, but the socket binding state was not fully cleaned up. The OS was still trying to route TCP connections through a tunnel that no longer existed.

**CCNA Skill:** Understanding the OSI model — this is a Layer 4/5 issue on the host itself, not a network infrastructure problem. Understanding virtual interfaces and their impact on the host TCP stack. Maps to: *OSI model application, host-level network troubleshooting*.

---

### Step 8: Reboot the MacBook
**What you did:** Full system restart.

**Result:** All TCP connections immediately worked after reboot. `curl -I https://github.com` returned HTTP/2 200. Websites loaded. SSH connected.

**Why it worked:** The reboot cleared all stale socket bindings, ARP caches, DNS caches, and virtual interface state. The TCP/IP stack reinitialized cleanly without Tailscale's modifications.

**CCNA Skill:** Knowing when to escalate from software troubleshooting to a clean restart. In enterprise environments, this is equivalent to restarting a service or clearing a device's control plane. Maps to: *Troubleshooting methodology, knowing when to reset vs. when to debug further*.

---

## Root Cause Analysis

**Primary cause:** Tailscale's MagicDNS feature hijacked DNS resolution on the MacBook by inserting itself as the highest-priority DNS resolver (100.100.100.100 on utun8 tunnel interface, order 101200) above the DHCP-provided Pi-hole DNS (192.168.10.16, order 200000).

**Secondary cause:** When Tailscale was disabled and quit, its virtual tunnel interface (utun8) was removed but TCP socket bindings associated with that interface were not properly released. The MacBook's TCP stack entered a corrupted state where no new TCP connections could be created (EADDRNOTAVAIL error on all TCP socket creation attempts), while ICMP (which doesn't use TCP sockets) continued to work normally.

**Resolution:** Full system reboot cleared all stale network state. Tailscale's MagicDNS was disabled before reconnecting to prevent recurrence.

---

## Impact Assessment

| Affected | Not Affected |
|---|---|
| MacBook Pro (WiFi, VLAN 20) | Acer Server (wired, VLAN 10) |
| All TCP: HTTPS, SSH, curl, nc | All ICMP: ping |
| All browsers | Cisco router operations |
| Claude AI chat interface | Pi-hole DNS service |
| All streaming apps | UniFi Controller |

The outage was limited to the MacBook because Tailscale was only installed on the MacBook and Acer. The Acer was unaffected because its Tailscale installation did not have MagicDNS enabled by default (Windows handles DNS differently than macOS).

---

## CCNA Exam Topics Demonstrated

| CCNA Topic | How You Applied It |
|---|---|
| 1.1 Network Components | Identified that the issue was host-local, not network infrastructure |
| 1.5 TCP vs UDP vs ICMP | Used the ICMP-works-but-TCP-fails pattern to isolate the failure layer |
| 3.3 Default Gateway | Verified gateway reachability to confirm Layer 3 was intact |
| 4.5 DNS | Identified Tailscale's DNS hijack via `scutil --dns`, understood resolver priority |
| 5.3 IP Connectivity Troubleshooting | Systematic bottom-up approach from Layer 1 to Layer 7 |
| 5.5 Network Security | Understood how VPN overlay networks modify host network configuration |
| 1.2 VPN Concepts | Understood tunnel interfaces (utun8), split-DNS, and VPN impact on routing |

---

## Prevention Measures

1. **Always disable MagicDNS** before connecting Tailscale on machines that use Pi-hole or custom DNS
2. **Use `tailscale set --accept-dns=false`** on initial setup to prevent DNS hijacking
3. **Test connectivity immediately** after installing any VPN client — don't wait until you need it
4. **Know the reboot option** — when a VPN client corrupts the host TCP stack, restarting the service isn't enough; a full OS reboot is required

---

## Key Lessons Learned

1. **VPN clients modify more than routing.** Tailscale changed DNS resolution, interface priority, and TCP socket bindings — all without explicit user consent. Enterprise VPN clients (Cisco AnyConnect, GlobalProtect) do the same thing.

2. **"Can't assign requested address" means the local TCP stack is broken.** This is not a network error — it's a host OS error. No amount of router or switch troubleshooting will fix it.

3. **ICMP success ≠ TCP success.** This is the second time in this lab (after the Apple TV incident) that ping worked while applications failed. They test different things: ICMP tests Layer 3 reachability, TCP tests Layer 4 connectivity and local socket state.

4. **Always check DNS configuration after installing a VPN.** VPN clients routinely insert themselves as the primary DNS resolver, which can break Pi-hole, corporate DNS, and any other custom DNS infrastructure.

5. **The Acer being unaffected was the critical clue.** Same VLAN, same gateway, same Cisco WAN path — but the Acer worked fine. That immediately ruled out every network component (router, switch, ISP, NAT, MSS) and pointed to the MacBook itself.

---

*This incident demonstrated that not all network problems are network problems. Sometimes the issue is the host — and recognizing that quickly is what separates efficient troubleshooting from hours of chasing the wrong lead.*
