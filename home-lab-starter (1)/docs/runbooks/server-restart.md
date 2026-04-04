# Runbook: Server Restart Procedure

**Last updated:** April 2026
**Estimated time:** 5-10 minutes (manual) / 2-3 minutes (Docker)

---

## When To Use

- After a power outage or unexpected reboot
- After installing system updates
- When services are unresponsive and health-check.sh reports failures
- After hardware changes (RAM, disk, network cable)

---

## Pre-Docker (Current State)

### Step 1: Verify Network Connectivity

```bash
# Check if the server has an IP and internet
ip addr show
ping -c 3 8.8.8.8
ping -c 3 google.com
```

If no connectivity, check:
- Ethernet cable seated in wall jack
- Switch power and link lights
- Xfinity gateway status

### Step 2: Start the MCP Server

```bash
cd ~/social-media-mcp

# Check if already running
lsof -i :3000

# If not running, start it
npm start &

# Or with tsx for development mode
# npx tsx watch src/index.ts &

# Verify
sleep 5
curl -s http://localhost:3000/health || echo "Health endpoint not available, checking port..."
lsof -i :3000
```

### Step 3: Start the Ngrok Tunnel

```bash
# Check if already running
curl -s http://localhost:4040/api/tunnels

# If not running, start it
ngrok http 3000 &

# Wait for tunnel to establish
sleep 5

# Get the public URL
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1
```

**Important:** If the Ngrok URL changed, you need to update:
1. `MCP_SERVER_URL` or `TUNNEL_URL` in the meta_engagement_pipeline on Railway
2. Any MCP client configurations that reference the tunnel URL

If using a fixed Ngrok domain (paid plan), the URL won't change.

### Step 4: Verify End-to-End

```bash
# Run full health check
~/home-lab/scripts/health-check.sh

# Test MCP from external (replace with your Ngrok URL)
curl -s https://your-tunnel-url.ngrok.app/health
```

### Step 5: Verify Railway Connection

Check the Railway dashboard or logs to confirm:
- meta_engagement_pipeline can reach the MCP server
- Webhook processing is active
- Cron jobs are firing (check greeting schedule)

---

## Post-Docker (Phase 3)

```bash
# Single command to start everything
cd ~/home-lab
docker compose up -d

# Verify all containers are healthy
docker compose ps
docker compose logs --tail=20

# Run health check
~/home-lab/scripts/health-check.sh
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| MCP won't start | Port 3000 in use | `kill $(lsof -t -i :3000)` then restart |
| MCP starts but crashes | Missing .env vars | Check `~/social-media-mcp/.env` exists |
| Ngrok won't connect | Auth token expired | `ngrok config check` then re-auth |
| Ngrok URL changed | Free tier = random URLs | Update TUNNEL_URL on Railway |
| No internet | Cable unplugged or ISP down | Check physical connections, test WiFi |
| Services running but Railway can't reach | Ngrok tunnel not routing | Restart Ngrok, verify public URL |

---

## Post-Restart Checklist

- [ ] health-check.sh reports all green
- [ ] MCP server responding on :3000
- [ ] Ngrok tunnel active with public URL
- [ ] Railway meta_engagement_pipeline can call MCP
- [ ] Next scheduled greeting fires on time
- [ ] No error emails received in 15 minutes
