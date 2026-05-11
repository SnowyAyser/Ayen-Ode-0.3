// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'narrative_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConversationMessageImpl _$$ConversationMessageImplFromJson(
  Map<String, dynamic> json,
) => _$ConversationMessageImpl(
  role: json['role'] as String,
  content: json['content'] as String,
);

Map<String, dynamic> _$$ConversationMessageImplToJson(
  _$ConversationMessageImpl instance,
) => <String, dynamic>{'role': instance.role, 'content': instance.content};

_$NarrativeRequestImpl _$$NarrativeRequestImplFromJson(
  Map<String, dynamic> json,
) => _$NarrativeRequestImpl(
  worldId: json['world_id'] as String,
  action: json['action'] as String,
  history:
      (json['history'] as List<dynamic>?)
          ?.map((e) => ConversationMessage.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ConversationMessage>[],
);

Map<String, dynamic> _$$NarrativeRequestImplToJson(
  _$NarrativeRequestImpl instance,
) => <String, dynamic>{
  'world_id': instance.worldId,
  'action': instance.action,
  'history': instance.history.map((e) => e.toJson()).toList(),
};

_$NarrativeResponseImpl _$$NarrativeResponseImplFromJson(
  Map<String, dynamic> json,
) => _$NarrativeResponseImpl(
  narrative: json['narrative'] as String,
  history:
      (json['history'] as List<dynamic>?)
          ?.map((e) => ConversationMessage.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <ConversationMessage>[],
  investigationPoints: (json['investigation_points'] as num?)?.toInt(),
  maxInvestigationPoints: (json['max_investigation_points'] as num?)?.toInt(),
  gameTime: json['game_time'] == null
      ? null
      : GameTime.fromJson(json['game_time'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$NarrativeResponseImplToJson(
  _$NarrativeResponseImpl instance,
) => <String, dynamic>{
  'narrative': instance.narrative,
  'history': instance.history.map((e) => e.toJson()).toList(),
  'investigation_points': instance.investigationPoints,
  'max_investigation_points': instance.maxInvestigationPoints,
  'game_time': instance.gameTime?.toJson(),
};
