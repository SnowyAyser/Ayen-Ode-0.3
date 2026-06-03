import tkinter as tk
import customtkinter as ctk
import threading
from typing import Optional

from .colors import S950, S900, S800, S700, S500, S400, S300, S100, A800, A700, A100, RED, GRN
from .widgets import _label, _panel, _btn, _divider, _bind_click_recursive, _center
from .settings import SettingsDialog


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
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
            result = self.app.service.reset_world(wid)
            original_text = result.get("world", {}).get("original_opening_scene", "")
            if original_text and self.app.settings.anthropic_client:
                try:
                    from ..relinker import pre_generate_scene_investigations_sync
                    threading.Thread(
                        target=pre_generate_scene_investigations_sync,
                        args=(self.app.settings.anthropic_client, self.app.service, wid, original_text),
                        daemon=True
                    ).start()
                except Exception:
                    pass
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
