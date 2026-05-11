import 'package:flutter/material.dart';

import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';

/// Two input styles — login/dashboard (slate-700 fill + blue focus) and
/// wizard (slate-950 fill + amber focus with backdrop blur). The web app
/// uses the wizard style for most "real" form fields; the login screen has
/// its own slightly different look that we mirror via [InputStyle.login].
enum InputStyle { login, wizard }

class AppTextField extends StatelessWidget {
  const AppTextField({
    super.key,
    required this.controller,
    this.placeholder,
    this.obscure = false,
    this.style = InputStyle.wizard,
    this.maxLines = 1,
    this.minLines,
    this.onSubmitted,
    this.autofocus = false,
    this.label,
    this.error,
  });

  final TextEditingController controller;
  final String? placeholder;
  final bool obscure;
  final InputStyle style;
  final int maxLines;
  final int? minLines;
  final ValueChanged<String>? onSubmitted;
  final bool autofocus;
  final String? label;
  final String? error;

  @override
  Widget build(BuildContext context) {
    final isLogin = style == InputStyle.login;
    final focusBorder = isLogin ? AppColors.blue500 : AppColors.amber600;
    final fillColor = isLogin ? AppColors.slate700 : AppColors.slate950;
    final borderColor = isLogin ? AppColors.slate600 : AppColors.slate700;

    final field = TextField(
      controller: controller,
      obscureText: obscure,
      autofocus: autofocus,
      maxLines: obscure ? 1 : maxLines,
      minLines: minLines,
      onSubmitted: onSubmitted,
      style: AppTypography.body.copyWith(color: AppColors.textPrimary),
      decoration: InputDecoration(
        filled: true,
        fillColor: fillColor,
        hintText: placeholder,
        hintStyle: AppTypography.body.copyWith(color: AppColors.textVeryMuted),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.base,
          vertical: AppSpacing.md,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          borderSide: BorderSide(color: borderColor),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          borderSide: BorderSide(color: borderColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          borderSide: BorderSide(color: focusBorder, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          borderSide: const BorderSide(color: AppColors.red700),
        ),
        errorText: error,
      ),
    );

    if (label == null) return field;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label!, style: AppTypography.metadata),
        const SizedBox(height: AppSpacing.xs),
        field,
      ],
    );
  }
}
