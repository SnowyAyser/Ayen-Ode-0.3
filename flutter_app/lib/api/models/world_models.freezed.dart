// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'world_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

World _$WorldFromJson(Map<String, dynamic> json) {
  return _World.fromJson(json);
}

/// @nodoc
mixin _$World {
  String get worldId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String? get premise => throw _privateConstructorUsedError;
  String? get themeTone => throw _privateConstructorUsedError;
  String? get playerRole => throw _privateConstructorUsedError;
  String? get status => throw _privateConstructorUsedError;
  GameTime? get gameTime => throw _privateConstructorUsedError;

  /// Serializes this World to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WorldCopyWith<World> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WorldCopyWith<$Res> {
  factory $WorldCopyWith(World value, $Res Function(World) then) =
      _$WorldCopyWithImpl<$Res, World>;
  @useResult
  $Res call({
    String worldId,
    String name,
    String? premise,
    String? themeTone,
    String? playerRole,
    String? status,
    GameTime? gameTime,
  });

  $GameTimeCopyWith<$Res>? get gameTime;
}

/// @nodoc
class _$WorldCopyWithImpl<$Res, $Val extends World>
    implements $WorldCopyWith<$Res> {
  _$WorldCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? name = null,
    Object? premise = freezed,
    Object? themeTone = freezed,
    Object? playerRole = freezed,
    Object? status = freezed,
    Object? gameTime = freezed,
  }) {
    return _then(
      _value.copyWith(
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            premise: freezed == premise
                ? _value.premise
                : premise // ignore: cast_nullable_to_non_nullable
                      as String?,
            themeTone: freezed == themeTone
                ? _value.themeTone
                : themeTone // ignore: cast_nullable_to_non_nullable
                      as String?,
            playerRole: freezed == playerRole
                ? _value.playerRole
                : playerRole // ignore: cast_nullable_to_non_nullable
                      as String?,
            status: freezed == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as String?,
            gameTime: freezed == gameTime
                ? _value.gameTime
                : gameTime // ignore: cast_nullable_to_non_nullable
                      as GameTime?,
          )
          as $Val,
    );
  }

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GameTimeCopyWith<$Res>? get gameTime {
    if (_value.gameTime == null) {
      return null;
    }

    return $GameTimeCopyWith<$Res>(_value.gameTime!, (value) {
      return _then(_value.copyWith(gameTime: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$WorldImplCopyWith<$Res> implements $WorldCopyWith<$Res> {
  factory _$$WorldImplCopyWith(
    _$WorldImpl value,
    $Res Function(_$WorldImpl) then,
  ) = __$$WorldImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String worldId,
    String name,
    String? premise,
    String? themeTone,
    String? playerRole,
    String? status,
    GameTime? gameTime,
  });

  @override
  $GameTimeCopyWith<$Res>? get gameTime;
}

/// @nodoc
class __$$WorldImplCopyWithImpl<$Res>
    extends _$WorldCopyWithImpl<$Res, _$WorldImpl>
    implements _$$WorldImplCopyWith<$Res> {
  __$$WorldImplCopyWithImpl(
    _$WorldImpl _value,
    $Res Function(_$WorldImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? name = null,
    Object? premise = freezed,
    Object? themeTone = freezed,
    Object? playerRole = freezed,
    Object? status = freezed,
    Object? gameTime = freezed,
  }) {
    return _then(
      _$WorldImpl(
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        premise: freezed == premise
            ? _value.premise
            : premise // ignore: cast_nullable_to_non_nullable
                  as String?,
        themeTone: freezed == themeTone
            ? _value.themeTone
            : themeTone // ignore: cast_nullable_to_non_nullable
                  as String?,
        playerRole: freezed == playerRole
            ? _value.playerRole
            : playerRole // ignore: cast_nullable_to_non_nullable
                  as String?,
        status: freezed == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as String?,
        gameTime: freezed == gameTime
            ? _value.gameTime
            : gameTime // ignore: cast_nullable_to_non_nullable
                  as GameTime?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$WorldImpl implements _World {
  const _$WorldImpl({
    required this.worldId,
    required this.name,
    this.premise,
    this.themeTone,
    this.playerRole,
    this.status,
    this.gameTime,
  });

  factory _$WorldImpl.fromJson(Map<String, dynamic> json) =>
      _$$WorldImplFromJson(json);

  @override
  final String worldId;
  @override
  final String name;
  @override
  final String? premise;
  @override
  final String? themeTone;
  @override
  final String? playerRole;
  @override
  final String? status;
  @override
  final GameTime? gameTime;

  @override
  String toString() {
    return 'World(worldId: $worldId, name: $name, premise: $premise, themeTone: $themeTone, playerRole: $playerRole, status: $status, gameTime: $gameTime)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WorldImpl &&
            (identical(other.worldId, worldId) || other.worldId == worldId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.premise, premise) || other.premise == premise) &&
            (identical(other.themeTone, themeTone) ||
                other.themeTone == themeTone) &&
            (identical(other.playerRole, playerRole) ||
                other.playerRole == playerRole) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.gameTime, gameTime) ||
                other.gameTime == gameTime));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    worldId,
    name,
    premise,
    themeTone,
    playerRole,
    status,
    gameTime,
  );

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WorldImplCopyWith<_$WorldImpl> get copyWith =>
      __$$WorldImplCopyWithImpl<_$WorldImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WorldImplToJson(this);
  }
}

abstract class _World implements World {
  const factory _World({
    required final String worldId,
    required final String name,
    final String? premise,
    final String? themeTone,
    final String? playerRole,
    final String? status,
    final GameTime? gameTime,
  }) = _$WorldImpl;

  factory _World.fromJson(Map<String, dynamic> json) = _$WorldImpl.fromJson;

  @override
  String get worldId;
  @override
  String get name;
  @override
  String? get premise;
  @override
  String? get themeTone;
  @override
  String? get playerRole;
  @override
  String? get status;
  @override
  GameTime? get gameTime;

  /// Create a copy of World
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WorldImplCopyWith<_$WorldImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WorldListResponse _$WorldListResponseFromJson(Map<String, dynamic> json) {
  return _WorldListResponse.fromJson(json);
}

/// @nodoc
mixin _$WorldListResponse {
  List<World> get worlds => throw _privateConstructorUsedError;

  /// Serializes this WorldListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WorldListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WorldListResponseCopyWith<WorldListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WorldListResponseCopyWith<$Res> {
  factory $WorldListResponseCopyWith(
    WorldListResponse value,
    $Res Function(WorldListResponse) then,
  ) = _$WorldListResponseCopyWithImpl<$Res, WorldListResponse>;
  @useResult
  $Res call({List<World> worlds});
}

/// @nodoc
class _$WorldListResponseCopyWithImpl<$Res, $Val extends WorldListResponse>
    implements $WorldListResponseCopyWith<$Res> {
  _$WorldListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WorldListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? worlds = null}) {
    return _then(
      _value.copyWith(
            worlds: null == worlds
                ? _value.worlds
                : worlds // ignore: cast_nullable_to_non_nullable
                      as List<World>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$WorldListResponseImplCopyWith<$Res>
    implements $WorldListResponseCopyWith<$Res> {
  factory _$$WorldListResponseImplCopyWith(
    _$WorldListResponseImpl value,
    $Res Function(_$WorldListResponseImpl) then,
  ) = __$$WorldListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<World> worlds});
}

/// @nodoc
class __$$WorldListResponseImplCopyWithImpl<$Res>
    extends _$WorldListResponseCopyWithImpl<$Res, _$WorldListResponseImpl>
    implements _$$WorldListResponseImplCopyWith<$Res> {
  __$$WorldListResponseImplCopyWithImpl(
    _$WorldListResponseImpl _value,
    $Res Function(_$WorldListResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of WorldListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? worlds = null}) {
    return _then(
      _$WorldListResponseImpl(
        worlds: null == worlds
            ? _value._worlds
            : worlds // ignore: cast_nullable_to_non_nullable
                  as List<World>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$WorldListResponseImpl implements _WorldListResponse {
  const _$WorldListResponseImpl({final List<World> worlds = const <World>[]})
    : _worlds = worlds;

  factory _$WorldListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$WorldListResponseImplFromJson(json);

  final List<World> _worlds;
  @override
  @JsonKey()
  List<World> get worlds {
    if (_worlds is EqualUnmodifiableListView) return _worlds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_worlds);
  }

  @override
  String toString() {
    return 'WorldListResponse(worlds: $worlds)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WorldListResponseImpl &&
            const DeepCollectionEquality().equals(other._worlds, _worlds));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_worlds));

  /// Create a copy of WorldListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WorldListResponseImplCopyWith<_$WorldListResponseImpl> get copyWith =>
      __$$WorldListResponseImplCopyWithImpl<_$WorldListResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$WorldListResponseImplToJson(this);
  }
}

abstract class _WorldListResponse implements WorldListResponse {
  const factory _WorldListResponse({final List<World> worlds}) =
      _$WorldListResponseImpl;

  factory _WorldListResponse.fromJson(Map<String, dynamic> json) =
      _$WorldListResponseImpl.fromJson;

  @override
  List<World> get worlds;

  /// Create a copy of WorldListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WorldListResponseImplCopyWith<_$WorldListResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ActiveWorldResponse _$ActiveWorldResponseFromJson(Map<String, dynamic> json) {
  return _ActiveWorldResponse.fromJson(json);
}

/// @nodoc
mixin _$ActiveWorldResponse {
  World? get world => throw _privateConstructorUsedError;

  /// Serializes this ActiveWorldResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ActiveWorldResponseCopyWith<ActiveWorldResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ActiveWorldResponseCopyWith<$Res> {
  factory $ActiveWorldResponseCopyWith(
    ActiveWorldResponse value,
    $Res Function(ActiveWorldResponse) then,
  ) = _$ActiveWorldResponseCopyWithImpl<$Res, ActiveWorldResponse>;
  @useResult
  $Res call({World? world});

  $WorldCopyWith<$Res>? get world;
}

/// @nodoc
class _$ActiveWorldResponseCopyWithImpl<$Res, $Val extends ActiveWorldResponse>
    implements $ActiveWorldResponseCopyWith<$Res> {
  _$ActiveWorldResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? world = freezed}) {
    return _then(
      _value.copyWith(
            world: freezed == world
                ? _value.world
                : world // ignore: cast_nullable_to_non_nullable
                      as World?,
          )
          as $Val,
    );
  }

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $WorldCopyWith<$Res>? get world {
    if (_value.world == null) {
      return null;
    }

    return $WorldCopyWith<$Res>(_value.world!, (value) {
      return _then(_value.copyWith(world: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ActiveWorldResponseImplCopyWith<$Res>
    implements $ActiveWorldResponseCopyWith<$Res> {
  factory _$$ActiveWorldResponseImplCopyWith(
    _$ActiveWorldResponseImpl value,
    $Res Function(_$ActiveWorldResponseImpl) then,
  ) = __$$ActiveWorldResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({World? world});

  @override
  $WorldCopyWith<$Res>? get world;
}

/// @nodoc
class __$$ActiveWorldResponseImplCopyWithImpl<$Res>
    extends _$ActiveWorldResponseCopyWithImpl<$Res, _$ActiveWorldResponseImpl>
    implements _$$ActiveWorldResponseImplCopyWith<$Res> {
  __$$ActiveWorldResponseImplCopyWithImpl(
    _$ActiveWorldResponseImpl _value,
    $Res Function(_$ActiveWorldResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? world = freezed}) {
    return _then(
      _$ActiveWorldResponseImpl(
        world: freezed == world
            ? _value.world
            : world // ignore: cast_nullable_to_non_nullable
                  as World?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ActiveWorldResponseImpl implements _ActiveWorldResponse {
  const _$ActiveWorldResponseImpl({this.world});

  factory _$ActiveWorldResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ActiveWorldResponseImplFromJson(json);

  @override
  final World? world;

  @override
  String toString() {
    return 'ActiveWorldResponse(world: $world)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ActiveWorldResponseImpl &&
            (identical(other.world, world) || other.world == world));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, world);

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ActiveWorldResponseImplCopyWith<_$ActiveWorldResponseImpl> get copyWith =>
      __$$ActiveWorldResponseImplCopyWithImpl<_$ActiveWorldResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$ActiveWorldResponseImplToJson(this);
  }
}

abstract class _ActiveWorldResponse implements ActiveWorldResponse {
  const factory _ActiveWorldResponse({final World? world}) =
      _$ActiveWorldResponseImpl;

  factory _ActiveWorldResponse.fromJson(Map<String, dynamic> json) =
      _$ActiveWorldResponseImpl.fromJson;

  @override
  World? get world;

  /// Create a copy of ActiveWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ActiveWorldResponseImplCopyWith<_$ActiveWorldResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreateWorldRequest _$CreateWorldRequestFromJson(Map<String, dynamic> json) {
  return _CreateWorldRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateWorldRequest {
  String get name => throw _privateConstructorUsedError;
  String get premise => throw _privateConstructorUsedError;
  String? get themeTone => throw _privateConstructorUsedError;
  String? get playerRole => throw _privateConstructorUsedError;

  /// Serializes this CreateWorldRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateWorldRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateWorldRequestCopyWith<CreateWorldRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateWorldRequestCopyWith<$Res> {
  factory $CreateWorldRequestCopyWith(
    CreateWorldRequest value,
    $Res Function(CreateWorldRequest) then,
  ) = _$CreateWorldRequestCopyWithImpl<$Res, CreateWorldRequest>;
  @useResult
  $Res call({
    String name,
    String premise,
    String? themeTone,
    String? playerRole,
  });
}

/// @nodoc
class _$CreateWorldRequestCopyWithImpl<$Res, $Val extends CreateWorldRequest>
    implements $CreateWorldRequestCopyWith<$Res> {
  _$CreateWorldRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateWorldRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? premise = null,
    Object? themeTone = freezed,
    Object? playerRole = freezed,
  }) {
    return _then(
      _value.copyWith(
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            premise: null == premise
                ? _value.premise
                : premise // ignore: cast_nullable_to_non_nullable
                      as String,
            themeTone: freezed == themeTone
                ? _value.themeTone
                : themeTone // ignore: cast_nullable_to_non_nullable
                      as String?,
            playerRole: freezed == playerRole
                ? _value.playerRole
                : playerRole // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CreateWorldRequestImplCopyWith<$Res>
    implements $CreateWorldRequestCopyWith<$Res> {
  factory _$$CreateWorldRequestImplCopyWith(
    _$CreateWorldRequestImpl value,
    $Res Function(_$CreateWorldRequestImpl) then,
  ) = __$$CreateWorldRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String name,
    String premise,
    String? themeTone,
    String? playerRole,
  });
}

/// @nodoc
class __$$CreateWorldRequestImplCopyWithImpl<$Res>
    extends _$CreateWorldRequestCopyWithImpl<$Res, _$CreateWorldRequestImpl>
    implements _$$CreateWorldRequestImplCopyWith<$Res> {
  __$$CreateWorldRequestImplCopyWithImpl(
    _$CreateWorldRequestImpl _value,
    $Res Function(_$CreateWorldRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CreateWorldRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? premise = null,
    Object? themeTone = freezed,
    Object? playerRole = freezed,
  }) {
    return _then(
      _$CreateWorldRequestImpl(
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        premise: null == premise
            ? _value.premise
            : premise // ignore: cast_nullable_to_non_nullable
                  as String,
        themeTone: freezed == themeTone
            ? _value.themeTone
            : themeTone // ignore: cast_nullable_to_non_nullable
                  as String?,
        playerRole: freezed == playerRole
            ? _value.playerRole
            : playerRole // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateWorldRequestImpl implements _CreateWorldRequest {
  const _$CreateWorldRequestImpl({
    required this.name,
    required this.premise,
    this.themeTone,
    this.playerRole,
  });

  factory _$CreateWorldRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateWorldRequestImplFromJson(json);

  @override
  final String name;
  @override
  final String premise;
  @override
  final String? themeTone;
  @override
  final String? playerRole;

  @override
  String toString() {
    return 'CreateWorldRequest(name: $name, premise: $premise, themeTone: $themeTone, playerRole: $playerRole)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateWorldRequestImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.premise, premise) || other.premise == premise) &&
            (identical(other.themeTone, themeTone) ||
                other.themeTone == themeTone) &&
            (identical(other.playerRole, playerRole) ||
                other.playerRole == playerRole));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, name, premise, themeTone, playerRole);

  /// Create a copy of CreateWorldRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateWorldRequestImplCopyWith<_$CreateWorldRequestImpl> get copyWith =>
      __$$CreateWorldRequestImplCopyWithImpl<_$CreateWorldRequestImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateWorldRequestImplToJson(this);
  }
}

abstract class _CreateWorldRequest implements CreateWorldRequest {
  const factory _CreateWorldRequest({
    required final String name,
    required final String premise,
    final String? themeTone,
    final String? playerRole,
  }) = _$CreateWorldRequestImpl;

  factory _CreateWorldRequest.fromJson(Map<String, dynamic> json) =
      _$CreateWorldRequestImpl.fromJson;

  @override
  String get name;
  @override
  String get premise;
  @override
  String? get themeTone;
  @override
  String? get playerRole;

  /// Create a copy of CreateWorldRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateWorldRequestImplCopyWith<_$CreateWorldRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreateWorldResponse _$CreateWorldResponseFromJson(Map<String, dynamic> json) {
  return _CreateWorldResponse.fromJson(json);
}

/// @nodoc
mixin _$CreateWorldResponse {
  String get worldId => throw _privateConstructorUsedError;

  /// Serializes this CreateWorldResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateWorldResponseCopyWith<CreateWorldResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateWorldResponseCopyWith<$Res> {
  factory $CreateWorldResponseCopyWith(
    CreateWorldResponse value,
    $Res Function(CreateWorldResponse) then,
  ) = _$CreateWorldResponseCopyWithImpl<$Res, CreateWorldResponse>;
  @useResult
  $Res call({String worldId});
}

/// @nodoc
class _$CreateWorldResponseCopyWithImpl<$Res, $Val extends CreateWorldResponse>
    implements $CreateWorldResponseCopyWith<$Res> {
  _$CreateWorldResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? worldId = null}) {
    return _then(
      _value.copyWith(
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CreateWorldResponseImplCopyWith<$Res>
    implements $CreateWorldResponseCopyWith<$Res> {
  factory _$$CreateWorldResponseImplCopyWith(
    _$CreateWorldResponseImpl value,
    $Res Function(_$CreateWorldResponseImpl) then,
  ) = __$$CreateWorldResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String worldId});
}

/// @nodoc
class __$$CreateWorldResponseImplCopyWithImpl<$Res>
    extends _$CreateWorldResponseCopyWithImpl<$Res, _$CreateWorldResponseImpl>
    implements _$$CreateWorldResponseImplCopyWith<$Res> {
  __$$CreateWorldResponseImplCopyWithImpl(
    _$CreateWorldResponseImpl _value,
    $Res Function(_$CreateWorldResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CreateWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? worldId = null}) {
    return _then(
      _$CreateWorldResponseImpl(
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateWorldResponseImpl implements _CreateWorldResponse {
  const _$CreateWorldResponseImpl({required this.worldId});

  factory _$CreateWorldResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateWorldResponseImplFromJson(json);

  @override
  final String worldId;

  @override
  String toString() {
    return 'CreateWorldResponse(worldId: $worldId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateWorldResponseImpl &&
            (identical(other.worldId, worldId) || other.worldId == worldId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, worldId);

  /// Create a copy of CreateWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateWorldResponseImplCopyWith<_$CreateWorldResponseImpl> get copyWith =>
      __$$CreateWorldResponseImplCopyWithImpl<_$CreateWorldResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateWorldResponseImplToJson(this);
  }
}

abstract class _CreateWorldResponse implements CreateWorldResponse {
  const factory _CreateWorldResponse({required final String worldId}) =
      _$CreateWorldResponseImpl;

  factory _CreateWorldResponse.fromJson(Map<String, dynamic> json) =
      _$CreateWorldResponseImpl.fromJson;

  @override
  String get worldId;

  /// Create a copy of CreateWorldResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateWorldResponseImplCopyWith<_$CreateWorldResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WorldDetailResponse _$WorldDetailResponseFromJson(Map<String, dynamic> json) {
  return _WorldDetailResponse.fromJson(json);
}

/// @nodoc
mixin _$WorldDetailResponse {
  bool get success => throw _privateConstructorUsedError;
  World get world => throw _privateConstructorUsedError;
  String get worldId => throw _privateConstructorUsedError;
  List<Entity> get entities => throw _privateConstructorUsedError;
  String? get handoff => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Serializes this WorldDetailResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WorldDetailResponseCopyWith<WorldDetailResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WorldDetailResponseCopyWith<$Res> {
  factory $WorldDetailResponseCopyWith(
    WorldDetailResponse value,
    $Res Function(WorldDetailResponse) then,
  ) = _$WorldDetailResponseCopyWithImpl<$Res, WorldDetailResponse>;
  @useResult
  $Res call({
    bool success,
    World world,
    String worldId,
    List<Entity> entities,
    String? handoff,
    String? error,
  });

  $WorldCopyWith<$Res> get world;
}

/// @nodoc
class _$WorldDetailResponseCopyWithImpl<$Res, $Val extends WorldDetailResponse>
    implements $WorldDetailResponseCopyWith<$Res> {
  _$WorldDetailResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? world = null,
    Object? worldId = null,
    Object? entities = null,
    Object? handoff = freezed,
    Object? error = freezed,
  }) {
    return _then(
      _value.copyWith(
            success: null == success
                ? _value.success
                : success // ignore: cast_nullable_to_non_nullable
                      as bool,
            world: null == world
                ? _value.world
                : world // ignore: cast_nullable_to_non_nullable
                      as World,
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
            entities: null == entities
                ? _value.entities
                : entities // ignore: cast_nullable_to_non_nullable
                      as List<Entity>,
            handoff: freezed == handoff
                ? _value.handoff
                : handoff // ignore: cast_nullable_to_non_nullable
                      as String?,
            error: freezed == error
                ? _value.error
                : error // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $WorldCopyWith<$Res> get world {
    return $WorldCopyWith<$Res>(_value.world, (value) {
      return _then(_value.copyWith(world: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$WorldDetailResponseImplCopyWith<$Res>
    implements $WorldDetailResponseCopyWith<$Res> {
  factory _$$WorldDetailResponseImplCopyWith(
    _$WorldDetailResponseImpl value,
    $Res Function(_$WorldDetailResponseImpl) then,
  ) = __$$WorldDetailResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    bool success,
    World world,
    String worldId,
    List<Entity> entities,
    String? handoff,
    String? error,
  });

  @override
  $WorldCopyWith<$Res> get world;
}

/// @nodoc
class __$$WorldDetailResponseImplCopyWithImpl<$Res>
    extends _$WorldDetailResponseCopyWithImpl<$Res, _$WorldDetailResponseImpl>
    implements _$$WorldDetailResponseImplCopyWith<$Res> {
  __$$WorldDetailResponseImplCopyWithImpl(
    _$WorldDetailResponseImpl _value,
    $Res Function(_$WorldDetailResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? world = null,
    Object? worldId = null,
    Object? entities = null,
    Object? handoff = freezed,
    Object? error = freezed,
  }) {
    return _then(
      _$WorldDetailResponseImpl(
        success: null == success
            ? _value.success
            : success // ignore: cast_nullable_to_non_nullable
                  as bool,
        world: null == world
            ? _value.world
            : world // ignore: cast_nullable_to_non_nullable
                  as World,
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
        entities: null == entities
            ? _value._entities
            : entities // ignore: cast_nullable_to_non_nullable
                  as List<Entity>,
        handoff: freezed == handoff
            ? _value.handoff
            : handoff // ignore: cast_nullable_to_non_nullable
                  as String?,
        error: freezed == error
            ? _value.error
            : error // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$WorldDetailResponseImpl implements _WorldDetailResponse {
  const _$WorldDetailResponseImpl({
    required this.success,
    required this.world,
    required this.worldId,
    final List<Entity> entities = const <Entity>[],
    this.handoff,
    this.error,
  }) : _entities = entities;

  factory _$WorldDetailResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$WorldDetailResponseImplFromJson(json);

  @override
  final bool success;
  @override
  final World world;
  @override
  final String worldId;
  final List<Entity> _entities;
  @override
  @JsonKey()
  List<Entity> get entities {
    if (_entities is EqualUnmodifiableListView) return _entities;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_entities);
  }

  @override
  final String? handoff;
  @override
  final String? error;

  @override
  String toString() {
    return 'WorldDetailResponse(success: $success, world: $world, worldId: $worldId, entities: $entities, handoff: $handoff, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WorldDetailResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.world, world) || other.world == world) &&
            (identical(other.worldId, worldId) || other.worldId == worldId) &&
            const DeepCollectionEquality().equals(other._entities, _entities) &&
            (identical(other.handoff, handoff) || other.handoff == handoff) &&
            (identical(other.error, error) || other.error == error));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    success,
    world,
    worldId,
    const DeepCollectionEquality().hash(_entities),
    handoff,
    error,
  );

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WorldDetailResponseImplCopyWith<_$WorldDetailResponseImpl> get copyWith =>
      __$$WorldDetailResponseImplCopyWithImpl<_$WorldDetailResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$WorldDetailResponseImplToJson(this);
  }
}

abstract class _WorldDetailResponse implements WorldDetailResponse {
  const factory _WorldDetailResponse({
    required final bool success,
    required final World world,
    required final String worldId,
    final List<Entity> entities,
    final String? handoff,
    final String? error,
  }) = _$WorldDetailResponseImpl;

  factory _WorldDetailResponse.fromJson(Map<String, dynamic> json) =
      _$WorldDetailResponseImpl.fromJson;

  @override
  bool get success;
  @override
  World get world;
  @override
  String get worldId;
  @override
  List<Entity> get entities;
  @override
  String? get handoff;
  @override
  String? get error;

  /// Create a copy of WorldDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WorldDetailResponseImplCopyWith<_$WorldDetailResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CurrencyBalance _$CurrencyBalanceFromJson(Map<String, dynamic> json) {
  return _CurrencyBalance.fromJson(json);
}

/// @nodoc
mixin _$CurrencyBalance {
  int get balance => throw _privateConstructorUsedError;
  int get maxBalance => throw _privateConstructorUsedError;
  int get points => throw _privateConstructorUsedError;
  int get maxPoints => throw _privateConstructorUsedError;

  /// Serializes this CurrencyBalance to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CurrencyBalance
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CurrencyBalanceCopyWith<CurrencyBalance> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CurrencyBalanceCopyWith<$Res> {
  factory $CurrencyBalanceCopyWith(
    CurrencyBalance value,
    $Res Function(CurrencyBalance) then,
  ) = _$CurrencyBalanceCopyWithImpl<$Res, CurrencyBalance>;
  @useResult
  $Res call({int balance, int maxBalance, int points, int maxPoints});
}

/// @nodoc
class _$CurrencyBalanceCopyWithImpl<$Res, $Val extends CurrencyBalance>
    implements $CurrencyBalanceCopyWith<$Res> {
  _$CurrencyBalanceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CurrencyBalance
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? balance = null,
    Object? maxBalance = null,
    Object? points = null,
    Object? maxPoints = null,
  }) {
    return _then(
      _value.copyWith(
            balance: null == balance
                ? _value.balance
                : balance // ignore: cast_nullable_to_non_nullable
                      as int,
            maxBalance: null == maxBalance
                ? _value.maxBalance
                : maxBalance // ignore: cast_nullable_to_non_nullable
                      as int,
            points: null == points
                ? _value.points
                : points // ignore: cast_nullable_to_non_nullable
                      as int,
            maxPoints: null == maxPoints
                ? _value.maxPoints
                : maxPoints // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CurrencyBalanceImplCopyWith<$Res>
    implements $CurrencyBalanceCopyWith<$Res> {
  factory _$$CurrencyBalanceImplCopyWith(
    _$CurrencyBalanceImpl value,
    $Res Function(_$CurrencyBalanceImpl) then,
  ) = __$$CurrencyBalanceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int balance, int maxBalance, int points, int maxPoints});
}

/// @nodoc
class __$$CurrencyBalanceImplCopyWithImpl<$Res>
    extends _$CurrencyBalanceCopyWithImpl<$Res, _$CurrencyBalanceImpl>
    implements _$$CurrencyBalanceImplCopyWith<$Res> {
  __$$CurrencyBalanceImplCopyWithImpl(
    _$CurrencyBalanceImpl _value,
    $Res Function(_$CurrencyBalanceImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CurrencyBalance
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? balance = null,
    Object? maxBalance = null,
    Object? points = null,
    Object? maxPoints = null,
  }) {
    return _then(
      _$CurrencyBalanceImpl(
        balance: null == balance
            ? _value.balance
            : balance // ignore: cast_nullable_to_non_nullable
                  as int,
        maxBalance: null == maxBalance
            ? _value.maxBalance
            : maxBalance // ignore: cast_nullable_to_non_nullable
                  as int,
        points: null == points
            ? _value.points
            : points // ignore: cast_nullable_to_non_nullable
                  as int,
        maxPoints: null == maxPoints
            ? _value.maxPoints
            : maxPoints // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CurrencyBalanceImpl implements _CurrencyBalance {
  const _$CurrencyBalanceImpl({
    this.balance = 0,
    this.maxBalance = 5,
    this.points = 0,
    this.maxPoints = 5,
  });

  factory _$CurrencyBalanceImpl.fromJson(Map<String, dynamic> json) =>
      _$$CurrencyBalanceImplFromJson(json);

  @override
  @JsonKey()
  final int balance;
  @override
  @JsonKey()
  final int maxBalance;
  @override
  @JsonKey()
  final int points;
  @override
  @JsonKey()
  final int maxPoints;

  @override
  String toString() {
    return 'CurrencyBalance(balance: $balance, maxBalance: $maxBalance, points: $points, maxPoints: $maxPoints)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CurrencyBalanceImpl &&
            (identical(other.balance, balance) || other.balance == balance) &&
            (identical(other.maxBalance, maxBalance) ||
                other.maxBalance == maxBalance) &&
            (identical(other.points, points) || other.points == points) &&
            (identical(other.maxPoints, maxPoints) ||
                other.maxPoints == maxPoints));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, balance, maxBalance, points, maxPoints);

  /// Create a copy of CurrencyBalance
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CurrencyBalanceImplCopyWith<_$CurrencyBalanceImpl> get copyWith =>
      __$$CurrencyBalanceImplCopyWithImpl<_$CurrencyBalanceImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$CurrencyBalanceImplToJson(this);
  }
}

abstract class _CurrencyBalance implements CurrencyBalance {
  const factory _CurrencyBalance({
    final int balance,
    final int maxBalance,
    final int points,
    final int maxPoints,
  }) = _$CurrencyBalanceImpl;

  factory _CurrencyBalance.fromJson(Map<String, dynamic> json) =
      _$CurrencyBalanceImpl.fromJson;

  @override
  int get balance;
  @override
  int get maxBalance;
  @override
  int get points;
  @override
  int get maxPoints;

  /// Create a copy of CurrencyBalance
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CurrencyBalanceImplCopyWith<_$CurrencyBalanceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CurrencyRestoreResponse _$CurrencyRestoreResponseFromJson(
  Map<String, dynamic> json,
) {
  return _CurrencyRestoreResponse.fromJson(json);
}

/// @nodoc
mixin _$CurrencyRestoreResponse {
  int get balanceAfter => throw _privateConstructorUsedError;
  int get maxBalance => throw _privateConstructorUsedError;

  /// Serializes this CurrencyRestoreResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CurrencyRestoreResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CurrencyRestoreResponseCopyWith<CurrencyRestoreResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CurrencyRestoreResponseCopyWith<$Res> {
  factory $CurrencyRestoreResponseCopyWith(
    CurrencyRestoreResponse value,
    $Res Function(CurrencyRestoreResponse) then,
  ) = _$CurrencyRestoreResponseCopyWithImpl<$Res, CurrencyRestoreResponse>;
  @useResult
  $Res call({int balanceAfter, int maxBalance});
}

/// @nodoc
class _$CurrencyRestoreResponseCopyWithImpl<
  $Res,
  $Val extends CurrencyRestoreResponse
>
    implements $CurrencyRestoreResponseCopyWith<$Res> {
  _$CurrencyRestoreResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CurrencyRestoreResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? balanceAfter = null, Object? maxBalance = null}) {
    return _then(
      _value.copyWith(
            balanceAfter: null == balanceAfter
                ? _value.balanceAfter
                : balanceAfter // ignore: cast_nullable_to_non_nullable
                      as int,
            maxBalance: null == maxBalance
                ? _value.maxBalance
                : maxBalance // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CurrencyRestoreResponseImplCopyWith<$Res>
    implements $CurrencyRestoreResponseCopyWith<$Res> {
  factory _$$CurrencyRestoreResponseImplCopyWith(
    _$CurrencyRestoreResponseImpl value,
    $Res Function(_$CurrencyRestoreResponseImpl) then,
  ) = __$$CurrencyRestoreResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int balanceAfter, int maxBalance});
}

/// @nodoc
class __$$CurrencyRestoreResponseImplCopyWithImpl<$Res>
    extends
        _$CurrencyRestoreResponseCopyWithImpl<
          $Res,
          _$CurrencyRestoreResponseImpl
        >
    implements _$$CurrencyRestoreResponseImplCopyWith<$Res> {
  __$$CurrencyRestoreResponseImplCopyWithImpl(
    _$CurrencyRestoreResponseImpl _value,
    $Res Function(_$CurrencyRestoreResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CurrencyRestoreResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? balanceAfter = null, Object? maxBalance = null}) {
    return _then(
      _$CurrencyRestoreResponseImpl(
        balanceAfter: null == balanceAfter
            ? _value.balanceAfter
            : balanceAfter // ignore: cast_nullable_to_non_nullable
                  as int,
        maxBalance: null == maxBalance
            ? _value.maxBalance
            : maxBalance // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CurrencyRestoreResponseImpl implements _CurrencyRestoreResponse {
  const _$CurrencyRestoreResponseImpl({
    this.balanceAfter = 0,
    this.maxBalance = 5,
  });

  factory _$CurrencyRestoreResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$CurrencyRestoreResponseImplFromJson(json);

  @override
  @JsonKey()
  final int balanceAfter;
  @override
  @JsonKey()
  final int maxBalance;

  @override
  String toString() {
    return 'CurrencyRestoreResponse(balanceAfter: $balanceAfter, maxBalance: $maxBalance)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CurrencyRestoreResponseImpl &&
            (identical(other.balanceAfter, balanceAfter) ||
                other.balanceAfter == balanceAfter) &&
            (identical(other.maxBalance, maxBalance) ||
                other.maxBalance == maxBalance));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, balanceAfter, maxBalance);

  /// Create a copy of CurrencyRestoreResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CurrencyRestoreResponseImplCopyWith<_$CurrencyRestoreResponseImpl>
  get copyWith =>
      __$$CurrencyRestoreResponseImplCopyWithImpl<
        _$CurrencyRestoreResponseImpl
      >(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CurrencyRestoreResponseImplToJson(this);
  }
}

abstract class _CurrencyRestoreResponse implements CurrencyRestoreResponse {
  const factory _CurrencyRestoreResponse({
    final int balanceAfter,
    final int maxBalance,
  }) = _$CurrencyRestoreResponseImpl;

  factory _CurrencyRestoreResponse.fromJson(Map<String, dynamic> json) =
      _$CurrencyRestoreResponseImpl.fromJson;

  @override
  int get balanceAfter;
  @override
  int get maxBalance;

  /// Create a copy of CurrencyRestoreResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CurrencyRestoreResponseImplCopyWith<_$CurrencyRestoreResponseImpl>
  get copyWith => throw _privateConstructorUsedError;
}
