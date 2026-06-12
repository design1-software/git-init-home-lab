# Windows Network Lab 001 - Endpoint Baseline and Reachability

Status: Draft for live validation  
Domain: Networking / Windows Endpoint Network Troubleshooting / DNS / DHCP / Reachability  
Training Block: Windows Network Foundational Block  
Lab Type: Hands-on Windows endpoint network discovery and evidence collection  
Risk Level: Low  
Target Endpoint: JLM-WIN01  
Target User: JLM\student01  
Target Network: VLAN 60 LAB / 192.168.60.0/24  
Cisco IOS Labs: Deferred until dedicated Cisco practice hardware is added  

## Lab Objective

Teach students how to collect a Windows endpoint network baseline and prove basic network reachability using real Windows commands.

This lab is hands-on. Students must run commands, collect evidence, interpret the results, and write a short ticket-style summary.

Students will learn how to answer:

```text
What computer am I on?
What user am I logged in as?
What IP address did the endpoint receive?
What subnet is the endpoint on?
What is the default gateway?
What is the DHCP server?
What is the DNS server?
Can the endpoint reach its gateway?
Can the endpoint reach the domain controller / DNS server?
Can the endpoint reach the internet by IP?
Does DNS resolution work?
What does the route path look like?
What evidence proves each answer?
```

## Why This Lab Matters

Network troubleshooting often starts at the endpoint.

A network engineer, help desk technician, field technician, sysadmin, or SOC analyst needs to know how to prove whether a problem is caused by:

```text
Endpoint configuration
DHCP
DNS
Default gateway
Routing
Firewall or ACL behavior
Domain controller reachability
Upstream internet path
```

This lab teaches students not to guess.

The professional habit is:

```text
Run the command.
Read the output.
Explain what it means.
Document the evidence.
```

## Scope

This lab focuses on Windows-side network troubleshooting only.

Cisco IOS labs are deferred until a dedicated Cisco practice environment is available.

Current future Cisco practice plan:

```text
Additional Cisco Catalyst 3560 switch
Three Raspberry Pi 3B+ devices
Dedicated safe Cisco practice VLANs and ports
Hands-on IOS configuration labs after hardware is ready
```

## Safety Guardrail

This lab does not change network configuration.

Students must not change:

```text
IP settings
DNS settings
DHCP settings
Firewall rules
Domain settings
Group Policy
Cisco switch/router configuration
Proxmox networking
```

Allowed actions:

```text
Run Windows network commands
Collect screenshots or copied output
Interpret results
Write a ticket-style summary
Ask ARIA Mentor for guided troubleshooting questions
```

## Current Lab Environment

Validated environment:

```text
Endpoint: JLM-WIN01
User: JLM\student01
Domain: jlm.lab
Network: VLAN 60 LAB
Subnet: 192.168.60.0/24
Default gateway: 192.168.60.1
DHCP server: 192.168.60.1
DNS server: 192.168.60.10
Domain controller / DNS server: JLM-DC01 / 192.168.60.10
```

Expected baseline pattern:

```text
JLM-WIN01 receives a 192.168.60.x address.
The default gateway is 192.168.60.1.
The DHCP server is 192.168.60.1.
The DNS server is 192.168.60.10.
The endpoint can ping 192.168.60.1.
The endpoint can ping 192.168.60.10.
The endpoint can ping public IPs such as 1.1.1.1 and 8.8.8.8.
tracert to 1.1.1.1 should show 192.168.60.1 as the first hop.
```

During initial validation, DNS lookup to `192.168.60.10` timed out. That should be treated as a real troubleshooting observation, not ignored.

## Student Role

In this lab, the student acts as a junior network technician responding to a basic connectivity ticket.

Example ticket:

```text
User reports: The computer is connected, but I need you to verify whether the network is working correctly.
```

The student must collect evidence before escalating or declaring the issue resolved.

## Required Tools

Use Windows PowerShell or Command Prompt.

Required commands:

```cmd
hostname
whoami
ipconfig /all
ping 192.168.60.1
ping 192.168.60.10
ping 1.1.1.1
ping 8.8.8.8
nslookup jlm.lab
nslookup google.com
tracert 1.1.1.1
```

Optional additional commands:

```cmd
route print
ipconfig /displaydns
Get-NetIPConfiguration
Get-DnsClientServerAddress
Resolve-DnsName google.com
Resolve-DnsName jlm.lab
```

## Part 1 - Identify the Computer and User

Open PowerShell on JLM-WIN01.

Run:

```cmd
hostname
whoami
```

Expected example:

```text
hostname
JLM-WIN01

whoami
jlm\student01
```

Record:

```text
Computer name:
Logged-in user:
Domain or local account:
```

### Student Interpretation

The student should explain:

```text
I am logged into the expected Windows endpoint as the expected domain user.
```

If the user is not `JLM\student01`, the student should document the actual user and notify the instructor.

## Part 2 - Collect IP Configuration

Run:

```cmd
ipconfig /all
```

Record these fields:

```text
Host Name:
Primary DNS Suffix:
DNS Suffix Search List:
Adapter name:
Description:
Physical Address:
DHCP Enabled:
IPv4 Address:
Subnet Mask:
Default Gateway:
DHCP Server:
DNS Servers:
NetBIOS over Tcpip:
Lease Obtained:
Lease Expires:
```

Expected example:

```text
Host Name: JLM-WIN01
Primary DNS Suffix: jlm.lab
DNS Suffix Search List: jlm.lab
IPv4 Address: 192.168.60.x
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.60.1
DHCP Server: 192.168.60.1
DNS Servers: 192.168.60.10
```

### Student Interpretation

The student should answer:

```text
Is DHCP enabled?
What IP address did the computer receive?
What subnet is it on?
What is the default gateway?
What DNS server is assigned?
Does the DNS suffix match the domain?
```

## Part 3 - Identify the Likely VLAN or Network

Use the IP address from `ipconfig /all`.

Known baseline:

```text
192.168.60.0/24 = VLAN 60 LAB
192.168.70.0/24 = VLAN 70 SERVER / ARIA management
```

Student answer format:

```text
My endpoint IP address is: __________
My subnet mask is: __________
My likely network is: __________
My evidence is: __________
```

Expected for JLM-WIN01:

```text
JLM-WIN01 is on 192.168.60.0/24, which is the VLAN 60 LAB network.
```

## Part 4 - Test the Default Gateway

Run:

```cmd
ping 192.168.60.1
```

Expected successful result:

```text
Reply from 192.168.60.1: bytes=32 time<1ms TTL=255
Reply from 192.168.60.1: bytes=32 time<1ms TTL=255
Reply from 192.168.60.1: bytes=32 time<1ms TTL=255
Reply from 192.168.60.1: bytes=32 time<1ms TTL=255

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

### Student Interpretation

If this passes:

```text
The endpoint can reach its local default gateway.
The local subnet and gateway path are working.
```

If this fails:

```text
Do not troubleshoot DNS first.
A gateway failure points to local IP configuration, VLAN placement, adapter state, switchport, gateway, or firewall/ICMP behavior.
```

## Part 5 - Test Domain Controller / DNS Server Reachability

Run:

```cmd
ping 192.168.60.10
```

Expected successful result:

```text
Reply from 192.168.60.10: bytes=32 time<1ms TTL=128
Reply from 192.168.60.10: bytes=32 time<1ms TTL=128
Reply from 192.168.60.10: bytes=32 time<1ms TTL=128
Reply from 192.168.60.10: bytes=32 time<1ms TTL=128

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

### Student Interpretation

If this passes:

```text
The endpoint can reach JLM-DC01 by IP.
The domain controller / DNS server is reachable at the IP layer.
```

If this fails:

```text
The endpoint may have an internal reachability issue, firewall issue, host issue, or segmentation issue.
A failed ping does not automatically prove DNS is broken.
```

## Part 6 - Test Internet Reachability by IP

Run:

```cmd
ping 1.1.1.1
ping 8.8.8.8
```

Expected successful result for `1.1.1.1`:

```text
Reply from 1.1.1.1: bytes=32 time=17ms TTL=54
Reply from 1.1.1.1: bytes=32 time=21ms TTL=54
Reply from 1.1.1.1: bytes=32 time=17ms TTL=54
Reply from 1.1.1.1: bytes=32 time=22ms TTL=54

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

Expected successful result for `8.8.8.8`:

```text
Reply from 8.8.8.8: bytes=32 time=20ms TTL=114
Reply from 8.8.8.8: bytes=32 time=19ms TTL=114
Reply from 8.8.8.8: bytes=32 time=19ms TTL=114
Reply from 8.8.8.8: bytes=32 time=16ms TTL=114

Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

### Student Interpretation

If public IP pings pass:

```text
The endpoint has internet reachability by IP.
Routing/NAT/upstream path is working enough to reach public IPs.
```

If public IP pings fail but the gateway ping works:

```text
The issue may be routing, NAT, ACL, upstream edge, ISP, or firewall policy.
```

## Part 7 - Test DNS Resolution

Run:

```cmd
nslookup jlm.lab
nslookup google.com
```

Record:

```text
DNS server queried:
Internal domain result:
Public domain result:
Any timeout or failure messages:
```

Possible failure example from validation:

```text
DNS request timed out.
timeout was 2 seconds.
Server: Unknown
Address: 192.168.60.10

*** Request to Unknown timed-out
```

### Student Interpretation

If `ping 1.1.1.1` and `ping 8.8.8.8` work, but `nslookup google.com` fails:

```text
This is not a general internet outage.
The endpoint has internet by IP.
The symptom points toward DNS resolution.
```

If `nslookup jlm.lab` fails:

```text
Internal domain DNS may need review.
This can affect domain services, Group Policy, domain controller discovery, and authentication workflows.
```

Do not write:

```text
The internet is down.
```

Write:

```text
Internet by IP works, but DNS lookup timed out against 192.168.60.10.
```

## Part 8 - Trace the Route to the Internet

Run:

```cmd
tracert 1.1.1.1
```

Expected pattern:

```text
Tracing route to 1.1.1.1 over a maximum of 30 hops

1    <1 ms    <1 ms    <1 ms    192.168.60.1
2    <1 ms    <1 ms    <1 ms    192.168.199.1
3    ... ISP / upstream path ...
...
Final hop: 1.1.1.1

Trace complete.
```

### Student Interpretation

The student should explain:

```text
Hop 1 is the local VLAN 60 gateway.
Hop 2 is the upstream transit path toward the edge router.
Later hops belong to the ISP / internet path.
A timeout on one intermediate hop does not always mean the trace failed.
The trace is successful if it reaches the final destination.
```

If one intermediate hop times out but the final destination replies, write:

```text
One intermediate hop did not respond to traceroute, but the route completed successfully to 1.1.1.1.
```

## Part 9 - Optional Route Table Review

Run:

```cmd
route print
```

Or in PowerShell:

```powershell
Get-NetRoute
```

Identify the default route:

```text
0.0.0.0/0 via 192.168.60.1
```

### Student Interpretation

The default route tells Windows where to send traffic that is not local.

For JLM-WIN01, the expected default gateway is:

```text
192.168.60.1
```

## Part 10 - Optional PowerShell Network Cmdlets

Run:

```powershell
Get-NetIPConfiguration
Get-DnsClientServerAddress
Resolve-DnsName google.com
Resolve-DnsName jlm.lab
```

These commands provide a PowerShell-based way to validate the same information.

Students should understand that PowerShell is useful for:

```text
Automation
Repeatable evidence collection
Remote support
Scripting
Escalation reports
```

## Results Table

Students must complete this table.

| Test | Command | Pass/Fail | Evidence | What It Proves |
|---|---|---|---|---|
| Identify computer | `hostname` |  |  | Confirms endpoint name |
| Identify user | `whoami` |  |  | Confirms logged-in identity |
| IP configuration | `ipconfig /all` |  |  | Shows IP, gateway, DHCP, DNS |
| Gateway reachability | `ping 192.168.60.1` |  |  | Local gateway path |
| DC/DNS reachability | `ping 192.168.60.10` |  |  | Internal server reachability by IP |
| Internet by IP | `ping 1.1.1.1` |  |  | Public IP reachability |
| Internet by IP | `ping 8.8.8.8` |  |  | Public IP reachability |
| Internal DNS | `nslookup jlm.lab` |  |  | Domain DNS resolution |
| Public DNS | `nslookup google.com` |  |  | Public DNS resolution |
| Route path | `tracert 1.1.1.1` |  |  | First hop and upstream path |

## Required Evidence Checklist

Submit:

```text
[ ] hostname output
[ ] whoami output
[ ] ipconfig /all output
[ ] ping 192.168.60.1 output
[ ] ping 192.168.60.10 output
[ ] ping 1.1.1.1 output
[ ] ping 8.8.8.8 output
[ ] nslookup jlm.lab output
[ ] nslookup google.com output
[ ] tracert 1.1.1.1 output
[ ] Completed results table
[ ] Written student summary
[ ] Ticket-style escalation note if any test fails
```

## Student Summary Template

Students should complete this summary:

```text
I tested from endpoint: __________
I was logged in as: __________
The computer IP address is: __________
The subnet mask is: __________
The default gateway is: __________
The DHCP server is: __________
The DNS server is: __________
The likely network/VLAN is: __________

Gateway reachability: Pass / Fail
Domain controller reachability by IP: Pass / Fail
Internet reachability by IP: Pass / Fail
Internal DNS lookup: Pass / Fail
Public DNS lookup: Pass / Fail
Traceroute completed: Pass / Fail

My conclusion:
__________

The evidence that supports my conclusion is:
__________

If this needed escalation, I would tell the next technician:
__________
```

## Ticket-Style Note Examples

### Healthy Baseline Example

```text
Validated JLM-WIN01 network baseline as JLM\student01. The endpoint received a 192.168.60.x address with gateway 192.168.60.1 and DNS server 192.168.60.10. Gateway, domain controller, and public IP reachability tests passed. Traceroute to 1.1.1.1 completed with 192.168.60.1 as the first hop. No endpoint-side reachability issue identified during baseline testing.
```

### DNS Failure Example

```text
Validated JLM-WIN01 network baseline as JLM\student01. The endpoint received a valid 192.168.60.x address and can reach the gateway 192.168.60.1, domain controller 192.168.60.10, and public IPs 1.1.1.1 / 8.8.8.8. However, nslookup to google.com timed out against DNS server 192.168.60.10. Internet by IP works, so this does not appear to be a general connectivity outage. Evidence points to a DNS resolution issue requiring DNS/domain review.
```

### Gateway Failure Example

```text
JLM-WIN01 has IP configuration but cannot ping the default gateway 192.168.60.1. Since the gateway is unreachable, DNS and internet tests may fail as a secondary symptom. Recommend checking endpoint IP configuration, VLAN placement, adapter status, switchport path, or gateway availability.
```

## Troubleshooting Decision Tree

Use this logic:

```text
No IPv4 address?
  -> Check adapter state, DHCP, or APIPA.

IPv4 address starts with 169.254?
  -> APIPA. DHCP likely failed.

No default gateway?
  -> DHCP option or static configuration issue.

Cannot ping default gateway?
  -> Local subnet/VLAN/gateway path problem. Do not start with DNS.

Can ping gateway but cannot ping 192.168.60.10?
  -> Internal host, firewall, ACL, or routing/segmentation issue.

Can ping gateway and 192.168.60.10 but cannot ping 1.1.1.1?
  -> Upstream routing, NAT, ACL, or internet path issue.

Can ping 1.1.1.1 and 8.8.8.8 but nslookup fails?
  -> DNS resolution issue.

tracert has one timed-out intermediate hop but reaches final destination?
  -> Not necessarily a failure. Some routers do not answer traceroute probes.

Everything works?
  -> Document a healthy baseline.
```

## ARIA AI Mentor Role

ARIA should coach students through evidence.

ARIA should not simply give the answer.

Example mentor questions:

```text
What is the endpoint hostname?
What account are you logged in with?
What IPv4 address did the endpoint receive?
Is DHCP enabled?
What is the default gateway?
What DNS server is configured?
Can you ping the default gateway?
Can you ping the DNS server by IP?
Can you ping a public IP?
Can you resolve a public hostname?
Can you resolve the internal domain?
Which command proves this is DNS-related?
Which command proves this is routing-related?
What would you write in the ticket note?
```

## Instructor Validation

The instructor should confirm:

```text
[ ] Student ran all required commands
[ ] Student identified hostname and user
[ ] Student identified IP address, subnet, gateway, DHCP server, and DNS server
[ ] Student tested gateway reachability
[ ] Student tested domain controller / DNS server reachability by IP
[ ] Student tested internet by IP
[ ] Student tested internal DNS
[ ] Student tested public DNS
[ ] Student interpreted traceroute correctly
[ ] Student completed the results table
[ ] Student wrote a clear summary
[ ] Student avoided unsupported claims such as "the internet is down" when IP reachability works
```

## Completion Criteria

This lab is complete when the student can explain:

```text
What endpoint they tested
What IP configuration it has
Whether the default gateway works
Whether the domain controller / DNS server is reachable by IP
Whether internet by IP works
Whether DNS resolution works
What the traceroute path shows
What evidence supports their conclusion
```

## Key Lesson

The key lesson of this lab is:

```text
A good network technician separates IP reachability from DNS resolution and documents evidence before escalating.
```

## Lab Status Checklist

```text
[ ] Built in documentation
[ ] Pulled into local repo
[ ] KB rebuilt
[ ] Validated on JLM-WIN01
[ ] Evidence reviewed
[ ] Marked validated after successful run
```

## Next Lab

Next planned lab:

```text
Windows Network Lab 002 - DHCP Lease and IP Configuration Troubleshooting
```
