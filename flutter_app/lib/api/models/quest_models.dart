import 'package:freezed_annotation/freezed_annotation.dart';

part 'quest_models.freezed.dart';
part 'quest_models.g.dart';

@freezed
class Quest with _$Quest {
  const factory Quest({
    required String questId,
    required int tier,
    required String title,
    String? description,
    /// `active`, `pending_player`, `completed`, `dismissed`, …
    @Default('active') String status,
    @Default(<String>[]) List<String> completionTags,
    @Default(<String>[]) List<String> progressTags,
  }) = _Quest;

  factory Quest.fromJson(Map<String, dynamic> json) => _$QuestFromJson(json);
}

@freezed
class QuestListResponse with _$QuestListResponse {
  const factory QuestListResponse({
    @Default(<Quest>[]) List<Quest> quests,
  }) = _QuestListResponse;

  factory QuestListResponse.fromJson(Map<String, dynamic> json) =>
      _$QuestListResponseFromJson(json);
}

@freezed
class QuestCheckResponse with _$QuestCheckResponse {
  const factory QuestCheckResponse({
    required String title,
    @Default(0) int matched,
    @Default(0) int total,
    @Default(0) int percentage,
    @Default(0) int pointsSpent,
  }) = _QuestCheckResponse;

  factory QuestCheckResponse.fromJson(Map<String, dynamic> json) =>
      _$QuestCheckResponseFromJson(json);
}
