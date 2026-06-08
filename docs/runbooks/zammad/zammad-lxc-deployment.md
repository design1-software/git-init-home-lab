# Zammad LXC Deployment Runbook

> **Status:** Implemented and validated 2026-06-07  
> **Service:** ARIA Help Desk / Ticketing Platform  
> **Hostname:** `aria-zammad-01`  
> **CT ID:** `110`  
> **FQDN:** `helpdesk.aria.local`  
> **IP:** `192.168.70.20/24`  
> **Gateway:** `192.168.70.1`  
> **DNS:** `192.168.10.16`  
> **Access model:** Internal-only, VLAN/Tailscale path only  
> **TLS:** Phase 1 HTTP only; HTTPS reverse proxy later  
> **Install model:** Docker Compose inside unprivileged Debian 12 LXC

---

## 1. Purpose

This runbook documents the deployment of Zammad as the first ARIA platform workload. Zammad provides the ticketing interface for ARIA student training and the future AI Mentor workflow.

The deployment uses Docker Compose inside a dedicated unprivileged Debian 12 LXC container. This keeps the service portable, repeatable, backup-friendly, and aligned with the ARIA training-platform model.

---

## 2. As-Built Build Profile

| Item | Value |
|---|---|
| CT ID | `110` |
| Hostname | `aria-zammad-01` |
| OS | Debian 12 Bookworm |
| LXC type | Unprivileged |
| LXC features | Nesting enabled, keyctl enabled |
| CPU | 4 cores |
| RAM | 12 GB / `12288` MB |
| Swap | 4 GB / `4096` MB |
| Disk | 60 GB on `vmstore` |
| IP | `192.168.70.20/24` |
| Gateway | `192.168.70.1` |
| DNS | `192.168.10.16` |
| FQDN | `helpdesk.aria.local` |
| Install method | Docker Compose CLI |
| Source | Official `zammad/zammad-docker-compose` repository |
| Search backend | Bundled/default Elasticsearch container |
| Published port | `8080` |
| First validation ticket | Ticket-009: Zammad Ticket Triage |
| Backup | Proxmox CT snapshot backup completed |

---

## 3. Proxmox Host Prerequisite

Elasticsearch requires the host kernel `vm.max_map_count` value to be at least `262144`. Because LXC containers share the Proxmox host kernel, this must be checked on the Proxmox host, not inside the LXC.

Validated value:

```bash
cat /proc/sys/vm/max_map_count
```

Observed:

```text
1048576
```

Result: **PASS**. No change was required.

If the value is ever lower than `262144`, apply this on the Proxmox host:

```bash
sysctl -w vm.max_map_count=262144
cat >/etc/sysctl.d/99-zammad-elasticsearch.conf <<'EOF'
vm.max_map_count=262144
EOF
sysctl --system
cat /proc/sys/vm/max_map_count
```

Expected output:

```text
262144
```

---

## 4. Debian 12 Template

The Proxmox host initially only had Debian 13 downloaded locally. Debian 12 was available from the Proxmox template repository.

Template used:

```text
debian-12-standard_12.12-1_amd64.tar.zst
```

Download command:

```bash
pveam update
pveam download local debian-12-standard_12.12-1_amd64.tar.zst
```

---

## 5. LXC Creation Command

The container was created from the Proxmox host with:

```bash
pct create 110 local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst \
  --hostname aria-zammad-01 \
  --storage vmstore \
  --rootfs vmstore:60 \
  --cores 4 \
  --memory 12288 \
  --swap 4096 \
  --unprivileged 1 \
  --features nesting=1,keyctl=1 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.70.20/24,gw=192.168.70.1 \
  --nameserver 192.168.10.16 \
  --searchdomain aria.local \
  --onboot 1 \
  --start 1
```

Validated configuration:

```bash
pct status 110
pct config 110
```

Expected key values:

```text
status: running
hostname: aria-zammad-01
memory: 12288
swap: 4096
cores: 4
features: nesting=1,keyctl=1
net0: name=eth0,bridge=vmbr0,gw=192.168.70.1,ip=192.168.70.20/24,type=veth
rootfs: vmstore:vm-110-disk-0,size=60G
unprivileged: 1
```

---

## 6. LXC Network Validation

Inside CT 110:

```bash
pct enter 110
hostname
ip addr
ip route
cat /etc/resolv.conf
ping -c 4 192.168.70.1
ping -c 4 192.168.10.16
ping -c 4 1.1.1.1
ping -c 4 google.com
```

Validated results:

| Test | Result |
|---|---|
| Hostname `aria-zammad-01` | PASS |
| IP `192.168.70.20/24` | PASS |
| Gateway `192.168.70.1` | PASS |
| DNS server `192.168.10.16` | PASS |
| Internet by IP `1.1.1.1` | PASS |
| DNS resolution `google.com` | PASS |

---

## 7. Debian Update and Base Tools

Inside CT 110:

```bash
apt update
apt upgrade -y
apt install -y ca-certificates curl gnupg git nano htop lsb-release
cat /etc/os-release
```

Validated OS:

```text
Debian GNU/Linux 12 (bookworm)
```

---

## 8. Docker Installation

Inside CT 110:

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Validated versions:

```text
Docker version 29.5.3
Docker Compose version v5.1.4
Docker service active/running
```

Docker-in-LXC validation:

```bash
docker run --rm hello-world
```

Result: **PASS**.

---

## 9. Zammad Docker Compose Deployment

Inside CT 110:

```bash
mkdir -p /opt
cd /opt
git clone https://github.com/zammad/zammad-docker-compose.git
cd /opt/zammad-docker-compose
```

The stack was started with:

```bash
docker compose up -d
```

Validate stack status:

```bash
cd /opt/zammad-docker-compose
docker compose ps
```

Validated services:

```text
zammad-backup          Up
zammad-elasticsearch   Up
zammad-memcached       Up healthy
zammad-nginx           Up, 0.0.0.0:8080->8080/tcp
zammad-postgresql      Up healthy
zammad-railsserver     Up healthy
zammad-redis           Up healthy
zammad-scheduler       Up
zammad-websocket       Up
```

---

## 10. HTTP and DNS Validation

Inside CT 110:

```bash
curl -I http://localhost:8080
```

Result:

```text
HTTP/1.1 200 OK
Server: nginx
```

From a Mac/internal client:

```bash
curl -I http://192.168.70.20:8080
```

Result:

```text
HTTP/1.1 200 OK
```

Pi-hole local DNS record:

```text
helpdesk.aria.local -> 192.168.70.20
```

Validation:

```bash
nslookup helpdesk.aria.local 192.168.10.16
curl -I http://helpdesk.aria.local:8080
```

Result:

```text
Name: helpdesk.aria.local
Address: 192.168.70.20
HTTP/1.1 200 OK
```

Browser URL:

```text
http://helpdesk.aria.local:8080
```

---

## 11. Zammad Initial Setup Notes

Inbound email was intentionally skipped/deferred.

Reason: ARIA v1 uses manual web-based ticketing.

Current v1 workflow:

```text
Student logs into Zammad -> Student opens ticket manually -> Instructor reviews and responds -> Student updates ticket -> Ticket is closed
```

Deferred workflow:

```text
Email to helpdesk address -> Zammad automatically creates ticket
```

Do not configure Gmail IMAP/SMTP during v1 validation.

---

## 12. Organization, Group, and User Model

Organization created:

```text
JLM Lab Trainees
```

Organization settings:

```text
Shared Organization: yes
Domain Based Assignment: no
Domain: blank
VIP: no
Active: active
```

Ticket handling group:

```text
ARIA Help Desk
```

Important account model correction:

Zammad uses email-based login identifiers in this deployment. ARIA Linux/container usernames are not forced into Zammad login fields.

Use this mapping standard:

| System | Identifier |
|---|---|
| Linux/container username | Short username, e.g. `sprather` |
| Zammad login | Student email address |
| Zammad display name | Student real name |
| Zammad note/reference | Linux/container username |

Example:

```text
Linux/container username: sprather
Zammad login: sprath11@wgu.edu
Zammad display name: Sha Neal Prather
Zammad organization: JLM Lab Trainees
Zammad role: Customer
```

Admin account:

```text
Zammad login: admin email address
Zammad display name: Julius Moore
Role: Admin/Agent as needed
```

---

## 13. Ticket-009 Validation

First live validation ticket:

```text
Ticket-009: Zammad Ticket Triage
```

Validated workflow:

| Action | Result |
|---|---|
| Admin login | PASS |
| Student login | PASS |
| Student/admin ticket visibility | PASS |
| Ticket opened | PASS |
| Comments added | PASS |
| Ticket closed | PASS |
| Web UI via `helpdesk.aria.local:8080` | PASS |

Result: **Zammad v1 platform validation passed.**

---

## 14. Baseline Proxmox Backup

After validation, a Proxmox snapshot backup was taken from the Proxmox host:

```bash
vzdump 110 --mode snapshot --compress zstd --storage backup-vault
```

Observed result:

```text
INFO: Finished Backup of VM 110 (00:00:21)
INFO: Backup job finished successfully
```

Backup files:

```text
/mnt/backup/dump/vzdump-lxc-110-2026_06_07-19_50_49.log
/mnt/backup/dump/vzdump-lxc-110-2026_06_07-19_50_49.tar.zst
```

Archive size:

```text
2.8G
```

---

## 15. Operational Commands

Enter the container:

```bash
pct enter 110
```

Check Zammad stack:

```bash
cd /opt/zammad-docker-compose
docker compose ps
```

View logs:

```bash
cd /opt/zammad-docker-compose
docker compose logs -f
```

Restart stack:

```bash
cd /opt/zammad-docker-compose
docker compose restart
```

Stop stack:

```bash
cd /opt/zammad-docker-compose
docker compose down
```

Start stack:

```bash
cd /opt/zammad-docker-compose
docker compose up -d
```

Check web response:

```bash
curl -I http://localhost:8080
curl -I http://helpdesk.aria.local:8080
```

---

## 16. Security Notes

- Zammad is internal-only for v1.
- No public exposure.
- No port forwarding.
- No Cloudflare Tunnel or ngrok.
- TLS is deferred until after core workflow validation.
- Email inbound/outbound channels are deferred.
- Student accounts use customer-level permissions only unless specifically promoted for a lab.

---

## 17. Next Steps

1. Add Docker-level backup with PostgreSQL dump.
2. Document restore procedure.
3. Update `ROADMAP.md` to mark Zammad LXC deployed and validated.
4. Begin AI Mentor backend planning against the live Zammad service.
5. Add HTTPS reverse proxy after the platform workflow remains stable.

---

*Document created after live deployment validation: 2026-06-07*