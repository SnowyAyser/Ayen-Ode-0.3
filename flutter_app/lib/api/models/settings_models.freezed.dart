// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'settings_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

AppSettings _$AppSettingsFromJson(Map<String, dynamic> json) {
  return _AppSettings.fromJson(json);
}

/// @nodoc
mixin _$AppSettings {
  bool get anthropicApiKeySet => throw _privateConstructorUsedError;
  String? get anthropicApiKeyMasked => throw _privateConstructorUsedError;
  String? get appUsername => throw _privateConstructorUsedError;
  bool get appPasswordSet => throw _privateConstructorUsedError;
  String? get allowedIps => throw _privateConstructorUsedError;
  String? get ayenOdePort => throw _privateConstructorUsedError;
  bool get fullscreen => throw _privateConstructorUsedError;

  /// Serializes this AppSettings to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AppSettings
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AppSettingsCopyWith<AppSettings> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AppSettingsCopyWith<$Res> {
  factory $AppSettingsCopyWith(
    AppSettings value,
    $Res Function(AppSettings) then,
  ) = _$AppSettingsCopyWithImpl<$Res, AppSettings>;
  @useResult
  $Res call({
    bool anthropicApiKeySet,
    String? anthropicApiKeyMasked,
    String? appUsername,
    bool appPasswordSet,
    String? allowedIps,
    String? ayenOdePort,
    bool fullscreen,
  });
}

/// @nodoc
class _$AppSettingsCopyWithImpl<$Res, $Val extends AppSettings>
    implements $AppSettingsCopyWith<$Res> {
  _$AppSettingsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AppSettings
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? anthropicApiKeySet = null,
    Object? anthropicApiKeyMasked = freezed,
    Object? appUsername = freezed,
    Object? appPasswordSet = null,
    Object? allowedIps = freezed,
    Object? ayenOdePort = freezed,
    Object? fullscreen = null,
  }) {
    return _then(
      _value.copyWith(
            anthropicApiKeySet: null == anthropicApiKeySet
                ? _value.anthropicApiKeySet
                : anthropicApiKeySet // ignore: cast_nullable_to_non_nullable
                      as bool,
            anthropicApiKeyMasked: freezed == anthropicApiKeyMasked
                ? _value.anthropicApiKeyMasked
                : anthropicApiKeyMasked // ignore: cast_nullable_to_non_nullable
                      as String?,
            appUsername: freezed == appUsername
                ? _value.appUsername
                : appUsername // ignore: cast_nullable_to_non_nullable
                      as String?,
            appPasswordSet: null == appPasswordSet
                ? _value.appPasswordSet
                : appPasswordSet // ignore: cast_nullable_to_non_nullable
                      as bool,
            allowedIps: freezed == allowedIps
                ? _value.allowedIps
                : allowedIps // ignore: cast_nullable_to_non_nullable
                      as String?,
            ayenOdePort: freezed == ayenOdePort
                ? _value.ayenOdePort
                : ayenOdePort // ignore: cast_nullable_to_non_nullable
                      as String?,
            fullscreen: null == fullscreen
                ? _value.fullscreen
                : fullscreen // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$AppSettingsImplCopyWith<$Res>
    implements $AppSettingsCopyWith<$Res> {
  factory _$$AppSettingsImplCopyWith(
    _$AppSettingsImpl value,
    $Res Function(_$AppSettingsImpl) then,
  ) = __$$AppSettingsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    bool anthropicApiKeySet,
    String? anthropicApiKeyMasked,
    String? appUsername,
    bool appPasswordSet,
    String? allowedIps,
    String? ayenOdePort,
    bool fullscreen,
  });
}

/// @nodoc
class __$$AppSettingsImplCopyWithImpl<$Res>
    extends _$AppSettingsCopyWithImpl<$Res, _$AppSettingsImpl>
    implements _$$AppSettingsImplCopyWith<$Res> {
  __$$AppSettingsImplCopyWithImpl(
    _$AppSettingsImpl _value,
    $Res Function(_$AppSettingsImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of AppSettings
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? anthropicApiKeySet = null,
    Object? anthropicApiKeyMasked = freezed,
    Object? appUsername = freezed,
    Object? appPasswordSet = null,
    Object? allowedIps = freezed,
    Object? ayenOdePort = freezed,
    Object? fullscreen = null,
  }) {
    return _then(
      _$AppSettingsImpl(
        anthropicApiKeySet: null == anthropicApiKeySet
            ? _value.anthropicApiKeySet
            : anthropicApiKeySet // ignore: cast_nullable_to_non_nullable
                  as bool,
        anthropicApiKeyMasked: freezed == anthropicApiKeyMasked
            ? _value.anthropicApiKeyMasked
            : anthropicApiKeyMasked // ignore: cast_nullable_to_non_nullable
                  as String?,
        appUsername: freezed == appUsername
            ? _value.appUsername
            : appUsername // ignore: cast_nullable_to_non_nullable
                  as String?,
        appPasswordSet: null == appPasswordSet
            ? _value.appPasswordSet
            : appPasswordSet // ignore: cast_nullable_to_non_nullable
                  as bool,
        allowedIps: freezed == allowedIps
            ? _value.allowedIps
            : allowedIps // ignore: cast_nullable_to_non_nullable
                  as String?,
        ayenOdePort: freezed == ayenOdePort
            ? _value.ayenOdePort
            : ayenOdePort // ignore: cast_nullable_to_non_nullable
                  as String?,
        fullscreen: null == fullscreen
            ? _value.fullscreen
            : fullscreen // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$AppSettingsImpl implements _AppSettings {
  const _$AppSettingsImpl({
    this.anthropicApiKeySet = false,
    this.anthropicApiKeyMasked,
    this.appUsername,
    this.appPasswordSet = false,
    this.allowedIps,
    this.ayenOdePort,
    this.fullscreen = false,
  });

  factory _$AppSettingsImpl.fromJson(Map<String, dynamic> json) =>
      _$$AppSettingsImplFromJson(json);

  @override
  @JsonKey()
  final bool anthropicApiKeySet;
  @override
  final String? anthropicApiKeyMasked;
  @override
  final String? appUsername;
  @override
  @JsonKey()
  final bool appPasswordSet;
  @override
  final String? allowedIps;
  @override
  final String? ayenOdePort;
  @override
  @JsonKey()
  final bool fullscreen;

  @override
  String toString() {
    return 'AppSettings(anthropicApiKeySet: $anthropicApiKeySet, anthropicApiKeyMasked: $anthropicApiKeyMasked, appUsername: $appUsername, appPasswordSet: $appPasswordSet, allowedIps: $allowedIps, ayenOdePort: $ayenOdePort, fullscreen: $fullscreen)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AppSettingsImpl &&
            (identical(other.anthropicApiKeySet, anthropicApiKeySet) ||
                other.anthropicApiKeySet == anthropicApiKeySet) &&
            (identical(other.anthropicApiKeyMasked, anthropicApiKeyMasked) ||
                other.anthropicApiKeyMasked == anthropicApiKeyMasked) &&
            (identical(other.appUsername, appUsername) ||
                other.appUsername == appUsername) &&
            (identical(other.appPasswordSet, appPasswordSet) ||
                other.appPasswordSet == appPasswordSet) &&
            (identical(other.allowedIps, allowedIps) ||
                other.allowedIps == allowedIps) &&
            (identical(other.ayenOdePort, ayenOdePort) ||
                other.ayenOdePort == ayenOdePort) &&
            (identical(other.fullscreen, fullscreen) ||
                other.fullscreen == fullscreen));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    anthropicApiKeySet,
    anthropicApiKeyMasked,
    appUsername,
    appPasswordSet,
    allowedIps,
    ayenOdePort,
    fullscreen,
  );

  /// Create a copy of AppSettings
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AppSettingsImplCopyWith<_$AppSettingsImpl> get copyWith =>
      __$$AppSettingsImplCopyWithImpl<_$AppSettingsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AppSettingsImplToJson(this);
  }
}

abstract class _AppSettings implements AppSettings {
  const factory _AppSettings({
    final bool anthropicApiKeySet,
    final String? anthropicApiKeyMasked,
    final String? appUsername,
    final bool appPasswordSet,
    final String? allowedIps,
    final String? ayenOdePort,
    final bool fullscreen,
  }) = _$AppSettingsImpl;

  factory _AppSettings.fromJson(Map<String, dynamic> json) =
      _$AppSettingsImpl.fromJson;

  @override
  bool get anthropicApiKeySet;
  @override
  String? get anthropicApiKeyMasked;
  @override
  String? get appUsername;
  @override
  bool get appPasswordSet;
  @override
  String? get allowedIps;
  @override
  String? get ayenOdePort;
  @override
  bool get fullscreen;

  /// Create a copy of AppSettings
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AppSettingsImplCopyWith<_$AppSettingsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SettingsStatus _$SettingsStatusFromJson(Map<String, dynamic> json) {
  return _SettingsStatus.fromJson(json);
}

/// @nodoc
mixin _$SettingsStatus {
  bool get apiKeyConfigured => throw _privateConstructorUsedError;

  /// Serializes this SettingsStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SettingsStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SettingsStatusCopyWith<SettingsStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SettingsStatusCopyWith<$Res> {
  factory $SettingsStatusCopyWith(
    SettingsStatus value,
    $Res Function(SettingsStatus) then,
  ) = _$SettingsStatusCopyWithImpl<$Res, SettingsStatus>;
  @useResult
  $Res call({bool apiKeyConfigured});
}

/// @nodoc
class _$SettingsStatusCopyWithImpl<$Res, $Val extends SettingsStatus>
    implements $SettingsStatusCopyWith<$Res> {
  _$SettingsStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SettingsStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? apiKeyConfigured = null}) {
    return _then(
      _value.copyWith(
            apiKeyConfigured: null == apiKeyConfigured
                ? _value.apiKeyConfigured
                : apiKeyConfigured // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$SettingsStatusImplCopyWith<$Res>
    implements $SettingsStatusCopyWith<$Res> {
  factory _$$SettingsStatusImplCopyWith(
    _$SettingsStatusImpl value,
    $Res Function(_$SettingsStatusImpl) then,
  ) = __$$SettingsStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool apiKeyConfigured});
}

/// @nodoc
class __$$SettingsStatusImplCopyWithImpl<$Res>
    extends _$SettingsStatusCopyWithImpl<$Res, _$SettingsStatusImpl>
    implements _$$SettingsStatusImplCopyWith<$Res> {
  __$$SettingsStatusImplCopyWithImpl(
    _$SettingsStatusImpl _value,
    $Res Function(_$SettingsStatusImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of SettingsStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? apiKeyConfigured = null}) {
    return _then(
      _$SettingsStatusImpl(
        apiKeyConfigured: null == apiKeyConfigured
            ? _value.apiKeyConfigured
            : apiKeyConfigured // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$SettingsStatusImpl implements _SettingsStatus {
  const _$SettingsStatusImpl({this.apiKeyConfigured = false});

  factory _$SettingsStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$SettingsStatusImplFromJson(json);

  @override
  @JsonKey()
  final bool apiKeyConfigured;

  @override
  String toString() {
    return 'SettingsStatus(apiKeyConfigured: $apiKeyConfigured)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SettingsStatusImpl &&
            (identical(other.apiKeyConfigured, apiKeyConfigured) ||
                other.apiKeyConfigured == apiKeyConfigured));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, apiKeyConfigured);

  /// Create a copy of SettingsStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SettingsStatusImplCopyWith<_$SettingsStatusImpl> get copyWith =>
      __$$SettingsStatusImplCopyWithImpl<_$SettingsStatusImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$SettingsStatusImplToJson(this);
  }
}

abstract class _SettingsStatus implements SettingsStatus {
  const factory _SettingsStatus({final bool apiKeyConfigured}) =
      _$SettingsStatusImpl;

  factory _SettingsStatus.fromJson(Map<String, dynamic> json) =
      _$SettingsStatusImpl.fromJson;

  @override
  bool get apiKeyConfigured;

  /// Create a copy of SettingsStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SettingsStatusImplCopyWith<_$SettingsStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
