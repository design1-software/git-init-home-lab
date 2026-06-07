# ARIA Student Container Provisioning Standard

## Purpose

This checklist defines the standard process for creating a dedicated ARIA Linux training container for each student.

**ARIA operating rule: One student = one dedicated container.**

Each student has their own Linux endpoint, user account, Tailscale share, lab history, and documentation trail. No two students share a container.

---

## 1. Student Intake Information

Before creating the container, collect:

```text
Student full name:
Student preferred name:
Student email:
Training role:
Degree/career path:
Current experience level:
GitHub username:
LinkedIn profile:
Assigned lab track:
Start date:
```

Example:

```text
Student: Sha-Neal Prather
Training role: JLM Lab Trainee
Degree path: BS Cybersecurity and Assurance, WGU
Current experience: Field technician internship
Assigned lab track: ARIA Field-to-Cyber Lab Series
```

---

## 2. Container Naming Standard

Use a predictable naming structure:

```text
student-linux-01
student-linux-02
student-linux-03
```

Recommended future enterprise-style standard:

```text
aria-lnx-stu01
aria-lnx-stu02
aria-lnx-stu03
```

For continuity, Sha-Neal stays on `student-linux-01`. Next student receives `student-linux-02`.

---

## 3. CT ID Assignment and Student Registry

Assign the next available Proxmox container ID.

Current state:

| CT ID | Hostname | Student | Username | Local IP | Tailscale IP | Status |
|---|---|---|---|---|---|---|
| 101 | lab-linux-01 | — | — | — | — | Template (Debian 13) |
| 102 | student-linux-01 | Sha-Neal Prather | sprather | 192.168.70.12 | 100.125.65.78 | Active |
| 103 | student-linux-02 | TBD | TBD | 192.168.70.13 | TBD | Not created |

Record for each new student:

```text
Student:
CT ID:
Hostname:
Local IP:
Tailscale IP:
Student username:
Instructor username: julius
```

---

## 4. Clone From Approved Template

Clone the student container from the approved Debian 13 LXC template (CT 101).

```bash
pct clone 101 <new-ct-id> --hostname student-linux-XX --full
```

`--full` creates an independent copy — not a linked clone. Always clone from the template. Do not build student containers from scratch unless the template is broken.

---

## 5. Assign Hostname

Set the hostname to match the container name:

```bash
pct set <ct-id> --hostname student-linux-XX
```

Validation inside the container:

```bash
hostname
```

Expected: `student-linux-XX`

---

## 6. Assign VLAN 70 Network Address

All student containers run on VLAN 70 SERVER:

```text
Bridge:  vmbr0
Gateway: 192.168.70.1
DNS:     192.168.10.16
```

Current and planned IP assignments:

```text
student-linux-01 = 192.168.70.12
student-linux-02 = 192.168.70.13
student-linux-03 = 192.168.70.14
student-linux-04 = 192.168.70.15
```

Set via Proxmox:

```bash
pct set <ct-id> --ipconfig0 ip=192.168.70.XX/24,gw=192.168.70.1 --nameserver 192.168.10.16
```

Validation:

```bash
ip addr
ip route
cat /etc/resolv.conf
```

---

## 7. Start and Validate Container

```bash
pct start <ct-id>
pct status <ct-id>
```

Expected: `status: running`

Enter the container if needed:

```bash
pct enter <ct-id>
```

---

## 8. Create Student User

Inside the container:

```bash
adduser <studentusername>
usermod -aG sudo <studentusername>
```

Username format: `firstinitiallastname` (e.g. `sprather`, `jdoe`, `asmith`)

Force password change on first login:

```bash
passwd -e <studentusername>
```

Do not commit passwords to the repo. Deliver the temporary password to the student via secure channel only.

Validate:

```bash
groups <studentusername>
su - <studentusername>
sudo whoami
```

Expected: `root`

**Policy:**
- Student accounts are unique — no shared accounts
- No instructor use of student credentials
- Sudo access is intentional and per-lab-track, not automatic

---

## 9. Create Instructor Account

Every student container must include the `julius` instructor account:

```bash
adduser julius
usermod -aG sudo julius
```

Validate:

```bash
groups julius
su - julius
sudo whoami
```

Expected: `root`

**Account model inside every container:**

| Account | Type | Access | Sudo |
|---|---|---|---|
| student username | Normal user | Password + SSH | Yes — password required |
| julius | Instructor/admin | SSH key only (`aria_julius_ed25519`) | Yes |
| root | Emergency only | Proxmox console (`pct enter`) | — |

---

## 10. Configure Instructor SSH Key

ARIA-specific instructor key on Julius Mac: `~/.ssh/aria_julius_ed25519`

Copy the public key to the new container:

```bash
ssh-copy-id -i ~/.ssh/aria_julius_ed25519.pub julius@<local-or-tailscale-ip>
```

Test key-based login:

```bash
ssh -i ~/.ssh/aria_julius_ed25519 julius@<ip>
```

Add to `~/.ssh/config` on the instructor machine:

```text
Host aria-student-linux-XX
    HostName <tailscale-ip>
    User julius
    IdentityFile ~/.ssh/aria_julius_ed25519
    IdentitiesOnly yes
```

Connect using: `ssh aria-student-linux-XX`

---

## 11. Install and Enable Tailscale

Inside the container:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

Authenticate in the Tailscale admin console. Record the assigned IP:

```bash
tailscale ip -4
tailscale status
```

Record:

```text
Tailscale IP:
Tailscale device name:
Shared with:
```

---

## 12. Share Only the Assigned Container

In Tailscale admin console:

```text
Devices → select student container → Share → enter student email
```

**Share only the student's assigned container.** Never share:

```text
Proxmox host
C1111 or 3560CX management
Comet KVM
Pi-hole / DNS
Other student containers
The entire tailnet
```

Student accepts the email invite and confirms the shared device appears in their Tailscale app.

---

## 13. Validate Student SSH Access

```bash
ssh <studentusername>@<tailscale-ip>
```

Student validation commands:

```bash
whoami        # → student username
hostname      # → student-linux-XX
ip addr       # → 192.168.70.XX assigned
ip route      # → default via 192.168.70.1
cat /etc/resolv.conf  # → nameserver 192.168.10.16
```

---

## 14. Validate Instructor SSH Access

```bash
ssh aria-student-linux-XX
```

Validate:

```bash
whoami        # → julius
sudo whoami   # → root
hostname      # → student-linux-XX
```

---

## 15. Run Baseline Network Tests

```bash
ping -c 4 192.168.70.1    # gateway
ping -c 4 192.168.10.16   # DNS server
ping -c 4 1.1.1.1         # internet by IP
ping -c 4 google.com      # DNS resolution + internet
```

If `1.1.1.1` passes but `google.com` fails: investigate DNS.
If gateway fails: investigate VLAN/IP/bridge configuration.

---

## 16. Assign First Lab

Every new student starts with:

**Field Tech Lab 001: Verify Endpoint Identity and Network Connectivity**

This lab validates: SSH access, correct user, correct hostname, IP address, gateway, DNS, connectivity, and documentation.

Student message template:

```text
Your training system is ready.

System: student-linux-XX
SSH: ssh <username>@<tailscale-ip>
Temporary password: [send separately — never in the repo]

You will be prompted to set a new password on first login.

Your first lab is Field Tech Lab 001: Verify Endpoint Identity and Network Connectivity.
I will send you the lab guide separately.
```

---

## 17. Required Student Deliverables (After Lab 001)

```text
GitHub README
Commands-used file
Findings summary
Lessons learned
LinkedIn post draft
```

Recommended folder structure:

```text
field-tech-labs/
└── lab-001-endpoint-identity-network-connectivity/
    ├── README.md
    ├── commands-used.md
    ├── findings.md
    └── lessons-learned.md
```

---

## 18. Training Record

Maintain a training record for each student:

```text
Student:
Container:
CT ID:
Student username:
Instructor username: julius
Local IP:
Tailscale IP:
Start date:
Lab track:
Current lab:
Completed labs:
GitHub repo:
LinkedIn profile:
Notes:
```

Current record:

```text
Student: Sha-Neal Prather
Container: student-linux-01
CT ID: 102
Student username: sprather
Instructor username: julius
Local IP: 192.168.70.12
Tailscale IP: 100.125.65.78
Lab track: ARIA Field-to-Cyber Lab Series
Current lab: Field Tech Lab 002
Completed labs: Lab 001
```

---

## 19. Security Rules

- One student per container
- One student account per student
- One instructor account (`julius`) per container
- No shared student credentials
- Instructor does not log in as the student
- `root` is accessed only through Proxmox host console — emergency only
- Share only the assigned container via Tailscale
- Do not expose Proxmox, routers, switches, Comet KVM, DNS, or other student containers to trainees
- Document every student endpoint in this registry

---

## 20. Completion Checklist

A student container is ready when all items below are complete:

```text
[ ] Container cloned from approved Debian 13 template (CT 101)
[ ] CT ID assigned and recorded in registry
[ ] Hostname configured and validated
[ ] VLAN 70 IP configured (192.168.70.XX)
[ ] Gateway configured (192.168.70.1)
[ ] DNS configured (192.168.10.16)
[ ] Container running (pct status = running)
[ ] Student user created with controlled sudo
[ ] Student first-login password change enforced
[ ] julius instructor account created with sudo
[ ] julius SSH key installed and tested
[ ] Tailscale installed and running
[ ] Tailscale IP recorded
[ ] Container shared only with assigned student
[ ] Student accepted Tailscale share
[ ] Student SSH access validated
[ ] Instructor SSH access validated (ssh aria-student-linux-XX)
[ ] Gateway ping successful (192.168.70.1)
[ ] DNS server ping successful (192.168.10.16)
[ ] Internet by IP successful (1.1.1.1)
[ ] DNS resolution successful (google.com)
[ ] Lab 001 assigned and guide sent
[ ] Training record created/updated
[ ] docs/network-quick-reference.md updated with new container row
[ ] ~/.ssh/config updated with new Host entry
```

---

## 21. ARIA Provisioning Principle

Do not overbuild before the student can train.

The goal is a repeatable, secure, student-ready endpoint that supports hands-on learning and documentation.

```text
Provision cleanly.
Share narrowly.
Validate access.
Run Lab 001.
Document everything.
```

---

*Created: Jun 7, 2026*
*Standard: one student = one container, cloned from approved Debian 13 template (CT 101)*
