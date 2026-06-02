# JLM Home Lab — Network Quick Reference

> Keep this accurate. When IPs or ports change, update this first.
> Last verified: May 19, 2026.

---

## Network Infrastructure

| Device | IP / Access | VLAN | MAC | How to Reach |
|---|---|---|---|---|
| Cisco C1111 (JLM-LAB-R1) | 192.168.199.1 (SSH — TRANSIT SVI) | All (SVIs) | 44:AE:25:99:9D:80 | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.199.1` — 192.168.10.1 is now the 3560CX HSRP VIP |
| GS308EP | 192.168.100.95 (web UI) | 1 (hardware limit) | 28:94:01:84:2D:8A | `http://192.168.100.95` — must be on VLAN 1 or route via C1111. DHCP reserved permanently. |
| GS316EP | 192.168.100.96 (web UI) | 1 (hardware limit) | 28:94:01:7F:A7:F7 | `http://192.168.100.96` — must be on VLAN 1 or route via C1111. DHCP, no reservation set. |
| Pi 4B | 192.168.10.16 | 10 (MGMT) | 88:A2:9E:A8:33:C6 | `ssh admin@192.168.10.16` |
| Pi-hole | 192.168.10.16/admin | 10 (MGMT) | (same as Pi) | `http://192.168.10.16/admin` |
| UniFi Controller | 192.168.10.16:8443 | 10 (MGMT) | (same as Pi) | `https://192.168.10.16:8443` |
| Mosquitto MQTT | 192.168.10.16:1883 | 10 (MGMT) | (same as Pi) | `mosquitto_sub -h 192.168.10.16 -t '#'` |
| CUPS Print Server | 192.168.10.16:631 | 10 (MGMT) | (same as Pi) | `http://192.168.10.16:631` (admin from VLAN 20 only) |
| HP ENVY Inspire 7200e | DHCP on VLAN 30 | 30 (IOT) | 7C:4D:8F:BE:B1:EC | Print via CUPS: `ipp://192.168.10.16:631/printers/HP_Envy_Lab` |
| Acer Server | 192.168.10.11 | 10 (MGMT) | 40:C2:BA:E9:23:07 | Physical · RDP · Tailscale (100.113.164.125) |
| UniFi AP #1 | 192.168.99.12 | 99 (MGMT/NATIVE) | 6C:63:F8:A5:7C:1D | Via UniFi Controller |
| UniFi AP #2 | 192.168.99.11 | 99 (MGMT/NATIVE) | 6C:63:F8:A5:73:AD | Via UniFi Controller |
| XB8 (bridge mode) | Not routable (modem only) | — | — | Physical access only. Factory reset: hold reset 30 sec |
| Catalyst 3560CX (JLM-LAB-SW1) | 192.168.10.1 (HSRP VIP) / 192.168.199.2 (SSH) | All production VLANs | — | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.199.2` |
| Proxmox Server (pve) | 192.168.100.10 :8006 (web UI) | 1 (VLAN 70 cabling pending) | — | `https://192.168.100.10:8006` · Tailscale 100.71.239.21 |

---

## Tailscale Nodes

| Device | Hostname | Tailscale IP | OS |
|---|---|---|---|
| MacBook Pro | juliuss-macbook-pro | 100.111.203.45 | macOS |
| Acer Server | jmg-server | 100.113.164.125 | Windows 11 25H2 |
| Pi 4B | jlm-lab-pi | 100.122.55.14 | Linux |
| iMac | juliuss-imac | 100.75.3.82 | macOS |
| Desktop | desktop-opm9863 | 100.87.58.10 | Windows 10 |
| MacBook Air | macbook-air | 100.102.47.66 | macOS |
| Proxmox Server | pve | 100.71.239.21 | Linux (Proxmox VE) |
| Desktop (Windows) | jm-swe | 100.74.46.90 | Windows |

> Phone and Android 7.0 tablet pending addition.

---

## Cisco C1111 Port Map

| Port | Connected To | Mode | VLAN(s) |
|---|---|---|---|
| GE0/0/0 | XB8 WAN (public IP from Comcast) | DHCP client | Outside |
| GE0/1/0 | 3560CX Gi0/1 | Access | 199 (TRANSIT) |
| GE0/1/1 | Available (trunk moved to 3560CX Gi0/2) | — | — |
| GE0/1/2 | Available (trunk moved to 3560CX Gi0/3) | — | — |
| GE0/1/3 | Available | — | — |

> **Phase B trunk cutover COMPLETE (Jun 1, 2026).** 3560CX is the active L3 core. HSRP VIPs active. OSPF FULL. Internet and DNS verified. **Post-cutover cleanup remaining:** remove C1111 VLAN SVIs/DHCP pools, remove 3560CX static default. **Cleanup backlog:** GS308EP DHCP reservation stuck in Selecting (reachable at .95). See also: docs/runbooks/ssh-key-collision.md for SSH host key issues after gateway IP handoffs.

---

## Catalyst 3560CX Port Map (verified Jun 1, 2026)

**Hostname:** JLM-LAB-SW1 · **SSH:** `admin@192.168.199.2`

| Port | Connected To | Mode | Role |
|---|---|---|---|
| Gi0/1 | C1111 GE0/1/0 | Routed (no switchport) | TRANSIT — 192.168.199.2/30 |
| Gi0/2 | GS308EP Port 1 | Trunk | Production access-layer switch |
| Gi0/3 | GS316EP Port 15 | Trunk | Household access-layer switch |
| Gi0/4 | Proxmox Server | Trunk (reserved) | Currently down — Proxmox VLAN 70 cabling pending |

---

## GS308EP Port Map (verified Jun 1, 2026)

**Management IP:** 192.168.100.95 (DHCP reserved)
**Firmware:** V2.0.0.5 · **Serial:** 6V665C53A4801

| Port | Device | PVID | VLANs |
|---|---|---|---|
| 1 | Trunk to 3560CX Gi0/2 | 99 | 1,10,20,30,31,40,50,99 |
| 2 | Acer Server (192.168.10.11) | 10 | 10 |
| 3 | Pi 4B (PoE) | 10 | 10 |
| 4 | UniFi AP #1 | 99 | 20,30,31,40,50,99 |
| 5 | UniFi AP #2 | 99 | 20,30,31,40,50,99 |
| 6 | Spare | 1 | 1 |
| 7 | Spare | 1 | 1 |
| 8 | Spare | 1 | 1 |

---

## GS316EP Port Map (verified May 19, 2026)

**Management IP:** 192.168.100.96 (DHCP, no reservation)
**MAC:** 28:94:01:7F:A7:F7

| Port | Device | PVID | VLANs |
|---|---|---|---|
| 1 | Spare | 1 | 1 |
| 2 | Apple TV (Front Bedroom) | 20 | 20 |
| 3 | Apple TV (Living Room) | 20 | 20 |
| 4 | Apple TV (Master Bedroom) | 20 | 20 |
| 5–14 | Wall outlets (spare) | 1 | 1 |
| 15 | Trunk to 3560CX Gi0/3 | 1 | 1,10,20,30,31,40,99 |
| 16 | SFP slot — empty, not in use | — | — |

> VLAN 50 (JM&G-GUEST) added May 19, 2026 — Port 15 carries all active VLANs.

> **Port 16 — SFP slot:** Mini-GBIC expansion port. Accepts a fiber SFP transceiver (1000BASE-SX/LX) or a compatible copper SFP (1000BASE-T). Currently empty — no module inserted. Not connected to anything. Reserved for future fiber uplink if a longer run is ever needed (e.g., cross-building or basement-to-floor fiber drop). Do not insert a copper SFP and expect PoE — this slot has no PoE budget.

---

## VLAN Summary

| VLAN | Name | Subnet | Gateway | SSID | ACL | Status |
|---|---|---|---|---|---|---|
| 1 | DEFAULT | 192.168.100.0/24 | .1 | — | None | ✅ Active (legacy, retirement planned) |
| 10 | MGMT | 192.168.10.0/24 | .1 | (wired) | None | ✅ Active |
| 20 | TRUSTED | 192.168.20.0/24 | .1 | Gorgeous | None | ✅ Active |
| 30 | IOT | 192.168.30.0/24 | .1 | Gorgeous-IoT | IOT-ACL | ✅ Active |
| 31 | IOT-AUTO | 192.168.31.0/24 | .1 | Gorgeous-Auto | IOT-AUTO-ACL | ✅ Active |
| 40 | HOUSEHOLD | 192.168.40.0/24 | .1 | Gorgeous-Home | HOUSEHOLD-ACL | ✅ Active |
| 50 | JM&G-GUEST | 192.168.50.0/24 | .1 | JM&G-GUEST | GUEST-ACL | ✅ Active |
| 99 | MGMT/NATIVE | 192.168.99.0/24 | .1 | — | None | ✅ Active (native on trunks) |
| 60 | LAB | 192.168.60.0/24 | .1 | — | TBD | ❌ Pending Phase D |
| 70 | SERVER | 192.168.70.0/24 | .1 | — | TBD | ❌ Pending Phase C |
| 199 | TRANSIT | 192.168.199.0/30 | — | — | None | ✅ Active Phase B — routed transit C1111 ↔ 3560CX, OSPFv2 FULL |

---

## WiFi SSIDs

| SSID | VLAN | Purpose |
|---|---|---|
| Gorgeous | 20 | Personal devices |
| Gorgeous-IoT | 30 | Smart home devices |
| Gorgeous-Auto | 31 | ESP32 automation |
| Gorgeous-Home | 40 | Family internet-only |
| JM&G-GUEST | 50 | Guest internet-only, client isolation |

---

## Key Commands

### Cisco C1111

| Task | Command |
|---|---|
| SSH from Mac | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.199.1` |
| Note | `192.168.10.1` is now the 3560CX HSRP VIP — use TRANSIT SVI `192.168.199.1` to reach C1111 directly |
| SSH from Acer | `ssh cisco` |

### Catalyst 3560CX (JLM-LAB-SW1)

| Task | Command |
|---|---|
| SSH from Mac (alias) | `ssh jlm-lab-sw1` |
| SSH from Mac (explicit) | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group-exchange-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.199.2` |

> 3560CX offers both `diffie-hellman-group14-sha1` and `diffie-hellman-group-exchange-sha1` — both must be permitted. The C1111 only requires `group14-sha1`.
| Show all DHCP leases | `show ip dhcp binding` |
| Show MAC table | `show mac address-table` |
| Show trunk VLANs | `show interfaces trunk` |
| Show all ACLs | `show ip access-lists` |
| Show interface status | `show ip interface brief` |
| Show ARP table | `show arp` |
| Find device by MAC | `show arp \| include <mac>` |
| Save config | `write memory` |
| Enter config mode | `configure terminal` |

### Pi (192.168.10.16)

| Task | Command |
|---|---|
| SSH to Pi | `ssh admin@192.168.10.16` |
| Pi-hole admin | `http://192.168.10.16/admin` |
| UniFi Controller | `https://192.168.10.16:8443` |
| CUPS admin | `http://192.168.10.16:631` |
| Subscribe to all MQTT | `mosquitto_sub -h 192.168.10.16 -t '#'` |
| Print test page | `lp -d HP_Envy_Lab /usr/share/cups/data/default-testpage.pdf` |

### Acer Server (192.168.10.11)

| Task | Command |
|---|---|
| Start MCP stack | `cd C:\Users\jbm06\social-media-mcp && docker compose up -d` |
| Check Docker status | `docker compose ps` |
| View Docker logs | `docker compose logs --tail=100 -f` |
| Restart Docker stack | `docker compose restart` |
| Rebuild after code change | `docker compose down && docker compose build && docker compose up -d` |

### Network Troubleshooting

| Task | Command |
|---|---|
| Find device IP by MAC (Cisco) | `show arp \| include <mac>` |
| Find device by partial MAC | `show mac address-table \| include <last4>` |
| Scan subnet from Mac | `for i in {1..254}; do ping -c 1 -W 1 192.168.X.$i > /dev/null 2>&1 && echo "192.168.X.$i is up"; done` |
| Check ARP from Mac | `arp -a \| grep -v incomplete` |
| Reach VLAN 1 devices from Mac | Temporarily set static IP 192.168.100.x/24 GW 192.168.100.1 on Mac |

---

## Access Notes

- **GS308EP and GS316EP web UIs** are on VLAN 1 (192.168.100.0/24). The C1111 routes between VLAN 20 and VLAN 1 — reach them directly at `http://192.168.100.95` (GS308EP) and `http://192.168.100.96` (GS316EP) from any routed VLAN. No static IP workaround needed.
- **Cisco HTTP management UI** is accessible at `http://192.168.99.1` — disable this at Phase B cutover (hardening task).
- **3560CX** (JLM-LAB-SW1) — Active L3 core. SSH at `192.168.199.2` (TRANSIT SVI). Gi0/1 = routed TRANSIT to C1111 · Gi0/2 = trunk to GS308EP · Gi0/3 = trunk to GS316EP · Gi0/4 = reserved for Proxmox (currently down).

---

*Last verified: May 31, 2026*
