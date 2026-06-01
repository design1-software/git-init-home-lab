# Runbook: SSH Host Key Collision

**Trigger:** `Host key verification failed` when SSHing to a known IP after a gateway IP moved between physical devices.

**Cause:** When a gateway or management IP changes hands — HSRP failover, HSRP teardown, or a router reclaiming an IP that was previously on a different device — the new device presents a different RSA host key. OpenSSH's `known_hosts` still has the old key cached for that IP and refuses to connect as a security measure.

---

## Fix

```bash
ssh-keygen -R <IP>
```

Then reconnect and accept the new fingerprint when prompted.

---

## Verify identity before accepting

Before accepting an unknown fingerprint, cross-check it:

1. SSH to the IP — OpenSSH will print:

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
...
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:X: 192.168.100.1
```

2. If the "other names/addresses" line shows another IP you already trust for this device (e.g., the C1111's Vlan1 SVI at 192.168.100.1 when you're now trying 192.168.10.1), the key is already in your known_hosts under a different IP. Same key → same device → safe to accept.

3. If no cross-reference appears, verify the fingerprint out-of-band (console access, Tailscale, etc.) before accepting.

---

## When this happens in this lab

| Scenario | Affected IP | Action |
|---|---|---|
| HSRP configured on a new IP — 3560CX takes over as active | Any VLAN gateway (.1) | `ssh-keygen -R 192.168.X.1` on all SSH clients |
| HSRP torn down — C1111 reclaims the gateway IP | Any VLAN gateway (.1) | `ssh-keygen -R 192.168.X.1` on all SSH clients |
| 3560CX SSH configured for first time after cutover | 192.168.10.1 (new) | Accept new fingerprint; cross-check against known C1111 key |

---

## Prevention

Configure a stable, device-specific management IP for each device that never moves between devices (e.g., VLAN 99 loopbacks or dedicated mgmt IPs). Only floating VIPs (HSRP) should change hands.
