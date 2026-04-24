# CUPS Print Server Setup

**Role:** Network print server for the home lab — allows any authorized client to print to a USB-attached HP All-in-One via IPP.
**Host:** Raspberry Pi on the SERVER VLAN
**CUPS Version:** 2.4.x
**Status:** Operational — verified from Linux, macOS, and Windows clients

---

## Architecture

The printer operates as a **dual-path device**:

- **Print path** — all local print jobs route through CUPS on the Pi via USB. Clients connect to the queue over IPP on the SERVER VLAN.
- **Vendor cloud path** — the printer's own WiFi radio lives on the **IOT VLAN** with dynamic DHCP. This segment only permits outbound internet + DNS to Pi-hole, so the cloud features work (Instant-Ink tracking, Print Anywhere, firmware updates) without the printer being reachable from trusted VLANs on its own.

```
CUPS client (TRUSTED / SERVER / HOUSEHOLD)
         │ IPP :631
         ▼
   Pi  ───USB───► HP All-in-One ───WiFi (IOT VLAN)───► Vendor cloud
  (CUPS)                                                (outbound only)
```

Trusted clients never talk directly to the printer — only through the CUPS queue.

---

## Why not just use the printer's built-in network stack?

- Attack surface: consumer printers commonly ship IPP, mDNS, SNMP, HTTP admin, FTP, and raw :9100 all listening on the LAN. Putting the raw device on TRUSTED exposes all of that.
- Vendor telemetry: even with Wi-Fi Direct disabled, the cloud features require outbound internet — best handled on the IOT VLAN.
- Auth and access control: CUPS gives us per-operation, per-VLAN access rules that the printer firmware doesn't.
- Uniformity: every client uses one IPP URI regardless of OS (no per-driver binaries).

---

## The Problem Encountered During Install

Initial setup failed with a `stat=12` error loop. Root cause: the kernel's `usblp` module and HPLIP (the HP driver stack) were both binding to the same USB endpoint and fighting for control. This also prevented the CUPS web UI from being reachable across the network.

## Resolution

1. **Kernel conflict** — blacklisted the `usblp` module:

   ```
   echo "blacklist usblp" | sudo tee /etc/modprobe.d/blacklist-usblp.conf
   sudo reboot
   ```

2. **Permissions** — added the admin user to the `lp` and `lpadmin` groups.

3. **Network access** — enabled remote admin/sharing:

   ```
   sudo cupsctl --remote-admin --remote-any --share-printers
   ```

   Then hardened access in `/etc/cups/cupsd.conf`:

   - Print submission: allowed from SERVER, TRUSTED, and HOUSEHOLD VLAN subnets + localhost
   - Admin access (add/remove queues, config changes): TRUSTED VLAN + localhost only

4. **Driver** — switched from the flaky `hp://` backend to the native `usb://` backend using **IPP Everywhere** (driverless). More reliable and no per-client driver install required.

---

## Configuration Summary

| Setting | Value |
|---|---|
| Protocol | IPP Everywhere (driverless) |
| Backend | `usb://` |
| Queue name | `HP_Envy_Lab` |
| CUPS port | 631 |
| Print ACL | SERVER + TRUSTED + HOUSEHOLD VLANs + localhost |
| Admin ACL | TRUSTED VLAN + localhost |

The Pi's LAN address is resolved via Pi-hole / DNS; clients are set up with the Pi's hostname rather than a raw IP so the queue remains portable if the address ever changes.

---

## Client Setup

**macOS:**
System Settings → Printers & Scanners → Add Printer → IP tab:

- Address: `<pi-hostname>`
- Protocol: IPP
- Queue: `/printers/HP_Envy_Lab`

Command line equivalent:

```
lpadmin -p HP_Envy_Lab -E \
  -v ipp://<pi-hostname>:631/printers/HP_Envy_Lab \
  -m everywhere
```

**Windows:**
Add printer via URL `http://<pi-hostname>:631/printers/HP_Envy_Lab`
Requires the "Internet Printing Client" feature enabled.
If jobs stall on a resource-constrained print server, toggle *Printer Properties → Advanced → "Start printing after last page is spooled"*.

**iOS / Android:**
Auto-detected via AirPrint/IPP from TRUSTED and HOUSEHOLD VLANs.

---

## Printer Hardening

- [x] Wi-Fi Direct disabled (was using vendor-default password)
- [x] Vendor marketing / telemetry sharing disabled
- [x] Admin password changed from default
- [x] Printer WiFi kept on IOT VLAN for cloud features only
- [x] CUPS admin restricted to TRUSTED VLAN
- [x] Printer reachable from TRUSTED/HOUSEHOLD only via the CUPS queue — never directly

---

## Disaster Recovery

If the Pi goes down:

1. Plug the printer's USB cable into any other machine and print locally, or
2. Temporarily re-enable the printer's own IPP listener on the IOT VLAN (access from TRUSTED via explicit allow rule), or
3. Restore the CUPS config on a fresh Pi from the backup at `/etc/cups/cupsd.conf.bak.YYYYMMDD`.

The queue definition is pure config — re-adding the USB device and restoring `cupsd.conf` is a 2-minute restore.

---

## Lessons Learned

1. Consumer printers with cloud subscriptions need internet — they cannot be fully air-gapped without breaking the subscription. Segment them on the IOT VLAN instead.
2. Consumer printers do not always honor DHCP reservations from every router. When reservations are unreliable, static-IP the printer's WiFi interface inside the IOT subnet *or* use USB + CUPS and skip the printer's own network stack entirely.
3. Cisco `hardware-address` in DHCP host pools is BOOTP-only; DHCP devices need `client-identifier` with the correct per-vendor format. Packet capture is often required to find it.
4. `show running-config | section dhcp` does not always show all pools — verify with `show ip dhcp pool` (no arguments) for the authoritative list.
5. The `usblp` kernel module **must** be blacklisted for CUPS to get exclusive USB access when using HPLIP.
6. IPP Everywhere via `usb://` is more reliable than HPLIP's `hp://` for newer HP all-in-ones.
7. Windows IPP clients may appear to "stall" on resource-constrained print servers — the fix is spool-then-print, not a server-side change.

---

*Last updated: April 24, 2026*
