$sh = New-Object -ComObject WScript.Shell
Get-ChildItem "C:\Users\zgreiniman\Desktop\*.lnk", "C:\GitHub\Ayen-Ode-0.3\*.lnk" -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*ayen*" } | ForEach-Object {
    $s = $sh.CreateShortcut($_.FullName)
    Write-Host "File: $($_.FullName)"
    Write-Host "  Target: $($s.TargetPath)"
    Write-Host "  Args: $($s.Arguments)"
    Write-Host "  WorkingDir: $($s.WorkingDirectory)"
}
