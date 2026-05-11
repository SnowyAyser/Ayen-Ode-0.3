// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'quest_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$QuestImpl _$$QuestImplFromJson(Map<String, dynamic> json) => _$QuestImpl(
  questId: json['quest_id'] as String,
  tier: (json['tier'] as num).toInt(),
  title: json['title'] as String,
  description: json['description'] as String?,
  status: json['status'] as String? ?? 'active',
  completionTags:
      (json['completion_tags'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
  progressTags:
      (json['progress_tags'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
);

Map<String, dynamic> _$$QuestImplToJson(_$QuestImpl instance) =>
    <String, dynamic>{
      'quest_id': instance.questId,
      'tier': instance.tier,
      'title': instance.title,
      'description': instance.description,
      'status': instance.status,
      'completion_tags': instance.completionTags,
      'progress_tags': instance.progressTags,
    };

_$QuestListResponseImpl _$$QuestListResponseImplFromJson(
  Map<String, dynamic> json,
) => _$QuestListResponseImpl(
  quests:
      (json['quests'] as List<dynamic>?)
          ?.map((e) => Quest.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <Quest>[],
);

Map<String, dynamic> _$$QuestListResponseImplToJson(
  _$QuestListResponseImpl instance,
) => <String, dynamic>{
  'quests': instance.quests.map((e) => e.toJson()).toList(),
};

_$QuestCheckResponseImpl _$$QuestCheckResponseImplFromJson(
  Map<String, dynamic> json,
) => _$QuestCheckResponseImpl(
  title: json['title'] as String,
  matched: (json['matched'] as num?)?.toInt() ?? 0,
  total: (json['total'] as num?)?.toInt() ?? 0,
  percentage: (json['percentage'] as num?)?.toInt() ?? 0,
  pointsSpent: (json['points_spent'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$$QuestCheckResponseImplToJson(
  _$QuestCheckResponseImpl instance,
) => <String, dynamic>{
  'title': instance.title,
  'matched': instance.matched,
  'total': instance.total,
  'percentage': instance.percentage,
  'points_spent': instance.pointsSpent,
};
