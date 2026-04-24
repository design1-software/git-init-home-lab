# ============================================================
# HOME LAB HEALTH CHECK — Windows PowerShell (Docker-aware)
# ============================================================
# Checks all critical services and reports status.
# Schedule via Task Scheduler every 5 minutes.
#
# Usage: powershell -ExecutionPolicy Bypass -File health-check.ps1
# ============================================================

$MCP_PORT = if ($env:MCP_PORT) { $env:MCP_PORT } else { "3000" }
$MCP_HEALTH_URL = "http://localhost:$MCP_PORT/health"
$NGROK_API = "http://localhost:4040/api/tunnels"
$NGROK_EXTERNAL = "https://mea.ngrok.app/health"
$DISK_WARN_PERCENT = 85
$MEM_WARN_PERCENT = 90

# Log setup
$LogDir = "$env:USERPROFILE\home-lab\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$LogFile = Join-Path $LogDir "health-$(Get-Date -Format 'yyyyMMdd').log"

$Failures = 0
$Warnings = 0

function Write-Log {
    param([string]$Level, [string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp [$Level] $Message" | Out-File -Append -FilePath $LogFile
    switch ($Level) {
        "OK"   { Write-Host "  [OK]   $Message" -ForegroundColor Green }
        "WARN" { Write-Host "  [WARN] $Message" -ForegroundColor Yellow }
        "FAIL" { Write-Host "  [FAIL] $Message" -ForegroundColor Red }
        default { Write-Host "  $Message" }
    }
}

Write-Host ""
Write-Host "=======================================" 
Write-Host "  Home Lab Health Check — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "======================================="
Write-Host ""

# --- 1. Docker Desktop ---
Write-Host "  Docker Desktop"
Write-Host "  -----------------------------"
$dockerProc = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProc) {
    Write-Log "OK" "Docker Desktop running"
} else {
    Write-Log "FAIL" "Docker Desktop NOT running"
    $Failures++
}

# --- 2. Docker Containers ---
Write-Host ""
Write-Host "  Docker Containers"
Write-Host "  -----------------------------"
try {
    $composeDir = "C:\Users\jbm06\social-media-mcp"
    $containers = docker compose -f "$composeDir\docker-compose.yml" ps --format json 2>$null | ConvertFrom-Json
    
    if ($containers) {
        foreach ($c in $containers) {
            $name = $c.Name
            $state = $c.State
            $health = $c.Health
            
            if ($state -eq "running") {
                if ($health -eq "healthy" -or $health -eq "") {
                    Write-Log "OK" "$name — $state $(if($health){"($health)"})"
                } else {
                    Write-Log "WARN" "$name — $state ($health)"
                    $Warnings++
                }
            } else {
                Write-Log "FAIL" "$name — $state"
                $Failures++
            }
        }
    } else {
        Write-Log "FAIL" "No Docker containers found"
        $Failures++
    }
} catch {
    Write-Log "FAIL" "Could not query Docker containers: $($_.Exception.Message)"
    $Failures++
}

# --- 3. MCP Server Health ---
Write-Host ""
Write-Host "  MCP Server (social-media-mcp)"
Write-Host "  -----------------------------"
try {
    $response = Invoke-WebRequest -Uri $MCP_HEALTH_URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    $healthData = $response.Content | ConvertFrom-Json
    Write-Log "OK" "MCP server healthy — v$($healthData.version), storage: $($healthData.storage.status)"
} catch {
    Write-Log "FAIL" "MCP server NOT responding on :$MCP_PORT"
    $Failures++
}

# --- 4. Ngrok Tunnel (Local) ---
Write-Host ""
Write-Host "  Ngrok Tunnel"
Write-Host "  -----------------------------"
try {
    $tunnelResponse = Invoke-WebRequest -Uri $NGROK_API -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    $tunnelData = $tunnelResponse.Content | ConvertFrom-Json
    if ($tunnelData.tunnels.Count -gt 0) {
        $publicUrl = $tunnelData.tunnels[0].public_url
        Write-Log "OK" "Ngrok tunnel active: $publicUrl"
    } else {
        Write-Log "WARN" "Ngrok API responding but no active tunnels"
        $Warnings++
    }
} catch {
    Write-Log "FAIL" "Ngrok not responding (tunnel may be down)"
    $Failures++
}

# --- 5. External Reachability ---
Write-Host ""
Write-Host "  External Access (mea.ngrok.app)"
Write-Host "  -----------------------------"
try {
    $extResponse = Invoke-WebRequest -Uri $NGROK_EXTERNAL -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Log "OK" "External health check passed (HTTP $($extResponse.StatusCode))"
} catch {
    Write-Log "FAIL" "External health check failed — Railway cannot reach MCP"
    $Failures++
}

# --- 6. Disk Usage ---
Write-Host ""
Write-Host "  Disk Usage"
Write-Host "  -----------------------------"
$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskPercent = [math]::Round(($disk.Size - $disk.FreeSpace) / $disk.Size * 100)
$diskFreeGB = [math]::Round($disk.FreeSpace / 1GB, 1)
if ($diskPercent -ge $DISK_WARN_PERCENT) {
    Write-Log "WARN" "C: drive at ${diskPercent}% (${diskFreeGB}GB free)"
    $Warnings++
} else {
    Write-Log "OK" "C: drive at ${diskPercent}% (${diskFreeGB}GB free)"
}

# Check D: drive if it exists (media storage)
$diskD = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='D:'" -ErrorAction SilentlyContinue
if ($diskD) {
    $diskDPercent = [math]::Round(($diskD.Size - $diskD.FreeSpace) / $diskD.Size * 100)
    $diskDFreeGB = [math]::Round($diskD.FreeSpace / 1GB, 1)
    if ($diskDPercent -ge $DISK_WARN_PERCENT) {
        Write-Log "WARN" "D: drive at ${diskDPercent}% (${diskDFreeGB}GB free)"
        $Warnings++
    } else {
        Write-Log "OK" "D: drive at ${diskDPercent}% (${diskDFreeGB}GB free)"
    }
}

# --- 7. Memory ---
Write-Host ""
Write-Host "  Memory"
Write-Host "  -----------------------------"
$os = Get-WmiObject Win32_OperatingSystem
$memTotal = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$memFree = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$memUsed = $memTotal - $memFree
$memPercent = [math]::Round($memUsed / $memTotal * 100)
if ($memPercent -ge $MEM_WARN_PERCENT) {
    Write-Log "WARN" "Memory at ${memPercent}% (${memUsed}GB / ${memTotal}GB)"
    $Warnings++
} else {
    Write-Log "OK" "Memory at ${memPercent}% (${memUsed}GB / ${memTotal}GB)"
}

# --- 8. Docker Resource Usage ---
Write-Host ""
Write-Host "  Docker Resources"
Write-Host "  -----------------------------"
try {
    $stats = docker stats --no-stream --format "{{.Name}}: CPU {{.CPUPerc}}, Mem {{.MemUsage}}" 2>$null
    if ($stats) {
        foreach ($line in $stats) {
            Write-Log "OK" $line
        }
    }
} catch {
    Write-Log "WARN" "Could not query Docker resource stats"
    $Warnings++
}

# --- 9. Network ---
Write-Host ""
Write-Host "  Network"
Write-Host "  -----------------------------"
$ping = Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($ping) {
    Write-Log "OK" "Internet connectivity OK"
} else {
    Write-Log "FAIL" "No internet connectivity"
    $Failures++
}

# --- Summary ---
Write-Host ""
Write-Host "======================================="
if ($Failures -gt 0) {
    Write-Host "  CRITICAL: $Failures failure(s), $Warnings warning(s)" -ForegroundColor Red
    $exitCode = 2
} elseif ($Warnings -gt 0) {
    Write-Host "  DEGRADED: $Warnings warning(s)" -ForegroundColor Yellow
    $exitCode = 1
} else {
    Write-Host "  ALL SYSTEMS HEALTHY" -ForegroundColor Green
    $exitCode = 0
}
Write-Host "======================================="
Write-Host ""

exit $exitCode
