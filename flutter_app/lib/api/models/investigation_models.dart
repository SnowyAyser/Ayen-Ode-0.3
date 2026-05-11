import 'package:freezed_annotation/freezed_annotation.dart';

import 'entity_models.dart';

part 'investigation_models.freezed.dart';
part 'investigation_models.g.dart';

@freezed
class InvestigateRequest with _$InvestigateRequest {
  const factory InvestigateRequest({
    required String worldId,
    required String itemName,
    @Default('object') String entityType,
    @Default(1) int cost,
  }) = _InvestigateRequest;

  factory InvestigateRequest.fromJson(Map<String, dynamic> json) =>
      _$InvestigateRequestFromJson(json);
}

@freezed
class InvestigateResponse with _$InvestigateResponse {
  const factory InvestigateResponse({
    required String investigationId,
    @Default(0) int remainingPoints,
  }) = _InvestigateResponse;

  factory InvestigateResponse.fromJson(Map<String, dynamic> json) =>
      _$InvestigateResponseFromJson(json);
}

@freezed
class InvestigationResult with _$InvestigationResult {
  const factory InvestigationResult({
    Entity? entity,
  }) = _InvestigationResult;

  factory InvestigationResult.fromJson(Map<String, dynamic> json) =>
      _$InvestigationResultFromJson(json);
}

@freezed
class InvestigationStatusResponse with _$InvestigationStatusResponse {
  const factory InvestigationStatusResponse({
    /// `queued` / `processing` / `complete` / `failed`.
    required String status,
    InvestigationResult? result,
  }) = _InvestigationStatusResponse;

  factory InvestigationStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$InvestigationStatusResponseFromJson(json);
}
