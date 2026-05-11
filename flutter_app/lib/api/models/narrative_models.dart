import 'package:freezed_annotation/freezed_annotation.dart';

import 'game_time.dart';

part 'narrative_models.freezed.dart';
part 'narrative_models.g.dart';

/// One row in `conversationHistory`.
@freezed
class ConversationMessage with _$ConversationMessage {
  const factory ConversationMessage({
    /// `user` or `assistant`.
    required String role,
    required String content,
  }) = _ConversationMessage;

  factory ConversationMessage.fromJson(Map<String, dynamic> json) =>
      _$ConversationMessageFromJson(json);
}

@freezed
class NarrativeRequest with _$NarrativeRequest {
  const factory NarrativeRequest({
    required String worldId,
    required String action,
    @Default(<ConversationMessage>[]) List<ConversationMessage> history,
  }) = _NarrativeRequest;

  factory NarrativeRequest.fromJson(Map<String, dynamic> json) =>
      _$NarrativeRequestFromJson(json);
}

@freezed
class NarrativeResponse with _$NarrativeResponse {
  const factory NarrativeResponse({
    required String narrative,
    @Default(<ConversationMessage>[]) List<ConversationMessage> history,
    int? investigationPoints,
    int? maxInvestigationPoints,
    GameTime? gameTime,
  }) = _NarrativeResponse;

  factory NarrativeResponse.fromJson(Map<String, dynamic> json) =>
      _$NarrativeResponseFromJson(json);
}
