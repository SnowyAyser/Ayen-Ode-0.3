import tkinter as tk
import customtkinter as ctk
import threading
from .colors import S900, S800, S700, S600, S500, S400, S300, S200, S100, A800, A700, A400, A300, A100, RED
from .widgets import _label, _btn, _split_investigate


class NarrativeView:
    def __init__(self, parent_frame, controller) -> None:
        self.parent = parent_frame
        self.controller = controller
        self._build()

    def _build(self) -> None:
        # Story area
        story_wrap = ctk.CTkFrame(self.parent, fg_color="transparent")
        story_wrap.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Native Tkinter Text widget is best for complex multi-font tag styles
        self.controller.story = tk.Text(
            story_wrap, wrap="word", bg=S900, fg=S300, bd=0, highlightthickness=0,
            padx=4, pady=4, cursor="arrow", font=("Georgia", 13)
        )
        self.controller.story.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(story_wrap, command=self.controller.story.yview)
        scrollbar.pack(side="right", fill="y")
        self.controller.story.configure(yscrollcommand=scrollbar.set)

        # Input form wrap
        form_wrap = ctk.CTkFrame(self.parent, fg_color="transparent")
        form_wrap.pack(fill="x", padx=20, pady=(0, 20))

        self.controller.input_var = tk.StringVar()
        self.controller.input_var.trace_add("write", lambda *_: self._on_input_change())

        ib = ctk.CTkFrame(form_wrap, fg_color=S800, corner_radius=8,
                           border_width=1, border_color=S700)
        ib.pack(fill="x", side="left", expand=True, padx=(0, 10))

        self.controller.input_box = ctk.CTkEntry(
            ib, textvariable=self.controller.input_var, font=("Georgia", 13),
            placeholder_text="What do you do?",
            fg_color="transparent", border_width=0, text_color=S100
        )
        self.controller.input_box.pack(fill="x", side="left", expand=True, padx=12, pady=10)

        self.controller.char_lbl = _label(ib, "", S600, 11)
        self.controller.char_lbl.pack(side="right", padx=(0, 14), pady=10)

        self.controller.send_btn = ctk.CTkButton(
            form_wrap, text="Act", width=90, height=44,
            fg_color=A800, hover_color=A700, text_color=A100,
            font=("", 13, "bold"), command=self._send
        )
        self.controller.send_btn.pack(side="right")

        # Bottom hint line
        hints = ctk.CTkFrame(self.parent, fg_color="transparent", height=16)
        hints.pack(fill="x", padx=24, pady=(0, 10))
        hints.pack_propagate(False)
        self.controller.hint_lbl = _label(hints, "Enter to send", S700, 10)
        self.controller.hint_lbl.pack(side="left")

        # Quick action suggestions row
        self.controller.quick_row = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.controller.quick_row.pack(fill="x", padx=20, pady=(0, 10))

        self.controller.input_box.bind("<Return>", lambda _: self._send())
        self.controller.input_box.bind("<Up>",     lambda _: self._hist_up())
        self.controller.input_box.bind("<Down>",   lambda _: self._hist_down())
        self.controller.input_box.bind("<Escape>", lambda _: self._cancel_confirm())

    # ── Story text ────────────────────────────────────────────────────
    def append(self, text: str, tag: str = "narration") -> None:
        self.controller.story.configure(state="normal")
        self.controller.story.insert("end", text, tag)
        self.controller.story.configure(state="disabled")
        self.controller.story.see("end")

    def append_narration(self, text: str) -> None:
        self.controller.story.configure(state="normal")
        for chunk, meta in _split_investigate(text):
            if meta is None:
                self.controller.story.insert("end", chunk, "narration")
            else:
                item, etype, cost = meta
                already = any(e.get("name", "").lower() == item.lower()
                              for e in self.controller.entities)
                if already:
                    self.controller.story.insert("end", chunk, "inv_done")
                else:
                    tn = f"inv_{len(self.controller._inv_tag_map)}"
                    self.controller._inv_tag_map[tn] = (item, etype, cost)
                    self.controller.story.tag_configure(tn, foreground=A300, underline=True,
                                                         font=("Georgia", 13))
                    self.controller.story.tag_bind(tn, "<Button-1>",
                        lambda _, n=item, t=etype, c=cost:
                            self.controller.investigation_overlay.click_investigate(n, t, c))
                    self.controller.story.tag_bind(tn, "<Enter>",
                        lambda _: self.controller.story.configure(cursor="hand2"))
                    self.controller.story.tag_bind(tn, "<Leave>",
                        lambda _: self.controller.story.configure(cursor="arrow"))
                    self.controller.story.insert("end", chunk, tn)
        self.controller.story.configure(state="disabled")
        self.controller.story.see("end")

    def remove_thinking(self) -> None:
        self.controller.story.configure(state="normal")
        content = self.controller.story.get("1.0", "end")
        marker  = "Thinking…\n"
        idx = content.rfind(marker)
        if idx >= 0:
            self.controller.story.delete(f"1.0+{idx}c", f"1.0+{idx+len(marker)}c")
        self.controller.story.configure(state="disabled")

    # ── Input helpers ─────────────────────────────────────────────────
    def _on_input_change(self) -> None:
        n = len(self.controller.input_var.get())
        self.controller.char_lbl.configure(text=f"{n}" if n else "")

    def quick_action(self, text: str) -> None:
        self.controller.input_var.set(text)
        self.controller.input_box.icursor("end")
        self.controller.input_box.focus()

    def _hist_up(self) -> None:
        if not self.controller._input_hist: return
        if self.controller._hist_pos == -1:
            self.controller._draft = self.controller.input_var.get()
            self.controller._hist_pos = len(self.controller._input_hist) - 1
        elif self.controller._hist_pos > 0:
            self.controller._hist_pos -= 1
        self.controller.input_var.set(self.controller._input_hist[self.controller._hist_pos])
        self.controller.input_box.icursor("end")

    def _hist_down(self) -> None:
        if self.controller._hist_pos == -1: return
        self.controller._hist_pos += 1
        if self.controller._hist_pos >= len(self.controller._input_hist):
            self.controller._hist_pos = -1
            self.controller.input_var.set(self.controller._draft)
        else:
            self.controller.input_var.set(self.controller._input_hist[self.controller._hist_pos])
        self.controller.input_box.icursor("end")

    def _cancel_confirm(self) -> None:
        if self.controller._pending_confirm:
            self.controller._pending_confirm = False
            self.controller.input_box.configure(border_color=S700)
            self.controller.hint_lbl.configure(text="Enter to send", text_color=S700)

    def flash_hint(self, msg: str) -> None:
        self.controller.hint_lbl.configure(text=msg, text_color=RED)
        self.controller.after(3500, lambda: self.controller.hint_lbl.configure(
            text="Enter to send", text_color=S700))

    # ── Send ──────────────────────────────────────────────────────────
    def _send(self) -> None:
        if self.controller._busy: return
        action = self.controller.input_var.get().strip()
        if not action: return

        if self.controller._confirm_send and not self.controller._pending_confirm:
            self.controller._pending_confirm = True
            self.controller.input_box.configure(border_color=A700)
            self.controller.hint_lbl.configure(
                text="Press Enter to confirm  ·  Esc to cancel",
                text_color=A400)
            return

        self._cancel_confirm()

        if not self.controller._input_hist or self.controller._input_hist[-1] != action:
            self.controller._input_hist.append(action)
        self.controller._hist_pos = -1

        self.controller.input_var.set("")
        self.controller.char_lbl.configure(text="")
        self.controller._busy = True
        self.controller.send_btn.configure(state="disabled", text="…")

        self.append(f"\n> {action}\n\n", "player")
        self.append("Thinking…\n", "thinking")

        def work():
            try:
                from .. import narrative as narr
                result = narr.process_user_action(
                    client=self.controller.app.settings.anthropic_client,
                    service=self.controller.app.service,
                    world_id=self.controller.world_id,
                    user_action=action,
                    conversation_history=self.controller.conv_history,
                    player_entity_id=self.controller.app.current_user,
                )
                narration = result[0]
                self.controller.conv_history = result[1]
                self.controller._q.put(("ok", narration))
            except Exception as exc:
                self.controller._q.put(("err", str(exc)))

        threading.Thread(target=work, daemon=True).start()
