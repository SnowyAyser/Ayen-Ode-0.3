import tkinter as tk
import customtkinter as ctk
import threading

from .colors import S950, S900, S800, S700, S500, S300, S100, A800, A700, A100, RED
from .widgets import _label, _panel, _btn


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
    def __init__(self, parent, app) -> None:
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
                from .. import narrative as narr
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
