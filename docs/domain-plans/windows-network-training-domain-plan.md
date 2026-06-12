# Windows Network Training Domain Plan

Status: Active training domain plan  
Domain: Networking / Windows Endpoint Network Troubleshooting / DNS / DHCP / Reachability  
Platform: ARIA IT Enterprise Training Platform  
Current Position: Identity/IAM foundational v1 complete; Windows Network labs are active; Cisco IOS hands-on labs are deferred until dedicated Cisco practice hardware is added  

## Purpose

This document defines the active Windows Network training path for ARIA.

The goal is to give students hands-on practice troubleshooting networking from a Windows endpoint before moving into dedicated Cisco IOS configuration labs.

This is not a paper-only plan. Students must run commands, collect evidence, interpret failures, and write ticket-style summaries.

## Decision: Cisco Labs Deferred

Cisco IOS labs are intentionally deferred for now.

Reason:

```text
The current Cisco 3560CX and C1111 are part of the live ARIA/production lab network.
Students need hands-on Cisco IOS configuration practice, but that practice should not risk the active network.
```

Future Cisco hands-on practice will use a separate Cisco practice lane after additional hardware is purchased:

```text
Planned hardware:
- Additional Cisco Catalyst 3560 switch
- Three Raspberry Pi 3B+ devices
```

The future Cisco practice environment should support safe VLAN, trunk, access-port, DHCP, DNS, routing, switch security, and break/fix practice without risking the live production/ARIA network.

## Current Active Focus

The active focus is now:

```text
Windows endpoint network troubleshooting
DNS troubleshooting
DHCP lease review
Gateway/reachability testing
Traceroute path interpretation
Domain/DNS path validation
Ticket-style escalation evidence
```

This still supports the Networking / Cisco / DNS / VLAN / Switching domain because network engineers must understand both endpoint-side evidence and infrastructure-side evidence.

## Why Windows Network Labs Matter

Network engineers, help desk technicians, field techs, sysadmins, and SOC analysts all need to know how to prove whether a problem is local to the endpoint, DNS-related, DHCP-related, gateway-related, routing-related, or service-related.

Windows endpoint evidence often determines whether a ticket should remain with help desk or escalate to network engineering.

Students need repeated practice with:

```text
ipconfig
ping
tracert
nslookup
route print
netsh
PowerShell networking cmdlets
Event Viewer
Windows Firewall checks
Domain reachability checks
DNS cache checks
DHCP renewal tests
```

## Active Windows Network Lab Block

The Windows Network foundational block will include six labs:

```text
Lab 001 - Endpoint Baseline and Reachability
Lab 002 - DHCP Lease and IP Configuration Troubleshooting
Lab 003 - DNS Failure vs Routing Failure
Lab 004 - Traceroute and Gateway Path Interpretation
Lab 005 - Domain/DNS Path Validation for jlm.lab
Lab 006 - Windows Network Ticket Escalation Evidence
```

Each lab should be:

```text
Hands-on
Evidence-driven
Beginner-accessible
Ticket-oriented
Validated on the live ARIA Windows endpoint environment
Documented before moving to the next lab
Committed and pushed before moving to the next lab
```

## Current Windows Endpoint Environment

Current validated Windows network endpoint:

```text
Endpoint: JLM-WIN01
User: JLM\student01
Domain: jlm.lab
Likely VLAN/subnet: VLAN 60 LAB / 192.168.60.0/24
Default gateway: 192.168.60.1
DHCP server: 192.168.60.1
DNS server: 192.168.60.10
Domain controller / DNS server: JLM-DC01 / 192.168.60.10
```

Validated baseline observations:

```text
JLM-WIN01 received a DHCP lease on 192.168.60.0/24
Gateway 192.168.60.1 replies
Domain controller/DNS server 192.168.60.10 replies
Internet by IP works using 1.1.1.1 and 8.8.8.8
tracert to 1.1.1.1 shows first hop as 192.168.60.1
tracert to 1.1.1.1 shows second hop as 192.168.199.1
DNS lookup to 192.168.60.10 timed out during initial validation and should be treated as a troubleshooting finding, not ignored
```

## Lab 001 - Endpoint Baseline and Reachability

### Objective

Teach students how to collect a Windows endpoint network baseline and prove basic reachability.

### Core Commands

```cmd
hostname
whoami
ipconfig /all
ping 192.168.60.1
ping 192.168.60.10
ping 1.1.1.1
ping 8.8.8.8
tracert 1.1.1.1
nslookup jlm.lab
nslookup google.com
```

### Skills Taught

```text
Identify endpoint identity
Identify logged-in user
Identify IP address
Identify subnet mask
Identify default gateway
Identify DHCP server
Identify DNS server
Test gateway reachability
Test domain controller reachability
Test internet by IP
Interpret traceroute first and second hop
Identify DNS timeout symptoms
Document results
```

### Evidence Required

```text
Screenshot or copied output for every command
Completed baseline table
Short written summary
Ticket-style note explaining whether this is healthy or needs escalation
```

## Lab 002 - DHCP Lease and IP Configuration Troubleshooting

### Objective

Teach students how to read DHCP lease details and identify incorrect or missing IP configuration.

### Core Commands

```cmd
ipconfig /all
ipconfig /release
ipconfig /renew
ipconfig /displaydns
route print
Get-NetIPConfiguration
Get-DnsClientServerAddress
```

### Skills Taught

```text
DHCP enabled vs static configuration
Lease obtained time
Lease expiration time
DHCP server identification
Default gateway validation
DNS server assignment
APIPA recognition
Difference between IP address, subnet mask, gateway, and DNS
```

## Lab 003 - DNS Failure vs Routing Failure

### Objective

Teach students how to determine whether a failure is DNS-related or routing/connectivity-related.

### Core Commands

```cmd
ping 1.1.1.1
ping 8.8.8.8
ping google.com
nslookup google.com
nslookup jlm.lab
ipconfig /flushdns
ipconfig /displaydns
Resolve-DnsName google.com
Resolve-DnsName jlm.lab
```

### Skills Taught

```text
Internet by IP vs internet by name
DNS timeout interpretation
Configured DNS server review
Internal domain DNS testing
Public DNS testing
Client DNS cache behavior
Escalation evidence for DNS issues
```

## Lab 004 - Traceroute and Gateway Path Interpretation

### Objective

Teach students how to interpret a route path from the endpoint to the internet.

### Core Commands

```cmd
tracert 1.1.1.1
tracert 8.8.8.8
ping 192.168.60.1
ping 192.168.199.1
route print
Get-NetRoute
```

### Skills Taught

```text
First hop = local default gateway
Second hop = upstream routed transit path
Timeouts inside traceroute are not always failures
Final destination reachability matters
Route table interpretation
Default route identification
```

## Lab 005 - Domain/DNS Path Validation for jlm.lab

### Objective

Teach students how Windows domain membership depends on DNS and domain controller reachability.

### Core Commands

```cmd
whoami
hostname
ipconfig /all
nslookup jlm.lab
nslookup JLM-DC01.jlm.lab
nltest /dsgetdc:jlm.lab
gpresult /r
ping 192.168.60.10
```

### Skills Taught

```text
Domain identity
DNS suffix review
Domain controller discovery
Group Policy dependency on domain/DNS reachability
Difference between pinging a DC and discovering a DC
Escalation evidence for domain connectivity issues
```

## Lab 006 - Windows Network Ticket Escalation Evidence

### Objective

Teach students how to collect and organize network evidence for a professional ticket escalation.

### Core Evidence Bundle

```text
hostname
whoami
ipconfig /all
route print
ping gateway
ping DNS server
ping public IP
nslookup internal domain
nslookup public domain
tracert public IP
nltest /dsgetdc:jlm.lab when domain-related
Short summary of pass/fail findings
Recommended escalation path
```

### Skills Taught

```text
Evidence collection
Differentiating DNS, DHCP, routing, gateway, and domain symptoms
Writing clear escalation notes
Avoiding vague statements like "internet is down"
Explaining what works and what fails
```

## ARIA AI Mentor Standard

ARIA should guide students with questions, not simply provide answers.

Example mentor questions:

```text
What is your IP address?
What subnet are you on?
What is your default gateway?
Can you ping your gateway?
Can you ping by IP?
Can you resolve names?
Which test proves this is DNS and not routing?
Which test proves this is routing and not DNS?
What would you include in a ticket escalation note?
```

## Evidence Standard

Every Windows Network lab must require:

```text
1. Command used
2. Output observed
3. Student interpretation
4. Pass/fail conclusion
5. Ticket-style summary
```

## Completion Criteria for Windows Network Foundational Block

The Windows Network foundational block is complete when:

```text
[x] Six Windows Network labs exist
[x] Each lab is hands-on and evidence-driven
[x] Each lab has ARIA Mentor coaching questions
[x] Each lab has a student summary template
[x] Each lab is validated against JLM-WIN01 or another approved Windows endpoint
[x] Documentation is committed and pushed
[x] KB is rebuilt after documentation updates
```

## Future Cisco IOS Lab Roadmap

Cisco IOS labs are deferred, not abandoned.

Future Cisco IOS training will resume after the dedicated Cisco practice hardware is available.

Planned Cisco lab environment:

```text
Additional Cisco Catalyst 3560 switch
Three Raspberry Pi 3B+ devices
Dedicated practice VLANs
Dedicated access ports
Dedicated trunking practice path
Safe reset/rollback procedures
```

Future Cisco lab topics:

```text
Cisco IOS login and navigation
VLAN creation
Access port configuration
Trunk configuration
SVI creation
Inter-VLAN routing concepts
DHCP relay/DHCP troubleshooting
PortFast and BPDU Guard
DHCP Snooping
Dynamic ARP Inspection
IP Source Guard
ACL basics
Break/fix switching scenarios
```
