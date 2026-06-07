# Session Plan — Field Tech Lab 001

**Lab Series:** ARIA Field-to-Cyber Lab Series
**Track:** Field Tech Foundation Labs
**Student:** Sha-Neal Prather
**Instructor:** Julius Moore

---

## Student Context

Sha-Neal is working toward a BS in Cybersecurity and Assurance from WGU and recently started her first internship as a field technician with Robert Half. During her first week she worked with Chromebooks and iPads, performed device sanitation, completed Chromebook powerwash/factory reset steps, checked for and applied updates, used retest.us for functionality testing, counted devices, documented damaged equipment, and navigated real field-site logistics.

This lab connects directly to that experience.

---

## Session Goal

Help Sha-Neal understand that endpoint support, network verification, documentation, and cybersecurity fundamentals are connected.

By the end of the session she should be able to securely access her assigned Linux endpoint, confirm system identity, verify basic network configuration, test connectivity, and document the results professionally.

---

## Assigned Training System

| Item | Value |
|---|---|
| System name | student-linux-01 |
| Student username | sprather |
| Tailscale IP | 100.125.65.78 |
| Local lab IP | 192.168.70.12 |
| VLAN | 70 SERVER |
| Default gateway | 192.168.70.1 |
| DNS server | 192.168.10.16 |

---

## Instructor Opening

Start by connecting the lab to her real internship work:

> "You already started doing real endpoint support: resetting devices, checking updates, identifying damaged hardware, counting inventory, and documenting device issues. This lab builds the technical foundation behind that work. Instead of only working with Chromebooks and iPads, today you will verify a Linux endpoint and document it like a field technician or help desk analyst."

---

## Student Tasks

### 1. Connect to the lab system

```bash
ssh sprather@100.125.65.78
```

### 2. Confirm the logged-in user

```bash
whoami
```

Expected: `sprather`

### 3. Confirm the hostname

```bash
hostname
```

Expected: `student-linux-01`

### 4. Identify IP addresses

```bash
ip addr
```

Student should identify:
- Local lab IP: 192.168.70.12
- Tailscale IP: 100.125.65.78

### 5. Identify the default gateway

```bash
ip route
```

Expected gateway: `192.168.70.1`

### 6. Check DNS configuration

```bash
cat /etc/resolv.conf
```

Expected DNS server: `192.168.10.16`

### 7. Test gateway connectivity

```bash
ping -c 4 192.168.70.1
```

### 8. Test DNS server reachability

```bash
ping -c 4 192.168.10.16
```

### 9. Test internet connectivity by IP

```bash
ping -c 4 1.1.1.1
```

### 10. Test DNS resolution

```bash
ping -c 4 google.com
```

---

## Teaching Points

Explain these concepts in beginner-friendly language:

| Concept | Plain language explanation |
|---|---|
| SSH | Remote command-line access to a system across a network |
| whoami | Confirms who is logged in — not the computer name, the user |
| hostname | Confirms which machine she is working on |
| IP address | Identifies the system on a specific network |
| Default gateway | The door out — where traffic goes when leaving the local network |
| DNS | Converts names like google.com into IP addresses the network understands |
| ping by IP | Tests routing and internet reachability without DNS |
| ping by name | Tests routing + DNS together — both must work |
| Documentation | Proves the work was done and makes the findings repeatable |

---

## Instructor Rule

Do not take over the keyboard unless absolutely necessary.

Use coaching questions:

- What command did you run?
- What output do you see?
- What do you think that means?
- What would you check next?
- How would you document that for a ticket?

---

## Completion Criteria

Lab 001 is complete when Sha-Neal can explain:

- How she connected to the system
- What system she connected to
- What account she used
- What IP addresses were assigned
- What gateway the system uses
- What DNS server the system uses
- Whether the system has network and internet connectivity
- How this connects to field technician and cybersecurity work

---

## Portfolio Output

After the lab, Sha-Neal should create:

1. A GitHub lab folder with her findings
2. A short lab README
3. A commands-used file
4. A findings summary
5. A LinkedIn post summarizing what she learned

---

## Next Lab

Field Tech Lab 002: Perform a Basic Linux Endpoint Health Check
