# Phase D VLAN 60 End-to-End Validation

## Status

Phase D VLAN 60 is fully proven end-to-end.

## Validated Path

LXC container on vmbr1
  -> untagged frames
nic0 10:ff:e0:c4:fa:a6
  -> Cat6
3560CX Gi0/6 access VLAN 60
  -> Vlan60 SVI 192.168.60.1
  -> LAB-ACL inbound
  -> DHCP snooping + DAI + IP Source Guard
  -> 3560CX OSPF area 0
  -> 192.168.199.0/30 transit
  -> C1111 OSPF + NAT inside for 192.168.60.0/24
  -> GigabitEthernet0/0/0
  -> WAN 174.53.28.46
  -> Internet

## Bridge Mapping

| Purpose | Bridge | Physical NIC | Switch Port | VLAN |
|---|---|---|---|---|
| Proxmox management | vmbr0 | nic1 | Gi0/4 | Access VLAN 70 |
| AD/IAM lab workloads | vmbr1 | nic0 | Gi0/6 | Access VLAN 60 |

## Design Decision

VLAN 60 is carried through a dedicated Proxmox workload bridge instead of the Proxmox management uplink.

This design avoids risking Proxmox management connectivity while still giving lab workloads a clean VLAN 60 path.

## Operational Notes

- Gi0/4 should remain access VLAN 70 for Proxmox management.
- Gi0/6 should remain access VLAN 60 for lab workloads.
- Guests attached to vmbr1 should normally be untagged.
- Do not add VLAN tag 60 inside Proxmox guests while Gi0/6 is configured as an access VLAN 60 port.
- VLAN 60 is ready for JLM-DC01 and JLM-WIN01 deployment.
