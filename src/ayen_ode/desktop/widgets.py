import re
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from typing import Any, Optional
import customtkinter as ctk

from .colors import S900, S800, S700, S600, S500, S400, S300, S200, S100

_ICON_PATH: Optional[Path] = None
_INV_RE = re.compile(r"<investigate\s+([^>]*?)>(.*?)</investigate>", re.DOTALL)


def _find_icon() -> Optional[Path]:
    global _ICON_PATH
    if _ICON_PATH is not None:
        return _ICON_PATH
    try:
        from .. import paths
        p = paths.static_dir() / "clover.ico"
        if p.exists():
            _ICON_PATH = p
            return _ICON_PATH
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        p = candidate / "static" / "clover.ico"
        if p.exists():
            _ICON_PATH = p
            return _ICON_PATH
    return None


def _split_investigate(text: str):
    result = []
    last = 0
    for m in _INV_RE.finditer(text):
        if m.start() > last:
            result.append((text[last:m.start()], None))
        attrs = m.group(1)
        display = m.group(2).strip()
        item_name, entity_type, cost = "", "object", 1
        item_matches = list(re.finditer(r"(item|npc|location|faction|event)=(['\"])(.*?)\2", attrs))
        if not item_matches:
            item_matches = list(re.finditer(r"(item|npc|location|faction|event)=([^\s'\">]+)", attrs))
            for am in item_matches:
                item_name = am.group(2)
                t = am.group(1)
                if t == "npc":        entity_type = "character"
                elif t == "location": entity_type = "location"
                elif t == "faction":  entity_type = "faction"
                elif t == "event":    entity_type = "event"
        else:
            for am in item_matches:
                item_name = am.group(3)
                t = am.group(1)
                if t == "npc":        entity_type = "character"
                elif t == "location": entity_type = "location"
                elif t == "faction":  entity_type = "faction"
                elif t == "event":    entity_type = "event"
        cm = re.search(r"cost=(['\"]?)(\d+)\1", attrs)
        if cm:
            cost = int(cm.group(2))
        result.append((display or item_name, (item_name or display, entity_type, cost)))
        last = m.end()
    if last < len(text):
        result.append((text[last:], None))
    return result


def strip_investigate(text: str) -> str:
    return _INV_RE.sub(lambda m: m.group(2).strip(), text)


def _format_seconds(s: int) -> str:
    if not s or s <= 0:
        return ""
    days  = s // 86400
    hours = (s % 86400) // 3600
    if days > 0:
        return f"Day {days + 1}" + (f", Hour {hours}" if hours else "")
    if hours > 0:
        return f"Hour {hours}"
    mins = s // 60
    return f"{mins} min elapsed" if mins else f"{s}s elapsed"


def _center(win, w: int, h: int) -> None:
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")


def _pill(parent, text: str, bg: str, fg: str, **kw) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, fg_color=bg, text_color=fg,
                        corner_radius=999, font=("", 11, "bold"), **kw)


def _btn(parent, text: str, cmd, *, w=None, h=32,
         bg=S800, hbg=S700, fg=S300, font_size=12, **kw) -> ctk.CTkButton:
    kwargs = dict(text=text, command=cmd, height=h,
                  fg_color=bg, hover_color=hbg, text_color=fg,
                  font=("", font_size), border_width=1, border_color=S700, **kw)
    if w is not None:
        kwargs["width"] = w
    return ctk.CTkButton(parent, **kwargs)


def _label(parent, text: str, color=S400, size=12, **kw) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, text_color=color,
                        font=("", size), **kw)


def _entry(parent, var: tk.StringVar, *, w=340, ph="", show="") -> ctk.CTkEntry:
    return ctk.CTkEntry(parent, textvariable=var, width=w,
                        placeholder_text=ph, show=show,
                        fg_color=S800, border_color=S700,
                        text_color=S100, font=("", 14))


def _divider(parent) -> ctk.CTkFrame:
    f = ctk.CTkFrame(parent, fg_color=S800, height=1)
    f.pack(fill="x")
    return f


def _panel(parent, *, w=None, r=12, **kw) -> ctk.CTkFrame:
    kwargs = dict(fg_color=S900, corner_radius=r,
                  border_width=1, border_color=S800, **kw)
    if w is not None:
        kwargs["width"] = w
    return ctk.CTkFrame(parent, **kwargs)


def _bind_click_recursive(widget, handler) -> None:
    widget.bind("<Button-1>", handler)
    for child in widget.winfo_children():
        _bind_click_recursive(child, handler)
