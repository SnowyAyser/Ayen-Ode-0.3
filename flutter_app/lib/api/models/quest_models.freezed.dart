// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'quest_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Quest _$QuestFromJson(Map<String, dynamic> json) {
  return _Quest.fromJson(json);
}

/// @nodoc
mixin _$Quest {
  String get questId => throw _privateConstructorUsedError;
  int get tier => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// `active`, `pending_player`, `completed`, `dismissed`, …
  String get status => throw _privateConstructorUsedError;
  List<String> get completionTags => throw _privateConstructorUsedError;
  List<String> get progressTags => throw _privateConstructorUsedError;

  /// Serializes this Quest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Quest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $QuestCopyWith<Quest> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QuestCopyWith<$Res> {
  factory $QuestCopyWith(Quest value, $Res Function(Quest) then) =
      _$QuestCopyWithImpl<$Res, Quest>;
  @useResult
  $Res call({
    String questId,
    int tier,
    String title,
    String? description,
    String status,
    List<String> completionTags,
    List<String> progressTags,
  });
}

/// @nodoc
class _$QuestCopyWithImpl<$Res, $Val extends Quest>
    implements $QuestCopyWith<$Res> {
  _$QuestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Quest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? questId = null,
    Object? tier = null,
    Object? title = null,
    Object? description = freezed,
    Object? status = null,
    Object? completionTags = null,
    Object? progressTags = null,
  }) {
    return _then(
      _value.copyWith(
            questId: null == questId
                ? _value.questId
                : questId // ignore: cast_nullable_to_non_nullable
                      as String,
            tier: null == tier
                ? _value.tier
                : tier // ignore: cast_nullable_to_non_nullable
                      as int,
            title: null == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                      as String,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
            status: null == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as String,
            completionTags: null == completionTags
                ? _value.completionTags
                : completionTags // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            progressTags: null == progressTags
                ? _value.progressTags
                : progressTags // ignore: cast_nullable_to_non_nullable
                      as List<String>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$QuestImplCopyWith<$Res> implements $QuestCopyWith<$Res> {
  factory _$$QuestImplCopyWith(
    _$QuestImpl value,
    $Res Function(_$QuestImpl) then,
  ) = __$$QuestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String questId,
    int tier,
    String title,
    String? description,
    String status,
    List<String> completionTags,
    List<String> progressTags,
  });
}

/// @nodoc
class __$$QuestImplCopyWithImpl<$Res>
    extends _$QuestCopyWithImpl<$Res, _$QuestImpl>
    implements _$$QuestImplCopyWith<$Res> {
  __$$QuestImplCopyWithImpl(
    _$QuestImpl _value,
    $Res Function(_$QuestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Quest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? questId = null,
    Object? tier = null,
    Object? title = null,
    Object? description = freezed,
    Object? status = null,
    Object? completionTags = null,
    Object? progressTags = null,
  }) {
    return _then(
      _$QuestImpl(
        questId: null == questId
            ? _value.questId
            : questId // ignore: cast_nullable_to_non_nullable
                  as String,
        tier: null == tier
            ? _value.tier
            : tier // ignore: cast_nullable_to_non_nullable
                  as int,
        title: null == title
            ? _value.title
            : title // ignore: cast_nullable_to_non_nullable
                  as String,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
        status: null == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as String,
        completionTags: null == completionTags
            ? _value._completionTags
            : completionTags // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        progressTags: null == progressTags
            ? _value._progressTags
            : progressTags // ignore: cast_nullable_to_non_nullable
                  as List<String>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$QuestImpl implements _Quest {
  const _$QuestImpl({
    required this.questId,
    required this.tier,
    required this.title,
    this.description,
    this.status = 'active',
    final List<String> completionTags = const <String>[],
    final List<String> progressTags = const <String>[],
  }) : _completionTags = completionTags,
       _progressTags = progressTags;

  factory _$QuestImpl.fromJson(Map<String, dynamic> json) =>
      _$$QuestImplFromJson(json);

  @override
  final String questId;
  @override
  final int tier;
  @override
  final String title;
  @override
  final String? description;

  /// `active`, `pending_player`, `completed`, `dismissed`, …
  @override
  @JsonKey()
  final String status;
  final List<String> _completionTags;
  @override
  @JsonKey()
  List<String> get completionTags {
    if (_completionTags is EqualUnmodifiableListView) return _completionTags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_completionTags);
  }

  final List<String> _progressTags;
  @override
  @JsonKey()
  List<String> get progressTags {
    if (_progressTags is EqualUnmodifiableListView) return _progressTags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_progressTags);
  }

  @override
  String toString() {
    return 'Quest(questId: $questId, tier: $tier, title: $title, description: $description, status: $status, completionTags: $completionTags, progressTags: $progressTags)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QuestImpl &&
            (identical(other.questId, questId) || other.questId == questId) &&
            (identical(other.tier, tier) || other.tier == tier) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.status, status) || other.status == status) &&
            const DeepCollectionEquality().equals(
              other._completionTags,
              _completionTags,
            ) &&
            const DeepCollectionEquality().equals(
              other._progressTags,
              _progressTags,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    questId,
    tier,
    title,
    description,
    status,
    const DeepCollectionEquality().hash(_completionTags),
    const DeepCollectionEquality().hash(_progressTags),
  );

  /// Create a copy of Quest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$QuestImplCopyWith<_$QuestImpl> get copyWith =>
      __$$QuestImplCopyWithImpl<_$QuestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$QuestImplToJson(this);
  }
}

abstract class _Quest implements Quest {
  const factory _Quest({
    required final String questId,
    required final int tier,
    required final String title,
    final String? description,
    final String status,
    final List<String> completionTags,
    final List<String> progressTags,
  }) = _$QuestImpl;

  factory _Quest.fromJson(Map<String, dynamic> json) = _$QuestImpl.fromJson;

  @override
  String get questId;
  @override
  int get tier;
  @override
  String get title;
  @override
  String? get description;

  /// `active`, `pending_player`, `completed`, `dismissed`, …
  @override
  String get status;
  @override
  List<String> get completionTags;
  @override
  List<String> get progressTags;

  /// Create a copy of Quest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$QuestImplCopyWith<_$QuestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

QuestListResponse _$QuestListResponseFromJson(Map<String, dynamic> json) {
  return _QuestListResponse.fromJson(json);
}

/// @nodoc
mixin _$QuestListResponse {
  List<Quest> get quests => throw _privateConstructorUsedError;

  /// Serializes this QuestListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of QuestListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $QuestListResponseCopyWith<QuestListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QuestListResponseCopyWith<$Res> {
  factory $QuestListResponseCopyWith(
    QuestListResponse value,
    $Res Function(QuestListResponse) then,
  ) = _$QuestListResponseCopyWithImpl<$Res, QuestListResponse>;
  @useResult
  $Res call({List<Quest> quests});
}

/// @nodoc
class _$QuestListResponseCopyWithImpl<$Res, $Val extends QuestListResponse>
    implements $QuestListResponseCopyWith<$Res> {
  _$QuestListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of QuestListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? quests = null}) {
    return _then(
      _value.copyWith(
            quests: null == quests
                ? _value.quests
                : quests // ignore: cast_nullable_to_non_nullable
                      as List<Quest>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$QuestListResponseImplCopyWith<$Res>
    implements $QuestListResponseCopyWith<$Res> {
  factory _$$QuestListResponseImplCopyWith(
    _$QuestListResponseImpl value,
    $Res Function(_$QuestListResponseImpl) then,
  ) = __$$QuestListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<Quest> quests});
}

/// @nodoc
class __$$QuestListResponseImplCopyWithImpl<$Res>
    extends _$QuestListResponseCopyWithImpl<$Res, _$QuestListResponseImpl>
    implements _$$QuestListResponseImplCopyWith<$Res> {
  __$$QuestListResponseImplCopyWithImpl(
    _$QuestListResponseImpl _value,
    $Res Function(_$QuestListResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of QuestListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? quests = null}) {
    return _then(
      _$QuestListResponseImpl(
        quests: null == quests
            ? _value._quests
            : quests // ignore: cast_nullable_to_non_nullable
                  as List<Quest>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$QuestListResponseImpl implements _QuestListResponse {
  const _$QuestListResponseImpl({final List<Quest> quests = const <Quest>[]})
    : _quests = quests;

  factory _$QuestListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$QuestListResponseImplFromJson(json);

  final List<Quest> _quests;
  @override
  @JsonKey()
  List<Quest> get quests {
    if (_quests is EqualUnmodifiableListView) return _quests;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_quests);
  }

  @override
  String toString() {
    return 'QuestListResponse(quests: $quests)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QuestListResponseImpl &&
            const DeepCollectionEquality().equals(other._quests, _quests));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_quests));

  /// Create a copy of QuestListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$QuestListResponseImplCopyWith<_$QuestListResponseImpl> get copyWith =>
      __$$QuestListResponseImplCopyWithImpl<_$QuestListResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$QuestListResponseImplToJson(this);
  }
}

abstract class _QuestListResponse implements QuestListResponse {
  const factory _QuestListResponse({final List<Quest> quests}) =
      _$QuestListResponseImpl;

  factory _QuestListResponse.fromJson(Map<String, dynamic> json) =
      _$QuestListResponseImpl.fromJson;

  @override
  List<Quest> get quests;

  /// Create a copy of QuestListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$QuestListResponseImplCopyWith<_$QuestListResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

QuestCheckResponse _$QuestCheckResponseFromJson(Map<String, dynamic> json) {
  return _QuestCheckResponse.fromJson(json);
}

/// @nodoc
mixin _$QuestCheckResponse {
  String get title => throw _privateConstructorUsedError;
  int get matched => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  int get percentage => throw _privateConstructorUsedError;
  int get pointsSpent => throw _privateConstructorUsedError;

  /// Serializes this QuestCheckResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of QuestCheckResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $QuestCheckResponseCopyWith<QuestCheckResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QuestCheckResponseCopyWith<$Res> {
  factory $QuestCheckResponseCopyWith(
    QuestCheckResponse value,
    $Res Function(QuestCheckResponse) then,
  ) = _$QuestCheckResponseCopyWithImpl<$Res, QuestCheckResponse>;
  @useResult
  $Res call({
    String title,
    int matched,
    int total,
    int percentage,
    int pointsSpent,
  });
}

/// @nodoc
class _$QuestCheckResponseCopyWithImpl<$Res, $Val extends QuestCheckResponse>
    implements $QuestCheckResponseCopyWith<$Res> {
  _$QuestCheckResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of QuestCheckResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? matched = null,
    Object? total = null,
    Object? percentage = null,
    Object? pointsSpent = null,
  }) {
    return _then(
      _value.copyWith(
            title: null == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                      as String,
            matched: null == matched
                ? _value.matched
                : matched // ignore: cast_nullable_to_non_nullable
                      as int,
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
            percentage: null == percentage
                ? _value.percentage
                : percentage // ignore: cast_nullable_to_non_nullable
                      as int,
            pointsSpent: null == pointsSpent
                ? _value.pointsSpent
                : pointsSpent // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$QuestCheckResponseImplCopyWith<$Res>
    implements $QuestCheckResponseCopyWith<$Res> {
  factory _$$QuestCheckResponseImplCopyWith(
    _$QuestCheckResponseImpl value,
    $Res Function(_$QuestCheckResponseImpl) then,
  ) = __$$QuestCheckResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String title,
    int matched,
    int total,
    int percentage,
    int pointsSpent,
  });
}

/// @nodoc
class __$$QuestCheckResponseImplCopyWithImpl<$Res>
    extends _$QuestCheckResponseCopyWithImpl<$Res, _$QuestCheckResponseImpl>
    implements _$$QuestCheckResponseImplCopyWith<$Res> {
  __$$QuestCheckResponseImplCopyWithImpl(
    _$QuestCheckResponseImpl _value,
    $Res Function(_$QuestCheckResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of QuestCheckResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? title = null,
    Object? matched = null,
    Object? total = null,
    Object? percentage = null,
    Object? pointsSpent = null,
  }) {
    return _then(
      _$QuestCheckResponseImpl(
        title: null == title
            ? _value.title
            : title // ignore: cast_nullable_to_non_nullable
                  as String,
        matched: null == matched
            ? _value.matched
            : matched // ignore: cast_nullable_to_non_nullable
                  as int,
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
        percentage: null == percentage
            ? _value.percentage
            : percentage // ignore: cast_nullable_to_non_nullable
                  as int,
        pointsSpent: null == pointsSpent
            ? _value.pointsSpent
            : pointsSpent // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$QuestCheckResponseImpl implements _QuestCheckResponse {
  const _$QuestCheckResponseImpl({
    required this.title,
    this.matched = 0,
    this.total = 0,
    this.percentage = 0,
    this.pointsSpent = 0,
  });

  factory _$QuestCheckResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$QuestCheckResponseImplFromJson(json);

  @override
  final String title;
  @override
  @JsonKey()
  final int matched;
  @override
  @JsonKey()
  final int total;
  @override
  @JsonKey()
  final int percentage;
  @override
  @JsonKey()
  final int pointsSpent;

  @override
  String toString() {
    return 'QuestCheckResponse(title: $title, matched: $matched, total: $total, percentage: $percentage, pointsSpent: $pointsSpent)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QuestCheckResponseImpl &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.matched, matched) || other.matched == matched) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.percentage, percentage) ||
                other.percentage == percentage) &&
            (identical(other.pointsSpent, pointsSpent) ||
                other.pointsSpent == pointsSpent));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, title, matched, total, percentage, pointsSpent);

  /// Create a copy of QuestCheckResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$QuestCheckResponseImplCopyWith<_$QuestCheckResponseImpl> get copyWith =>
      __$$QuestCheckResponseImplCopyWithImpl<_$QuestCheckResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$QuestCheckResponseImplToJson(this);
  }
}

abstract class _QuestCheckResponse implements QuestCheckResponse {
  const factory _QuestCheckResponse({
    required final String title,
    final int matched,
    final int total,
    final int percentage,
    final int pointsSpent,
  }) = _$QuestCheckResponseImpl;

  factory _QuestCheckResponse.fromJson(Map<String, dynamic> json) =
      _$QuestCheckResponseImpl.fromJson;

  @override
  String get title;
  @override
  int get matched;
  @override
  int get total;
  @override
  int get percentage;
  @override
  int get pointsSpent;

  /// Create a copy of QuestCheckResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$QuestCheckResponseImplCopyWith<_$QuestCheckResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
