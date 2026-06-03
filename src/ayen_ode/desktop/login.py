import tkinter as tk
import customtkinter as ctk

from .colors import S950, S100, S500, S400, A800, A700, A100, RED
from .widgets import _label, _entry, _panel


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
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
