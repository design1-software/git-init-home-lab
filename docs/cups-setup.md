# CUPS Print Server Setup

**Date:** April 23, 2026
**Host:** jlm-lab-pi (Raspberry Pi 4B, 192.168.10.16)
**Printer:** HP ENVY Inspire 7200e All-in-One
**CUPS Version:** 2.4.10
**Status:** Functional — verified via Debian, Windows, and macOS test pages

---

## Architecture

The printer operates as a dual-path device:

- **Print path:** All local printing goes through CUPS on the Pi via USB.
  Clients connect to `ipp://192.168.10.16:631/printers/HP_Envy_Lab`
- **HP cloud path:** Printer's WiFi radio connects to Gorgeous-IOT (VLAN 30)
  for Instant Ink monitoring, Print Anywhere, and firmware updates.

```
Mac/iPhone (VLAN 20) ──► Pi CUPS (VLAN 10, :631) ──► USB ──► HP ENVY
Family (VLAN 40)    ──►                                         │
                                                                 │ WiFi
                                                     Gorgeous-IOT (VLAN 30)
                                                                 │
                                                          HP Cloud (Instant Ink)
```

---

## The Problem

Initial setup encountered a "stat=12" error loop caused by the Linux kernel's
`usblp` module and HPLIP fighting for control of the same USB port. This also
prevented the CUPS Web UI from being reachable across the network.

---

## Resolution

1. **Kernel conflict:** Blacklisted `usblp` module
   ```bash
   echo "blacklist usblp" | sudo tee /etc/modprobe.d/blacklist-usblp.conf
   ```

2. **Permissions:** Added admin user to `lp` and `lpadmin` groups
   ```bash
   sudo usermod -aG lp,lpadmin admin
   ```

3. **Network access:** Opened CUPS to the local network
   ```bash
   sudo cupsctl --remote-admin --remote-any --share-printers
   ```
   Then hardened access in `/etc/cups/cupsd.conf`:
   - Print submission (`/`): localhost + VLAN 10 + VLAN 20 + VLAN 40
   - Admin access (`/admin`, `/admin/conf`, `/admin/log`): localhost + VLAN 20 only

4. **Driver:** Switched from buggy `hp://` backend to native `usb://` backend
   using IPP Everywhere (driverless) protocol

---

## Configuration Details

| Setting | Value |
|---|---|
| Connection URI | `usb://HP/ENVY%20Inspire%207200%20series?serial=TH35VJX0GB&interface=1` |
| Protocol | IPP Everywhere / Driverless |
| CUPS Queue Name | `HP_Envy_Lab` |
| Access URL | `http://192.168.10.16:631/printers/HP_Envy_Lab` |
| Config file | `/etc/cups/cupsd.conf` |
| Config backup | `/etc/cups/cupsd.conf.bak.YYYYMMDD` |

---

## CUPS Access Policy

```
<Location />              → Allow 127.0.0.1, 192.168.10.16, 192.168.20.0/24, 192.168.40.0/24
<Location /admin>         → Allow 127.0.0.1, 192.168.10.16, 192.168.20.0/24
<Location /admin/conf>    → Allow 127.0.0.1, 192.168.10.16, 192.168.20.0/24
<Location /admin/log>     → Allow 127.0.0.1, 192.168.10.16, 192.168.20.0/24
```

All other VLANs (IOT, IOT-AUTO, GUEST) are denied by `Order allow,deny`.

---

## Client Setup

**macOS (all Macs):**

System Settings → Printers & Scanners → Add Printer → IP tab:
- Address: `192.168.10.16`
- Protocol: IPP
- Queue: `/printers/HP_Envy_Lab`

Or via command line:
```bash
lpadmin -p HP_Envy_Lab -E -v ipp://192.168.10.16:631/printers/HP_Envy_Lab -m everywhere
```

**Windows:**

Add printer via URL: `http://192.168.10.16:631/printers/HP_Envy_Lab`

Requires "Internet Printing Client" enabled in Windows Features.

If print jobs stall, change to "Start printing after last page is spooled"
in Printer Properties → Advanced tab.

**iOS/Android:**

Auto-detect via AirPrint/IPP on VLAN 20 and VLAN 40.

---

## Printer Hardening

- [x] Wi-Fi Direct: Disabled (was using default password `12345678`)
- [x] HP marketing data sharing: Disabled
- [x] Admin password: Changed from default
- [x] WiFi kept on Gorgeous-IOT (VLAN 30) for Instant Ink only
- [x] CUPS admin restricted to VLAN 20 (Trusted)

---

## Disaster Recovery

If the Pi goes down:
1. Plug the printer's USB cable directly into any computer
2. Or: re-enable the printer's WiFi-based printing as a temporary fallback
3. CUPS config is backed up at `/etc/cups/cupsd.conf.bak.YYYYMMDD`

---

## Lessons Learned

1. HP Envy 7200e does not reliably accept DHCP reservations from Cisco IOS — use USB/CUPS instead
2. Cisco IOS `hardware-address` in DHCP host pools is BOOTP-only; DHCP devices need `client-identifier`
3. HP Instant Ink requires internet — printer WiFi must stay enabled on an internet-capable VLAN
4. `usblp` kernel module must be blacklisted for CUPS to have exclusive USB access
5. IPP Everywhere (driverless) via `usb://` is more reliable than HPLIP `hp://` for this printer
6. Windows print jobs may stall on resource-constrained print servers — spool fully before printing

---

*Deployed and verified: April 23, 2026*
