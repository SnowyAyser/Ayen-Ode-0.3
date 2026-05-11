import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../routing/router.dart';
import '../state/auth_provider.dart';
import '../theme/colors.dart';
import '../theme/spacing.dart';
import '../theme/typography.dart';
import '../widgets/app_input.dart';
import '../widgets/clover_loader.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

enum _Mode { signIn, register }

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _username = TextEditingController();
  final _password = TextEditingController();
  _Mode _mode = _Mode.signIn;
  bool _submitting = false;
  String? _error;

  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final u = _username.text.trim();
    final p = _password.text;
    if (u.isEmpty || p.isEmpty) {
      setState(() => _error = 'Username and password are required');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
    });

    try {
      final auth = ref.read(authControllerProvider.notifier);
      // Mirror the web's 1200ms minimum-wait so the loader animation reads.
      final minWait = Future<void>.delayed(const Duration(milliseconds: 1200));
      if (_mode == _Mode.signIn) {
        await Future.wait([auth.signIn(u, p), minWait]);
      } else {
        await Future.wait([auth.register(u, p), minWait]);
      }
      if (!mounted) return;
      context.go(AppRoutes.dashboard);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _submitting = false;
        _error = _mode == _Mode.signIn
            ? 'Invalid username or password'
            : 'Could not create account';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Slate gradient backdrop, matching the web's bg-gradient-to-br.
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [AppColors.slate900, AppColors.slate800],
          ),
        ),
        child: Stack(
          children: [
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 448),
                child: _LoginCard(
                  username: _username,
                  password: _password,
                  mode: _mode,
                  onModeChanged: (m) => setState(() {
                    _mode = m;
                    _error = null;
                  }),
                  onSubmit: _submit,
                  submitting: _submitting,
                  error: _error,
                ),
              ),
            ),
            if (_submitting) const _LoginLoaderOverlay(),
          ],
        ),
      ),
    );
  }
}

class _LoginCard extends StatelessWidget {
  const _LoginCard({
    required this.username,
    required this.password,
    required this.mode,
    required this.onModeChanged,
    required this.onSubmit,
    required this.submitting,
    required this.error,
  });

  final TextEditingController username;
  final TextEditingController password;
  final _Mode mode;
  final ValueChanged<_Mode> onModeChanged;
  final VoidCallback onSubmit;
  final bool submitting;
  final String? error;

  @override
  Widget build(BuildContext context) {
    final isSignIn = mode == _Mode.signIn;
    return Padding(
      padding: const EdgeInsets.all(AppSpacing.base),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.slate800,
          borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          border: Border.all(color: AppColors.slate700),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.4),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Ayen-Ode',
              textAlign: TextAlign.center,
              style: AppTypography.title.copyWith(color: Colors.white),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              isSignIn ? 'Sign in to continue' : 'Create an account',
              textAlign: TextAlign.center,
              style: AppTypography.body.copyWith(color: AppColors.slate400),
            ),
            const SizedBox(height: AppSpacing.xl),
            _ModeTabs(mode: mode, onChanged: onModeChanged),
            const SizedBox(height: AppSpacing.xl),
            AppTextField(
              controller: username,
              placeholder: 'username',
              label: 'Username',
              style: InputStyle.login,
              onSubmitted: (_) => onSubmit(),
            ),
            const SizedBox(height: AppSpacing.xl),
            AppTextField(
              controller: password,
              placeholder: '••••••••',
              label: 'Password',
              obscure: true,
              style: InputStyle.login,
              onSubmitted: (_) => onSubmit(),
            ),
            const SizedBox(height: AppSpacing.xl),
            _SubmitButton(
              label: isSignIn ? 'Login' : 'Create account',
              onPressed: submitting ? null : onSubmit,
            ),
            if (error != null) ...[
              const SizedBox(height: AppSpacing.base),
              Container(
                decoration: BoxDecoration(
                  color: AppColors.red900,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusSm),
                  border: Border.all(color: AppColors.red700),
                ),
                padding: const EdgeInsets.all(AppSpacing.md),
                child: Text(
                  error!,
                  style: AppTypography.body.copyWith(color: AppColors.red200),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ModeTabs extends StatelessWidget {
  const _ModeTabs({required this.mode, required this.onChanged});
  final _Mode mode;
  final ValueChanged<_Mode> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.slate900,
        borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
      ),
      padding: const EdgeInsets.all(AppSpacing.xs),
      child: Row(
        children: [
          Expanded(child: _tab(_Mode.signIn, 'Sign in')),
          Expanded(child: _tab(_Mode.register, 'Create account')),
        ],
      ),
    );
  }

  Widget _tab(_Mode m, String label) {
    final selected = m == mode;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: () => onChanged(m),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        decoration: BoxDecoration(
          color: selected ? AppColors.slate700 : Colors.transparent,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        ),
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
        child: Text(
          label,
          textAlign: TextAlign.center,
          style: AppTypography.bodyMedium.copyWith(
            color: selected ? Colors.white : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }
}

class _SubmitButton extends StatefulWidget {
  const _SubmitButton({required this.label, required this.onPressed});
  final String label;
  final VoidCallback? onPressed;

  @override
  State<_SubmitButton> createState() => _SubmitButtonState();
}

class _SubmitButtonState extends State<_SubmitButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    final disabled = widget.onPressed == null;
    return MouseRegion(
      cursor: disabled ? SystemMouseCursors.basic : SystemMouseCursors.click,
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: widget.onPressed,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          decoration: BoxDecoration(
            color: disabled
                ? AppColors.blue600.withValues(alpha: 0.5)
                : (_hovering ? AppColors.blue500 : AppColors.blue600),
            borderRadius: BorderRadius.circular(AppSpacing.radiusLg),
          ),
          padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
          child: Text(
            widget.label,
            textAlign: TextAlign.center,
            style: AppTypography.bodyMedium.copyWith(color: Colors.white),
          ),
        ),
      ),
    );
  }
}

class _LoginLoaderOverlay extends StatelessWidget {
  const _LoginLoaderOverlay();

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 300),
        opacity: 1,
        child: Container(
          color: AppColors.slate900,
          alignment: Alignment.center,
          child: const CloverLoader.rgb(
            size: 220,
            rgb: AppColors.loginCloverGreen,
          ),
        ),
      ),
    );
  }
}
