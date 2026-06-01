# Custom Proxmox Server Build — Ryzen 9 7900X

## Purpose

Dedicated hypervisor node for SERVER and LAB workloads in the home lab.

## Hardware

- Chassis: SAMA V40
- PSU: SL-650G
- CPU: Ryzen 9 7900X
- Motherboard: B650
- Cooler: Thermalright PA120 SE
- RAM: 64GB DDR5 UDIMM
- NVMe: WD Black SN770 2TB
- OS Drive: Samsung 860 EVO
- Backup Vault: Samsung 860 EVO 458GB

## BIOS / Power Tuning

- BIOS PPT power cap completed in motherboard settings.
- Purpose: reduce heat, noise, and power draw while keeping enough compute headroom for Proxmox workloads.

## Storage Layout

- `/dev/sda`: Proxmox OS drive
- `vmstore`: WD Black SN770 2TB NVMe, LVM-thin, approximately 1.8TB
- `backup-vault`: Samsung 860 EVO, approximately 458GB

## Network

Current state:

- Hostname: `pve`
- Current LAN IP: `192.168.100.10`
- Proxmox UI: `https://192.168.100.10:8006`
- Tailscale: `pve / 100.71.239.21`

Target state:

- Management VLAN: VLAN 70 SERVER
- Target IP: `192.168.70.10/24`
- Gateway: `192.168.70.1`
- DNS: `192.168.10.16`
- Switch port: Catalyst 3560CX Gi0/4 trunk

## NIC Plan

- Intel I225V: Proxmox management uplink
- Realtek RTL8125: future VM trunk or secondary uplink

## Out-of-Band Management

Planned addition:

- Comet GL-RM1PE KVM
- ATX board integration
- BIOS-level remote console access
- Proxmox console recovery during VLAN changes or network lockout events

## Cutover Checklist

- [x] Build custom ATX server
- [x] Install Proxmox VE bare metal
- [x] Install 64GB DDR5 RAM
- [x] Install WD Black SN770 2TB NVMe
- [x] Confirm Proxmox UI at `192.168.100.10:8006`
- [x] Add Proxmox host to Tailscale mesh
- [x] Complete BIOS PPT power cap in motherboard settings
- [ ] Add Comet GL-RM1PE KVM
- [ ] Validate KVM remote console access
- [ ] Cable server to 3560CX Gi0/4
- [ ] Configure Proxmox VLAN-aware bridge
- [ ] Move Proxmox management to VLAN 70
- [ ] Verify Proxmox UI at `192.168.70.10:8006`
- [ ] Verify Tailscale fallback after VLAN 70 cutover
- [ ] Deploy first VM or LXC workload

## Planned First Workloads

- Wazuh SIEM
- Netdata
- NetAlertX
- ntfy
- Active Directory lab VM
- osTicket lab VM

## Rollback Plan

If the VLAN 70 cutover fails:

1. Use Comet GL-RM1PE KVM console or local keyboard/monitor.
2. Restore the previous `/etc/network/interfaces` backup.
3. Reconnect to legacy VLAN 1 path if needed.
4. Reboot or reload networking from console.
5. Confirm Tailscale recovery path.
