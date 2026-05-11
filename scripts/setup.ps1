# Ayen-Ode setup + run script (Windows)
#
# Idempotent: first run installs everything; subsequent runs skip finished
# steps and just start the server. Re-run any time you want to start the
# server.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

$ErrorActionPreference = "Stop"

# Resolve the repo root (parent of this script's folder)
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ">> Ayen-Ode setup ($Root)" -ForegroundColor Cyan

# Refuse to run inside a syncing folder
if ($Root -match '\\OneDrive\\|\\Dropbox\\|\\iCloudDrive\\|\\Google Drive\\') {
    Write-Host "ERROR: project is inside a cloud-sync folder ($Root)." -ForegroundColor Red
    Write-Host "Sync corrupts .venv and SQLite. Move to e.g. C:\dev\Ayen-Ode and re-run." -ForegroundColor Red
    exit 1
}

# --- Step 1: find a real Python interpreter ---
function Test-RealPython($exe) {
    if (-not $exe) { return $false }
    try {
        $out = & $exe --version 2>&1
        # Reject the Microsoft Store stub: it prints to stderr and returns
        # non-zero, but a successful invocation should print "Python X.Y.Z".
        if ($LASTEXITCODE -eq 0 -and "$out" -match '^Python 3\.(11|12|13|14)') {
            return $true
        }
    } catch { }
    return $false
}

$Python = $null
foreach ($candidate in @('py -3.12','py -3.11','py -3','python3','python')) {
    $parts = $candidate -split ' '
    $exe = (Get-Command $parts[0] -ErrorAction SilentlyContinue).Source
    if (-not $exe) { continue }
    $invoke = if ($parts.Count -gt 1) { @($exe) + $parts[1..($parts.Count-1)] } else { @($exe) }
    try {
        $out = & $invoke[0] $invoke[1..($invoke.Count-1)] --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$out" -match '^Python 3\.(11|12|13|14)') {
            $Python = $invoke
            Write-Host ">> Python: $($invoke -join ' ') ($out)" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $Python) {
    Write-Host "ERROR: no Python 3.11+ found." -ForegroundColor Red
    Write-Host "Install with:  winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host "Then open a NEW shell and re-run this script." -ForegroundColor Yellow
    exit 1
}

# --- Step 2: virtualenv ---
$VenvPy = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
    Write-Host ">> Creating .venv ..." -ForegroundColor Cyan
    & $Python[0] $Python[1..($Python.Count-1)] -m venv "$Root\.venv"
}

# --- Step 3: install deps if anthropic isn't present ---
& $VenvPy -c "import anthropic" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host ">> Installing dependencies ..." -ForegroundColor Cyan
    & $VenvPy -m pip install --upgrade pip
    & $VenvPy -m pip install -e .
    if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: pip install failed." -ForegroundColor Red; exit 1 }
}

# --- Step 4: .env ---
$EnvPath = Join-Path $Root ".env"
$NeedsKey = $false
if (-not (Test-Path $EnvPath)) {
    Write-Host ">> Creating .env from .env.example ..." -ForegroundColor Cyan
    Copy-Item (Join-Path $Root ".env.example") $EnvPath
    $NeedsKey = $true
} else {
    # Detect placeholder or empty key — also triggers the settings window.
    $envContent = Get-Content $EnvPath -Raw
    if ($envContent -match 'ANTHROPIC_API_KEY=\s*(sk-ant-\.\.\.)?\s*(\r?\n|$)') {
        $NeedsKey = $true
    }
}

if ($NeedsKey) {
    Write-Host ">> Opening settings window for first-run setup ..." -ForegroundColor Cyan
    Write-Host "   (enter your Anthropic API key in the window, then Save)" -ForegroundColor DarkGray
    & $VenvPy -m ayen_ode.settings_window
    Write-Host "   settings window closed; continuing" -ForegroundColor DarkGray
}

# --- Step 5: data dir ---
New-Item -ItemType Directory -Force -Path (Join-Path $Root "data") | Out-Null

# --- Step 6: launch server ---
Write-Host ""
Write-Host ">> Starting server on http://localhost:8000  (Ctrl-C to stop)" -ForegroundColor Green
Write-Host ""
& $VenvPy -m ayen_ode
