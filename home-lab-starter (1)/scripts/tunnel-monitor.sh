#!/bin/bash
# ============================================================
# NGROK TUNNEL WATCHDOG
# ============================================================
# Monitors the Ngrok tunnel and restarts it if disconnected.
# Run as a cron job every 2 minutes:
#   */2 * * * * /path/to/tunnel-monitor.sh >> /home/user/home-lab/logs/tunnel.log 2>&1
#
# Requires: curl, ngrok CLI installed and configured
# ============================================================

set -uo pipefail

# --- Configuration ---
MCP_PORT="${MCP_PORT:-3000}"
NGROK_API="http://localhost:4040/api/tunnels"
NGROK_CONFIG="${HOME}/.config/ngrok/ngrok.yml"  # Adjust if different
MAX_RETRIES=3
RETRY_DELAY=10
LOG_PREFIX="[tunnel-watchdog]"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(timestamp) $LOG_PREFIX $1"; }

# --- Check if tunnel is healthy ---
check_tunnel() {
    local response
    response=$(curl -sf --max-time 5 "$NGROK_API" 2>/dev/null)
    if [ $? -ne 0 ]; then
        return 1
    fi

    # Check if there's an active tunnel
    local tunnel_count
    tunnel_count=$(echo "$response" | grep -c '"public_url"' 2>/dev/null || echo "0")
    if [ "$tunnel_count" -eq 0 ]; then
        return 1
    fi

    return 0
}

# --- Restart tunnel ---
restart_tunnel() {
    log "Attempting to restart Ngrok tunnel..."

    # Kill existing ngrok processes
    pkill -f "ngrok" 2>/dev/null || true
    sleep 2

    # Start ngrok in background
    if [ -f "$NGROK_CONFIG" ]; then
        nohup ngrok http "$MCP_PORT" --config "$NGROK_CONFIG" > /dev/null 2>&1 &
    else
        nohup ngrok http "$MCP_PORT" > /dev/null 2>&1 &
    fi

    # Wait for tunnel to establish
    sleep 5

    # Verify it came up
    if check_tunnel; then
        local new_url
        new_url=$(curl -s "$NGROK_API" 2>/dev/null | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
        log "Tunnel restored: $new_url"
        return 0
    else
        log "Tunnel failed to restart"
        return 1
    fi
}

# --- Main ---
if check_tunnel; then
    # Tunnel is healthy, nothing to do
    # Only log every 30 minutes to avoid noise (check minute divisible by 30)
    MINUTE=$(date +%M)
    if [ "$((MINUTE % 30))" -eq 0 ]; then
        log "Tunnel healthy"
    fi
    exit 0
fi

# Tunnel is down — attempt recovery
log "ALERT: Tunnel is DOWN. Starting recovery..."

for i in $(seq 1 $MAX_RETRIES); do
    log "Recovery attempt $i/$MAX_RETRIES..."
    if restart_tunnel; then
        log "Recovery successful on attempt $i"

        # Optional: Send notification
        # If you have email configured in the MCP server, you could curl a notification endpoint
        # curl -sf "http://localhost:${MCP_PORT}/api/notify?msg=Tunnel+recovered" > /dev/null 2>&1

        exit 0
    fi
    log "Attempt $i failed, waiting ${RETRY_DELAY}s..."
    sleep "$RETRY_DELAY"
done

log "CRITICAL: Tunnel recovery FAILED after $MAX_RETRIES attempts. Manual intervention required."

# Optional: Send critical alert email
# This could call your MCP server's email transport if available

exit 2
