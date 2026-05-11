// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settings_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AppSettingsImpl _$$AppSettingsImplFromJson(Map<String, dynamic> json) =>
    _$AppSettingsImpl(
      anthropicApiKeySet: json['anthropic_api_key_set'] as bool? ?? false,
      anthropicApiKeyMasked: json['anthropic_api_key_masked'] as String?,
      appUsername: json['app_username'] as String?,
      appPasswordSet: json['app_password_set'] as bool? ?? false,
      allowedIps: json['allowed_ips'] as String?,
      ayenOdePort: json['ayen_ode_port'] as String?,
      fullscreen: json['fullscreen'] as bool? ?? false,
    );

Map<String, dynamic> _$$AppSettingsImplToJson(_$AppSettingsImpl instance) =>
    <String, dynamic>{
      'anthropic_api_key_set': instance.anthropicApiKeySet,
      'anthropic_api_key_masked': instance.anthropicApiKeyMasked,
      'app_username': instance.appUsername,
      'app_password_set': instance.appPasswordSet,
      'allowed_ips': instance.allowedIps,
      'ayen_ode_port': instance.ayenOdePort,
      'fullscreen': instance.fullscreen,
    };

_$SettingsStatusImpl _$$SettingsStatusImplFromJson(Map<String, dynamic> json) =>
    _$SettingsStatusImpl(
      apiKeyConfigured: json['api_key_configured'] as bool? ?? false,
    );

Map<String, dynamic> _$$SettingsStatusImplToJson(
  _$SettingsStatusImpl instance,
) => <String, dynamic>{'api_key_configured': instance.apiKeyConfigured};
