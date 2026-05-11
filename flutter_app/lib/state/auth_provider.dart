import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../api/clients.dart';
import '../api/models/auth_models.dart';
import '../api/token_storage.dart';

/// Auth state machine consumed by the router for redirect gating.
///
/// `null` means "still bootstrapping" (we haven't yet checked secure storage).
/// `false` means "no token". `true` means "we have a token; treat the user
/// as signed in until a 401 says otherwise".
class AuthState {
  const AuthState({required this.signedIn, this.username});
  final bool signedIn;
  final String? username;
}

class AuthController extends StateNotifier<AsyncValue<AuthState>> {
  AuthController({required this.tokens, required this.authApi})
      : super(const AsyncValue.loading()) {
    _bootstrap();
  }

  final TokenStorage tokens;
  final AuthApi authApi;

  Future<void> _bootstrap() async {
    try {
      final token = await tokens.readToken();
      final username = await tokens.readUsername();
      state = AsyncValue.data(
        AuthState(signedIn: token != null && token.isNotEmpty, username: username),
      );
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> signIn(String username, String password) async {
    state = const AsyncValue.loading();
    try {
      final res = await authApi.login(
        LoginRequest(username: username, password: password),
      );
      await tokens.writeToken(res.token);
      await tokens.writeUsername(username);
      state = AsyncValue.data(AuthState(signedIn: true, username: username));
      bumpAuth();
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> register(String username, String password) async {
    state = const AsyncValue.loading();
    try {
      final res = await authApi.register(
        LoginRequest(username: username, password: password),
      );
      await tokens.writeToken(res.token);
      await tokens.writeUsername(username);
      state = AsyncValue.data(AuthState(signedIn: true, username: username));
      bumpAuth();
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      rethrow;
    }
  }

  Future<void> signOut() async {
    await authApi.logout();
    await tokens.clearAll();
    state = const AsyncValue.data(AuthState(signedIn: false));
    bumpAuth();
  }
}

final authControllerProvider =
    StateNotifierProvider<AuthController, AsyncValue<AuthState>>((ref) {
  return AuthController(
    tokens: ref.watch(tokenStorageProvider),
    authApi: ref.watch(authApiProvider),
  );
});
