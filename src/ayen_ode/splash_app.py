from __future__ import annotations

import math
import time
from typing import Any

try:
    import tkinter as tk
except ImportError:
    tk = None


def _log_boot_error(msg: str, exc: Exception | None = None):
    try:
        import traceback
        from ayen_ode import paths
        paths.ensure_user_dir()
        boot_log = paths.user_data_dir() / "boot.log"
        with open(boot_log, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
            if exc is not None:
                traceback.print_exc(file=f)
    except Exception:
        pass


class SplashApp:
    def __init__(self, root) -> None:
        self.root = root
        self.root.title("Ayen-Ode")
        self.root.overrideredirect(True)
        
        # Dark Slate Color Scheme matching the game theme
        self.bg_color = "#0b0f19"       # Deep dark indigo-blue
        self.text_color = "#94a3b8"     # slate-400
        self.accent_color = "#10b981"   # emerald-500
        self.gold_color = "#f59e0b"     # amber-500
        
        self.root.configure(bg=self.bg_color)
        
        # Dimensions and centering
        self.width = 450
        self.height = 320
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - self.width) // 2
        y = (screen_h - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        self.border_frame = None
        try:
            self.border_frame = tk.Frame(self.root, bg="#1e293b", bd=1)
            self.border_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            self.inner_frame = tk.Frame(self.border_frame, bg=self.bg_color)
            self.inner_frame.place(relx=0.005, rely=0.005, relwidth=0.99, relheight=0.99)
            
            # Canvas for clover loading animation
            self.canvas = tk.Canvas(
                self.inner_frame, 
                width=120, 
                height=120, 
                bg=self.bg_color, 
                highlightthickness=0
            )
            self.canvas.pack(pady=(40, 10))
            
            self.title_label = tk.Label(
                self.inner_frame, 
                text="AYEN-ODE", 
                font=("Outfit", 24, "bold"), 
                fg=self.gold_color, 
                bg=self.bg_color
            )
            self.title_label.pack()
            
            self.subtitle_label = tk.Label(
                self.inner_frame, 
                text="Forging the world...", 
                font=("Inter", 10), 
                fg=self.text_color, 
                bg=self.bg_color
            )
            self.subtitle_label.pack(pady=(5, 20))
        except Exception as e:
            _log_boot_error("Error initializing Splash GUI widgets", e)
            
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

        self.angle = 0.0
        self.pulse_val = 0.0
        self.pulse_dir = 1.0
        
        self.animate()
        self.check_status()

    def animate(self) -> None:
        try:
            if hasattr(self, "canvas") and self.canvas:
                self.canvas.delete("all")
                cx, cy = 60, 60
                r_base = 25
                
                self.pulse_val += 0.05 * self.pulse_dir
                if self.pulse_val > 1.0:
                    self.pulse_val = 1.0
                    self.pulse_dir = -1
                elif self.pulse_val < 0.2:
                    self.pulse_val = 0.2
                    self.pulse_dir = 1
                    
                glow_r = r_base + (self.pulse_val * 8)
                self.canvas.create_oval(
                    cx - glow_r, cy - glow_r, 
                    cx + glow_r, cy + glow_r, 
                    outline="#064e3b", width=1
                )
                
                self.angle += 0.08
                for i in range(4):
                    theta = self.angle + (i * math.pi / 2)
                    lcx = cx + math.cos(theta) * 18
                    lcy = cy + math.sin(theta) * 18
                    l_rad = 12
                    
                    self.canvas.create_oval(
                        lcx - l_rad - 2, lcy - l_rad - 2,
                        lcx + l_rad + 2, lcy + l_rad + 2,
                        fill="", outline="#047857", width=1
                    )
                    self.canvas.create_oval(
                        lcx - l_rad, lcy - l_rad,
                        lcx + l_rad, lcy + l_rad,
                        fill=self.accent_color, outline="#34d399", width=2
                    )
                    
                self.canvas.create_oval(
                    cx - 5, cy - 5, cx + 5, cy + 5,
                    fill=self.gold_color, outline="white", width=1
                )
        except Exception as e:
            _log_boot_error("Error in Splash animation loop", e)
            
        self.root.after(20, self.animate)

    def trigger_update(self) -> None:
        try:
            if hasattr(self, "subtitle_label") and self.subtitle_label:
                self.subtitle_label.configure(
                    text="Update detected! Rebuilding engine...", 
                    fg=self.gold_color
                )
        except Exception:
            pass

    def trigger_failed(self) -> None:
        try:
            if hasattr(self, "subtitle_label") and self.subtitle_label:
                self.subtitle_label.configure(
                    text="Boot failed! See boot.log.", 
                    fg="#ef4444"
                )
        except Exception:
            pass

    def check_status(self) -> None:
        import sys
        main_mod = sys.modules.get("__main__")
        dl_mod = sys.modules.get("ayen_ode.desktop_launcher")
        
        target_mod = None
        if main_mod and hasattr(main_mod, "server_ready"):
            target_mod = main_mod
        elif dl_mod and hasattr(dl_mod, "server_ready"):
            target_mod = dl_mod
            
        update_triggered = getattr(target_mod, "update_triggered", False)
        server_ready = getattr(target_mod, "server_ready", False)
        server_failed = getattr(target_mod, "server_failed", False)
        
        if update_triggered:
            self.trigger_update()
            self.root.after(1500, self.root.destroy)
            return
        elif server_ready:
            self.root.destroy()
            return
        elif server_failed:
            self.trigger_failed()
            self.root.after(2500, self.root.destroy)
            return
            
        self.root.after(100, self.check_status)
