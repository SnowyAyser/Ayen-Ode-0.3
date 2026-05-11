import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'api_exception.dart';
import 'models/auth_models.dart';
import 'models/entity_models.dart';
import 'models/game_time.dart';
import 'models/investigation_models.dart';
import 'models/narrative_models.dart';
import 'models/quest_models.dart';
import 'models/settings_models.dart';
import 'models/world_models.dart';

/// Typed endpoint wrappers. One per route family in design-audit.md §5.
///
/// Every method returns the bare success-payload type and throws
/// `ApiException` on any failure. UI code shouldn't need to touch `Dio`
/// directly.

// ─── Auth ────────────────────────────────────────────────────────────────

class AuthApi {
  AuthApi(this._dio);
  final Dio _dio;

  Future<LoginResponse> login(LoginRequest request) async {
    try {
      final res = await _dio.post('/api/login', data: request.toJson());
      return LoginResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e, fallback: 'Invalid username or password');
    }
  }

  Future<LoginResponse> register(LoginRequest request) async {
    try {
      final res = await _dio.post('/api/register', data: request.toJson());
      return LoginResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e, fallback: 'Could not create account');
    }
  }

  /// Best-effort logout — failures don't matter, the client always clears
  /// local state regardless.
  Future<void> logout() async {
    try {
      await _dio.post('/api/logout');
    } catch (_) {
      // Intentionally swallowed.
    }
  }
}

// ─── Worlds ──────────────────────────────────────────────────────────────

class WorldApi {
  WorldApi(this._dio);
  final Dio _dio;

  Future<WorldListResponse> list() async {
    try {
      final res = await _dio.get('/api/worlds');
      return WorldListResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<ActiveWorldResponse> active() async {
    try {
      final res = await _dio.get('/api/worlds/active');
      return ActiveWorldResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<WorldDetailResponse> fetch(String worldId) async {
    try {
      final res = await _dio.get(
        '/api/world',
        queryParameters: {'world_id': worldId},
      );
      return WorldDetailResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<CreateWorldResponse> create(CreateWorldRequest request) async {
    try {
      final res = await _dio.post(
        '/api/worlds/create',
        data: request.toJson(),
      );
      return CreateWorldResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e, fallback: 'Failed to create world');
    }
  }

  Future<void> switchWorld(String worldId) async {
    try {
      await _dio.post('/api/worlds/switch', data: {'world_id': worldId});
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> reset(String worldId) async {
    try {
      await _dio.post('/api/worlds/$worldId/reset', data: const <String, dynamic>{});
    } catch (e) {
      throw toApiException(e, fallback: 'Reset failed');
    }
  }

  Future<void> delete(String worldId) async {
    try {
      await _dio.delete('/api/worlds/$worldId');
    } catch (e) {
      throw toApiException(e, fallback: 'Delete failed');
    }
  }

  Future<GameTime> time(String worldId) async {
    try {
      final res = await _dio.get('/api/worlds/$worldId/time');
      return GameTime.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  /// `POST /api/worlds/{id}/skip-time`. Returns the new `GameTime` on
  /// success. On a `blocking` response (active investigations / open
  /// threads) the server replies with non-2xx + a body; we surface that as
  /// `ApiException` with the descriptive message.
  Future<GameTime> skipTime(String worldId, int seconds) async {
    try {
      final res = await _dio.post(
        '/api/worlds/$worldId/skip-time',
        data: {'seconds': seconds},
      );
      if (res.statusCode != null && res.statusCode! >= 400) {
        final data = res.data;
        String message = 'Cannot skip time';
        if (data is Map<String, dynamic>) {
          final blocking = data['blocking'];
          if (blocking is Map<String, dynamic>) {
            final inv = blocking['investigation'];
            if (inv is List && inv.isNotEmpty) {
              final names = inv
                  .whereType<Map<String, dynamic>>()
                  .map((j) => j['name'] as String? ?? '')
                  .where((s) => s.isNotEmpty)
                  .join(', ');
              if (names.isNotEmpty) message = 'Active: $names';
            }
          }
          message = (data['error'] as String?) ?? message;
        }
        throw ApiException(message, statusCode: res.statusCode);
      }
      final data = res.data as Map<String, dynamic>;
      final gameTime = data['game_time'] ?? data;
      return GameTime.fromJson(gameTime as Map<String, dynamic>);
    } on ApiException {
      rethrow;
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<CurrencyBalance> currency(String worldId) async {
    try {
      final res = await _dio.get('/api/worlds/$worldId/currencies');
      return CurrencyBalance.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<CurrencyRestoreResponse> restoreCurrency(String worldId, int amount) async {
    try {
      final res = await _dio.post(
        '/api/worlds/$worldId/currencies/restore',
        data: {'amount': amount},
      );
      return CurrencyRestoreResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  // Quests
  Future<QuestListResponse> quests(String worldId) async {
    try {
      final res = await _dio.get('/api/worlds/$worldId/quests');
      return QuestListResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> promoteQuest(String worldId, String questId) async {
    try {
      await _dio.post('/api/worlds/$worldId/quests/$questId/promote');
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> dismissQuest(String worldId, String questId) async {
    try {
      await _dio.post('/api/worlds/$worldId/quests/$questId/dismiss');
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<QuestCheckResponse> checkQuest(String worldId, String questId) async {
    try {
      final res = await _dio.post('/api/worlds/$worldId/quests/$questId/check');
      return QuestCheckResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }
}

// ─── Narrative ───────────────────────────────────────────────────────────

class NarrativeApi {
  NarrativeApi(this._dio);
  final Dio _dio;

  Future<NarrativeResponse> submit(NarrativeRequest request) async {
    try {
      final res = await _dio.post('/api/narrative', data: request.toJson());
      return NarrativeResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e, fallback: 'Failed to process action');
    }
  }
}

// ─── Investigations ──────────────────────────────────────────────────────

class InvestigationApi {
  InvestigationApi(this._dio);
  final Dio _dio;

  Future<InvestigateResponse> start(InvestigateRequest request) async {
    try {
      final res = await _dio.post('/api/investigate', data: request.toJson());
      return InvestigateResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e, fallback: 'Failed to queue investigation');
    }
  }

  Future<InvestigationStatusResponse> status(String jobId) async {
    try {
      final res = await _dio.get('/api/investigations/$jobId');
      return InvestigationStatusResponse.fromJson(
        res.data as Map<String, dynamic>,
      );
    } catch (e) {
      throw toApiException(e);
    }
  }
}

// ─── Entities ────────────────────────────────────────────────────────────

class EntityApi {
  EntityApi(this._dio);
  final Dio _dio;

  Future<EntityDetailResponse> get(String entityId, String worldId) async {
    try {
      final res = await _dio.get(
        '/api/entities/$entityId',
        queryParameters: {'world_id': worldId},
      );
      return EntityDetailResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<EntityStatsResponse> stats(String entityId, String worldId) async {
    try {
      final res = await _dio.get(
        '/api/entities/$entityId/stats',
        queryParameters: {'world_id': worldId},
      );
      return EntityStatsResponse.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> link(EntityLinkRequest request) async {
    try {
      await _dio.post('/api/entities/link', data: request.toJson());
    } catch (e) {
      throw toApiException(e);
    }
  }
}

// ─── Settings ────────────────────────────────────────────────────────────

class SettingsApi {
  SettingsApi(this._dio);
  final Dio _dio;

  Future<AppSettings> get() async {
    try {
      final res = await _dio.get('/api/settings');
      return AppSettings.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  /// POST body is shaped as env-var keys (`ANTHROPIC_API_KEY`,
  /// `APP_USERNAME`, …) — see audit §4.5.
  Future<void> save(Map<String, dynamic> envPayload) async {
    try {
      await _dio.post('/api/settings', data: envPayload);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<SettingsStatus> status() async {
    try {
      final res = await _dio.get('/api/settings/status');
      return SettingsStatus.fromJson(res.data as Map<String, dynamic>);
    } catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> serverRestart() async {
    try {
      await _dio.post('/api/server/restart', data: const <String, dynamic>{});
    } catch (e) {
      throw toApiException(e);
    }
  }
}

// ─── Riverpod wiring ────────────────────────────────────────────────────

final authApiProvider = Provider<AuthApi>((ref) => AuthApi(ref.watch(dioProvider)));
final worldApiProvider = Provider<WorldApi>((ref) => WorldApi(ref.watch(dioProvider)));
final narrativeApiProvider =
    Provider<NarrativeApi>((ref) => NarrativeApi(ref.watch(dioProvider)));
final investigationApiProvider =
    Provider<InvestigationApi>((ref) => InvestigationApi(ref.watch(dioProvider)));
final entityApiProvider = Provider<EntityApi>((ref) => EntityApi(ref.watch(dioProvider)));
final settingsApiProvider =
    Provider<SettingsApi>((ref) => SettingsApi(ref.watch(dioProvider)));
