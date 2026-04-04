# ============================================================
# NGROK TUNNEL WATCHDOG — Windows PowerShell
# ============================================================
# Monitors the Ngrok tunnel and restarts it if disconnected.
# Schedule via Task Scheduler every 2 minutes.
#
# Usage: powershell -ExecutionPolicy Bypass -File tunnel-monitor.ps1
# ============================================================

$MCP_PORT = if ($env:MCP_PORT) { $env:MCP_PORT } else { "3000" }
$NGROK_API = "http://localhost:4040/api/tunnels"
$MAX_RETRIES = 3
$RETRY_DELAY = 10  # seconds

# Log setup
$LogDir = "$env:USERPROFILE\home-lab\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$LogFile = Join-Path $LogDir "tunnel-$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp [tunnel-watchdog] $Message" | Out-File -Append -FilePath $LogFile
}

function Test-Tunnel {
    try {
        $response = Invoke-WebRequest -Uri $NGROK_API -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $data = $response.Content | ConvertFrom-Json
        return ($data.tunnels.Count -gt 0)
    } catch {
        return $false
    }
}

function Restart-Tunnel {
    Write-Log "Attempting to restart Ngrok tunnel..."

    # Kill existing ngrok
    $ngrokProcs = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
    if ($ngrokProcs) {
        $ngrokProcs | Stop-Process -Force
        Start-Sleep -Seconds 3
    }

    # Start ngrok in background
    # Adjust the path to ngrok.exe if it's not in your PATH
    try {
        Start-Process -FilePath "ngrok" -ArgumentList "http", $MCP_PORT -WindowStyle Hidden -ErrorAction Stop
    } catch {
        # Try common install locations
        $ngrokPaths = @(
            "$env:USERPROFILE\ngrok\ngrok.exe",
            "$env:USERPROFILE\Downloads\ngrok.exe",
            "C:\ngrok\ngrok.exe",
            "$env:LOCALAPPDATA\ngrok\ngrok.exe"
        )
        $found = $false
        foreach ($path in $ngrokPaths) {
            if (Test-Path $path) {
                Start-Process -FilePath $path -ArgumentList "http", $MCP_PORT -WindowStyle Hidden
                $found = $true
                break
            }
        }
        if (-not $found) {
            Write-Log "ERROR: ngrok.exe not found in PATH or common locations"
            return $false
        }
    }

    # Wait for tunnel to establish
    Start-Sleep -Seconds 5

    if (Test-Tunnel) {
        try {
            $response = Invoke-WebRequest -Uri $NGROK_API -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            $data = $response.Content | ConvertFrom-Json
            $newUrl = $data.tunnels[0].public_url
            Write-Log "Tunnel restored: $newUrl"
        } catch {
            Write-Log "Tunnel restored (couldn't read URL)"
        }
        return $true
    } else {
        Write-Log "Tunnel failed to restart"
        return $false
    }
}

# --- Main Logic ---

if (Test-Tunnel) {
    # Tunnel is healthy — only log every 30 minutes
    $minute = (Get-Date).Minute
    if ($minute % 30 -eq 0) {
        Write-Log "Tunnel healthy"
    }
    exit 0
}

# Tunnel is down — recovery mode
Write-Log "ALERT: Tunnel is DOWN. Starting recovery..."

for ($i = 1; $i -le $MAX_RETRIES; $i++) {
    Write-Log "Recovery attempt $i/$MAX_RETRIES..."
    
    if (Restart-Tunnel) {
        Write-Log "Recovery successful on attempt $i"
        exit 0
    }

    Write-Log "Attempt $i failed, waiting ${RETRY_DELAY}s..."
    Start-Sleep -Seconds $RETRY_DELAY
}

Write-Log "CRITICAL: Tunnel recovery FAILED after $MAX_RETRIES attempts. Manual intervention required."
exit 2
