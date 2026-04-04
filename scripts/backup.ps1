# ============================================================
# HOME LAB BACKUP — Windows PowerShell
# ============================================================
# Backs up critical configs, databases, and env files.
# Schedule via Task Scheduler daily at 3:00 AM.
#
# Usage: powershell -ExecutionPolicy Bypass -File backup.ps1
# ============================================================

$BackupRoot = "$env:USERPROFILE\backups"
$RetentionDays = 7
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "homelab_$Timestamp"
$BackupPath = Join-Path $BackupRoot $BackupName

# Adjust these to match your actual project locations
$McpDir = "D:\SocialMediaMcp"                           # or wherever social-media-mcp lives
$ContentDir = "$env:USERPROFILE\Desktop\fb-content-system"  # adjust to actual path
$HomeLab = "$env:USERPROFILE\git-init-home-lab"

# Log setup
$LogDir = "$env:USERPROFILE\home-lab\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$LogFile = Join-Path $LogDir "backup-$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp [backup] $Message" | Out-File -Append -FilePath $LogFile
    Write-Host "  $Message"
}

Write-Log "Starting backup: $BackupName"
New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null

# --- 1. Environment Files ---
Write-Log "Backing up environment files..."
$envDir = Join-Path $BackupPath "env"
New-Item -ItemType Directory -Path $envDir -Force | Out-Null

$envFiles = @(
    "$McpDir\.env",
    "$ContentDir\tools\.env",
    "$HomeLab\.env"
)
foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        $parent = Split-Path (Split-Path $envFile) -Leaf
        Copy-Item $envFile -Destination (Join-Path $envDir "${parent}_.env")
        Write-Log "  Copied: $envFile"
    }
}

# --- 2. SQLite Databases ---
Write-Log "Backing up databases..."
$dbDir = Join-Path $BackupPath "databases"
New-Item -ItemType Directory -Path $dbDir -Force | Out-Null

$searchDirs = @($McpDir, $ContentDir)
foreach ($dir in $searchDirs) {
    if (Test-Path $dir) {
        Get-ChildItem -Path $dir -Recurse -Include "*.sqlite", "*.sqlite3", "*.db" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notlike "*node_modules*" } |
        ForEach-Object {
            Copy-Item $_.FullName -Destination $dbDir
            Write-Log "  Backed up: $($_.Name)"
        }
    }
}

# --- 3. Ngrok Config ---
Write-Log "Backing up configurations..."
$configDir = Join-Path $BackupPath "configs"
New-Item -ItemType Directory -Path $configDir -Force | Out-Null

$ngrokConfig = "$env:USERPROFILE\.config\ngrok\ngrok.yml"
if (-not (Test-Path $ngrokConfig)) {
    $ngrokConfig = "$env:USERPROFILE\AppData\Local\ngrok\ngrok.yml"
}
if (Test-Path $ngrokConfig) {
    Copy-Item $ngrokConfig -Destination $configDir
    Write-Log "  Copied: ngrok.yml"
}

# --- 4. Page Brand Data ---
Write-Log "Backing up page brand data..."
$pageDir = Join-Path $BackupPath "page-data"
New-Item -ItemType Directory -Path $pageDir -Force | Out-Null

foreach ($page in @("mea", "a2b", "atu")) {
    $pagePath = Join-Path $ContentDir $page
    if (Test-Path $pagePath) {
        $destDir = Join-Path $pageDir $page
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        Get-ChildItem -Path $pagePath -Filter "*.json" -ErrorAction SilentlyContinue |
        ForEach-Object { Copy-Item $_.FullName -Destination $destDir }
        Write-Log "  Backed up: $page/ brand data"
    }
}

# --- 5. Session Data ---
Write-Log "Backing up sessions..."
$sessDir = Join-Path $BackupPath "sessions"
$mcpSessions = Join-Path $McpDir "sessions"
if (Test-Path $mcpSessions) {
    Copy-Item -Path $mcpSessions -Destination $sessDir -Recurse
    Write-Log "  Copied MCP sessions"
}

# --- 6. Compress ---
Write-Log "Compressing backup..."
$zipPath = "$BackupRoot\$BackupName.zip"
Compress-Archive -Path $BackupPath -DestinationPath $zipPath -Force
Remove-Item -Path $BackupPath -Recurse -Force
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Log "Compressed: $BackupName.zip (${zipSize}MB)"

# --- 7. Retention Cleanup ---
Write-Log "Cleaning up old backups (keeping $RetentionDays days)..."
$cutoff = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupRoot -Filter "homelab_*.zip" |
Where-Object { $_.LastWriteTime -lt $cutoff } |
ForEach-Object {
    Remove-Item $_.FullName -Force
    Write-Log "  Deleted: $($_.Name)"
}

# --- Summary ---
$totalBackups = (Get-ChildItem -Path $BackupRoot -Filter "homelab_*.zip").Count
$totalSize = [math]::Round((Get-ChildItem -Path $BackupRoot -Filter "homelab_*.zip" | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Log "Backup complete. $totalBackups backups stored (${totalSize}MB total)"
Write-Log "---"
