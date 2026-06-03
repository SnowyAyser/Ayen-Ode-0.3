from typing import Optional
import customtkinter as ctk

from .colors import S950
from .widgets import _center, _find_icon
from .login import LoginFrame
from .dashboard import DashboardFrame
from .create_world import CreateWorldFrame
from .narrative_layout import NarrativeFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class AyenOdeApp:
    def __init__(self) -> None:
        from ..config import load_settings
        from ..services import AyenOdeService
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
            try:
                self.root.iconbitmap(str(icon))
            except Exception:
                pass

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

    def show_login(self) -> None:
        from ..config import load_settings
        self.settings = load_settings()
        self._swap(LoginFrame)
    def show_dashboard(self)                -> None: self._swap(DashboardFrame)
    def show_create_world(self)             -> None: self._swap(CreateWorldFrame)
    def show_narrative(self, world_id: str) -> None:
        self.current_world_id = world_id
        self._swap(NarrativeFrame, world_id=world_id)

    def run(self) -> None:
        self.root.mainloop()
