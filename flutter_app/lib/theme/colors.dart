import 'package:flutter/material.dart';

/// Design tokens for Ayen-Ode.
///
/// Source: `flutter_app/design-audit.md` §2.1. Values mirror the Tailwind
/// palette the web frontend uses via CDN, plus a handful of project-specific
/// constants (the PWA theme-color `#0b0b10`, the world-enter overlay base,
/// and the quest accent `#7c65f7`).
class AppColors {
  AppColors._();

  // ─── Slate (canvas + surfaces) ─────────────────────────────────────────
  static const slate50 = Color(0xFFF8FAFC);
  static const slate100 = Color(0xFFF1F5F9);
  static const slate200 = Color(0xFFE2E8F0);
  static const slate300 = Color(0xFFCBD5E1);
  static const slate400 = Color(0xFF94A3B8);
  static const slate500 = Color(0xFF64748B);
  static const slate600 = Color(0xFF475569);
  static const slate700 = Color(0xFF334155);
  static const slate800 = Color(0xFF1E293B);
  static const slate900 = Color(0xFF0F172A);
  static const slate950 = Color(0xFF020617);

  // ─── Amber (primary accent — firelight) ────────────────────────────────
  static const amber50 = Color(0xFFFFFBEB);
  static const amber100 = Color(0xFFFEF3C7);
  static const amber200 = Color(0xFFFDE68A);
  static const amber300 = Color(0xFFFCD34D);
  static const amber400 = Color(0xFFFBBF24);
  static const amber500 = Color(0xFFF59E0B);
  static const amber600 = Color(0xFFD97706);
  static const amber700 = Color(0xFFB45309);
  static const amber800 = Color(0xFF92400E);
  static const amber900 = Color(0xFF78350F);
  static const amber950 = Color(0xFF451A03);

  // ─── Emerald (success, active) ─────────────────────────────────────────
  static const emerald300 = Color(0xFF6EE7B7);
  static const emerald400 = Color(0xFF34D399);
  static const emerald500 = Color(0xFF10B981);
  static const emerald600 = Color(0xFF059669);
  static const emerald700 = Color(0xFF047857);
  static const emerald800 = Color(0xFF065F46);
  static const emerald900 = Color(0xFF064E3B);
  static const emerald950 = Color(0xFF022C22);

  // ─── Red (danger) ──────────────────────────────────────────────────────
  static const red200 = Color(0xFFFECACA);
  static const red300 = Color(0xFFFCA5A5);
  static const red400 = Color(0xFFF87171);
  static const red500 = Color(0xFFEF4444);
  static const red700 = Color(0xFFB91C1C);
  static const red800 = Color(0xFF991B1B);
  static const red900 = Color(0xFF7F1D1D);
  static const red950 = Color(0xFF450A0A);

  // ─── Blue (user-message attribution) ───────────────────────────────────
  static const blue400 = Color(0xFF60A5FA);
  static const blue500 = Color(0xFF3B82F6);
  static const blue600 = Color(0xFF2563EB);
  static const blue950 = Color(0xFF172554);

  // ─── Purple + custom quest-violet ──────────────────────────────────────
  static const purple400 = Color(0xFFC084FC);
  static const purple600 = Color(0xFF9333EA);
  static const purple700 = Color(0xFF7E22CE);

  /// Quest progress-bar fill. Project-specific, not in the Tailwind palette.
  static const questViolet = Color(0xFF7C65F7);

  // ─── Orange (object entity dot) ────────────────────────────────────────
  static const orange400 = Color(0xFFFB923C);
  static const orange500 = Color(0xFFF97316);

  // ─── Project-specific atmospherics ─────────────────────────────────────

  /// PWA `<meta name="theme-color">` value.
  static const themeBg = Color(0xFF0B0B10);

  /// World-enter transition radial-gradient base (a warm near-black).
  static const worldEnterBase = Color(0xFF1C1917);

  /// Login clover loader colour (web version uses raw RGB rather than HSL).
  static const loginCloverGreen = Color(0xFF44D668);

  // ─── Semantic aliases — what the UI actually reaches for ───────────────

  /// Default page background (dashboard, narrative, settings).
  static const bg = slate950;

  /// Header / card surface.
  static const surface = slate900;

  /// Elevated surface (input fields, popovers).
  static const surfaceElevated = slate800;

  /// Subtle hairline borders inside dark panels.
  static const borderSubtle = Color(0x991E293B); // slate-800 @ 60%

  /// Emphasis borders (focused inputs, selected cards, modal outlines).
  static const border = slate700;

  /// Primary text on dark surfaces.
  static const textPrimary = slate100;

  /// Body text.
  static const textBody = slate200;

  /// Secondary / supporting text.
  static const textSecondary = slate400;

  /// Muted text (hints, metadata).
  static const textMuted = slate500;

  /// Very muted text (placeholders, dimmed labels).
  static const textVeryMuted = slate600;

  /// Primary accent button background.
  static const accentBg = amber800;

  /// Primary accent button hover state.
  static const accentBgHover = amber700;

  /// Primary accent text colour (on amber backgrounds).
  static const accentText = amber100;
}
