import 'package:flutter/material.dart';

import 'colors.dart';

/// Type scale for Ayen-Ode.
///
/// The web frontend uses the platform `ui-sans-serif, system-ui, sans-serif`
/// stack — there are no custom font files. On Windows that resolves to
/// Segoe UI; on Android to Roboto. Passing `fontFamily: null` to a
/// `TextStyle` gives us exactly the same behaviour, so we don't ship any
/// font assets.
///
/// Sizes mirror the Tailwind classes the web frontend uses (text-xs through
/// text-3xl), with one project-specific `metadata` style for the
/// `text-[10px] uppercase tracking-wide` labels that appear all over the
/// settings + wizard.
class AppTypography {
  AppTypography._();

  // Sizes (px) — Tailwind default scale.
  static const _xs10 = 10.0; // uppercase metadata labels
  static const _xs11 = 11.0; // hints, supporting copy
  static const _xs = 12.0; // text-xs
  static const _sm = 14.0; // text-sm (bulk body)
  static const _base = 16.0; // text-base
  static const _lg = 18.0; // text-lg
  static const _xl = 20.0; // text-xl
  static const _xl2 = 24.0; // text-2xl (world name)
  static const _xl3 = 30.0; // text-3xl (page titles)

  /// 10px uppercase, slate-400 — used on settings field labels.
  static const TextStyle metadata = TextStyle(
    fontSize: _xs10,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.08 * _xs10,
    color: AppColors.slate400,
    height: 1.2,
  );

  /// 11px slate-500 — hints below inputs, supporting copy.
  static const TextStyle hint = TextStyle(
    fontSize: _xs11,
    fontWeight: FontWeight.w400,
    color: AppColors.textMuted,
    height: 1.4,
  );

  /// 12px slate-500 — `text-xs` body. Used on counts, helper text.
  static const TextStyle xs = TextStyle(
    fontSize: _xs,
    fontWeight: FontWeight.w400,
    color: AppColors.textMuted,
    height: 1.4,
  );

  /// 14px — `text-sm`, the dominant body size in the app.
  static const TextStyle body = TextStyle(
    fontSize: _sm,
    fontWeight: FontWeight.w400,
    color: AppColors.textBody,
    height: 1.5,
  );

  /// 14px, slightly heavier — used on labels, button text.
  static const TextStyle bodyMedium = TextStyle(
    fontSize: _sm,
    fontWeight: FontWeight.w500,
    color: AppColors.textBody,
    height: 1.5,
  );

  /// 16px — `text-base` for narrative paragraphs (with `leading-7` ≈ 1.75
  /// line-height for breathing room).
  static const TextStyle narrative = TextStyle(
    fontSize: _base,
    fontWeight: FontWeight.w400,
    color: AppColors.textBody,
    height: 1.75,
  );

  /// 18px — `text-lg` for emphasized inline copy.
  static const TextStyle lg = TextStyle(
    fontSize: _lg,
    fontWeight: FontWeight.w500,
    color: AppColors.textPrimary,
    height: 1.5,
  );

  /// 20px bold — `text-xl font-bold` for section / header titles.
  static const TextStyle headerSmall = TextStyle(
    fontSize: _xl,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.01,
    height: 1.3,
  );

  /// 24px bold — `text-2xl font-bold tracking-tight`. World name in narrative
  /// header.
  static const TextStyle header = TextStyle(
    fontSize: _xl2,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.02,
    height: 1.2,
  );

  /// 30px bold — `text-3xl font-bold tracking-tight`. Login + wizard step
  /// titles.
  static const TextStyle title = TextStyle(
    fontSize: _xl3,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.03,
    height: 1.2,
  );

  /// Wide uppercase caption used in section markers
  /// (`tracking-widest`). 12px so it stays subtle.
  static const TextStyle sectionLabel = TextStyle(
    fontSize: _xs,
    fontWeight: FontWeight.w600,
    color: AppColors.slate200,
    letterSpacing: 0.1 * _xs,
    height: 1.2,
  );

  /// Quest tier marker — `quest-tier-label` in the CSS.
  /// 0.6rem (9.6px) → 10px, 800 weight, slate-500, tracking 0.1em.
  static const TextStyle questTierLabel = TextStyle(
    fontSize: _xs10,
    fontWeight: FontWeight.w800,
    color: AppColors.slate500,
    letterSpacing: 0.1 * _xs10,
    height: 1.2,
  );

  /// Monospaced numeric for the IP counter pill ("5/5"), char count.
  static const TextStyle mono = TextStyle(
    fontFamily: 'monospace',
    fontSize: _sm,
    fontWeight: FontWeight.w400,
    color: AppColors.amber300,
    fontFeatures: [FontFeature.tabularFigures()],
  );

  /// Build the Material `TextTheme` from these styles.
  static const TextTheme textTheme = TextTheme(
    displayLarge: title,
    displayMedium: title,
    displaySmall: header,
    headlineLarge: header,
    headlineMedium: header,
    headlineSmall: headerSmall,
    titleLarge: headerSmall,
    titleMedium: bodyMedium,
    titleSmall: bodyMedium,
    bodyLarge: narrative,
    bodyMedium: body,
    bodySmall: xs,
    labelLarge: bodyMedium,
    labelMedium: hint,
    labelSmall: metadata,
  );
}
