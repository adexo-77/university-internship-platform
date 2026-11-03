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
function Get-StackHealth {
    try {
        $raw = curl.exe -s -m 3 "http://127.0.0.1:8080/api/health"
        if ($raw) {
            return ($raw | ConvertFrom-Json)
        }
        return $null
    } catch {
        return $null
    }
}

$needRestoreNormalMode = $false
$initialHealth = Get-StackHealth

# Ensure stack is running and guarantee DEMO_PUBLIC_MODE=true
if (-not $initialHealth -or $initialHealth.status -ne "ok") {
    Write-Host "Local demo stack is down. Starting containers with DEMO_PUBLIC_MODE=true..." -ForegroundColor Cyan
    $env:DEMO_PUBLIC_MODE = "true"
    docker compose up -d --wait
    $needRestoreNormalMode = $true
} elseif ($initialHealth.public_demo -ne $true) {
    Write-Host "Local stack is running in normal mode. Recreating backend with DEMO_PUBLIC_MODE=true..." -ForegroundColor Cyan
    $env:DEMO_PUBLIC_MODE = "true"
    docker compose up -d --no-deps --force-recreate backend
    $needRestoreNormalMode = $true
}

# Wait until health check verifies public_demo is active
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$isPublicDemoReady = $false
while ($sw.Elapsed.TotalSeconds -lt 30) {
    $currentHealth = Get-StackHealth
    if ($currentHealth -and $currentHealth.status -eq "ok" -and $currentHealth.public_demo -eq $true) {
        $isPublicDemoReady = $true
        break
    }
    Start-Sleep -Milliseconds 500
}

if (-not $isPublicDemoReady) {
    Write-Error "Failed to activate public demo mode on http://127.0.0.1:8080"
    if ($needRestoreNormalMode -and -not $ResetAfter) {
        $env:DEMO_PUBLIC_MODE = "false"
        docker compose up -d --no-deps --force-recreate backend | Out-Null
    }
    exit 1
}
Write-Host "Public demo mode verified (public_demo: true)." -ForegroundColor Green

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
$tempErr = [System.IO.Path]::GetTempFileName()
$reader = $null
$streamReader = $null

try {
    # Launch cloudflared process redirecting stderr so log output is streamable
    $proc = Start-Process -FilePath "cloudflared" -ArgumentList $cfArgs -PassThru -NoNewWindow -RedirectStandardError $tempErr
    $targetTime = (Get-Date).AddMinutes($Minutes)

    Write-Host "Tunnel process started (PID: $($proc.Id)). Connecting to Cloudflare..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to close the tunnel immediately.`n" -ForegroundColor DarkGray

    $fileStream = [System.IO.File]::Open($tempErr, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    $streamReader = New-Object System.IO.StreamReader($fileStream)

    while ((Get-Date) -lt $targetTime -and -not $proc.HasExited) {
        while (-not $streamReader.EndOfStream) {
            $logLine = $streamReader.ReadLine()
            if ($logLine) {
                Write-Host $logLine
            }
        }
        Start-Sleep -Milliseconds 500
    }

    if ($proc.HasExited) {
        Write-Host "Tunnel process exited unexpectedly (ExitCode: $($proc.ExitCode))." -ForegroundColor Red
    } else {
        Write-Host "`nTime limit of $Minutes minute(s) reached. Shutting down tunnel..." -ForegroundColor Yellow
    }
} finally {
    if ($streamReader) { $streamReader.Dispose() }
    if ($fileStream) { $fileStream.Dispose() }
    Remove-Item -Force -ErrorAction SilentlyContinue $tempErr

    if ($proc -and -not $proc.HasExited) {
        Write-Host "Stopping cloudflared process (PID: $($proc.Id))..." -ForegroundColor Cyan
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $proc.WaitForExit(5000)
    }

    if ($ResetAfter) {
        Write-Host "ResetAfter enabled: resetting Docker Compose volumes and demo state..." -ForegroundColor Cyan
        docker compose down -v
        Write-Host "Demo stack teardown complete." -ForegroundColor Green
    } elseif ($needRestoreNormalMode) {
        Write-Host "Restoring normal demo mode (public_demo: false)..." -ForegroundColor Cyan
        $env:DEMO_PUBLIC_MODE = "false"
        docker compose up -d --no-deps --force-recreate backend | Out-Null
        $swRestore = [System.Diagnostics.Stopwatch]::StartNew()
        while ($swRestore.Elapsed.TotalSeconds -lt 30) {
            $h = Get-StackHealth
            if ($h -and $h.status -eq "ok" -and $h.public_demo -eq $false) {
                break
            }
            Start-Sleep -Milliseconds 500
        }
        Write-Host "Restored normal demo mode successfully (public_demo: false)." -ForegroundColor Green
    }

    Write-Host "Share session ended cleanly." -ForegroundColor Green
}
