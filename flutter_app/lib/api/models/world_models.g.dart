// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'world_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$WorldImpl _$$WorldImplFromJson(Map<String, dynamic> json) => _$WorldImpl(
  worldId: json['world_id'] as String,
  name: json['name'] as String,
  premise: json['premise'] as String?,
  themeTone: json['theme_tone'] as String?,
  playerRole: json['player_role'] as String?,
  status: json['status'] as String?,
  gameTime: json['game_time'] == null
      ? null
      : GameTime.fromJson(json['game_time'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$WorldImplToJson(_$WorldImpl instance) =>
    <String, dynamic>{
      'world_id': instance.worldId,
      'name': instance.name,
      'premise': instance.premise,
      'theme_tone': instance.themeTone,
      'player_role': instance.playerRole,
      'status': instance.status,
      'game_time': instance.gameTime?.toJson(),
    };

_$WorldListResponseImpl _$$WorldListResponseImplFromJson(
  Map<String, dynamic> json,
) => _$WorldListResponseImpl(
  worlds:
      (json['worlds'] as List<dynamic>?)
          ?.map((e) => World.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <World>[],
);

Map<String, dynamic> _$$WorldListResponseImplToJson(
  _$WorldListResponseImpl instance,
) => <String, dynamic>{
  'worlds': instance.worlds.map((e) => e.toJson()).toList(),
};

_$ActiveWorldResponseImpl _$$ActiveWorldResponseImplFromJson(
  Map<String, dynamic> json,
) => _$ActiveWorldResponseImpl(
  world: json['world'] == null
      ? null
      : World.fromJson(json['world'] as Map<String, dynamic>),
);

Map<String, dynamic> _$$ActiveWorldResponseImplToJson(
  _$ActiveWorldResponseImpl instance,
) => <String, dynamic>{'world': instance.world?.toJson()};

_$CreateWorldRequestImpl _$$CreateWorldRequestImplFromJson(
  Map<String, dynamic> json,
) => _$CreateWorldRequestImpl(
  name: json['name'] as String,
  premise: json['premise'] as String,
  themeTone: json['theme_tone'] as String?,
  playerRole: json['player_role'] as String?,
);

Map<String, dynamic> _$$CreateWorldRequestImplToJson(
  _$CreateWorldRequestImpl instance,
) => <String, dynamic>{
  'name': instance.name,
  'premise': instance.premise,
  'theme_tone': instance.themeTone,
  'player_role': instance.playerRole,
};

_$CreateWorldResponseImpl _$$CreateWorldResponseImplFromJson(
  Map<String, dynamic> json,
) => _$CreateWorldResponseImpl(worldId: json['world_id'] as String);

Map<String, dynamic> _$$CreateWorldResponseImplToJson(
  _$CreateWorldResponseImpl instance,
) => <String, dynamic>{'world_id': instance.worldId};

_$WorldDetailResponseImpl _$$WorldDetailResponseImplFromJson(
  Map<String, dynamic> json,
) => _$WorldDetailResponseImpl(
  success: json['success'] as bool,
  world: World.fromJson(json['world'] as Map<String, dynamic>),
  worldId: json['world_id'] as String,
  entities:
      (json['entities'] as List<dynamic>?)
          ?.map((e) => Entity.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <Entity>[],
  handoff: json['handoff'] as String?,
  error: json['error'] as String?,
);

Map<String, dynamic> _$$WorldDetailResponseImplToJson(
  _$WorldDetailResponseImpl instance,
) => <String, dynamic>{
  'success': instance.success,
  'world': instance.world.toJson(),
  'world_id': instance.worldId,
  'entities': instance.entities.map((e) => e.toJson()).toList(),
  'handoff': instance.handoff,
  'error': instance.error,
};

_$CurrencyBalanceImpl _$$CurrencyBalanceImplFromJson(
  Map<String, dynamic> json,
) => _$CurrencyBalanceImpl(
  balance: (json['balance'] as num?)?.toInt() ?? 0,
  maxBalance: (json['max_balance'] as num?)?.toInt() ?? 5,
  points: (json['points'] as num?)?.toInt() ?? 0,
  maxPoints: (json['max_points'] as num?)?.toInt() ?? 5,
);

Map<String, dynamic> _$$CurrencyBalanceImplToJson(
  _$CurrencyBalanceImpl instance,
) => <String, dynamic>{
  'balance': instance.balance,
  'max_balance': instance.maxBalance,
  'points': instance.points,
  'max_points': instance.maxPoints,
};

_$CurrencyRestoreResponseImpl _$$CurrencyRestoreResponseImplFromJson(
  Map<String, dynamic> json,
) => _$CurrencyRestoreResponseImpl(
  balanceAfter: (json['balance_after'] as num?)?.toInt() ?? 0,
  maxBalance: (json['max_balance'] as num?)?.toInt() ?? 5,
);

Map<String, dynamic> _$$CurrencyRestoreResponseImplToJson(
  _$CurrencyRestoreResponseImpl instance,
) => <String, dynamic>{
  'balance_after': instance.balanceAfter,
  'max_balance': instance.maxBalance,
};
