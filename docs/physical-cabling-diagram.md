# Physical Cabling Diagram

> All copper unless noted. Speeds are gigabit unless otherwise stated.
> Last verified: Jun 2, 2026.

---

```
                        ┌─────────────────────┐
                        │   INTERNET (Comcast) │
                        └──────────┬──────────┘
                                   │ coax
                        ┌──────────▼──────────┐
                        │   Xfinity XB8        │
                        │   (bridge mode)      │
                        └──────────┬──────────┘
                                   │ ethernet (WAN — DHCP public IP)
                        ┌──────────▼──────────────────────────────┐
                        │   Cisco C1111-4PWB  (JLM-LAB-R1)        │
                        │   GE0/0/0  ← WAN                        │
                        │   GE0/1/0  ── TRANSIT /30 ──────────┐   │
                        │   GE0/1/1  (available)               │   │
                        │   GE0/1/2  (available)               │   │
                        │   GE0/1/3  (available)               │   │
                        └─────────────────────────────────────────┘
                                   │ 192.168.199.1 ↔ 192.168.199.2
                        ┌──────────▼──────────────────────────────┐
                        │   Catalyst 3560CX-8PC-S  (JLM-LAB-SW1) │
                        │   Gi0/1  ← TRANSIT from C1111 GE0/1/0  │
                        │   Gi0/2  ── trunk ──────────────┐       │
                        │   Gi0/3  ── trunk ──────────────│──┐    │
                        │   Gi0/4  ── (reserved, no cable) │  │   │
                        │   Gi0/5–8  (available)           │  │   │
                        └─────────────────────────────────────────┘
                                   │                │
         ┌─────────────────────────┘                └──────────────────────────┐
         │ trunk (VLANs 1,10,20,30,31,40,50,99)       trunk (VLANs 1,10,20,   │
         │ native VLAN 99                              30,31,40,50,99)         │
┌────────▼─────────────────────────────┐    ┌─────────────────────────────────▼──┐
│   NETGEAR GS308EP  (Lab Switch)      │    │   NETGEAR GS316EP (Household Switch)│
│   Mgmt: 192.168.100.95               │    │   Mgmt: 192.168.100.96              │
│                                      │    │                                     │
│   Port 1  ← Trunk from 3560CX Gi0/2 │    │   Port 1   Spare                   │
│   Port 2  ── VLAN 10 access          │    │   Port 2   Apple TV (Front Bed) ─┐ │
│   Port 3  ── VLAN 10 access (PoE) ──│──┐ │   Port 3   Apple TV (Living Rm) ─┤ │
│   Port 4  ── Trunk (AP VLANs) ──────│──│─│── │   Port 4   Apple TV (Master Bed)─┘ │
│   Port 5  ── Trunk (AP VLANs) ──────│──│ │   Ports 5–14  Wall outlets (spare) │
│   Ports 6–8  Spare                  │  │ │   Port 15  ← Trunk from 3560CX Gi0/3│
└──────────────────────────────────────┘  │ │   Port 16  SFP slot (empty)        │
         │              │                 │ └────────────────────────────────────┘
         │              │                 │          │         │         │
         │              │                 │    VLAN 20   VLAN 20   VLAN 20
         │              │ PoE             │   Apple TV  Apple TV  Apple TV
         │              │                 │
         │     ┌────────▼────────┐        │
         │     │  Raspberry Pi 4B│        │
         │     │  192.168.10.16  │        │
         │     │  VLAN 10 (MGMT) │        │
         │     └─────────────────┘        │
         │                                │
   ┌─────▼─────────┐    ┌─────────────────▼──┐  ┌────────────────────────┐
   │  Acer Server  │    │  UniFi U6+ AP #1   │  │  UniFi U6+ AP #2       │
   │  192.168.10.11│    │  192.168.99.12      │  │  192.168.99.11         │
   │  VLAN 10      │    │  GS308EP Port 4     │  │  GS308EP Port 5        │
   │  (MGMT)       │    │  (desk-mounted)     │  │  (desk-mounted)        │
   └───────────────┘    └─────────────────────┘  └────────────────────────┘
                              │                         │
                    ┌─────────┴─────────────────────────┘
                    │   WiFi SSIDs (both APs broadcast all 5):
                    │     Gorgeous        → VLAN 20 (TRUSTED)
                    │     Gorgeous-IoT    → VLAN 30 (IOT)
                    │     Gorgeous-Auto   → VLAN 31 (IOT-AUTO)
                    │     Gorgeous-Home   → VLAN 40 (HOUSEHOLD)
                    │     JM&G-GUEST      → VLAN 50 (GUEST)

┌──────────────────────────────────────────────────────────────────────────┐
│  Proxmox Server (pve)                                                    │
│  192.168.100.10 (VLAN 1 interim) · Tailscale 100.71.239.21              │
│  Intel I225V mgmt NIC ── (cable not yet run to 3560CX Gi0/4)            │
│  Realtek RTL8125  ── (future VM trunk — awaiting Phase C)               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Cable Index

| Run | From | To | Type | Notes |
|---|---|---|---|---|
| 1 | Xfinity XB8 | C1111 GE0/0/0 | Cat5e/6 | WAN — DHCP public IP |
| 2 | C1111 GE0/1/0 | 3560CX Gi0/1 | Cat5e/6 | TRANSIT /30 — 192.168.199.1 ↔ .2 |
| 3 | 3560CX Gi0/2 | GS308EP Port 1 | Cat5e/6 | Trunk — all production VLANs, native 99 |
| 4 | 3560CX Gi0/3 | GS316EP Port 15 | Cat5e/6 | Trunk — all production VLANs |
| 5 | GS308EP Port 2 | Acer Server | Cat5e/6 | Access VLAN 10 |
| 6 | GS308EP Port 3 | Raspberry Pi 4B | Cat5e/6 | Access VLAN 10 · PoE powered |
| 7 | GS308EP Port 4 | UniFi U6+ AP #1 | Cat5e/6 | Trunk — AP VLANs 20,30,31,40,50,99 |
| 8 | GS308EP Port 5 | UniFi U6+ AP #2 | Cat5e/6 | Trunk — AP VLANs 20,30,31,40,50,99 |
| 9 | GS316EP Port 2 | Apple TV (Front Bedroom) | Cat5e/6 | Access VLAN 20 |
| 10 | GS316EP Port 3 | Apple TV (Living Room) | Cat5e/6 | Access VLAN 20 |
| 11 | GS316EP Port 4 | Apple TV (Master Bedroom) | Cat5e/6 | Access VLAN 20 |
| — | 3560CX Gi0/4 | Proxmox Intel I225V | Cat5e/6 | **Not yet run** — pending Phase C |
| — | GS316EP Port 16 | — | SFP fiber | **Empty** — slot unused, no module inserted |

---

## Notes

- All switches managed via VLAN 1 (192.168.100.0/24) web UI — reachable from any routed VLAN via C1111
- GS308EP provides PoE+ to Pi 4B (Port 3), AP #1 (Port 4), AP #2 (Port 5)
- GS316EP Port 16 is an SFP mini-GBIC slot — accepts 1000BASE-SX/LX fiber or 1000BASE-T copper SFP module; currently empty
- Proxmox is reachable via Tailscale (`pve`, 100.71.239.21) until the VLAN 70 trunk cable is run
- UPS #1 (CP1500PFCLCD) protects critical infra (C1111, switches, Pi, Acer); UPS #2 (SX950U) protects office Tailscale nodes
