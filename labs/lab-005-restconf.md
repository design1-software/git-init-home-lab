# Lab: RESTCONF — REST API Programmability on Cisco IOS XE
# lab-005-restconf.md
# JLM Home Lab — git-init-home-lab
# Completed: May 21, 2026

---

## Overview

This lab documents the implementation of RESTCONF on the JLM home lab
C1111 router (IOS XE 16.10) and demonstrates programmatic access to
network device configuration and operational data via REST API calls
using Python.

**CCNA domains covered:**
- Domain 6 — Automation & Programmability (REST API, JSON, YANG)
- Domain 5 — Security Fundamentals (API attack surface, access control)

**Devices:**
- Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10, 192.168.10.1

---

## Part 1 — What RESTCONF Is

### Definition

RESTCONF (RFC 8040) is a protocol that exposes network device configuration
and operational data as a REST API over HTTPS. It uses:

- **HTTP methods** — GET, POST, PUT, PATCH, DELETE
- **YANG data models** — define the structure of the data
- **JSON or XML** — data format for requests and responses
- **HTTPS** — transport (port 443)

### RESTCONF vs CLI vs NETCONF

| Method | Transport | Data Format | Use Case |
|---|---|---|---|
| CLI | SSH/Telnet | Human text | Manual configuration |
| NETCONF | SSH port 830 | XML only | Programmatic config management |
| RESTCONF | HTTPS port 443 | JSON or XML | REST API automation |
| gNMI | gRPC | Protobuf | Streaming telemetry |

RESTCONF is the most approachable for developers — it uses standard HTTP
that any programming language can call natively.

### YANG Data Models

YANG (Yet Another Next Generation) is a data modeling language that defines
the structure of configuration and operational data. Every RESTCONF URL
maps to a YANG model path.

Example URL structure:
```
https://<device>/restconf/data/<yang-module>:<container>/<leaf>
```

Example from this lab:
```
https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname
```

Breaking this down:
- `restconf/data` — RESTCONF data store endpoint
- `Cisco-IOS-XE-native` — Cisco's native IOS XE YANG module
- `native` — top-level container
- `hostname` — the specific leaf node (device hostname)

---

## Part 2 — Configuration

### Prerequisites

- IOS XE 16.6 or later (RESTCONF was introduced in 16.3, stable in 16.6+)
- Local user with privilege level 15
- `ip http secure-server` enabled
- `restconf` command enabled

### C1111 Configuration

```
ip http secure-server
ip http authentication local
restconf
```

Verify:
```
show running-config | include http|restconf
```

Expected output:
```
restconf
ip http authentication local
ip http secure-server
ip http client source-interface GigabitEthernet0/0/0
```

### Security Note

Enabling HTTPS and RESTCONF exposes the router's full configuration
via API to anyone who can reach port 443. In this lab:

- `ip http server` (HTTP port 80) remains **disabled** — HTTPS only
- Authentication is local (admin privilege 15 required)
- Port 443 is accessible from any VLAN currently

**Hardening recommendation for production:**
Add an ACL restricting HTTPS access to management VLAN only:
```
ip access-list standard MGMT-ACCESS
 permit 192.168.99.0 0.0.0.255
 permit 192.168.10.0 0.0.0.255
 deny any log
ip http access-class MGMT-ACCESS
```

This is a good cybersecurity lab exercise — demonstrate what the API
exposes, then demonstrate how to restrict access to it.

---

## Part 3 — API Calls

### Tool 1: curl (command line)

curl is a command-line HTTP client. The `-k` flag skips SSL certificate
verification (needed for self-signed certs on lab devices).

#### GET hostname
```bash
curl -k -u admin:'password' \
  -H "Accept: application/yang-data+json" \
  https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname
```

Response:
```json
{
    "Cisco-IOS-XE-native:hostname": "JLM-LAB-R1"
}
```

#### GET all interfaces
```bash
curl -k -u admin:'password' \
  -H "Accept: application/yang-data+json" \
  https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/interface \
  | python3 -m json.tool
```

#### GET OSPF configuration
```bash
curl -k -u admin:'password' \
  -H "Accept: application/yang-data+json" \
  "https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf"
```

### Tool 2: Python requests library

See `ansible/playbooks/restconf-query.py` for the full script.

Key pattern:
```python
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()  # suppress self-signed cert warning

response = requests.get(
    "https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname",
    auth=HTTPBasicAuth("admin", "password"),
    headers={"Accept": "application/yang-data+json"},
    verify=False  # self-signed cert
)

data = response.json()
print(data["Cisco-IOS-XE-native:hostname"])
```

---

## Part 4 — Live Query Results (May 21, 2026)

### Query 1: Hostname
```json
{"Cisco-IOS-XE-native:hostname": "JLM-LAB-R1"}
```

### Query 2: IOS Version
```json
{"Cisco-IOS-XE-native:version": "16.10"}
```

### Query 3: Interface Summary (parsed)
```
Interface            Status          VLAN/IP
-------------------- --------------- --------------------
GigabitEthernet0/0/0 enabled         DHCP
GigabitEthernet0/0/1 shutdown
GigabitEthernet0/1/0 enabled         access VLAN 10
GigabitEthernet0/1/1 enabled         trunk native 99
GigabitEthernet0/1/2 enabled         access VLAN 10
GigabitEthernet0/1/3 enabled
```

### Query 4: OSPF Process 1
```
OSPF Process: 1
Router ID:    not set (uses loopback 10.0.0.1)
Networks:     9 configured
              10.0.0.1 0.0.0.0 area 0
              192.168.10.0 0.0.0.255 area 0
              192.168.20.0 0.0.0.255 area 0
              192.168.30.0 0.0.0.255 area 0
              192.168.31.0 0.0.0.255 area 0
              192.168.40.0 0.0.0.255 area 0
              192.168.50.0 0.0.0.255 area 0
              192.168.99.0 0.0.0.255 area 0
              192.168.100.0 0.0.0.255 area 0
```

### Query 5: NTP
```
NTP Server: 216.239.35.0
NTP Server: 216.239.35.4
NTP Master: stratum configured
```

---

## Part 5 — HTTP Methods Reference (CCNA)

| Method | RESTCONF Use | SQL Equivalent |
|---|---|---|
| GET | Read configuration or operational data | SELECT |
| POST | Create new configuration | INSERT |
| PUT | Replace existing configuration | REPLACE |
| PATCH | Merge/update partial configuration | UPDATE |
| DELETE | Remove configuration | DELETE |

### HTTP Response Codes

| Code | Meaning | When You See It |
|---|---|---|
| 200 OK | Successful GET | Config retrieved |
| 201 Created | Successful POST | New config created |
| 204 No Content | Successful PUT/PATCH/DELETE | Change applied |
| 400 Bad Request | Malformed request | Bad JSON/YANG path |
| 401 Unauthorized | Auth failed | Wrong credentials |
| 404 Not Found | Resource doesn't exist | Wrong YANG path |
| 409 Conflict | Resource already exists | POST on existing config |

---

## Part 6 — Useful YANG Paths for IOS XE

| What You Want | YANG Path |
|---|---|
| Hostname | `Cisco-IOS-XE-native:native/hostname` |
| IOS version | `Cisco-IOS-XE-native:native/version` |
| All interfaces | `Cisco-IOS-XE-native:native/interface` |
| Specific interface | `Cisco-IOS-XE-native:native/interface/GigabitEthernet=0%2F0%2F0` |
| OSPF config | `Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf` |
| NTP config | `Cisco-IOS-XE-native:native/ntp` |
| All VLANs | `Cisco-IOS-XE-native:native/vlan` |
| DHCP pools | `Cisco-IOS-XE-native:native/ip/dhcp/pool` |
| ACLs | `Cisco-IOS-XE-native:native/ip/access-list` |
| Routing table | `Cisco-IOS-XE-ip:ip-route-oper:routing` |

**Note:** Forward slashes in interface names must be URL-encoded as `%2F`
when used in a URL path parameter.

---

## Part 7 — Cybersecurity Lab Extensions

This RESTCONF setup is a useful cybersecurity teaching resource. The
following exercises demonstrate API attack surface and defense:

### Exercise 1 — What does an unauthenticated request return?
```bash
curl -k -H "Accept: application/yang-data+json" \
  https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname
```
Expected: 401 Unauthorized — authentication required.

### Exercise 2 — What can a read-only user see?
Create a priv 1 user and test what RESTCONF returns.
Note: RESTCONF requires privilege 15 — priv 1 returns 401.
This demonstrates why privilege level matters for API access.

### Exercise 3 — Restrict API access by source IP
Apply `ip http access-class` to limit RESTCONF to management VLAN only.
Verify that requests from VLAN 20 (TRUSTED) are rejected after applying
the ACL. Demonstrates defense-in-depth for management plane security.

### Exercise 4 — What does a PUT request do?
Attempt to change the hostname via PUT:
```bash
curl -k -X PUT \
  -u admin:'password' \
  -H "Content-Type: application/yang-data+json" \
  -H "Accept: application/yang-data+json" \
  -d '{"Cisco-IOS-XE-native:hostname": "HACKED"}' \
  https://192.168.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname
```
Demonstrates that API access with write permissions is equivalent to
full CLI access — why credential security and access control matter.
**Always revert after this exercise:** `write memory` after restoring hostname.

---

## CCNA Exam Topics Covered

| Topic | Domain | Coverage |
|---|---|---|
| REST API concepts | 6 | GET/POST/PUT/PATCH/DELETE demonstrated |
| HTTP methods and status codes | 6 | Full reference table with examples |
| JSON data format | 6 | All responses parsed and displayed |
| YANG data models | 6 | URL structure explained, 10 paths documented |
| RESTCONF vs NETCONF | 6 | Comparison table |
| Ansible/programmability tools | 6 | Python requests library used |
| Management plane security | 5 | API attack surface, access-class hardening |
| Privilege levels | 5 | Privilege 15 required for RESTCONF |
| IOS XE programmability | 6 | Live queries on production device |

---

## Lessons Learned

1. **RESTCONF URLs are case-sensitive.** `Cisco-IOS-XE-native` must be
   exact. A single character difference returns 404.

2. **Self-signed certificates require `-k` in curl and `verify=False`
   in Python requests.** In production, use a trusted certificate or
   import the device cert into your trust store.

3. **Forward slashes in interface names must be URL-encoded.** Use `%2F`
   for `/` when referencing specific interfaces in the URL path.

4. **RESTCONF privilege requirement is strict.** Unlike SSH which prompts
   for enable, RESTCONF requires privilege 15 at login — a priv 1 user
   gets 401 immediately.

5. **RESTCONF exposes the entire running configuration as an API.**
   Any credential that can authenticate to RESTCONF has read (and
   potentially write) access to every configuration element. This is
   why restricting HTTPS access to the management VLAN is critical
   in any real deployment.

6. **`ip http server` (port 80) and `ip http secure-server` (port 443)
   are independent.** Always disable HTTP and use HTTPS only. Even in
   a lab, developing good habits matters.

---

*Lab completed: May 21, 2026*
*Device: Cisco C1111-4PWB JLM-LAB-R1, IOS XE 16.10*
*CCNA domains: Domain 6 — Automation & Programmability, Domain 5 — Security*
