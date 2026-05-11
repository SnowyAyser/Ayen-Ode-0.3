// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'game_time.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$GameTimeImpl _$$GameTimeImplFromJson(Map<String, dynamic> json) =>
    _$GameTimeImpl(
      seconds: (json['seconds'] as num?)?.toInt() ?? 0,
      label: json['label'] as String?,
    );

Map<String, dynamic> _$$GameTimeImplToJson(_$GameTimeImpl instance) =>
    <String, dynamic>{'seconds': instance.seconds, 'label': instance.label};
