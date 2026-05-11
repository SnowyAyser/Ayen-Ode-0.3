import 'package:flutter/material.dart';

import 'colors.dart';
import 'spacing.dart';
import 'typography.dart';

/// Builds the dark Material 3 theme that mirrors the web frontend's
/// slate-canvas + amber-firelight design language.
///
/// We're using Material 3 (`useMaterial3: true`) for its richer component
/// defaults, but most screens reach for custom widgets that consume
/// `AppColors` / `AppTypography` / `AppSpacing` directly — the `ThemeData`
/// here just provides sensible fall-backs for generic widgets (text fields,
/// dialogs, snack bars) so they don't stand out from the bespoke layouts.
ThemeData buildAyenOdeTheme() {
  const scheme = ColorScheme(
    brightness: Brightness.dark,
    primary: AppColors.amber700,
    onPrimary: AppColors.amber100,
    primaryContainer: AppColors.amber950,
    onPrimaryContainer: AppColors.amber200,
    secondary: AppColors.emerald600,
    onSecondary: Colors.white,
    secondaryContainer: AppColors.emerald950,
    onSecondaryContainer: AppColors.emerald300,
    tertiary: AppColors.questViolet,
    onTertiary: Colors.white,
    error: AppColors.red800,
    onError: AppColors.red200,
    errorContainer: AppColors.red950,
    onErrorContainer: AppColors.red300,
    surface: AppColors.slate900,
    onSurface: AppColors.textBody,
    surfaceContainerHighest: AppColors.slate800,
    onSurfaceVariant: AppColors.textSecondary,
    outline: AppColors.slate700,
    outlineVariant: AppColors.borderSubtle,
    inverseSurface: AppColors.slate100,
    onInverseSurface: AppColors.slate900,
    inversePrimary: AppColors.amber400,
    shadow: Colors.black,
    scrim: Colors.black,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: scheme,
    scaffoldBackgroundColor: AppColors.bg,
    canvasColor: AppColors.bg,
    fontFamily: null,
    textTheme: AppTypography.textTheme.apply(
      bodyColor: AppColors.textBody,
      displayColor: AppColors.textPrimary,
    ),
    iconTheme: const IconThemeData(
      color: AppColors.textSecondary,
      size: 18,
    ),
    dividerTheme: const DividerThemeData(
      color: AppColors.slate800,
      thickness: 1,
      space: 1,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.slate800,
      hintStyle: AppTypography.body.copyWith(color: AppColors.textVeryMuted),
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.base,
        vertical: AppSpacing.smPlus,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        borderSide: const BorderSide(color: AppColors.slate700),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        borderSide: const BorderSide(color: AppColors.slate700),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        borderSide: const BorderSide(color: AppColors.amber600, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        borderSide: const BorderSide(color: AppColors.red700),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.accentBg,
        foregroundColor: AppColors.accentText,
        elevation: 0,
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.smPlus,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        ),
        textStyle: AppTypography.bodyMedium,
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: AppColors.textSecondary,
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
        textStyle: AppTypography.bodyMedium,
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.textBody,
        side: const BorderSide(color: AppColors.slate700),
        backgroundColor: AppColors.slate800,
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
        textStyle: AppTypography.bodyMedium,
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: AppColors.slate900,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        side: const BorderSide(color: AppColors.slate700),
      ),
      titleTextStyle: AppTypography.bodyMedium.copyWith(
        color: AppColors.textPrimary,
        fontWeight: FontWeight.w600,
        fontSize: 16,
      ),
      contentTextStyle: AppTypography.body,
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.slate800,
      contentTextStyle: AppTypography.body,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        side: const BorderSide(color: AppColors.slate700),
      ),
    ),
    popupMenuTheme: PopupMenuThemeData(
      color: AppColors.slate900,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        side: const BorderSide(color: AppColors.slate700),
      ),
      textStyle: AppTypography.body,
    ),
    scrollbarTheme: ScrollbarThemeData(
      thumbColor: WidgetStateProperty.all(
        AppColors.slate500.withValues(alpha: 0.35),
      ),
      thickness: WidgetStateProperty.all(4),
      radius: const Radius.circular(2),
    ),
  );
}
