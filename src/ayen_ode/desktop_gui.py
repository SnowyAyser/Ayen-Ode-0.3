"""
Native desktop GUI for Ayen-Ode.

Visual style matches the original HTML/Tailwind frontend:
  - Slate colour palette (bg-slate-950 / slate-900 / slate-800)
  - Amber accent for the Act button and investigation points
  - Purple accent for quests
  - Georgia for narrative text, system sans for UI
  - Three-panel layout: [Narrative] | [Quests] | [Compendium]
  - Investigation panel drops from the top on demand
"""

from __future__ import annotations

import queue
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from typing import Any, Optional

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------------------------------------------------------------------------
# Icon
# ---------------------------------------------------------------------------
_ICON_PATH: Optional[Path] = None


def _find_icon() -> Optional[Path]:
    global _ICON_PATH
    if _ICON_PATH is not None:
        return _ICON_PATH
    try:
        from . import paths
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


# ---------------------------------------------------------------------------
# Colour palette  —  matches Tailwind slate + amber
# ---------------------------------------------------------------------------
# Backgrounds
S950 = "#020617"   # slate-950  — page background
S900 = "#0f172a"   # slate-900  — panel / card background
S800 = "#1e293b"   # slate-800  — borders, input bg, dividers
S700 = "#334155"   # slate-700  — lighter borders
S600 = "#475569"   # slate-600  — muted text, icons
S500 = "#64748b"   # slate-500  — secondary muted
S400 = "#94a3b8"   # slate-400  — chip / hint text
S300 = "#cbd5e1"   # slate-300  — secondary body text
S200 = "#e2e8f0"   # slate-200  — panel headings
S100 = "#f1f5f9"   # slate-100  — primary text

# Amber (Act button, investigation)
A950 = "#431407"   # amber-950  — invest pill bg
A800 = "#92400e"   # amber-800  — invest pill border, btn bg
A700 = "#b45309"   # amber-700  — btn hover
A400 = "#fbbf24"   # amber-400  — invest points value
A300 = "#fcd34d"   # amber-300  — invest points text
A100 = "#fef3c7"   # amber-100  — btn text

# Purple (quest panel)
P600 = "#9333ea"   # purple-600

# Semantic
RED  = "#ef4444"
GRN  = "#22c55e"

# Entity-type dots
TYPE_COLORS = {
    "character": "#3b82f6",
    "location":  "#10b981",
    "faction":   "#8b5cf6",
    "object":    "#f97316",
    "event":     "#ef4444",
}

SKIP_PRESETS = [
    ("1 hour",    3600),
    ("4 hours",   14400),
    ("Rest (8h)", 28800),
    ("1 day",     86400),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_INV_RE = re.compile(r"<investigate\s+([^>]*?)>(.*?)</investigate>", re.DOTALL)


def _split_investigate(text: str):
    result = []
    last = 0
    for m in _INV_RE.finditer(text):
        if m.start() > last:
            result.append((text[last:m.start()], None))
        attrs = m.group(1)
        display = m.group(2).strip()
        item_name, entity_type, cost = "", "object", 1
        for am in re.finditer(r"(item|npc|location|faction|event)='([^']+)'", attrs):
            item_name = am.group(2)
            t = am.group(1)
            if t == "npc":        entity_type = "character"
            elif t == "location": entity_type = "location"
            elif t == "faction":  entity_type = "faction"
            elif t == "event":    entity_type = "event"
        cm = re.search(r"cost='(\d+)'", attrs)
        if cm:
            cost = int(cm.group(1))
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


# ---------------------------------------------------------------------------
# App root
# ---------------------------------------------------------------------------
class AyenOdeApp:
    def __init__(self) -> None:
        from .config import load_settings
        from .services import AyenOdeService
        self.settings = load_settings()
        self.service  = AyenOdeService(self.settings.db_path)
        self.current_user: str = ""
        self.current_world_id: Optional[str] = None
        self._frame: Optional[ctk.CTkFrame] = None

        self.root = ctk.CTk()
        self.root.title("Ayen-Ode")
        self.root.minsize(1100, 700)
        self.root.configure(fg_color=S950)
        _center(self.root, 1400, 880)

        icon = _find_icon()
        if icon:
            try: self.root.iconbitmap(str(icon))
            except Exception: pass

        self.root.lift()
        self.root.focus_force()
        self._container = ctk.CTkFrame(self.root, fg_color="transparent")
        self._container.pack(fill="both", expand=True)
        self.show_login()

    def _swap(self, cls, **kw) -> None:
        if self._frame:
            self._frame.destroy()
        self._frame = cls(self._container, self, **kw)
        self._frame.pack(fill="both", expand=True)

    def show_login(self)                    -> None: self._swap(LoginFrame)
    def show_dashboard(self)                -> None: self._swap(DashboardFrame)
    def show_create_world(self)             -> None: self._swap(CreateWorldFrame)
    def show_narrative(self, world_id: str) -> None:
        self.current_world_id = world_id
        self._swap(NarrativeFrame, world_id=world_id)

    def run(self) -> None: self.root.mainloop()


# ---------------------------------------------------------------------------
# Shared widget helpers
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app: AyenOdeApp) -> None:
        super().__init__(parent, fg_color=S950)
        self.app = app
        self._build()

    def _build(self) -> None:
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="Ayen-Ode",
                     font=("Georgia", 42, "bold"), text_color=S100).pack(pady=(0, 4))
        _label(box, "Narrative RPG Engine", S500, 13).pack(pady=(0, 40))

        card = _panel(box, r=16)
        card.pack()
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=48, pady=44)

        def row(lbl, var, **kw):
            _label(inner, lbl, S400, 12).pack(anchor="w", pady=(0, 4))
            e = _entry(inner, var, w=360, **kw)
            e.pack(pady=(0, 20))
            return e

        self.u_var = tk.StringVar()
        self.p_var = tk.StringVar()
        ue = row("Username", self.u_var, ph="username")
        pe = row("Password", self.p_var, ph="••••••••", show="•")

        ctk.CTkButton(inner, text="Login", width=360, height=46,
                      fg_color=A800, hover_color=A700, text_color=A100,
                      font=("", 14, "bold"), command=self._login).pack()

        self.err = _label(inner, "", RED, 12)
        self.err.pack(pady=(14, 0))

        for e in (ue, pe):
            e.bind("<Return>", lambda _: self._login())
        ue.focus()

    def _login(self) -> None:
        u, p = self.u_var.get().strip(), self.p_var.get()
        cu, cp = self.app.settings.app_username, self.app.settings.app_password
        if (not cu or u == cu) and (not cp or p == cp):
            self.app.current_user = u or cu or "player"
            self.app.show_dashboard()
        else:
            self.err.configure(text="Invalid credentials.")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app: AyenOdeApp) -> None:
        super().__init__(parent, fg_color=S950)
        self.app = app
        self._build()
        self._load()

    def _build(self) -> None:
        # Header
        hdr = ctk.CTkFrame(self, fg_color=S900, height=60, corner_radius=0,
                           border_width=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        hl = ctk.CTkFrame(hdr, fg_color="transparent")
        hl.pack(side="left", padx=28, fill="y")
        ctk.CTkLabel(hl, text="Ayen-Ode",
                     font=("Georgia", 20, "bold"), text_color=S100
                     ).pack(side="left", pady=18)
        _label(hl, "  World Dashboard", S500, 12).pack(side="left", pady=18)

        hr = ctk.CTkFrame(hdr, fg_color="transparent")
        hr.pack(side="right", padx=24, pady=12)
        _btn(hr, "⚙  Settings", self._settings, w=110).pack(side="left", padx=(0, 8))
        _btn(hr, "Logout", self.app.show_login, w=80,
             bg="#7f1d1d", hbg="#991b1b", fg="#fca5a5").pack(side="left")

        # API key warning
        if not self.app.settings.anthropic_api_key:
            warn = ctk.CTkFrame(self, fg_color="#431407", corner_radius=0)
            warn.pack(fill="x")
            _label(warn,
                   "⚠  No Anthropic API key set — narrative calls will fail. "
                   "Click Settings to add your key.",
                   "#fb923c", 12).pack(padx=20, pady=6)

        _divider(self)

        # Body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=60, pady=32)

        _label(body, "ALL WORLDS", "#3b82f6", 11).pack(anchor="w", pady=(0, 12))
        self.list_frame = ctk.CTkScrollableFrame(body, fg_color="transparent",
                                                  border_width=0)
        self.list_frame.pack(fill="both", expand=True, pady=(0, 32))

        _label(body, "CREATE NEW WORLD", "#3b82f6", 11).pack(anchor="w", pady=(0, 12))
        self._create_card(body)

    def _create_card(self, parent) -> None:
        card = _panel(parent, r=10, cursor="hand2")
        card.pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(inner, text="⊕  Forge a new world",
                     font=("", 15, "bold"), text_color=S100).pack(anchor="w")
        _label(inner, "Name it, set the tone, write the premise, choose your role.",
               S500, 12).pack(anchor="w", pady=(4, 0))
        _bind_click_recursive(card, lambda _: self.app.show_create_world())

    def _load(self) -> None:
        for w in self.list_frame.winfo_children():
            w.destroy()
        try:
            worlds = self.app.service.list_worlds().get("worlds", [])
        except Exception:
            worlds = []
        if not worlds:
            _label(self.list_frame, "No worlds yet — create one below.", S500, 13
                   ).pack(anchor="w", pady=8)
            return
        for world in worlds:
            self._world_card(world)

    def _world_card(self, world: dict) -> None:
        wid    = world.get("world_id", "")
        name   = world.get("name", "Unnamed")
        premise = (world.get("premise") or "")[:90]

        card = _panel(self.list_frame, r=10)
        card.pack(fill="x", pady=5)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=16)

        # Title row
        tr = ctk.CTkFrame(inner, fg_color="transparent")
        tr.pack(fill="x")
        ctk.CTkLabel(tr, text=name, font=("", 15, "bold"), text_color=S100
                     ).pack(side="left")

        if premise:
            _label(inner,
                   premise + ("…" if len(world.get("premise", "")) > 90 else ""),
                   S500, 12, wraplength=700, justify="left"
                   ).pack(anchor="w", pady=(4, 12))

        br = ctk.CTkFrame(inner, fg_color="transparent")
        br.pack(anchor="w")

        _btn(br, "Enter World", lambda w=wid: self.app.show_narrative(w),
             w=110, bg=A800, hbg=A700, fg=A100).pack(side="left", padx=(0, 6))

        _btn(br, "Reset", lambda w=wid, n=name: self._confirm_reset(w, n),
             w=72, fg="#f87171", hbg="#7f1d1d").pack(side="left", padx=(0, 6))
        _btn(br, "Delete", lambda w=wid, n=name: self._confirm_delete(w, n),
             w=72, fg=RED, hbg="#7f1d1d").pack(side="left")

    def _confirm_reset(self, wid: str, name: str) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title("Reset World")
        dlg.configure(fg_color=S900)
        dlg.grab_set()
        _center(dlg, 440, 220)
        ctk.CTkLabel(dlg, text=f'Reset "{name}"?',
                     font=("Georgia", 16, "bold"), text_color=S100).pack(pady=(28, 8))
        _label(dlg,
               "Clears all narrative history and entity data,\n"
               "but keeps world name, premise and tone.",
               S500, 12, justify="center").pack(pady=(0, 24))
        row = ctk.CTkFrame(dlg, fg_color="transparent")
        row.pack()
        _btn(row, "Cancel", dlg.destroy, w=100).pack(side="left", padx=(0, 12))
        _btn(row, "Reset", lambda: self._do_reset(dlg, wid),
             w=100, bg="#7f1d1d", hbg="#991b1b", fg="#fca5a5").pack(side="left")

    def _do_reset(self, dlg, wid: str) -> None:
        dlg.destroy()
        try:
            self.app.service.reset_world(wid)
            self._load()
        except Exception as e:
            self._toast(str(e))

    def _confirm_delete(self, wid: str, name: str) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title("Delete World")
        dlg.configure(fg_color=S900)
        dlg.grab_set()
        _center(dlg, 440, 230)
        ctk.CTkLabel(dlg, text=f'Delete "{name}"?',
                     font=("Georgia", 16, "bold"), text_color=S100).pack(pady=(28, 8))
        _label(dlg, "Permanent. All world data will be deleted.\nThis cannot be undone.",
               RED, 12, justify="center").pack(pady=(0, 24))
        row = ctk.CTkFrame(dlg, fg_color="transparent")
        row.pack()
        _btn(row, "Cancel", dlg.destroy, w=100).pack(side="left", padx=(0, 12))
        _btn(row, "Delete Permanently", lambda: self._do_delete(dlg, wid),
             w=160, bg="#7f1d1d", hbg="#991b1b", fg=RED).pack(side="left")

    def _do_delete(self, dlg, wid: str) -> None:
        dlg.destroy()
        try:
            self.app.service.delete_world(wid)
            self._load()
        except Exception as e:
            self._toast(str(e))

    def _settings(self) -> None:
        SettingsDialog(self.app.root)

    def _toast(self, msg: str) -> None:
        lbl = _label(self.list_frame, f"⚠ {msg}", RED, 12)
        lbl.pack(anchor="w", pady=4)
        self.after(4000, lbl.destroy)


# ---------------------------------------------------------------------------
# Create-world wizard
# ---------------------------------------------------------------------------
STEPS = [
    ("Name Your World",
     "Every great story begins with a name."),
    ("Set the Tone",
     "What kind of world is this? Pick a genre that fits your vision."),
    ("Write the Premise",
     "Describe the world and its current situation in a few sentences."),
    ("Your Role",
     "Who are you in this world?"),
]
TONES = ["Dark Fantasy", "High Fantasy", "Sci-Fi", "Horror",
         "Mystery", "Historical", "Grimdark", "Mythic"]


class CreateWorldFrame(ctk.CTkFrame):
    def __init__(self, parent, app: AyenOdeApp) -> None:
        super().__init__(parent, fg_color=S950)
        self.app  = app
        self.step = 0
        self.data = {"name": "", "tone": "", "premise": "", "player_role": ""}
        self._build()
        self._refresh()

    def _build(self) -> None:
        _btn(self, "← Dashboard", self.app.show_dashboard, w=130,
             h=32, bg="transparent", hbg=S900, fg=S500
             ).pack(anchor="nw", padx=20, pady=16)

        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.place(relx=0.5, rely=0.5, anchor="center")

        self.dots_row = ctk.CTkFrame(self.center, fg_color="transparent")
        self.dots_row.pack(pady=(0, 20))

        self.step_lbl  = _label(self.center, "", A700, 12)
        self.step_lbl.pack()
        self.title_lbl = ctk.CTkLabel(self.center, text="",
                                      font=("Georgia", 30, "bold"),
                                      text_color=S100, wraplength=620)
        self.title_lbl.pack(pady=(4, 6))
        self.sub_lbl   = _label(self.center, "", S500, 13, wraplength=540)
        self.sub_lbl.pack(pady=(0, 22))

        self.name_entry  = ctk.CTkEntry(self.center, width=600, height=48,
                                         placeholder_text="e.g. The Shattered Empire…",
                                         fg_color=S800, border_color=S700,
                                         text_color=S100, font=("", 14))
        self.role_entry  = ctk.CTkEntry(self.center, width=600, height=48,
                                         placeholder_text="e.g. a wandering sell-sword with a secret",
                                         fg_color=S800, border_color=S700,
                                         text_color=S100, font=("", 14))
        self.premise_box = ctk.CTkTextbox(self.center, width=600, height=160,
                                           fg_color=S800, border_width=1,
                                           border_color=S700, font=("Georgia", 13),
                                           text_color=S100)

        self.tone_frame = ctk.CTkFrame(self.center, fg_color="transparent")
        self.tone_var   = tk.StringVar()
        for i, t in enumerate(TONES):
            ctk.CTkButton(self.tone_frame, text=t, width=180, height=42,
                          fg_color=S800, hover_color=S700, border_width=1,
                          border_color=S700, text_color=S300, font=("", 13),
                          command=lambda x=t: self._pick_tone(x)
                          ).grid(row=i // 4, column=i % 4, padx=6, pady=6)

        self.err_lbl = _label(self.center, "", RED, 12)
        self.err_lbl.pack(pady=(4, 0))

        nav = ctk.CTkFrame(self.center, fg_color="transparent")
        nav.pack(pady=(22, 0))
        self.back_btn = _btn(nav, "← Back", self._prev, w=110, h=42,
                             bg="transparent", hbg=S900, fg=S500)
        self.back_btn.pack(side="left", padx=(0, 14))
        self.next_btn = ctk.CTkButton(nav, text="Continue →", width=160, height=42,
                                      fg_color=A800, hover_color=A700,
                                      text_color=A100, font=("", 14, "bold"),
                                      command=self._next)
        self.next_btn.pack(side="left")

    def _save_current(self) -> None:
        k = ["name", "tone", "premise", "player_role"][self.step]
        if   self.step == 2: self.data[k] = self.premise_box.get("1.0", "end").strip()
        elif self.step == 1: self.data[k] = self.tone_var.get()
        elif self.step == 0: self.data[k] = self.name_entry.get().strip()
        else:                self.data[k] = self.role_entry.get().strip()

    def _refresh(self) -> None:
        for w in self.dots_row.winfo_children():
            w.destroy()
        for i in range(4):
            w = 30 if i == self.step else 10
            c = A700 if i <= self.step else S800
            ctk.CTkFrame(self.dots_row, width=w, height=8,
                         fg_color=c, corner_radius=4).pack(side="left", padx=3)

        title, sub = STEPS[self.step]
        self.step_lbl.configure(text=f"STEP {self.step+1} OF {len(STEPS)}")
        self.title_lbl.configure(text=title)
        self.sub_lbl.configure(text=sub)
        self.err_lbl.configure(text="")

        for w in (self.name_entry, self.role_entry, self.premise_box, self.tone_frame):
            w.pack_forget()

        if self.step == 0:
            self.name_entry.pack()
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, self.data["name"])
            self.name_entry.bind("<Return>", lambda _: self._next())
            self.name_entry.focus()
        elif self.step == 1:
            self.tone_frame.pack()
            sel = self.tone_var.get()
            for btn in self.tone_frame.winfo_children():
                act = btn.cget("text") == sel
                btn.configure(fg_color=A800 if act else S800,
                              border_color=A700 if act else S700,
                              text_color=A100 if act else S300)
        elif self.step == 2:
            self.premise_box.pack()
            self.premise_box.delete("1.0", "end")
            if self.data["premise"]:
                self.premise_box.insert("1.0", self.data["premise"])
            self.premise_box.focus()
        else:
            self.role_entry.pack()
            self.role_entry.delete(0, "end")
            self.role_entry.insert(0, self.data["player_role"])
            self.role_entry.bind("<Return>", lambda _: self._next())
            self.role_entry.focus()

        if self.step == 0:
            self.back_btn.pack_forget()
        else:
            self.back_btn.pack(side="left", padx=(0, 14))

        self.next_btn.configure(
            text="Create World →" if self.step == len(STEPS)-1 else "Continue →",
            state="normal",
        )

    def _pick_tone(self, t: str) -> None:
        self.tone_var.set(t)
        self.data["tone"] = t
        self._refresh()

    def _prev(self) -> None:
        if self.step > 0:
            self._save_current()
            self.step -= 1
            self._refresh()

    def _next(self) -> None:
        self._save_current()
        val = self.data[["name", "tone", "premise", "player_role"][self.step]].strip()
        if not val:
            self.err_lbl.configure(text="This field is required.")
            return
        if self.step < len(STEPS) - 1:
            self.step += 1
            self._refresh()
        else:
            self._create()

    def _create(self) -> None:
        self.next_btn.configure(text="Creating…", state="disabled")

        def work() -> None:
            try:
                from . import narrative as narr
                result = self.app.service.create_world(
                    name=self.data["name"], premise=self.data["premise"],
                    theme_tone=self.data["tone"], player_role=self.data["player_role"])
                wid = result["world"]["world_id"]
                narr.initialize_world(
                    client=self.app.settings.anthropic_client,
                    service=self.app.service, world_id=wid,
                    name=self.data["name"], premise=self.data["premise"],
                    theme_tone=self.data["tone"], player_role=self.data["player_role"])
                self.after(0, lambda: self.app.show_narrative(wid))
            except Exception as exc:
                self.after(0, lambda e=exc: (
                    self.err_lbl.configure(text=f"Error: {e}"),
                    self.next_btn.configure(text="Create World →", state="normal"),
                ))

        threading.Thread(target=work, daemon=True).start()


# ---------------------------------------------------------------------------
# Narrative screen
# ---------------------------------------------------------------------------
class NarrativeFrame(ctk.CTkFrame):
    """
    Layout (matches original HTML):

      [HEADER: world name | premise | investigation pill | home | logout]
      ┌──────────────────────┬──────────────┬──────────────┐
      │ Narrative + Input    │ Quest Panel  │ Compendium   │
      │  (flex-1)            │  (w≈280)     │  (w≈280)     │
      └──────────────────────┴──────────────┴──────────────┘

    Investigation panel: drops in from top of the narrative column on demand.
    """

    PANEL_W = 284   # quest / compendium column width

    def __init__(self, parent, app: AyenOdeApp, world_id: str) -> None:
        super().__init__(parent, fg_color=S950)
        self.app      = app
        self.world_id = world_id

        # state
        self.entities:       list[dict]  = []
        self.conv_history:   list[dict]  = []
        self.inv_jobs:       dict        = {}
        self.inv_balance:    int         = 0
        self.inv_max:        int         = 0
        self._busy           = False
        self._q: queue.Queue = queue.Queue()
        self._input_hist:    list[str]   = []
        self._hist_pos:      int         = -1
        self._draft:         str         = ""
        self._confirm_send:  bool        = False
        self._pending_confirm            = False
        self._section_open:  dict        = {}
        self._inv_tag_map:   dict        = {}
        self._detail_eid:    Optional[str] = None

        self._build()
        self._load_world()
        self._poll()
        self._poll_investigations()

    # ── Layout ────────────────────────────────────────────────────────
    def _build(self) -> None:
        self._build_header()
        # thin amber trigger strip at very top (investigation)
        self._inv_strip = ctk.CTkFrame(self, fg_color="#431407", height=4,
                                       corner_radius=0, cursor="hand2")
        self._inv_strip.pack(fill="x")
        self._inv_strip.bind("<Enter>", lambda _: self._show_inv_panel())
        self._inv_strip.bind("<Button-1>", lambda _: self._show_inv_panel())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # Center: narrative + input
        self._center_col = ctk.CTkFrame(body, fg_color="transparent")
        self._center_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._build_narrative()

        # Quest panel
        qf = _panel(body, w=self.PANEL_W, r=12)
        qf.pack(side="left", fill="y", padx=(0, 10))
        qf.pack_propagate(False)
        self._build_quest_panel(qf)

        # Compendium
        cf = _panel(body, w=self.PANEL_W, r=12)
        cf.pack(side="left", fill="y")
        cf.pack_propagate(False)
        self._build_compendium(cf)

    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color=S900, height=64, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        hl = ctk.CTkFrame(hdr, fg_color="transparent")
        hl.pack(side="left", padx=24, fill="y")
        self.world_lbl = ctk.CTkLabel(hl, text="Loading…",
                                      font=("", 20, "bold"), text_color=S100)
        self.world_lbl.pack(side="left", pady=20)
        self.premise_lbl = _label(hl, "", S600, 12)
        self.premise_lbl.pack(side="left", padx=(12, 0), pady=20)

        hr = ctk.CTkFrame(hdr, fg_color="transparent")
        hr.pack(side="right", padx=20, pady=14)

        # Investigation points pill
        inv_pill = ctk.CTkFrame(hr, fg_color=A950, corner_radius=999,
                                border_width=1, border_color=A800)
        inv_pill.pack(side="left", padx=(0, 8))
        _label(inv_pill, "\U0001f50d", A400, 11).pack(side="left", padx=(10, 2), pady=6)
        self.inv_pill_lbl = _label(inv_pill, "5/5", A300, 12)
        self.inv_pill_lbl.pack(side="left", padx=(0, 10), pady=6)

        _btn(hr, "Worlds", self._show_world_switcher, w=72).pack(side="left", padx=(0, 6))
        _btn(hr, "Home", self.app.show_dashboard, w=62).pack(side="left", padx=(0, 6))
        _btn(hr, "Logout", self.app.show_login, w=70,
             bg="#7f1d1d", hbg="#991b1b", fg="#fca5a5").pack(side="left")

    def _build_narrative(self) -> None:
        """Narrative text + input form inside a rounded panel."""
        panel = _panel(self._center_col, r=12)
        panel.pack(fill="both", expand=True)

        # Story text
        self.story = tk.Text(
            panel,
            bg=S900, fg=S300,
            font=("Georgia", 13),
            wrap="word", relief="flat", bd=0,
            state="disabled",
            highlightthickness=0,
            padx=24, pady=20,
            cursor="arrow",
            spacing1=2, spacing3=6,
            selectbackground=S700, selectforeground=S100,
        )
        self.story.pack(fill="both", expand=True)
        self._configure_tags()

        # Investigation drop panel (lives inside narrative panel, hidden by default)
        self._inv_panel = ctk.CTkFrame(panel, fg_color=S950,
                                       border_width=1, border_color=A800,
                                       corner_radius=0, height=0)
        # Don't pack yet — shown on demand
        self._inv_panel.pack_propagate(False)
        self._build_inv_panel_content()

        # Divider above input
        ctk.CTkFrame(panel, fg_color=S800, height=1).pack(fill="x")

        # Input area
        inp = ctk.CTkFrame(panel, fg_color=S950, corner_radius=0)
        inp.pack(fill="x")

        # Quick-action chips
        chips = ctk.CTkFrame(inp, fg_color="transparent")
        chips.pack(fill="x", padx=16, pady=(10, 0))
        for chip in ["Look around", "Wait and listen", "Examine…",
                     "Speak to…", "Search…"]:
            ctk.CTkButton(chips, text=chip, width=0, height=24,
                          fg_color=S800, hover_color=S700, border_width=1,
                          border_color=S700, font=("", 10), text_color=S400,
                          corner_radius=999,
                          command=lambda t=chip: self._quick_action(t)
                          ).pack(side="left", padx=(0, 4))

        # Form row
        form = ctk.CTkFrame(inp, fg_color="transparent")
        form.pack(fill="x", padx=14, pady=(8, 0))

        self.input_var = tk.StringVar()
        self.input_box = ctk.CTkEntry(form, textvariable=self.input_var,
                                      height=48, font=("", 14),
                                      placeholder_text="What do you do?",
                                      fg_color=S800, border_color=S700,
                                      text_color=S100, corner_radius=8)
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_box.bind("<Return>",     lambda _: self._send())
        self.input_box.bind("<Up>",         lambda _: self._hist_up())
        self.input_box.bind("<Down>",       lambda _: self._hist_down())
        self.input_box.bind("<Escape>",     lambda _: self._cancel_confirm())
        self.input_box.bind("<KeyRelease>", lambda _: self._on_input_change())

        # Act button column
        act_col = ctk.CTkFrame(form, fg_color="transparent")
        act_col.pack(side="right")

        time_row = ctk.CTkFrame(act_col, fg_color="transparent")
        time_row.pack(fill="x")
        self.time_lbl = _label(time_row, "", S600, 10)
        self.time_lbl.pack(side="right")
        self.skip_btn = ctk.CTkButton(time_row, text="↷", width=18, height=16,
                                      fg_color="transparent", hover_color=S800,
                                      text_color=S600, font=("", 12),
                                      command=self._show_skip_time)
        self.skip_btn.pack(side="right", padx=(0, 2))
        self.skip_btn.pack_forget()

        self.send_btn = ctk.CTkButton(act_col, text="Act", width=80, height=48,
                                      fg_color=A800, hover_color=A700,
                                      text_color=A100, font=("", 14, "bold"),
                                      command=self._send)
        self.send_btn.pack()

        # Hint row
        hint_row = ctk.CTkFrame(inp, fg_color="transparent")
        hint_row.pack(fill="x", padx=16, pady=(4, 10))
        self.hint_lbl = _label(hint_row, "Enter to send", S700, 11)
        self.hint_lbl.pack(side="left")
        self.char_lbl = _label(hint_row, "", S700, 11)
        self.char_lbl.pack(side="left", padx=(8, 0))
        # settings gear
        ctk.CTkButton(hint_row, text="⚙", width=20, height=20,
                      fg_color="transparent", hover_color=S800,
                      text_color=S600, font=("", 13),
                      command=self._open_settings).pack(side="right")

    def _build_inv_panel_content(self) -> None:
        hdr = ctk.CTkFrame(self._inv_panel, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(10, 6))
        _label(hdr, "\U0001f50d  Investigations", S200, 13).pack(side="left")
        ctk.CTkButton(hdr, text="×", width=28, height=28,
                      fg_color="transparent", hover_color=S800,
                      text_color=S600, font=("", 14),
                      command=self._hide_inv_panel).pack(side="right")
        ctk.CTkFrame(self._inv_panel, fg_color=S800, height=1).pack(fill="x")
        self.inv_queue_frame = ctk.CTkScrollableFrame(
            self._inv_panel, fg_color="transparent",
            height=90, orientation="horizontal", border_width=0)
        self.inv_queue_frame.pack(fill="x", padx=10, pady=8)
        _label(self.inv_queue_frame, "No active investigations", S600, 12).pack(padx=10)

    def _build_quest_panel(self, parent: ctk.CTkFrame) -> None:
        # Header
        qhdr = ctk.CTkFrame(parent, fg_color="transparent", height=48)
        qhdr.pack(fill="x")
        qhdr.pack_propagate(False)
        ctk.CTkFrame(qhdr, fg_color=P600, width=3, corner_radius=999,
                     height=18).pack(side="left", padx=(14, 8), pady=14)
        _label(qhdr, "Current Goals", S200, 13).pack(side="left", pady=14)
        ctk.CTkFrame(parent, fg_color=S800, height=1).pack(fill="x")

        self.quest_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                                    border_width=0)
        self.quest_scroll.pack(fill="both", expand=True)

    def _build_compendium(self, parent: ctk.CTkFrame) -> None:
        # Header
        chdr = ctk.CTkFrame(parent, fg_color="transparent", height=48)
        chdr.pack(fill="x")
        chdr.pack_propagate(False)
        ctk.CTkFrame(chdr, fg_color=A700, width=3, corner_radius=999,
                     height=18).pack(side="left", padx=(14, 8), pady=14)
        _label(chdr, "Compendium", S200, 13).pack(side="left", pady=14)
        ctk.CTkFrame(parent, fg_color=S800, height=1).pack(fill="x")

        # Search
        search_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        search_wrap.pack(fill="x", padx=10, pady=(8, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._render_compendium())
        ctk.CTkEntry(search_wrap, textvariable=self.search_var,
                     height=28, font=("", 11),
                     placeholder_text="Search…",
                     fg_color=S800, border_color=S700,
                     text_color=S100).pack(fill="x")

        # Entity list
        self.compendium = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                                  border_width=0)
        self.compendium.pack(fill="both", expand=True, padx=4, pady=4)

        # Detail pane (slides up at bottom)
        self.detail_pane = ctk.CTkFrame(parent, fg_color=S950, corner_radius=0,
                                         border_width=1, border_color=S800, height=0)
        self.detail_pane.pack(fill="x")
        self.detail_pane.pack_propagate(False)
        self._build_detail_pane()

    def _build_detail_pane(self) -> None:
        dhdr = ctk.CTkFrame(self.detail_pane, fg_color=S900)
        dhdr.pack(fill="x")
        self.detail_name = ctk.CTkLabel(dhdr, text="",
                                         font=("", 13, "bold"), text_color=S100)
        self.detail_name.pack(side="left", padx=12, pady=7)
        ctk.CTkButton(dhdr, text="×", width=26, height=26,
                      fg_color="transparent", hover_color=S800,
                      text_color=S600, font=("", 13),
                      command=self._close_detail).pack(side="right", padx=6)
        self.detail_type = _label(dhdr, "", S600, 10)
        self.detail_type.pack(side="left", pady=7)
        ctk.CTkFrame(self.detail_pane, fg_color=S800, height=1).pack(fill="x")
        self.detail_scroll = ctk.CTkScrollableFrame(
            self.detail_pane, fg_color="transparent", height=170, border_width=0)
        self.detail_scroll.pack(fill="x", padx=10, pady=4)

    def _configure_tags(self) -> None:
        self.story.tag_configure("narration", foreground=S300,
                                              font=("Georgia", 13))
        self.story.tag_configure("player",    foreground="#93c5fd",
                                              font=("Georgia", 13, "bold"))
        self.story.tag_configure("muted",     foreground=S600,
                                              font=("", 12))
        self.story.tag_configure("error",     foreground=RED,
                                              font=("", 12))
        self.story.tag_configure("thinking",  foreground=A400,
                                              font=("", 12, "italic"))
        self.story.tag_configure("inv_link",  foreground=A300,
                                              font=("Georgia", 13),
                                              underline=True)
        self.story.tag_configure("inv_done",  foreground=S600,
                                              font=("Georgia", 13))

    # ── World loading ─────────────────────────────────────────────────
    def _load_world(self) -> None:
        try:
            worlds = self.app.service.list_worlds()
            w = next((x for x in worlds.get("worlds", [])
                      if x.get("world_id") == self.world_id), None)
            if w:
                self.world_lbl.configure(text=w.get("name", ""))
                premise = (w.get("premise") or "")[:80]
                if premise:
                    self.premise_lbl.configure(
                        text=("  " + premise + ("…" if len(w.get("premise",""))>80 else "")))
                label = w.get("game_time_label", "")
                if label:
                    self.time_lbl.configure(text=label)
                    self.skip_btn.pack(side="right", padx=(0, 2))
        except Exception:
            pass

        try:
            handoff = self.app.service.get_world_handoff(self.world_id)
            scene   = handoff.get("handoff") or handoff.get("handoff_text", "")
            if scene:
                self._append_narration(scene + "\n\n")
            else:
                self._append("World loaded. What do you do?\n\n", "muted")
        except Exception:
            self._append("World loaded. What do you do?\n\n", "muted")

        self._refresh_entities()
        self._refresh_quests()
        self._refresh_inv_balance()
        self.input_box.focus()

    # ── Compendium ────────────────────────────────────────────────────
    def _refresh_entities(self) -> None:
        try:
            self.entities = self.app.service.list_entities(
                world=self.world_id).get("entities", [])
        except Exception:
            self.entities = []
        self._render_compendium()

    def _render_compendium(self) -> None:
        for w in self.compendium.winfo_children():
            w.destroy()

        q = self.search_var.get().lower().strip()
        groups: dict[str, list] = {}
        for e in self.entities:
            etype = e.get("entity_type", "unknown")
            if q and q not in e.get("name", "").lower():
                continue
            groups.setdefault(etype, []).append(e)

        if not groups:
            _label(self.compendium,
                   "No entities yet." if not q else "No matches.",
                   S600, 11).pack(pady=12)
            return

        order = ["character", "location", "faction", "object", "event"]
        for etype in order + [t for t in groups if t not in order]:
            if etype not in groups:
                continue
            color = TYPE_COLORS.get(etype, S500)
            key   = f"sec_{etype}"
            open_ = self._section_open.get(key, True)
            icon  = tk.StringVar(value="▾" if open_ else "▸")

            # Section header
            sec_hdr = ctk.CTkFrame(self.compendium, fg_color=S800,
                                   corner_radius=6, cursor="hand2")
            sec_hdr.pack(fill="x", pady=(4, 0))
            hr = ctk.CTkFrame(sec_hdr, fg_color="transparent")
            hr.pack(fill="x", padx=8, pady=5)
            icon_lbl = ctk.CTkLabel(hr, textvariable=icon,
                                    font=("", 10), text_color=color, width=12)
            icon_lbl.pack(side="left")
            _label(hr, f"  {etype.upper()}  ({len(groups[etype])})",
                   color, 10).pack(side="left")

            # Body
            body = ctk.CTkFrame(self.compendium, fg_color="transparent")
            if open_:
                body.pack(fill="x")

            for e in groups[etype]:
                eid  = e.get("entity_id", "")
                name = e.get("name", "?")

                row = ctk.CTkFrame(body, fg_color="transparent", cursor="hand2")
                row.pack(fill="x", pady=1, padx=4)
                dot = ctk.CTkFrame(row, fg_color=color, width=5, height=5,
                                   corner_radius=999)
                dot.pack(side="left", padx=(8, 6), pady=9)
                nl = ctk.CTkLabel(row, text=name, font=("", 12),
                                  text_color=S300, anchor="w")
                nl.pack(side="left", fill="x", expand=True)

                for w in (row, dot, nl):
                    w.bind("<Button-1>", lambda _, i=eid: self._open_detail(i))
                    w.bind("<Enter>",    lambda _, r=row: r.configure(fg_color=S800))
                    w.bind("<Leave>",    lambda _, r=row: r.configure(fg_color="transparent"))

            def _toggle(key=key, body=body, icon=icon):
                now = self._section_open.get(key, True)
                self._section_open[key] = not now
                if not now:
                    body.pack(fill="x")
                    icon.set("▾")
                else:
                    body.pack_forget()
                    icon.set("▸")

            for w in (sec_hdr, hr, icon_lbl):
                w.bind("<Button-1>", lambda _, t=_toggle: t())

    # ── Entity detail ─────────────────────────────────────────────────
    def _open_detail(self, eid: str) -> None:
        if self._detail_eid == eid:
            self._close_detail()
            return
        self._detail_eid = eid
        e = next((x for x in self.entities if x.get("entity_id") == eid), None)
        if not e:
            return
        self.detail_name.configure(text=e.get("name", ""))
        self.detail_type.configure(
            text=f"  {e.get('entity_type','')}  ·  {e.get('status','')}")
        self.detail_pane.configure(height=270)
        for w in self.detail_scroll.winfo_children():
            w.destroy()
        _label(self.detail_scroll, "Loading…", S600, 11).pack(pady=8)

        def _fetch():
            try:
                ed  = self.app.service.get_entity(eid, world=self.world_id)
                sd  = self.app.service.get_entity_stats(eid, world=self.world_id)
                ent = ed.get("entity", e)
                sts = sd.get("stats", {})
            except Exception:
                ent, sts = e, {}
            self.after(0, lambda: self._render_detail(eid, ent, sts))

        threading.Thread(target=_fetch, daemon=True).start()

    def _render_detail(self, eid: str, e: dict, stats: dict) -> None:
        if self._detail_eid != eid:
            return
        for w in self.detail_scroll.winfo_children():
            w.destroy()
        summ = e.get("summary", "")
        if summ:
            _label(self.detail_scroll, summ, S400, 11,
                   wraplength=240, justify="left").pack(anchor="w", pady=(0, 6))
        for stat, val in (stats or {}).items():
            if not isinstance(val, (int, float)):
                continue
            pct = max(0, min(100, int(val)))
            br = ctk.CTkFrame(self.detail_scroll, fg_color="transparent")
            br.pack(fill="x", pady=1)
            _label(br, stat.capitalize(), S600, 10, width=70,
                   anchor="w").pack(side="left")
            fc = "#10b981" if pct >= 70 else "#3b82f6" if pct >= 40 else RED
            pb = ctk.CTkProgressBar(br, height=5, width=110,
                                    progress_color=fc, fg_color=S800)
            pb.set(pct / 100)
            pb.pack(side="left", padx=(4, 4))
            _label(br, str(pct), S600, 10).pack(side="left")
        for note in (e.get("timeline_notes") or []):
            r = ctk.CTkFrame(self.detail_scroll, fg_color="transparent")
            r.pack(fill="x", pady=1)
            _label(r, "•", S600, 11, width=10).pack(side="left")
            _label(r, note, S500, 11, wraplength=220,
                   justify="left").pack(side="left")
        for q in (e.get("open_questions") or []):
            r = ctk.CTkFrame(self.detail_scroll, fg_color="transparent")
            r.pack(fill="x", pady=1)
            _label(r, "?", A400, 11, width=10).pack(side="left")
            _label(r, q, S600, 11, wraplength=220,
                   justify="left").pack(side="left")
        if not summ and not stats and not e.get("timeline_notes"):
            _label(self.detail_scroll, "No details yet.", S600, 11).pack(pady=8)

    def _close_detail(self) -> None:
        self._detail_eid = None
        self.detail_pane.configure(height=0)

    # ── Quest panel ───────────────────────────────────────────────────
    def _refresh_quests(self) -> None:
        def _fetch():
            try:
                quests = self.app.service.list_quests(
                    world=self.world_id).get("quests", [])
            except Exception:
                quests = []
            self.after(0, lambda q=quests: self._render_quests(q))
        threading.Thread(target=_fetch, daemon=True).start()

    def _render_quests(self, quests: list) -> None:
        for w in self.quest_scroll.winfo_children():
            w.destroy()
        tier1   = [q for q in quests if q.get("tier")==1 and q.get("status")=="active"]
        tier2   = [q for q in quests if q.get("tier")==2 and q.get("status")=="active"]
        pending = [q for q in quests if q.get("status")=="pending_player"]

        if not tier1 and not tier2 and not pending:
            _label(self.quest_scroll, "No active goals yet.", S600, 11
                   ).pack(pady=12, padx=14)
            return

        def section(title, items, color):
            if not items: return
            _label(self.quest_scroll, title, color, 9).pack(
                anchor="w", padx=14, pady=(8, 2))
            for q in items: fn(q)

        def fn(q):
            f = ctk.CTkFrame(self.quest_scroll, fg_color=S800, corner_radius=8)
            f.pack(fill="x", padx=8, pady=3)
            inn = ctk.CTkFrame(f, fg_color="transparent")
            inn.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(inn, text=q.get("title",""), font=("", 11, "bold"),
                         text_color=S200, wraplength=220,
                         justify="left").pack(anchor="w")
            desc = q.get("description","")
            if desc:
                _label(inn, desc, S600, 10, wraplength=220,
                       justify="left").pack(anchor="w", pady=(2,0))
            td = q.get("progress_tags",[]) or []
            tt = q.get("completion_tags",[]) or []
            if tt:
                pb = ctk.CTkProgressBar(inn, height=2, progress_color=P600,
                                        fg_color=S700)
                pb.set(len(td)/len(tt))
                pb.pack(fill="x", pady=(5,0))
                _label(inn, f"{len(td)} of {len(tt)} milestones",
                       S600, 9).pack(anchor="w")

        def thread_fn(q):
            f = ctk.CTkFrame(self.quest_scroll, fg_color=S800, corner_radius=8)
            f.pack(fill="x", padx=8, pady=3)
            inn = ctk.CTkFrame(f, fg_color="transparent")
            inn.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(inn, text=q.get("title",""), font=("", 11),
                         text_color=S300, wraplength=200,
                         justify="left").pack(anchor="w")
            br = ctk.CTkFrame(inn, fg_color="transparent")
            br.pack(anchor="w", pady=(5,0))
            qid = q.get("quest_id","")
            ctk.CTkButton(br, text="Track", width=54, height=22,
                          fg_color="#312e81", hover_color="#3730a3",
                          text_color="#a5b4fc", font=("", 10),
                          command=lambda i=qid: self._promote_quest(i)
                          ).pack(side="left", padx=(0,4))
            ctk.CTkButton(br, text="Ignore", width=54, height=22,
                          fg_color=S800, hover_color=S700,
                          text_color=S600, font=("", 10),
                          command=lambda i=qid: self._dismiss_quest(i)
                          ).pack(side="left")

        section("OVERARCHING", tier1, "#7c6af7")
        section("ACTIVE", tier2, "#7c6af7")
        if pending:
            _label(self.quest_scroll, "THREADS — YOUR CALL", A400, 9
                   ).pack(anchor="w", padx=14, pady=(8,2))
            for q in pending: thread_fn(q)

    def _promote_quest(self, qid: str) -> None:
        def _d():
            try: self.app.service.promote_quest(qid, world=self.world_id)
            except Exception: pass
            self.after(0, self._refresh_quests)
        threading.Thread(target=_d, daemon=True).start()

    def _dismiss_quest(self, qid: str) -> None:
        def _d():
            try: self.app.service.dismiss_quest(qid, world=self.world_id)
            except Exception: pass
            self.after(0, self._refresh_quests)
        threading.Thread(target=_d, daemon=True).start()

    # ── Investigation ─────────────────────────────────────────────────
    def _refresh_inv_balance(self) -> None:
        def _f():
            try:
                b = self.app.service.get_investigation_balance(world=self.world_id)
                self.inv_balance = b.get("balance", 0)
                self.inv_max     = b.get("max_balance", 0)
            except Exception: pass
            self.after(0, self._update_inv_pill)
        threading.Thread(target=_f, daemon=True).start()

    def _update_inv_pill(self) -> None:
        self.inv_pill_lbl.configure(
            text=f"{self.inv_balance}/{self.inv_max}" if self.inv_max else "—")

    def _show_inv_panel(self) -> None:
        # Place investigation panel at top of narrative column
        self._inv_panel.place(in_=self._center_col, relx=0, rely=0,
                              relwidth=1, anchor="nw")
        self._inv_panel.configure(height=160)
        self._inv_panel.lift()

    def _hide_inv_panel(self) -> None:
        self._inv_panel.place_forget()

    def _render_inv_queue(self) -> None:
        for w in self.inv_queue_frame.winfo_children():
            w.destroy()

        active = [j for j in self.inv_jobs.values()
                  if j.get("status") in ("queued","processing")]
        done   = [j for j in self.inv_jobs.values()
                  if j.get("status") == "complete"]

        if not active and not done:
            _label(self.inv_queue_frame, "No active investigations",
                   S600, 12).pack(padx=10, pady=6)
            return

        for job in active:
            c = ctk.CTkFrame(self.inv_queue_frame, fg_color=S800,
                             corner_radius=8, width=160)
            c.pack(side="left", padx=(0,8), pady=4)
            c.pack_propagate(False)
            ci = ctk.CTkFrame(c, fg_color="transparent")
            ci.pack(fill="both", padx=10, pady=8)
            _label(ci, job.get("entity_name","?"), A300, 12).pack(anchor="w")
            _label(ci, "… investigating", S600, 10).pack(anchor="w")

        for job in done:
            c = ctk.CTkFrame(self.inv_queue_frame, fg_color="#1c1208",
                             corner_radius=8, width=180,
                             border_width=1, border_color=A800)
            c.pack(side="left", padx=(0,8), pady=4)
            c.pack_propagate(False)
            ci = ctk.CTkFrame(c, fg_color="transparent")
            ci.pack(fill="both", padx=10, pady=8)
            _label(ci, "✓  " + job.get("entity_name","?"),
                   "#86efac", 12).pack(anchor="w")
            ctk.CTkButton(ci, text="View findings", height=24, font=("",10),
                          fg_color=S800, hover_color=S700,
                          text_color=S400, border_width=0,
                          command=lambda j=job: self._view_inv_result(j)
                          ).pack(anchor="w", pady=(4,0))

    def _click_investigate(self, item: str, etype: str, cost: int) -> None:
        existing = next(
            (e for e in self.entities
             if e.get("name","").lower() == item.lower()), None)
        if existing:
            self._open_detail(existing["entity_id"])
            return
        self._show_investigate_confirm(item, etype, cost)

    def _show_investigate_confirm(self, item: str, etype: str, cost: int) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title("Investigate")
        dlg.configure(fg_color=S900)
        dlg.grab_set()
        _center(dlg, 420, 250)
        ctk.CTkLabel(dlg, text=f"Investigate: {item}",
                     font=("", 16, "bold"), text_color=S100
                     ).pack(pady=(28,10), padx=24, anchor="w")
        _label(dlg,
               f"Spend {cost} investigation point{'s' if cost!=1 else ''} "
               f"to dig deeper.\nYou have {self.inv_balance} available.",
               S400, 12, justify="left").pack(padx=24, anchor="w")
        _label(dlg, "The point is refunded when you review the findings.",
               S600, 11).pack(padx=24, anchor="w", pady=(4,20))
        br = ctk.CTkFrame(dlg, fg_color="transparent")
        br.pack(padx=24, anchor="e")
        _btn(br, "Cancel", dlg.destroy, w=90).pack(side="left", padx=(0,8))
        ok = "normal" if self.inv_balance >= cost else "disabled"
        ctk.CTkButton(br, text="Investigate", width=120, height=36,
                      fg_color=A800, hover_color=A700, text_color=A100,
                      font=("",13,"bold"), state=ok,
                      command=lambda: (
                          dlg.destroy(),
                          self._queue_investigation(item, etype, cost))
                      ).pack(side="left")

    def _queue_investigation(self, item: str, etype: str, cost: int) -> None:
        def _d():
            try:
                self.app.service.spend_investigation_points(cost, world=self.world_id)
                job = self.app.service.create_investigation_job(
                    item, etype, world=self.world_id)
                self.inv_jobs[job["job_id"]] = {
                    "job_id": job["job_id"], "entity_name": item,
                    "entity_type": etype, "status": "queued", "result": None}
                self.inv_balance = max(0, self.inv_balance - cost)
            except Exception as e:
                self.after(0, lambda m=str(e): self._flash_hint(m))
                return
            self.after(0, self._update_inv_pill)
            self.after(0, self._render_inv_queue)
        threading.Thread(target=_d, daemon=True).start()

    def _poll_investigations(self) -> None:
        active = [jid for jid, j in self.inv_jobs.items()
                  if j.get("status") in ("queued","processing")]
        if active:
            def _f():
                changed = False
                for jid in active:
                    try:
                        r = self.app.service.get_investigation_job(jid)
                        self.inv_jobs[jid]["status"] = r["status"]
                        if r["status"] == "complete" and r.get("result"):
                            self.inv_jobs[jid]["result"] = r["result"]
                            changed = True
                    except Exception: pass
                if changed:
                    self.after(0, self._on_inv_complete)
            threading.Thread(target=_f, daemon=True).start()
        self.after(2000, self._poll_investigations)

    def _on_inv_complete(self) -> None:
        self._render_inv_queue()
        self._refresh_entities()
        self._refresh_inv_balance()

    def _view_inv_result(self, job: dict) -> None:
        result = job.get("result") or {}
        entity = result.get("entity") if isinstance(result, dict) else None
        if entity and entity.get("entity_id"):
            self._open_detail(entity["entity_id"])
        jid = job.get("job_id")
        if jid in self.inv_jobs:
            del self.inv_jobs[jid]
        self._render_inv_queue()

    # ── Story text ────────────────────────────────────────────────────
    def _append(self, text: str, tag: str = "narration") -> None:
        self.story.configure(state="normal")
        self.story.insert("end", text, tag)
        self.story.configure(state="disabled")
        self.story.see("end")

    def _append_narration(self, text: str) -> None:
        self.story.configure(state="normal")
        for chunk, meta in _split_investigate(text):
            if meta is None:
                self.story.insert("end", chunk, "narration")
            else:
                item, etype, cost = meta
                already = any(e.get("name","").lower()==item.lower()
                              for e in self.entities)
                if already:
                    self.story.insert("end", chunk, "inv_done")
                else:
                    tn = f"inv_{len(self._inv_tag_map)}"
                    self._inv_tag_map[tn] = (item, etype, cost)
                    self.story.tag_configure(tn, foreground=A300, underline=True,
                                             font=("Georgia",13))
                    self.story.tag_bind(tn, "<Button-1>",
                        lambda _, n=item, t=etype, c=cost:
                            self._click_investigate(n, t, c))
                    self.story.tag_bind(tn, "<Enter>",
                        lambda _: self.story.configure(cursor="hand2"))
                    self.story.tag_bind(tn, "<Leave>",
                        lambda _: self.story.configure(cursor="arrow"))
                    self.story.insert("end", chunk, tn)
        self.story.configure(state="disabled")
        self.story.see("end")

    def _remove_thinking(self) -> None:
        self.story.configure(state="normal")
        content = self.story.get("1.0", "end")
        marker  = "Thinking…\n"
        idx = content.rfind(marker)
        if idx >= 0:
            self.story.delete(f"1.0+{idx}c", f"1.0+{idx+len(marker)}c")
        self.story.configure(state="disabled")

    # ── Input helpers ─────────────────────────────────────────────────
    def _on_input_change(self) -> None:
        n = len(self.input_var.get())
        self.char_lbl.configure(text=f"{n}" if n else "")

    def _quick_action(self, text: str) -> None:
        self.input_var.set(text)
        self.input_box.icursor("end")
        self.input_box.focus()

    def _hist_up(self) -> None:
        if not self._input_hist: return
        if self._hist_pos == -1:
            self._draft = self.input_var.get()
            self._hist_pos = len(self._input_hist) - 1
        elif self._hist_pos > 0:
            self._hist_pos -= 1
        self.input_var.set(self._input_hist[self._hist_pos])
        self.input_box.icursor("end")

    def _hist_down(self) -> None:
        if self._hist_pos == -1: return
        self._hist_pos += 1
        if self._hist_pos >= len(self._input_hist):
            self._hist_pos = -1
            self.input_var.set(self._draft)
        else:
            self.input_var.set(self._input_hist[self._hist_pos])
        self.input_box.icursor("end")

    def _cancel_confirm(self) -> None:
        if self._pending_confirm:
            self._pending_confirm = False
            self.input_box.configure(border_color=S700)
            self.hint_lbl.configure(text="Enter to send", text_color=S700)

    def _flash_hint(self, msg: str) -> None:
        self.hint_lbl.configure(text=msg, text_color=RED)
        self.after(3500, lambda: self.hint_lbl.configure(
            text="Enter to send", text_color=S700))

    # ── Send ──────────────────────────────────────────────────────────
    def _send(self) -> None:
        if self._busy: return
        action = self.input_var.get().strip()
        if not action: return

        if self._confirm_send and not self._pending_confirm:
            self._pending_confirm = True
            self.input_box.configure(border_color=A700)
            self.hint_lbl.configure(
                text="Press Enter to confirm  ·  Esc to cancel",
                text_color=A400)
            return

        self._cancel_confirm()

        if not self._input_hist or self._input_hist[-1] != action:
            self._input_hist.append(action)
        self._hist_pos = -1

        self.input_var.set("")
        self.char_lbl.configure(text="")
        self._busy = True
        self.send_btn.configure(state="disabled", text="…")

        self._append(f"\n> {action}\n\n", "player")
        self._append("Thinking…\n", "thinking")

        def work():
            try:
                from . import narrative as narr
                narration, self.conv_history = narr.process_user_action(
                    client=self.app.settings.anthropic_client,
                    service=self.app.service,
                    world_id=self.world_id,
                    user_action=action,
                    conversation_history=self.conv_history,
                    player_entity_id=self.app.current_user,
                )
                self._q.put(("ok", narration))
            except Exception as exc:
                self._q.put(("err", str(exc)))

        threading.Thread(target=work, daemon=True).start()

    # ── Poll ──────────────────────────────────────────────────────────
    def _poll(self) -> None:
        try:
            while True:
                kind, data = self._q.get_nowait()
                self._remove_thinking()
                if kind == "ok":
                    self._append_narration(data + "\n\n")
                    self._refresh_entities()
                    self._refresh_quests()
                    self._refresh_inv_balance()
                    try:
                        t = self.app.service.get_world_time(world=self.world_id)
                        lbl = t.get("label","") or _format_seconds(t.get("seconds",0))
                        if lbl:
                            self.time_lbl.configure(text=lbl)
                            self.skip_btn.pack(side="right", padx=(0,2))
                    except Exception: pass
                else:
                    self._append(f"[Error: {data}]\n\n", "error")
                self._busy = False
                self.send_btn.configure(state="normal", text="Act")
        except queue.Empty:
            pass
        self.after(120, self._poll)

    # ── Modals ────────────────────────────────────────────────────────
    def _show_world_switcher(self) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title("Switch World")
        dlg.configure(fg_color=S950)
        dlg.grab_set()
        _center(dlg, 480, 500)
        ctk.CTkLabel(dlg, text="Worlds", font=("Georgia", 18, "bold"),
                     text_color=S100).pack(padx=24, pady=(22,14), anchor="w")
        scroll = ctk.CTkScrollableFrame(dlg, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0,16))
        try:
            worlds = self.app.service.list_worlds().get("worlds", [])
        except Exception:
            worlds = []
        for world in worlds:
            wid, name = world.get("world_id",""), world.get("name","")
            premise = (world.get("premise") or "")[:70]
            row = _panel(scroll, r=8)
            row.pack(fill="x", pady=4)
            inn = ctk.CTkFrame(row, fg_color="transparent")
            inn.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(inn, text=name, font=("",13,"bold"),
                         text_color=S100).pack(anchor="w")
            if premise:
                _label(inn, premise+"…", S600, 11,
                       wraplength=360, justify="left").pack(anchor="w", pady=(4,8))
            _btn(inn, "Enter",
                 lambda w=wid: (dlg.destroy(), self.app.show_narrative(w)),
                 h=30).pack(anchor="w")

    def _show_skip_time(self) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title("Skip Time")
        dlg.configure(fg_color=S900)
        dlg.grab_set()
        _center(dlg, 300, 260)
        _label(dlg, "Skip time", S500, 10).pack(padx=16, pady=(16,4), anchor="w")
        for label, secs in SKIP_PRESETS:
            _btn(dlg, label, lambda s=secs: self._do_skip(dlg, s),
                 h=36).pack(fill="x", padx=14, pady=3)
        _btn(dlg, "Cancel", dlg.destroy, h=30,
             bg="transparent", hbg=S800, fg=S600).pack(pady=(4,0))

    def _do_skip(self, dlg, seconds: int) -> None:
        dlg.destroy()
        def _s():
            try:
                r = self.app.service.advance_world_time(seconds, world=self.world_id)
                lbl = r.get("label","") or _format_seconds(r.get("seconds",0))
                if lbl:
                    self.after(0, lambda l=lbl: self.time_lbl.configure(text=l))
            except Exception as e:
                self.after(0, lambda m=str(e): self._flash_hint(m))
        threading.Thread(target=_s, daemon=True).start()

    def _open_settings(self) -> None:
        SettingsDialog(self.app.root)


# ---------------------------------------------------------------------------
# Settings dialog
# ---------------------------------------------------------------------------
class SettingsDialog(ctk.CTkToplevel):
    """Modal dialog for editing .env values (API key, login, port, IPs).

    Reuses load_current_values() / write_env() from settings_window so the
    .env parsing and comment-preserving writer aren't duplicated.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        from .settings_window import EDITABLE_KEYS, load_current_values

        self._keys = EDITABLE_KEYS
        self._values = load_current_values()
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._show_vars: dict[str, tk.BooleanVar] = {}

        self.title("Ayen-Ode · Settings")
        self.configure(fg_color=S950)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build()
        _center(self, 540, 620)
        self.bind("<Escape>", lambda _e: self.destroy())

    def _build(self) -> None:
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=24, pady=22)

        ctk.CTkLabel(outer, text="Ayen-Ode",
                     font=("Georgia", 20, "bold"), text_color=S100
                     ).pack(anchor="w")
        _label(outer, "Local settings · these write to your .env file",
               S500, 11).pack(anchor="w", pady=(0, 16))

        panel = _panel(outer, r=10)
        panel.pack(fill="x")
        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        for key, label, hint, is_secret in self._keys:
            self._build_field(inner, key, label, hint, is_secret)

        row = ctk.CTkFrame(outer, fg_color="transparent")
        row.pack(fill="x", pady=(16, 0))
        self.status_lbl = _label(row, "", S500, 11)
        self.status_lbl.pack(side="left")

        ctk.CTkButton(row, text="Save", width=110, height=36,
                      fg_color=A800, hover_color=A700, text_color=A100,
                      font=("", 13, "bold"),
                      command=self._save).pack(side="right")
        _btn(row, "Cancel", self.destroy, w=90, h=36
             ).pack(side="right", padx=(0, 8))

    def _build_field(self, parent, key: str, label: str, hint: str,
                     is_secret: bool) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 12))

        _label(wrap, label.upper(), S400, 9).pack(anchor="w")

        entry = ctk.CTkEntry(wrap, height=34, font=("", 12),
                             fg_color=S800, border_color=S700,
                             text_color=S100)
        entry.insert(0, self._values.get(key, ""))
        if is_secret:
            entry.configure(show="•")
        entry.pack(fill="x", pady=(4, 2))
        self._entries[key] = entry

        bottom = ctk.CTkFrame(wrap, fg_color="transparent")
        bottom.pack(fill="x")
        _label(bottom, hint, S600, 10).pack(side="left")

        if is_secret:
            var = tk.BooleanVar(value=False)
            self._show_vars[key] = var
            def toggle(e=entry, v=var):
                e.configure(show="" if v.get() else "•")
            ctk.CTkCheckBox(bottom, text="show", variable=var, command=toggle,
                            fg_color=A800, hover_color=A700,
                            text_color=S500, font=("", 10),
                            checkbox_width=14, checkbox_height=14,
                            border_width=1, border_color=S700
                            ).pack(side="right")

    def _save(self) -> None:
        from tkinter import messagebox
        from .settings_window import write_env

        new_values = {k: self._entries[k].get().strip() for k, *_ in self._keys}

        api_key = new_values.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            messagebox.showwarning(
                "API key required",
                "ANTHROPIC_API_KEY is empty. The app will start but narrative "
                "actions will fail until a key is set.",
                parent=self,
            )
        elif not api_key.startswith("sk-ant-"):
            if not messagebox.askyesno(
                "Unusual API key",
                "Anthropic API keys usually start with 'sk-ant-'. Save anyway?",
                parent=self,
            ):
                return

        try:
            write_env(new_values)
        except OSError as e:
            messagebox.showerror(
                "Couldn't save settings",
                f"Failed to write .env:\n\n{e}",
                parent=self,
            )
            return

        self.status_lbl.configure(text="Saved. Restart Ayen-Ode to apply.",
                                  text_color=GRN)
        self.after(900, self.destroy)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def run() -> None:
    app = AyenOdeApp()
    app.run()


if __name__ == "__main__":
    run()
