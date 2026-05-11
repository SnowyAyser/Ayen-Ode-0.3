# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Ayen-Ode (Windows desktop EXE).

Build:
    pyinstaller --noconfirm ayen-ode.spec

Output (onedir, no UPX):
    dist/Ayen-Ode/
        Ayen-Ode.exe
        static/
        .env.example
        ...runtime DLLs/PYDs and the _internal/ folder

We deliberately use onedir (not onefile) for three reasons:
  1. Startup is <500 ms instead of 1-3 s (onefile extracts to %TEMP% every launch).
  2. Antivirus engines flag onefile self-extractors at much higher rates.
  3. StaticFiles path resolution is simpler when files live next to the EXE.
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

# ---------------------------------------------------------------------------
# Hidden imports
# ---------------------------------------------------------------------------
# uvicorn uses dynamic dispatch (`uvicorn.loops.auto`, `protocols.http.auto`,
# `protocols.websockets.auto`) which PyInstaller's static analyzer cannot follow.
# Collecting all submodules is the safe blanket-fix.

hiddenimports = []
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("ayen_ode")
hiddenimports += collect_submodules("anthropic")
hiddenimports += collect_submodules("httpx")
hiddenimports += collect_submodules("httpcore")
hiddenimports += collect_submodules("pydantic")
hiddenimports += collect_submodules("pydantic_core")
hiddenimports += collect_submodules("starlette")

hiddenimports += [
    # uvicorn (belt-and-braces, in case collect_submodules misses any)
    "uvicorn.logging",
    "uvicorn.loops", "uvicorn.loops.auto", "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl", "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.protocols.websockets.wsproto_impl",
    "uvicorn.lifespan", "uvicorn.lifespan.on", "uvicorn.lifespan.off",
    # ASGI / HTTP plumbing
    "httptools", "websockets", "wsproto", "h11", "anyio", "sniffio",
    "anyio._backends._asyncio",
    # Starlette
    "starlette.routing", "starlette.staticfiles", "starlette.middleware",
    "starlette.middleware.base", "starlette.middleware.cors",
    "starlette.responses", "starlette.requests", "starlette.applications",
    # Anthropic SDK ecosystem
    "distro", "jiter", "certifi",
    # libsql (Turso) — top-level import is conditional in services/base.py
    "libsql_experimental",
    # python-dotenv
    "dotenv",
    # pywebview (Windows: Edge WebView2 backend, hosted in WinForms via pythonnet)
    "webview", "webview.platforms.edgechromium", "webview.platforms.winforms",
    "clr", "clr_loader", "pythonnet",
    # tkinter (settings window) — usually picked up automatically, but force it
    "tkinter", "tkinter.ttk", "tkinter.messagebox",
]

# ---------------------------------------------------------------------------
# Data files (read-only, bundled next to the EXE)
# ---------------------------------------------------------------------------

datas = [
    ("static", "static"),
    (".env.example", "."),
]
datas += collect_data_files("certifi")          # CA bundle for httpx -> Anthropic
datas += collect_data_files("anthropic")        # any packaged data (defensive)

# ---------------------------------------------------------------------------
# Native binaries
# ---------------------------------------------------------------------------
# libsql_experimental ships a Rust .pyd. PyInstaller usually picks it up via
# normal import-graph analysis, but the import is conditional in our code, so
# we force-collect its dynamic libraries.

binaries = []
try:
    binaries += collect_dynamic_libs("libsql_experimental")
except Exception:
    pass  # libsql_experimental may not be installed in dev environments

# ---------------------------------------------------------------------------
# Excludes — drop modules we don't use to shrink the bundle and avoid
# pywebview's hook pulling in every GUI toolkit on the machine.
# ---------------------------------------------------------------------------

excludes = [
    "watchfiles",            # uvicorn reload-only; reload is disabled in frozen mode
    "uvloop",                # no Windows wheel; harmless on POSIX but unused
    "tokenizers",            # only used by anthropic.count_tokens(); ~10 MB
    # pywebview backends we don't use on Windows:
    "PyQt5", "PyQt6", "PySide2", "PySide6",
    "gi", "cefpython3",
    "webview.platforms.cef", "webview.platforms.qt", "webview.platforms.gtk",
    "webview.platforms.cocoa", "webview.platforms.mshtml",
    # Test/dev tooling — never need at runtime
    "pytest", "_pytest",
    # Notebook stuff occasionally pulled by transitive deps
    "IPython", "ipykernel", "jupyter",
]


# ---------------------------------------------------------------------------
# Analysis / PYZ / EXE / COLLECT
# ---------------------------------------------------------------------------

a = Analysis(
    ["desktop_launcher.py"],
    pathex=["src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Ayen-Ode",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX is the #1 cause of Defender false positives.
    console=False,             # GUI app — no console window. Logs go to %APPDATA%/Ayen-Ode/app.log.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,                 # add path to .ico here once we have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Ayen-Ode",
)
