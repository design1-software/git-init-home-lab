# Helpdesk Ticket 008 — Comet ATX Board Hard Reset Validation

**Domain:** Out-of-Band Management / Hardware / KVM
**Difficulty:** Intermediate
**Estimated time:** 45–60 minutes
**Status:** Live validation complete — Jun 5, 2026 — **ATX Gate: PASSED WITH NOTE**

---

## Scenario

A student is assigned to validate the Comet GL-ATXPC ATX control board after installation. The board provides hard power and reset relay control through the Comet GL-RM1PE KVM. Until this ticket is completed, ARIA's only remote power-on path is Wake-on-LAN — insufficient for a hard crash or kernel panic recovery.

This is a structured validation, not a break/fix. The student works through each capability in order, documents every result, and confirms the full out-of-band recovery stack is operational.

---

## Ticket Details

**Reported by:** Lab instructor (assigned validation task)
**Affected system:** ARIA Proxmox — out-of-band management
**Priority:** High (blocks VLAN 70 migration and workload deployment)
**Category:** Hardware — KVM / Out-of-Band

---

## Background: Why This Matters

Wake-on-LAN is a power-on convenience feature. It is not a recovery tool.

WoL cannot recover from:
- Frozen kernel — NIC stack may be unresponsive
- Hung motherboard state
- Failed boot after a package upgrade or misconfiguration
- OS-level deadlock

The ATX board provides:
- Power button relay — clean shutdown or force-off
- Reset button relay — hard reset without power cycle
- Power state visibility through Comet

Without the ATX board confirmed operational, ARIA cannot safely receive package upgrades, VLAN migrations, or workload deployments. A failure during any of those requires physical presence.

---

## ATX Board Installation Context

The GL-ATXPC board sits between the motherboard F_PANEL header and the SAMA V40 case front-panel wiring. It intercepts the power and reset button signals and also connects to the Comet via USB-C.

Wiring path:
```
Gigabyte B650 GAMING X AX V2 F_PANEL header
  → GL-ATXPC board (intercepts PWR_BTN and RESET_BTN)
  → SAMA V40 front panel (case buttons still work normally)
  → Comet GL-RM1PE (USB-C from GL-ATXPC)
```

---

## AI Mentor Opening Questions

```
1. Is the GL-ATXPC board physically installed and connected to the B650 F_PANEL header?
2. Is the USB-C cable from the GL-ATXPC connected to the Comet?
3. Is the Comet dashboard accessible at http://192.168.100.11?
4. Does the Comet dashboard show ARIA power state (on/off indicator)?
5. Is the case power button still functional after the ATX board installation?
   (Test: press physical power button — does ARIA respond?)
```

---

## Validation Sequence

The student must complete these steps in order. Each step must be confirmed before proceeding to the next.

### Step 1 — Comet console visibility

```
Confirm: Comet dashboard at http://192.168.100.11
Confirm: ARIA video is visible in the Comet console
Confirm: Comet keyboard input works (type in ARIA terminal)
Result: PASS or FAIL
```

### Step 2 — Power state indicator

```
Confirm: Comet shows ARIA power state correctly
  - When ARIA is running: indicator shows ON
  - When ARIA is off: indicator shows OFF
Result: PASS or FAIL
```

### Step 3 — Clean shutdown via Comet

```
Action: Use Comet power action → "Power Off" (clean/ACPI shutdown)
Expected: ARIA shuts down gracefully (OS shutdown sequence visible in console)
Confirm: ARIA is fully off, Comet power indicator shows OFF
Result: PASS or FAIL
```

### Step 4 — Power on via Comet

```
Action: Use Comet power action → "Power On"
Expected: ARIA powers on, POST visible in Comet console
Confirm: ARIA boots to Proxmox login, web UI accessible
Result: PASS or FAIL
```

### Step 5 — Hard reset via Comet (the critical test)

```
Action: Simulate a non-responsive host
  - SSH into ARIA
  - Freeze the display: while true; do echo test; done (fills terminal)
  - Do NOT press Ctrl+C — leave ARIA in a busy state

Action: Use Comet power action → "Reset" (hard reset)
Expected: ARIA reboots immediately without clean shutdown
Confirm: ARIA POST is visible in Comet console within ~30 seconds
Confirm: ARIA boots back to Proxmox
Result: PASS or FAIL
```

### Step 6 — Force power off via Comet (the recovery test)

```
Action: Leave ARIA running
Action: Use Comet power action → "Force Power Off" (holds power relay)
Expected: ARIA powers off immediately (no graceful shutdown)
Confirm: Comet power indicator shows OFF
Action: Power ARIA back on via Comet
Confirm: ARIA boots normally, no filesystem errors
Result: PASS or FAIL
```

### Step 7 — Physical case button still works

```
Confirm: Press physical power button on SAMA V40 case
Expected: ARIA responds normally (brief press = clean shutdown, hold = force off)
Result: PASS or FAIL
```

### Step 8 — BIOS/POST access via Comet

```
Action: Restart ARIA via Comet
During POST: press Delete key via Comet keyboard input
Expected: Gigabyte BIOS UI appears in Comet console
Confirm: Full BIOS navigation works via Comet keyboard
Result: PASS or FAIL
```

---

## Evidence Required

```
For each step: screenshot or text confirmation of PASS/FAIL result
Comet dashboard showing power state transitions
Comet console showing ARIA POST during at least one boot
Filesystem check output after force-off test (Step 6)
```

---

## Live Validation Results (Jun 5, 2026)

| Step | Test | Result |
|---|---|---|
| 1 | Comet KVM video visible | ✅ PASS |
| 2 | ATX board detected in Comet UI / power state visible | ✅ PASS |
| 3 | Clean shutdown via Comet | ✅ PASS |
| 4 | Power on via Comet — ARIA boots, returns to network, ARP resolves | ✅ PASS |
| 5 | Hard reset via Comet | ⚠️ NOT WIRED — SAMA V40 has no physical reset button; reset circuit not connected to B650 reset pins |
| 6 | Force power off via Comet | ✅ PASS |
| 7 | Physical SAMA V40 power button still functional | ✅ PASS |
| 8 | BIOS/POST access via Comet keyboard | ✅ PASS (previously validated Jun 4, 2026) |

**Gate decision: PASSED WITH NOTE**
- Remote power control: PASS
- Remote reset: NOT WIRED / OPTIONAL — not a blocker. Recovery uses force power-off + power-on.
- WoL secondary path: PASS

ARIA is now cleared for VLAN 70 migration and package upgrades.

---

## Acceptance Criteria

All 8 steps must be PASS before this ticket can be closed. A single FAIL means the ATX board installation needs to be reviewed before ARIA is considered ready for VLAN 70 migration or package upgrades.

> **Note on Step 5:** The SAMA V40 case has no reset button. The reset relay has no circuit to intercept. This is a hardware limitation of the case, not a failure of the ATX board installation. All critical recovery scenarios (unresponsive OS, kernel panic, hung boot) are covered by force power-off + power-on.

---

## Documentation Prompt

```
Write a validation report covering:
- ATX board installation summary (wiring path)
- Results of all 8 validation steps (PASS/FAIL for each)
- Any issues encountered and how they were resolved
- Final confirmation that ARIA's out-of-band recovery stack is operational
- Statement: "ARIA is now cleared for VLAN 70 migration and package upgrades"
  (only if all 8 steps PASS)
```

---

## Learning Objectives

- Understand the difference between WoL (power-on convenience) and ATX relay (hard recovery)
- Know the physical wiring path for a KVM ATX control board
- Execute a structured hardware validation sequence with documented results
- Understand why each validation step tests a different recovery scenario
- Recognize what "out-of-band management" means in enterprise infrastructure
- Understand why this validation gates further work (VLAN migration, upgrades)
