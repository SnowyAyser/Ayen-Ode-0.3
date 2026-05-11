"""Native desktop settings window for editing the project .env file.

Run with:  python -m ayen_ode.settings_window

A small tkinter app — no extra dependencies. Reads .env at the project root,
lets the user edit ANTHROPIC_API_KEY (and a few related fields), writes the
file back on Save. Launched either by setup.ps1 on first run or by the web
UI's settings button via /api/settings/launch.
"""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from . import paths

# In frozen mode these resolve under %APPDATA%/Ayen-Ode/. In source mode they
# resolve to the repo root, matching the original behaviour.
paths.ensure_user_dir()
ENV_PATH = paths.env_path()
ENV_EXAMPLE_PATH = paths.env_example_path()

EDITABLE_KEYS = [
    ("ANTHROPIC_API_KEY", "Anthropic API key", "Required. Starts with sk-ant-…", True),
    ("APP_USERNAME", "Login username", "Optional. Leave blank for no login.", False),
    ("APP_PASSWORD", "Login password", "Optional. Leave blank for no login.", True),
    ("ALLOWED_IPS", "Allowed client IPs", "Comma-separated. Leave blank for any.", False),
    ("AYEN_ODE_PORT", "Server port", "Default 8000.", False),
]

BG = "#0f172a"
PANEL = "#1e293b"
PANEL_BORDER = "#334155"
TEXT = "#e2e8f0"
MUTED = "#64748b"
ACCENT = "#b45309"
ACCENT_HOVER = "#d97706"
ENTRY_BG = "#0b1221"


def parse_env(text: str) -> dict[str, str]:
    """Parse a .env file body into a {KEY: value} dict, skipping comments and blanks."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def write_env(values: dict[str, str]) -> None:
    """Write values to .env, preserving comments and untouched keys."""
    if ENV_PATH.exists():
        original_lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    elif ENV_EXAMPLE_PATH.exists():
        original_lines = ENV_EXAMPLE_PATH.read_text(encoding="utf-8").splitlines()
    else:
        original_lines = []

    seen: set[str] = set()
    out_lines: list[str] = []
    for line in original_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                out_lines.append(f"{key}={values[key]}")
                seen.add(key)
                continue
        out_lines.append(line)

    for k, v in values.items():
        if k not in seen:
            out_lines.append(f"{k}={v}")

    ENV_PATH.write_text("\n".join(out_lines).rstrip() + "\n", encoding="utf-8")


def load_current_values() -> dict[str, str]:
    """Return the current editable key values from .env (or .env.example as fallback)."""
    if ENV_PATH.exists():
        text = ENV_PATH.read_text(encoding="utf-8")
    elif ENV_EXAMPLE_PATH.exists():
        text = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    else:
        text = ""
    parsed = parse_env(text)
    cleaned: dict[str, str] = {}
    for key, *_ in EDITABLE_KEYS:
        v = parsed.get(key, "")
        if v == "sk-ant-...":
            v = ""
        cleaned[key] = v
    return cleaned


class SettingsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Ayen-Ode · Settings")
        root.configure(bg=BG)
        root.geometry("520x540")
        root.minsize(480, 480)

        try:
            root.tk.call("tk", "scaling", 1.2)
        except tk.TclError:
            pass

        self.values = load_current_values()
        self.entries: dict[str, tk.Entry] = {}
        self.show_secret: dict[str, tk.BooleanVar] = {}

        self._build_layout()
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.bind("<Return>", lambda _e: self._save())
        root.bind("<Escape>", lambda _e: self._on_close())

    def _build_layout(self) -> None:
        """Construct the full tkinter widget tree."""
        outer = tk.Frame(self.root, bg=BG, padx=24, pady=22)
        outer.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            outer,
            text="Ayen-Ode",
            font=("Segoe UI", 18, "bold"),
            bg=BG,
            fg=TEXT,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            outer,
            text="Local settings · these write to your .env file",
            font=("Segoe UI", 9),
            bg=BG,
            fg=MUTED,
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        panel = tk.Frame(
            outer,
            bg=PANEL,
            highlightbackground=PANEL_BORDER,
            highlightthickness=1,
        )
        panel.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(panel, bg=PANEL, padx=20, pady=18)
        inner.pack(fill=tk.BOTH, expand=True)

        for key, label, hint, is_secret in EDITABLE_KEYS:
            self._build_field(inner, key, label, hint, is_secret)

        button_row = tk.Frame(outer, bg=BG)
        button_row.pack(fill=tk.X, pady=(16, 0))

        cancel = tk.Button(
            button_row,
            text="Cancel",
            command=self._on_close,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL_BORDER,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        cancel.pack(side=tk.RIGHT, padx=(8, 0))

        save = tk.Button(
            button_row,
            text="Save",
            command=self._save,
            bg=ACCENT,
            fg="#fef3c7",
            activebackground=ACCENT_HOVER,
            activeforeground="#fef3c7",
            relief="flat",
            borderwidth=0,
            padx=22,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        )
        save.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            button_row,
            text="",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side=tk.LEFT)

    def _build_field(self, parent: tk.Frame, key: str, label: str, hint: str, is_secret: bool) -> None:
        """Add a single labeled entry row (with optional show/hide toggle for secrets)."""
        wrap = tk.Frame(parent, bg=PANEL, pady=6)
        wrap.pack(fill=tk.X)

        label_row = tk.Frame(wrap, bg=PANEL)
        label_row.pack(fill=tk.X)
        tk.Label(
            label_row,
            text=label.upper(),
            font=("Segoe UI", 8, "bold"),
            bg=PANEL,
            fg="#94a3b8",
        ).pack(side=tk.LEFT)

        entry = tk.Entry(
            wrap,
            bg=ENTRY_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=PANEL_BORDER,
            highlightcolor=ACCENT,
            font=("Segoe UI", 10),
        )
        entry.insert(0, self.values.get(key, ""))
        if is_secret:
            entry.config(show="•")
        entry.pack(fill=tk.X, ipady=6, pady=(4, 2))
        self.entries[key] = entry

        bottom_row = tk.Frame(wrap, bg=PANEL)
        bottom_row.pack(fill=tk.X)
        tk.Label(
            bottom_row,
            text=hint,
            font=("Segoe UI", 8),
            bg=PANEL,
            fg=MUTED,
        ).pack(side=tk.LEFT)

        if is_secret:
            var = tk.BooleanVar(value=False)
            self.show_secret[key] = var

            def toggle(e=entry, v=var):
                e.config(show="" if v.get() else "•")

            cb = tk.Checkbutton(
                bottom_row,
                text="show",
                variable=var,
                command=toggle,
                bg=PANEL,
                fg=MUTED,
                activebackground=PANEL,
                activeforeground=TEXT,
                selectcolor=PANEL,
                font=("Segoe UI", 8),
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
            )
            cb.pack(side=tk.RIGHT)

    def _save(self) -> None:
        """Validate entries and write them to .env. Destroys the window on success."""
        new_values = {key: self.entries[key].get().strip() for key, *_ in EDITABLE_KEYS}

        api_key = new_values.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            messagebox.showwarning(
                "API key required",
                "ANTHROPIC_API_KEY is empty. The server will start but narrative actions will fail until a key is set.",
                parent=self.root,
            )
        elif not api_key.startswith("sk-ant-"):
            if not messagebox.askyesno(
                "Unusual API key",
                "Anthropic API keys usually start with 'sk-ant-'. Save anyway?",
                parent=self.root,
            ):
                return

        try:
            write_env(new_values)
        except OSError as e:
            messagebox.showerror