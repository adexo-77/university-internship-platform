<#
.SYNOPSIS
    Expose local demo instance over temporary Cloudflare Quick Tunnel.

.DESCRIPTION
    Runs cloudflared quick tunnel pointing to http://localhost:8080 with
    public demo mode protections, timeout enforcement, and optional cleanup.

.PARAMETER Minutes
    Duration in minutes to keep tunnel open (default 120, clamped 1-480).

.PARAMETER AllowedMail
    Optional comma-separated email addresses or wildcard domains allowed access.

.PARAMETER ResetAfter
    When specified, tears down docker compose containers and volumes on exit.
#>

[CmdletBinding()]
param(
    [int]$Minutes = 120,
    [string]$AllowedMail = "",
    [switch]$ResetAfter
)

# Clamp runtime between 1 and 480 minutes (8 hours maximum)
if ($Minutes -lt 1) {
    $Minutes = 1
} elseif ($Minutes -gt 480) {
    $Minutes = 480
}

# Verify cloudflared executable exists
$cloudflaredCmd = Get-Command "cloudflared" -ErrorAction SilentlyContinue
if (-not $cloudflaredCmd) {
    Write-Error "cloudflared is not installed or not in PATH.`nInstall it with: winget install --id Cloudflare.cloudflared"
    exit 1
}

# Helper to check local demo health endpoint
function Test-DemoHealth {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:8080/api/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        return ($res.status -eq "ok")
    } catch {
        return $false
    }
}

# Ensure local stack is running with DEMO_PUBLIC_MODE=true
if (-not (Test-DemoHealth)) {
    Write-Host "Demo stack is not running. Starting containers with DEMO_PUBLIC_MODE=true..." -ForegroundColor Cyan
    $env:DEMO_PUBLIC_MODE = "true"
    docker compose up -d --wait
    if ($LASTEXITCODE -ne 0 -or -not (Test-DemoHealth)) {
        Write-Error "Failed to start healthy demo stack on http://localhost:8080"
        exit 1
    }
    Write-Host "Demo stack is up and operational." -ForegroundColor Green
}

# Build cloudflared command arguments
$cfArgs = @("tunnel", "--url", "http://localhost:8080")
if ($AllowedMail -and $AllowedMail.Trim() -ne "") {
    $cfArgs += @("--allowed-mail", $AllowedMail.Trim())
}

# Display public warning banner
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host " WARNING: PUBLIC DEMO ACCESS" -ForegroundColor Yellow
Write-Host " Anyone with the link will be able to access this demo instance." -ForegroundColor Yellow
Write-Host " Active duration : $Minutes minute(s)" -ForegroundColor Yellow
if ($AllowedMail -and $AllowedMail.Trim() -ne "") {
    Write-Host " Restricted to   : $AllowedMail" -ForegroundColor Green
} else {
    Write-Host " Access          : Open to anyone with the link" -ForegroundColor Yellow
}
Write-Host " Termination     : Auto-stops after $Minutes minute(s) or on Ctrl+C" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host ""

$proc = $null
try {
    # Launch cloudflared process
    $proc = Start-Process -FilePath "cloudflared" -ArgumentList $cfArgs -PassThru -NoNewWindow
    $targetTime = (Get-Date).AddMinutes($Minutes)

    Write-Host "Tunnel process started (PID: $($proc.Id)). Connecting to Cloudflare..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to close the tunnel immediately.`n" -ForegroundColor DarkGray

    while ((Get-Date) -lt $targetTime -and -not $proc.HasExited) {
        Start-Sleep -Seconds 1
    }

    if ($proc.HasExited) {
        Write-Host "Tunnel process exited unexpectedly (ExitCode: $($proc.ExitCode))." -ForegroundColor Red
    } else {
        Write-Host "`nTime limit of $Minutes minute(s) reached. Shutting down tunnel..." -ForegroundColor Yellow
    }
} finally {
    if ($proc -and -not $proc.HasExited) {
        Write-Host "Stopping cloudflared process (PID: $($proc.Id))..." -ForegroundColor Cyan
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit(5000)
    }

    if ($ResetAfter) {
        Write-Host "ResetAfter enabled: resetting Docker Compose volumes and demo state..." -ForegroundColor Cyan
        docker compose down -v
        Write-Host "Demo stack teardown complete." -ForegroundColor Green
    }

    Write-Host "Share session ended cleanly." -ForegroundColor Green
}
