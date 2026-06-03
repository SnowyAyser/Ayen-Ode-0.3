import webview
import sys
import ctypes
from pathlib import Path

def set_window_icon(hwnd, icon_path):
    if not hwnd or not icon_path.exists():
        return
    try:
        # Load the .ico file
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x00000010
        hicon = ctypes.windll.user32.LoadImageW(
            None,
            str(icon_path),
            IMAGE_ICON,
            0, 0,
            LR_LOADFROMFILE
        )
        if hicon:
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1
            # Set small icon
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
            # Set big icon
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
            print("Successfully set window icon!")
    except Exception as e:
        print(f"Error setting window icon: {e}")

def main():
    window = webview.create_window("Icon Test", "https://google.com")
    
    def on_shown():
        print("Window shown! native =", window.native)
        icon_path = Path("C:/GitHub/Ayen-Ode-0.3/static/clover.ico")
        if sys.platform == "win32":
            set_window_icon(window.native, icon_path)
            
    window.events.shown += on_shown
    
    # We won't start the webview here so the script exits quickly in the sandbox
    print("Webview configured with event hooks successfully!")

if __name__ == "__main__":
    main()
