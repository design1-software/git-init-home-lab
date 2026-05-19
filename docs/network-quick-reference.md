# JLM Home Lab — Network Quick Reference

> Keep this accurate. When IPs or ports change, update this first.
> Last verified: May 19, 2026.

---

## Network Infrastructure

| Device | IP / Access | VLAN | MAC | How to Reach |
|---|---|---|---|---|
| Cisco C1111 (JLM-LAB-R1) | 192.168.10.1 (SSH) | All (SVIs) | 44:AE:25:99:9D:80 | `ssh cisco` from Acer · `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.10.1` from Mac |
| GS308EP | 192.168.100.100 (web UI) | 1 (hardware limit) | 28:94:01:84:2D:8A | `http://192.168.100.100` — must be on VLAN 1 or route via C1111. DHCP reserved permanently. |
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
| Catalyst 3560CX (JLM-LAB-SW1) | Staged — not yet in production | — | — | Console cable · SSH after cutover |

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

> Phone and Android 7.0 tablet pending addition. Custom Proxmox server will be 7th node at Phase C.

---

## Cisco C1111 Port Map

| Port | Connected To | Mode | VLAN(s) |
|---|---|---|---|
| GE0/0/0 | XB8 WAN (public IP from Comcast) | DHCP client | Outside |
| GE0/1/0 | Acer Server | Access | 10 |
| GE0/1/1 | GS308EP Port 1 | Trunk (native 99) | 1,10,20,30,31,40,50,99 |
| GE0/1/2 | GS316EP Port 15 | Trunk (native 99) | 1,10,20,30,31,40,50,99 |
| GE0/1/3 | Available | — | — |

> At Phase B cutover: GE0/1/0 becomes TRANSIT L3 port (192.168.199.1/30). Acer moves to 3560CX port. GE0/1/1 becomes uplink to 3560CX.

---

## GS308EP Port Map (verified May 19, 2026)

**Management IP:** 192.168.100.100 (DHCP reserved)
**Firmware:** V2.0.0.5 · **Serial:** 6V665C53A4801

| Port | Device | PVID | VLANs |
|---|---|---|---|
| 1 | Trunk to Cisco GE0/1/1 | 99 | 1,10,20,30,31,40,50,99 |
| 2 | Spare | 1 | 1 |
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
| 15 | Trunk to Cisco GE0/1/2 | 1 | 1,10,20,30,31,40,99 |
| 16 | SFP (fiber only — do not use) | — | — |

> VLAN 50 (JM&G-GUEST) added May 19, 2026 — Port 15 carries all active VLANs.

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
| 199 | TRANSIT | 192.168.199.0/30 | — | — | None | ❌ Pending Phase B |

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
| SSH from Mac | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.10.1` |
| SSH from Acer | `ssh cisco` |
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

- **GS308EP and GS316EP web UIs** are on VLAN 1 (192.168.100.0/24). Your Mac is on VLAN 20. To reach the UIs, temporarily set a static IP on your Mac: `192.168.100.50`, subnet `255.255.255.0`, gateway `192.168.100.1`.
- **Cisco HTTP management UI** is accessible at `http://192.168.99.1` — disable this at Phase B cutover (hardening task).
- **3560CX** (JLM-LAB-SW1) is staged offline. Console access via USB-to-serial cable. SSH available after Phase B cutover.

---

*Last verified: May 19, 2026*