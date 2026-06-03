import threading
import customtkinter as ctk
from .colors import S900, S800, S700, S600, S500, S400, S100, A800, A700, A300, A100
from .widgets import _label, _btn, _center


class InvestigationOverlay:
    def __init__(self, parent_frame, controller) -> None:
        self.parent = parent_frame
        self.controller = controller
        self._build()

    def _build(self) -> None:
        # Investigation queue panel (hidden/shown at top)
        self.controller._inv_panel = ctk.CTkFrame(self.controller._center_col, fg_color=S900,
                                                   border_width=1, border_color=S800, height=0)
        
        # Add a close button inside the overlay
        ctk.CTkButton(self.controller._inv_panel, text="×", width=28, height=28,
                      fg_color="transparent", hover_color=S800,
                      text_color=S600, font=("", 15, "bold"),
                      command=self._hide_inv_panel).pack(anchor="ne", padx=10, pady=8)
        
        _label(self.controller._inv_panel, "Investigation Queue", S100, 13,
               font=("", 12, "bold")).pack(anchor="nw", padx=18, pady=(0, 2))
        
        self.controller.inv_queue_frame = ctk.CTkFrame(self.controller._inv_panel, fg_color="transparent")
        self.controller.inv_queue_frame.pack(fill="both", expand=True, padx=18, pady=4)

    def _show_inv_panel(self) -> None:
        self.controller._inv_panel.place(in_=self.controller._center_col, relx=0, rely=0,
                                          relwidth=1, anchor="nw")
        self.controller._inv_panel.configure(height=160)
        self.controller._inv_panel.lift()

    def _hide_inv_panel(self) -> None:
        self.controller._inv_panel.place_forget()

    def render_inv_queue(self) -> None:
        for w in self.controller.inv_queue_frame.winfo_children():
            w.destroy()

        active = [j for j in self.controller.inv_jobs.values()
                  if j.get("status") in ("queued", "processing")]
        done   = [j for j in self.controller.inv_jobs.values()
                  if j.get("status") == "complete"]

        if not active and not done:
            _label(self.controller.inv_queue_frame, "No active investigations",
                   S600, 12).pack(padx=10, pady=6)
            return

        for job in active:
            c = ctk.CTkFrame(self.controller.inv_queue_frame, fg_color=S800,
                             corner_radius=8, width=160)
            c.pack(side="left", padx=(0, 8), pady=4)
            c.pack_propagate(False)
            ci = ctk.CTkFrame(c, fg_color="transparent")
            ci.pack(fill="both", padx=10, pady=8)
            _label(ci, job.get("entity_name", "?"), A300, 12).pack(anchor="w")
            _label(ci, "… investigating", S600, 10).pack(anchor="w")

        for job in done:
            c = ctk.CTkFrame(self.controller.inv_queue_frame, fg_color="#1c1208",
                             corner_radius=8, width=180,
                             border_width=1, border_color=A800)
            c.pack(side="left", padx=(0, 8), pady=4)
            c.pack_propagate(False)
            ci = ctk.CTkFrame(c, fg_color="transparent")
            ci.pack(fill="both", padx=10, pady=8)
            _label(ci, "✓  " + job.get("entity_name", "?"),
                   "#86efac", 12).pack(anchor="w")
            ctk.CTkButton(ci, text="View findings", height=24, font=("", 10),
                          fg_color=S800, hover_color=S700,
                          text_color=S400, border_width=0,
                          command=lambda j=job: self._view_inv_result(j)
                          ).pack(anchor="w", pady=(4, 0))

    def click_investigate(self, item: str, etype: str, cost: int) -> None:
        existing = next(
            (e for e in self.controller.entities
             if e.get("name", "").lower() == item.lower()), None)
        if existing:
            self.controller.compendium_panel.open_detail(existing["entity_id"])
            return
        self._show_investigate_confirm(item, etype, cost)

    def _show_investigate_confirm(self, item: str, etype: str, cost: int) -> None:
        dlg = ctk.CTkToplevel(self.controller)
        dlg.title("Investigate")
        dlg.configure(fg_color=S900)
        dlg.grab_set()
        _center(dlg, 420, 250)
        ctk.CTkLabel(dlg, text=f"Investigate: {item}",
                     font=("", 16, "bold"), text_color=S100
                     ).pack(pady=(28, 10), padx=24, anchor="w")
        _label(dlg,
               f"Spend {cost} investigation point{'s' if cost != 1 else ''} "
               f"to dig deeper.\nYou have {self.controller.inv_balance} available.",
               S400, 12, justify="left").pack(padx=24, anchor="w")
        _label(dlg, "The point is refunded when you review the findings.",
               S600, 11).pack(padx=24, anchor="w", pady=(4, 20))
        br = ctk.CTkFrame(dlg, fg_color="transparent")
        br.pack(padx=24, anchor="e")
        _btn(br, "Cancel", dlg.destroy, w=90).pack(side="left", padx=(0, 8))
        ok = "normal" if self.controller.inv_balance >= cost else "disabled"
        ctk.CTkButton(br, text="Investigate", width=120, height=36,
                      fg_color=A800, hover_color=A700, text_color=A100,
                      font=("", 13, "bold"), state=ok,
                      command=lambda: (
                          dlg.destroy(),
                          self._queue_investigation(item, etype, cost))
                      ).pack(side="left")

    def _queue_investigation(self, item: str, etype: str, cost: int) -> None:
        def _d():
            try:
                self.controller.app.service.spend_investigation_points(cost, world=self.controller.world_id)
                job = self.controller.app.service.create_investigation_job(
                    item, etype, world=self.controller.world_id)
                self.controller.inv_jobs[job["job_id"]] = {
                    "job_id": job["job_id"], "entity_name": item,
                    "entity_type": etype, "status": "queued", "result": None}
                self.controller.inv_balance = max(0, self.controller.inv_balance - cost)
            except Exception as e:
                self.controller.after(0, lambda m=str(e): self.controller._flash_hint(m))
                return
            self.controller.after(0, self.controller._update_inv_pill)
            self.controller.after(0, self.render_inv_queue)
        threading.Thread(target=_d, daemon=True).start()

    def poll_investigations(self) -> None:
        active = [jid for jid, j in self.controller.inv_jobs.items()
                  if j.get("status") in ("queued", "processing")]
        if active:
            def _f():
                changed = False
                for jid in active:
                    try:
                        r = self.controller.app.service.get_investigation_job(jid)
                        self.controller.inv_jobs[jid]["status"] = r["status"]
                        if r["status"] == "complete" and r.get("result"):
                            self.controller.inv_jobs[jid]["result"] = r["result"]
                            changed = True
                    except Exception: pass
                if changed:
                    self.controller.after(0, self._on_inv_complete)
            threading.Thread(target=_f, daemon=True).start()
        self.controller.after(2000, self.poll_investigations)

    def _on_inv_complete(self) -> None:
        self.render_inv_queue()
        self.controller._refresh_entities()
        self.controller._refresh_inv_balance()

    def _view_inv_result(self, job: dict) -> None:
        result = job.get("result") or {}
        entity = result.get("entity") if isinstance(result, dict) else None
        if entity and entity.get("entity_id"):
            # Mark investigation job as reviewed/deleted locally so it drops from queue
            self.controller.inv_jobs.pop(job["job_id"], None)
            self.render_inv_queue()
            self.controller.compendium_panel.open_detail(entity["entity_id"])
