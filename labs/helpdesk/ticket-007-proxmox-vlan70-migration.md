# Helpdesk Ticket 007 — Proxmox VLAN 70 Migration

**Domain:** Proxmox / Networking / VLAN
**Difficulty:** Advanced
**Estimated time:** 60–90 minutes
**Status:** Live validation complete — Jun 5, 2026 — ARIA on VLAN 70 · 192.168.70.10 · vmbr0 bridge active · ping + ARP + web UI all PASS

---

## Scenario

A student is assigned the task of migrating the Proxmox server (ARIA) from its temporary VLAN 1 address (`192.168.100.10`) to its permanent VLAN 70 address (`192.168.70.10/24`). The Comet KVM and ATX board are confirmed operational. The 3560CX has VLAN 70 pre-staged.

The student must complete this migration without permanently losing Proxmox access. If networking is misconfigured, the Comet console is the recovery path.

---

## Ticket Details

**Reported by:** Lab instructor (assigned task, not a break/fix)
**Affected system:** ARIA Proxmox host — network migration
**Priority:** High (maintenance window task)
**Category:** Proxmox — Network Migration

---

## Pre-Migration Checklist (AI Mentor enforces this)

Before the mentor provides any migration steps, the student must confirm:

```
1. Comet KVM is operational and ARIA console is visible
2. ATX board is installed and hard reset is validated (see ticket-008)
3. Tailscale is active on ARIA — fallback path confirmed (pve / 100.71.239.21)
4. configs/ has a current Proxmox network snapshot
5. VLAN 70 SVI is up on 3560CX (show interface Vlan70 on switch)
6. 3560CX Gi0/4 is configured as VLAN 70 trunk port (not access port)
```

If any item is not confirmed, the mentor stops and requires it before proceeding.

---

## AI Mentor Opening Questions

```
1. Is the Comet KVM console showing ARIA's desktop or terminal right now?
2. Can you confirm Tailscale is connected on ARIA?
   (tailscale status | grep pve)
3. What is the current /etc/network/interfaces on ARIA?
   (cat /etc/network/interfaces)
4. What does 3560CX show for Gi0/4?
   (show interface GigabitEthernet0/4 status)
5. What does 3560CX show for Vlan70?
   (show interface Vlan70)
```

---

## Evidence Required

```
From ARIA:
- Current /etc/network/interfaces
- ip -br addr (current IP assignments)
- tailscale status

From 3560CX:
- show interface GigabitEthernet0/4 status
- show interface Vlan70
- show ip route 192.168.70.0
```

---

## Diagnostic / Migration Path

```
Step 1: Confirm current state
  ARIA is on nic1, static 192.168.100.10/24, gateway 192.168.100.1
  Confirm: cat /etc/network/interfaces

Step 2: Design the new configuration
  Current (wrong for VLAN 70):
    Direct IP on nic1 — not a bridge, not VLAN-aware

  Required for VLAN 70:
    vmbr0 bridge on nic1 — standard Proxmox bridge design
    VLAN 70 access port OR trunk on Gi0/4

  Option A — Access port (simpler for now):
    Gi0/4 as VLAN 70 access port
    vmbr0 gets 192.168.70.10/24 directly, no VLAN tag needed on the bridge

  Option B — Trunk (future-proof for VM VLANs):
    Gi0/4 as trunk carrying VLAN 70 and other VLANs
    vmbr0 as VLAN-aware bridge with VLAN 70 as management VLAN

  For Phase C, Option A is sufficient. Option B is the target for full VM deployment.

Step 3: Reconfigure Gi0/4 on 3560CX
  For Option A (access port):
    interface GigabitEthernet0/4
     description ARIA-PROXMOX-VLAN70
     no switchport mode access     (currently access VLAN 1)
     switchport access vlan 70
     spanning-tree portfast edge
     spanning-tree bpduguard enable

  Verify: show interface GigabitEthernet0/4 status
  Expected: connected, VLAN 70

Step 4: Update /etc/network/interfaces on ARIA
  Take a backup first:
    cp /etc/network/interfaces /etc/network/interfaces.bak

  New configuration (Option A — bridge on nic1):
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

Step 5: Apply networking WITHOUT rebooting (use ifupdown)
  ifdown nic1
  ifdown vmbr0 (if it existed before)
  ifup vmbr0

  If this command hangs or fails, Comet console + Tailscale are recovery paths.

Step 6: Verify from another device
  ping 192.168.70.10
  ssh admin@192.168.70.10 (if SSH is configured)
  https://192.168.70.10:8006 (Proxmox web UI)

Step 7: Verify Tailscale still works
  tailscale status
  Tailscale IP should remain 100.71.239.21

Step 8: Remove /32 host routes from C1111
  Only after ARIA and Comet have both moved off VLAN 1.
  See: docs/runbooks/cisco/vlan1-temporary-host-routes.md
```

---

## Recovery Procedure (if ARIA becomes unreachable mid-migration)

```
Path 1 — Tailscale (if network stack partially up):
  ssh pve (via tailscale)
  Restore: cp /etc/network/interfaces.bak /etc/network/interfaces
  Apply: systemctl restart networking

Path 2 — Comet KVM console (if network stack is completely down):
  Open Comet dashboard at 192.168.100.11
  Access ARIA console
  Restore: cp /etc/network/interfaces.bak /etc/network/interfaces
  Apply: systemctl restart networking OR reboot

Path 3 — Hard reset via Comet ATX board (if ARIA is fully unresponsive):
  Use Comet power action to hard reset ARIA
  ARIA will boot with the restored config from NVRAM
```

---

## Documentation Prompt

```
Write a structured migration summary:
- Pre-migration state (IP, NIC, VLAN, switchport config)
- Changes made on 3560CX (Gi0/4 reconfiguration)
- Changes made to /etc/network/interfaces (what changed and why)
- Why vmbr0 bridge is required instead of direct NIC assignment
- How you verified the migration succeeded
- What the Tailscale fallback path was and whether you needed it
- What cleanup tasks remain (VLAN 1 host routes, C1111 SVI removal)
```

---

## Learning Objectives

- Understand why Proxmox requires a bridge (vmbr0) for proper VM networking
- Design and apply /etc/network/interfaces for a bridge configuration
- Reconfigure a 3560CX switchport from one VLAN to another safely
- Execute a live network migration with a documented rollback path
- Understand the three recovery paths (Tailscale, Comet console, ATX hard reset)
- Identify and execute cleanup tasks after a migration is complete
