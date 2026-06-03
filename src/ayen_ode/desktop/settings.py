import tkinter as tk
import customtkinter as ctk

from .colors import S950, S100, S800, S700, S600, S500, S400, A800, A700, A100, GRN
from .widgets import _label, _panel, _btn, _center


class SettingsDialog(ctk.CTkToplevel):
    """Modal dialog for editing .env values (API key, login, port, IPs).

    Reuses load_current_values() / write_env() from settings_window so the
    .env parsing and comment-preserving writer aren't duplicated.
    """

    def __init__(self, parent) -> None:
        super().__init__(parent)
        from ..settings_window import EDITABLE_KEYS, load_current_values

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
        from ..settings_window import write_env

        new_values = {k: self._entries[k].get().strip() for k, *_ in self._keys}



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
