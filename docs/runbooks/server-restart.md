# Runbook: Server Restart Procedure

**Last updated:** April 24, 2026
**Estimated time:** 2-3 minutes (Docker auto-recovers most cases)

---

## When To Use

- After a power outage or unexpected reboot
- After installing system updates
- When services are unresponsive and health-check.ps1 reports failures
- After hardware changes (RAM, disk, network cable)

---

## Docker (Current State)

Docker Desktop auto-starts on Windows login. Both containers have `restart: always`.
In most cases, after a reboot, **everything comes back automatically** — wait 2-3 minutes
for Docker Desktop to initialize, then verify.

### Step 1: Verify Containers Are Running

```powershell
cd C:\Users\jbm06\social-media-mcp
docker compose ps
```

Expected output:
```
NAME           IMAGE                         STATUS                    PORTS
mcp-server     social-media-mcp-mcp-server   Up (healthy)              0.0.0.0:3000->3000/tcp
ngrok-tunnel   ngrok/ngrok:latest            Up                        0.0.0.0:4040->4040/tcp
```

If both show `Up` → skip to Step 4.

### Step 2: If Containers Are Down

```powershell
# Start the stack
docker compose up -d

# Wait for health check to pass (15-30 seconds)
Start-Sleep -Seconds 20

# Verify
docker compose ps
```

### Step 3: If Containers Won't Start

```powershell
# Check what went wrong
docker compose logs mcp-server --tail=50
docker compose logs ngrok --tail=20

# Common fixes:
# - Missing .env file: verify C:\Users\jbm06\social-media-mcp\.env exists
# - Port conflict: Get-NetTCPConnection -LocalPort 3000
# - Docker Desktop not running: start Docker Desktop, wait 2 min, retry
```

### Step 4: Verify End-to-End

```powershell
# Local health
curl http://localhost:3000/health

# Ngrok tunnel
curl http://localhost:4040/api/tunnels

# External (what Railway sees)
curl https://mea.ngrok.app/health
```

All three should return HTTP 200 with `{"status":"OK"}`.

### Step 5: Verify Railway Connection

Check the Railway dashboard or logs to confirm:
- meta_engagement_pipeline can reach the MCP server via `mea.ngrok.app`
- Webhook processing is active
- Cron jobs are firing

---

## Fallback: Bare Metal (if Docker is broken)

Only use this if Docker Desktop itself is failing.

```powershell
# Stop Docker containers if partially running
docker compose down

# Start the old way
cd C:\Users\jbm06\social-media-mcp
npm run build
node dist/index.js

# In a separate terminal
ngrok http 3000 --domain=mea.ngrok.app
```

Nothing has been deleted — source code, .env, storage, and sessions are
on disk. Docker mounts them as volumes.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Both containers down after reboot | Docker Desktop didn't auto-start | Start Docker Desktop, wait 2 min, `docker compose up -d` |
| mcp-server exits immediately | Missing .env var or build error | `docker compose logs mcp-server --tail=50` |
| mcp-server healthy but ngrok down | NGROK_AUTHTOKEN missing or expired | Check .env, verify at dashboard.ngrok.com |
| Health returns OK locally, fails externally | Ngrok tunnel not routing | `docker compose restart ngrok` |
| Port 3000 conflict | Another process using the port | `Get-NetTCPConnection -LocalPort 3000`, kill conflict |
| No internet | Cable or ISP | Check physical connections, `Test-Connection 8.8.8.8` |

---

## Post-Restart Checklist

- [ ] `docker compose ps` shows both containers Up (healthy)
- [ ] `curl http://localhost:3000/health` returns OK
- [ ] `curl https://mea.ngrok.app/health` returns OK
- [ ] Railway logs show MCP server reachable
- [ ] Next scheduled content post fires on time
- [ ] No error emails received in 15 minutes
