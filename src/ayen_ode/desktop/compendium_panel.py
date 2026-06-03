import tkinter as tk
import customtkinter as ctk
import threading
from typing import Optional

from .colors import S950, S900, S800, S700, S600, S500, S400, S300, S200, S100, TYPE_COLORS, A700, A400, RED
from .widgets import _label, _panel, _btn, _center


class CompendiumPanel:
    def __init__(self, parent_frame, controller) -> None:
        self.parent = parent_frame
        self.controller = controller
        self._build()

    def _build(self) -> None:
        # Header
        chdr = ctk.CTkFrame(self.parent, fg_color="transparent", height=48)
        chdr.pack(fill="x")
        chdr.pack_propagate(False)
        ctk.CTkFrame(chdr, fg_color=A700, width=3, corner_radius=999,
                     height=18).pack(side="left", padx=(14, 8), pady=14)
        _label(chdr, "Compendium", S200, 13).pack(side="left", pady=14)
        ctk.CTkFrame(self.parent, fg_color=S800, height=1).pack(fill="x")

        # Search
        search_wrap = ctk.CTkFrame(self.parent, fg_color="transparent")
        search_wrap.pack(fill="x", padx=10, pady=(8, 0))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.render_compendium())
        ctk.CTkEntry(search_wrap, textvariable=self.search_var,
                     height=28, font=("", 11),
                     placeholder_text="Search…",
                     fg_color=S800, border_color=S700,
                     text_color=S100).pack(fill="x")

        # Entity list
        self.compendium = ctk.CTkScrollableFrame(self.parent, fg_color="transparent",
                                                  border_width=0)
        self.compendium.pack(fill="both", expand=True, padx=4, pady=4)

        # Detail pane (slides up at bottom)
        self.detail_pane = ctk.CTkFrame(self.parent, fg_color=S950, corner_radius=0,
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
                      command=self.close_detail).pack(side="right", padx=6)
        self.detail_type = _label(dhdr, "", S600, 10)
        self.detail_type.pack(side="left", pady=7)
        ctk.CTkFrame(self.detail_pane, fg_color=S800, height=1).pack(fill="x")
        self.detail_scroll = ctk.CTkScrollableFrame(
            self.detail_pane, fg_color="transparent", height=170, border_width=0)
        self.detail_scroll.pack(fill="x", padx=10, pady=4)

    def render_compendium(self) -> None:
        for w in self.compendium.winfo_children():
            w.destroy()

        q = self.search_var.get().lower().strip()
        groups: dict[str, list] = {}
        for e in self.controller.entities:
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
            open_ = self.controller._section_open.get(key, True)
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
                    w.bind("<Button-1>", lambda _, i=eid: self.open_detail(i))
                    w.bind("<Enter>",    lambda _, r=row: r.configure(fg_color=S800))
                    w.bind("<Leave>",    lambda _, r=row: r.configure(fg_color="transparent"))

            def _toggle(key=key, body=body, icon=icon):
                now = self.controller._section_open.get(key, True)
                self.controller._section_open[key] = not now
                if not now:
                    body.pack(fill="x")
                    icon.set("▾")
                else:
                    body.pack_forget()
                    icon.set("▸")

            for w in (sec_hdr, hr, icon_lbl):
                w.bind("<Button-1>", lambda _, t=_toggle: t())

    def open_detail(self, eid: str) -> None:
        if self.controller._detail_eid == eid:
            self.close_detail()
            return
        self.controller._detail_eid = eid
        e = next((x for x in self.controller.entities if x.get("entity_id") == eid), None)
        if not e:
            return
        self.detail_name.configure(text=e.get("name", ""))
        self.detail_type.configure(
            text=f"  {e.get('entity_type', '')}  ·  {e.get('status', '')}")
        self.detail_pane.configure(height=270)
        for w in self.detail_scroll.winfo_children():
            w.destroy()
        _label(self.detail_scroll, "Loading…", S600, 11).pack(pady=8)

        def _fetch():
            try:
                ed  = self.controller.app.service.get_entity(eid, world=self.controller.world_id)
                sd  = self.controller.app.service.get_entity_stats(eid, world=self.controller.world_id)
                ent = ed.get("entity", e)
                sts = sd.get("stats", {})
            except Exception:
                ent, sts = e, {}
            self.parent.after(0, lambda: self._render_detail(eid, ent, sts))

        threading.Thread(target=_fetch, daemon=True).start()

    def _render_detail(self, eid: str, e: dict, stats: dict) -> None:
        if self.controller._detail_eid != eid:
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

    def close_detail(self) -> None:
        self.controller._detail_eid = None
        self.detail_pane.configure(height=0)
