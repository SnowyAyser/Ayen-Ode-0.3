import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Persists the bearer token across launches.
///
/// The web frontend reads/writes `localStorage.apiKey`. We use
/// `flutter_secure_storage` instead — same lifetime (persists until logout),
/// but encrypted at rest on both Windows (DPAPI) and Android (Keystore).
class TokenStorage {
  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _tokenKey = 'ayen_ode_auth_token';
  static const _usernameKey = 'ayen_ode_username';

  final FlutterSecureStorage _storage;

  Future<String?> readToken() => _storage.read(key: _tokenKey);

  Future<void> writeToken(String token) =>
      _storage.write(key: _tokenKey, value: token);

  Future<void> clearToken() => _storage.delete(key: _tokenKey);

  Future<String?> readUsername() => _storage.read(key: _usernameKey);

  Future<void> writeUsername(String username) =>
      _storage.write(key: _usernameKey, value: username);

  Future<void> clearUsername() => _storage.delete(key: _usernameKey);

  Future<void> clearAll() async {
    await Future.wait([clearToken(), clearUsername()]);
  }
}

final tokenStorageProvider = Provider<TokenStorage>((ref) {
  return TokenStorage();
});
