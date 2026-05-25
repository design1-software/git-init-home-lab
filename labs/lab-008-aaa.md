# Lab: AAA — Authentication, Authorization & Accounting

# lab-008-aaa.md

# JLM Home Lab — git-init-home-lab

# Completed: May 25, 2026

-----

## Overview

This lab documents the configuration of AAA (Authentication,
Authorization, and Accounting) on the JLM home lab C1111 router using
the local user database. AAA replaces the legacy line-based
authentication model with a centralized, extensible security framework.

**CCNA Domain:** Domain 5 — Security Fundamentals (15% of exam)

**Device:** Cisco C1111-4PWB (JLM-LAB-R1) — IOS XE 16.10

**Safety procedure used:** Console session (COM5) kept open throughout
configuration. SSH tested in a second session before saving. This is
the correct procedure any time AAA is modified on a production device.

-----

## Part 1 — What AAA Is

### The Three Components

|Component         |Question It Answers|Example                                      |
|------------------|-------------------|---------------------------------------------|
|**Authentication**|Who are you?       |Username + password verified against local DB|
|**Authorization** |What can you do?   |Privilege level 15 = full exec access        |
|**Accounting**    |What did you do?   |Log session start/stop, commands executed    |

### Legacy Authentication vs AAA

**Before AAA (line-based authentication):**

```
line vty 0 4
 login local          ← checks local username database
 transport input ssh
```

This works but has limitations:

- No authorization control — all users get same access level
- No accounting — no session logging
- Cannot integrate with RADIUS/TACACS+ without reconfiguring every line
- No centralized policy — each line configured independently

**After AAA:**

```
aaa new-model
aaa authentication login default local
aaa authorization exec default local
```

All authentication goes through the AAA framework. Switching from
local to RADIUS later requires changing one line — the source, not
the structure.

-----

## Part 2 — AAA Methods

### Authentication Methods

|Method         |What It Uses           |Use Case                               |
|---------------|-----------------------|---------------------------------------|
|`local`        |Local username database|Single device, no external server      |
|`group radius` |RADIUS server          |Enterprise, centralized auth           |
|`group tacacs+`|TACACS+ server         |Cisco enterprise, command authorization|
|`enable`       |Enable password        |Fallback for enable authentication     |
|`none`         |No authentication      |Emergency access (use carefully)       |

### Method Lists

AAA uses **method lists** — ordered lists of authentication methods
to try in sequence. If the first method fails or is unavailable,
the next is tried.

```
aaa authentication login default local
```

This creates a method list named `default` that uses the local
database. If you wanted a fallback:

```
aaa authentication login default group radius local
```

This tries RADIUS first, falls back to local if RADIUS is unreachable.
The `local` fallback is critical — without it, a RADIUS server outage
locks everyone out.

-----

## Part 3 — Configuration

### Pre-configuration State

Before AAA, the C1111 used line-based authentication:

```
line vty 0 4
 login local
 transport input ssh
```

Users had to type `enable` after login to reach privilege 15.

### AAA Configuration Applied

```
aaa new-model
aaa authentication login default local
aaa authentication enable default enable
aaa authorization exec default local
```

**`aaa new-model`** — activates the AAA framework. This single command
immediately changes how all authentication works on the device. There
is no partial AAA — it’s all or nothing. This is why a console session
must be open before running this command.

**`aaa authentication login default local`** — creates the default
login method list using the local database. Applies to all lines
(console and VTY) unless overridden.

**`aaa authentication enable default enable`** — uses the enable
password for enable mode authentication. Without this, `aaa new-model`
breaks the `enable` command.

**`aaa authorization exec default local`** — grants exec shell access
based on the user’s privilege level in the local database. Users with
`privilege 15` get direct enable prompt without typing `enable`.
This is why SSH sessions now land directly at `JLM-LAB-R1#` instead
of `JLM-LAB-R1>`.

### Line Configuration

```
line console 0
 login authentication default

line vty 0 4
 login authentication default
 authorization exec default
```

**`login authentication default`** — explicitly applies the default
AAA method list to this line. When `aaa new-model` is enabled, this
happens automatically, but explicit configuration is best practice
and makes the intent clear.

**`authorization exec default`** — applies the exec authorization
method list to VTY lines, enabling automatic privilege level assignment.

### Why Accounting Failed

```
aaa accounting exec default start-stop logging
              ^
% Invalid input detected
```

The `logging` keyword for accounting requires an active syslog
destination or TACACS+ server to be configured. On IOS XE 16.10
without an external server, this command is rejected.

**Resolution:** Full accounting will be configured at Phase C when
FreeRADIUS runs as an LXC container on the Proxmox server. At that
point, accounting records will be sent to the RADIUS server for
centralized logging.

-----

## Part 4 — Verification (Live Output — May 25, 2026)

### show running-config | include aaa

```
aaa new-model
aaa authentication login default local
aaa authentication enable default enable
aaa authorization exec default local
aaa session-id common
login on-success log
```

**`aaa session-id common`** — auto-generated by IOS when AAA is
enabled. Ensures authentication and authorization use the same
session ID for consistent accounting records.

**`login on-success log`** — logs successful login events to syslog.
Pre-existing configuration, now enforced through AAA framework.

### AAA in action — syslog evidence

From the console during testing:

```
%SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin]
[Source: 192.168.20.43] [localport: 22] at 13:02:04 UTC Mon May 25 2026
```

This confirms:

- AAA authentication processed the login ✅
- User `admin` authenticated successfully ✅
- Source IP logged (192.168.20.43 = MacBook Pro on VLAN 20) ✅
- Timestamp recorded ✅

```
%SYS-2-PRIVCFG_ENCRYPT: Successfully encrypted private config
```

IOS automatically encrypted the private configuration when AAA was
enabled — additional security improvement. ✅

### SSH behavior before vs after AAA

**Before AAA:**

```
login as: admin
Password: ****
JLM-LAB-R1>          ← user mode, must type 'enable'
Password: ****
JLM-LAB-R1#          ← enable mode
```

**After AAA with authorization exec:**

```
(admin@192.168.10.1) Password: ****
JLM-LAB-R1#          ← directly at enable mode (privilege 15 granted by AAA)
```

The `aaa authorization exec default local` command checks the user’s
configured privilege level (`privilege 15` in the username command)
and grants the appropriate exec level automatically. No separate
`enable` password required.

-----

## Part 5 — AAA vs RADIUS vs TACACS+

This lab implements local AAA. The framework is designed to swap the
authentication source without changing the structure.

|Feature        |Local AAA    |RADIUS         |TACACS+              |
|---------------|-------------|---------------|---------------------|
|Auth database  |Router local |External server|External server      |
|Protocol       |N/A          |UDP 1812/1813  |TCP 49               |
|Encryption     |N/A          |Password only  |Full packet          |
|Command auth   |No           |No             |Yes                  |
|Scalability    |Single device|Many devices   |Many devices         |
|Cisco preferred|No           |Yes (802.1X)   |Yes (network devices)|

**RADIUS** (Remote Authentication Dial-In User Service) — industry
standard, used for 802.1X wireless authentication and VPN. UDP based.
Only encrypts the password field.

**TACACS+** (Terminal Access Controller Access-Control System Plus) —
Cisco proprietary, preferred for managing network device access.
TCP based, encrypts entire payload, supports per-command authorization.

**Migration path from this lab to RADIUS:**

```
! Add RADIUS server
radius server FREERADIUS
 address ipv4 192.168.70.x auth-port 1812 acct-port 1813
 key <shared-secret>

! Update method list to try RADIUS first, fall back to local
aaa authentication login default group radius local
aaa authorization exec default group radius local
```

This is all that changes — the line configuration stays the same.

-----

## Part 6 — CCNA Exam Topics Covered

|Topic                     |Coverage                                            |
|--------------------------|----------------------------------------------------|
|AAA framework concepts    |Authentication, Authorization, Accounting defined   |
|`aaa new-model`           |Configured on C1111                                 |
|Local authentication      |`aaa authentication login default local`            |
|Enable authentication     |`aaa authentication enable default enable`          |
|Exec authorization        |`aaa authorization exec default local`              |
|Method lists              |Default list, ordered fallback explained            |
|AAA vs line authentication|Before/after comparison                             |
|RADIUS vs TACACS+         |Comparison table                                    |
|Privilege levels          |Priv 15 auto-granted via AAA authorization          |
|Login success logging     |`login on-success log` in action                    |
|AAA accounting            |Concepts documented, full config deferred to Phase C|

-----

## Part 7 — Phase C Extension (RADIUS)

When the Proxmox server is online, FreeRADIUS will be deployed as
an LXC container on VLAN 70. At that point:

1. Deploy FreeRADIUS LXC on Proxmox (192.168.70.x)
1. Configure shared secret between C1111 and FreeRADIUS
1. Add users to FreeRADIUS database
1. Update C1111 AAA method lists to use RADIUS with local fallback
1. Configure RADIUS accounting for full session logging
1. Test authentication via RADIUS, verify fallback to local works

This completes the full AAA → RADIUS implementation and closes the
enterprise authentication gap entirely.

-----

## Lessons Learned

1. **Always keep a console session open when enabling `aaa new-model`.**
   The moment `aaa new-model` is entered, authentication changes
   immediately. A misconfiguration can lock out all SSH access.
   Console access bypasses AAA and is the recovery path.
1. **`aaa authorization exec default local` eliminates the need for
   a separate enable password for privileged users.** Users with
   privilege 15 in the local database land directly at the enable
   prompt. This is more secure and more convenient.
1. **`aaa authentication enable default enable` is required.** Without
   it, `aaa new-model` breaks the `enable` command — the router
   doesn’t know how to authenticate enable mode transitions.
1. **`aaa accounting` requires an external server on IOS XE 16.10.**
   The `logging` keyword for accounting was rejected without a
   TACACS+/RADIUS destination. Full accounting is a Phase C task.
1. **AAA is all-or-nothing.** There is no partial AAA mode. Once
   `aaa new-model` is entered, all lines use AAA. This is why the
   method lists must be correct before the command is entered.
1. **RADIUS uses UDP, TACACS+ uses TCP.** This is a common exam
   question. RADIUS is connectionless (UDP 1812 auth, 1813 accounting).
   TACACS+ is connection-oriented (TCP 49) and encrypts the full
   packet — making it preferred for device management.

-----

## Verification Commands

```
show running-config | include aaa
```

All AAA configuration lines.

```
show aaa sessions
```

Active AAA sessions.

```
show aaa user all
```

AAA user attributes for active sessions.

```
debug aaa authentication
```

Real-time authentication events — use carefully.

```
debug aaa authorization
```

Real-time authorization events — use carefully.

-----

*Lab completed: May 25, 2026*
*Device: Cisco C1111-4PWB JLM-LAB-R1, IOS XE 16.10*
*Phase C extension: Full RADIUS with FreeRADIUS on Proxmox*
*CCNA domain: Domain 5 — Security Fundamentals*