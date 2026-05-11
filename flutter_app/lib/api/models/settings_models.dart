import 'package:freezed_annotation/freezed_annotation.dart';

part 'settings_models.freezed.dart';
part 'settings_models.g.dart';

@freezed
class AppSettings with _$AppSettings {
  const factory AppSettings({
    @Default(false) bool anthropicApiKeySet,
    String? anthropicApiKeyMasked,
    String? appUsername,
    @Default(false) bool appPasswordSet,
    String? allowedIps,
    String? ayenOdePort,
    @Default(false) bool fullscreen,
  }) = _AppSettings;

  factory AppSettings.fromJson(Map<String, dynamic> json) =>
      _$AppSettingsFromJson(json);
}

@freezed
class SettingsStatus with _$SettingsStatus {
  const factory SettingsStatus({
    @Default(false) bool apiKeyConfigured,
  }) = _SettingsStatus;

  factory SettingsStatus.fromJson(Map<String, dynamic> json) =>
      _$SettingsStatusFromJson(json);
}
