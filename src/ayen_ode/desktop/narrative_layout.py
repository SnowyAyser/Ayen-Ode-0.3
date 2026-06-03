import queue
import threading
import tkinter as tk
import customtkinter as ctk
from typing import Optional

from .colors import (
    S950, S900, S800, S700, S600, S500, S400, S300, S200, S100,
    A950, A800, A700, A400, A300, A100, RED, GRN, P600, SKIP_PRESETS
)
from .widgets import _label, _panel, _btn, _center, _format_seconds
from .narrative_view import NarrativeView
from .quest_panel import QuestPanel
from .compendium_panel import CompendiumPanel
from .investigation_overlay import InvestigationOverlay
from .settings import SettingsDialog


class NarrativeFrame(ctk.CTkFrame):
    """
    Layout (matches original HTML):

      [HEADER: world name | premise | game time | investigation pill | home | logout]
      ┌──────────────────────┬──────────────┬──────────────┐
      │ Narrative + Input    │ Quest Panel  │ Compendium   │
      │  (flex-1)            │  (w≈284)     │  (w≈284)     │
      └──────────────────────┴──────────────┴──────────────┘

    Investigation panel: drops in from top of the narrative column on demand.
    """

    PANEL_W = 284   # quest / compendium column width

    def __init__(self, parent, app, world_id: str) -> None:
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
        self.investigation_overlay.poll_investigations()

    # ── Layout ────────────────────────────────────────────────────────
    def _build(self) -> None:
        self._build_header()

        # thin amber trigger strip at very top of body (investigation)
        self._inv_strip = ctk.CTkFrame(self, fg_color="#431407", height=4,
                                       corner_radius=0, cursor="hand2")
        self._inv_strip.pack(fill="x")
        self._inv_strip.bind("<Enter>", lambda _: self.investigation_overlay._show_inv_panel())
        self._inv_strip.bind("<Button-1>", lambda _: self.investigation_overlay._show_inv_panel())

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # Center: narrative + input
        self._center_col = ctk.CTkFrame(body, fg_color="transparent")
        self._center_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Narrative pane panel
        narrative_panel = _panel(self._center_col, r=12)
        narrative_panel.pack(fill="both", expand=True)

        self.narrative_view = NarrativeView(narrative_panel, self)
        self._configure_tags()

        # Build investigation overlay dropping into self._center_col
        self.investigation_overlay = InvestigationOverlay(self._center_col, self)

        # Populating quick suggestions chip buttons
        for chip in ["Look around", "Wait and listen", "Examine…", "Speak to…", "Search…"]:
            ctk.CTkButton(self.narrative_view.controller.quick_row, text=chip, width=0, height=24,
                          fg_color=S800, hover_color=S700, border_width=1,
                          border_color=S700, font=("", 10), text_color=S400,
                          corner_radius=999,
                          command=lambda t=chip: self.narrative_view.quick_action(t)
                          ).pack(side="left", padx=(0, 4))

        # Quest panel column
        qf = _panel(body, w=self.PANEL_W, r=12)
        qf.pack(side="left", fill="y", padx=(0, 10))
        qf.pack_propagate(False)
        self.quest_panel = QuestPanel(qf, self)

        # Compendium column
        cf = _panel(body, w=self.PANEL_W, r=12)
        cf.pack(side="left", fill="y")
        cf.pack_propagate(False)
        self.compendium_panel = CompendiumPanel(cf, self)

    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color=S900, height=64, corner_radius=0)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        hl = ctk.CTkFrame(hdr, fg_color="transparent")
        hl.pack(side="left", padx=24, fill="y")
        self.world_lbl = ctk.CTkLabel(hl, text="Loading…",
                                      font=("Georgia", 20, "bold"), text_color=S100)
        self.world_lbl.pack(side="left", pady=20)
        self.premise_lbl = _label(hl, "", S600, 12)
        self.premise_lbl.pack(side="left", padx=(12, 0), pady=20)

        hr = ctk.CTkFrame(hdr, fg_color="transparent")
        hr.pack(side="right", padx=20, pady=14)

        # Game time status
        self.time_lbl = _label(hr, "", S600, 11)
        self.time_lbl.pack(side="left", padx=(0, 4))
        self.skip_btn = ctk.CTkButton(hr, text="↷", width=22, height=22,
                                      fg_color="transparent", hover_color=S800,
                                      text_color=S600, font=("", 14),
                                      command=self._show_skip_time)
        self.skip_btn.pack(side="left", padx=(0, 12))
        self.skip_btn.pack_forget()

        # Investigation points pill
        inv_pill = ctk.CTkFrame(hr, fg_color=A950, corner_radius=999,
                                border_width=1, border_color=A800)
        inv_pill.pack(side="left", padx=(0, 12))
        _label(inv_pill, "🔍", A400, 11).pack(side="left", padx=(10, 2), pady=6)
        self.inv_pill_lbl = _label(inv_pill, "5/5", A300, 12)
        self.inv_pill_lbl.pack(side="left", padx=(0, 10), pady=6)

        _btn(hr, "⚙", self._open_settings, w=32).pack(side="left", padx=(0, 8))
        _btn(hr, "Worlds", self._show_world_switcher, w=72).pack(side="left", padx=(0, 6))
        _btn(hr, "Home", self.app.show_dashboard, w=62).pack(side="left", padx=(0, 6))
        _btn(hr, "Logout", self.app.show_login, w=70,
             bg="#7f1d1d", hbg="#991b1b", fg="#fca5a5").pack(side="left")

    def _configure_tags(self) -> None:
        self.story.tag_configure("narration", foreground=S300, font=("Georgia", 13))
        self.story.tag_configure("player",    foreground="#93c5fd", font=("Georgia", 13, "bold"))
        self.story.tag_configure("muted",     foreground=S600, font=("", 12))
        self.story.tag_configure("error",     foreground=RED, font=("", 12))
        self.story.tag_configure("thinking",  foreground=A400, font=("", 12, "italic"))
        self.story.tag_configure("inv_link",  foreground=A300, font=("Georgia", 13), underline=True)
        self.story.tag_configure("inv_done",  foreground=S600, font=("Georgia", 13))

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
                    self.skip_btn.pack(side="left", padx=(0, 12))
        except Exception:
            pass

        try:
            handoff = self.app.service.get_world_handoff(self.world_id)
            scene   = handoff.get("handoff") or handoff.get("handoff_text", "")
            if scene:
                self.narrative_view.append_narration(scene + "\n\n")
            else:
                self.narrative_view.append("World loaded. What do you do?\n\n", "muted")
        except Exception:
            self.narrative_view.append("World loaded. What do you do?\n\n", "muted")

        self._refresh_entities()
        self._refresh_quests()
        self._refresh_inv_balance()
        self.input_box.focus()

    # ── Refresh & Delegates ───────────────────────────────────────────
    def _refresh_entities(self) -> None:
        try:
            self.entities = self.app.service.list_entities(
                world=self.world_id).get("entities", [])
        except Exception:
            self.entities = []
        self.compendium_panel.render_compendium()

    def _open_detail(self, eid: str) -> None:
        self.compendium_panel.open_detail(eid)

    def _refresh_quests(self) -> None:
        def _fetch():
            try:
                quests = self.app.service.list_quests(
                    world=self.world_id).get("quests", [])
            except Exception:
                quests = []
            self.after(0, lambda q=quests: self.quest_panel.render_quests(q))
        threading.Thread(target=_fetch, daemon=True).start()

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

    def _flash_hint(self, msg: str) -> None:
        self.narrative_view.flash_hint(msg)

    # ── Poll ──────────────────────────────────────────────────────────
    def _poll(self) -> None:
        try:
            while True:
                kind, data = self._q.get_nowait()
                self.narrative_view.remove_thinking()
                if kind == "ok":
                    self.narrative_view.append_narration(data + "\n\n")
                    self._refresh_entities()
                    self._refresh_quests()
                    self._refresh_inv_balance()
                    try:
                        t = self.app.service.get_world_time(world=self.world_id)
                        lbl = t.get("label","") or _format_seconds(t.get("seconds",0))
                        if lbl:
                            self.time_lbl.configure(text=lbl)
                            self.skip_btn.pack(side="left", padx=(0, 12))
                    except Exception: pass
                else:
                    self.narrative_view.append(f"[Error: {data}]\n\n", "error")
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
