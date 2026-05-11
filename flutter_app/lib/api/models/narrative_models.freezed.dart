// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'narrative_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

ConversationMessage _$ConversationMessageFromJson(Map<String, dynamic> json) {
  return _ConversationMessage.fromJson(json);
}

/// @nodoc
mixin _$ConversationMessage {
  /// `user` or `assistant`.
  String get role => throw _privateConstructorUsedError;
  String get content => throw _privateConstructorUsedError;

  /// Serializes this ConversationMessage to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConversationMessage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConversationMessageCopyWith<ConversationMessage> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConversationMessageCopyWith<$Res> {
  factory $ConversationMessageCopyWith(
    ConversationMessage value,
    $Res Function(ConversationMessage) then,
  ) = _$ConversationMessageCopyWithImpl<$Res, ConversationMessage>;
  @useResult
  $Res call({String role, String content});
}

/// @nodoc
class _$ConversationMessageCopyWithImpl<$Res, $Val extends ConversationMessage>
    implements $ConversationMessageCopyWith<$Res> {
  _$ConversationMessageCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConversationMessage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? role = null, Object? content = null}) {
    return _then(
      _value.copyWith(
            role: null == role
                ? _value.role
                : role // ignore: cast_nullable_to_non_nullable
                      as String,
            content: null == content
                ? _value.content
                : content // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ConversationMessageImplCopyWith<$Res>
    implements $ConversationMessageCopyWith<$Res> {
  factory _$$ConversationMessageImplCopyWith(
    _$ConversationMessageImpl value,
    $Res Function(_$ConversationMessageImpl) then,
  ) = __$$ConversationMessageImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String role, String content});
}

/// @nodoc
class __$$ConversationMessageImplCopyWithImpl<$Res>
    extends _$ConversationMessageCopyWithImpl<$Res, _$ConversationMessageImpl>
    implements _$$ConversationMessageImplCopyWith<$Res> {
  __$$ConversationMessageImplCopyWithImpl(
    _$ConversationMessageImpl _value,
    $Res Function(_$ConversationMessageImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of ConversationMessage
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? role = null, Object? content = null}) {
    return _then(
      _$ConversationMessageImpl(
        role: null == role
            ? _value.role
            : role // ignore: cast_nullable_to_non_nullable
                  as String,
        content: null == content
            ? _value.content
            : content // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ConversationMessageImpl implements _ConversationMessage {
  const _$ConversationMessageImpl({required this.role, required this.content});

  factory _$ConversationMessageImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConversationMessageImplFromJson(json);

  /// `user` or `assistant`.
  @override
  final String role;
  @override
  final String content;

  @override
  String toString() {
    return 'ConversationMessage(role: $role, content: $content)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConversationMessageImpl &&
            (identical(other.role, role) || other.role == role) &&
            (identical(other.content, content) || other.content == content));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, role, content);

  /// Create a copy of ConversationMessage
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConversationMessageImplCopyWith<_$ConversationMessageImpl> get copyWith =>
      __$$ConversationMessageImplCopyWithImpl<_$ConversationMessageImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$ConversationMessageImplToJson(this);
  }
}

abstract class _ConversationMessage implements ConversationMessage {
  const factory _ConversationMessage({
    required final String role,
    required final String content,
  }) = _$ConversationMessageImpl;

  factory _ConversationMessage.fromJson(Map<String, dynamic> json) =
      _$ConversationMessageImpl.fromJson;

  /// `user` or `assistant`.
  @override
  String get role;
  @override
  String get content;

  /// Create a copy of ConversationMessage
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConversationMessageImplCopyWith<_$ConversationMessageImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

NarrativeRequest _$NarrativeRequestFromJson(Map<String, dynamic> json) {
  return _NarrativeRequest.fromJson(json);
}

/// @nodoc
mixin _$NarrativeRequest {
  String get worldId => throw _privateConstructorUsedError;
  String get action => throw _privateConstructorUsedError;
  List<ConversationMessage> get history => throw _privateConstructorUsedError;

  /// Serializes this NarrativeRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of NarrativeRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $NarrativeRequestCopyWith<NarrativeRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NarrativeRequestCopyWith<$Res> {
  factory $NarrativeRequestCopyWith(
    NarrativeRequest value,
    $Res Function(NarrativeRequest) then,
  ) = _$NarrativeRequestCopyWithImpl<$Res, NarrativeRequest>;
  @useResult
  $Res call({String worldId, String action, List<ConversationMessage> history});
}

/// @nodoc
class _$NarrativeRequestCopyWithImpl<$Res, $Val extends NarrativeRequest>
    implements $NarrativeRequestCopyWith<$Res> {
  _$NarrativeRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of NarrativeRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? action = null,
    Object? history = null,
  }) {
    return _then(
      _value.copyWith(
            worldId: null == worldId
                ? _value.worldId
                : worldId // ignore: cast_nullable_to_non_nullable
                      as String,
            action: null == action
                ? _value.action
                : action // ignore: cast_nullable_to_non_nullable
                      as String,
            history: null == history
                ? _value.history
                : history // ignore: cast_nullable_to_non_nullable
                      as List<ConversationMessage>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$NarrativeRequestImplCopyWith<$Res>
    implements $NarrativeRequestCopyWith<$Res> {
  factory _$$NarrativeRequestImplCopyWith(
    _$NarrativeRequestImpl value,
    $Res Function(_$NarrativeRequestImpl) then,
  ) = __$$NarrativeRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String worldId, String action, List<ConversationMessage> history});
}

/// @nodoc
class __$$NarrativeRequestImplCopyWithImpl<$Res>
    extends _$NarrativeRequestCopyWithImpl<$Res, _$NarrativeRequestImpl>
    implements _$$NarrativeRequestImplCopyWith<$Res> {
  __$$NarrativeRequestImplCopyWithImpl(
    _$NarrativeRequestImpl _value,
    $Res Function(_$NarrativeRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of NarrativeRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? worldId = null,
    Object? action = null,
    Object? history = null,
  }) {
    return _then(
      _$NarrativeRequestImpl(
        worldId: null == worldId
            ? _value.worldId
            : worldId // ignore: cast_nullable_to_non_nullable
                  as String,
        action: null == action
            ? _value.action
            : action // ignore: cast_nullable_to_non_nullable
                  as String,
        history: null == history
            ? _value._history
            : history // ignore: cast_nullable_to_non_nullable
                  as List<ConversationMessage>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$NarrativeRequestImpl implements _NarrativeRequest {
  const _$NarrativeRequestImpl({
    required this.worldId,
    required this.action,
    final List<ConversationMessage> history = const <ConversationMessage>[],
  }) : _history = history;

  factory _$NarrativeRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$NarrativeRequestImplFromJson(json);

  @override
  final String worldId;
  @override
  final String action;
  final List<ConversationMessage> _history;
  @override
  @JsonKey()
  List<ConversationMessage> get history {
    if (_history is EqualUnmodifiableListView) return _history;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_history);
  }

  @override
  String toString() {
    return 'NarrativeRequest(worldId: $worldId, action: $action, history: $history)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NarrativeRequestImpl &&
            (identical(other.worldId, worldId) || other.worldId == worldId) &&
            (identical(other.action, action) || other.action == action) &&
            const DeepCollectionEquality().equals(other._history, _history));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    worldId,
    action,
    const DeepCollectionEquality().hash(_history),
  );

  /// Create a copy of NarrativeRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$NarrativeRequestImplCopyWith<_$NarrativeRequestImpl> get copyWith =>
      __$$NarrativeRequestImplCopyWithImpl<_$NarrativeRequestImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$NarrativeRequestImplToJson(this);
  }
}

abstract class _NarrativeRequest implements NarrativeRequest {
  const factory _NarrativeRequest({
    required final String worldId,
    required final String action,
    final List<ConversationMessage> history,
  }) = _$NarrativeRequestImpl;

  factory _NarrativeRequest.fromJson(Map<String, dynamic> json) =
      _$NarrativeRequestImpl.fromJson;

  @override
  String get worldId;
  @override
  String get action;
  @override
  List<ConversationMessage> get history;

  /// Create a copy of NarrativeRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$NarrativeRequestImplCopyWith<_$NarrativeRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

NarrativeResponse _$NarrativeResponseFromJson(Map<String, dynamic> json) {
  return _NarrativeResponse.fromJson(json);
}

/// @nodoc
mixin _$NarrativeResponse {
  String get narrative => throw _privateConstructorUsedError;
  List<ConversationMessage> get history => throw _privateConstructorUsedError;
  int? get investigationPoints => throw _privateConstructorUsedError;
  int? get maxInvestigationPoints => throw _privateConstructorUsedError;
  GameTime? get gameTime => throw _privateConstructorUsedError;

  /// Serializes this NarrativeResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of NarrativeResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $NarrativeResponseCopyWith<NarrativeResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NarrativeResponseCopyWith<$Res> {
  factory $NarrativeResponseCopyWith(
    NarrativeResponse value,
    $Res Function(NarrativeResponse) then,
  ) = _$NarrativeResponseCopyWithImpl<$Res, NarrativeResponse>;
  @useResult
  $Res call({
    String narrative,
    List<ConversationMessage> history,
    int? investigationPoints,
    int? maxInvestigationPoints,
    GameTime? gameTime,
  });

  $GameTimeCopyWith<$Res>? get gameTime;
}

/// @nodoc
class _$NarrativeResponseCopyWithImpl<$Res, $Val extends NarrativeResponse>
    implements $NarrativeResponseCopyWith<$Res> {
  _$NarrativeResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of NarrativeResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? narrative = null,
    Object? history = null,
    Object? investigationPoints = freezed,
    Object? maxInvestigationPoints = freezed,
    Object? gameTime = freezed,
  }) {
    return _then(
      _value.copyWith(
            narrative: null == narrative
                ? _value.narrative
                : narrative // ignore: cast_nullable_to_non_nullable
                      as String,
            history: null == history
                ? _value.history
                : history // ignore: cast_nullable_to_non_nullable
                      as List<ConversationMessage>,
            investigationPoints: freezed == investigationPoints
                ? _value.investigationPoints
                : investigationPoints // ignore: cast_nullable_to_non_nullable
                      as int?,
            maxInvestigationPoints: freezed == maxInvestigationPoints
                ? _value.maxInvestigationPoints
                : maxInvestigationPoints // ignore: cast_nullable_to_non_nullable
                      as int?,
            gameTime: freezed == gameTime
                ? _value.gameTime
                : gameTime // ignore: cast_nullable_to_non_nullable
                      as GameTime?,
          )
          as $Val,
    );
  }

  /// Create a copy of NarrativeResponse
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
abstract class _$$NarrativeResponseImplCopyWith<$Res>
    implements $NarrativeResponseCopyWith<$Res> {
  factory _$$NarrativeResponseImplCopyWith(
    _$NarrativeResponseImpl value,
    $Res Function(_$NarrativeResponseImpl) then,
  ) = __$$NarrativeResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String narrative,
    List<ConversationMessage> history,
    int? investigationPoints,
    int? maxInvestigationPoints,
    GameTime? gameTime,
  });

  @override
  $GameTimeCopyWith<$Res>? get gameTime;
}

/// @nodoc
class __$$NarrativeResponseImplCopyWithImpl<$Res>
    extends _$NarrativeResponseCopyWithImpl<$Res, _$NarrativeResponseImpl>
    implements _$$NarrativeResponseImplCopyWith<$Res> {
  __$$NarrativeResponseImplCopyWithImpl(
    _$NarrativeResponseImpl _value,
    $Res Function(_$NarrativeResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of NarrativeResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? narrative = null,
    Object? history = null,
    Object? investigationPoints = freezed,
    Object? maxInvestigationPoints = freezed,
    Object? gameTime = freezed,
  }) {
    return _then(
      _$NarrativeResponseImpl(
        narrative: null == narrative
            ? _value.narrative
            : narrative // ignore: cast_nullable_to_non_nullable
                  as String,
        history: null == history
            ? _value._history
            : history // ignore: cast_nullable_to_non_nullable
                  as List<ConversationMessage>,
        investigationPoints: freezed == investigationPoints
            ? _value.investigationPoints
            : investigationPoints // ignore: cast_nullable_to_non_nullable
                  as int?,
        maxInvestigationPoints: freezed == maxInvestigationPoints
            ? _value.maxInvestigationPoints
            : maxInvestigationPoints // ignore: cast_nullable_to_non_nullable
                  as int?,
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
class _$NarrativeResponseImpl implements _NarrativeResponse {
  const _$NarrativeResponseImpl({
    required this.narrative,
    final List<ConversationMessage> history = const <ConversationMessage>[],
    this.investigationPoints,
    this.maxInvestigationPoints,
    this.gameTime,
  }) : _history = history;

  factory _$NarrativeResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$NarrativeResponseImplFromJson(json);

  @override
  final String narrative;
  final List<ConversationMessage> _history;
  @override
  @JsonKey()
  List<ConversationMessage> get history {
    if (_history is EqualUnmodifiableListView) return _history;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_history);
  }

  @override
  final int? investigationPoints;
  @override
  final int? maxInvestigationPoints;
  @override
  final GameTime? gameTime;

  @override
  String toString() {
    return 'NarrativeResponse(narrative: $narrative, history: $history, investigationPoints: $investigationPoints, maxInvestigationPoints: $maxInvestigationPoints, gameTime: $gameTime)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NarrativeResponseImpl &&
            (identical(other.narrative, narrative) ||
                other.narrative == narrative) &&
            const DeepCollectionEquality().equals(other._history, _history) &&
            (identical(other.investigationPoints, investigationPoints) ||
                other.investigationPoints == investigationPoints) &&
            (identical(other.maxInvestigationPoints, maxInvestigationPoints) ||
                other.maxInvestigationPoints == maxInvestigationPoints) &&
            (identical(other.gameTime, gameTime) ||
                other.gameTime == gameTime));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    narrative,
    const DeepCollectionEquality().hash(_history),
    investigationPoints,
    maxInvestigationPoints,
    gameTime,
  );

  /// Create a copy of NarrativeResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$NarrativeResponseImplCopyWith<_$NarrativeResponseImpl> get copyWith =>
      __$$NarrativeResponseImplCopyWithImpl<_$NarrativeResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$NarrativeResponseImplToJson(this);
  }
}

abstract class _NarrativeResponse implements NarrativeResponse {
  const factory _NarrativeResponse({
    required final String narrative,
    final List<ConversationMessage> history,
    final int? investigationPoints,
    final int? maxInvestigationPoints,
    final GameTime? gameTime,
  }) = _$NarrativeResponseImpl;

  factory _NarrativeResponse.fromJson(Map<String, dynamic> json) =
      _$NarrativeResponseImpl.fromJson;

  @override
  String get narrative;
  @override
  List<ConversationMessage> get history;
  @override
  int? get investigationPoints;
  @override
  int? get maxInvestigationPoints;
  @override
  GameTime? get gameTime;

  /// Create a copy of NarrativeResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$NarrativeResponseImplCopyWith<_$NarrativeResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
