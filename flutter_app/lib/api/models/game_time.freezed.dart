// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'game_time.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

GameTime _$GameTimeFromJson(Map<String, dynamic> json) {
  return _GameTime.fromJson(json);
}

/// @nodoc
mixin _$GameTime {
  int get seconds => throw _privateConstructorUsedError;
  String? get label => throw _privateConstructorUsedError;

  /// Serializes this GameTime to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GameTime
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GameTimeCopyWith<GameTime> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GameTimeCopyWith<$Res> {
  factory $GameTimeCopyWith(GameTime value, $Res Function(GameTime) then) =
      _$GameTimeCopyWithImpl<$Res, GameTime>;
  @useResult
  $Res call({int seconds, String? label});
}

/// @nodoc
class _$GameTimeCopyWithImpl<$Res, $Val extends GameTime>
    implements $GameTimeCopyWith<$Res> {
  _$GameTimeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GameTime
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? seconds = null, Object? label = freezed}) {
    return _then(
      _value.copyWith(
            seconds: null == seconds
                ? _value.seconds
                : seconds // ignore: cast_nullable_to_non_nullable
                      as int,
            label: freezed == label
                ? _value.label
                : label // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GameTimeImplCopyWith<$Res>
    implements $GameTimeCopyWith<$Res> {
  factory _$$GameTimeImplCopyWith(
    _$GameTimeImpl value,
    $Res Function(_$GameTimeImpl) then,
  ) = __$$GameTimeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int seconds, String? label});
}

/// @nodoc
class __$$GameTimeImplCopyWithImpl<$Res>
    extends _$GameTimeCopyWithImpl<$Res, _$GameTimeImpl>
    implements _$$GameTimeImplCopyWith<$Res> {
  __$$GameTimeImplCopyWithImpl(
    _$GameTimeImpl _value,
    $Res Function(_$GameTimeImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GameTime
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? seconds = null, Object? label = freezed}) {
    return _then(
      _$GameTimeImpl(
        seconds: null == seconds
            ? _value.seconds
            : seconds // ignore: cast_nullable_to_non_nullable
                  as int,
        label: freezed == label
            ? _value.label
            : label // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GameTimeImpl implements _GameTime {
  const _$GameTimeImpl({this.seconds = 0, this.label});

  factory _$GameTimeImpl.fromJson(Map<String, dynamic> json) =>
      _$$GameTimeImplFromJson(json);

  @override
  @JsonKey()
  final int seconds;
  @override
  final String? label;

  @override
  String toString() {
    return 'GameTime(seconds: $seconds, label: $label)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GameTimeImpl &&
            (identical(other.seconds, seconds) || other.seconds == seconds) &&
            (identical(other.label, label) || other.label == label));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, seconds, label);

  /// Create a copy of GameTime
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GameTimeImplCopyWith<_$GameTimeImpl> get copyWith =>
      __$$GameTimeImplCopyWithImpl<_$GameTimeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GameTimeImplToJson(this);
  }
}

abstract class _GameTime implements GameTime {
  const factory _GameTime({final int seconds, final String? label}) =
      _$GameTimeImpl;

  factory _GameTime.fromJson(Map<String, dynamic> json) =
      _$GameTimeImpl.fromJson;

  @override
  int get seconds;
  @override
  String? get label;

  /// Create a copy of GameTime
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GameTimeImplCopyWith<_$GameTimeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
