$root = (Get-Item .).FullName
$exe = Join-Path $root 'Ayen-Ode.exe'
$ico = Join-Path $root 'icon_v2.ico'
$shell = New-Object -ComObject WScript.Shell

$rootLnk = Join-Path $root 'Ayen-Ode.lnk'
$s1 = $shell.CreateShortcut($rootLnk)
$s1.TargetPath = $exe
$s1.WorkingDirectory = $root
$s1.IconLocation = $ico
$s1.Description = 'Launch Ayen-Ode'
$s1.Save()
Write-Host "Created root shortcut: $rootLnk"

$desktop = [System.Environment]::GetFolderPath('Desktop')
if ($desktop) {
    $desktopLnk = Join-Path $desktop 'Ayen-Ode.lnk'
    $s2 = $shell.CreateShortcut($desktopLnk)
    $s2.TargetPath = $exe
    $s2.WorkingDirectory = $root
    $s2.IconLocation = $ico
    $s2.Description = 'Launch Ayen-Ode'
    $s2.Save()
    Write-Host "Created desktop shortcut: $desktopLnk"
}
