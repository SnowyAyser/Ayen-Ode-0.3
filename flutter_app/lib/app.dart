import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'routing/router.dart';
import 'theme/theme.dart';

class AyenOdeApp extends ConsumerWidget {
  const AyenOdeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'Ayen-Ode',
      debugShowCheckedModeBanner: false,
      theme: buildAyenOdeTheme(),
      routerConfig: router,
    );
  }
}
