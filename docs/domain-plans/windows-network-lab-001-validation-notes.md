# Windows Network Lab 001 - Validation Notes

Status: Validated with DNS finding  
Domain: Networking / Windows Endpoint Network Troubleshooting / DNS / DHCP / Reachability  
Lab: Windows Network Lab 001 - Endpoint Baseline and Reachability  
Validation Endpoint: JLM-WIN01  
Validation User: JLM\student01  
Validation Network: VLAN 60 LAB / 192.168.60.0/24  

## Validation Summary

Windows Network Lab 001 was validated from JLM-WIN01 while logged in as JLM\student01.

The lab successfully proves that the Windows endpoint has valid IP configuration, can reach its local gateway, can reach the domain controller/DNS server by IP, and can reach the public internet by IP.

The lab also exposed a real DNS finding: DNS lookups through 192.168.60.10 are delayed or failing, especially for public names such as google.com.

This is a valid training result and should be preserved as evidence because it teaches students how to separate IP reachability from DNS resolution.

## Endpoint Identity Evidence

Observed:

```text
Hostname: JLM-WIN01
User context: JLM\student01
Primary DNS suffix: jlm.lab
DNS suffix search list: jlm.lab
```

Interpretation:

```text
The student is logged into the expected Windows endpoint using the expected domain user context.
The endpoint is domain-associated with jlm.lab.
```

## IP Configuration Evidence

Observed from `ipconfig /all`:

```text
Adapter: Ethernet
Description: Intel(R) PRO/1000 MT Network Connection
Physical Address: BC-24-11-75-89-B1
DHCP Enabled: Yes
Autoconfiguration Enabled: Yes
IPv4 Address: 192.168.60.14 (Preferred)
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.60.1
DHCP Server: 192.168.60.1
DNS Server: 192.168.60.10
NetBIOS over Tcpip: Enabled
```

Interpretation:

```text
JLM-WIN01 received a valid DHCP address on 192.168.60.0/24.
The endpoint is correctly placed on the VLAN 60 LAB network.
The default gateway is 192.168.60.1.
The configured DNS server is 192.168.60.10.
```

## Reachability Evidence

Observed from endpoint testing:

```text
ping 192.168.60.1: Passed
ping 192.168.60.10: Passed
ping 1.1.1.1: Passed
ping 8.8.8.8: Passed
```

Interpretation:

```text
The endpoint can reach its local default gateway.
The endpoint can reach the domain controller/DNS server by IP.
The endpoint can reach public internet IP addresses.
This is not a general network outage.
```

## Traceroute Evidence

Observed from `tracert 1.1.1.1`:

```text
Hop 1: 192.168.60.1
Hop 2: 192.168.199.1
Final destination: 1.1.1.1
Trace complete.
```

One intermediate hop timed out, but the trace completed successfully.

Interpretation:

```text
Hop 1 confirms the endpoint is using 192.168.60.1 as its local gateway.
Hop 2 confirms the upstream transit path.
The completed trace confirms working IP routing from VLAN 60 to the public internet.
An intermediate timeout does not mean the route failed when the final destination is reached.
```

## DNS Evidence

Observed from `nslookup jlm.lab`:

```text
DNS request timed out.
timeout was 2 seconds.
Server: Unknown
Address: 192.168.60.10

Name: jlm.lab
Address: 192.168.60.10
```

Interpretation:

```text
The internal domain name eventually resolved to 192.168.60.10, but the response was delayed enough to produce a timeout first.
The DNS server is reachable by IP, but DNS response behavior needs review.
```

Observed from `nslookup google.com`:

```text
DNS request timed out.
timeout was 2 seconds.
Server: Unknown
Address: 192.168.60.10

*** Request to Unknown timed-out
```

Interpretation:

```text
Public DNS resolution through 192.168.60.10 failed during validation.
Because public IP pings and traceroute succeeded, this points to a DNS resolution or forwarding issue rather than a general routing/internet outage.
```

Observed from `Resolve-DnsName google.com -Server 1.1.1.1`:

```text
google.com returned public A and AAAA records.
```

Observed from `Test-NetConnection 8.8.8.8 -Port 53` and `Test-NetConnection 1.1.1.1 -Port 53`:

```text
TcpTestSucceeded: True
```

Interpretation:

```text
The Windows endpoint can reach external DNS servers on TCP port 53.
External DNS resolution works when querying 1.1.1.1 directly.
The failure is specific to DNS resolution through the configured DNS server path, 192.168.60.10.
```

## Incorrect Command Context Finding

The following commands were attempted from JLM-WIN01:

```powershell
Get-DnsServerForwarder
Get-DnsServerRootHint
```

Result:

```text
CommandNotFoundException
```

Interpretation:

```text
This is expected on a standard Windows client because these are DNS Server role cmdlets.
They should be run on JLM-DC01 or from an admin workstation with the appropriate RSAT/DNS Server tools installed.
This is a useful student lesson: run server-role diagnostic commands from the correct system/context.
```

## Validation Conclusion

Final status:

```text
Windows Network Lab 001: VALIDATED WITH DNS FINDING
```

Validated outcomes:

```text
[x] Endpoint identity confirmed
[x] Domain user context confirmed
[x] DHCP address confirmed
[x] VLAN 60 subnet confirmed
[x] Default gateway confirmed
[x] DNS server assignment confirmed
[x] Gateway reachability passed
[x] Domain controller/DNS server IP reachability passed
[x] Public internet reachability by IP passed
[x] Traceroute completed successfully
[x] DNS issue identified and documented
```

Known finding:

```text
DNS lookups through 192.168.60.10 are delayed or failing.
Internal lookup for jlm.lab resolves after an initial timeout.
Public lookup for google.com times out through 192.168.60.10.
Direct external DNS query to 1.1.1.1 works.
TCP/53 connectivity to 8.8.8.8 and 1.1.1.1 succeeds.
```

## Ticket-Style Validation Note

```text
Validated Windows Network Lab 001 from JLM-WIN01 as JLM\student01. The endpoint received DHCP address 192.168.60.14/24 with default gateway 192.168.60.1, DHCP server 192.168.60.1, and DNS server 192.168.60.10. Gateway reachability passed. Domain controller/DNS server reachability by IP passed. Public internet reachability by IP passed using 1.1.1.1 and 8.8.8.8. Traceroute to 1.1.1.1 completed successfully with first hop 192.168.60.1 and second hop 192.168.199.1. DNS lookup for jlm.lab returned 192.168.60.10 after an initial timeout, while DNS lookup for google.com timed out against 192.168.60.10. Direct query to 1.1.1.1 resolves google.com and TCP/53 to 1.1.1.1 and 8.8.8.8 succeeds. Conclusion: endpoint IP configuration and routing are working; configured DNS path through 192.168.60.10 requires follow-up review.
```

## Next Recommended Diagnostic Step

Before treating DNS as resolved, run the DNS server checks from JLM-DC01, not from JLM-WIN01:

```powershell
hostname
ipconfig /all
nslookup jlm.lab
nslookup google.com
nslookup google.com 127.0.0.1
Get-DnsServerForwarder
Get-DnsServerRootHint | Select-Object -First 5
Test-NetConnection 8.8.8.8 -Port 53
Test-NetConnection 1.1.1.1 -Port 53
```

If `Get-DnsServerForwarder` or `Get-DnsServerRootHint` is unavailable on JLM-DC01, confirm that the DNS Server PowerShell module is installed and that the shell is running with administrative permissions.

## Impact on Lab Sequence

Lab 001 can be closed as validated with a documented DNS finding.

The DNS finding should carry forward into:

```text
Windows Network Lab 003 - DNS Failure vs Routing Failure
Windows Network Lab 005 - Domain/DNS Path Validation for jlm.lab
```

Lab 002 may proceed because the endpoint DHCP lease and IP configuration evidence are valid.
