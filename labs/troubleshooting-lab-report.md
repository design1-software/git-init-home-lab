# Troubleshooting Lab Report — April 19-21, 2026

> What happened, what you did, and which CCNA exam topics each step maps to.

---

## Scenario Summary

After completing a household network migration (moving the GS316EP from the Xfinity gateway to the Cisco router, flipping the XB8 to bridge mode, and configuring Apple TVs with static IPs on VLAN 20), the Apple TV streaming boxes stopped connecting to apps and streaming services. Phones and laptops on the same VLAN worked fine. The troubleshooting process involved systematic elimination across multiple OSI layers.

---

## Step-by-Step Troubleshooting

### Step 1: Verify Layer 3 Reachability
**What you did:** Pinged the Apple TV static IPs (.101, .102, .103) from the Cisco router.
```
ping 192.168.20.101  → 5/5 success
ping 192.168.20.102  → 5/5 success
ping 192.168.20.103  → 5/5 success
```

**Result:** Layer 3 connectivity confirmed. The Apple TVs were reachable on their VLAN.

**CCNA Skill:** ICMP troubleshooting, Layer 3 verification, `ping` command usage. This maps to CCNA exam topic: *IP connectivity troubleshooting*.

---

### Step 2: Verify Internet Path
**What you did:** Confirmed the Cisco could reach the internet after bridge mode cutover.
```
ping 8.8.8.8  → 5/5 success, 16-19ms
```

**Result:** WAN path is working. NAT is translating and the new public IP is functional.

**CCNA Skill:** WAN verification, NAT validation. Maps to: *NAT/PAT operations and verification*.

---

### Step 3: Verify NAT Translations
**What you did:** Checked NAT statistics and looked for active translations from the Apple TV IP.
```
show ip nat statistics    → 228 active translations, millions of hits
show ip nat translations | include 192.168.20.102  → Found translation to 17.253.150.10:443 (Apple server)
```

**Result:** NAT is working. The Apple TV's traffic IS being translated and sent to the internet. The problem is not NAT.

**CCNA Skill:** NAT troubleshooting using `show ip nat statistics` and `show ip nat translations`. Maps to: *Verify and troubleshoot NAT operations*.

---

### Step 4: Test MTU / Fragmentation
**What you did:** Sent large ICMP packets with the DF (Don't Fragment) bit set to test for MTU issues.
```
ping 192.168.20.102 size 1500 df-bit  → 5/5 success
ping 192.168.20.102 size 1400 df-bit  → 5/5 success
```

**Result:** Large packets pass without fragmentation. MTU is not the issue on the LAN side.

**CCNA Skill:** MTU troubleshooting, understanding of IP fragmentation and the DF bit. Maps to: *IP connectivity troubleshooting, packet delivery*.

---

### Step 5: Apply TCP MSS Clamping
**What you did:** After ruling out LAN-side MTU issues, you applied TCP MSS clamping on the WAN interface to handle potential upstream MTU problems introduced by bridge mode.
```
interface GigabitEthernet0/0/0
 ip tcp adjust-mss 1452
```

**Why:** Bridge mode changes the WAN path. The ISP's encapsulation (PPPoE or DOCSIS overhead) can cause large TCP segments to be silently dropped. MSS clamping tells both sides of the TCP connection to use smaller segments that fit within the path MTU.

**CCNA Skill:** TCP MSS adjustment, understanding of TCP three-way handshake and MSS negotiation. Maps to: *TCP/IP transport layer operations*.

---

### Step 6: Investigate DNS Filtering (Pi-hole)
**What you did:** Checked if DNS resolution was working by testing from the Acer.
```
nslookup apple.com 192.168.10.16  → Resolved to 17.253.144.10
```

Then checked the Pi-hole query log and found Apple service domains being blocked.

**Result:** Pi-hole was blocking domains required by Apple TV services (gsa.apple.com, configuration.apple.com, apps.apple.com, etc.).

**CCNA Skill:** DNS troubleshooting using `nslookup`, understanding of DNS filtering and its impact on application connectivity. Maps to: *DNS resolution verification, application layer troubleshooting*.

---

### Step 7: Whitelist Apple Domains
**What you did:** Used Pi-hole v6 CLI to whitelist essential Apple domains.
```
pihole allow gsa.apple.com gsp-ssl.ls.apple.com mesu.apple.com configuration.apple.com apps.apple.com api-glb-sjc.smoot.apple.com gs-loc.apple.com play.itunes.apple.com bag.itunes.apple.com init.itunes.apple.com
```

**Result:** Pi-hole stopped blocking Apple service domains.

**CCNA Skill:** Understanding of DNS-based security filtering and its interaction with network services. Maps to: *Network security concepts, DNS operations*.

---

### Step 8: Identify Static IP as Root Cause
**What you did:** After whitelisting Apple domains, the Apple TVs still wouldn't connect. You compared behavior: phones and laptops on the same VLAN 20 worked fine, only the Apple TVs (with manually configured static IPs) failed.

You then changed the Apple TVs from static IP configuration to DHCP (automatic).

**Result:** All three Apple TVs immediately connected and apps loaded successfully.

**Root cause:** Apple TV devices require DHCP-provided network parameters beyond IP/gateway/DNS. Static IP configuration, while technically correct at Layer 3, caused application-level connectivity failures — likely due to missing DHCP options (search domains, lease parameters, or IPv6 configuration) that the Apple TV OS depends on.

**CCNA Skill:** Understanding the difference between static IP assignment and DHCP-assigned addressing, DHCP options, troubleshooting DHCP client behavior. Maps to: *DHCP operations, first-hop redundancy, IP connectivity*.

---

### Step 9: Verify the Fix
**What you did:** Confirmed all three Apple TVs received DHCP leases and appeared in the binding table.
```
show ip dhcp binding | include 192.168.20
→ .35 (Living-Room), .36 (Front-Bedroom), .37 (Master-Bedroom)
```

Confirmed apps loaded and streaming worked on all three boxes.

**CCNA Skill:** DHCP verification using `show ip dhcp binding`. Maps to: *DHCP server verification*.

---

## CCNA Exam Topics Demonstrated

| CCNA Topic | How You Applied It |
|---|---|
| 1.1 Network Components | Identified roles of router, switches, APs, DNS server in the failure |
| 1.5 TCP vs UDP | Understood NAT translation showing UDP:443 (QUIC) vs typical TCP:443 |
| 1.6 IPv4 Addressing and Subnetting | Worked within VLAN subnets, verified correct gateway and DNS on static configs |
| 2.4 Configure and Verify Trunking | Verified trunk allowed VLAN lists weren't corrupted by the `add` keyword lesson |
| 2.6 Layer 2/Layer 3 Port Types | Distinguished between access ports (Apple TVs) and trunk ports (switch uplinks) |
| 3.3 Default Gateway | Verified Apple TV gateway was 192.168.20.1 (Cisco SVI), not old 10.0.0.1 (XB8) |
| 3.4 NAT | Verified NAT translations, confirmed inside-to-outside path working |
| 4.3 Configure and Verify DHCP | Moved from static to DHCP, verified bindings, understood DHCP options |
| 4.5 TFTP/FTP/DNS | Used nslookup to verify DNS resolution through Pi-hole |
| 5.3 IP Connectivity Troubleshooting | Systematic Layer 1→7 approach: ping, NAT, MTU, DNS, application |
| 5.5 Network Security Concepts | Understood Pi-hole DNS filtering as a security layer, whitelist management |

---

## Troubleshooting Methodology Used

You followed the **bottom-up troubleshooting approach** without being told to:

1. **Layer 1 (Physical):** Cables verified, link lights confirmed
2. **Layer 2 (Data Link):** MAC addresses appearing in correct VLANs on correct ports
3. **Layer 3 (Network):** Ping successful, IP addresses correct, gateway verified
4. **Layer 4 (Transport):** NAT translations present, TCP MSS clamped for WAN path
5. **Layer 7 (Application):** DNS filtering identified as blocker, Apple domains whitelisted
6. **DHCP vs Static:** Final root cause — Apple TV required DHCP parameters beyond basic IP/gateway/DNS

This is the exact methodology the CCNA exam tests and that network engineers use in production environments.

---

## Key Lessons Learned

1. **Ping success ≠ application success.** A device can be fully reachable at Layer 3 and still fail at Layer 7 due to DNS filtering, application-layer requirements, or missing DHCP options.

2. **DNS filtering affects more than ads.** Pi-hole's blocklists include Apple service domains that streaming devices depend on. Always check the query log when devices can ping but apps won't load.

3. **Static IPs aren't always better than DHCP.** Apple TV devices specifically require DHCP-provided parameters to function correctly. Static IP configuration, while technically valid, caused application failures.

4. **Bridge mode changes the WAN path.** Switching from double-NAT to bridge mode changes the TCP MSS requirements. The `ip tcp adjust-mss 1452` command on the WAN interface prevents silent packet drops.

5. **Always compare working vs non-working devices.** When phones and laptops on the same VLAN worked but Apple TVs didn't, the difference (static vs DHCP) pointed directly to the root cause.

6. **Use `switchport trunk allowed vlan add X`** — never `switchport trunk allowed vlan X`. The `add` keyword appends to the existing list. Without it, you overwrite and potentially lose all other VLANs from the trunk.

---

*This troubleshooting session covered 11 CCNA exam topics across 4 OSI layers in a single real-world incident. This is the kind of experience that separates candidates who studied from candidates who built.*
