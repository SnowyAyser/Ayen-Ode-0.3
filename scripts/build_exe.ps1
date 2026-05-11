# Builds the Ayen-Ode desktop EXE (and optional installer) on Windows.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -Installer
#   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -Clean
#
# Output:
#   dist\Ayen-Ode\Ayen-Ode.exe                  (portable — copy folder anywhere)
#   dist\Ayen-Ode-Setup-<version>.exe           (installer, if -Installer used)
#
# Requirements (script tries to handle these for you):
#   - Python 3.11+ on PATH
#   - Inno Setup 6 (only needed with -Installer). Install via:
#         winget install JRSoftware.InnoSetup

[CmdletBinding()]
param(
    [switch]$Clean,       # wipe build/ and dist/ first
    [switch]$Installer,   # also build the Inno Setup installer
    [string]$Version = "" # optional version override, default = pyproject.toml
)

$ErrorActionPreference = "Stop"
$script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $script:RepoRoot

function Write-Stage($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

# --- 1. Locate Python -------------------------------------------------------

Write-Stage "Locating Python 3.11+"
$pythonExe = $null
foreach ($cmd in @("py -3.12", "py -3.11", "python", "python3")) {
    try {
        $parts = $cmd -split " "
        $version = & $parts[0] $parts[1..($parts.Length - 1)] -c "import sys; print(sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $version -match "\((\d+), (\d+)\)") {
            $major = [int]$Matches[1]; $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 11) {
                $pythonExe = $cmd
                Write-Host "    Found: $pythonExe -> Python $major.$minor"
                break
            }
        }
    } catch {}
}
if (-not $pythonExe) {
    Write-Error "Python 3.11+ not found. Install via: winget install Python.Python.3.12"
}

# --- 2. Create dedicated build venv ----------------------------------------

$buildVenv = Join-Path $script:RepoRoot ".venv-build"
Write-Stage "Preparing build venv at .venv-build"
if (-not (Test-Path $buildVenv)) {
    & $pythonExe.Split(" ") -m venv $buildVenv
}
$venvPython = Join-Path $buildVenv "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Failed to create venv at $buildVenv"
}

Write-Stage "Installing build dependencies"
& $venvPython -m pip install --upgrade pip --quiet
& $venvPython -m pip install -e ".[build]" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "pip install failed"
}

# --- 3. Clean previous build artifacts -------------------------------------

if ($Clean) {
    Write-Stage "Cleaning build/ and dist/"
    foreach ($d in @("build", "dist")) {
        $p = Join-Path $script:RepoRoot $d
        if (Test-Path $p) { Remove-Item -Recurse -Force $p }
    }
}

# --- 4. Run PyInstaller ----------------------------------------------------

Write-Stage "Running PyInstaller (this takes a minute)"
& $venvPython -m PyInstaller --noconfirm --clean ayen-ode.spec
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed"
}

$exePath = Join-Path $script:RepoRoot "dist\Ayen-Ode\Ayen-Ode.exe"
if (-not (Test-Path $exePath)) {
    Write-Error "Expected EXE not found at $exePath"
}

Write-Host ""
Write-Host "Portable build: $exePath" -ForegroundColor Green
Write-Host "Distribution folder: $(Split-Path $exePath)" -ForegroundColor Green

# --- 5. Optional: build the installer --------------------------------------

if ($Installer) {
    Write-Stage "Building Inno Setup installer"

    # Resolve version from pyproject.toml if not passed.
    if (-not $Version) {
        $py = $venvPython
        $Version = & $py -c "import re,pathlib; m=re.search(r'^version\s*=\s*["']([^"']+)', pathlib.Path('pyproject.toml').read_text(), re.M); print(m.group(1) if m else '0.0.0')"
    }
    Write-Host "    Version: $Version"

    $iscc = $null
    foreach ($candidate in @(
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    )) {
        if (Test-Path $candidate) { $iscc = $candidate; break }
    }
    if (-not $iscc) {
        Write-Warning "Inno Setup 6 not found. Install with: winget install JRSoftware.InnoSetup"
        Write-Warning "Skipping installer step. The portable build is still at:"
        Write-Warning "    $exePath"
        exit 0
    }

    $issPath = Join-Path $script:RepoRoot "installer\installer.iss"
    & $iscc "/DAyenOdeVersion=$Version" $issPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Inno Setup compilation failed"
    }

    $installerPath = Join-Path $script:RepoRoot "dist\Ayen-Ode-Setup-$Version.exe"
    if (Test-Path $installerPath) {
        Write-Host ""
        Write-Host "Installer:    $installerPath" -ForegroundColor Green
    } else {
        Write-Warning "Installer compiled but expected output not found at $installerPath"
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
