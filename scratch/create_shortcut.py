import os
import subprocess
from pathlib import Path

repo_root = Path("C:/GitHub/Ayen-Ode-0.3").resolve()
shortcut_path = repo_root / "Ayen-Ode.lnk"
desktop_shortcut_path = Path("C:/Users/zgreiniman/Desktop/Ayen-Ode.lnk")
pythonw_path = repo_root / ".venv" / "Scripts" / "pythonw.exe"
script_args = "-m ayen_ode.desktop_launcher"
icon_path = repo_root / "icon_v2.ico"

# Create/update shortcut in repo root
ps_code = f"""
$sh = New-Object -ComObject WScript.Shell
$target = $sh.CreateShortcut('{shortcut_path}')
$target.TargetPath = '{pythonw_path}'
$target.Arguments = '{script_args}'
$target.WorkingDirectory = '{repo_root}'
$target.IconLocation = '{icon_path},0'
$target.Save()
"""

print("Creating/updating shortcut at:", shortcut_path)
subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_code], check=True)

# Create/update shortcut on Desktop
if desktop_shortcut_path.parent.exists():
    print("Creating/updating shortcut on Desktop at:", desktop_shortcut_path)
    ps_code_desktop = f"""
    $sh = New-Object -ComObject WScript.Shell
    $target = $sh.CreateShortcut('{desktop_shortcut_path}')
    $target.TargetPath = '{pythonw_path}'
    $target.Arguments = '{script_args}'
    $target.WorkingDirectory = '{repo_root}'
    $target.IconLocation = '{icon_path},0'
    $target.Save()
    """
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_code_desktop], check=True)
    print("Desktop shortcut updated successfully!")
else:
    print("Desktop folder not found, skipping desktop shortcut creation.")

print("All shortcuts updated successfully!")
