import 'package:freezed_annotation/freezed_annotation.dart';

part 'entity_models.freezed.dart';
part 'entity_models.g.dart';

@freezed
class Entity with _$Entity {
  const factory Entity({
    required String entityId,
    required String name,
    /// `character`, `location`, `faction`, `object`, `event`, or `unknown`.
    /// Note the backend sometimes returns the type under `type`, sometimes
    /// under `entity_type`; we accept either by mapping in the API layer.
    String? entityType,
    String? type,
    String? summary,
    String? status,
    @Default(<String>[]) List<String> tags,
    @Default(<String>[]) List<String> timelineNotes,
    @Default(<String>[]) List<String> openQuestions,
  }) = _Entity;

  factory Entity.fromJson(Map<String, dynamic> json) => _$EntityFromJson(json);
}

@freezed
class EntityDetailResponse with _$EntityDetailResponse {
  const factory EntityDetailResponse({
    required Entity entity,
  }) = _EntityDetailResponse;

  factory EntityDetailResponse.fromJson(Map<String, dynamic> json) =>
      _$EntityDetailResponseFromJson(json);
}

@freezed
class EntityStatsResponse with _$EntityStatsResponse {
  const factory EntityStatsResponse({
    @Default(<String, int>{}) Map<String, int> stats,
  }) = _EntityStatsResponse;

  factory EntityStatsResponse.fromJson(Map<String, dynamic> json) =>
      _$EntityStatsResponseFromJson(json);
}

@freezed
class EntityLinkRequest with _$EntityLinkRequest {
  const factory EntityLinkRequest({
    required String worldId,
    required String entityIdA,
    required String entityIdB,
    @Default('references') String relation,
  }) = _EntityLinkRequest;

  factory EntityLinkRequest.fromJson(Map<String, dynamic> json) =>
      _$EntityLinkRequestFromJson(json);
}
