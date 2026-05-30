# Computes a single hash of the Ayen-Ode source tree.
#
# Both Play-Ayen-Ode.bat and the packaged Ayen-Ode.exe (via updater.py) call
# this script so they agree on what "the current source version" is. The hash
# combines each source file's MD5 with its last-write timestamp, so any edit
# changes the result. Prints the hash to stdout, or 'EMPTY' / 'ERROR'.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\source_hash.ps1 -RepoRoot "C:\path\to\repo"

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot
)

try {
    $paths = @(
        (Join-Path $RepoRoot 'src'),
        (Join-Path $RepoRoot 'static'),
        (Join-Path $RepoRoot 'scripts\ayen-ode.spec')
    )
    $files = Get-ChildItem -Recurse -File -Path $paths -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -match '^\.(py|js|html|css|json|spec|toml|ico)$' } |
        Sort-Object FullName
    if ($files) {
        $hashes = $files | ForEach-Object { (Get-FileHash $_.FullName -Algorithm MD5).Hash + $_.LastWriteTimeUtc.Ticks }
        $joined = $hashes -join ''
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($joined)
        $md5 = [System.Security.Cryptography.MD5]::Create()
        $hashBytes = $md5.ComputeHash($bytes)
        [BitConverter]::ToString($hashBytes).Replace('-', '')
    } else {
        'EMPTY'
    }
} catch {
    'ERROR'
}
