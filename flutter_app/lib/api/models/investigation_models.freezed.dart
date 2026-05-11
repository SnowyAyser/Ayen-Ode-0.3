// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'investigation_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

InvestigateRequest _$InvestigateRequestFromJson(Map<String, dynamic> json) {
  return _InvestigateRequest.fromJson(json);
}

/// @nodoc
mixin _$InvestigateRequest {
  String get worldId => throw _privateConstructorUsedError;
  String get itemName => throw _privateConstructorUsedError;
  String get entityType => throw _privateConstructorUsedError;
  int get cost => throw _privateConstructorUsedError;

  /// Serializes this InvestigateRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InvestigateRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InvestigateRequestCopyWith<InvestigateRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InvestigateRequestCopyWith<$Res> {
  factory $InvestigateRequestCopyWith(
    InvestigateRequest value,
    $Res Function(InvestigateRequest) then,
  ) = _$InvestigateRequestCopyWithImpl<$Res, InvestigateRequest>;
  @useResult
  $Res call({String worldId, String itemName, String entityType, int cost});
}

/// @nodoc
class _$InvestigateRequestCopyWithImpl<$Res, $Val extends InvestigateRequest>
    implements $InvestigateRequestCopyWith<$Res> {
  _$InvestigateRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InvestigateRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? itemName = null,
    Object? entityType = null,
    Object? cost = null,
  }) {
    return _then(
      _value.copyWith(
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
            itemName: null == itemName
                ? _value.itemName
                : itemName // ignore: cast_nullable_to_non_nullable
                      as String,
            entityType: null == entityType
                ? _value.entityType
                : entityType // ignore: cast_nullable_to_non_nullable
                      as String,
            cost: null == cost
                ? _value.cost
                : cost // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$InvestigateRequestImplCopyWith<$Res>
    implements $InvestigateRequestCopyWith<$Res> {
  factory _$$InvestigateRequestImplCopyWith(
    _$InvestigateRequestImpl value,
    $Res Function(_$InvestigateRequestImpl) then,
  ) = __$$InvestigateRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String worldId, String itemName, String entityType, int cost});
}

/// @nodoc
class __$$InvestigateRequestImplCopyWithImpl<$Res>
    extends _$InvestigateRequestCopyWithImpl<$Res, _$InvestigateRequestImpl>
    implements _$$InvestigateRequestImplCopyWith<$Res> {
  __$$InvestigateRequestImplCopyWithImpl(
    _$InvestigateRequestImpl _value,
    $Res Function(_$InvestigateRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of InvestigateRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? itemName = null,
    Object? entityType = null,
    Object? cost = null,
  }) {
    return _then(
      _$InvestigateRequestImpl(
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
        itemName: null == itemName
            ? _value.itemName
            : itemName // ignore: cast_nullable_to_non_nullable
                  as String,
        entityType: null == entityType
            ? _value.entityType
            : entityType // ignore: cast_nullable_to_non_nullable
                  as String,
        cost: null == cost
            ? _value.cost
            : cost // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$InvestigateRequestImpl implements _InvestigateRequest {
  const _$InvestigateRequestImpl({
    required this.worldId,
    required this.itemName,
    this.entityType = 'object',
    this.cost = 1,
  });

  factory _$InvestigateRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$InvestigateRequestImplFromJson(json);

  @override
  final String worldId;
  @override
  final String itemName;
  @override
  @JsonKey()
  final String entityType;
  @override
  @JsonKey()
  final int cost;

  @override
  String toString() {
    return 'InvestigateRequest(worldId: $worldId, itemName: $itemName, entityType: $entityType, cost: $cost)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InvestigateRequestImpl &&
            (identical(other.worldId, worldId) || other.worldId == worldId) &&
            (identical(other.itemName, itemName) ||
                other.itemName == itemName) &&
            (identical(other.entityType, entityType) ||
                other.entityType == entityType) &&
            (identical(other.cost, cost) || other.cost == cost));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, worldId, itemName, entityType, cost);

  /// Create a copy of InvestigateRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InvestigateRequestImplCopyWith<_$InvestigateRequestImpl> get copyWith =>
      __$$InvestigateRequestImplCopyWithImpl<_$InvestigateRequestImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$InvestigateRequestImplToJson(this);
  }
}

abstract class _InvestigateRequest implements InvestigateRequest {
  const factory _InvestigateRequest({
    required final String worldId,
    required final String itemName,
    final String entityType,
    final int cost,
  }) = _$InvestigateRequestImpl;

  factory _InvestigateRequest.fromJson(Map<String, dynamic> json) =
      _$InvestigateRequestImpl.fromJson;

  @override
  String get worldId;
  @override
  String get itemName;
  @override
  String get entityType;
  @override
  int get cost;

  /// Create a copy of InvestigateRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InvestigateRequestImplCopyWith<_$InvestigateRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InvestigateResponse _$InvestigateResponseFromJson(Map<String, dynamic> json) {
  return _InvestigateResponse.fromJson(json);
}

/// @nodoc
mixin _$InvestigateResponse {
  String get investigationId => throw _privateConstructorUsedError;
  int get remainingPoints => throw _privateConstructorUsedError;

  /// Serializes this InvestigateResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InvestigateResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InvestigateResponseCopyWith<InvestigateResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InvestigateResponseCopyWith<$Res> {
  factory $InvestigateResponseCopyWith(
    InvestigateResponse value,
    $Res Function(InvestigateResponse) then,
  ) = _$InvestigateResponseCopyWithImpl<$Res, InvestigateResponse>;
  @useResult
  $Res call({String investigationId, int remainingPoints});
}

/// @nodoc
class _$InvestigateResponseCopyWithImpl<$Res, $Val extends InvestigateResponse>
    implements $InvestigateResponseCopyWith<$Res> {
  _$InvestigateResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InvestigateResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? investigationId = null, Object? remainingPoints = null}) {
    return _then(
      _value.copyWith(
            investigationId: null == investigationId
                ? _value.investigationId
                : investigationId // ignore: cast_nullable_to_non_nullable
                      as String,
            remainingPoints: null == remainingPoints
                ? _value.remainingPoints
                : remainingPoints // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$InvestigateResponseImplCopyWith<$Res>
    implements $InvestigateResponseCopyWith<$Res> {
  factory _$$InvestigateResponseImplCopyWith(
    _$InvestigateResponseImpl value,
    $Res Function(_$InvestigateResponseImpl) then,
  ) = __$$InvestigateResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String investigationId, int remainingPoints});
}

/// @nodoc
class __$$InvestigateResponseImplCopyWithImpl<$Res>
    extends _$InvestigateResponseCopyWithImpl<$Res, _$InvestigateResponseImpl>
    implements _$$InvestigateResponseImplCopyWith<$Res> {
  __$$InvestigateResponseImplCopyWithImpl(
    _$InvestigateResponseImpl _value,
    $Res Function(_$InvestigateResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of InvestigateResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? investigationId = null, Object? remainingPoints = null}) {
    return _then(
      _$InvestigateResponseImpl(
        investigationId: null == investigationId
            ? _value.investigationId
            : investigationId // ignore: cast_nullable_to_non_nullable
                  as String,
        remainingPoints: null == remainingPoints
            ? _value.remainingPoints
            : remainingPoints // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$InvestigateResponseImpl implements _InvestigateResponse {
  const _$InvestigateResponseImpl({
    required this.investigationId,
    this.remainingPoints = 0,
  });

  factory _$InvestigateResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$InvestigateResponseImplFromJson(json);

  @override
  final String investigationId;
  @override
  @JsonKey()
  final int remainingPoints;

  @override
  String toString() {
    return 'InvestigateResponse(investigationId: $investigationId, remainingPoints: $remainingPoints)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InvestigateResponseImpl &&
            (identical(other.investigationId, investigationId) ||
                other.investigationId == investigationId) &&
            (identical(other.remainingPoints, remainingPoints) ||
                other.remainingPoints == remainingPoints));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, investigationId, remainingPoints);

  /// Create a copy of InvestigateResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InvestigateResponseImplCopyWith<_$InvestigateResponseImpl> get copyWith =>
      __$$InvestigateResponseImplCopyWithImpl<_$InvestigateResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$InvestigateResponseImplToJson(this);
  }
}

abstract class _InvestigateResponse implements InvestigateResponse {
  const factory _InvestigateResponse({
    required final String investigationId,
    final int remainingPoints,
  }) = _$InvestigateResponseImpl;

  factory _InvestigateResponse.fromJson(Map<String, dynamic> json) =
      _$InvestigateResponseImpl.fromJson;

  @override
  String get investigationId;
  @override
  int get remainingPoints;

  /// Create a copy of InvestigateResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InvestigateResponseImplCopyWith<_$InvestigateResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InvestigationResult _$InvestigationResultFromJson(Map<String, dynamic> json) {
  return _InvestigationResult.fromJson(json);
}

/// @nodoc
mixin _$InvestigationResult {
  Entity? get entity => throw _privateConstructorUsedError;

  /// Serializes this InvestigationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InvestigationResultCopyWith<InvestigationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InvestigationResultCopyWith<$Res> {
  factory $InvestigationResultCopyWith(
    InvestigationResult value,
    $Res Function(InvestigationResult) then,
  ) = _$InvestigationResultCopyWithImpl<$Res, InvestigationResult>;
  @useResult
  $Res call({Entity? entity});

  $EntityCopyWith<$Res>? get entity;
}

/// @nodoc
class _$InvestigationResultCopyWithImpl<$Res, $Val extends InvestigationResult>
    implements $InvestigationResultCopyWith<$Res> {
  _$InvestigationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? entity = freezed}) {
    return _then(
      _value.copyWith(
            entity: freezed == entity
                ? _value.entity
                : entity // ignore: cast_nullable_to_non_nullable
                      as Entity?,
          )
          as $Val,
    );
  }

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $EntityCopyWith<$Res>? get entity {
    if (_value.entity == null) {
      return null;
    }

    return $EntityCopyWith<$Res>(_value.entity!, (value) {
      return _then(_value.copyWith(entity: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$InvestigationResultImplCopyWith<$Res>
    implements $InvestigationResultCopyWith<$Res> {
  factory _$$InvestigationResultImplCopyWith(
    _$InvestigationResultImpl value,
    $Res Function(_$InvestigationResultImpl) then,
  ) = __$$InvestigationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({Entity? entity});

  @override
  $EntityCopyWith<$Res>? get entity;
}

/// @nodoc
class __$$InvestigationResultImplCopyWithImpl<$Res>
    extends _$InvestigationResultCopyWithImpl<$Res, _$InvestigationResultImpl>
    implements _$$InvestigationResultImplCopyWith<$Res> {
  __$$InvestigationResultImplCopyWithImpl(
    _$InvestigationResultImpl _value,
    $Res Function(_$InvestigationResultImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? entity = freezed}) {
    return _then(
      _$InvestigationResultImpl(
        entity: freezed == entity
            ? _value.entity
            : entity // ignore: cast_nullable_to_non_nullable
                  as Entity?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$InvestigationResultImpl implements _InvestigationResult {
  const _$InvestigationResultImpl({this.entity});

  factory _$InvestigationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$InvestigationResultImplFromJson(json);

  @override
  final Entity? entity;

  @override
  String toString() {
    return 'InvestigationResult(entity: $entity)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InvestigationResultImpl &&
            (identical(other.entity, entity) || other.entity == entity));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, entity);

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InvestigationResultImplCopyWith<_$InvestigationResultImpl> get copyWith =>
      __$$InvestigationResultImplCopyWithImpl<_$InvestigationResultImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$InvestigationResultImplToJson(this);
  }
}

abstract class _InvestigationResult implements InvestigationResult {
  const factory _InvestigationResult({final Entity? entity}) =
      _$InvestigationResultImpl;

  factory _InvestigationResult.fromJson(Map<String, dynamic> json) =
      _$InvestigationResultImpl.fromJson;

  @override
  Entity? get entity;

  /// Create a copy of InvestigationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InvestigationResultImplCopyWith<_$InvestigationResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

InvestigationStatusResponse _$InvestigationStatusResponseFromJson(
  Map<String, dynamic> json,
) {
  return _InvestigationStatusResponse.fromJson(json);
}

/// @nodoc
mixin _$InvestigationStatusResponse {
  /// `queued` / `processing` / `complete` / `failed`.
  String get status => throw _privateConstructorUsedError;
  InvestigationResult? get result => throw _privateConstructorUsedError;

  /// Serializes this InvestigationStatusResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $InvestigationStatusResponseCopyWith<InvestigationStatusResponse>
  get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $InvestigationStatusResponseCopyWith<$Res> {
  factory $InvestigationStatusResponseCopyWith(
    InvestigationStatusResponse value,
    $Res Function(InvestigationStatusResponse) then,
  ) =
      _$InvestigationStatusResponseCopyWithImpl<
        $Res,
        InvestigationStatusResponse
      >;
  @useResult
  $Res call({String status, InvestigationResult? result});

  $InvestigationResultCopyWith<$Res>? get result;
}

/// @nodoc
class _$InvestigationStatusResponseCopyWithImpl<
  $Res,
  $Val extends InvestigationStatusResponse
>
    implements $InvestigationStatusResponseCopyWith<$Res> {
  _$InvestigationStatusResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? status = null, Object? result = freezed}) {
    return _then(
      _value.copyWith(
            status: null == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as String,
            result: freezed == result
                ? _value.result
                : result // ignore: cast_nullable_to_non_nullable
                      as InvestigationResult?,
          )
          as $Val,
    );
  }

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $InvestigationResultCopyWith<$Res>? get result {
    if (_value.result == null) {
      return null;
    }

    return $InvestigationResultCopyWith<$Res>(_value.result!, (value) {
      return _then(_value.copyWith(result: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$InvestigationStatusResponseImplCopyWith<$Res>
    implements $InvestigationStatusResponseCopyWith<$Res> {
  factory _$$InvestigationStatusResponseImplCopyWith(
    _$InvestigationStatusResponseImpl value,
    $Res Function(_$InvestigationStatusResponseImpl) then,
  ) = __$$InvestigationStatusResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String status, InvestigationResult? result});

  @override
  $InvestigationResultCopyWith<$Res>? get result;
}

/// @nodoc
class __$$InvestigationStatusResponseImplCopyWithImpl<$Res>
    extends
        _$InvestigationStatusResponseCopyWithImpl<
          $Res,
          _$InvestigationStatusResponseImpl
        >
    implements _$$InvestigationStatusResponseImplCopyWith<$Res> {
  __$$InvestigationStatusResponseImplCopyWithImpl(
    _$InvestigationStatusResponseImpl _value,
    $Res Function(_$InvestigationStatusResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? status = null, Object? result = freezed}) {
    return _then(
      _$InvestigationStatusResponseImpl(
        status: null == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as String,
        result: freezed == result
            ? _value.result
            : result // ignore: cast_nullable_to_non_nullable
                  as InvestigationResult?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$InvestigationStatusResponseImpl
    implements _InvestigationStatusResponse {
  const _$InvestigationStatusResponseImpl({required this.status, this.result});

  factory _$InvestigationStatusResponseImpl.fromJson(
    Map<String, dynamic> json,
  ) => _$$InvestigationStatusResponseImplFromJson(json);

  /// `queued` / `processing` / `complete` / `failed`.
  @override
  final String status;
  @override
  final InvestigationResult? result;

  @override
  String toString() {
    return 'InvestigationStatusResponse(status: $status, result: $result)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$InvestigationStatusResponseImpl &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.result, result) || other.result == result));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, status, result);

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$InvestigationStatusResponseImplCopyWith<_$InvestigationStatusResponseImpl>
  get copyWith =>
      __$$InvestigationStatusResponseImplCopyWithImpl<
        _$InvestigationStatusResponseImpl
      >(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$InvestigationStatusResponseImplToJson(this);
  }
}

abstract class _InvestigationStatusResponse
    implements InvestigationStatusResponse {
  const factory _InvestigationStatusResponse({
    required final String status,
    final InvestigationResult? result,
  }) = _$InvestigationStatusResponseImpl;

  factory _InvestigationStatusResponse.fromJson(Map<String, dynamic> json) =
      _$InvestigationStatusResponseImpl.fromJson;

  /// `queued` / `processing` / `complete` / `failed`.
  @override
  String get status;
  @override
  InvestigationResult? get result;

  /// Create a copy of InvestigationStatusResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$InvestigationStatusResponseImplCopyWith<_$InvestigationStatusResponseImpl>
  get copyWith => throw _privateConstructorUsedError;
}
