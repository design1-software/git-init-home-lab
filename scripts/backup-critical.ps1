# ============================================================
# HOME LAB BACKUP — Critical Files
# ============================================================
# Backs up .env files, SQLite databases, CUPS config, Docker 
# compose files, and other non-recoverable data to D:\ drive.
#
# Usage: powershell -ExecutionPolicy Bypass -File backup-critical.ps1
# Schedule: Task Scheduler, weekly (or before any major change)
#
# IMPORTANT: After running, copy the latest backup folder to an
# off-machine location (iCloud, Google Drive, USB stick).
# The D:\ drive protects against C:\ failure but NOT against
# theft, fire, or power surge that takes out the whole Acer.
# ============================================================

$BackupRoot = "D:\home-lab-backups"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$BackupDir = Join-Path $BackupRoot $Timestamp

# Create backup directory
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host ""
Write-Host "======================================="
Write-Host "  Home Lab Backup — $Timestamp"
Write-Host "  Destination: $BackupDir"
Write-Host "======================================="
Write-Host ""

$Copied = 0
$Failed = 0

function Backup-Item {
    param([string]$Source, [string]$DestSubfolder, [string]$Label)
    
    $dest = Join-Path $BackupDir $DestSubfolder
    
    if (Test-Path $Source) {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        
        if ((Get-Item $Source).PSIsContainer) {
            # Directory — copy recursively
            Copy-Item -Path "$Source\*" -Destination $dest -Recurse -Force
        } else {
            # Single file
            Copy-Item -Path $Source -Destination $dest -Force
        }
        
        Write-Host "  [OK]   $Label" -ForegroundColor Green
        $script:Copied++
    } else {
        Write-Host "  [SKIP] $Label — not found at $Source" -ForegroundColor Yellow
        $script:Failed++
    }
}

# --- 1. Environment files (API keys, secrets — MOST CRITICAL) ---
Write-Host "  Secrets & Environment"
Write-Host "  -----------------------------"
Backup-Item "C:\Users\jbm06\social-media-mcp\.env" "secrets\social-media-mcp" ".env (social-media-mcp)"

# --- 2. Docker configuration ---
Write-Host ""
Write-Host "  Docker Configuration"
Write-Host "  -----------------------------"
Backup-Item "C:\Users\jbm06\social-media-mcp\Dockerfile" "docker\social-media-mcp" "Dockerfile"
Backup-Item "C:\Users\jbm06\social-media-mcp\docker-compose.yml" "docker\social-media-mcp" "docker-compose.yml"
Backup-Item "C:\Users\jbm06\social-media-mcp\.dockerignore" "docker\social-media-mcp" ".dockerignore"
Backup-Item "C:\Users\jbm06\social-media-mcp\.env.example" "docker\social-media-mcp" ".env.example"

# --- 3. closet-monitor data (SQLite + config) ---
Write-Host ""
Write-Host "  closet-monitor Data"
Write-Host "  -----------------------------"
# Adjust these paths if your closet-monitor files are in a different location
Backup-Item "C:\Users\jbm06\closet-monitor" "closet-monitor" "closet-monitor directory"

# --- 4. MCP sessions and storage metadata ---
Write-Host ""
Write-Host "  MCP Sessions & Storage"
Write-Host "  -----------------------------"
Backup-Item "C:\Users\jbm06\social-media-mcp\sessions" "mcp\sessions" "MCP sessions"
# Note: storage/ contains rendered media (large). Back up selectively.
# Full storage backup is optional — uncomment the next line if you want it:
# Backup-Item "C:\Users\jbm06\social-media-mcp\storage" "mcp\storage" "MCP storage (media)"

# --- 5. Home lab scripts and docs ---
Write-Host ""
Write-Host "  Home Lab Repo (local copy)"
Write-Host "  -----------------------------"
Backup-Item "C:\Users\jbm06\git-init-home-lab" "git-init-home-lab" "Home lab repo"

# --- 6. Tailscale config ---
Write-Host ""
Write-Host "  Tailscale"
Write-Host "  -----------------------------"
$tailscaleDir = "$env:LOCALAPPDATA\Tailscale"
if (Test-Path $tailscaleDir) {
    Backup-Item $tailscaleDir "tailscale" "Tailscale config"
} else {
    Write-Host "  [SKIP] Tailscale config — not found" -ForegroundColor Yellow
}

# --- 7. PowerPanel config ---
Write-Host ""
Write-Host "  PowerPanel (UPS)"
Write-Host "  -----------------------------"
$ppDir = "C:\Program Files (x86)\CyberPower PowerPanel Personal"
if (Test-Path $ppDir) {
    Backup-Item $ppDir "powerpanel" "PowerPanel config"
} else {
    Write-Host "  [SKIP] PowerPanel — not found at expected path" -ForegroundColor Yellow
}

# --- 8. Create manifest ---
Write-Host ""
Write-Host "  Creating manifest..."
$manifest = @"
Home Lab Backup Manifest
========================
Date: $Timestamp
Host: $env:COMPUTERNAME
User: $env:USERNAME

Files backed up: $Copied
Files skipped:   $Failed

Contents:
- secrets/          .env files (API keys, tokens)
- docker/           Dockerfile, docker-compose.yml, .dockerignore
- closet-monitor/   SQLite database, Python scripts, sensor data
- mcp/              MCP session state
- git-init-home-lab/ Home lab documentation repo
- tailscale/        Tailscale VPN config
- powerpanel/       UPS shutdown config

CRITICAL REMINDER:
Copy this backup folder to an OFF-MACHINE location:
- iCloud Drive
- Google Drive
- USB stick stored away from the Acer
- NAS (when deployed)

The D:\ drive protects against C:\ SSD failure only.
It does NOT protect against theft, fire, surge, or
physical damage to the Acer.
"@

[System.IO.File]::WriteAllText((Join-Path $BackupDir "MANIFEST.txt"), $manifest)

# --- 9. Prune old backups (keep last 5) ---
$allBackups = Get-ChildItem -Path $BackupRoot -Directory | Sort-Object Name -Descending
if ($allBackups.Count -gt 5) {
    $toDelete = $allBackups | Select-Object -Skip 5
    foreach ($old in $toDelete) {
        Remove-Item -Path $old.FullName -Recurse -Force
        Write-Host "  [PRUNE] Removed old backup: $($old.Name)" -ForegroundColor DarkGray
    }
}

# --- Summary ---
Write-Host ""
Write-Host "======================================="
if ($Failed -eq 0) {
    Write-Host "  BACKUP COMPLETE: $Copied items backed up" -ForegroundColor Green
} else {
    Write-Host "  BACKUP PARTIAL: $Copied backed up, $Failed skipped" -ForegroundColor Yellow
}
Write-Host "  Location: $BackupDir"
Write-Host "  Size: $([math]::Round((Get-ChildItem $BackupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1))MB"
Write-Host "======================================="
Write-Host ""
Write-Host "  >> REMINDER: Copy this backup to iCloud/Google Drive/USB <<" -ForegroundColor Cyan
Write-Host ""
