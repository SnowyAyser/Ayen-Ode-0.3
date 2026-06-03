import threading
import customtkinter as ctk
from .colors import S200, S800, S700, S600, S300, P600, A400
from .widgets import _label


class QuestPanel:
    def __init__(self, parent_frame, controller) -> None:
        self.parent = parent_frame
        self.controller = controller
        self._build()

    def _build(self) -> None:
        # Header
        qhdr = ctk.CTkFrame(self.parent, fg_color="transparent", height=48)
        qhdr.pack(fill="x")
        qhdr.pack_propagate(False)
        ctk.CTkFrame(qhdr, fg_color=P600, width=3, corner_radius=999,
                     height=18).pack(side="left", padx=(14, 8), pady=14)
        _label(qhdr, "Current Goals", S200, 13).pack(side="left", pady=14)
        ctk.CTkFrame(self.parent, fg_color=S800, height=1).pack(fill="x")

        self.quest_scroll = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                                    border_width=0)
        self.quest_scroll.pack(fill="both", expand=True)

    def render_quests(self, quests: list) -> None:
        for w in self.quest_scroll.winfo_children():
            w.destroy()
        tier1   = [q for q in quests if q.get("tier") == 1 and q.get("status") == "active"]
        tier2   = [q for q in quests if q.get("tier") == 2 and q.get("status") == "active"]
        pending = [q for q in quests if q.get("status") == "pending_player"]

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
            ctk.CTkLabel(inn, text=q.get("title", ""), font=("", 11, "bold"),
                          text_color=S200, wraplength=220,
                          justify="left").pack(anchor="w")
            desc = q.get("description", "")
            if desc:
                _label(inn, desc, S600, 10, wraplength=220,
                       justify="left").pack(anchor="w", pady=(2, 0))
            td = q.get("progress_tags", []) or []
            tt = q.get("completion_tags", []) or []
            if tt:
                pb = ctk.CTkProgressBar(inn, height=2, progress_color=P600,
                                        fg_color=S700)
                pb.set(len(td) / len(tt))
                pb.pack(fill="x", pady=(5, 0))
                _label(inn, f"{len(td)} of {len(tt)} milestones",
                       S600, 9).pack(anchor="w")

        def thread_fn(q):
            f = ctk.CTkFrame(self.quest_scroll, fg_color=S800, corner_radius=8)
            f.pack(fill="x", padx=8, pady=3)
            inn = ctk.CTkFrame(f, fg_color="transparent")
            inn.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(inn, text=q.get("title", ""), font=("", 11),
                          text_color=S300, wraplength=200,
                          justify="left").pack(anchor="w")
            br = ctk.CTkFrame(inn, fg_color="transparent")
            br.pack(anchor="w", pady=(5, 0))
            qid = q.get("quest_id", "")
            ctk.CTkButton(br, text="Track", width=54, height=22,
                          fg_color="#312e81", hover_color="#3730a3",
                          text_color="#a5b4fc", font=("", 10),
                          command=lambda i=qid: self._promote_quest(i)
                          ).pack(side="left", padx=(0, 4))
            ctk.CTkButton(br, text="Ignore", width=54, height=22,
                          fg_color=S800, hover_color=S700,
                          text_color=S600, font=("", 10),
                          command=lambda i=qid: self._dismiss_quest(i)
                          ).pack(side="left")

        section("OVERARCHING", tier1, "#7c6af7")
        section("ACTIVE", tier2, "#7c6af7")
        if pending:
            _label(self.quest_scroll, "THREADS — YOUR CALL", A400, 9
                   ).pack(anchor="w", padx=14, pady=(8, 2))
            for q in pending: thread_fn(q)

    def _promote_quest(self, qid: str) -> None:
        def _d():
            try:
                self.controller.app.service.promote_quest(qid, world=self.controller.world_id)
            except Exception: pass
            self.parent.after(0, self.controller._refresh_quests)
        threading.Thread(target=_d, daemon=True).start()

    def _dismiss_quest(self, qid: str) -> None:
        def _d():
            try:
                self.controller.app.service.dismiss_quest(qid, world=self.controller.world_id)
            except Exception: pass
            self.parent.after(0, self.controller._refresh_quests)
        threading.Thread(target=_d, daemon=True).start()
