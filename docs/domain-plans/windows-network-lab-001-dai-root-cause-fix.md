# Windows Network Lab 001 - DAI Root Cause and Fix

Status: Root cause identified and fixed  
Domain: Networking / Windows Endpoint Network Troubleshooting / DNS / DHCP / Reachability  
Related Lab: Windows Network Lab 001 - Endpoint Baseline and Reachability  
Affected Systems: JLM-WIN01, JLM-DC01, JLM-LAB-SW1  
Affected VLAN: VLAN 60 LAB  
Root Cause Area: Cisco DHCP Snooping / Dynamic ARP Inspection / IP Source Guard with static infrastructure host  

## Summary

Windows Network Lab 001 originally appeared to show a DNS problem from JLM-WIN01 because the client could reach the internet by IP but DNS lookups through 192.168.60.10 were delayed or failing.

Further testing showed the actual root cause was upstream from DNS:

```text
JLM-DC01 was reachable by clients, but JLM-DC01 could not reach its own default gateway 192.168.60.1.
```

The final root cause was Cisco Layer 2 security enforcement on VLAN 60:

```text
Dynamic ARP Inspection and IP Source Guard were active on VLAN 60.
JLM-WIN01 worked because it had a DHCP snooping binding.
JLM-DC01 used a static IP address and did not have a DHCP snooping/source binding.
The switch dropped ARP traffic from JLM-DC01.
```

The fix was to add a static source binding for JLM-DC01 on JLM-LAB-SW1.

## Original Symptom from JLM-WIN01

JLM-WIN01 showed valid IP configuration:

```text
Endpoint: JLM-WIN01
IP address: 192.168.60.14/24
Default gateway: 192.168.60.1
DHCP server: 192.168.60.1
DNS server: 192.168.60.10
```

JLM-WIN01 could reach the network by IP:

```text
ping 192.168.60.1: Passed
ping 192.168.60.10: Passed
ping 1.1.1.1: Passed
ping 8.8.8.8: Passed
tracert 1.1.1.1: Completed
```

But DNS through 192.168.60.10 was delayed or failing:

```text
nslookup jlm.lab: initial timeout, then resolved
nslookup google.com: timed out through 192.168.60.10
```

Initial interpretation:

```text
The endpoint routing path works, but DNS through 192.168.60.10 needs review.
```

## JLM-DC01 Diagnostic Evidence

JLM-DC01 had expected static IP configuration:

```text
Hostname: JLM-DC01
IP address: 192.168.60.10/24
Default gateway: 192.168.60.1
DNS servers: ::1 and 127.0.0.1
```

But JLM-DC01 could not reach its gateway or the internet:

```text
ping 192.168.60.1: Destination host unreachable from 192.168.60.10
ping 1.1.1.1: Destination host unreachable from 192.168.60.10
ping 8.8.8.8: Destination host unreachable from 192.168.60.10
tracert 1.1.1.1: JLM-DC01 reported destination host unreachable
```

Route table showed the correct default route:

```text
0.0.0.0/0 via 192.168.60.1 interface 192.168.60.10
```

This proved the issue was not a missing Windows default gateway. The problem was lower in the path, likely Layer 2/ARP/security inspection.

## Cisco Evidence

On JLM-LAB-SW1:

```text
show ip arp inspection statistics vlan 60
```

Output showed high ARP drops:

```text
Vlan 60
Forwarded: 289
Dropped: 42265+
DHCP Drops: 42265+
ACL Drops: 0
```

This proved Dynamic ARP Inspection was dropping ARP on VLAN 60.

DHCP snooping bindings showed DHCP clients but did not show JLM-DC01:

```text
show ip dhcp snooping binding | include 192.168.60
```

Observed DHCP bindings included:

```text
192.168.60.11 on Gi0/6
192.168.60.13 on Gi0/6
192.168.60.14 on Gi0/6
```

JLM-DC01 was missing because it uses a static IP address:

```text
JLM-DC01 IP: 192.168.60.10
JLM-DC01 MAC: BC:24:11:B4:88:BF
```

VLAN 60 inspection was active:

```text
ip arp inspection vlan 30-31,40,50,60
ip dhcp snooping vlan 30-31,40,50,60
ip dhcp snooping
```

Gi0/6 was configured as the Proxmox VLAN 60 lab path and had IP Source Guard enabled:

```text
interface GigabitEthernet0/6
 description ARIA-PROXMOX-VLAN60-ADLAB
 switchport access vlan 60
 switchport mode access
 spanning-tree portfast edge
 spanning-tree bpduguard enable
 ip verify source
```

## Root Cause

Final root cause:

```text
JLM-DC01 is a static-IP infrastructure VM behind Proxmox vmbr1 on VLAN 60.
VLAN 60 has DHCP Snooping, Dynamic ARP Inspection, and IP Source Guard enabled.
Because JLM-DC01 does not receive its IP by DHCP, it did not have an automatic DHCP snooping binding.
The switch dropped ARP traffic from JLM-DC01, preventing it from reaching 192.168.60.1.
```

Why JLM-WIN01 worked:

```text
JLM-WIN01 received its address by DHCP and had a DHCP snooping binding.
DAI/IP Source Guard allowed JLM-WIN01 traffic.
```

Why JLM-DC01 failed:

```text
JLM-DC01 used static IP 192.168.60.10 and had no automatic binding.
DAI/IP Source Guard treated its ARP/source traffic as untrusted.
```

## Fix Applied

A static source binding was added on JLM-LAB-SW1:

```text
conf t
ip source binding bc24.11b4.88bf vlan 60 192.168.60.10 interface gi0/6
end
```

Running configuration confirmed:

```text
show running-config | include ip source binding
ip source binding BC24.11B4.88BF vlan 60 192.168.60.10 interface Gi0/6
```

## Post-Fix Validation

After clearing ARP on JLM-DC01:

```powershell
arp -d *
ping 192.168.60.1
ping 1.1.1.1
nslookup google.com
```

JLM-DC01 successfully reached the gateway:

```text
ping 192.168.60.1: Passed
Replies from 192.168.60.1, 0% loss
```

JLM-DC01 successfully reached the internet by IP:

```text
ping 1.1.1.1: Passed
Replies from 1.1.1.1, 0% loss
```

DNS lookup improved:

```text
nslookup google.com: returned google.com IPv6 records after initial timeout
```

This confirmed the static source binding restored JLM-DC01 outbound network reachability.

## Best-Practice Decision

The lab should keep these protections enabled:

```text
DHCP Snooping
Dynamic ARP Inspection
IP Source Guard
```

Do not permanently fix the issue by trusting Gi0/6 unless the entire Proxmox lab path is intentionally trusted.

Do not permanently fix the issue by disabling DAI on VLAN 60.

Best practice for this ARIA lab:

```text
DHCP clients use normal DHCP snooping bindings.
Static infrastructure hosts must be documented and given static source bindings.
DAI/IP Source Guard remain enabled.
Hypervisor lab ports remain untrusted unless explicitly designed otherwise.
```

## Student Learning Value

This is a strong real-world training scenario because the first symptom looked like DNS failure, but the root cause was Layer 2 security enforcement.

The troubleshooting path was:

```text
1. Windows client showed DNS lookup failure.
2. Windows client still had working IP reachability.
3. DNS server was reachable by IP from the client.
4. DNS server could not reach its own gateway.
5. Route table on DNS server was correct.
6. Cisco DAI statistics showed ARP drops on VLAN 60.
7. DHCP snooping table showed DHCP clients but not the static DC.
8. Static source binding fixed the issue.
```

Key lesson:

```text
Not every DNS symptom is a DNS root cause.
Endpoint evidence must be correlated with server evidence and network infrastructure evidence.
```

## Carry Forward

This finding should be referenced in future labs:

```text
Windows Network Lab 003 - DNS Failure vs Routing Failure
Windows Network Lab 005 - Domain/DNS Path Validation for jlm.lab
Future Cisco IOS Lab - DHCP Snooping, DAI, and IP Source Guard
```

## Commands to Recheck Later

On JLM-LAB-SW1:

```text
show running-config | include ip source binding
show ip arp inspection statistics vlan 60
show ip dhcp snooping binding | include 192.168.60
show running-config interface gi0/6
```

On JLM-DC01:

```powershell
ping 192.168.60.1
ping 1.1.1.1
nslookup jlm.lab
nslookup google.com
```
