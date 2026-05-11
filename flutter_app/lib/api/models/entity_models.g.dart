// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'entity_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$EntityImpl _$$EntityImplFromJson(Map<String, dynamic> json) => _$EntityImpl(
  entityId: json['entity_id'] as String,
  name: json['name'] as String,
  entityType: json['entity_type'] as String?,
  type: json['type'] as String?,
  summary: json['summary'] as String?,
  status: json['status'] as String?,
  tags:
      (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const <String>[],
  timelineNotes:
      (json['timeline_notes'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
  openQuestions:
      (json['open_questions'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const <String>[],
);

Map<String, dynamic> _$$EntityImplToJson(_$EntityImpl instance) =>
    <String, dynamic>{
      'entity_id': instance.entityId,
      'name': instance.name,
      'entity_type': instance.entityType,
      'type': instance.type,
      'summary': instance.summary,
      'status': instance.status,
      'tags': instance.tags,
      'timeline_notes': instance.timelineNotes,
      'open_questions': instance.openQuestions,
    };

_$EntityDetailResponseImpl _$$EntityDetailResponseImplFromJson(
  Map<String, dynamic> json,
) => _$EntityDetailResponseImpl(
  entity: Entity.fromJson(json['entity'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$EntityDetailResponseImplToJson(
  _$EntityDetailResponseImpl instance,
) => <String, dynamic>{'entity': instance.entity.toJson()};

_$EntityStatsResponseImpl _$$EntityStatsResponseImplFromJson(
  Map<String, dynamic> json,
) => _$EntityStatsResponseImpl(
  stats:
      (json['stats'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ) ??
      const <String, int>{},
);

Map<String, dynamic> _$$EntityStatsResponseImplToJson(
  _$EntityStatsResponseImpl instance,
) => <String, dynamic>{'stats': instance.stats};

_$EntityLinkRequestImpl _$$EntityLinkRequestImplFromJson(
  Map<String, dynamic> json,
) => _$EntityLinkRequestImpl(
  worldId: json['world_id'] as String,
  entityIdA: json['entity_id_a'] as String,
  entityIdB: json['entity_id_b'] as String,
  relation: json['relation'] as String? ?? 'references',
);

Map<String, dynamic> _$$EntityLinkRequestImplToJson(
  _$EntityLinkRequestImpl instance,
) => <String, dynamic>{
  'world_id': instance.worldId,
  'entity_id_a': instance.entityIdA,
  'entity_id_b': instance.entityIdB,
  'relation': instance.relation,
};
