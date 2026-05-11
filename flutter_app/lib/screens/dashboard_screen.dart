import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../api/clients.dart';
import '../api/models/world_models.dart';
import '../routing/router.dart';
import '../state/auth_provider.dart';
import '../state/world_provider.dart';
import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';
import '../widgets/app_button.dart';
import '../widgets/clover_loader.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Column(
        children: [
          const _DashboardHeader(),
          Expanded(
            child: SingleChildScrollView(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1024),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.xl,
                    vertical: AppSpacing.xl2,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      _ApiKeyBanner(),
                      SizedBox(height: AppSpacing.xl3),
                      _SectionTitle(label: 'All Worlds'),
                      SizedBox(height: AppSpacing.base),
                      _WorldsList(),
                      SizedBox(height: AppSpacing.xl3),
                      _SectionTitle(label: 'Create New World'),
                      SizedBox(height: AppSpacing.base),
                      _CreateWorldCta(),
                    ],
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

class _DashboardHeader extends ConsumerWidget {
  const _DashboardHeader();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
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
          constraints: const BoxConstraints(maxWidth: 1024),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ayen-Ode',
                      style: AppTypography.headerSmall.copyWith(
                        letterSpacing: -0.02,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'World Dashboard',
                      style: AppTypography.xs.copyWith(
                        color: AppColors.textVeryMuted,
                      ),
                    ),
                  ],
                ),
              ),
              AppIconButton(
                icon: Icons.settings_outlined,
                tooltip: 'Settings',
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => const _SettingsModalStub(),
                  );
                },
              ),
              const SizedBox(width: AppSpacing.sm),
              AppButton(
                label: 'Logout',
                variant: AppButtonVariant.danger,
                onPressed: () async {
                  await ref.read(authControllerProvider.notifier).signOut();
                  if (!context.mounted) return;
                  context.go(AppRoutes.login);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ApiKeyBanner extends ConsumerWidget {
  const _ApiKeyBanner();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = ref.watch(settingsStatusProvider);
    return status.when(
      data: (s) {
        if (s.apiKeyConfigured) return const SizedBox.shrink();
        return Container(
          decoration: BoxDecoration(
            color: AppColors.amber950.withValues(alpha: 0.4),
            borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
            border: Border.all(
              color: AppColors.amber800.withValues(alpha: 0.6),
            ),
          ),
          padding: const EdgeInsets.all(AppSpacing.base),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.amber900.withValues(alpha: 0.7),
                ),
                alignment: Alignment.center,
                child: const Icon(
                  Icons.warning_amber_rounded,
                  size: 16,
                  color: AppColors.amber300,
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Anthropic API key not configured',
                      style: AppTypography.bodyMedium.copyWith(
                        color: AppColors.amber200,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Open Settings to add your key. Worlds and narrative will fail without it.',
                      style: AppTypography.xs.copyWith(
                        color: AppColors.amber400.withValues(alpha: 0.7),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              AppButton(
                label: 'Open Settings',
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => const _SettingsModalStub(),
                  );
                },
              ),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, _) => const SizedBox.shrink(),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 2,
          height: 16,
          decoration: BoxDecoration(
            color: AppColors.slate600,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: AppSpacing.smPlus),
        Text(
          label.toUpperCase(),
          style: AppTypography.sectionLabel,
        ),
      ],
    );
  }
}

class _WorldsList extends ConsumerWidget {
  const _WorldsList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final worlds = ref.watch(worldsListProvider);
    return worlds.when(
      loading: () => Row(
        children: [
          const CloverLoader(size: 28, hue: 142),
          const SizedBox(width: AppSpacing.md),
          Text('Loading…', style: AppTypography.body.copyWith(color: AppColors.textVeryMuted)),
        ],
      ),
      error: (e, _) => Text(
        'Could not load worlds: $e',
        style: AppTypography.body.copyWith(color: AppColors.red400),
      ),
      data: (list) {
        if (list.isEmpty) {
          return Text(
            'No worlds yet. Create one below.',
            style: AppTypography.body.copyWith(color: AppColors.textVeryMuted),
          );
        }
        return LayoutBuilder(
          builder: (context, constraints) {
            final cols = constraints.maxWidth >= 900
                ? 3
                : (constraints.maxWidth >= 600 ? 2 : 1);
            return GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: cols,
                crossAxisSpacing: AppSpacing.base,
                mainAxisSpacing: AppSpacing.base,
                mainAxisExtent: 180,
              ),
              itemCount: list.length,
              itemBuilder: (context, i) => _WorldCard(world: list[i]),
            );
          },
        );
      },
    );
  }
}

class _WorldCard extends ConsumerWidget {
  const _WorldCard({required this.world});
  final World world;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isActive = world.status == 'active';
    final premise = world.premise ?? '';
    final premiseSnip = premise.length > 80 ? '${premise.substring(0, 80)}…' : premise;

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        border: Border.all(
          color: isActive
              ? AppColors.amber900.withValues(alpha: 0.4)
              : AppColors.slate800,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  world.name,
                  overflow: TextOverflow.ellipsis,
                  style: AppTypography.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (isActive) ...[
                const SizedBox(width: AppSpacing.sm),
                Container(
                  decoration: BoxDecoration(
                    color: AppColors.emerald950,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(
                      color: AppColors.emerald800.withValues(alpha: 0.5),
                    ),
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.xxs,
                    vertical: 1,
                  ),
                  child: Text(
                    'active',
                    style: AppTypography.xs.copyWith(color: AppColors.emerald400),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: AppSpacing.xs),
          Expanded(
            child: Text(
              premiseSnip,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: AppTypography.xs.copyWith(color: AppColors.textMuted),
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          const Divider(),
          const SizedBox(height: AppSpacing.sm),
          Row(
            children: [
              Expanded(
                child: isActive
                    ? AppButton(
                        label: 'Enter →',
                        variant: AppButtonVariant.primary,
                        compact: true,
                        fullWidth: true,
                        onPressed: () => context.go(
                          '${AppRoutes.narrative}?world_id=${world.worldId}&fresh=1',
                        ),
                      )
                    : AppButton(
                        label: 'Switch',
                        variant: AppButtonVariant.secondary,
                        compact: true,
                        fullWidth: true,
                        onPressed: () async {
                          await ref
                              .read(worldApiProvider)
                              .switchWorld(world.worldId);
                          ref.invalidate(worldsListProvider);
                          ref.invalidate(activeWorldProvider);
                        },
                      ),
              ),
              const SizedBox(width: AppSpacing.sm),
              AppButton(
                label: 'Reset',
                variant: AppButtonVariant.danger,
                compact: true,
                onPressed: () => _confirmReset(context, ref, world),
              ),
              const SizedBox(width: AppSpacing.sm),
              AppButton(
                label: 'Delete',
                variant: AppButtonVariant.danger,
                compact: true,
                onPressed: () => _confirmDelete(context, ref, world),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _confirmReset(
    BuildContext context,
    WidgetRef ref,
    World world,
  ) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => _ConfirmDialog(
        title: 'Reset World',
        message:
            'All story progress, entities, and investigations will be wiped. '
            'The opening scene and world details are kept.',
        confirmLabel: 'Reset',
        confirmVariant: AppButtonVariant.primary,
        accent: AppColors.amber700,
      ),
    );
    if (ok == true && context.mounted) {
      await ref.read(worldApiProvider).reset(world.worldId);
      ref.invalidate(worldsListProvider);
    }
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    World world,
  ) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => _ConfirmDialog(
        title: 'Delete World',
        message: 'Permanently delete "${world.name}"? '
            'This cannot be undone. All world data will be destroyed forever.',
        confirmLabel: 'Delete Forever',
        confirmVariant: AppButtonVariant.dangerStrong,
        accent: AppColors.red800,
      ),
    );
    if (ok == true && context.mounted) {
      await ref.read(worldApiProvider).delete(world.worldId);
      ref.invalidate(worldsListProvider);
    }
  }
}

class _CreateWorldCta extends StatelessWidget {
  const _CreateWorldCta();

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.go(AppRoutes.createWorld),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
              border: Border.all(color: AppColors.slate800),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.2),
                  blurRadius: 20,
                ),
              ],
            ),
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.amber950.withValues(alpha: 0.6),
                    border: Border.all(
                      color: AppColors.amber900.withValues(alpha: 0.4),
                    ),
                  ),
                  alignment: Alignment.center,
                  child: Icon(
                    Icons.add,
                    size: 20,
                    color: AppColors.amber500.withValues(alpha: 0.7),
                  ),
                ),
                const SizedBox(width: AppSpacing.lg),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Forge a new world',
                        style: AppTypography.bodyMedium.copyWith(
                          color: AppColors.slate200,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Name it, set the tone, write the premise, choose your role — guided step by step.',
                        style: AppTypography.body.copyWith(
                          color: AppColors.textVeryMuted,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.chevron_right,
                  color: AppColors.slate700,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ConfirmDialog extends StatelessWidget {
  const _ConfirmDialog({
    required this.title,
    required this.message,
    required this.confirmLabel,
    required this.confirmVariant,
    required this.accent,
  });

  final String title;
  final String message;
  final String confirmLabel;
  final AppButtonVariant confirmVariant;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        side: BorderSide(color: accent.withValues(alpha: 0.4)),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 384),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.xl,
                vertical: AppSpacing.base,
              ),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  title,
                  style: AppTypography.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
            const Divider(),
            Padding(
              padding: const EdgeInsets.all(AppSpacing.xl),
              child: Text(
                message,
                style: AppTypography.body,
              ),
            ),
            const Divider(),
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.xl,
                vertical: AppSpacing.md,
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  AppButton(
                    label: 'Cancel',
                    variant: AppButtonVariant.ghost,
                    onPressed: () => Navigator.pop(context, false),
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  AppButton(
                    label: confirmLabel,
                    variant: confirmVariant,
                    onPressed: () => Navigator.pop(context, true),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Minimal in-app settings dialog — full UX from the web's settings modal
/// (with the phone-access section) is too large to fit in this phase. The
/// stub still covers the audit's "in-app settings" surface: API key + login
/// credentials + port + fullscreen toggle.
class _SettingsModalStub extends ConsumerStatefulWidget {
  const _SettingsModalStub();

  @override
  ConsumerState<_SettingsModalStub> createState() => _SettingsModalStubState();
}

class _SettingsModalStubState extends ConsumerState<_SettingsModalStub> {
  final _apiKey = TextEditingController();
  final _username = TextEditingController();
  final _password = TextEditingController();
  final _port = TextEditingController();
  bool _loading = true;
  bool _saving = false;
  String? _status;
  String? _maskedKey;
  bool _keySet = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _apiKey.dispose();
    _username.dispose();
    _password.dispose();
    _port.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final settings = await ref.read(settingsApiProvider).get();
      if (!mounted) return;
      setState(() {
        _maskedKey = settings.anthropicApiKeyMasked;
        _keySet = settings.anthropicApiKeySet;
        _username.text = settings.appUsername ?? '';
        _port.text = settings.ayenOdePort ?? '';
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _status = 'Could not load settings';
      });
    }
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _status = 'Saving…';
    });
    final payload = <String, dynamic>{};
    if (_apiKey.text.trim().isNotEmpty) {
      payload['ANTHROPIC_API_KEY'] = _apiKey.text.trim();
    }
    if (_username.text.trim().isNotEmpty) {
      payload['APP_USERNAME'] = _username.text.trim();
    }
    if (_password.text.isNotEmpty) {
      payload['APP_PASSWORD'] = _password.text;
    }
    if (_port.text.trim().isNotEmpty) {
      payload['AYEN_ODE_PORT'] = _port.text.trim();
    }
    try {
      await ref.read(settingsApiProvider).save(payload);
      if (!mounted) return;
      ref.invalidate(settingsStatusProvider);
      setState(() {
        _saving = false;
        _status = 'Saved. Restart to apply API key changes.';
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _saving = false;
        _status = 'Save failed: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        side: const BorderSide(color: AppColors.slate700),
      ),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 512, maxHeight: 720),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.xl,
                vertical: AppSpacing.base,
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Settings',
                      style: AppTypography.bodyMedium.copyWith(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 16),
                    color: AppColors.textVeryMuted,
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            const Divider(),
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppSpacing.xl),
                child: _loading
                    ? const Center(child: CloverLoader(size: 32, hue: 142))
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _field('Anthropic API Key', _apiKey,
                              obscure: true,
                              placeholder: _maskedKey ?? 'sk-ant-…',
                              hint: _keySet
                                  ? 'A key is already saved. Type a new one to replace it, or leave blank to keep it.'
                                  : 'Required for narrative actions.'),
                          const SizedBox(height: AppSpacing.lg),
                          _field('Login Username', _username,
                              placeholder: '(optional)'),
                          const SizedBox(height: AppSpacing.lg),
                          _field('Login Password', _password,
                              obscure: true,
                              placeholder: '(unchanged)'),
                          const SizedBox(height: AppSpacing.lg),
                          _field('Server Port', _port,
                              placeholder: '8000',
                              hint:
                                  'Default 8000. Restart required to change.'),
                        ],
                      ),
              ),
            ),
            const Divider(),
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.xl,
                vertical: AppSpacing.md,
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      _status ?? '',
                      style: AppTypography.hint,
                    ),
                  ),
                  AppButton(
                    label: 'Cancel',
                    variant: AppButtonVariant.ghost,
                    onPressed: () => Navigator.pop(context),
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  AppButton(
                    label: 'Save',
                    variant: AppButtonVariant.primary,
                    onPressed: _saving ? null : _save,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _field(
    String label,
    TextEditingController c, {
    bool obscure = false,
    String? placeholder,
    String? hint,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label.toUpperCase(), style: AppTypography.metadata),
        const SizedBox(height: AppSpacing.xs),
        TextField(
          controller: c,
          obscureText: obscure,
          style: AppTypography.body.copyWith(color: AppColors.textPrimary),
          decoration: InputDecoration(
            hintText: placeholder,
            hintStyle: AppTypography.body.copyWith(color: AppColors.textVeryMuted),
            filled: true,
            fillColor: AppColors.slate950,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.md,
              vertical: AppSpacing.sm,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
              borderSide: const BorderSide(color: AppColors.slate700),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
              borderSide: const BorderSide(color: AppColors.slate700),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
              borderSide: const BorderSide(color: AppColors.amber600),
            ),
          ),
        ),
        if (hint != null) ...[
          const SizedBox(height: AppSpacing.xs),
          Text(hint, style: AppTypography.hint),
        ],
      ],
    );
  }
}
