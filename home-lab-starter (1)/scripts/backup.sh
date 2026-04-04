#!/bin/bash
# ============================================================
# HOME LAB BACKUP SCRIPT
# ============================================================
# Backs up critical configs, databases, and env files.
# Does NOT back up node_modules, media assets, or git repos
# (those can be rebuilt from source).
#
# Run daily via cron:
#   0 3 * * * /path/to/backup.sh >> /home/user/home-lab/logs/backup.log 2>&1
#
# Retention: 7 daily backups (configurable)
# ============================================================

set -euo pipefail

# --- Configuration ---
BACKUP_DIR="${HOME}/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="homelab_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Directories to back up (adjust paths to your setup)
MCP_DIR="${HOME}/social-media-mcp"
CONTENT_DIR="${HOME}/fb-content-system"
HOME_LAB_DIR="${HOME}/home-lab"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(timestamp) [backup] $1"; }

# --- Pre-flight ---
log "Starting backup: ${BACKUP_NAME}"
mkdir -p "$BACKUP_PATH"

# --- 1. Environment Files ---
log "Backing up environment files..."
mkdir -p "${BACKUP_PATH}/env"
for envfile in "${MCP_DIR}/.env" "${CONTENT_DIR}/tools/.env" "${HOME_LAB_DIR}/.env"; do
    if [ -f "$envfile" ]; then
        cp "$envfile" "${BACKUP_PATH}/env/$(basename $(dirname $envfile))_$(basename $envfile)"
        log "  Copied: $envfile"
    fi
done

# --- 2. SQLite Databases ---
log "Backing up SQLite databases..."
mkdir -p "${BACKUP_PATH}/databases"
find "${MCP_DIR}" "${CONTENT_DIR}" -name "*.sqlite" -o -name "*.sqlite3" -o -name "*.db" 2>/dev/null | while read dbfile; do
    if [ -f "$dbfile" ]; then
        # Use sqlite3 .backup for consistency (if available), otherwise cp
        if command -v sqlite3 &> /dev/null; then
            sqlite3 "$dbfile" ".backup '${BACKUP_PATH}/databases/$(basename $dbfile)'"
        else
            cp "$dbfile" "${BACKUP_PATH}/databases/"
        fi
        log "  Backed up: $(basename $dbfile)"
    fi
done

# --- 3. Configuration Files ---
log "Backing up configuration files..."
mkdir -p "${BACKUP_PATH}/configs"

# Ngrok config
NGROK_CONF="${HOME}/.config/ngrok/ngrok.yml"
if [ -f "$NGROK_CONF" ]; then
    cp "$NGROK_CONF" "${BACKUP_PATH}/configs/ngrok.yml"
    log "  Copied: ngrok.yml"
fi

# PM2 ecosystem (if exists)
for ecosys in "${MCP_DIR}/ecosystem.config.js" "${HOME}/ecosystem.config.js"; do
    if [ -f "$ecosys" ]; then
        cp "$ecosys" "${BACKUP_PATH}/configs/$(basename $ecosys)"
        log "  Copied: ecosystem.config.js"
    fi
done

# Docker compose (if exists)
for compose in "${HOME}/docker-compose.yml" "${HOME_LAB_DIR}/docker-compose.yml"; do
    if [ -f "$compose" ]; then
        cp "$compose" "${BACKUP_PATH}/configs/docker-compose.yml"
        log "  Copied: docker-compose.yml"
    fi
done

# --- 4. Page Brand Data (fb-content-system) ---
log "Backing up page brand data..."
mkdir -p "${BACKUP_PATH}/page-data"
for page_dir in "${CONTENT_DIR}/mea" "${CONTENT_DIR}/a2b" "${CONTENT_DIR}/atu"; do
    if [ -d "$page_dir" ]; then
        page_name=$(basename "$page_dir")
        mkdir -p "${BACKUP_PATH}/page-data/${page_name}"
        cp "${page_dir}"/*.json "${BACKUP_PATH}/page-data/${page_name}/" 2>/dev/null || true
        log "  Backed up: ${page_name}/ brand data"
    fi
done

# --- 5. Session Data ---
log "Backing up session data..."
mkdir -p "${BACKUP_PATH}/sessions"
if [ -d "${MCP_DIR}/sessions" ]; then
    cp -r "${MCP_DIR}/sessions/"* "${BACKUP_PATH}/sessions/" 2>/dev/null || true
    log "  Copied MCP sessions"
fi

# --- 6. Home Lab Docs ---
log "Backing up home lab documentation..."
if [ -d "${HOME_LAB_DIR}/docs" ]; then
    cp -r "${HOME_LAB_DIR}/docs" "${BACKUP_PATH}/home-lab-docs"
    log "  Copied home-lab docs/"
fi

# --- 7. Compress ---
log "Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_PATH"
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
log "Compressed: ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"

# --- 8. Retention Cleanup ---
log "Cleaning up old backups (keeping ${RETENTION_DAYS} days)..."
DELETED=0
find "$BACKUP_DIR" -name "homelab_*.tar.gz" -type f -mtime +"$RETENTION_DAYS" | while read old; do
    rm "$old"
    log "  Deleted: $(basename $old)"
    ((DELETED++)) || true
done

# --- Summary ---
TOTAL_BACKUPS=$(ls -1 "${BACKUP_DIR}"/homelab_*.tar.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
log "Backup complete. ${TOTAL_BACKUPS} backups stored (${TOTAL_SIZE} total)"
log "─────────────────────────────────"
