# Ayen-Ode — Flutter client

Cross-platform Flutter client for Ayen-Ode, targeting **Windows desktop** and
**Android**. Replaces the static HTML/JS frontend in `../static/` over time;
the backend (`../src/ayen_ode/`) is unchanged and remains the single source
of truth.

Lives inside the backend repo as a subfolder rather than a sibling repo so
backend + client stay version-locked.

## Status (2026-05-11)

Phases 0–5 are merged on the `flutter-app` branch. Phase 6 (Windows + Android
release builds) is blocked on local-toolchain installs that need UAC — see
[§Resume](#resume) below.

| Phase | What | Commit |
|---|---|---|
| 0 | Flutter SDK 3.41.9 installed at `C:\Users\snowy\flutter` | — |
| 1 | `design-audit.md` — exhaustive screen / token / API audit | 1631b83 |
| 2 | `flutter create` scaffold + pubspec deps | 1631b83 |
| 3 | Design tokens (`lib/theme/`) | ae21bca |
| 4 | Dio API client + Freezed models for every endpoint | 5741966 |
| 5 | All 5 screens (login, dashboard, wizard, narrative, settings) | a8bcdc2 |
| 6 | Windows `.exe` + Android `.apk` builds | **blocked** |

## What works in the Flutter client today

- Auth: sign in / register / sign out with token stored in
  `flutter_secure_storage`. 401 anywhere clears the token and redirects to
  login.
- Dashboard: list all worlds (active pill, Enter/Switch/Reset/Delete),
  create-world CTA, API-key-missing banner, in-app settings modal.
- World creation wizard: 4 steps with slide transitions, chip selection,
  validation shake, ambient atmosphere, Forging overlay.
- Narrative loop: load a world, render conversation history + opening
  handoff, submit actions with quick-action chips, see the IP pill update,
  see in-game time updates, browse the quest panel + compendium.

## Deferred — search the code for `TODO(audit-§…)` markers

The audit (`design-audit.md`) is the source of truth. These behaviours are
documented there and intentionally not implemented in v0.1:

- Investigation panel: top-edge hover/tap trigger exists, but the
  poll-the-job-every-500ms + 60s timer + auto-close-after-last-finished
  behaviour is not wired (`narrative_screen.dart` near the trigger zone).
- Opening-scene typewriter intro on `?fresh=1` entry.
- `<investigate item='name' cost='1'>display</investigate>` inline-tag
  parsing in narrative text (a key feature — without it, investigation links
  aren't clickable).
- Entity-ref linkification (clicking an entity name in narrative text opens
  its compendium detail).
- Worlds switcher modal from the narrative header (dashboard does it for
  now).
- Mobile (≤768px) bottom-sheet drawers for the Quest + Compendium rails.
  Currently mobile collapses to single column with rails hidden.
- Cinematic dashboard entrance + world-enter blackout transition.
- Phone-access (Cloudflare Tunnel) setup screen.

None of these block the core gameplay loop.

## Resume

### What you need to enable / install (UAC required for items marked 🔒)

1. **Windows Developer Mode** — Settings → Privacy & Security → For
   Developers → toggle on. Lets `flutter pub get` create the plugin
   symlinks. No UAC, just a toggle.
2. 🔒 **Visual Studio 2022 Build Tools** with the *Desktop development with
   C++* workload — needed for `flutter build windows`. Install:
   ```
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --quiet --wait"
   ```
3. 🔒 **Android Studio + Android SDK + Java 17** — needed for `flutter build apk`. Easiest:
   ```
   winget install Google.AndroidStudio
   ```
   On first launch it installs the SDK + cmdline tools. Then accept licences with `flutter doctor --android-licenses`.

### Finishing Phase 6

Once the toolchain is in place:

```powershell
# Sanity
flutter doctor -v

# Builds
cd C:\dev\Ayen-Ode\flutter_app
flutter build windows --release
flutter build apk --release

# Verify
.\build\windows\x64\runner\Release\ayen_ode.exe
# (Android) — adb install build\app\outputs\flutter-apk\app-release.apk
```

The Windows build produces a standalone .exe under
`build\windows\x64\runner\Release\`. The Android build produces an APK
under `build\app\outputs\flutter-apk\`.

### Picking up the Phase 5 polish work

`design-audit.md` §8 enumerates every deferred behaviour. The simplest order
to land them in:

1. `<investigate>` tag parsing (`lib/screens/narrative_screen.dart` —
   replace `_NarrativeBlock`'s plain `Text` with a `RichText` that walks the
   audit's regex).
2. Investigation polling + panel drop animation
   (`lib/state/investigation_provider.dart` — new file).
3. Entity-ref linkification + compendium detail pane.
4. Typewriter opening-scene intro.
5. Mobile bottom-sheet drawers.

## Layout

```
flutter_app/
├── assets/
│   └── config.json          # api_base_url; override with --dart-define=API_BASE_URL=…
├── lib/
│   ├── api/
│   │   ├── api_client.dart  # Dio instance + AuthInterceptor + JsonRpcUnwrap
│   │   ├── api_exception.dart
│   │   ├── clients.dart     # AuthApi/WorldApi/NarrativeApi/InvestigationApi/EntityApi/SettingsApi
│   │   ├── token_storage.dart
│   │   └── models/          # Freezed + json_serializable, snake_case fieldRename
│   ├── config/config.dart   # AppConfig.load() reads assets/config.json
│   ├── routing/router.dart  # GoRouter with auth-gated redirects
│   ├── screens/             # login / dashboard / create_world / narrative / settings
│   ├── state/               # Riverpod providers (auth, worlds, …)
│   ├── theme/               # colors / typography / spacing / theme.dart
│   ├── widgets/             # app_button, app_input, clover_loader
│   ├── app.dart             # MaterialApp.router
│   └── main.dart
├── android/                 # standard flutter create stubs
├── windows/                 # standard flutter create stubs
├── pubspec.yaml             # deps: go_router, riverpod, dio, freezed, …
├── build.yaml               # json_serializable.field_rename: snake
└── design-audit.md          # ★ source of truth for the port
```

## Running against a local backend

Backend lives at `..\` and serves on `http://localhost:8000` by default. The
client's `assets/config.json` already points there. To target the production
host instead:

```powershell
flutter run -d windows --dart-define=API_BASE_URL=https://app.ayen-ode.com
```

## Why this lives inside the backend repo

The static HTML frontend in `../static/` stays alive until the Flutter
Windows build reaches feature parity. After parity, `../static/` can be
deleted in a follow-up commit. Keeping the Flutter app in `flutter_app/`
means:

- One git history, one CI surface.
- Cross-installation of Turso-backed auth works for free — same backend,
  same DB.
- The backend's `desktop.py` / `desktop_launcher.py` and `Ayen-Ode.exe`
  build pipeline (`scripts/`) remain untouched.
