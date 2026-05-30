# Self-update helper for the packaged Ayen-Ode.exe.
#
# Spawned (detached, in its own console) by updater.py when the on-disk source
# is newer than the hash the running exe was built from. It waits for the
# running exe to exit so the file lock is released, rebuilds the exe, records
# the new build hash, then relaunches the fresh build.
#
# Usage (invoked automatically):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\update_and_launch.ps1 -RepoRoot "<repo>" -WaitPid <pid>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [int]$WaitPid = 0
)

$ErrorActionPreference = "Stop"
$exe = Join-Path $RepoRoot "Ayen-Ode.exe"

$host.UI.RawUI.WindowTitle = "Ayen-Ode Updater"
Write-Host ""
Write-Host "  A newer version of Ayen-Ode is available. Updating before launch..." -ForegroundColor Cyan
Write-Host ""

# 1. Wait for the running exe to exit (so we can overwrite it).
if ($WaitPid -gt 0) {
    try { Wait-Process -Id $WaitPid -Timeout 30 -ErrorAction SilentlyContinue } catch {}
}
# Belt-and-braces: wait until the exe file itself is writable (lock released).
for ($i = 0; $i -lt 40; $i++) {
    try {
        $fs = [System.IO.File]::Open($exe, 'Open', 'ReadWrite', 'None')
        $fs.Close()
        break
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

# 2. Rebuild the exe.
$buildOk = $false
try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\build_exe.ps1")
    if ($LASTEXITCODE -eq 0) { $buildOk = $true }
} catch {
    Write-Host "  Build error: $_" -ForegroundColor Red
}

# 3. Record the new build hash so the next launch skips rebuilding.
if ($buildOk) {
    try {
        $hash = & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\source_hash.ps1") -RepoRoot $RepoRoot
        if ($hash -and $hash -ne 'ERROR' -and $hash -ne 'EMPTY') {
            Set-Content -Path (Join-Path $RepoRoot ".build_hash") -Value $hash -NoNewline -Encoding ASCII
        }
    } catch {}
    Write-Host ""
    Write-Host "  Update complete. Launching..." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  Update failed. Launching the existing version instead." -ForegroundColor Yellow
}

# 4. Launch (the freshly built exe, or the existing one if the build failed).
if (Test-Path $exe) {
    Start-Process -FilePath $exe
}
Start-Sleep -Seconds 2
