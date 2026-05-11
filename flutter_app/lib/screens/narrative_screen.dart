import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../api/clients.dart';
import '../api/models/entity_models.dart';
import '../api/models/narrative_models.dart';
import '../api/models/world_models.dart';
import '../routing/router.dart';
import '../state/auth_provider.dart';
import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';
import '../widgets/app_button.dart';
import '../widgets/clover_loader.dart';

/// Narrative play screen.
///
/// v0.1 scope: load the world, render conversation history, submit actions,
/// show the IP counter pill, render the right-rail quest + compendium
/// panels, render the top-edge investigation trigger. The polished
/// behaviours from design-audit.md §1.4 / §8 that are deferred:
///
///   * Investigation panel polling + timer + auto-close. The trigger zone
///     is wired so we can ship that next.
///   * Opening-scene typewriter intro + skip button.
///   * Entity reference linkification + `<investigate …>` tag parsing.
///   * Worlds-modal switcher (the dashboard handles that for now).
///   * Mobile bottom-sheet drawer for the side rails (desktop layout only).
///
/// Each deferred behaviour is logged inline with a `// TODO(audit-§…)`
/// pointer so the next pass can pick them up.
class NarrativeScreen extends ConsumerStatefulWidget {
  const NarrativeScreen({super.key, this.worldId, this.fresh = false});

  final String? worldId;
  final bool fresh;

  @override
  ConsumerState<NarrativeScreen> createState() => _NarrativeScreenState();
}

class _NarrativeScreenState extends ConsumerState<NarrativeScreen> {
  final _input = TextEditingController();
  final _scrollController = ScrollController();
  final _history = <ConversationMessage>[];

  World? _world;
  List<Entity> _entities = const [];
  String? _handoff;
  bool _loading = true;
  bool _submitting = false;
  String? _loadError;

  int _ip = 5;
  int _maxIp = 5;
  String? _timeLabel;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  @override
  void dispose() {
    _input.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    final wid = widget.worldId;
    if (wid == null) {
      // Mirror the web's behaviour: try the active world if no id in the URL.
      try {
        final active = await ref.read(worldApiProvider).active();
        if (active.world == null) {
          setState(() {
            _loading = false;
            _loadError = 'No active world. Create one first.';
          });
          return;
        }
        await _loadWorld(active.world!.worldId);
      } catch (e) {
        if (mounted) {
          setState(() {
            _loading = false;
            _loadError = '$e';
          });
        }
      }
      return;
    }
    await _loadWorld(wid);
  }

  Future<void> _loadWorld(String worldId) async {
    setState(() {
      _loading = true;
      _loadError = null;
    });
    try {
      final api = ref.read(worldApiProvider);
      final detail = await api.fetch(worldId);
      final currency = await api.currency(worldId);
      if (!mounted) return;
      setState(() {
        _world = detail.world;
        _entities = detail.entities;
        _handoff = detail.handoff;
        _ip = currency.balance > 0 ? currency.balance : currency.points;
        _maxIp =
            currency.maxBalance > 0 ? currency.maxBalance : currency.maxPoints;
        _loading = false;
      });
      // Best-effort time fetch — non-critical.
      try {
        final t = await api.time(worldId);
        if (!mounted) return;
        setState(() => _timeLabel = t.label);
      } catch (_) {}
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _loadError = '$e';
      });
    }
  }

  Future<void> _submit() async {
    final action = _input.text.trim();
    final world = _world;
    if (action.isEmpty || world == null) return;

    setState(() {
      _history.add(ConversationMessage(role: 'user', content: action));
      _submitting = true;
      _input.clear();
    });
    _scrollToBottom();

    try {
      final api = ref.read(narrativeApiProvider);
      final res = await api.submit(NarrativeRequest(
        worldId: world.worldId,
        action: action,
        history: List<ConversationMessage>.from(_history),
      ));
      if (!mounted) return;
      setState(() {
        _history
          ..clear()
          ..addAll(res.history.isNotEmpty
              ? res.history
              : [
                  ..._history,
                  ConversationMessage(role: 'assistant', content: res.narrative),
                ]);
        if (res.investigationPoints != null) _ip = res.investigationPoints!;
        if (res.maxInvestigationPoints != null) {
          _maxIp = res.maxInvestigationPoints!;
        }
        if (res.gameTime?.label != null) _timeLabel = res.gameTime!.label;
        _submitting = false;
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _history.add(ConversationMessage(
          role: 'assistant',
          content: '⚠ Error: $e',
        ));
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        backgroundColor: AppColors.bg,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CloverLoader(size: 60, hue: 142),
              const SizedBox(height: AppSpacing.base),
              Text('Loading world…',
                  style: AppTypography.body.copyWith(color: AppColors.textMuted)),
            ],
          ),
        ),
      );
    }
    if (_loadError != null) {
      return Scaffold(
        backgroundColor: AppColors.bg,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.xl2),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(_loadError!,
                    style:
                        AppTypography.body.copyWith(color: AppColors.red400)),
                const SizedBox(height: AppSpacing.lg),
                AppButton(
                  label: '← Dashboard',
                  variant: AppButtonVariant.secondary,
                  onPressed: () => context.go(AppRoutes.dashboard),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final isMobile = MediaQuery.of(context).size.width <= AppSpacing.mobileBreakpoint;

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: Stack(
        children: [
          Column(
            children: [
              _NarrativeHeader(
                world: _world!,
                ip: _ip,
                maxIp: _maxIp,
                onHome: () => context.go(AppRoutes.dashboard),
                onLogout: () async {
                  await ref.read(authControllerProvider.notifier).signOut();
                  if (!context.mounted) return;
                  context.go(AppRoutes.login);
                },
              ),
              Expanded(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 1280),
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.base),
                      child: isMobile
                          ? _NarrativePane(
                              scrollController: _scrollController,
                              history: _history,
                              handoff: _handoff,
                              input: _input,
                              submitting: _submitting,
                              timeLabel: _timeLabel,
                              onSubmit: _submit,
                            )
                          : Row(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                Expanded(
                                  child: _NarrativePane(
                                    scrollController: _scrollController,
                                    history: _history,
                                    handoff: _handoff,
                                    input: _input,
                                    submitting: _submitting,
                                    timeLabel: _timeLabel,
                                    onSubmit: _submit,
                                  ),
                                ),
                                const SizedBox(width: AppSpacing.base),
                                _QuestPanel(worldId: _world!.worldId),
                                const SizedBox(width: AppSpacing.base),
                                _CompendiumPanel(entities: _entities),
                              ],
                            ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          // Top-edge investigation trigger zone (desktop: centered 35%).
          // TODO(audit-§1.4/§8): wire to investigation polling + panel drop.
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Center(
              child: FractionallySizedBox(
                widthFactor: isMobile ? 1.0 : 0.35,
                child: Container(
                  height: 6,
                  decoration: BoxDecoration(
                    color: AppColors.amber600.withValues(alpha: 0.3),
                    borderRadius: const BorderRadius.vertical(
                      bottom: Radius.circular(6),
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

class _NarrativeHeader extends StatelessWidget {
  const _NarrativeHeader({
    required this.world,
    required this.ip,
    required this.maxIp,
    required this.onHome,
    required this.onLogout,
  });

  final World world;
  final int ip;
  final int maxIp;
  final VoidCallback onHome;
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
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
          constraints: const BoxConstraints(maxWidth: 1280),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      world.name,
                      style: AppTypography.header.copyWith(
                        color: AppColors.slate100,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    if ((world.premise ?? '').isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        world.premise!,
                        style: AppTypography.body.copyWith(
                          color: AppColors.textMuted,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              _IpPill(ip: ip, maxIp: maxIp),
              const SizedBox(width: AppSpacing.sm),
              AppButton(
                label: 'Home',
                variant: AppButtonVariant.secondary,
                compact: true,
                onPressed: onHome,
              ),
              const SizedBox(width: AppSpacing.sm),
              AppButton(
                label: 'Logout',
                variant: AppButtonVariant.danger,
                compact: true,
                onPressed: onLogout,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _IpPill extends StatelessWidget {
  const _IpPill({required this.ip, required this.maxIp});
  final int ip;
  final int maxIp;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.amber950.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
        border: Border.all(
          color: AppColors.amber800.withValues(alpha: 0.5),
        ),
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xxs,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.search,
              size: 14,
              color: AppColors.amber300.withValues(alpha: 0.7)),
          const SizedBox(width: AppSpacing.xs),
          Text(
            '$ip/$maxIp',
            style: AppTypography.mono.copyWith(color: AppColors.amber300),
          ),
        ],
      ),
    );
  }
}

class _NarrativePane extends StatelessWidget {
  const _NarrativePane({
    required this.scrollController,
    required this.history,
    required this.handoff,
    required this.input,
    required this.submitting,
    required this.timeLabel,
    required this.onSubmit,
  });

  final ScrollController scrollController;
  final List<ConversationMessage> history;
  final String? handoff;
  final TextEditingController input;
  final bool submitting;
  final String? timeLabel;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        border: Border.all(color: AppColors.slate800),
      ),
      child: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              controller: scrollController,
              padding: const EdgeInsets.all(AppSpacing.xl),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Opening handoff (if any) + history.
                  // TODO(audit-§4.4 step 1): typewriter intro on fresh entry.
                  if (history.isEmpty && (handoff ?? '').isNotEmpty)
                    _NarrativeBlock(content: handoff!),
                  for (final msg in history)
                    msg.role == 'user'
                        ? _UserBlock(content: msg.content)
                        : _NarrativeBlock(content: msg.content),
                  if (history.isEmpty &&
                      (handoff ?? '').isEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(
                        vertical: AppSpacing.xl3,
                      ),
                      child: Text(
                        'Ready to explore…',
                        textAlign: TextAlign.center,
                        style: AppTypography.body.copyWith(
                          color: AppColors.textVeryMuted,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          _InputBar(
            controller: input,
            submitting: submitting,
            timeLabel: timeLabel,
            onSubmit: onSubmit,
          ),
        ],
      ),
    );
  }
}

class _NarrativeBlock extends StatelessWidget {
  const _NarrativeBlock({required this.content});
  final String content;

  @override
  Widget build(BuildContext context) {
    final paragraphs = content
        .split('\n')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final p in paragraphs)
            Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.md),
              // TODO(audit-§8): parse `<investigate …>` tags + linkify
              // entity refs.
              child: Text(p, style: AppTypography.narrative),
            ),
        ],
      ),
    );
  }
}

class _UserBlock extends StatelessWidget {
  const _UserBlock({required this.content});
  final String content;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.lg),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.blue950.withValues(alpha: 0.1),
          borderRadius: const BorderRadius.only(
            topRight: Radius.circular(AppSpacing.radiusLg),
            bottomRight: Radius.circular(AppSpacing.radiusLg),
          ),
          border: const Border(
            left: BorderSide(color: AppColors.blue600, width: 2),
          ),
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.base,
          vertical: AppSpacing.sm,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'YOU',
              style: AppTypography.xs.copyWith(
                color: AppColors.blue500,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              content,
              style: AppTypography.body.copyWith(
                color: AppColors.slate300,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  const _InputBar({
    required this.controller,
    required this.submitting,
    required this.timeLabel,
    required this.onSubmit,
  });

  final TextEditingController controller;
  final bool submitting;
  final String? timeLabel;
  final VoidCallback onSubmit;

  static const _quickChips = [
    'Look around',
    'Wait',
    'Examine ',
    'Speak to ',
    'Search ',
  ];

  void _setText(String text) {
    controller.text = text;
    controller.selection =
        TextSelection.collapsed(offset: controller.text.length);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.slate950.withValues(alpha: 0.4),
        border: const Border(top: BorderSide(color: AppColors.slate800)),
      ),
      padding: const EdgeInsets.all(AppSpacing.base),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Wrap(
            spacing: AppSpacing.xxs,
            runSpacing: AppSpacing.xs,
            children: [
              for (final chip in _quickChips)
                _QuickChip(label: chip.trim(), onTap: () => _setText(chip)),
            ],
          ),
          const SizedBox(height: AppSpacing.smPlus),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Expanded(
                child: TextField(
                  controller: controller,
                  maxLines: 6,
                  minLines: 1,
                  enabled: !submitting,
                  onSubmitted: (_) => onSubmit(),
                  style: AppTypography.body.copyWith(
                    color: Colors.white,
                    height: 1.5,
                  ),
                  decoration: InputDecoration(
                    hintText: 'What do you do?',
                    hintStyle: AppTypography.body.copyWith(
                      color: AppColors.textVeryMuted,
                    ),
                    filled: true,
                    fillColor: AppColors.slate800,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.base,
                      vertical: AppSpacing.smPlus,
                    ),
                    border: OutlineInputBorder(
                      borderRadius:
                          BorderRadius.circular(AppSpacing.radiusLg),
                      borderSide: BorderSide(
                        color: AppColors.slate700.withValues(alpha: 0.7),
                      ),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius:
                          BorderRadius.circular(AppSpacing.radiusLg),
                      borderSide: BorderSide(
                        color: AppColors.slate700.withValues(alpha: 0.7),
                      ),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius:
                          BorderRadius.circular(AppSpacing.radiusLg),
                      borderSide: BorderSide(
                        color: AppColors.amber600.withValues(alpha: 0.6),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  SizedBox(
                    height: 16,
                    child: timeLabel == null
                        ? const SizedBox.shrink()
                        : Text(
                            timeLabel!,
                            style: AppTypography.xs.copyWith(
                              color: AppColors.textVeryMuted,
                            ),
                          ),
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  AppButton(
                    label: submitting ? '…' : 'Act',
                    variant: AppButtonVariant.primary,
                    onPressed: submitting ? null : onSubmit,
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Text(
            'Enter to send · Shift+Enter for new line',
            style: AppTypography.xs.copyWith(color: AppColors.slate700),
          ),
        ],
      ),
    );
  }
}

class _QuickChip extends StatefulWidget {
  const _QuickChip({required this.label, required this.onTap});
  final String label;
  final VoidCallback onTap;

  @override
  State<_QuickChip> createState() => _QuickChipState();
}

class _QuickChipState extends State<_QuickChip> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.xs + 5,
            vertical: 2,
          ),
          decoration: BoxDecoration(
            color: _hover
                ? AppColors.slate700.withValues(alpha: 0.8)
                : AppColors.slate800.withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            border: Border.all(
              color: _hover
                  ? AppColors.slate500.withValues(alpha: 0.5)
                  : AppColors.slate500.withValues(alpha: 0.25),
            ),
          ),
          child: Text(
            widget.label,
            style: AppTypography.xs.copyWith(
              color: _hover ? AppColors.slate300 : AppColors.slate400,
            ),
          ),
        ),
      ),
    );
  }
}

class _QuestPanel extends ConsumerWidget {
  const _QuestPanel({required this.worldId});
  final String worldId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SizedBox(
      width: AppSpacing.railWidth,
      child: FutureBuilder(
        future: ref.read(worldApiProvider).quests(worldId),
        builder: (context, snap) {
          return Container(
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
              border: Border.all(color: AppColors.slate800),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.base,
                    vertical: AppSpacing.md,
                  ),
                  decoration: const BoxDecoration(
                    border: Border(
                      bottom: BorderSide(color: AppColors.slate800),
                    ),
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 2,
                        height: 16,
                        decoration: BoxDecoration(
                          color: AppColors.purple600,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: AppSpacing.smPlus),
                      Text(
                        'Current Goals',
                        style: AppTypography.bodyMedium.copyWith(
                          color: AppColors.slate200,
                        ),
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.base,
                    vertical: AppSpacing.base,
                  ),
                  child: snap.connectionState != ConnectionState.done
                      ? Text(
                          'Loading goals…',
                          style: AppTypography.xs.copyWith(
                            color: AppColors.textVeryMuted,
                          ),
                        )
                      : (snap.data?.quests.isEmpty ?? true)
                          ? Text(
                              'No active goals yet.',
                              style: AppTypography.xs.copyWith(
                                color: AppColors.textVeryMuted,
                              ),
                            )
                          : Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                for (final q in snap.data!.quests)
                                  Padding(
                                    padding: const EdgeInsets.only(
                                      bottom: AppSpacing.md,
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          q.title,
                                          style: AppTypography.xs.copyWith(
                                            color: AppColors.slate200,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        if (q.description != null)
                                          Padding(
                                            padding: const EdgeInsets.only(
                                              top: 2,
                                            ),
                                            child: Text(
                                              q.description!,
                                              style: AppTypography.xs.copyWith(
                                                color: AppColors.textMuted,
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _CompendiumPanel extends StatelessWidget {
  const _CompendiumPanel({required this.entities});
  final List<Entity> entities;

  @override
  Widget build(BuildContext context) {
    final byType = <String, List<Entity>>{};
    for (final e in entities) {
      final t = e.entityType ?? e.type ?? 'unknown';
      byType.putIfAbsent(t, () => []).add(e);
    }

    const typeOrder = ['character', 'location', 'faction', 'object', 'event'];
    const typeColor = {
      'character': AppColors.blue400,
      'location': AppColors.emerald400,
      'faction': AppColors.purple400,
      'object': AppColors.orange400,
      'event': AppColors.red400,
    };

    return SizedBox(
      width: AppSpacing.railWidth,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
          border: Border.all(color: AppColors.slate800),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.base,
                vertical: AppSpacing.md,
              ),
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: AppColors.slate800),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 2,
                    height: 16,
                    decoration: BoxDecoration(
                      color: AppColors.amber600,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.smPlus),
                  Text(
                    'Compendium',
                    style: AppTypography.bodyMedium.copyWith(
                      color: AppColors.slate200,
                    ),
                  ),
                ],
              ),
            ),
            if (entities.isEmpty)
              Padding(
                padding: const EdgeInsets.all(AppSpacing.base),
                child: Text(
                  'No entities yet. They will appear as the story unfolds.',
                  style: AppTypography.xs.copyWith(
                    color: AppColors.textVeryMuted,
                  ),
                ),
              )
            else
              Flexible(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(AppSpacing.sm),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (final type in typeOrder)
                        if (byType[type]?.isNotEmpty ?? false) ...[
                          Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: AppSpacing.sm,
                              vertical: AppSpacing.xs,
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 6,
                                  height: 6,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: typeColor[type] ?? AppColors.slate500,
                                  ),
                                ),
                                const SizedBox(width: AppSpacing.sm),
                                Text(
                                  '${type[0].toUpperCase()}${type.substring(1)}s'.toUpperCase(),
                                  style: AppTypography.xs.copyWith(
                                    color: typeColor[type] ?? AppColors.slate400,
                                    fontWeight: FontWeight.w600,
                                    letterSpacing: 1.4,
                                  ),
                                ),
                                const SizedBox(width: AppSpacing.xs),
                                Text(
                                  '${byType[type]!.length}',
                                  style: AppTypography.xs.copyWith(
                                    color: AppColors.slate700,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          for (final e in byType[type]!)
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: AppSpacing.sm,
                                vertical: 2,
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    width: 4,
                                    height: 4,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: (typeColor[type] ??
                                              AppColors.slate500)
                                          .withValues(alpha: 0.4),
                                    ),
                                  ),
                                  const SizedBox(width: AppSpacing.sm),
                                  Expanded(
                                    child: Text(
                                      e.name,
                                      overflow: TextOverflow.ellipsis,
                                      style: AppTypography.body.copyWith(
                                        color: AppColors.slate200,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                        ],
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
