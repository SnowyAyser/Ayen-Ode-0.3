import sys
from pathlib import Path
from PIL import Image

def main():
    png_path = Path(r"C:\Users\zgreiniman\.gemini\antigravity\brain\281ba3d9-fbc7-4d32-919c-bf5a0aeafcb1\ayen_ode_sketch_icon_1780107011208.png")
    if not png_path.exists():
        print(f"Error: PNG not found at {png_path}")
        sys.exit(1)
        
    img = Image.open(png_path)
    
    # Save as ICO with multiple sizes for Windows support
    ico_path1 = Path(r"C:\GitHub\Ayen-Ode-0.3\static\icon_v2.ico")
    ico_path2 = Path(r"C:\GitHub\Ayen-Ode-0.3\icon_v2.ico")
    
    # Ensure static directory exists
    ico_path1.parent.mkdir(parents=True, exist_ok=True)
    
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path1, format="ICO", sizes=sizes)
    img.save(ico_path2, format="ICO", sizes=sizes)
    print(f"Success: Converted PNG to ICO at:\n  - {ico_path1}\n  - {ico_path2}")

if __name__ == "__main__":
    main()
