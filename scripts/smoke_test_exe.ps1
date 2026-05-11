# Headless smoke test for Ayen-Ode.exe.
#
# Covers the failure modes that have actually broken builds so far:
#   1. EXE refuses to start (missing module, import error, segfault).
#   2. Embedded server fails to bind / respond to /health.
#   3. Frozen .env hermeticity: an external .env with TURSO_* or other vars
#      must not leak into the EXE.
#   4. /desktop-bootstrap mints a working session token.
#   5. /api/settings/launch spawns a child Ayen-Ode.exe --settings that
#      stays alive (i.e. the tk settings window opened). This catches the
#      "settings_window.main not exported" class of bug.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\smoke_test_exe.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\smoke_test_exe.ps1 -ExePath C:\dev\Ayen-Ode\Ayen-Ode.exe
#
# Exits 0 on success, non-zero on the first failure. ASCII-only so PowerShell
# 5.1 parses it correctly without a UTF-8 BOM.

[CmdletBinding()]
param(
    [string]$ExePath = "$(Join-Path $PSScriptRoot '..\Ayen-Ode.exe')",
    [int]$Port = 0
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "[..] $msg" -ForegroundColor Cyan }
function Write-Pass($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) {
    Write-Host "[!!] $msg" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ExePath)) {
    Write-Fail "EXE not found at $ExePath"
}
$ExePath = (Resolve-Path $ExePath).Path

$sandbox = Join-Path $env:TEMP "ayen-ode-smoke-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $sandbox | Out-Null

$externalCwd = Join-Path $env:TEMP "ayen-ode-poison-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $externalCwd | Out-Null
Set-Content -Path (Join-Path $externalCwd ".env") -Encoding utf8 -Value @"
ANTHROPIC_API_KEY=should-be-ignored
TURSO_DATABASE_URL=libsql://should-be-ignored.invalid
TURSO_AUTH_TOKEN=should-be-ignored
"@

$env:AYEN_ODE_USER_DATA = $sandbox
if ($Port -gt 0) { $env:AYEN_ODE_PORT = "$Port" }

Get-Process -Name "Ayen-Ode" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

try {
    Write-Step "Launching EXE from a poisoned cwd"
    Write-Host ("    cwd:    " + $externalCwd)
    Write-Host ("    exe:    " + $ExePath)
    Write-Host ("    sandbox: " + $sandbox)
    $proc = Start-Process -FilePath $ExePath -WorkingDirectory $externalCwd -PassThru
    if (-not $proc) { Write-Fail "Start-Process returned null" }
    Write-Host ("    PID: " + $proc.Id)

    Write-Step "Waiting for /health (up to 20s)"
    $runtimeJson = Join-Path $sandbox "runtime.json"
    $url = $null
    $ready = $false
    for ($i = 0; $i -lt 80; $i++) {
        if (Test-Path $runtimeJson) {
            try {
                $rt = Get-Content $runtimeJson -Raw | ConvertFrom-Json
                $url = $rt.url
            } catch {}
        }
        if ($url) {
            try {
                $r = Invoke-WebRequest -Uri "$url/health" -UseBasicParsing -TimeoutSec 1
                if ($r.StatusCode -eq 200) { $ready = $true; break }
            } catch {}
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) {
        $log = ""
        if (Test-Path (Join-Path $sandbox "app.log")) {
            $log = Get-Content (Join-Path $sandbox "app.log") -Raw
        }
        Write-Host ("    app.log: " + $log)
        Write-Fail "Server never came up. url=$url"
    }
    Write-Pass ("Server responded on " + $url)

    Write-Step "Confirming external .env did NOT leak in"
    $appLog = Join-Path $sandbox "app.log"
    if (Test-Path $appLog) {
        $log = Get-Content $appLog -Raw
        if ($log -match "TURSO|libsql_experimental|Traceback|Error|Exception") {
            Write-Host "    app.log contents:" -ForegroundColor Yellow
            Write-Host $log
            Write-Fail "Unexpected error or TURSO reference in app.log"
        }
    }
    $userEnvPath = Join-Path $sandbox ".env"
    if (Test-Path $userEnvPath) {
        $userEnv = Get-Content $userEnvPath -Raw
        if ($userEnv -match "should-be-ignored") {
            Write-Fail "User-data .env contains values from the external .env (hermeticity broken)"
        }
    }
    Write-Pass "External .env was correctly ignored (frozen build is hermetic)"

    Write-Step "Probing /desktop-bootstrap"
    $boot = Invoke-WebRequest -Uri "$url/desktop-bootstrap" -UseBasicParsing -TimeoutSec 2
    if ($boot.StatusCode -ne 200) { Write-Fail "/desktop-bootstrap returned $($boot.StatusCode)" }
    $m = [regex]::Match($boot.Content, "'apiKey','([a-f0-9]+)'")
    if (-not $m.Success) { Write-Fail "/desktop-bootstrap did not mint a token" }
    $token = $m.Groups[1].Value
    if ($token.Length -ne 64) { Write-Fail "Token length is $($token.Length), expected 64" }

    $worlds = Invoke-WebRequest -Uri "$url/api/worlds" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing -TimeoutSec 2
    if ($worlds.StatusCode -ne 200) { Write-Fail "/api/worlds with token returned $($worlds.StatusCode)" }
    Write-Pass "/desktop-bootstrap to /api/worlds round-trip works"

    Write-Step "Confirming the removed /api/settings/launch route is GONE"
    try {
        $r = Invoke-WebRequest -Uri "$url/api/settings/launch" -Method POST -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Fail "/api/settings/launch still responds ($($r.StatusCode)); should be 404/405"
    } catch {
        $sc = $_.Exception.Response.StatusCode.value__
        if ($sc -in 404, 405) {
            Write-Pass "/api/settings/launch is correctly gone (HTTP $sc)"
        } else {
            Write-Fail "/api/settings/launch unexpected error: $_"
        }
    }

    Write-Step "GET /api/settings (returns current values, API key masked)"
    $sg = Invoke-WebRequest -Uri "$url/api/settings" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing -TimeoutSec 3
    if ($sg.StatusCode -ne 200) { Write-Fail "GET /api/settings returned $($sg.StatusCode)" }
    $settings = $sg.Content | ConvertFrom-Json
    foreach ($field in @("anthropic_api_key_set", "anthropic_api_key_masked", "app_username", "app_password_set", "allowed_ips", "ayen_ode_port", "fullscreen")) {
        if (-not ($settings.PSObject.Properties.Name -contains $field)) {
            Write-Fail "GET /api/settings response missing field '$field'"
        }
    }
    Write-Pass "GET /api/settings returns all expected fields"

    Write-Step "POST /api/settings round-trips AYEN_ODE_FULLSCREEN=1"
    $sp = Invoke-WebRequest -Uri "$url/api/settings" -Method POST `
        -Headers @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" } `
        -Body '{"AYEN_ODE_FULLSCREEN":"1"}' -UseBasicParsing -TimeoutSec 3
    if ($sp.StatusCode -ne 200) { Write-Fail "POST /api/settings returned $($sp.StatusCode)" }
    $wrote = ($sp.Content | ConvertFrom-Json).wrote
    if (-not ($wrote -contains "AYEN_ODE_FULLSCREEN")) {
        Write-Fail "POST /api/settings didn't write AYEN_ODE_FULLSCREEN (wrote: $($wrote -join ','))"
    }
    # Verify it now comes back from a subsequent GET
    $sg2 = (Invoke-WebRequest -Uri "$url/api/settings" -Headers @{ "Authorization" = "Bearer $token" } -UseBasicParsing -TimeoutSec 3).Content | ConvertFrom-Json
    if (-not $sg2.fullscreen) { Write-Fail "After POST, GET /api/settings still reports fullscreen=false" }
    # And confirm .env on disk actually has the line
    $envOnDisk = Get-Content (Join-Path $sandbox ".env") -Raw
    if ($envOnDisk -notmatch "AYEN_ODE_FULLSCREEN=1") {
        Write-Fail ".env on disk does not contain AYEN_ODE_FULLSCREEN=1 after POST"
    }
    Write-Pass "POST /api/settings round-trips correctly and persists to .env"

    Write-Step "Dashboard HTML contains the new in-window settings modal markup"
    $dash = Invoke-WebRequest -Uri "$url/dashboard.html" -UseBasicParsing -TimeoutSec 3
    foreach ($marker in @('id="settingsModal"', 'openSettingsModal', 'toggleFullscreenNow', 'settingFullscreen')) {
        if ($dash.Content -notmatch [regex]::Escape($marker)) {
            Write-Fail "dashboard.html missing expected marker: $marker"
        }
    }
    Write-Pass "dashboard.html has settings modal + fullscreen controls"

    Write-Host ""
    Write-Host "All smoke checks passed." -ForegroundColor Green
}
finally {
    Get-Process -Name "Ayen-Ode" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $sandbox -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $externalCwd -ErrorAction SilentlyContinue
    Remove-Item Env:AYEN_ODE_USER_DATA -ErrorAction SilentlyContinue
    Remove-Item Env:AYEN_ODE_PORT -ErrorAction SilentlyContinue
}
