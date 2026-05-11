import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../api/clients.dart';
import '../api/models/world_models.dart';
import '../routing/router.dart';
import '../state/world_provider.dart';
import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';
import '../widgets/app_button.dart';
import '../widgets/clover_loader.dart';

/// 4-step world creation wizard, ported from `create-world.html`.
///
/// Implements the slide transition, validation shake, chip selection, and
/// review summary. The web's ambient starfield background is approximated
/// with the same radial-gradient glow — without the per-star canvas
/// twinkle (deferred; not load-bearing).
class CreateWorldScreen extends ConsumerStatefulWidget {
  const CreateWorldScreen({super.key});

  @override
  ConsumerState<CreateWorldScreen> createState() => _CreateWorldScreenState();
}

class _CreateWorldScreenState extends ConsumerState<CreateWorldScreen> {
  static const _total = 4;
  int _step = 0;
  bool _forging = false;
  String? _error;

  final _name = TextEditingController();
  final _theme = TextEditingController();
  final _premise = TextEditingController();
  final _role = TextEditingController();

  static const _toneChips = [
    'Dark fantasy',
    'Political intrigue',
    'Cosmic horror',
    'Solarpunk',
    'Noir mystery',
    'Mythic epic',
    'Fae & folklore',
    'Biopunk',
  ];
  static const _roleChips = [
    'Disgraced knight',
    'Wandering scholar',
    'Exiled heir',
    'Street thief',
    'Court spy',
    'Temple acolyte',
  ];

  String? _shakingField;

  @override
  void dispose() {
    _name.dispose();
    _theme.dispose();
    _premise.dispose();
    _role.dispose();
    super.dispose();
  }

  bool _validateStep() {
    if (_step == 0 && _name.text.trim().isEmpty) {
      setState(() => _shakingField = 'name');
      Future.delayed(const Duration(milliseconds: 400), () {
        if (mounted) setState(() => _shakingField = null);
      });
      return false;
    }
    if (_step == 2 && _premise.text.trim().isEmpty) {
      setState(() => _shakingField = 'premise');
      Future.delayed(const Duration(milliseconds: 400), () {
        if (mounted) setState(() => _shakingField = null);
      });
      return false;
    }
    return true;
  }

  void _next() {
    if (!_validateStep()) return;
    if (_step < _total - 1) setState(() => _step++);
  }

  void _prev() {
    if (_step > 0) setState(() => _step--);
  }

  Future<void> _forge() async {
    if (!_validateStep()) return;
    setState(() {
      _forging = true;
      _error = null;
    });
    try {
      final api = ref.read(worldApiProvider);
      final res = await api.create(
        CreateWorldRequest(
          name: _name.text.trim(),
          premise: _premise.text.trim(),
          themeTone: _theme.text.trim().isEmpty ? null : _theme.text.trim(),
          playerRole: _role.text.trim().isEmpty ? null : _role.text.trim(),
        ),
      );
      ref.invalidate(worldsListProvider);
      if (!mounted) return;
      await Future.delayed(const Duration(milliseconds: 700));
      if (!mounted) return;
      context.go('${AppRoutes.narrative}?world_id=${res.worldId}&fresh=1');
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _forging = false;
        _error = '$e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate950,
      body: Stack(
        children: [
          // Ambient atmosphere — approximates the radial-gradient glow stack
          // from the web's `.bg-glow` layer.
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(-0.7, 0.2),
                  radius: 1.4,
                  colors: [
                    AppColors.amber900.withValues(alpha: 0.18),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0.7, -0.4),
                  radius: 1.2,
                  colors: [
                    AppColors.blue950.withValues(alpha: 0.18),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          // Body
          Column(
            children: [
              _wizardHeader(),
              Expanded(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 512),
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.xl),
                      child: Column(
                        children: [
                          _stepDots(),
                          const SizedBox(height: AppSpacing.xl3),
                          Expanded(
                            child: AnimatedSwitcher(
                              duration: const Duration(milliseconds: 380),
                              switchInCurve: Curves.fastOutSlowIn,
                              switchOutCurve: Curves.fastOutSlowIn,
                              transitionBuilder: (child, anim) {
                                return FadeTransition(
                                  opacity: anim,
                                  child: SlideTransition(
                                    position: Tween<Offset>(
                                      begin: const Offset(0.06, 0),
                                      end: Offset.zero,
                                    ).animate(anim),
                                    child: child,
                                  ),
                                );
                              },
                              child: KeyedSubtree(
                                key: ValueKey(_step),
                                child: _stepPanel(),
                              ),
                            ),
                          ),
                          const SizedBox(height: AppSpacing.xl),
                          _navRow(),
                          if (_error != null) ...[
                            const SizedBox(height: AppSpacing.base),
                            Text(_error!,
                                style: AppTypography.body.copyWith(
                                    color: AppColors.red300)),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          if (_forging) const _ForgingOverlay(),
        ],
      ),
    );
  }

  Widget _wizardHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.xl,
        vertical: AppSpacing.lg,
      ),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => context.go(AppRoutes.dashboard),
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.chevron_left,
                      size: 14, color: AppColors.textMuted),
                  const SizedBox(width: AppSpacing.sm),
                  Text(
                    'Dashboard',
                    style: AppTypography.body.copyWith(
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Spacer(),
          const CloverLoader(size: 22, hue: 38),
          const SizedBox(width: AppSpacing.smPlus),
          Text(
            'AYEN-ODE',
            style: AppTypography.xs.copyWith(
              color: AppColors.amber500.withValues(alpha: 0.6),
              letterSpacing: 2,
              fontWeight: FontWeight.w500,
            ),
          ),
          const Spacer(),
          const SizedBox(width: 88),
        ],
      ),
    );
  }

  Widget _stepDots() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(_total, (i) {
        final state = i < _step
            ? _DotState.done
            : (i == _step ? _DotState.active : _DotState.pending);
        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xs),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 450),
            curve: Curves.fastOutSlowIn,
            height: 6,
            width: state == _DotState.active
                ? 32
                : (state == _DotState.done ? 18 : 6),
            decoration: BoxDecoration(
              color: state == _DotState.active
                  ? AppColors.amber600
                  : (state == _DotState.done
                      ? AppColors.amber700.withValues(alpha: 0.45)
                      : AppColors.slate600.withValues(alpha: 0.3)),
              borderRadius: BorderRadius.circular(3),
              boxShadow: state == _DotState.active
                  ? [
                      BoxShadow(
                        color: AppColors.amber600.withValues(alpha: 0.55),
                        blurRadius: 10,
                      ),
                    ]
                  : null,
            ),
          ),
        );
      }),
    );
  }

  Widget _stepPanel() {
    switch (_step) {
      case 0:
        return _step0();
      case 1:
        return _step1();
      case 2:
        return _step2();
      case 3:
      default:
        return _step3();
    }
  }

  Widget _stepHeader(int n, String title, String description) {
    return Column(
      children: [
        Text(
          'Step ${n + 1} of 4'.toUpperCase(),
          style: AppTypography.xs.copyWith(
            color: AppColors.amber500.withValues(alpha: 0.5),
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: AppSpacing.base),
        Text(
          title,
          textAlign: TextAlign.center,
          style: AppTypography.title.copyWith(color: AppColors.slate100),
        ),
        const SizedBox(height: AppSpacing.md),
        Text(
          description,
          textAlign: TextAlign.center,
          style: AppTypography.body.copyWith(color: AppColors.textMuted),
        ),
      ],
    );
  }

  Widget _step0() {
    return Column(
      children: [
        _stepHeader(0, 'Name Your World',
            'Every great story begins with a name. Choose something that feels right — you can always build the myth around it.'),
        const SizedBox(height: AppSpacing.xl3),
        _wizardInput(
          _name,
          shaking: _shakingField == 'name',
          placeholder:
              'The Shattered Empire, Veilfall, The City of Clocks…',
          large: true,
        ),
      ],
    );
  }

  Widget _step1() {
    return Column(
      children: [
        _stepHeader(1, 'Set the Tone',
            'What mood should the narrative carry? Pick a quick-start or describe your own.'),
        const SizedBox(height: AppSpacing.xl2),
        _chipRow(_toneChips, _theme),
        const SizedBox(height: AppSpacing.lg),
        _wizardInput(_theme, placeholder: 'Or describe your own tone…'),
        const SizedBox(height: AppSpacing.sm),
        Text('Optional — you can leave this blank',
            textAlign: TextAlign.center,
            style: AppTypography.xs.copyWith(color: AppColors.slate700)),
      ],
    );
  }

  Widget _step2() {
    return Column(
      children: [
        _stepHeader(2, 'The Premise',
            'Describe the world, its central conflict, and what makes it breathe. The more texture you give, the richer the narrative.'),
        const SizedBox(height: AppSpacing.xl2),
        _wizardInput(
          _premise,
          shaking: _shakingField == 'premise',
          placeholder:
              'A dying empire fractures into warring city-states while an ancient god slowly awakens beneath the capital…',
          minLines: 5,
          maxLines: 7,
        ),
        const SizedBox(height: AppSpacing.xs),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Required',
                style: AppTypography.xs.copyWith(color: AppColors.slate700)),
            ListenableBuilder(
              listenable: _premise,
              builder: (_, _) => Text(
                '${_premise.text.length} characters',
                style: AppTypography.xs.copyWith(color: AppColors.slate700),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _step3() {
    return Column(
      children: [
        _stepHeader(3, 'Your Place In It',
            'Who are you in this world? Be as specific or vague as you like.'),
        const SizedBox(height: AppSpacing.xl),
        _chipRow(_roleChips, _role),
        const SizedBox(height: AppSpacing.lg),
        _wizardInput(_role, placeholder: 'Or describe your character…'),
        const SizedBox(height: AppSpacing.lg),
        _reviewCard(),
      ],
    );
  }

  Widget _chipRow(List<String> chips, TextEditingController target) {
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: AppSpacing.sm,
      runSpacing: AppSpacing.sm,
      children: chips.map((label) {
        final selected = target.text == label;
        return GestureDetector(
          onTap: () => setState(() {
            target.text = selected ? '' : label;
          }),
          child: MouseRegion(
            cursor: SystemMouseCursors.click,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.xs + 2,
              ),
              decoration: BoxDecoration(
                color: selected
                    ? AppColors.amber900.withValues(alpha: 0.28)
                    : AppColors.slate900.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                border: Border.all(
                  color: selected
                      ? AppColors.amber700.withValues(alpha: 0.7)
                      : AppColors.slate700.withValues(alpha: 0.5),
                ),
              ),
              child: Text(
                label,
                style: AppTypography.xs.copyWith(
                  color: selected
                      ? AppColors.amber200
                      : AppColors.textSecondary.withValues(alpha: 0.75),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _wizardInput(
    TextEditingController controller, {
    String? placeholder,
    int maxLines = 1,
    int? minLines,
    bool large = false,
    bool shaking = false,
  }) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: shaking ? 1 : 0),
      duration: const Duration(milliseconds: 380),
      builder: (context, t, child) {
        final offset = shaking ? (t * 8 * (t < 0.5 ? 1 : -1)) : 0.0;
        return Transform.translate(
          offset: Offset(offset, 0),
          child: child,
        );
      },
      child: TextField(
        controller: controller,
        maxLines: maxLines,
        minLines: minLines,
        style: AppTypography.body.copyWith(
          color: AppColors.slate100,
          fontSize: large ? 16 : 14,
        ),
        decoration: InputDecoration(
          filled: true,
          fillColor: AppColors.slate900.withValues(alpha: 0.65),
          hintText: placeholder,
          hintStyle: AppTypography.body.copyWith(
            color: AppColors.slate500.withValues(alpha: 0.55),
          ),
          contentPadding: EdgeInsets.symmetric(
            horizontal: AppSpacing.base,
            vertical: large ? AppSpacing.base : AppSpacing.md,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
            borderSide: BorderSide(
              color: shaking
                  ? AppColors.red500.withValues(alpha: 0.55)
                  : AppColors.slate700.withValues(alpha: 0.7),
            ),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
            borderSide: BorderSide(
              color: shaking
                  ? AppColors.red500.withValues(alpha: 0.55)
                  : AppColors.slate700.withValues(alpha: 0.7),
            ),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
            borderSide: BorderSide(
              color: AppColors.amber600.withValues(alpha: 0.65),
              width: 1.5,
            ),
          ),
        ),
      ),
    );
  }

  Widget _reviewCard() {
    final name = _name.text.trim().isEmpty ? '—' : _name.text.trim();
    final tone =
        _theme.text.trim().isEmpty ? 'No specific tone set' : _theme.text.trim();
    final premise = _premise.text.trim().isEmpty ? '—' : _premise.text.trim();
    return Container(
      decoration: BoxDecoration(
        color: AppColors.slate900.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(AppSpacing.radiusXl),
        border: Border.all(
          color: AppColors.slate800.withValues(alpha: 0.6),
        ),
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _reviewRow('World', name),
          const Divider(),
          _reviewRow('Tone', tone),
          const Divider(),
          _reviewRow(
            'Premise',
            premise.length > 140
                ? '${premise.substring(0, 140)}…'
                : premise,
          ),
        ],
      ),
    );
  }

  Widget _reviewRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs + 2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: AppTypography.xs.copyWith(
              color: AppColors.textVeryMuted,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 2),
          Text(value, style: AppTypography.body.copyWith(color: AppColors.slate200)),
        ],
      ),
    );
  }

  Widget _navRow() {
    final isLast = _step == _total - 1;
    return Row(
      children: [
        if (_step > 0)
          AppButton(
            label: '← Back',
            variant: AppButtonVariant.ghost,
            onPressed: _prev,
          )
        else
          const SizedBox(width: 80),
        const Spacer(),
        if (isLast)
          AppButton(
            label: '✦ Forge This World',
            variant: AppButtonVariant.primaryStrong,
            onPressed: _forge,
          )
        else
          AppButton(
            label: 'Continue →',
            variant: AppButtonVariant.primary,
            onPressed: _next,
          ),
      ],
    );
  }
}

enum _DotState { done, active, pending }

class _ForgingOverlay extends StatelessWidget {
  const _ForgingOverlay();

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: Container(
        color: AppColors.slate950.withValues(alpha: 0.96),
        alignment: Alignment.center,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CloverLoader(size: 84, hue: 38),
            const SizedBox(height: AppSpacing.xl2),
            Text('Forging Your World',
                style:
                    AppTypography.headerSmall.copyWith(color: AppColors.slate100)),
            const SizedBox(height: AppSpacing.sm),
            Text('Initialising with Claude…',
                style: AppTypography.body.copyWith(color: AppColors.textMuted)),
          ],
        ),
      ),
    );
  }
}
