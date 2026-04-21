# JLM Home Lab — Device Quick Reference

> Print this. Keep it near your desk. Updated April 21, 2026.

---

## Network Infrastructure

| Device | IP / Access | VLAN | MAC | How to reach |
|---|---|---|---|---|
| Cisco C1111 | 192.168.10.1 (SSH) | All (SVIs) | 44:AE:25:99:9D:80 | `ssh cisco` from Acer, `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.10.1` from Mac |
| GS308EP | 192.168.100.100 (web) | 1 (floats) | 28:94:01:84:2D:8A | `http://192.168.100.100` from any browser |
| GS316EP | Floats on VLAN 1 (no stable IP) | 1 (floats) | 28:94:01:7F:A7:F7 | Check `show arp` or scan VLAN 1. May need physical access to find IP. |
| Pi 4B (Pi-hole) | 192.168.10.16 | 10 (SERVER) | 88:A2:9E:A8:33:C6 | `ssh admin@192.168.10.16` or `http://192.168.10.16/admin` |
| UniFi Controller | 192.168.10.16:8443 | 10 (SERVER) | (same as Pi) | `https://192.168.10.16:8443` |
| Acer Server | 192.168.10.17 | 10 (SERVER) | 40:C2:BA:E9:23:07 | Physical or RDP |
| UniFi AP #1 | DHCP on VLAN 99 | 99 (MGMT) | 6C:63:F8:A5:7C:1D | Via UniFi Controller |
| UniFi AP #2 | DHCP on VLAN 99 | 99 (MGMT) | 6C:63:F8:A5:73:AD | Via UniFi Controller |
| XB8 (bridge mode) | Not routable (modem only) | — | — | Physical access only. Factory reset: hold reset 30 sec |

---

## Cisco Port Map

| Port | Connected to | Mode | VLAN(s) |
|---|---|---|---|
| GE0/0/0 | XB8 WAN (public IP from Comcast) | DHCP client | Outside |
| GE0/1/0 | Acer Server | Access | 10 |
| GE0/1/1 | GS308EP Port 1 | Trunk | 1,10,20,30,31,40,50,99 |
| GE0/1/2 | GS316EP Port 15 | Trunk | 1,10,20,30,31,40,50,99 |
| GE0/1/3 | Available | — | — |

---

## GS308EP Port Map (FW V2.0.0.5, SN 6V665C53A4801)

| Port | Device | PVID | VLANs |
|---|---|---|---|
| 1 | Trunk to Cisco GE0/1/1 | 99 | 1(T),10(T),20(T),30(T),31(T),40(T),50(T),99(U) |
| 2 | Spare | 1 | 1(U) |
| 3 | Pi 4B (PoE) | 10 | 10(U) |
| 4 | UniFi AP #1 | 99 | 20(T),30(T),31(T),40(T),50(T),99(U) |
| 5 | UniFi AP #2 | 99 | 20(T),30(T),31(T),40(T),50(T),99(U) |
| 6-8 | Spare | 1 | 1(U) |

---

## GS316EP Port Map (MAC 28:94:01:7F:A7:F7)

| Port | Device | PVID | VLANs |
|---|---|---|---|
| 1 | Available (was XB8) | 1 | 1(U) |
| 2 | Apple TV Front-Bedroom | 20 | 20(U) |
| 3 | Apple TV Living-Room | 20 | 20(U) |
| 4 | Apple TV Master-Bedroom | 20 | 20(U) |
| 5-14 | Wall outlets (spare) | 1 | 1(U) |
| 15 | Trunk to Cisco GE0/1/2 | 99 | 1(T),10(T),20(T),30(T),31(T),40(T),99(U). VLAN 50 pending. |
| 16 | SFP (fiber only, not RJ-45) | — | Do not use |

---

## VLAN Summary

| VLAN | Name | Subnet | Gateway | SSID | ACL |
|---|---|---|---|---|---|
| 1 | DEFAULT | 192.168.100.0/24 | .1 | — | None (legacy) |
| 10 | SERVER | 192.168.10.0/24 | .1 | (wired) | None |
| 20 | TRUSTED | 192.168.20.0/24 | .1 | Gorgeous | None |
| 30 | IOT | 192.168.30.0/24 | .1 | Gorgeous-IoT | IOT-ACL |
| 31 | IOT-AUTO | 192.168.31.0/24 | .1 | Gorgeous-Auto | IOT-AUTO-ACL |
| 40 | HOUSEHOLD | 192.168.40.0/24 | .1 | Gorgeous-Home | HOUSEHOLD-ACL |
| 50 | GUEST | 192.168.50.0/24 | .1 | JM&G-GUEST | GUEST-ACL |
| 99 | MGMT | 192.168.99.0/24 | .1 | — | None |

---

## WiFi SSIDs

| SSID | VLAN | Purpose | Password |
|---|---|---|---|
| Gorgeous | 20 | Personal devices + family | (your password) |
| Gorgeous-IoT | 30 | Smart home devices | (your password) |
| Gorgeous-Auto | 31 | ESP32 automation | (your password) |
| Gorgeous-Home | 40 | Family internet-only | (your password) |
| JM&G-GUEST | 50 | Guest internet-only, client isolation | (guest password) |

---

## Key Commands

| Task | Command |
|---|---|
| SSH to Cisco from Acer | `ssh cisco` |
| SSH to Cisco from Mac | `ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa admin@192.168.10.1` |
| SSH to Pi | `ssh admin@192.168.10.16` |
| Pi-hole admin | `http://192.168.10.16/admin` |
| UniFi Controller | `https://192.168.10.16:8443` |
| GS308EP admin | `http://192.168.100.100` |
| Show all DHCP leases | `show ip dhcp binding` |
| Show MAC table | `show mac address-table` |
| Show trunk VLANs | `show interfaces Gi0/1/1 switchport \| include Trunking` |
| Show all ACLs | `show ip access-lists` |
| Save Cisco config | `write memory` |
| Find a device by MAC | `show mac address-table \| include <last4>` |
| Find a device IP by MAC | `show arp \| include <mac>` |

---

*Keep this document updated when IPs or ports change.*
