#!/bin/bash
# ============================================================
# HOME LAB HEALTH CHECK
# ============================================================
# Checks all critical services and reports status.
# Run manually or via cron: */5 * * * * /path/to/health-check.sh
#
# Exit codes:
#   0 = All services healthy
#   1 = One or more services degraded
#   2 = Critical failure (MCP server down)
# ============================================================

set -euo pipefail

# --- Configuration ---
MCP_PORT="${MCP_PORT:-3000}"
MCP_HEALTH_URL="http://localhost:${MCP_PORT}/health"
NGROK_API="http://localhost:4040/api/tunnels"
DISK_WARN_PERCENT=85
MEM_WARN_PERCENT=90
LOG_FILE="${HOME}/home-lab/logs/health-$(date +%Y%m%d).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# --- Helpers ---
timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log() {
    local level="$1" msg="$2"
    echo "$(timestamp) [$level] $msg" >> "$LOG_FILE"
    case "$level" in
        OK)   echo -e "  ${GREEN}✓${NC} $msg" ;;
        WARN) echo -e "  ${YELLOW}⚠${NC} $msg" ;;
        FAIL) echo -e "  ${RED}✗${NC} $msg" ;;
        *)    echo "  $msg" ;;
    esac
}

FAILURES=0
WARNINGS=0

# --- Checks ---
echo ""
echo "═══════════════════════════════════════"
echo "  Home Lab Health Check — $(timestamp)"
echo "═══════════════════════════════════════"
echo ""

# 1. MCP Server
echo "  MCP Server (social-media-mcp)"
echo "  ─────────────────────────────"
if curl -sf --max-time 5 "$MCP_HEALTH_URL" > /dev/null 2>&1; then
    log "OK" "MCP server responding on :${MCP_PORT}"
else
    # Try checking if the process is running even if /health isn't implemented
    if lsof -i :"$MCP_PORT" > /dev/null 2>&1; then
        log "WARN" "MCP server process on :${MCP_PORT} but /health not responding"
        ((WARNINGS++))
    else
        log "FAIL" "MCP server NOT running on :${MCP_PORT}"
        ((FAILURES++))
    fi
fi

# 2. Ngrok Tunnel
echo ""
echo "  Ngrok Tunnel"
echo "  ─────────────────────────────"
if curl -sf --max-time 5 "$NGROK_API" > /dev/null 2>&1; then
    TUNNEL_URL=$(curl -s "$NGROK_API" 2>/dev/null | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$TUNNEL_URL" ]; then
        log "OK" "Ngrok tunnel active: $TUNNEL_URL"
    else
        log "WARN" "Ngrok API responding but no active tunnels"
        ((WARNINGS++))
    fi
else
    log "FAIL" "Ngrok not responding (tunnel may be down)"
    ((FAILURES++))
fi

# 3. Disk Usage
echo ""
echo "  Disk Usage"
echo "  ─────────────────────────────"
DISK_PERCENT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_PERCENT" -ge "$DISK_WARN_PERCENT" ]; then
    log "WARN" "Disk usage at ${DISK_PERCENT}% (threshold: ${DISK_WARN_PERCENT}%)"
    ((WARNINGS++))
else
    log "OK" "Disk usage at ${DISK_PERCENT}%"
fi

# 4. Memory Usage
echo ""
echo "  Memory"
echo "  ─────────────────────────────"
MEM_TOTAL=$(free | awk '/Mem:/ {print $2}')
MEM_USED=$(free | awk '/Mem:/ {print $3}')
MEM_PERCENT=$((MEM_USED * 100 / MEM_TOTAL))
MEM_USED_GB=$(awk "BEGIN {printf \"%.1f\", $MEM_USED/1048576}")
MEM_TOTAL_GB=$(awk "BEGIN {printf \"%.1f\", $MEM_TOTAL/1048576}")
if [ "$MEM_PERCENT" -ge "$MEM_WARN_PERCENT" ]; then
    log "WARN" "Memory at ${MEM_PERCENT}% (${MEM_USED_GB}GB / ${MEM_TOTAL_GB}GB)"
    ((WARNINGS++))
else
    log "OK" "Memory at ${MEM_PERCENT}% (${MEM_USED_GB}GB / ${MEM_TOTAL_GB}GB)"
fi

# 5. Docker (if installed)
echo ""
echo "  Docker Containers"
echo "  ─────────────────────────────"
if command -v docker &> /dev/null; then
    RUNNING=$(docker ps -q 2>/dev/null | wc -l)
    STOPPED=$(docker ps -aq --filter "status=exited" 2>/dev/null | wc -l)
    if [ "$STOPPED" -gt 0 ]; then
        log "WARN" "${RUNNING} running, ${STOPPED} stopped containers"
        ((WARNINGS++))
    else
        log "OK" "${RUNNING} containers running, none stopped"
    fi
else
    log "INFO" "Docker not installed (Phase 3)"
fi

# 6. Network Connectivity
echo ""
echo "  Network"
echo "  ─────────────────────────────"
if ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
    log "OK" "Internet connectivity OK"
else
    log "FAIL" "No internet connectivity"
    ((FAILURES++))
fi

# 7. Process Check (Node.js for MCP)
echo ""
echo "  Key Processes"
echo "  ─────────────────────────────"
NODE_PROCS=$(pgrep -c node 2>/dev/null || echo "0")
if [ "$NODE_PROCS" -gt 0 ]; then
    log "OK" "${NODE_PROCS} Node.js process(es) running"
else
    log "WARN" "No Node.js processes found"
    ((WARNINGS++))
fi

# --- Summary ---
echo ""
echo "═══════════════════════════════════════"
if [ "$FAILURES" -gt 0 ]; then
    echo -e "  ${RED}CRITICAL: ${FAILURES} failure(s), ${WARNINGS} warning(s)${NC}"
    echo "═══════════════════════════════════════"
    echo ""
    exit 2
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "  ${YELLOW}DEGRADED: ${WARNINGS} warning(s)${NC}"
    echo "═══════════════════════════════════════"
    echo ""
    exit 1
else
    echo -e "  ${GREEN}ALL SYSTEMS HEALTHY${NC}"
    echo "═══════════════════════════════════════"
    echo ""
    exit 0
fi
