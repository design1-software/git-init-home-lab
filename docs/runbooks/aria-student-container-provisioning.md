# Runbook — Create New ARIA Student Container

**Standard:** One student = one dedicated LXC container cloned from the approved Debian 13 template.

---

## Operating Rule

Every ARIA student receives a dedicated LXC training container cloned from the approved Debian template. No two students share a container. This ensures each student has their own Linux endpoint, hostname, user account, Tailscale connection, lab history, file space, and break/fix environment.

---

## Per-Student Provisioning Spec

| Field | Value |
|---|---|
| CT ID | Next available number (see Student Registry below) |
| Hostname | `student-linux-XX` (sequential) |
| Username | Student-specific (e.g. `sprather`) |
| Local IP | Next available VLAN 70 address (see registry) |
| Gateway | 192.168.70.1 (3560CX HSRP VIP) |
| DNS | 192.168.10.16 (Pi-hole) |
| Tailscale | Installed on container · shared only with that student |
| Instructor account | `julius` (SSH key: `aria_julius_ed25519`) |
| Student account | Student username · password · controlled sudo |

---

## Account Model Inside Every Container

| Account | Type | Access method | Sudo |
|---|---|---|---|
| student username | Normal user | Password + SSH | Yes — password required |
| julius | Instructor | SSH key only (`aria_julius_ed25519`) | Yes — for observation and assist |
| root | Emergency only | Proxmox console (`pct exec`) | — |

Root inside the container is not routinely used. Student accounts practice with controlled sudo. Julius can escalate if a student is stuck.

---

## Student Registry

| CT ID | Hostname | Student | Username | Local IP | Tailscale IP | Status |
|---|---|---|---|---|---|---|
| 101 | lab-linux-01 | — | — | — | — | Template |
| 102 | student-linux-01 | Sha-Neal Prather | sprather | 192.168.70.12 | 100.125.65.78 | Active |
| 103 | student-linux-02 | TBD | TBD | 192.168.70.13 | TBD | Not created |

---

## Provisioning Checklist

Follow these steps in order for every new student. Do not skip steps.

---

### Step 1 — Clone from the Debian template

On the ARIA Proxmox host:

```bash
# List available templates to confirm the template CT ID
pct list

# Clone the template to a new CT ID
pct clone 101 <new-ct-id> --hostname student-linux-XX --full
```

`--full` creates an independent copy, not a linked clone. This ensures each student container is isolated.

---

### Step 2 — Set the hostname and static IP

```bash
pct set <ct-id> \
  --hostname student-linux-XX \
  --ipconfig0 ip=192.168.70.XX/24,gw=192.168.70.1 \
  --nameserver 192.168.10.16
```

Verify the config:

```bash
pct config <ct-id>
```

---

### Step 3 — Start the container

```bash
pct start <ct-id>
```

Confirm it is running:

```bash
pct list
```

---

### Step 4 — Create the student user account

```bash
pct exec <ct-id> -- bash -c "
  useradd -m -s /bin/bash <username> &&
  echo '<username>:<temporary-password>' | chpasswd &&
  usermod -aG sudo <username>
"
```

Force password change on first login:

```bash
pct exec <ct-id> -- passwd -e <username>
```

Do not commit the temporary password to the repo. Deliver it to the student separately.

---

### Step 5 — Create the julius instructor account

```bash
pct exec <ct-id> -- bash -c "
  useradd -m -s /bin/bash julius &&
  usermod -aG sudo julius &&
  mkdir -p /home/julius/.ssh &&
  chmod 700 /home/julius/.ssh &&
  chown julius:julius /home/julius/.ssh
"
```

Add the julius public key (paste the contents of `~/.ssh/aria_julius_ed25519.pub`):

```bash
pct exec <ct-id> -- bash -c "
  echo '<julius-public-key>' >> /home/julius/.ssh/authorized_keys &&
  chmod 600 /home/julius/.ssh/authorized_keys &&
  chown julius:julius /home/julius/.ssh/authorized_keys
"
```

Test instructor SSH access before proceeding:

```bash
ssh -i ~/.ssh/aria_julius_ed25519 julius@192.168.70.XX
```

---

### Step 6 — Install and enable Tailscale

```bash
pct exec <ct-id> -- bash -c "
  curl -fsSL https://tailscale.com/install.sh | sh
"
```

Bring Tailscale up:

```bash
pct exec <ct-id> -- tailscale up
```

Authenticate in the Tailscale admin console. The container will appear as a new device.

---

### Step 7 — Share the container with the student only

In the Tailscale admin console:

1. Find the new container device
2. Use **Share** to share it with the student's Tailscale account
3. Do not share it with anyone else
4. Note the Tailscale IP assigned to the container

Each student connects to their own container only — they cannot reach other student containers via Tailscale.

---

### Step 8 — Validate SSH access

**Instructor access:**

```bash
ssh -i ~/.ssh/aria_julius_ed25519 julius@<tailscale-ip>
```

Add the entry to `~/.ssh/config`:

```text
Host aria-student-linux-XX
    HostName <tailscale-ip>
    User julius
    IdentityFile ~/.ssh/aria_julius_ed25519
    IdentitiesOnly yes
```

Then confirm: `ssh aria-student-linux-XX`

**Student access (verify before sending credentials):**

```bash
ssh <username>@<tailscale-ip>
```

Confirm the student can log in and that `sudo` prompts for a password.

---

### Step 9 — Assign the first lab

Send the student:

1. Their Tailscale SSH address
2. Their temporary password (via secure channel — not the repo)
3. The student guide for Field Tech Lab 001

Message template:

```text
Your training system is ready.

System: student-linux-XX
SSH command: ssh <username>@<tailscale-ip>
Temporary password: [send separately]

You will be asked to set a new password on first login.

Your first lab is Field Tech Lab 001: Verify Endpoint Identity and Network Connectivity.
I will send you the lab guide separately.
```

---

### Step 10 — Update the Student Registry and repo

Update the Student Registry table in this runbook with:
- CT ID, hostname, student name, username, local IP, Tailscale IP, status

Update `docs/proxmox-server-build.md` Active LXC Containers table.

Update `docs/network-quick-reference.md` with the new container row and instructor SSH config block.

Commit to `main`.

---

## Teardown (When a Student Completes the Program)

```bash
# Stop the container
pct stop <ct-id>

# Archive or snapshot if the student's work should be preserved
# Then destroy
pct destroy <ct-id>
```

Remove the Tailscale share in the admin console. Remove the `~/.ssh/config` entry for that container.

---

*Created: Jun 7, 2026*
*Standard: one student = one container, cloned from approved Debian 13 template*
