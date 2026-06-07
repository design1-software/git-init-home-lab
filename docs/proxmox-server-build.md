# Custom Proxmox Server Build — ARIA (Ryzen 9 7900X)

## Purpose

Dedicated hypervisor node for SERVER and LAB workloads in the home lab. Hostname: `pve`. Nickname: **ARIA**.

## Hardware

- Chassis: SAMA V40
- PSU: SL-650G (650W)
- CPU: Ryzen 9 7900X
- Motherboard: Gigabyte B650 GAMING X AX V2
- Cooler: Thermalright PA120 SE
- RAM: 64GB DDR5 UDIMM
- NVMe: WD Black SN770 2TB (vmstore)
- OS Drive: Samsung 860 EVO (Proxmox OS)
- Backup Vault: Samsung 860 EVO 458GB

## OS / Software

- **OS:** Debian 13 (trixie)
- **Proxmox VE:** 9.x (trixie-based — PVE 8.x was bookworm/Debian 12)
- **Repository:** `pve-no-subscription` — free community repo, correct for homelab; enterprise repo removed
- **Tailscale:** stable channel, trixie packages

## BIOS / Power Tuning

- BIOS PPT power cap completed in motherboard settings.
- Purpose: reduce heat, noise, and power draw while keeping enough compute headroom for Proxmox workloads.

## BIOS Findings (Jun 4, 2026)

### Platform Power (Settings → Platform Power)

| Setting | Current Value | Notes |
|---|---|---|
| AC BACK | Always Off | **Recommend: Memory** — ARIA returns to previous powered state after power loss |
| Keyboard Wake Up From S3 | Enabled | — |
| Mouse Wake Up From S3 | Enabled | — |
| ErP | Disabled | Required for WoL — ErP cuts standby NIC power after shutdown |
| Soft-Off by PWR-BTTN | Instant-Off | — |
| Resume by Alarm | Disabled | — |

> **ErP must remain Disabled.** If ErP is enabled, the NIC loses standby power and cannot receive Magic Packets after shutdown.

> **Recommended change**: Set AC BACK from `Always Off` to `Memory`. With Memory: if ARIA was on before a power loss, it powers back on when AC restores. If ARIA was intentionally off, it stays off.

### IO Ports (Settings → IO Ports)

| Finding | Value |
|---|---|
| Onboard LAN Controller | Enabled |
| Realtek PCIe 2.5GbE Family Controller | Detected |
| Realtek MAC | 10:FF:E0:C4:FA:A6 |
| PCIEX16 Bifurcation | Auto — **supported** |

> **PCIe bifurcation is supported** on this board. BIOS exposes `PCIEX16 Bifurcation: Auto` under IO Ports. No changes made — remains Auto. This contradicts prior information that the board did not support bifurcation.

## Storage Layout

- `/dev/sda`: Proxmox OS drive (Samsung 860 EVO)
- `vmstore`: WD Black SN770 2TB NVMe, LVM-thin, approximately 1.8TB
- `backup-vault`: Samsung 860 EVO, approximately 458GB

## Network

### Current State (Jun 5, 2026) — VLAN 70 Active

```
Hostname: pve
IP:       192.168.70.10/24
Gateway:  192.168.70.1 (3560CX HSRP VIP, VLAN 70)
DNS:      192.168.10.16 (Pi-hole, VLAN 10)
NIC:      nic1 (Intel I225V — physical uplink, no IP)
Bridge:   vmbr0 (Proxmox management bridge)
MAC:      00:1B:41:0A:05:09
Port:     3560CX Gi0/4 (access VLAN 70)
```

ARIA `/etc/network/interfaces`:

```
auto lo
iface lo inet loopback

auto nic1
iface nic1 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.70.10/24
    gateway 192.168.70.1
    dns-nameservers 192.168.10.16
    bridge-ports nic1
    bridge-stp off
    bridge-fd 0

auto nic0
iface nic0 inet manual
```

### NIC Identification

| NIC | Driver | MAC | Role | Status |
|---|---|---|---|---|
| nic1 | Intel I225V | 00:1B:41:0A:05:09 | Proxmox management (active) | In use — 3560CX Gi0/4 |
| nic0 | Realtek RTL8125 2.5GbE | 10:FF:E0:C4:FA:A6 | Future VM trunk | Manual (unused) |

> The Realtek NIC (`nic0`) is the onboard controller visible in BIOS. It was briefly connected to the wrong switchport during initial cabling — the 3560CX learned MAC `10:ff:e0:c4:fa:a6` before the cable was moved to the correct Intel NIC (`nic1`).

### Target State (Post-Phase-C Cutover)

- VLAN: 70 (SERVER, 192.168.70.0/24)
- IP: `192.168.70.10/24`
- Gateway: `192.168.70.1` (3560CX HSRP VIP)
- DNS: `192.168.10.16`
- Switch port: 3560CX Gi0/4 (trunk)
- Proxmox bridge: `vmbr0` on nic1

## Out-of-Band Management — Comet GL-RM1PE KVM

### Current Status (Jun 5, 2026)

| Item | Status |
|---|---|
| Comet powered by PoE | ✅ 3560CX Gi0/5 · 15.4W |
| Comet dashboard | ✅ `http://192.168.100.11` · `https://192.168.100.11` |
| Comet KVM video | ✅ PASS |
| Comet keyboard input | ✅ PASS |
| Comet BIOS/UEFI access | ✅ PASS — entered Gigabyte BIOS via Comet |
| ATX control board | ✅ Replacement GL-ATXPC installed Jun 5, 2026 |
| ATX board detected in Comet UI | ✅ PASS |
| Comet remote power-on | ✅ PASS — ARIA boots, returns to network, ARP resolves |
| Comet remote reset | ⚠️ NOT WIRED — SAMA V40 has no physical reset button; reset circuit not connected to B650 reset pins. Recovery uses force power-off + power-on. Not a blocker. |
| Physical power button (SAMA V40) | ✅ PASS — still functional through ATX board |
| WoL (secondary path) | ✅ PASS |
| **ATX Gate** | **PASSED WITH NOTE ✅ (Jun 5, 2026)** |

### Comet Device Details

```
Device:    Comet GL-RM1PE
IP:        192.168.10.12
MAC:       94:83:C4:D0:C7:BF
Switchport: 3560CX Gi0/5 (access VLAN 10)
VLAN:      10 (MGMT — permanent)
Power:     PoE from 3560CX (15.4W, IEEE PD)
Access:    http://192.168.10.12 or https://192.168.10.12
```

### Cabling

```
3560CX Gi0/4  →  ARIA management NIC (nic1, Intel I225V)
3560CX Gi0/5  →  Comet GL-RM1PE PoE Ethernet

Comet HDMI input  ←  ARIA video output
Comet USB         ←  ARIA USB port
```

### ATX Control Board Status

Replacement GL-ATXPC installed Jun 5, 2026. ATX Gate: **PASSED WITH NOTE**.

| Capability | Result |
|---|---|
| Remote power-on via Comet | ✅ PASS |
| Remote power-off via Comet | ✅ PASS |
| Remote reset via Comet | ⚠️ NOT WIRED — SAMA V40 has no physical reset button; reset circuit not connected to B650 reset pins |
| Physical power button passthrough | ✅ PASS — case button still functional |
| WoL (secondary power-on path) | ✅ PASS |

> **Reset note:** The SAMA V40 case has no reset button, so the ATX board reset relay has no circuit to intercept. A hard reset requires force power-off via Comet followed by power-on. This is sufficient for all expected recovery scenarios.

### 3560CX Port Configuration

**Gi0/4 — ARIA (temporary VLAN 1 access)**:

```cisco
interface GigabitEthernet0/4
 description ARIA-PROXMOX-TEMP-VLAN1
 switchport mode access
 spanning-tree portfast edge
 spanning-tree bpduguard enable
end
```

Stale trunk and security settings removed during setup:
```cisco
no switchport trunk allowed vlan
no switchport trunk native vlan
no ip arp inspection trust
no ip dhcp snooping trust
no ip verify source
switchport mode access
switchport access vlan 1
```

**Gi0/5 — Comet KVM (PoE, temporary VLAN 1)**:

```cisco
interface GigabitEthernet0/5
 description COMET-KVM-TEMP-VLAN1-POE
 switchport mode access
 spanning-tree portfast edge
 spanning-tree bpduguard enable
end
```

> `ip verify source` was removed from Gi0/5 to prevent IP Source Guard from blocking the Comet during DHCP/WoL testing.

### Final Architecture (Jun 5, 2026) ✅

```
Comet → VLAN 10 MGMT · 192.168.10.12 · 3560CX Gi0/5 (PoE)
ARIA  → VLAN 70 SERVER · 192.168.70.10 · 3560CX Gi0/4
ATX board → Gigabyte B650 F_PANEL header + SAMA V40 front-panel wiring
Comet USB-C → ATX board (power relay active · reset not wired — SAMA V40 has no reset button)
```

## Wake-on-LAN Configuration

### Status

```
NIC:   nic1 (Intel I225V)
MAC:   00:1B:41:0A:05:09
WoL:   Enabled (Magic Packet — wol g)
ErP:   Disabled in BIOS (required)
```

### ethtool Validation

```bash
ethtool nic1 | grep -i wake
```

Output:
```
Supports Wake-on: pumbg
Wake-on: g
```

`g` = Magic Packet wake enabled.

### Persistent WoL — systemd Service

`/etc/systemd/system/wol.service`:

```ini
[Unit]
Description=Enable Wake-on-LAN for ARIA Proxmox NIC nic1
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/ethtool -s nic1 wol g

[Install]
WantedBy=multi-user.target
```

Commands used:
```bash
systemctl daemon-reload
systemctl enable wol.service
systemctl start wol.service
systemctl is-enabled wol.service   # → enabled
```

> `Type=oneshot` services show as `inactive (dead)` after completion — this is expected. The setting is applied once on boot and persists until the NIC loses power.

### WoL Test Result (Jun 4, 2026)

1. ARIA shut down cleanly
2. Comet sent Magic Packet to `00:1B:41:0A:05:09`
3. ARIA powered on, ping to `192.168.100.10` successful

```
Comet Wake-on-LAN power-on path for ARIA: PASS ✅
```

### WoL Limitations

WoL cannot recover from: frozen kernel, hung motherboard, NIC lockup, hard crash, or OS-level deadlock. The ATX control board is still required for hard power cycle and reset relay.

## System Fixes (Jun 4, 2026)

| Issue | Status |
|---|---|
| Internet egress | ✅ Fixed |
| apt IPv4 preference | ✅ Fixed — `/etc/apt/apt.conf.d/99force-ipv4` |
| Proxmox repo mismatch | ✅ Fixed — corrected to `pve-no-subscription` on trixie |
| Enterprise repo 401 errors | ✅ Fixed — enterprise repo entry removed |
| Package upgrades | ⏳ Deferred — intentional; hold until ATX control board is installed and hard reset path is validated |

> Package upgrades are deferred because a kernel or Proxmox update could render ARIA unreachable and WoL cannot recover from a mid-upgrade kernel panic or boot failure. The ATX board's hard reset relay is the required safety net before running `apt upgrade`.

## Cutover Checklist

### Build and Base Install

- [x] Assemble custom ATX server
- [x] Install Proxmox VE bare metal
- [x] Install 64GB DDR5 RAM
- [x] Install WD Black SN770 2TB NVMe
- [x] Confirm Proxmox UI at `192.168.100.10:8006`
- [x] Add Proxmox host to Tailscale mesh (`pve`, 100.71.239.21)
- [x] Complete BIOS PPT power cap in motherboard settings

### Comet KVM + WoL (Phase C.1)

- [x] Configure 3560CX Gi0/4 as temporary ARIA VLAN 1 access port
- [x] Configure 3560CX Gi0/5 as temporary Comet PoE VLAN 1 access port
- [x] Confirm Comet powered by PoE (15.4W)
- [x] Confirm Comet dashboard at `http://192.168.100.11`
- [x] Confirm Comet video, keyboard, and BIOS access to ARIA
- [x] Identify ARIA management NIC as `nic1` (Intel I225V, `00:1B:41:0A:05:09`)
- [x] Confirm ARIA reachable at `192.168.100.10`
- [x] Confirm BIOS ErP Disabled (required for WoL)
- [x] Enable persistent WoL via systemd `wol.service`
- [x] Confirm Wake-on-LAN power-on from Comet: PASS
- [x] Install replacement GL-ATXPC / ATX control board (Jun 5, 2026)
- [x] Connect ATX board to B650 F_PANEL header + SAMA V40 front panel (Jun 5, 2026)
- [x] Connect Comet USB-C to ATX board (Jun 5, 2026)
- [x] Validate Comet remote power-on — PASS (Jun 5, 2026)
- [x] Validate physical power button still works — PASS (Jun 5, 2026)
- [ ] Validate Comet reset action — NOT WIRED (SAMA V40 has no reset button); not a blocker
- **ATX Gate: PASSED WITH NOTE ✅ (Jun 5, 2026)**

### VLAN 70 Cutover (Phase C)

**Pre-migration recovery paths — all confirmed (Jun 5, 2026):**
- [x] Comet KVM video/keyboard — PASS
- [x] Comet ATX remote power-on — PASS
- [x] Tailscale SSH to `pve` (100.71.239.21) — PASS · 0% packet loss · SSH successful from Mac

- [x] Configure Proxmox `vmbr0` bridge — nic1 = physical uplink (no IP), vmbr0 = management bridge (Jun 5, 2026)
- [x] Move ARIA from VLAN 1 to VLAN 70 — 192.168.70.10/24 · ping + ARP + internet PASS (Jun 5, 2026)
- [x] C1111 NAT ACL updated — 192.168.70.0/24 added to PAT overload rule (Jun 5, 2026)
- [x] Move Comet from VLAN 1 to VLAN 10 MGMT — 192.168.10.12 · PoE + KVM + ATX UI all PASS (Jun 5, 2026)
- [x] Verify Proxmox UI at `https://192.168.70.10:8006` — PASS (Jun 5, 2026)
- [x] Verify Tailscale online after VLAN 70 cutover — PASS (Jun 5, 2026)
- [x] Deploy first LXC container — CT 101 `lab-linux-01` · 192.168.70.11/24 · VLAN 70 · internet PASS · vmbr0 bridge validated (Jun 5, 2026)
- [x] CT 101 converted to Debian 13 baseline LXC template — student containers cloned from template; troubleshooting tools added to clones, not to template (Jun 5, 2026)

## Training Access Model

Three distinct access tiers on ARIA. The boundary between them is enforced — not advisory.

| Tier | Scope | Who |
|---|---|---|
| root | Proxmox host administration · template creation · networking changes · recovery actions · instructor-only maintenance | Julius only (host level) |
| julius (per container) | Instructor access inside each container · observe student work · assist or demonstrate · SSH key auth | Julius (container level) |
| student accounts | Linux practice · troubleshooting commands · ticket evidence gathering · service checks · controlled sudo tasks | Students |
| AI Mentor | Guides students within their assigned tier · asks for evidence · explains commands · does not hand out unrestricted root workflows | AI |

**Rule:** Every training container must have both a `julius` instructor account and the assigned student account created at deployment. The `julius` account uses SSH key authentication (`~/.ssh/aria_julius_ed25519`). The `root` account on the Proxmox host is separate and reserved for host-level operations only.

### Instructor SSH Config Pattern

Add to `~/.ssh/config` on the instructor machine for each container:

```text
Host aria-student-linux-01
    HostName 100.125.65.78
    User julius
    IdentityFile ~/.ssh/aria_julius_ed25519
    IdentitiesOnly yes
```

Connect with: `ssh aria-student-linux-01`

---

## LXC Templates

| Template | Base OS | Purpose |
|---|---|---|
| lab-linux-01 | Debian 13 (trixie) | Baseline student LXC — clone to deploy lab containers |

## Active LXC Containers

| CT ID | Name | IP | Accounts | Purpose |
|---|---|---|---|---|
| 102 | student-linux-01 | 192.168.70.12 | sprather (student) · julius (instructor) | First student Linux troubleshooting endpoint · SSH + sudo validated · Field Tech Lab 001 complete |

**Template approach:** baseline template contains only the OS and minimal configuration. Troubleshooting tools, lab-specific packages, and any scenario setup are added to clones after deployment — not to the template itself. Future template rebuilds may include a curated baseline toolset before conversion.

---

## Planned First Workloads

**On ARIA (VLAN 70 — pending cutover):**
- Wazuh SIEM (security telemetry)
- Prometheus + Grafana (infrastructure telemetry — Cisco SNMP, Proxmox host, Pi/Acer system metrics)
- snmp_exporter (C1111 + 3560CX interface stats, CPU, memory, PoE)
- node_exporter on ARIA host (system metrics exported to Prometheus)
- Active Directory lab VM (forest: jlm.lab)
- Zammad help desk VM (AI Mentor ticketing platform)
- AI Mentor backend (FastAPI + ChromaDB vector store)

**On Pi (no ARIA dependency — can deploy now):**
- NetAlertX (network presence / device discovery)
- ntfy (self-hosted push notifications — future unified alert routing)
- node_exporter on Pi (system metrics exported to ARIA Prometheus)

## Rollback Plan

If the VLAN 70 cutover fails:

1. Access ARIA via Comet GL-RM1PE KVM console.
2. Restore previous `/etc/network/interfaces`.
3. Reconnect to VLAN 1 path if needed.
4. Reboot or reload networking from console.
5. Confirm Tailscale recovery path (`pve`, 100.71.239.21).
