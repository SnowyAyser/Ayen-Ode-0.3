import 'package:flutter/material.dart';

import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';

/// The audit's button variants (§3.1) translated to widgets.
///
/// Every button is a small wrapper around [AnimatedContainer] + [InkWell] so
/// hover/press states match the web's `transition-colors` aesthetic without
/// reaching for Material's stock `ElevatedButton`-style chrome.

enum AppButtonVariant {
  /// `bg-amber-800 hover:bg-amber-700` — Enter / Continue / Forge / Save.
  primary,

  /// `bg-amber-700 hover:bg-amber-600` — confirmation dialogs.
  primaryStrong,

  /// `bg-slate-800 hover:bg-slate-700` — Home, Switch, Cancel.
  secondary,

  /// Transparent slate-text — Cancel links, Back arrows.
  ghost,

  /// `bg-red-950/60 hover:bg-red-900/80` — Logout, Delete.
  danger,

  /// `bg-red-800 hover:bg-red-700` — Delete Forever.
  dangerStrong,
}

class AppButton extends StatefulWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.icon,
    this.fullWidth = false,
    this.compact = false,
    this.enabled = true,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final IconData? icon;
  final bool fullWidth;
  final bool compact;
  final bool enabled;

  @override
  State<AppButton> createState() => _AppButtonState();
}

class _AppButtonState extends State<AppButton> {
  bool _hovering = false;

  ({Color bg, Color border, Color fg}) _palette() {
    switch (widget.variant) {
      case AppButtonVariant.primary:
        return (
          bg: _hovering ? AppColors.amber700 : AppColors.amber800,
          border: AppColors.amber700.withValues(alpha: 0.5),
          fg: AppColors.amber100,
        );
      case AppButtonVariant.primaryStrong:
        return (
          bg: _hovering ? AppColors.amber600 : AppColors.amber700,
          border: AppColors.amber600.withValues(alpha: 0.5),
          fg: Colors.white,
        );
      case AppButtonVariant.secondary:
        return (
          bg: _hovering ? AppColors.slate700 : AppColors.slate800,
          border: AppColors.slate700.withValues(alpha: 0.6),
          fg: AppColors.textBody,
        );
      case AppButtonVariant.ghost:
        return (
          bg: _hovering
              ? AppColors.slate800.withValues(alpha: 0.5)
              : Colors.transparent,
          border: Colors.transparent,
          fg: _hovering ? AppColors.textBody : AppColors.textMuted,
        );
      case AppButtonVariant.danger:
        return (
          bg: _hovering
              ? AppColors.red900.withValues(alpha: 0.8)
              : AppColors.red950.withValues(alpha: 0.6),
          border: AppColors.red900.withValues(alpha: 0.5),
          fg: AppColors.red400,
        );
      case AppButtonVariant.dangerStrong:
        return (
          bg: _hovering ? AppColors.red700 : AppColors.red800,
          border: AppColors.red700.withValues(alpha: 0.5),
          fg: Colors.white,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = _palette();
    final disabled = !widget.enabled || widget.onPressed == null;
    final horizontalPad = widget.compact ? AppSpacing.md : AppSpacing.lg;
    final verticalPad = widget.compact ? AppSpacing.sm : AppSpacing.smPlus;

    Widget content = Row(
      mainAxisSize: widget.fullWidth ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (widget.icon != null) ...[
          Icon(widget.icon, size: 16, color: p.fg),
          const SizedBox(width: AppSpacing.sm),
        ],
        Text(widget.label, style: AppTypography.bodyMedium.copyWith(color: p.fg)),
      ],
    );

    final button = AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      curve: Curves.easeOut,
      decoration: BoxDecoration(
        color: disabled ? p.bg.withValues(alpha: 0.4) : p.bg,
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
        border: Border.all(color: p.border),
      ),
      padding: EdgeInsets.symmetric(
        horizontal: horizontalPad,
        vertical: verticalPad,
      ),
      child: content,
    );

    return MouseRegion(
      cursor: disabled
          ? SystemMouseCursors.basic
          : SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: disabled ? null : widget.onPressed,
        child: Opacity(opacity: disabled ? 0.4 : 1, child: button),
      ),
    );
  }
}

/// Tiny icon button used in the header rows (refresh, install, phone, cog).
/// `bg-slate-800 hover:bg-slate-700` + colour-shift on the icon.
class AppIconButton extends StatefulWidget {
  const AppIconButton({
    super.key,
    required this.icon,
    required this.tooltip,
    this.onPressed,
    this.hoverColor = AppColors.amber400,
  });

  final IconData icon;
  final String tooltip;
  final VoidCallback? onPressed;
  final Color hoverColor;

  @override
  State<AppIconButton> createState() => _AppIconButtonState();
}

class _AppIconButtonState extends State<AppIconButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: widget.tooltip,
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        onEnter: (_) => setState(() => _hovering = true),
        onExit: (_) => setState(() => _hovering = false),
        child: GestureDetector(
          onTap: widget.onPressed,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            curve: Curves.easeOut,
            decoration: BoxDecoration(
              color: _hovering ? AppColors.slate700 : AppColors.slate800,
              borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
              border: Border.all(
                color: AppColors.slate700.withValues(alpha: 0.6),
              ),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.smPlus,
              vertical: AppSpacing.xxs,
            ),
            child: Icon(
              widget.icon,
              size: 16,
              color: _hovering ? widget.hoverColor : AppColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}
