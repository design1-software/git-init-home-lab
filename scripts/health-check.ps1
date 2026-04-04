# ============================================================
# HOME LAB HEALTH CHECK — Windows PowerShell
# ============================================================
# Checks all critical services and reports status.
# Schedule via Task Scheduler every 5 minutes.
#
# Usage: powershell -ExecutionPolicy Bypass -File health-check.ps1
# ============================================================

$MCP_PORT = if ($env:MCP_PORT) { $env:MCP_PORT } else { "3000" }
$MCP_HEALTH_URL = "http://localhost:$MCP_PORT/health"
$NGROK_API = "http://localhost:4040/api/tunnels"
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

# --- 1. MCP Server ---
Write-Host "  MCP Server (social-media-mcp)"
Write-Host "  -----------------------------"
try {
    $response = Invoke-WebRequest -Uri $MCP_HEALTH_URL -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Log "OK" "MCP server responding on :$MCP_PORT (HTTP $($response.StatusCode))"
} catch {
    # Check if process is at least listening on the port
    $listening = Get-NetTCPConnection -LocalPort $MCP_PORT -State Listen -ErrorAction SilentlyContinue
    if ($listening) {
        Write-Log "WARN" "MCP process on :$MCP_PORT but /health not responding"
        $Warnings++
    } else {
        Write-Log "FAIL" "MCP server NOT running on :$MCP_PORT"
        $Failures++
    }
}

# --- 2. Ngrok Tunnel ---
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

# --- 3. Disk Usage ---
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

# --- 4. Memory ---
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

# --- 5. Node.js Processes ---
Write-Host ""
Write-Host "  Key Processes"
Write-Host "  -----------------------------"
$nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcs) {
    $nodeCount = @($nodeProcs).Count
    $totalMem = [math]::Round(($nodeProcs | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB)
    Write-Log "OK" "$nodeCount Node.js process(es) running (${totalMem}MB total)"
} else {
    Write-Log "WARN" "No Node.js processes found"
    $Warnings++
}

# Check for ngrok process
$ngrokProc = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
if ($ngrokProc) {
    Write-Log "OK" "Ngrok process running"
} else {
    Write-Log "WARN" "Ngrok process not found"
    $Warnings++
}

# --- 6. Network ---
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
