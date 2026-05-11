import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.productionApiBaseUrl,
    required this.useProduction,
  });

  final String apiBaseUrl;
  final String productionApiBaseUrl;
  final bool useProduction;

  String get effectiveBaseUrl {
    const override = String.fromEnvironment('API_BASE_URL');
    if (override.isNotEmpty) return override;
    return useProduction ? productionApiBaseUrl : apiBaseUrl;
  }

  static Future<AppConfig> load() async {
    final raw = await rootBundle.loadString('assets/config.json');
    final json = jsonDecode(raw) as Map<String, dynamic>;
    return AppConfig(
      apiBaseUrl: json['api_base_url'] as String,
      productionApiBaseUrl: json['production_api_base_url'] as String,
      useProduction: json['use_production'] as bool? ?? false,
    );
  }
}

final appConfigProvider = Provider<AppConfig>((ref) {
  throw StateError('AppConfig must be overridden in ProviderScope');
});
