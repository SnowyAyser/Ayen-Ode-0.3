import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../routing/router.dart';
import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';
import '../widgets/app_button.dart';

/// Phone access / Cloudflare-Tunnel page.
///
/// Mirrors `static/settings.html` at a structural level — full implementation
/// of the Cloudflare-login + tunnel-start + QR-install dance is deferred. For
/// v0.1, this is a placeholder that links back to the dashboard.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Column(
        children: [
          Container(
            decoration: const BoxDecoration(
              color: AppColors.surface,
              border: Border(bottom: BorderSide(color: AppColors.slate800)),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.xl,
              vertical: AppSpacing.base,
            ),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 768),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Phone access',
                            style: AppTypography.headerSmall,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Set up Cloudflare Tunnel + install the phone app',
                            style: AppTypography.xs.copyWith(
                              color: AppColors.textMuted,
                            ),
                          ),
                        ],
                      ),
                    ),
                    AppButton(
                      label: 'Back',
                      variant: AppButtonVariant.secondary,
                      onPressed: () => context.go(AppRoutes.dashboard),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 600),
                child: Padding(
                  padding: const EdgeInsets.all(AppSpacing.xl),
                  child: Container(
                    decoration: BoxDecoration(
                      color: AppColors.slate900.withValues(alpha: 0.7),
                      borderRadius:
                          BorderRadius.circular(AppSpacing.radiusXl),
                      border: Border.all(
                        color: AppColors.slate700.withValues(alpha: 0.7),
                      ),
                    ),
                    padding: const EdgeInsets.all(AppSpacing.xl),
                    child: Text(
                      'Phone access setup will land in a follow-up — the Flutter app on Windows + Android already speaks to the local server directly via the configurable API base URL, so the Cloudflare-Tunnel wiring is no longer the only path to a phone client.',
                      style: AppTypography.body,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
