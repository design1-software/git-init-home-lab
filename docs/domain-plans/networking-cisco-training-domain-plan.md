# Networking / Cisco / DNS / VLAN / Switching Training Domain Plan

Status: Next training domain plan  
Domain: Networking / Cisco / DNS / VLAN / Switching  
Platform: ARIA IT Enterprise Training Platform  
Current Position: Identity/IAM foundational v1 complete; Networking is the next domain to catch up  

## Purpose

This document defines the next ARIA training domain build after completing the Identity/IAM six-lab foundational block.

The goal is to turn the already mature physical Cisco/VLAN infrastructure into a structured student training path with clear lab objectives, command evidence, troubleshooting prompts, and ARIA AI Mentor guidance.

## Why Networking Is Next

ARIA must remain balanced across five training domains:

```text
1. Help Desk / Ticketing
2. Networking / Cisco / DNS / VLAN / Switching
3. Security / SOC / Wazuh / Incident Review
4. Automation / SysAdmin / Linux / Proxmox / Field-Tech
5. Identity / IAM / Active Directory / GPO / Windows Endpoint Administration
```

Current status:

```text
[x] Help Desk / Ticketing - Complete v1
[x] Automation / SysAdmin / Linux / Proxmox / Field-Tech - Complete v1
[x] Identity / IAM / Active Directory / GPO / Windows Endpoint Administration - Foundational v1 complete
[~] Networking / Cisco / DNS / VLAN / Switching - Infrastructure mature, student lab path needed
[ ] Security / SOC / Wazuh / Incident Review - Infrastructure pending
```

Networking is the correct next domain because the infrastructure already exists and has been validated:

- Cisco C1111 edge router
- Cisco Catalyst 3560CX active L3 core
- VLAN segmentation
- OSPFv2 adjacency between C1111 and 3560CX
- VLAN 60 lab network path
- VLAN 70 Proxmox management path
- DNS through Pi-hole
- DHCP, ACLs, trunking, and switch security features
- Proxmox workloads tied into lab VLAN design

This domain can now be converted from infrastructure documentation into student-facing training labs.

## Current Network Foundation

Current production/lab network foundation:

```text
Cisco C1111-4PWB = WAN edge / NAT / default route originator / OSPF neighbor
Cisco Catalyst 3560CX-8PC-S = active L3 core / VLAN gateways / inter-VLAN ACLs / DHCP post-cutover
NETGEAR GS308EP + GS316EP = access-layer switches
Raspberry Pi 4B = Pi-hole DNS / UniFi / Mosquitto / CUPS / NTP client
Proxmox Server / ARIA = VLAN 70 management and VLAN 60 lab workloads
```

Important VLAN paths:

```text
VLAN 70 = Proxmox / ARIA management path on vmbr0 / nic1 / 3560CX Gi0/4
VLAN 60 = Lab workload path on vmbr1 / nic0 / 3560CX Gi0/6
```

Important VLAN 60 design rule:

```text
Do not tag VM NICs on vmbr1.
3560CX Gi0/6 is an access VLAN 60 port.
VM traffic on vmbr1 should be untagged.
```

## Training Domain Goal

Build a six-lab Networking/Cisco foundational block that teaches students how enterprise networks are segmented, verified, troubleshot, and documented.

The labs should be beginner-accessible but still real-world enough to prepare students for help desk escalation, junior network technician work, SOC context, and CCNA-style thinking.

## Proposed Six-Lab Networking Foundation

```text
Lab 001 - Network Baseline and Device Discovery
Lab 002 - VLANs, Subnets, and Default Gateways
Lab 003 - Trunk vs Access Port Troubleshooting
Lab 004 - DNS and DHCP Troubleshooting
Lab 005 - Inter-VLAN ACL Verification
Lab 006 - Switch Security Basics: PortFast, BPDU Guard, DHCP Snooping, DAI, and IP Source Guard
```

These six labs should be built one at a time, validated manually, documented, committed, and pushed before moving to the next lab.

---

# Lab 001 - Network Baseline and Device Discovery

## Objective

Teach students how to identify network devices, IP addresses, default gateways, DNS servers, VLAN placement, and basic reachability.

## Skills Taught

- Reading a network map
- Identifying endpoint IP configuration
- Using `ipconfig`, `ping`, `tracert`, and `nslookup`
- Understanding default gateways
- Finding the domain controller and DNS path
- Differentiating management, server, and lab VLANs

## Student Tasks

Students should document:

```text
Hostname
IP address
Subnet mask
Default gateway
DNS server
Domain name
Reachability to gateway
Reachability to DNS
Reachability to domain controller
Internet reachability
```

## Example Commands

Windows:

```cmd
hostname
ipconfig /all
ping 192.168.60.1
ping 192.168.60.10
nslookup jlm.lab
tracert 1.1.1.1
```

Linux:

```bash
hostname
ip addr
ip route
resolvectl status
ping -c 4 192.168.60.1
ping -c 4 192.168.60.10
traceroute 1.1.1.1
```

## Evidence

- Screenshot or output of IP configuration
- Successful gateway ping
- Successful DNS lookup
- Short written network summary

## ARIA Mentor Questions

- What is your IP address?
- What VLAN do you appear to be on?
- What is your default gateway?
- Which device provides DNS?
- Can you reach the domain controller?
- Can you reach the internet?
- What command proves each answer?

---

# Lab 002 - VLANs, Subnets, and Default Gateways

## Objective

Teach students how VLANs map to subnets, gateways, and network roles.

## Skills Taught

- VLAN purpose
- Subnet identification
- Gateway identification
- Management vs production vs lab segmentation
- Why VLANs reduce broadcast scope and improve policy control

## Student Tasks

Students should complete a VLAN/subnet table for the ARIA lab.

Example format:

```text
VLAN ID | Name/Purpose | Subnet | Gateway | Key Devices
```

Required known paths:

```text
VLAN 60 = LAB workload network
VLAN 70 = ARIA / Proxmox management network
VLAN 10 = management / core services path
```

## Evidence

- Completed VLAN table
- Output proving the endpoint subnet
- Explanation of why VLAN 60 and VLAN 70 are separated

## ARIA Mentor Questions

- What is a VLAN?
- What is a subnet?
- How do you know which VLAN your endpoint is using?
- Why should lab workloads be separated from Proxmox management?
- What happens if the gateway is wrong?

---

# Lab 003 - Trunk vs Access Port Troubleshooting

## Objective

Teach students the difference between access ports and trunk ports using the ARIA Cisco/Proxmox design.

## Skills Taught

- Access port behavior
- Trunk port behavior
- Untagged endpoint traffic
- VLAN tagging
- Proxmox bridge behavior
- Why VLAN 60 VM NICs should not be tagged on vmbr1

## Scenario

A student VM cannot reach the VLAN 60 gateway because the VM NIC or bridge path is misconfigured.

Students must determine whether the issue is:

```text
Wrong Proxmox bridge
Wrong VLAN tag on VM NIC
Wrong switchport mode
Wrong access VLAN
Gateway unreachable
DNS unrelated to the actual problem
```

## Evidence Commands

Proxmox host:

```bash
ip link show
bridge link
cat /etc/network/interfaces
```

Cisco switch:

```text
show interfaces status
show vlan brief
show interfaces switchport
show running-config interface gi0/6
```

Windows/Linux endpoint:

```text
ipconfig /all
ip addr
ping gateway
```

## Evidence

- Screenshot/output of correct bridge
- Screenshot/output of switchport VLAN
- Successful ping to VLAN 60 gateway after correction
- Written explanation of access vs trunk

## ARIA Mentor Questions

- Is this port supposed to carry one VLAN or multiple VLANs?
- Is the endpoint sending tagged or untagged traffic?
- Which Proxmox bridge is connected to VLAN 60?
- Why should the VM NIC not have a VLAN tag on vmbr1?
- What command proves the switchport mode?

---

# Lab 004 - DNS and DHCP Troubleshooting

## Objective

Teach students how to troubleshoot name resolution and address assignment separately.

## Skills Taught

- DHCP lease review
- DNS server identification
- DNS query testing
- Gateway vs DNS troubleshooting
- Pi-hole role in DNS
- Domain DNS vs internet DNS

## Scenario

A workstation has internet by IP but cannot browse by name or resolve internal records.

Students must determine whether the issue is:

```text
No DHCP lease
Wrong DNS server
Gateway failure
Pi-hole/DNS failure
Domain DNS issue
Client cache issue
```

## Commands

Windows:

```cmd
ipconfig /all
ipconfig /release
ipconfig /renew
ipconfig /flushdns
nslookup google.com
nslookup jlm.lab
ping 1.1.1.1
ping google.com
```

Linux:

```bash
ip addr
ip route
resolvectl status
resolvectl query google.com
resolvectl query jlm.lab
ping -c 4 1.1.1.1
ping -c 4 google.com
```

## Evidence

- DHCP lease details
- DNS server details
- Successful external lookup
- Successful internal lookup
- Written explanation of what failed and what fixed it

## ARIA Mentor Questions

- Do you have an IP address?
- Do you have a default gateway?
- Can you ping by IP?
- Can you resolve names?
- What DNS server are you using?
- Is this a DHCP problem or a DNS problem?

---

# Lab 005 - Inter-VLAN ACL Verification

## Objective

Teach students how to verify segmentation and explain why some traffic is allowed while other traffic is blocked.

## Skills Taught

- Inter-VLAN routing
- ACL purpose
- Allowed vs denied traffic
- Testing reachability safely
- Documenting segmentation behavior
- Avoiding assumptions from a single failed ping

## Scenario

Students test whether VLANs can reach each other and explain expected behavior.

Examples:

```text
LAB VLAN should reach required services only.
IoT VLAN should not freely reach internal server networks.
Guest VLAN should have internet/DNS but no internal access.
Management VLAN should remain protected.
```

## Commands

Endpoint:

```cmd
ping <gateway>
ping <allowed-service>
ping <blocked-internal-host>
tracert <destination>
nslookup <name>
```

Cisco:

```text
show access-lists
show ip interface vlan 60
show ip route
show ip ospf neighbor
```

## Evidence

- Successful allowed test
- Failed blocked test
- ACL output or screenshot
- Written explanation of segmentation result

## ARIA Mentor Questions

- Is the traffic supposed to be allowed?
- Which VLAN are you testing from?
- Which VLAN are you testing to?
- Is DNS allowed even when other traffic is blocked?
- What does the ACL say?
- What test proves the rule?

---

# Lab 006 - Switch Security Basics

## Objective

Teach students how common Layer 2 security controls protect enterprise access networks.

## Controls Covered

```text
PortFast
BPDU Guard
DHCP Snooping
Dynamic ARP Inspection
IP Source Guard
```

## Skills Taught

- Why access ports use PortFast
- Why BPDU Guard protects against accidental switch loops
- Why DHCP Snooping blocks rogue DHCP servers
- Why Dynamic ARP Inspection protects ARP integrity
- Why IP Source Guard limits spoofing
- How to validate switch security posture

## Cisco Evidence Commands

```text
show spanning-tree summary
show spanning-tree interface gi0/6 detail
show running-config interface gi0/6
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection vlan 60
show ip verify source
```

## Evidence

- Screenshot/output of switch security configuration
- Explanation of each control
- Student describes what risk each feature reduces
- Optional safe failure demonstration in a controlled lab window

## ARIA Mentor Questions

- Why should PortFast only be used on access ports?
- What does BPDU Guard protect against?
- What problem does DHCP Snooping solve?
- What does Dynamic ARP Inspection verify?
- What does IP Source Guard prevent?
- Which command proves the feature is active?

---

# Student Evidence Standard

Every Networking/Cisco lab should require:

```text
1. The command used
2. The output observed
3. A short explanation in plain English
4. A conclusion: pass, fail, or needs escalation
5. A ticket-style or lab-summary note
```

## Required Evidence Types

```text
Network configuration evidence
Connectivity test evidence
DNS/DHCP evidence
Cisco command evidence
Failure/success comparison
Written troubleshooting explanation
```

## ARIA Mentor Standard

ARIA should not give students the final answer immediately.

ARIA should guide with questions:

```text
What layer are you troubleshooting?
What changed?
What still works?
What fails?
What command proves the failure?
What command proves the fix?
Is this IP, DNS, DHCP, VLAN, routing, or ACL related?
What would you document in the ticket?
```

## Build Order

Recommended implementation order:

```text
1. Create Lab 001 markdown and validate with current environment.
2. Build Lab 001 student evidence checklist.
3. Add ARIA AI Mentor prompts for Lab 001.
4. Commit and push Lab 001.
5. Repeat for Labs 002-006.
6. Do not begin Security/SOC until Networking v1 is documented and stable.
```

## Completion Criteria for Networking v1

Networking/Cisco foundational v1 is complete when:

```text
[x] Six student-facing labs exist
[x] Each lab includes objective, commands, evidence, troubleshooting, and ARIA Mentor questions
[x] At least one lab has been validated end to end against the live ARIA network
[x] Documentation is committed and pushed
[x] ROADMAP.md reflects Networking as Complete v1 or Foundational v1 complete
```

## Next Action

Begin with:

```text
Networking/Cisco Lab 001 - Network Baseline and Device Discovery
```

This lab should be documentation-first and low-risk because it uses read-only discovery commands and does not change network configuration.
