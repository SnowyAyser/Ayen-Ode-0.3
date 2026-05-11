// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'investigation_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$InvestigateRequestImpl _$$InvestigateRequestImplFromJson(
  Map<String, dynamic> json,
) => _$InvestigateRequestImpl(
  worldId: json['world_id'] as String,
  itemName: json['item_name'] as String,
  entityType: json['entity_type'] as String? ?? 'object',
  cost: (json['cost'] as num?)?.toInt() ?? 1,
);

Map<String, dynamic> _$$InvestigateRequestImplToJson(
  _$InvestigateRequestImpl instance,
) => <String, dynamic>{
  'world_id': instance.worldId,
  'item_name': instance.itemName,
  'entity_type': instance.entityType,
  'cost': instance.cost,
};

_$InvestigateResponseImpl _$$InvestigateResponseImplFromJson(
  Map<String, dynamic> json,
) => _$InvestigateResponseImpl(
  investigationId: json['investigation_id'] as String,
  remainingPoints: (json['remaining_points'] as num?)?.toInt() ?? 0,
);

Map<String, dynamic> _$$InvestigateResponseImplToJson(
  _$InvestigateResponseImpl instance,
) => <String, dynamic>{
  'investigation_id': instance.investigationId,
  'remaining_points': instance.remainingPoints,
};

_$InvestigationResultImpl _$$InvestigationResultImplFromJson(
  Map<String, dynamic> json,
) => _$InvestigationResultImpl(
  entity: json['entity'] == null
      ? null
      : Entity.fromJson(json['entity'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$InvestigationResultImplToJson(
  _$InvestigationResultImpl instance,
) => <String, dynamic>{'entity': instance.entity?.toJson()};

_$InvestigationStatusResponseImpl _$$InvestigationStatusResponseImplFromJson(
  Map<String, dynamic> json,
) => _$InvestigationStatusResponseImpl(
  status: json['status'] as String,
  result: json['result'] == null
      ? null
      : InvestigationResult.fromJson(json['result'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$InvestigationStatusResponseImplToJson(
  _$InvestigationStatusResponseImpl instance,
) => <String, dynamic>{
  'status': instance.status,
  'result': instance.result?.toJson(),
};
