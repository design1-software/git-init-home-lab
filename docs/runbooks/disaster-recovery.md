# Runbook: Disaster Recovery — Bare Metal to Production

**Last updated:** April 24, 2026
**Estimated time:** 1-2 hours (with backups) / 4-8 hours (without backups)

---

## When To Use

- Acer SSD failure or corruption
- Windows won't boot after update
- Fresh OS reinstall required
- Replacing the Acer with a new machine
- Restoring after theft or physical damage (if off-site backup exists)

---

## Prerequisites

- A backup from `backup-critical.ps1` (either on D:\ drive or off-site)
- Internet connection
- Access to GitHub (repos are public)
- Access to API dashboards for key regeneration (if .env backup is lost)

---

## Recovery Priority Order

Restore in this order — each step unlocks the next:

```
1. Windows + Network     → machine is online
2. Docker Desktop        → container runtime ready
3. .env file             → secrets restored
4. social-media-mcp      → MCP server + Ngrok running
5. closet-monitor        → sensor pipeline + historical data restored
6. Tailscale             → remote access restored
7. PowerPanel            → UPS auto-shutdown restored
8. Verify end-to-end     → Railway can reach MCP
```

---

## Step 1: Windows + Network (15-30 min)

1. Install Windows 11 (or restore from recovery)
2. Connect Ethernet to Cisco GE0/1/0 (VLAN 10, access port)
3. Verify DHCP assigns `192.168.10.x` address
4. Verify internet: `ping 8.8.8.8`
5. Install Windows updates

The Acer should get `192.168.10.17` if the DHCP lease is still cached on the Cisco.
If it gets a different IP, the system still works — nothing is hardcoded to `.17`.

---

## Step 2: Docker Desktop (10 min)

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Install with WSL2 backend (default)
3. Restart when prompted
4. Open Docker Desktop → Settings → General → enable "Start Docker Desktop when you sign in"
5. Verify: `docker --version` and `docker compose version`

---

## Step 3: Restore .env File (5 min or 1-2 hours)

### If backup exists (D:\ drive or off-site):

```powershell
# Find the latest backup
Get-ChildItem D:\home-lab-backups | Sort-Object Name -Descending | Select-Object -First 1

# The .env file is in:
# D:\home-lab-backups\<latest>\secrets\social-media-mcp\.env
```

Copy it to the repo directory after cloning (Step 4).

### If .env backup is LOST:

This is the worst case. You need to regenerate every API key manually.
Use `.env.example` in the repo as your checklist. Sources for each key:

| Variable | Where to get it |
|---|---|
| NGROK_AUTHTOKEN | https://dashboard.ngrok.com/get-started/your-authtoken |
| NGROK_DOMAIN | https://dashboard.ngrok.com → Domains |
| MCP_AUTH_TOKEN | Generate a new UUID: `python -c "import uuid; print(uuid.uuid4())"` |
| GROK_API_KEY | https://console.x.ai/ |
| PERPLEXITY_API_KEY | https://www.perplexity.ai/settings/api |
| KIE_API_KEY | Kie.ai dashboard |
| SUNO_API_KEY | Suno dashboard |
| ELEVEN_LABS_API_KEY | https://elevenlabs.io/app/settings |
| CLIPDROP_API_KEY | ClipDrop/Stability AI dashboard |
| SUPABASE_URL, keys | https://supabase.com/dashboard → project settings |
| FACEBOOK_APP_SECRET | https://developers.facebook.com → App Settings |
| MEA_INTERNAL_KEY | Must match what's configured in Railway |
| POSTMARK_API_TOKEN | https://account.postmarkapp.com/servers |

After regenerating, update the matching variables in Railway (meta_engagement_pipeline)
for any shared secrets like MEA_INTERNAL_KEY.

**LESSON: This is why backup-critical.ps1 exists. Run it weekly. Copy off-site monthly.**

---

## Step 4: Clone and Start social-media-mcp (15-20 min)

```powershell
cd C:\Users\jbm06

# Clone the repo
git clone https://github.com/design1-software/social-media-mcp.git
cd social-media-mcp

# Copy .env from backup
Copy-Item "D:\home-lab-backups\<latest>\secrets\social-media-mcp\.env" .\.env

# Restore sessions from backup (if available)
Copy-Item -Recurse "D:\home-lab-backups\<latest>\mcp\sessions\*" .\sessions\

# Create storage directory (media will regenerate as new content is created)
New-Item -ItemType Directory -Path storage -Force

# Build and start
docker compose build
docker compose up -d

# Verify
docker compose ps
curl http://localhost:3000/health
curl https://mea.ngrok.app/health
```

If the build fails with peer dependency errors:
- Verify both `npm ci` lines in the Dockerfile have `--legacy-peer-deps`
- See the Docker migration guide for troubleshooting

---

## Step 5: Restore closet-monitor (10-15 min)

```powershell
cd C:\Users\jbm06

# Clone the repo
git clone https://github.com/design1-software/closet-monitor.git
cd closet-monitor

# Restore the SQLite database from backup (THIS IS THE HISTORICAL DATA)
Copy-Item "D:\home-lab-backups\<latest>\closet-monitor\*.db" .\
Copy-Item "D:\home-lab-backups\<latest>\closet-monitor\*.sqlite" .\

# Install Python dependencies
pip install -r requirements.txt

# Start the MQTT subscriber
python subscriber.py &

# Start the Streamlit dashboard
streamlit run dashboard.py --server.port 8501 &

# Verify
# Open http://localhost:8501 in a browser
```

The ESP32 sensor on VLAN 31 publishes to the Mosquitto broker on the Pi (192.168.10.16).
The subscriber on the Acer connects to the Pi's broker. As long as the Pi is up and the
Acer can reach `192.168.10.16:1883`, data will start flowing again immediately.

**If the SQLite database backup is lost:** The sensor data is gone. The ESP32 and Pi are
still collecting — new readings will start accumulating from this point forward. Document
the gap in your data engineering case study. Gaps are real; pretending they don't exist
is worse than explaining what happened.

---

## Step 6: Restore Tailscale (5 min)

```powershell
# Download and install Tailscale
# https://tailscale.com/download/windows

# Authenticate
tailscale login

# Verify
tailscale status

# IMPORTANT: Disable MagicDNS in Tailscale admin console
# https://login.tailscale.com/admin/dns
# MagicDNS hijacks DNS resolution — lesson #7
```

The Acer should get a new Tailscale IP (the old `100.113.164.125` may or may not be
reassigned). Update your home-lab-state doc with the new IP if it changes.

---

## Step 7: Restore PowerPanel Personal (5 min)

1. Download from https://www.cyberpowersystems.com/product/software/powerpanel-personal-windows/
2. Install
3. Connect USB-B cable from UPS to Acer
4. Configure: shutdown at 20% battery, 5-minute delay
5. Test: verify PowerPanel sees the UPS in its dashboard

---

## Step 8: Verify End-to-End (10 min)

Run the health check:

```powershell
cd C:\Users\jbm06\git-init-home-lab
powershell -ExecutionPolicy Bypass -File scripts\health-check.ps1
```

Expected: ALL SYSTEMS HEALTHY.

Also verify:
- [ ] `docker compose ps` shows both containers Up (healthy)
- [ ] `curl http://localhost:3000/health` returns OK
- [ ] `curl https://mea.ngrok.app/health` returns OK
- [ ] Railway logs show MCP server reachable
- [ ] closet-monitor Streamlit dashboard shows historical data at :8501
- [ ] Tailscale connected: `tailscale status`
- [ ] PowerPanel sees UPS: check system tray icon
- [ ] Next scheduled content post fires on time

---

## What Lives Where (Recovery Reference)

| Data | Location | Recoverable from... |
|---|---|---|
| Source code (all repos) | GitHub (public) | `git clone` |
| .env (API keys) | Acer C:\ only | D:\ backup or off-site backup |
| Docker config | In repo (Dockerfile, compose) | `git clone` |
| MCP sessions | Acer C:\, ephemeral | D:\ backup (nice-to-have) |
| MCP storage (media) | Acer C:\, regenerable | Regenerates as content is created |
| closet-monitor SQLite | Acer C:\ only | D:\ backup or off-site backup |
| closet-monitor code | GitHub (public) | `git clone` |
| Tailscale auth | Tailscale cloud | `tailscale login` |
| PowerPanel config | Reinstall + configure | 5-minute manual setup |
| Cisco config | On the Cisco flash | `show running-config` (unaffected by Acer failure) |
| Pi services | On the Pi SD card | Unaffected by Acer failure |
| CUPS config | On the Pi | Unaffected by Acer failure |

**Key insight:** The Pi and Cisco are independent of the Acer. If only the Acer dies,
Pi-hole, UniFi, Mosquitto, and CUPS keep running. The network stays up. Only the MCP
pipeline, closet-monitor subscriber, and Streamlit dashboard go down.

---

## Backup Schedule

| Frequency | Action |
|---|---|
| Weekly | Run `backup-critical.ps1` (backs up to D:\) |
| Monthly | Copy latest D:\ backup to iCloud Drive or Google Drive |
| Before major changes | Run `backup-critical.ps1` manually |
| After adding new API keys | Run `backup-critical.ps1` immediately |

---

## Time Estimates by Scenario

| Scenario | With backups | Without backups |
|---|---|---|
| SSD failure, D:\ intact | 1-2 hours | N/A |
| Full machine replacement | 1-2 hours | 4-8 hours (key regeneration) |
| Theft/fire, off-site backup exists | 2-3 hours (on new hardware) | N/A |
| Theft/fire, NO off-site backup | N/A | 4-8 hours + data loss |

---

*Written: April 24, 2026*
