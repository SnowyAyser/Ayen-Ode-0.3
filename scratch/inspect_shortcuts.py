import os
import sys
from pathlib import Path

def inspect_all_shortcuts():
    # Find all shortcuts in Desktop and Repo Root
    desktop_path = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
    repo_root = Path("C:/GitHub/Ayen-Ode-0.3")
    
    print(f"Desktop path: {desktop_path}")
    print(f"Repo root path: {repo_root}")
    
    paths_to_search = [desktop_path, repo_root]
    
    import subprocess
    # We will use powershell to inspect the shortcut target via a small script to avoid importing win32com
    for folder in paths_to_search:
        if not folder.exists():
            continue
        print(f"\n--- Shortcuts in {folder} ---")
        for lnk in folder.glob("*.lnk"):
            # Run PowerShell inline
            ps_cmd = f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').TargetPath"
            ps_args = f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').Arguments"
            ps_wd = f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').WorkingDirectory"
            
            target = subprocess.check_output(["powershell", "-Command", ps_cmd], text=True).strip()
            args = subprocess.check_output(["powershell", "-Command", ps_args], text=True).strip()
            wd = subprocess.check_output(["powershell", "-Command", ps_wd], text=True).strip()
            
            print(f"File: {lnk.name}")
            print(f"  Target: {target}")
            print(f"  Args: {args}")
            print(f"  WorkingDir: {wd}")

if __name__ == "__main__":
    inspect_all_shortcuts()
