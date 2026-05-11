// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'entity_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Entity _$EntityFromJson(Map<String, dynamic> json) {
  return _Entity.fromJson(json);
}

/// @nodoc
mixin _$Entity {
  String get entityId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;

  /// `character`, `location`, `faction`, `object`, `event`, or `unknown`.
  /// Note the backend sometimes returns the type under `type`, sometimes
  /// under `entity_type`; we accept either by mapping in the API layer.
  String? get entityType => throw _privateConstructorUsedError;
  String? get type => throw _privateConstructorUsedError;
  String? get summary => throw _privateConstructorUsedError;
  String? get status => throw _privateConstructorUsedError;
  List<String> get tags => throw _privateConstructorUsedError;
  List<String> get timelineNotes => throw _privateConstructorUsedError;
  List<String> get openQuestions => throw _privateConstructorUsedError;

  /// Serializes this Entity to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Entity
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityCopyWith<Entity> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityCopyWith<$Res> {
  factory $EntityCopyWith(Entity value, $Res Function(Entity) then) =
      _$EntityCopyWithImpl<$Res, Entity>;
  @useResult
  $Res call({
    String entityId,
    String name,
    String? entityType,
    String? type,
    String? summary,
    String? status,
    List<String> tags,
    List<String> timelineNotes,
    List<String> openQuestions,
  });
}

/// @nodoc
class _$EntityCopyWithImpl<$Res, $Val extends Entity>
    implements $EntityCopyWith<$Res> {
  _$EntityCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Entity
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityId = null,
    Object? name = null,
    Object? entityType = freezed,
    Object? type = freezed,
    Object? summary = freezed,
    Object? status = freezed,
    Object? tags = null,
    Object? timelineNotes = null,
    Object? openQuestions = null,
  }) {
    return _then(
      _value.copyWith(
            entityId: null == entityId
                ? _value.entityId
                : entityId // ignore: cast_nullable_to_non_nullable
                      as String,
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            entityType: freezed == entityType
                ? _value.entityType
                : entityType // ignore: cast_nullable_to_non_nullable
                      as String?,
            type: freezed == type
                ? _value.type
                : type // ignore: cast_nullable_to_non_nullable
                      as String?,
            summary: freezed == summary
                ? _value.summary
                : summary // ignore: cast_nullable_to_non_nullable
                      as String?,
            status: freezed == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as String?,
            tags: null == tags
                ? _value.tags
                : tags // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            timelineNotes: null == timelineNotes
                ? _value.timelineNotes
                : timelineNotes // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            openQuestions: null == openQuestions
                ? _value.openQuestions
                : openQuestions // ignore: cast_nullable_to_non_nullable
                      as List<String>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$EntityImplCopyWith<$Res> implements $EntityCopyWith<$Res> {
  factory _$$EntityImplCopyWith(
    _$EntityImpl value,
    $Res Function(_$EntityImpl) then,
  ) = __$$EntityImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String entityId,
    String name,
    String? entityType,
    String? type,
    String? summary,
    String? status,
    List<String> tags,
    List<String> timelineNotes,
    List<String> openQuestions,
  });
}

/// @nodoc
class __$$EntityImplCopyWithImpl<$Res>
    extends _$EntityCopyWithImpl<$Res, _$EntityImpl>
    implements _$$EntityImplCopyWith<$Res> {
  __$$EntityImplCopyWithImpl(
    _$EntityImpl _value,
    $Res Function(_$EntityImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Entity
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityId = null,
    Object? name = null,
    Object? entityType = freezed,
    Object? type = freezed,
    Object? summary = freezed,
    Object? status = freezed,
    Object? tags = null,
    Object? timelineNotes = null,
    Object? openQuestions = null,
  }) {
    return _then(
      _$EntityImpl(
        entityId: null == entityId
            ? _value.entityId
            : entityId // ignore: cast_nullable_to_non_nullable
                  as String,
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        entityType: freezed == entityType
            ? _value.entityType
            : entityType // ignore: cast_nullable_to_non_nullable
                  as String?,
        type: freezed == type
            ? _value.type
            : type // ignore: cast_nullable_to_non_nullable
                  as String?,
        summary: freezed == summary
            ? _value.summary
            : summary // ignore: cast_nullable_to_non_nullable
                  as String?,
        status: freezed == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as String?,
        tags: null == tags
            ? _value._tags
            : tags // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        timelineNotes: null == timelineNotes
            ? _value._timelineNotes
            : timelineNotes // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        openQuestions: null == openQuestions
            ? _value._openQuestions
            : openQuestions // ignore: cast_nullable_to_non_nullable
                  as List<String>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityImpl implements _Entity {
  const _$EntityImpl({
    required this.entityId,
    required this.name,
    this.entityType,
    this.type,
    this.summary,
    this.status,
    final List<String> tags = const <String>[],
    final List<String> timelineNotes = const <String>[],
    final List<String> openQuestions = const <String>[],
  }) : _tags = tags,
       _timelineNotes = timelineNotes,
       _openQuestions = openQuestions;

  factory _$EntityImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityImplFromJson(json);

  @override
  final String entityId;
  @override
  final String name;

  /// `character`, `location`, `faction`, `object`, `event`, or `unknown`.
  /// Note the backend sometimes returns the type under `type`, sometimes
  /// under `entity_type`; we accept either by mapping in the API layer.
  @override
  final String? entityType;
  @override
  final String? type;
  @override
  final String? summary;
  @override
  final String? status;
  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

  final List<String> _timelineNotes;
  @override
  @JsonKey()
  List<String> get timelineNotes {
    if (_timelineNotes is EqualUnmodifiableListView) return _timelineNotes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_timelineNotes);
  }

  final List<String> _openQuestions;
  @override
  @JsonKey()
  List<String> get openQuestions {
    if (_openQuestions is EqualUnmodifiableListView) return _openQuestions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_openQuestions);
  }

  @override
  String toString() {
    return 'Entity(entityId: $entityId, name: $name, entityType: $entityType, type: $type, summary: $summary, status: $status, tags: $tags, timelineNotes: $timelineNotes, openQuestions: $openQuestions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityImpl &&
            (identical(other.entityId, entityId) ||
                other.entityId == entityId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.entityType, entityType) ||
                other.entityType == entityType) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.summary, summary) || other.summary == summary) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(other._tags, _tags) &&
            const DeepCollectionEquality().equals(
              other._timelineNotes,
              _timelineNotes,
            ) &&
            const DeepCollectionEquality().equals(
              other._openQuestions,
              _openQuestions,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    entityId,
    name,
    entityType,
    type,
    summary,
    status,
    const DeepCollectionEquality().hash(_tags),
    const DeepCollectionEquality().hash(_timelineNotes),
    const DeepCollectionEquality().hash(_openQuestions),
  );

  /// Create a copy of Entity
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityImplCopyWith<_$EntityImpl> get copyWith =>
      __$$EntityImplCopyWithImpl<_$EntityImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityImplToJson(this);
  }
}

abstract class _Entity implements Entity {
  const factory _Entity({
    required final String entityId,
    required final String name,
    final String? entityType,
    final String? type,
    final String? summary,
    final String? status,
    final List<String> tags,
    final List<String> timelineNotes,
    final List<String> openQuestions,
  }) = _$EntityImpl;

  factory _Entity.fromJson(Map<String, dynamic> json) = _$EntityImpl.fromJson;

  @override
  String get entityId;
  @override
  String get name;

  /// `character`, `location`, `faction`, `object`, `event`, or `unknown`.
  /// Note the backend sometimes returns the type under `type`, sometimes
  /// under `entity_type`; we accept either by mapping in the API layer.
  @override
  String? get entityType;
  @override
  String? get type;
  @override
  String? get summary;
  @override
  String? get status;
  @override
  List<String> get tags;
  @override
  List<String> get timelineNotes;
  @override
  List<String> get openQuestions;

  /// Create a copy of Entity
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityImplCopyWith<_$EntityImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

EntityDetailResponse _$EntityDetailResponseFromJson(Map<String, dynamic> json) {
  return _EntityDetailResponse.fromJson(json);
}

/// @nodoc
mixin _$EntityDetailResponse {
  Entity get entity => throw _privateConstructorUsedError;

  /// Serializes this EntityDetailResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityDetailResponseCopyWith<EntityDetailResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityDetailResponseCopyWith<$Res> {
  factory $EntityDetailResponseCopyWith(
    EntityDetailResponse value,
    $Res Function(EntityDetailResponse) then,
  ) = _$EntityDetailResponseCopyWithImpl<$Res, EntityDetailResponse>;
  @useResult
  $Res call({Entity entity});

  $EntityCopyWith<$Res> get entity;
}

/// @nodoc
class _$EntityDetailResponseCopyWithImpl<
  $Res,
  $Val extends EntityDetailResponse
>
    implements $EntityDetailResponseCopyWith<$Res> {
  _$EntityDetailResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? entity = null}) {
    return _then(
      _value.copyWith(
            entity: null == entity
                ? _value.entity
                : entity // ignore: cast_nullable_to_non_nullable
                      as Entity,
          )
          as $Val,
    );
  }

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $EntityCopyWith<$Res> get entity {
    return $EntityCopyWith<$Res>(_value.entity, (value) {
      return _then(_value.copyWith(entity: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$EntityDetailResponseImplCopyWith<$Res>
    implements $EntityDetailResponseCopyWith<$Res> {
  factory _$$EntityDetailResponseImplCopyWith(
    _$EntityDetailResponseImpl value,
    $Res Function(_$EntityDetailResponseImpl) then,
  ) = __$$EntityDetailResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({Entity entity});

  @override
  $EntityCopyWith<$Res> get entity;
}

/// @nodoc
class __$$EntityDetailResponseImplCopyWithImpl<$Res>
    extends _$EntityDetailResponseCopyWithImpl<$Res, _$EntityDetailResponseImpl>
    implements _$$EntityDetailResponseImplCopyWith<$Res> {
  __$$EntityDetailResponseImplCopyWithImpl(
    _$EntityDetailResponseImpl _value,
    $Res Function(_$EntityDetailResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? entity = null}) {
    return _then(
      _$EntityDetailResponseImpl(
        entity: null == entity
            ? _value.entity
            : entity // ignore: cast_nullable_to_non_nullable
                  as Entity,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityDetailResponseImpl implements _EntityDetailResponse {
  const _$EntityDetailResponseImpl({required this.entity});

  factory _$EntityDetailResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityDetailResponseImplFromJson(json);

  @override
  final Entity entity;

  @override
  String toString() {
    return 'EntityDetailResponse(entity: $entity)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityDetailResponseImpl &&
            (identical(other.entity, entity) || other.entity == entity));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, entity);

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityDetailResponseImplCopyWith<_$EntityDetailResponseImpl>
  get copyWith =>
      __$$EntityDetailResponseImplCopyWithImpl<_$EntityDetailResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityDetailResponseImplToJson(this);
  }
}

abstract class _EntityDetailResponse implements EntityDetailResponse {
  const factory _EntityDetailResponse({required final Entity entity}) =
      _$EntityDetailResponseImpl;

  factory _EntityDetailResponse.fromJson(Map<String, dynamic> json) =
      _$EntityDetailResponseImpl.fromJson;

  @override
  Entity get entity;

  /// Create a copy of EntityDetailResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityDetailResponseImplCopyWith<_$EntityDetailResponseImpl>
  get copyWith => throw _privateConstructorUsedError;
}

EntityStatsResponse _$EntityStatsResponseFromJson(Map<String, dynamic> json) {
  return _EntityStatsResponse.fromJson(json);
}

/// @nodoc
mixin _$EntityStatsResponse {
  Map<String, int> get stats => throw _privateConstructorUsedError;

  /// Serializes this EntityStatsResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EntityStatsResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityStatsResponseCopyWith<EntityStatsResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityStatsResponseCopyWith<$Res> {
  factory $EntityStatsResponseCopyWith(
    EntityStatsResponse value,
    $Res Function(EntityStatsResponse) then,
  ) = _$EntityStatsResponseCopyWithImpl<$Res, EntityStatsResponse>;
  @useResult
  $Res call({Map<String, int> stats});
}

/// @nodoc
class _$EntityStatsResponseCopyWithImpl<$Res, $Val extends EntityStatsResponse>
    implements $EntityStatsResponseCopyWith<$Res> {
  _$EntityStatsResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EntityStatsResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? stats = null}) {
    return _then(
      _value.copyWith(
            stats: null == stats
                ? _value.stats
                : stats // ignore: cast_nullable_to_non_nullable
                      as Map<String, int>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$EntityStatsResponseImplCopyWith<$Res>
    implements $EntityStatsResponseCopyWith<$Res> {
  factory _$$EntityStatsResponseImplCopyWith(
    _$EntityStatsResponseImpl value,
    $Res Function(_$EntityStatsResponseImpl) then,
  ) = __$$EntityStatsResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({Map<String, int> stats});
}

/// @nodoc
class __$$EntityStatsResponseImplCopyWithImpl<$Res>
    extends _$EntityStatsResponseCopyWithImpl<$Res, _$EntityStatsResponseImpl>
    implements _$$EntityStatsResponseImplCopyWith<$Res> {
  __$$EntityStatsResponseImplCopyWithImpl(
    _$EntityStatsResponseImpl _value,
    $Res Function(_$EntityStatsResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of EntityStatsResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? stats = null}) {
    return _then(
      _$EntityStatsResponseImpl(
        stats: null == stats
            ? _value._stats
            : stats // ignore: cast_nullable_to_non_nullable
                  as Map<String, int>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityStatsResponseImpl implements _EntityStatsResponse {
  const _$EntityStatsResponseImpl({
    final Map<String, int> stats = const <String, int>{},
  }) : _stats = stats;

  factory _$EntityStatsResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityStatsResponseImplFromJson(json);

  final Map<String, int> _stats;
  @override
  @JsonKey()
  Map<String, int> get stats {
    if (_stats is EqualUnmodifiableMapView) return _stats;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_stats);
  }

  @override
  String toString() {
    return 'EntityStatsResponse(stats: $stats)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityStatsResponseImpl &&
            const DeepCollectionEquality().equals(other._stats, _stats));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_stats));

  /// Create a copy of EntityStatsResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityStatsResponseImplCopyWith<_$EntityStatsResponseImpl> get copyWith =>
      __$$EntityStatsResponseImplCopyWithImpl<_$EntityStatsResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityStatsResponseImplToJson(this);
  }
}

abstract class _EntityStatsResponse implements EntityStatsResponse {
  const factory _EntityStatsResponse({final Map<String, int> stats}) =
      _$EntityStatsResponseImpl;

  factory _EntityStatsResponse.fromJson(Map<String, dynamic> json) =
      _$EntityStatsResponseImpl.fromJson;

  @override
  Map<String, int> get stats;

  /// Create a copy of EntityStatsResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityStatsResponseImplCopyWith<_$EntityStatsResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

EntityLinkRequest _$EntityLinkRequestFromJson(Map<String, dynamic> json) {
  return _EntityLinkRequest.fromJson(json);
}

/// @nodoc
mixin _$EntityLinkRequest {
  String get worldId => throw _privateConstructorUsedError;
  String get entityIdA => throw _privateConstructorUsedError;
  String get entityIdB => throw _privateConstructorUsedError;
  String get relation => throw _privateConstructorUsedError;

  /// Serializes this EntityLinkRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of EntityLinkRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EntityLinkRequestCopyWith<EntityLinkRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EntityLinkRequestCopyWith<$Res> {
  factory $EntityLinkRequestCopyWith(
    EntityLinkRequest value,
    $Res Function(EntityLinkRequest) then,
  ) = _$EntityLinkRequestCopyWithImpl<$Res, EntityLinkRequest>;
  @useResult
  $Res call({
    String worldId,
    String entityIdA,
    String entityIdB,
    String relation,
  });
}

/// @nodoc
class _$EntityLinkRequestCopyWithImpl<$Res, $Val extends EntityLinkRequest>
    implements $EntityLinkRequestCopyWith<$Res> {
  _$EntityLinkRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of EntityLinkRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? entityIdA = null,
    Object? entityIdB = null,
    Object? relation = null,
  }) {
    return _then(
      _value.copyWith(
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
            entityIdA: null == entityIdA
                ? _value.entityIdA
                : entityIdA // ignore: cast_nullable_to_non_nullable
                      as String,
            entityIdB: null == entityIdB
                ? _value.entityIdB
                : entityIdB // ignore: cast_nullable_to_non_nullable
                      as String,
            relation: null == relation
                ? _value.relation
                : relation // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$EntityLinkRequestImplCopyWith<$Res>
    implements $EntityLinkRequestCopyWith<$Res> {
  factory _$$EntityLinkRequestImplCopyWith(
    _$EntityLinkRequestImpl value,
    $Res Function(_$EntityLinkRequestImpl) then,
  ) = __$$EntityLinkRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String worldId,
    String entityIdA,
    String entityIdB,
    String relation,
  });
}

/// @nodoc
class __$$EntityLinkRequestImplCopyWithImpl<$Res>
    extends _$EntityLinkRequestCopyWithImpl<$Res, _$EntityLinkRequestImpl>
    implements _$$EntityLinkRequestImplCopyWith<$Res> {
  __$$EntityLinkRequestImplCopyWithImpl(
    _$EntityLinkRequestImpl _value,
    $Res Function(_$EntityLinkRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of EntityLinkRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? entityIdA = null,
    Object? entityIdB = null,
    Object? relation = null,
  }) {
    return _then(
      _$EntityLinkRequestImpl(
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
        entityIdA: null == entityIdA
            ? _value.entityIdA
            : entityIdA // ignore: cast_nullable_to_non_nullable
                  as String,
        entityIdB: null == entityIdB
            ? _value.entityIdB
            : entityIdB // ignore: cast_nullable_to_non_nullable
                  as String,
        relation: null == relation
            ? _value.relation
            : relation // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$EntityLinkRequestImpl implements _EntityLinkRequest {
  const _$EntityLinkRequestImpl({
    required this.worldId,
    required this.entityIdA,
    required this.entityIdB,
    this.relation = 'references',
  });

  factory _$EntityLinkRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$EntityLinkRequestImplFromJson(json);

  @override
  final String worldId;
  @override
  final String entityIdA;
  @override
  final String entityIdB;
  @override
  @JsonKey()
  final String relation;

  @override
  String toString() {
    return 'EntityLinkRequest(worldId: $worldId, entityIdA: $entityIdA, entityIdB: $entityIdB, relation: $relation)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EntityLinkRequestImpl &&
            (identical(other.worldId, worldId) || other.worldId == worldId) &&
            (identical(other.entityIdA, entityIdA) ||
                other.entityIdA == entityIdA) &&
            (identical(other.entityIdB, entityIdB) ||
                other.entityIdB == entityIdB) &&
            (identical(other.relation, relation) ||
                other.relation == relation));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, worldId, entityIdA, entityIdB, relation);

  /// Create a copy of EntityLinkRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EntityLinkRequestImplCopyWith<_$EntityLinkRequestImpl> get copyWith =>
      __$$EntityLinkRequestImplCopyWithImpl<_$EntityLinkRequestImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$EntityLinkRequestImplToJson(this);
  }
}

abstract class _EntityLinkRequest implements EntityLinkRequest {
  const factory _EntityLinkRequest({
    required final String worldId,
    required final String entityIdA,
    required final String entityIdB,
    final String relation,
  }) = _$EntityLinkRequestImpl;

  factory _EntityLinkRequest.fromJson(Map<String, dynamic> json) =
      _$EntityLinkRequestImpl.fromJson;

  @override
  String get worldId;
  @override
  String get entityIdA;
  @override
  String get entityIdB;
  @override
  String get relation;

  /// Create a copy of EntityLinkRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EntityLinkRequestImplCopyWith<_$EntityLinkRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
