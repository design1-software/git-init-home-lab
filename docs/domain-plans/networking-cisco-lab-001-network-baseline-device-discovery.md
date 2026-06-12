# Networking/Cisco Lab 001 - Network Baseline and Device Discovery

Status: Draft for validation  
Domain: Networking / Cisco / DNS / VLAN / Switching  
Lab Type: Read-only discovery and evidence collection  
Risk Level: Low  
Target Environment: ARIA home lab / VLAN 60 and VLAN 70  
Primary Student Role: Beginner network technician / help desk escalation trainee  

## Lab Objective

Teach students how to collect a basic network baseline from a Windows or Linux endpoint and relate that evidence to the ARIA Cisco network design.

This lab is intentionally read-only. Students will not change Cisco, Proxmox, Windows, Linux, DNS, DHCP, firewall, or VLAN configuration.

The student will learn how to answer these questions with evidence:

```text
What device am I on?
What IP address do I have?
What subnet am I on?
What is my default gateway?
What DNS server am I using?
Can I reach my gateway?
Can I reach the domain controller?
Can I resolve internal names?
Can I resolve public names?
Can I reach the internet by IP?
What does the network path look like?
```

## Why This Lab Matters

Before changing anything in a network, a technician must understand the current state.

This lab teaches students to slow down and collect evidence before guessing.

Professional network troubleshooting starts with:

```text
1. Identify the endpoint.
2. Identify the IP configuration.
3. Test the default gateway.
4. Test DNS.
5. Test internal resources.
6. Test internet reachability.
7. Document what works and what fails.
```

## Safety Guardrail

This lab is read-only.

Students must not run configuration commands on Cisco devices.

Do not use:

```text
configure terminal
conf t
interface
ip address
shutdown
no shutdown
switchport
router ospf
access-list
write memory
copy running-config startup-config
```

Allowed actions:

```text
View network settings
Run ping tests
Run DNS lookups
Run traceroute/tracert
Run show commands if instructor provides read-only Cisco access
Record evidence
Write a summary
```

## Current ARIA Network Context

Relevant known infrastructure:

```text
Cisco C1111-4PWB = WAN edge / NAT / default route originator / OSPF neighbor
Cisco Catalyst 3560CX-8PC-S = active L3 core / VLAN gateways / ACLs / switching
Proxmox Server / ARIA = 192.168.70.10 on VLAN 70
JLM-DC01 = 192.168.60.10 on VLAN 60
VLAN 60 = LAB workload network
VLAN 70 = ARIA / Proxmox management network
```

Important bridge and port path:

```text
VLAN 70 = Proxmox management path on vmbr0 / nic1 / 3560CX Gi0/4
VLAN 60 = Lab workload path on vmbr1 / nic0 / 3560CX Gi0/6
```

Important VLAN 60 design rule:

```text
Do not tag VM NICs on vmbr1.
3560CX Gi0/6 is an access VLAN 60 port.
VM traffic on vmbr1 should be untagged.
```

## Student Starting Point

The student should start from one of these systems:

```text
JLM-WIN01 on VLAN 60
student-linux-01 if used as Linux endpoint
Another instructor-approved lab endpoint
```

The instructor should tell the student which endpoint to use.

## Required Tools

Windows tools:

```text
Command Prompt
PowerShell
ipconfig
ping
tracert
nslookup
hostname
whoami
```

Linux tools:

```text
bash shell
hostname
ip addr
ip route
resolvectl
ping
traceroute or tracepath
```

Optional Cisco read-only tools:

```text
show ip interface brief
show vlan brief
show interfaces status
show ip route
show ip ospf neighbor
show access-lists
```

## Part 1 - Identify the Endpoint

### Windows Commands

Run:

```cmd
hostname
whoami
ipconfig /all
```

Record:

```text
Hostname:
Logged-in user:
IPv4 address:
Subnet mask:
Default gateway:
DNS server:
Connection-specific DNS suffix:
```

### Linux Commands

Run:

```bash
hostname
whoami
ip addr
ip route
resolvectl status
```

Record:

```text
Hostname:
Logged-in user:
IPv4 address:
Subnet/CIDR:
Default gateway:
DNS server:
Search domain:
```

## Part 2 - Identify the Likely VLAN

Use the endpoint IP address to infer the VLAN.

Known examples:

```text
192.168.60.0/24 = VLAN 60 LAB
192.168.70.0/24 = VLAN 70 SERVER / ARIA management
```

Student answer format:

```text
My endpoint IP is: __________
My likely VLAN is: __________
My evidence is: __________
```

## Part 3 - Test Default Gateway Reachability

### Windows

Run:

```cmd
ping <default-gateway-ip>
```

Example for VLAN 60:

```cmd
ping 192.168.60.1
```

### Linux

Run:

```bash
ping -c 4 <default-gateway-ip>
```

Example for VLAN 60:

```bash
ping -c 4 192.168.60.1
```

Expected result:

```text
Successful replies from the default gateway.
```

If the gateway does not respond, the issue may be local IP configuration, VLAN placement, switchport configuration, or gateway availability.

Do not assume DNS is the problem if the default gateway cannot be reached.

## Part 4 - Test Internal Resource Reachability

From VLAN 60, test the domain controller:

### Windows

```cmd
ping 192.168.60.10
```

### Linux

```bash
ping -c 4 192.168.60.10
```

Expected result:

```text
Successful replies from JLM-DC01 if ICMP is allowed.
```

If ping fails, document the result. ICMP failure does not always mean the host is down. Continue with DNS tests if instructed.

## Part 5 - Test Public Internet by IP

### Windows

```cmd
ping 1.1.1.1
tracert 1.1.1.1
```

### Linux

```bash
ping -c 4 1.1.1.1
tracepath 1.1.1.1
```

Expected result:

```text
Successful IP reachability to 1.1.1.1.
```

If IP reachability works but name resolution fails, the problem may be DNS.

If IP reachability fails, the problem may be routing, gateway, ACL, NAT, or upstream connectivity.

## Part 6 - Test DNS Resolution

### Windows

Run:

```cmd
nslookup jlm.lab
nslookup google.com
```

Also run:

```cmd
ipconfig /displaydns
```

### Linux

Run:

```bash
resolvectl query jlm.lab
resolvectl query google.com
```

Expected result:

```text
Internal names resolve using the configured DNS path.
Public names resolve using the configured DNS path.
```

Student must identify which DNS server answered the query.

## Part 7 - Compare IP Reachability vs DNS Reachability

Complete this table:

| Test | Result | What It Proves |
|---|---|---|
| Ping default gateway | Pass/Fail | Local VLAN/gateway path |
| Ping 192.168.60.10 | Pass/Fail | Internal host reachability |
| Ping 1.1.1.1 | Pass/Fail | Internet by IP |
| nslookup jlm.lab | Pass/Fail | Internal DNS |
| nslookup google.com | Pass/Fail | Public DNS |
| tracert/tracepath 1.1.1.1 | Pass/Fail | Route path |

## Part 8 - Optional Cisco Read-Only Evidence

Only run these commands if the instructor provides read-only Cisco access.

Do not enter configuration mode.

### 3560CX Read-Only Commands

```text
show ip interface brief
show vlan brief
show interfaces status
show ip route
show ip ospf neighbor
show access-lists
```

### Evidence to Capture

```text
VLAN 60 SVI exists
VLAN 70 SVI exists
Relevant switchports are up/up or connected
OSPF neighbor relationship exists where expected
Routes exist for lab and server networks
ACLs are present for segmentation
```

## Student Evidence Checklist

Submit the following:

```text
[ ] Hostname output
[ ] Logged-in user output
[ ] IP configuration output
[ ] Default gateway identified
[ ] DNS server identified
[ ] Likely VLAN identified
[ ] Ping to default gateway
[ ] Ping to internal resource or explanation if blocked
[ ] Ping to 1.1.1.1
[ ] DNS lookup for jlm.lab
[ ] DNS lookup for google.com
[ ] Tracert/tracepath to 1.1.1.1
[ ] Completed results table
[ ] Short written summary
```

## Student Summary Template

Students should complete this:

```text
I tested from endpoint: __________
My IP address is: __________
My default gateway is: __________
My DNS server is: __________
My likely VLAN is: __________

Gateway reachability: Pass / Fail
Internal resource reachability: Pass / Fail
Internet by IP: Pass / Fail
Internal DNS: Pass / Fail
Public DNS: Pass / Fail

Based on my evidence, this endpoint appears to be correctly / incorrectly connected to the network because:
__________

If I had to escalate this ticket, I would include:
__________
```

## Troubleshooting Decision Tree

Use this logic:

```text
No IP address?
  -> Check DHCP, adapter state, VLAN placement.

IP address but no default gateway?
  -> Check DHCP options or static configuration.

Gateway unreachable?
  -> Check local subnet, VLAN, switchport, Proxmox bridge, or gateway SVI.

Gateway reachable but 1.1.1.1 unreachable?
  -> Check routing, ACL, NAT, or upstream path.

1.1.1.1 reachable but google.com does not resolve?
  -> Check DNS server, Pi-hole, domain DNS, or client DNS cache.

Internal DNS fails but public DNS works?
  -> Check domain DNS configuration or conditional forwarding.

Everything works?
  -> Document baseline as healthy.
```

## ARIA AI Mentor Role

ARIA should not give the answer immediately.

ARIA should coach students with questions like:

```text
What is your endpoint IP address?
What subnet does that IP belong to?
What is your default gateway?
Can you ping your gateway?
Can you reach the domain controller?
Can you reach the internet by IP?
Can you resolve internal names?
Can you resolve public names?
Which result points to DNS instead of routing?
Which result points to routing instead of DNS?
What command proves your conclusion?
What would you include in a ticket escalation note?
```

## Instructor Validation

The instructor should confirm:

```text
[ ] Student collected endpoint identity evidence
[ ] Student identified IP, gateway, DNS, and likely VLAN
[ ] Student tested gateway reachability
[ ] Student tested internal reachability
[ ] Student tested internet by IP
[ ] Student tested DNS
[ ] Student completed the table
[ ] Student wrote a reasonable summary
[ ] Student did not perform configuration changes
```

## Completion Criteria

This lab is complete when the student can explain:

```text
What network they are on
What their gateway is
What DNS server they use
Whether basic reachability works
Whether DNS works
What evidence supports their conclusion
```

## Key Lesson

The key lesson of this lab is:

```text
Baseline first. Troubleshoot second. Change last.
```

A professional technician collects evidence before making changes.

## Next Lab

Next planned lab:

```text
Networking/Cisco Lab 002 - VLANs, Subnets, and Default Gateways
```
