import 'package:flutter/animation.dart';

/// Spacing, radius, and animation tokens for Ayen-Ode.
///
/// Sourced from Tailwind's 4px base scale, with a handful of project-specific
/// durations (the world-enter transition stages, the typewriter delay window).
class AppSpacing {
  AppSpacing._();

  // ─── Spacing (Tailwind 4px scale) ──────────────────────────────────────
  static const double half = 2.0; // 0.5
  static const double xs = 4.0; // 1
  static const double xxs = 6.0; // 1.5
  static const double sm = 8.0; // 2
  static const double smPlus = 10.0; // 2.5
  static const double md = 12.0; // 3
  static const double mdPlus = 14.0; // 3.5
  static const double base = 16.0; // 4
  static const double lg = 20.0; // 5
  static const double xl = 24.0; // 6
  static const double xl2 = 32.0; // 8
  static const double xl3 = 40.0; // 10
  static const double xl4 = 48.0; // 12

  // ─── Border radii ──────────────────────────────────────────────────────
  static const double radiusSm = 4.0; // rounded
  static const double radiusMd = 6.0; // rounded-md
  static const double radiusLg = 8.0; // rounded-lg
  static const double radiusXl = 12.0; // rounded-xl
  static const double radius2xl = 16.0; // rounded-2xl
  static const double radiusFull = 9999.0; // rounded-full

  // ─── Breakpoints ──────────────────────────────────────────────────────
  /// Below this width, side rails collapse into bottom-sheet drawers
  /// (matches the web frontend's `@media (max-width: 768px)`).
  static const double mobileBreakpoint = 768.0;

  // ─── Common widget dimensions ─────────────────────────────────────────
  /// Width of each right rail (Quests + Compendium) on desktop.
  static const double railWidth = 288.0; // Tailwind w-72
  static const double headerHeight = 64.0;
  static const double inputMinHeight = 44.0;
  static const double inputMaxHeight = 164.0;
}

/// Animation durations + curves, mirroring the audit's table.
class AppMotion {
  AppMotion._();

  // Durations
  static const Duration fast = Duration(milliseconds: 120);
  static const Duration hover = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 200);
  static const Duration medium = Duration(milliseconds: 250);
  static const Duration slow = Duration(milliseconds: 300);
  static const Duration panel = Duration(milliseconds: 350);
  static const Duration step = Duration(milliseconds: 380);
  static const Duration introParagraph = Duration(milliseconds: 380);
  static const Duration overlayFade = Duration(milliseconds: 600);
  static const Duration overlayTitle = Duration(milliseconds: 700);
  static const Duration navBlackout = Duration(milliseconds: 800);
  static const Duration worldEnterTitle = Duration(milliseconds: 900);
  static const Duration introPause = Duration(milliseconds: 450);
  static const Duration blackoutHold = Duration(milliseconds: 1100);
  static const Duration toastFlash = Duration(seconds: 3);
  static const Duration welcomeToast = Duration(milliseconds: 3200);
  static const Duration forgeGlow = Duration(milliseconds: 2600);

  // Curves
  /// `cubic-bezier(0.4, 0, 0.2, 1)` — the dominant easing on the web app.
  /// Material's `Curves.fastOutSlowIn` is the same definition.
  static const Curve appEase = Curves.fastOutSlowIn;
  static const Curve easeOut = Curves.easeOut;
  static const Curve easeIn = Curves.easeIn;
  static const Curve easeInOut = Curves.easeInOut;
}
