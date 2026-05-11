# Ayen-Ode Flutter — Design Audit

Source: `C:\dev\Ayen-Ode\.claude\worktrees\great-poincare-3d4bc0\static\` (canonical worktree;
slight drift from `main`'s `static/`). Read date: 2026-05-11.

The web frontend is a small set of static HTML/CSS/JS pages served by the Starlette backend.
Styling is **Tailwind via CDN** (`https://cdn.tailwindcss.com`) with a handful of per-page
`<style>` blocks for animation. There are **no custom font-face declarations** — the UI runs
on the platform's `ui-sans-serif, system-ui, sans-serif` stack. The visual identity is
"dark slate canvas with amber-firelight accents and emerald success notes."

---

## 1. Screens

### 1.1 `index.html` — Login

- **Route:** `/` (also `/index.html`). Redirects to `/dashboard.html` immediately if `localStorage.apiKey` is set.
- **Layout:** centered card on a slate-gradient page. Single column, max-w-md.
- **Sections, top to bottom:**
  - Title "Ayen-Ode" (text-3xl, bold, slate-100).
  - Subtitle ("Sign in to continue" / "Create an account").
  - Tab strip (two pills, "Sign in" / "Create account") inside a slate-900 pill bar.
  - Username text input.
  - Password input (with `autocomplete=current-password|new-password` switched by mode).
  - Submit button (full-width, blue-600 bg) — label "Login" / "Create account".
  - Error banner (red-900 bg) shown on failure.
- **Loader:** a fixed full-screen `#loaderOverlay` with `<canvas id="cloverCanvas">` running a 2π rose-curve trail (a self-contained variant of `clover-loader.js` — see §4.4). Shown during submit; minimum 1200ms wait so the animation reads. RGB color in the loader is hardcoded `(68, 214, 104)` (green-400-ish), distinct from the `clover-loader.js` HSL variant.
- **Interactions:**
  - Sign in / Create toggle: rewrites button text + subtitle + password autocomplete; hides error.
  - Submit: `POST /api/login` or `/api/register` with `{username, password}`. On 2xx, stash `data.token` in `localStorage.apiKey`, set `localStorage.username`, set `sessionStorage.justLoggedIn = "1"`, redirect to `/dashboard.html`. On failure, surface server `error` field if present.
- **State:** `mode: "signin"|"register"` (local), nothing else.

### 1.2 `dashboard.html` — World Dashboard

- **Route:** `/dashboard.html`. Auth-gated (`checkAuth()` from `app.js`).
- **Layout:** header bar + main content (max-w-5xl), single column.
- **Header (slate-900 bar):**
  - Brand block: "Ayen-Ode" (text-xl, bold) + "World Dashboard" subtitle (text-xs, slate-600).
  - Right-aligned button row: `restartBtn` (refresh icon), `installBtn` (PWA install — Android only, hidden until `beforeinstallprompt` fires), Phone-access link (anchor to `/settings.html`), `settingsBtn` (cog icon, opens modal), Logout (red-950 bg).
- **Main:**
  - API-key banner (amber-950) — shown when `GET /api/settings/status` returns `api_key_configured: false`. Has "Open Settings" CTA.
  - **All Worlds** section: grid of world cards (`grid-cols-1 sm:2 lg:3`, gap-4). Each card shows name (with optional `active` emerald pill), truncated 80-char premise, and an action row: `Enter →` button (amber-800, only on active worlds) **or** `Switch` button (slate-800, on inactive worlds), then `Reset` (amber-950) and `Delete` (red-950) buttons.
  - **Create New World** CTA: a large clickable card linking to `/create-world.html`, with circle icon, title, supporting copy, and a chevron.
- **Modals:** Reset confirm, Delete confirm, Settings modal (see §3.4).
- **Cinematic entrance** (only when `sessionStorage.justLoggedIn === "1"`): full-screen radial-gradient overlay with a large amber clover (180px, hue 38), an "Ayen-Ode" caption that fades in at 250ms, sections stagger-fade in at 1400ms, overlay removed at 2100ms. A "Welcome back, {username}" toast (3.2s, animated `welcomeIn` keyframe) flashes in the top-center after the overlay fades.
- **World-enter transition** (on Enter click): a separate overlay paints a radial-gradient slate background, a 220px amber clover, then a title that slides up to center. After 2s, the clover fades out, title slides to dead-center, a solid black layer fades in over everything (1100ms), then navigation fires (1450ms). The destination (`narrative.html`) listens for the same blackout via its own `#navBlackout` so the transition is seamless (no flicker between pages). Pressing Esc cancels.
- **Interactions:**
  - `restartServer()` — `POST /api/server/restart`, then polls `GET /health` every 500ms for up to 12s before reloading.
  - `enterWorld(id)` — runs the world-enter transition, sets `sessionStorage.worldEntering = "1"`, navigates to `/narrative.html?world_id=ID&fresh=1`.
  - `switchWorld(id)` — `POST /api/worlds/switch` then reloads data.
  - `openResetModal` / `confirmReset` — `POST /api/worlds/{id}/reset`.
  - `openDeleteModal` / `confirmDelete` — `DELETE /api/worlds/{id}`.
  - Settings modal: see §3.4.

### 1.3 `create-world.html` — World Creation Wizard

- **Route:** `/create-world.html`. Auth-gated.
- **Layout:** ambient starfield background + dark gradient. 4-step wizard, max-w-lg, single column.
- **Header:** "← Dashboard" link, brand clover + "Ayen-Ode" caption, fixed-width spacer for symmetry.
- **Step dots:** 4 horizontal pills above the panels. The active pill is wide (32px) and amber-glowing; done pills are medium (18px, dim amber); pending pills are 6px slate.
- **Steps:**
  1. **Name** — single text input, "The Shattered Empire, Veilfall, The City of Clocks…" placeholder.
  2. **Tone** — chip grid (8 quick-start chips: Dark fantasy, Political intrigue, Cosmic horror, Solarpunk, Noir mystery, Mythic epic, Fae & folklore, Biopunk) + free-text input. Optional.
  3. **Premise** — textarea (h-36), character counter.
  4. **Role + Review** — chip grid (6 chips: Disgraced knight, Wandering scholar, Exiled heir, Street thief, Court spy, Temple acolyte) + free-text input + a Review card summarizing Name/Tone/Premise.
- **Transition between steps:** the outgoing panel slides 52px in the direction of travel and fades to opacity 0 (380ms cubic-bezier 0.4,0,0.2,1); the incoming panel starts at the opposite 52px and slides to 0. Direction-aware.
- **Validation:** Step 0 requires name; Step 2 requires premise. Empty input gets a shake animation (380ms) and red border flash.
- **Chips:** clicking a chip selects it (amber border + amber-200 text + amber-950/28% bg) and copies its label into the input. Typing into the input manually deselects mismatched chips.
- **Navigation row:** "Back" arrow button (slate-500 ghost, hidden on step 0), spacer, "Continue →" button (amber-800). On the final step, "Continue" is replaced by "✦ Forge This World" (amber-700, with `forgeGlow` 2.6s pulsing box-shadow animation).
- **Forge action:** disables button, shows loading overlay (96% opacity slate-950, with 84px amber clover, "Forging Your World" header, "Initialising with Claude…" status text). `POST /api/worlds/create` with `{name, premise, theme_tone, player_role}`. On success: 700ms delay → navigate to `/narrative.html?world_id={id}`.
- **Background atmosphere:** 130 randomly-placed white stars with random twinkle durations (2–6s) and per-star opacities; ambient radial-gradient glows (amber/blue/purple) layered over slate-950.

### 1.4 `narrative.html` — In-Game Narrative

The largest and most complex page; modular logic split across 5 JS files.

- **Route:** `/narrative.html?world_id={id}[&fresh=1][&replay_intro=1]`. Auth-gated.
- **Top-of-page blackout:** `html.entering` class is added before any other resource paints (inline script in `<head>`) when `?fresh=1`, `?replay_intro=1`, or sessionStorage indicates fresh entry. CSS forces body bg to `#000` and runs `navBlackoutFade` (800ms ease-out, starts at 100ms delay) on a top-layer `#navBlackout` div — covering the seam from the dashboard's transition.
- **Layout (desktop):** flex column, h-screen, overflow-hidden.
  - **Top-edge investigation trigger:** a fixed band `top-0, left-1/2 -translate-x-1/2, w-[35%], h-1.5` with a subtle amber tint. `onmouseenter="openInvestigationPanel()"` opens the panel. On mobile (≤768px) this band becomes the full width.
  - **Header (slate-900 bar):** brand block (world name h1, premise p), right cluster of: investigation-points pill ("5/5"), Home button → `/dashboard.html`, Logout, settings cog with popover anchored to the cog.
  - **Main (max-w-7xl, flex gap-4 p-4):** three columns.
    - **Narrative pane** (`flex-1`): scrollable `#narrativeContent` (p-6, space-y-5) above a non-scrolling input bar.
    - **Quest Panel** (w-72, aside): clickable header ("Current Goals" with purple accent stripe, chevron toggle), scrollable body. Three tier sections — "Overarching" (Tier 1), "Active" (Tier 2), "Threads — your call" (Tier 3 pending, amber-tinted). Each Tier 1/2 card shows title + description + progress bar (`#7c65f7` fill on slate track) + "X of Y milestones". Tier 3 cards have Track/Ignore buttons.
    - **Compendium Panel** (w-72, aside): header ("Compendium" with amber stripe), search input, scrollable entity list grouped by type (Characters/Locations/Factions/Objects/Events, each a collapsible section with a colored dot) and optional sub-groupings (factions, family tags, weapon/artifact tags, etc.). Selecting a card slides up a 270px detail pane at the bottom with summary, stats (with bar visualizations colored by value), timeline notes, open questions, tags.
  - **Layout (mobile, ≤768px):**
    - The two side rails (Quest + Compendium) collapse into fixed bottom-sheet drawers (slide up from `translateY(110%)`), toggled by a fixed-bottom-right `#mobileRailBar` pill cluster ("Goals", "Compendium").
    - Narrative pane and input bar fill the viewport.
    - Investigation trigger zone becomes full-width and 2rem tall with a slightly stronger amber tint (so it's tappable).
- **Input bar (bottom of narrative pane):**
  - Quick-action chip row: "Look around", "Wait", "Examine…", "Speak…", "Search…" (rounded-full pills, slate-800/60 bg).
  - Textarea (`#actionInput`, auto-resizing 44–164px) + a stacked-button column on the right: time label ("Late afternoon, Day 3") with `↷` skip-time button above an "Act" submit button (amber-800).
  - Skip-time popover (anchored above the Act button column): "1 hour", "4 hours", "Rest (8h)", "1 day", "Cancel".
  - Hint row: "Enter to send · Shift+Enter for new line" + optional char count.
- **Investigation panel** (drops from top, `transform: translateY(-110%)` → `0` on `.panel-open`):
  - Header row (icon + "Investigations" title + optional "Clear completed" button + close X).
  - Horizontal scrolling queue of investigation cards. Two card states:
    - **Queued/processing** (min-180px): small clover + name + "Investigating…" caption.
    - **Complete** (min-220px, amber-950/20 bg): checkmark icon + name + 90-char summary + "View Details →" button (amber-700) which calls `addToCompendium()`.
  - Closes on mouseleave (350ms grace via `panelCloseTimeout`) or auto-closes 1200ms after the LAST active job finishes (`anyJustCompleted && !stillRunning`).
- **Investigation timer bar:** fixed bottom-center pill (slate-900 with amber border), shows clover-style 2px progress bar over a 60s window, "~32s" remaining text. Visible whenever a job hasn't yet refunded its point.
- **Settings popover (cog):** small popover anchored under the cog. Single setting: a "Confirm before sending" toggle. Stored in `localStorage.ayen_ode_settings`.
- **Worlds modal** (`#worldsModal`): list of all worlds with switch buttons; opened from elsewhere in the app (not the narrative header directly).
- **Investigation confirmation dialog:** "Investigate: {name}" + cost line + cancel/Investigate buttons.
- **Investigation status dialog:** shown when clicking an in-progress (emerald-colored) `<investigate>` link in narrative text — "Under Investigation" message, "Got it" close.
- **Investigation retry toast:** brief slate-800 pill flashed at bottom-center when an investigation fails and auto-retries.
- **Opening-scene intro animation:** When `?fresh=1` and there's a `handoff` text from the server, the narrative pane animates the first paragraph with a typewriter cursor (12–35ms per char, scaling with line length), and subsequent paragraphs stagger-fade in at 380ms intervals. A `Skip ›` button (top-right) bails to the static rendering. A "Replay" badge (amber pill, top-center, 4s) shows when `?replay_intro=1`.
- **Entity ref linkification:** `narrative-entity.js` post-processes assistant text to wrap any occurrence of an existing entity's name with a button that opens the compendium detail pane. Investigation links are emitted by the AI directly as `<investigate item='name' cost='1'>display</investigate>` tags and parsed by `narrative-investigation.js`.

### 1.5 `settings.html` — Phone Access Setup

- **Route:** `/settings.html`. Auth-gated. Distinct from the in-dashboard Settings modal — this one is dedicated to Cloudflare-Tunnel phone-access setup.
- **Header:** "Phone access" h1 + ghost-style "Back" link to `/dashboard.html`.
- **Sections:**
  - **Loopback warning** banner (shown when the API rejects the request — typically when accessed from outside the local machine).
  - **Master switch:** large toggle ("Enable phone access") + supporting copy. Confirmation banner appears below when toggled on.
  - **Setup steps** (3 numbered cards, marked done with emerald border when complete):
    1. "Log in to Cloudflare" — opens browser to `/api/tunnel/login` URL, polls `/api/tunnel/login/status`.
    2. "Create tunnel & route DNS" — `POST /api/tunnel/setup`.
    3. "Run the tunnel" — Start (`POST /api/tunnel/start`) / Stop (`POST /api/tunnel/stop`) toggle.
  - **Status panel:** 6 read-only rows (Binary, Logged in, Tunnel ID, Hostname, Running, Last error) with status pills (good/bad/warn).
  - **Install card:** shown when tunnel is running — large QR (`/api/qrcode?text={url}&size=8`) on white bg + URL + install instructions ("Open menu → Install app").
  - **Advanced details:** Tunnel hostname + CORS allowed origins inputs + Save.
- **Toast:** generic bottom-center toast for success/error.

### 1.6 Other static pages (not part of the Flutter port scope)

- `clover-loader.html` — standalone demo page for the loader animation.
- `debug.html` + `debug.js` + `debug-panels.js` — dev-only debug inspector. Out of scope for v0.1 of the Flutter port.

---

## 2. Design Tokens

### 2.1 Color palette

All colors are Tailwind defaults unless noted. The few project-specific values are flagged.

| Role | Token | Hex |
|---|---|---|
| **Page background (PWA theme-color)** | `--bg-theme` | `#0b0b10` |
| Page background (body in dashboard/narrative) | slate-950 | `#020617` |
| Surface (header, cards, modals) | slate-900 | `#0f172a` |
| Surface elevated | slate-800 | `#1e293b` |
| Surface input | slate-800/80 mix | `#1e293bcc` |
| Border subtle | slate-800/60 | `#1e293b99` |
| Border emphasis | slate-700 | `#334155` |
| Border focus (input) | amber-600 | `#d97706` |
| Text primary | slate-100 | `#f1f5f9` |
| Text body | slate-200 / slate-300 | `#e2e8f0` / `#cbd5e1` |
| Text secondary | slate-400 | `#94a3b8` |
| Text muted | slate-500 / slate-600 | `#64748b` / `#475569` |
| Text very muted | slate-700 | `#334155` |
| **Primary accent (firelight)** amber-700 | `#b45309` |
| Primary accent hover amber-600 | `#d97706` |
| Primary accent text amber-100 / 200 / 300 | `#fef3c7` / `#fde68a` / `#fcd34d` |
| Primary accent border amber-900 | `#78350f` |
| Primary accent subtle bg amber-950/40 | `#451a0366` |
| **Success / active** emerald-600 | `#059669` |
| Success bg emerald-950 | `#022c22` |
| Success text emerald-300 / 400 | `#6ee7b7` / `#34d399` |
| **Danger** red-800 | `#991b1b` |
| Danger bg red-950 | `#450a0a` |
| Danger text red-300 / 400 | `#fca5a5` / `#f87171` |
| **User-message accent** blue-600 / blue-950/10 bg | `#2563eb` / `#172554` |
| **Quest / faction accent** purple-600 + custom `#7c65f7` (quest fill) |
| **Object accent** orange-500 | `#f97316` |
| **Event accent** red-500 | `#ef4444` |
| Investigation card success bg | `rgba(180,83,9,0.18)` (amber-700 @ 18%) |
| World-enter overlay bg | `radial-gradient(ellipse at center, #1c1917 0%, #020617 70%)` |
| Loader green (login canvas) | `rgb(68, 214, 104)` (project-specific) |

Standard Tailwind opacity suffixes (`/20`, `/40`, `/60`, `/80`) are heavily used on borders and overlays. The Flutter port should adopt `Color(0x__hex)` constants plus a helper to apply `withOpacity()`.

### 2.2 Typography

- **Font family:** `ui-sans-serif, system-ui, sans-serif` everywhere. On Windows that resolves to Segoe UI; on Android to Roboto. **The Flutter port should NOT ship a custom font** — keep it on the platform default to match.
- **Monospace:** `font-mono` is used for IP pill, char count, time elapsed (`tabular-nums`). On the web that's the platform monospace (Consolas / Roboto Mono).
- **Sizes (Tailwind):** `text-[10px]` (uppercase metadata), `text-[11px]` (hints), `text-xs` (12px), `text-sm` (14px) — bulk body, `text-base` (16px), `text-lg` (18px), `text-xl` (20px), `text-2xl` (24px, world name in narrative), `text-3xl` (30px, login/wizard titles).
- **Weights:** `font-medium` (500, default for buttons), `font-semibold` (600, headers), `font-bold` (700, page titles), `font-extrabold` (800, quest tier label).
- **Tracking:** `tracking-tight` (page titles), `tracking-wide`, `tracking-wider`, `tracking-widest` (uppercase section labels). One-off `letter-spacing: 0.3em` and `0.32em` on entrance overlays.
- **Line-height:** default for prose; narrative content uses `leading-7` (1.75rem) for breathing room; `leading-relaxed` (1.625) on descriptive copy; `leading-snug` (1.375) for tight labels.

### 2.3 Spacing

Tailwind's 4px scale, predominantly: 1 (4px), 1.5 (6), 2 (8), 2.5 (10), 3 (12), 3.5 (14), 4 (16), 5 (20), 6 (24), 8 (32), 10 (40), 12 (48). Negative offsets (`-translate-x-1/2`, `-translate-y-1/2`) used for centering pinned elements.

Flutter: a `class AppSpacing` with `static const double xs=4, sm=8, md=12, base=16, lg=24, xl=32` plus arbitrary values inline matches the existing usage well.

### 2.4 Border radius

- `rounded` (4px) — pills, small chips.
- `rounded-md` (6px) — buttons.
- `rounded-lg` (8px) — inputs, secondary cards.
- `rounded-xl` (12px) — primary cards, modals.
- `rounded-2xl` (16px) — large card on dashboard CTA; `rounded-3xl` is not used.
- `rounded-full` (9999px) — pills, IP counter, toggle switches, status pills, action chips.

### 2.5 Shadows

- `shadow-xl shadow-black/20` — cards, panels (heavy enough to read on slate-900).
- `shadow-2xl shadow-black/60` — modals, investigation panel, world-enter title.
- One-off: `box-shadow: 0 0 10px rgba(217,119,6,0.55)` on the active wizard step dot, `forgeGlow` animation pulses 18–40px amber glow on the Forge button.

### 2.6 Transitions & animations

| Element | Property | Duration | Easing |
|---|---|---|---|
| Investigation panel | `transform` (translateY) | 350ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Wizard step transition | `opacity + transform` | 380ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| Cinematic entrance overlay fade | `opacity` | 600ms | ease-out |
| World-enter title float | `top, transform` | 900ms | `cubic-bezier(0.4, 0, 0.2, 1)` |
| World-enter blackout | `opacity` | 350ms | ease-in |
| Nav blackout fade-out (narrative entry) | `opacity` (keyframe) | 800ms (start 100ms) | ease-out |
| Generic hover (buttons, links) | colors | 120–200ms | colors |
| Welcome toast | keyframe `welcomeIn` | 3s | ease-out |
| Forge glow pulse | keyframe | 2.6s | ease-in-out, infinite |
| Star twinkle | keyframe | 2–6s random per-star | ease-in-out, infinite |
| Clover loader trail | per-frame, ~60fps | continuous | linear (position step 2.5 / 600) |

The Flutter port should use `AnimationController` + `CurvedAnimation` with these durations; the
clover loader is best implemented as a `CustomPainter` driven by a `Ticker`.

---

## 3. Component Inventory

### 3.1 Buttons

- **Primary (amber):** `bg-amber-800 hover:bg-amber-700 border border-amber-700/50 text-amber-100`. Used for Enter/Continue/Forge/Save & Restart, etc. Padding varies (typ. `px-5 py-2.5` for medium).
- **Primary-strong (amber-700):** `bg-amber-700 hover:bg-amber-600 text-white font-medium`. Used on confirmation dialogs.
- **Secondary (slate):** `bg-slate-800 hover:bg-slate-700 border border-slate-700/60 text-slate-200`. Used for Home, Switch, Cancel.
- **Ghost (slate transparent):** `text-slate-500 hover:text-slate-200 hover:bg-slate-800`. Used for Cancel links, Back arrows.
- **Danger:** `bg-red-950/60 hover:bg-red-900/80 border border-red-900/50 text-red-400`. Used for Logout, Delete.
- **Danger-strong:** `bg-red-800 hover:bg-red-700 text-white`. Used on "Delete Forever" confirmation.
- **Icon button:** square (`w-8 h-8` or `p-1.5`) versions of secondary with a single SVG glyph (settings cog, restart, phone icon).
- **Disabled state:** `disabled:opacity-40 disabled:cursor-not-allowed`.

### 3.2 Inputs

- **Text input:** `bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:border-blue-500` (login) OR `bg-slate-950 border border-slate-700 focus:border-amber-600` (dashboard settings modal). The wizard variant has `backdrop-filter: blur(8px)` and the amber focus ring (`0 0 0 3px rgba(217,119,6,0.12)`).
- **Textarea:** same styling, plus `resize-none`, `leading-6`. Auto-resizes 44px–164px in the narrative input.
- **Shake animation** on validation failure: 380ms cubic-bezier keyframe, red border.

### 3.3 Chips

Two variants:

- **Selector chip** (wizard tone/role): `border-slate-700/50 text-slate-400 bg-slate-900/40` → selected: `border-amber-700 text-amber-200 bg-amber-950/28%`.
- **Quick-action chip** (narrative input): `bg-slate-800/60 border-slate-700/25 text-slate-400` → hover: `bg-slate-700/80 border-slate-700/50 text-slate-300`. Rounded-full pill.

### 3.4 Cards

- **World card** (dashboard): `bg-slate-900 border border-slate-800` (or `border-amber-900/40` if active) `rounded-xl p-5 shadow-lg shadow-black/20`.
- **Compendium entity card:** flat row, hover `bg-slate-800/60`, colored dot indicator (4px) per type. Selected → `bg-slate-800/80` + dot opacity 1.
- **Investigation card** (in panel queue): in-progress = slate-900 + amber-900/40 border + 180px wide; complete = amber-950/20 + amber-700/50 border + 220px wide.
- **Quest card** (quest panel): title + description + progress bar (`#7c65f7` fill) + "X of Y milestones".
- **Review card** (wizard step 4): slate-900/50 with slate-800/60 border, internal `review-row` divider lines.

### 3.5 Modals

- Layout: `fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50`.
- Inner: `bg-slate-900 rounded-xl max-w-{sm|md|lg} w-full mx-4 border border-slate-700 shadow-2xl`. Settings modal adds `max-h-[85vh] flex flex-col` so its body scrolls.
- Header: `px-6 py-4 border-b border-slate-800` with title and optional close X.
- Body: `p-6`.
- Footer: `px-6 py-3 border-t border-slate-800 flex justify-end gap-2`.

### 3.6 Toasts / Banners

- **Welcome toast** — bottom: false, top: 1rem center, 3s `welcomeIn` keyframe, slate-900/92 + amber border, pill shape.
- **Investigation retry toast** — bottom-center pill, slate-800 + amber border.
- **Quest check banner** — bottom-center pill, slate-900/95 + purple border, fades after 4s.
- **API-key banner** — full-width section, amber-950/40 + amber-800/60 border, with an inline action button.

### 3.7 IP Counter pill

`flex items-center gap-1.5 bg-amber-950/60 border border-amber-800/50 text-amber-300 px-3 py-1.5 rounded-full text-sm font-mono`. Magnifying-glass SVG + "5/5" text.

### 3.8 Popovers

- **Settings cog popover** (narrative): `absolute top-full mt-2 right-0 bg-slate-900 border-slate-700 rounded-lg p-3 shadow-xl z-50 min-w-[210px]`. Closes on outside click + Escape.
- **Skip-time popover** (narrative): `absolute bottom-full mb-1 right-0 bg-slate-900 ...`. Anchored above the Act button.

### 3.9 Toggle switch (settings.html)

Custom 2.5rem × 1.4rem track with 1rem circular thumb, off = slate-600, on = amber-700. 200ms slide.

### 3.10 Clover loader

Custom canvas/painter component. Inputs: `size: int (px)`, `hue: int (degrees, 0-360)`. Draws a 4-petal rose curve (`r = cos(2θ)`) with a 600-segment ring, a head dot with a radial-gradient glow, and an HSL-interpolated trail (lightness 22→64%, saturation 55→85% across the trail). Plays at `pos += 2.5` per frame. DPR-aware (clamped to 2). The login page has a bespoke RGB variant (green `(68,214,104)`); everywhere else uses HSL with `hue=38` (amber) or `hue=142` (default emerald-green).

---

## 4. Interaction Map

### 4.1 Auth flow

1. Page lands on `/` (`index.html`). If `localStorage.apiKey` is present, immediate redirect to `/dashboard.html`.
2. Sign in: `POST /api/login` `{username, password}` → `{token}`. Store in `localStorage.apiKey`; store `localStorage.username` for the welcome toast; set `sessionStorage.justLoggedIn = "1"`.
3. Register: same flow against `POST /api/register`.
4. All subsequent calls add `Authorization: Bearer <token>`. A 401 anywhere clears the token and redirects to `/`.
5. `POST /api/logout` (best-effort; ignores failures) and clear local token, redirect to `/`.

### 4.2 Dashboard flow

1. On load: `GET /api/worlds` and `GET /api/settings/status` in parallel.
2. Render world cards. Empty state: "No worlds yet. Create one below."
3. If `justLoggedIn`, play cinematic entrance (see §1.2).
4. Enter active world → world-enter transition → `/narrative.html?world_id={id}&fresh=1`.
5. Switch inactive world → `POST /api/worlds/switch {world_id}` → reload list.
6. Reset / Delete go through their respective modals.

### 4.3 World creation flow

1. Step through Name → Tone → Premise → Role.
2. Step 4 "Forge" → `POST /api/worlds/create {name, premise, theme_tone, player_role}`.
3. On success: 700ms transition → `/narrative.html?world_id={id}`.

### 4.4 Narrative gameplay flow

1. On load: `GET /api/world?world_id={id}` → `{world, entities, handoff, success}`. Render world name + premise + opening scene (with intro animation if fresh).
2. Restore `conversationHistory` from `localStorage[`ayen_ode_history_{worldId}`]`. Restore `draft` from `localStorage[`ayen_ode_draft_{worldId}`]`.
3. `GET /api/worlds/{id}/currencies` → populate the IP counter.
4. `GET /api/worlds/{id}/quests` → render quest panel.
5. `GET /api/worlds/{id}/time` → populate the time label.
6. Submit action: `POST /api/narrative {world_id, action, history}`. Optional double-tap confirm mode (toggled in cog popover). Response shape: `{narrative, history, investigation_points, max_investigation_points, game_time: {seconds, label}}`. Append the new narrative block, scroll to bottom, save history to localStorage.
7. After every successful narrative call: re-fetch the world (`GET /api/world?world_id={id}`) to refresh entities, then `loadWorldState()` (compendium re-render) and `loadQuests()`.
8. Investigation flow:
   - User hovers top-edge band → panel opens.
   - Click an `<investigate item='name' cost='1'>display</investigate>` link rendered in narrative HTML → `showInvestigationConfirmation()`. If the entity already exists in `currentEntities`, jump straight to the compendium detail pane instead.
   - Confirm → `POST /api/investigate {world_id, item_name, entity_type, cost}` → `{investigation_id, remaining_points}`. Add to `activeInvestigations`. Open panel. Start 500ms polling + 1s timer ticker.
   - Poll `GET /api/investigations/{jobId}` for status. On status `complete`: render result card with "View Details →".
   - After 60s, the point auto-refunds via `POST /api/worlds/{id}/currencies/restore {amount: 1}`.
   - View details → close panel, scroll/expand the compendium, slide up the entity detail pane.
   - Auto-close panel 1200ms after the LAST active job finishes.
9. Quest flow:
   - Tier 1/2 cards display passively with progress bars.
   - Tier 3 "Thread" cards have Track (`POST /api/worlds/{id}/quests/{questId}/promote`) and Ignore (`POST .../dismiss`) buttons.
   - `checkQuestProgress(questId)` calls `POST .../check` which costs points and returns `{title, matched, total, percentage, points_spent}` → flashed in a bottom-center banner.
10. Compendium flow:
    - Search input filters entities client-side by name/summary.
    - Entity card click → load detail pane: `GET /api/entities/{id}?world_id=X` + `GET /api/entities/{id}/stats?world_id=X` in parallel. Render summary, stat bars, timeline notes, open questions, tags. Cached in `entityCache`.
    - Linkified entity references in summary/notes/questions → clicking opens that entity (pushing detail history for back-nav).
    - Cross-entity link writes: `addToCompendium()` scans the entity's summary + timeline notes for references to other entities, then `POST /api/entities/link` for each.
11. Skip time: `POST /api/worlds/{id}/skip-time {seconds}`. May fail with `{blocking: {investigation: [{name}, ...]}}` → flash error label in the time bar for 3.5s.
12. Settings popover: persists `confirmBeforeSend` to `localStorage.ayen_ode_settings`.

### 4.5 Dashboard settings modal flow

1. Open: `GET /api/settings` → fill fields (API key field stays empty; placeholder shows masked value if a key is saved).
2. `phRefreshStatus()` (every 5s while open): `GET /api/tunnel/status` → update pill, hostname, install card with QR.
3. Phone access toggle: `POST /api/network/settings {network_access_enabled: bool}`.
4. Save: `POST /api/settings` with env-var-shaped payload (`ANTHROPIC_API_KEY`, `APP_USERNAME`, `APP_PASSWORD`, `ALLOWED_IPS`, `AYEN_ODE_PORT`, `AYEN_ODE_FULLSCREEN`).
5. Save & Restart: same, plus `POST /api/restart` and modal closes after 600ms.
6. Fullscreen "Toggle now" → calls `window.pywebview.api.toggle_fullscreen()` if running inside pywebview, else `document.fullscreenElement` API. **Flutter port:** call native `window_manager` package equivalents on Windows.

---

## 5. API Surface

All endpoints take `Authorization: Bearer <token>` unless noted. Bodies are JSON.
Responses go through `unwrapJsonRpcResponse()` in `app.js`: if the response object has `jsonrpc:"2.0"` and a `result` field, the `result` is returned; otherwise the response is passed through. **The Flutter Dio client must mirror this unwrap.**

### Auth
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/api/login` | `{username, password}` | `{token}` |
| POST | `/api/register` | `{username, password}` | `{token}` |
| POST | `/api/logout` | — | best-effort |
| GET | `/api/whoami` | — | `{user, ...}` *(referenced in CLAUDE.md)* |
| GET | `/health` | — | 200 OK |

### Worlds
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/api/worlds` | — | `{worlds: [{world_id, name, premise, theme_tone, status, ...}]}` |
| GET | `/api/worlds/active` | — | `{world: {...}}` |
| POST | `/api/worlds/create` | `{name, premise, theme_tone, player_role}` | `{world_id}` |
| POST | `/api/worlds/switch` | `{world_id}` | `{ok}` |
| POST | `/api/worlds/{id}/reset` | `{}` | `{success}` |
| DELETE | `/api/worlds/{id}` | — | `{success}` |
| GET | `/api/world?world_id={id}` | — | `{success, world, entities: [...], handoff, world_id}` |
| GET | `/api/worlds/{id}/time` | — | `{seconds, label}` |
| POST | `/api/worlds/{id}/skip-time` | `{seconds}` | `{game_time: {seconds, label}}` or `400 {blocking: {investigation: [...]}}` |
| GET | `/api/worlds/{id}/currencies` | — | `{balance, max_balance, points, max_points}` (both pairs returned for compat) |
| POST | `/api/worlds/{id}/currencies/restore` | `{amount}` | `{balance_after, max_balance}` |
| GET | `/api/worlds/{id}/quests` | — | `{quests: [{quest_id, tier, title, description, status, completion_tags, progress_tags}]}` |
| POST | `/api/worlds/{id}/quests/{questId}/promote` | — | `{ok}` |
| POST | `/api/worlds/{id}/quests/{questId}/dismiss` | — | `{ok}` |
| POST | `/api/worlds/{id}/quests/{questId}/check` | — | `{title, matched, total, percentage, points_spent}` |

### Narrative
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/api/narrative` | `{world_id, action, history}` | `{narrative, history: [...], investigation_points, max_investigation_points, game_time}` |

### Investigation
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/api/investigate` | `{world_id, item_name, entity_type, cost}` | `{investigation_id, remaining_points}` |
| GET | `/api/investigations/{jobId}` | — | `{status: "queued"\|"processing"\|"complete"\|"failed", result: {entity}}` |

### Entities
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/api/entities/{id}?world_id={w}` | — | `{entity: {entity_id, name, type, summary, timeline_notes, open_questions, tags, status}}` |
| GET | `/api/entities/{id}/stats?world_id={w}` | — | `{stats: {strength: 0-100, ...}}` |
| POST | `/api/entities/link` | `{world_id, entity_id_a, entity_id_b, relation}` | `{ok}` |

### Settings
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/api/settings` | — | `{anthropic_api_key_set, anthropic_api_key_masked, app_username, app_password_set, allowed_ips, ayen_ode_port, fullscreen}` |
| POST | `/api/settings` | env-var-shaped payload | `{ok}` |
| GET | `/api/settings/status` | — | `{api_key_configured}` |
| POST | `/api/server/restart` | `{}` | `{ok}` |
| POST | `/api/restart` | `{}` | (exits server with code 42) |

### Tunnel
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/api/tunnel/status` | — | `{binary_present, logged_in, tunnel_id, hostname, running, network_access_enabled, last_error}` |
| POST | `/api/tunnel/login` | `{}` | `{url}` |
| GET | `/api/tunnel/login/status` | — | `{done?, error?}` |
| POST | `/api/tunnel/setup` | `{}` | `{existing}` |
| POST | `/api/tunnel/start` | `{}` | `{ok}` |
| POST | `/api/tunnel/stop` | `{}` | `{ok}` |
| GET | `/api/network/settings` | — | `{tunnel_hostname, cors_origins[], network_access_enabled}` |
| POST | `/api/network/settings` | `{network_access_enabled?, tunnel_hostname?, cors_origins[]?}` | `{ok}` |
| GET | `/api/qrcode?text={url}&size={n}` | — | image/png blob |

### Open question
`narrative-quests.js` calls `apiFetch(...)` which is **not defined** in any file I read. This is a latent bug — quest calls likely throw `ReferenceError`. The Flutter port should use a single typed client uniformly (no equivalent of this gap).

---

## 6. Asset Inventory

- `static/favicon-16.png`, `favicon-32.png`
- `static/icons/icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon-180.png`
- No custom font files — system stack only.
- No image assets beyond favicons + PWA icons.
- All graphics (clover, stars, glows, gradients) are drawn at runtime via canvas/CSS.

For the Flutter port:
- Copy the four icons into `assets/icons/` (used for the dashboard QR backdrop white card, etc., once we wire them up).
- Generate Flutter launcher icons (Windows ICO + Android adaptive) from `icon-512.png` and `icon-maskable-512.png`.
- No font assets needed.

---

## 7. State Shape (client-side)

| Storage | Key | Type | Lifetime |
|---|---|---|---|
| `localStorage` | `apiKey` | string (auth token) | persistent |
| `localStorage` | `username` | string | persistent |
| `localStorage` | `ayen_ode_history_{worldId}` | JSON `[{role, content}, …]` | persistent per world |
| `localStorage` | `ayen_ode_draft_{worldId}` | string | persistent per world |
| `localStorage` | `ayen_ode_settings` | `{confirmBeforeSend: bool}` | persistent |
| `sessionStorage` | `justLoggedIn` | `"1"` | one-shot |
| `sessionStorage` | `worldEntering` | `"1"` | one-shot |
| `sessionStorage` | `replayIntro` | `"1"` | one-shot |

In-page mutable state (narrative.js):

- `currentWorldId`, `conversationHistory`, `currentEntities`
- `investigationPoints`, `maxInvestigationPoints`, `activeInvestigations: {jobId → {jobId, itemName, entityType, status, result, startedAt, pointRestored, reviewed}}`
- `selectedEntityId`, `detailHistory: string[]`, `entityCache: {id → html}`
- `compendiumSectionState: {sectionId → bool}` (collapse state, ephemeral)
- `currentTimeLabel`, `_introSkipRequested`, `pendingInvestigation`, `pendingConfirm`
- `historyRenderOffset` (pagination, 100 messages per page, load-more on upward scroll)

For the Flutter port, this maps to:
- `flutter_secure_storage` for `apiKey` (cross-platform secure storage).
- `shared_preferences` for `username`, `ayen_ode_settings.confirmBeforeSend`, draft, conversation history.
- Riverpod providers for everything in-page.

---

## 8. Behaviors That Need Explicit Flutter Implementation

1. **Center-35% top-edge hover trigger** for investigation panel on desktop; full-width tap-to-open on mobile (≤768px). Hover doesn't exist on mobile, so the desktop trigger should be `MouseRegion` + `onEnter` on Windows and a tap target on Android.
2. **Auto-close investigations panel** 1200ms after the LAST active job finishes (not the first).
3. **Settings cog in top-right of narrative header** with a popover (NOT a Material `PopupMenu` — needs custom anchoring + amber styling).
4. **Right rail behavior:** desktop = inline aside (w-72 each, gap-4 from main); mobile = swipeable bottom sheet drawer (translateY animation). Flutter: `MediaQuery.size.width <= 768` → use `showModalBottomSheet`; else inline `Row` children.
5. **Clover loader** as a `CustomPainter` driven by a `Ticker`, parametrized by `size` and `hue`. Used both as a small inline indicator and as a 180/220px hero element on entrance overlays. Login uses a slightly different RGB variant (just hardcode an alternate paint method or pass RGB instead of HSL).
6. **Page-to-page blackout** between dashboard and narrative: in Flutter we can use a custom page route with a `FadeTransition` to/from black to achieve the same seamless feel, then chain in the narrative's typewriter once on the new page.
7. **Typewriter intro** for the opening scene first paragraph (char delay 12–35ms, scaled by line length), plus stagger-fade for subsequent paragraphs (380ms each). Implement with a `Stream<String>` + `Text` rebuilds or an `AnimatedTextKit`-style controller. Honor a Skip button.
8. **Linkified entity references** in narrative text — port the regex-based name detection from `narrative-entity.js` and emit `TextSpan`s with `recognizer` that open the compendium detail.
9. **`<investigate item='name' cost='1'>` tag parsing** — the AI emits these inline tags. Port the regex in `parseInvestigateText` and render as `WidgetSpan` with a custom `InvestigateLink` widget.
10. **Polling cadences**: 500ms for `/api/investigations/{id}`, 5s for `/api/tunnel/status` while settings is open, 500ms for `/health` after a restart (max 12s). Use `Stream.periodic` or `Timer.periodic`.
11. **F11 fullscreen** key handler (`app.js`). On Windows: `window_manager` package's `setFullScreen`. On Android: full-screen by default in landscape orientation, no key handler.
12. **PWA install button** (Android Chrome). Not applicable in a native Android Flutter app — the app *is* the install. Hide that button on Android, hide on Windows desktop too.
13. **Confirmation mode for narrative submit** (`confirmBeforeSend`) — first Enter arms a "press Enter again to send" state (amber border on input, readonly, hint text changes); Escape cancels.
14. **Mobile drawer toggle bar** (`#mobileRailBar`) — two pills at bottom-right that open the Quest/Compendium drawers. Pure Flutter: `BottomSheet` + a `FloatingActionButton.extended` cluster.

---

## 9. Mapping → Flutter Port

| Web | Flutter |
|---|---|
| `localStorage.apiKey` | `flutter_secure_storage` `auth_token` key |
| `localStorage.username` | `shared_preferences` `username` |
| `localStorage.ayen_ode_history_{wid}` | `shared_preferences` `history_{wid}` |
| `localStorage.ayen_ode_settings` | `shared_preferences` `settings` |
| `sessionStorage.*` | in-memory Riverpod state, cleared on first read |
| `fetch(... { Authorization: Bearer ... })` | `Dio` with `AuthInterceptor` |
| `apiCall` JSON-RPC unwrap | `Dio` response transformer |
| 401 → redirect `/` | `Dio` `onError` → `clearToken()` + `goRouter.go('/login')` |
| Tailwind utility classes | `AppColors` + `AppSpacing` + `TextStyle`s in `lib/theme/` |
| `<canvas>` clover | `CloverLoader` widget (CustomPainter + Ticker) |
| Modals (HTML `position: fixed`) | `showDialog` with `Dialog` and a transparent barrier |
| World-enter overlay sequence | A `Route<dynamic>` page transition with a sequence of `AnimationController`s |
| Service worker / PWA | N/A — Flutter app on Windows + Android |
| Tunnel/QR settings | Out of scope for v0.1; the in-app settings shows API key + login creds + port, not phone-access |
| pywebview fullscreen bridge | `window_manager` (Windows); no-op on Android |

---

## 10. Open questions / risks for v0.1

1. **`apiFetch` mystery** — `narrative-quests.js` calls a function that isn't defined. Likely a missed refactor. The Flutter port treats quest endpoints as standard `Dio` calls; no equivalent gap.
2. **CDN Tailwind in production** — the web app pulls Tailwind from a CDN, which is fragile. Not our concern, but means the visual targets are stable as long as Tailwind doesn't ship breaking changes.
3. **Static drift** between `main` and the canonical worktree at `.claude/worktrees/great-poincare-3d4bc0/`. The worktree's `dashboard.html` includes the in-window Settings modal (recently moved out of `settings.html`); the audit is based on the worktree. Once main lands the same change, drift resolves.
4. **`/api/world` vs `/api/worlds/{id}/...`** inconsistency — single-world fetch uses singular path; everything else uses plural. The Dio client just mirrors the actual endpoints; no compatibility shim.
5. **Investigation timer (60s) refund** happens client-side after a fixed delay, not server-confirmed. Same behavior in the Flutter port.

---

This audit is the source of truth for Phases 2–5. Any divergence in implementation should be
either (a) updated here first or (b) flagged in the PR as a conscious deviation.
