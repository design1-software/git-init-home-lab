# Runbook: Ngrok Tunnel Recovery

**Last updated:** April 2026
**Estimated time:** 2-5 minutes

---

## When To Use

- tunnel-monitor.sh reports CRITICAL failure
- Railway logs show "MCP unreachable" or connection timeout errors
- Greeting posts are being created but not getting Sidecar media (stuck in "processing")
- Health check shows MCP server running but Ngrok not responding

---

## Quick Recovery (90% of cases)

```bash
# 1. Kill existing Ngrok
pkill -f ngrok

# 2. Wait for cleanup
sleep 3

# 3. Restart
ngrok http 3000 &

# 4. Wait for tunnel
sleep 5

# 5. Get new URL
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1
```

If using a **fixed Ngrok domain** (paid plan), no further action needed — Railway already points to the fixed URL.

If using **free tier** (random URL each time):

```bash
# Get the new URL
NEW_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
echo "New tunnel URL: $NEW_URL"

# Update Railway environment variable
# Option A: Railway CLI (if installed)
# railway variables set TUNNEL_URL="$NEW_URL"

# Option B: Manual — go to Railway dashboard → meta_engagement_pipeline → Variables
# Update TUNNEL_URL or MCP_SERVER_URL to the new URL
```

---

## Deep Recovery (if quick recovery fails)

### 1. Check if the MCP server is actually running

```bash
lsof -i :3000
# If empty, the MCP server is down — see server-restart.md
```

### 2. Check Ngrok auth status

```bash
ngrok config check
# If auth token is expired or missing:
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 3. Check for port conflicts

```bash
# Something else might be on port 4040 (Ngrok API port)
lsof -i :4040
# Kill if needed
kill $(lsof -t -i :4040)
```

### 4. Check internet connectivity

```bash
ping -c 3 tunnel.ngrok.com
# If this fails, it's a network issue, not Ngrok
```

### 5. Nuclear option: full restart

```bash
# Kill everything
pkill -f ngrok
pkill -f node

# Wait
sleep 5

# Start MCP server
cd ~/social-media-mcp
npm start &
sleep 5

# Start tunnel
ngrok http 3000 &
sleep 5

# Verify
~/home-lab/scripts/health-check.sh
```

---

## Why Tunnels Drop

| Cause | Frequency | Prevention |
|---|---|---|
| Ngrok free tier connection limit | Common | Upgrade to paid plan or switch to Cloudflare Tunnel |
| ISP IP change | Occasional | Ngrok handles this — auto-reconnects |
| Xfinity gateway reboot | Rare | UPS for gateway + auto-restart scripts |
| Ngrok service outage | Very rare | Monitor status.ngrok.com; Cloudflare Tunnel as backup |
| Server sleep/hibernate | If not disabled | Disable sleep: `systemctl mask sleep.target` |

---

## Automation (Already Configured)

The `tunnel-monitor.sh` script runs every 2 minutes via cron and auto-recovers most tunnel drops:

```cron
*/2 * * * * /home/user/home-lab/scripts/tunnel-monitor.sh >> /home/user/home-lab/logs/tunnel.log 2>&1
```

This runbook is for cases where automated recovery fails.

---

## Post-Recovery Checklist

- [ ] `curl http://localhost:4040/api/tunnels` shows active tunnel
- [ ] Tunnel URL matches what Railway expects (or is fixed domain)
- [ ] Railway can reach MCP: check Railway logs for successful MCP calls
- [ ] Next scheduled action from Railway executes successfully
- [ ] No "processing" stuck posts in meta_engagement_pipeline dashboard
