# ============================================================
# SETUP TASK SCHEDULER — Run Once as Administrator
# ============================================================
# Creates three scheduled tasks:
#   1. Health Check     — every 5 minutes
#   2. Tunnel Monitor   — every 2 minutes
#   3. Daily Backup     — 3:00 AM daily
#
# Usage: Right-click → Run as Administrator
#   powershell -ExecutionPolicy Bypass -File setup-tasks.ps1
# ============================================================

$ScriptDir = "$env:USERPROFILE\home-lab\scripts"

# Verify scripts exist
$scripts = @(
    @{ Name = "health-check.ps1"; Desc = "Health Check" },
    @{ Name = "tunnel-monitor.ps1"; Desc = "Tunnel Monitor" },
    @{ Name = "backup.ps1"; Desc = "Backup" }
)

foreach ($s in $scripts) {
    $path = Join-Path $ScriptDir $s.Name
    if (-not (Test-Path $path)) {
        Write-Host "[ERROR] Missing: $path" -ForegroundColor Red
        Write-Host "Copy the PowerShell scripts to $ScriptDir first." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Setting up Home Lab scheduled tasks..." -ForegroundColor Cyan
Write-Host ""

# --- Common settings ---
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$PowerShell = (Get-Command powershell).Source

# --- 1. Health Check (every 5 minutes) ---
Write-Host "  Creating: HomeLab-HealthCheck (every 5 min)..." -ForegroundColor Yellow

$trigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)
$action1 = New-ScheduledTaskAction -Execute $PowerShell -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptDir\health-check.ps1`""
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Remove existing task if present
Unregister-ScheduledTask -TaskName "HomeLab-HealthCheck" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "HomeLab-HealthCheck" -Trigger $trigger1 -Action $action1 -Settings $settings1 -Description "Home Lab health check — monitors MCP server, Ngrok tunnel, disk, memory" -RunLevel Highest | Out-Null

Write-Host "  [OK] HomeLab-HealthCheck created" -ForegroundColor Green

# --- 2. Tunnel Monitor (every 2 minutes) ---
Write-Host "  Creating: HomeLab-TunnelMonitor (every 2 min)..." -ForegroundColor Yellow

$trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration ([TimeSpan]::MaxValue)
$action2 = New-ScheduledTaskAction -Execute $PowerShell -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptDir\tunnel-monitor.ps1`""
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

Unregister-ScheduledTask -TaskName "HomeLab-TunnelMonitor" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "HomeLab-TunnelMonitor" -Trigger $trigger2 -Action $action2 -Settings $settings2 -Description "Home Lab Ngrok tunnel watchdog — auto-restarts on disconnect" -RunLevel Highest | Out-Null

Write-Host "  [OK] HomeLab-TunnelMonitor created" -ForegroundColor Green

# --- 3. Daily Backup (3:00 AM) ---
Write-Host "  Creating: HomeLab-Backup (daily 3:00 AM)..." -ForegroundColor Yellow

$trigger3 = New-ScheduledTaskTrigger -Daily -At "3:00AM"
$action3 = New-ScheduledTaskAction -Execute $PowerShell -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptDir\backup.ps1`""
$settings3 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun

Unregister-ScheduledTask -TaskName "HomeLab-Backup" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "HomeLab-Backup" -Trigger $trigger3 -Action $action3 -Settings $settings3 -Description "Home Lab daily backup — configs, databases, page data" -RunLevel Highest | Out-Null

Write-Host "  [OK] HomeLab-Backup created" -ForegroundColor Green

# --- Verify ---
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  All tasks registered. Verifying..." -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$tasks = @("HomeLab-HealthCheck", "HomeLab-TunnelMonitor", "HomeLab-Backup")
foreach ($taskName in $tasks) {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "  [OK] $taskName — Status: $($task.State)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $taskName — Not found!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  Logs will be written to: $env:USERPROFILE\home-lab\logs\" -ForegroundColor Gray
Write-Host "  Backups will be stored in: $env:USERPROFILE\backups\" -ForegroundColor Gray
Write-Host ""
Write-Host "  To view tasks: Open Task Scheduler → search 'HomeLab'" -ForegroundColor Gray
Write-Host "  To test now:   powershell -File `"$ScriptDir\health-check.ps1`"" -ForegroundColor Gray
Write-Host ""
