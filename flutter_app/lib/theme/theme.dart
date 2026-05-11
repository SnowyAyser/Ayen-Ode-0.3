import 'package:flutter/material.dart';

/// Placeholder theme — final tokens land in Phase 3.
ThemeData buildAyenOdeTheme() {
  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFFB45309),
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: const Color(0xFF020617),
  );
}
