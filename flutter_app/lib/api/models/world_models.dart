import 'package:freezed_annotation/freezed_annotation.dart';

import 'entity_models.dart';
import 'game_time.dart';

part 'world_models.freezed.dart';
part 'world_models.g.dart';

@freezed
class World with _$World {
  const factory World({
    required String worldId,
    required String name,
    String? premise,
    String? themeTone,
    String? playerRole,
    String? status,
    GameTime? gameTime,
  }) = _World;

  factory World.fromJson(Map<String, dynamic> json) => _$WorldFromJson(json);
}

@freezed
class WorldListResponse with _$WorldListResponse {
  const factory WorldListResponse({
    @Default(<World>[]) List<World> worlds,
  }) = _WorldListResponse;

  factory WorldListResponse.fromJson(Map<String, dynamic> json) =>
      _$WorldListResponseFromJson(json);
}

@freezed
class ActiveWorldResponse with _$ActiveWorldResponse {
  const factory ActiveWorldResponse({
    World? world,
  }) = _ActiveWorldResponse;

  factory ActiveWorldResponse.fromJson(Map<String, dynamic> json) =>
      _$ActiveWorldResponseFromJson(json);
}

@freezed
class CreateWorldRequest with _$CreateWorldRequest {
  const factory CreateWorldRequest({
    required String name,
    required String premise,
    String? themeTone,
    String? playerRole,
  }) = _CreateWorldRequest;

  factory CreateWorldRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateWorldRequestFromJson(json);
}

@freezed
class CreateWorldResponse with _$CreateWorldResponse {
  const factory CreateWorldResponse({
    required String worldId,
  }) = _CreateWorldResponse;

  factory CreateWorldResponse.fromJson(Map<String, dynamic> json) =>
      _$CreateWorldResponseFromJson(json);
}

/// Response shape of `GET /api/world?world_id={id}`.
@freezed
class WorldDetailResponse with _$WorldDetailResponse {
  const factory WorldDetailResponse({
    required bool success,
    required World world,
    required String worldId,
    @Default(<Entity>[]) List<Entity> entities,
    String? handoff,
    String? error,
  }) = _WorldDetailResponse;

  factory WorldDetailResponse.fromJson(Map<String, dynamic> json) =>
      _$WorldDetailResponseFromJson(json);
}

@freezed
class CurrencyBalance with _$CurrencyBalance {
  const factory CurrencyBalance({
    @Default(0) int balance,
    @Default(5) int maxBalance,
    @Default(0) int points,
    @Default(5) int maxPoints,
  }) = _CurrencyBalance;

  factory CurrencyBalance.fromJson(Map<String, dynamic> json) =>
      _$CurrencyBalanceFromJson(json);
}

@freezed
class CurrencyRestoreResponse with _$CurrencyRestoreResponse {
  const factory CurrencyRestoreResponse({
    @Default(0) int balanceAfter,
    @Default(5) int maxBalance,
  }) = _CurrencyRestoreResponse;

  factory CurrencyRestoreResponse.fromJson(Map<String, dynamic> json) =>
      _$CurrencyRestoreResponseFromJson(json);
}

