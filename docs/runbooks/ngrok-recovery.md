# Runbook: Ngrok Tunnel Recovery

**Last updated:** April 24, 2026
**Estimated time:** 1-2 minutes

---

## When To Use

- Railway logs show "MCP unreachable" or connection timeout errors
- `curl https://mea.ngrok.app/health` fails but `curl http://localhost:3000/health` succeeds
- Content posts fail with "sidecar unreachable" errors
- health-check.ps1 reports Ngrok FAIL but MCP OK

---

## Quick Recovery (Docker)

```powershell
cd C:\Users\jbm06\social-media-mcp

# Restart just the Ngrok container (MCP server stays up)
docker compose restart ngrok

# Wait for tunnel to establish
Start-Sleep -Seconds 10

# Verify tunnel is active
curl http://localhost:4040/api/tunnels

# Verify external access
curl https://mea.ngrok.app/health
```

Since you're using a **fixed Ngrok domain** (`mea.ngrok.app`), the URL never changes.
Railway doesn't need any updates after recovery.

---

## If Quick Recovery Fails

### Check 1: Is the MCP server healthy?

```powershell
docker compose ps
curl http://localhost:3000/health
```

If mcp-server is unhealthy or down, Ngrok won't start (it depends on `service_healthy`).
Fix the MCP server first — see the [Server Restart runbook](server-restart.md).

### Check 2: Is the Ngrok auth token valid?

```powershell
docker compose logs ngrok --tail=20
```

Look for `ERR_NGROK_105` (invalid auth token) or `ERR_NGROK_108` (auth token expired).

Fix: update `NGROK_AUTHTOKEN` in `.env` from https://dashboard.ngrok.com/get-started/your-authtoken

```powershell
# After updating .env
docker compose restart ngrok
```

### Check 3: Is the fixed domain still assigned?

Log into https://dashboard.ngrok.com → Domains. Verify `mea.ngrok.app` is listed.

If the domain was released or reassigned, you'll see `ERR_NGROK_9028` in the logs.

### Check 4: Nuclear option — full restart

```powershell
docker compose down
docker compose up -d
```

---

## Fallback: Bare Metal Ngrok

Only if the Docker Ngrok container is fundamentally broken:

```powershell
# Stop the Docker Ngrok container
docker compose stop ngrok

# Run Ngrok directly on Windows (if installed)
ngrok http 3000 --domain=mea.ngrok.app
```

This is temporary — fix the Docker container and switch back.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ERR_NGROK_105` | Invalid auth token | Update NGROK_AUTHTOKEN in .env |
| `ERR_NGROK_108` | Auth token expired | Regenerate at dashboard.ngrok.com |
| `ERR_NGROK_9028` | Domain not found | Check domain in Ngrok dashboard |
| Ngrok starts but tunnel doesn't route | MCP server not healthy | Fix MCP first, Ngrok will reconnect |
| "connection refused" in Ngrok logs | MCP container networking | `docker compose down && docker compose up -d` |
| Intermittent timeouts | Ngrok free tier rate limits | Check Ngrok dashboard for rate limit warnings |

---

## Post-Recovery Checklist

- [ ] `curl https://mea.ngrok.app/health` returns OK
- [ ] `curl http://localhost:4040/api/tunnels` shows active tunnel
- [ ] Railway logs confirm MCP server reachable
- [ ] No error emails in 10 minutes
