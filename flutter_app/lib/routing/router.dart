import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../api/api_client.dart';
import '../screens/create_world_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/login_screen.dart';
import '../screens/narrative_screen.dart';
import '../screens/settings_screen.dart';
import '../state/auth_provider.dart';

/// Application routes. Mirror the web frontend's URL set so backend
/// behaviour around `world_id` query params stays identical.
class AppRoutes {
  AppRoutes._();
  static const login = '/';
  static const dashboard = '/dashboard';
  static const createWorld = '/create-world';
  static const narrative = '/narrative';
  static const settings = '/settings';
}

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: AppRoutes.login,
    refreshListenable: authChangeNotifier,
    redirect: (context, state) {
      final authValue = ref.read(authControllerProvider);
      // While bootstrapping, hold on the current route — login is fine as a
      // splash. The redirect will re-fire once bootstrap completes via the
      // authChangeNotifier we bump on every auth state change.
      if (authValue.isLoading) return null;
      final signedIn = authValue.value?.signedIn ?? false;
      final atLogin = state.matchedLocation == AppRoutes.login;
      if (!signedIn && !atLogin) return AppRoutes.login;
      if (signedIn && atLogin) return AppRoutes.dashboard;
      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.dashboard,
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: AppRoutes.createWorld,
        builder: (context, state) => const CreateWorldScreen(),
      ),
      GoRoute(
        path: AppRoutes.narrative,
        builder: (context, state) {
          final worldId = state.uri.queryParameters['world_id'];
          final fresh = state.uri.queryParameters['fresh'] == '1';
          return NarrativeScreen(worldId: worldId, fresh: fresh);
        },
      ),
      GoRoute(
        path: AppRoutes.settings,
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});
