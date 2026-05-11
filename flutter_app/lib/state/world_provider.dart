import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/clients.dart';
import '../api/models/world_models.dart';

/// `GET /api/worlds` — list of every world the user owns.
final worldsListProvider = FutureProvider.autoDispose<List<World>>((ref) async {
  final api = ref.watch(worldApiProvider);
  final response = await api.list();
  return response.worlds;
});

/// `GET /api/worlds/active` — the world currently flagged active. May be null
/// when the user has worlds but none is marked active (rare; handled
/// gracefully by callers).
final activeWorldProvider = FutureProvider.autoDispose<World?>((ref) async {
  final api = ref.watch(worldApiProvider);
  final response = await api.active();
  return response.world;
});

/// `GET /api/world?world_id={id}` — full world payload (world + entities +
/// handoff). Keyed on the world id so navigating between worlds yields a
/// fresh future without thrashing siblings.
final worldDetailProvider =
    FutureProvider.autoDispose.family<WorldDetailResponse, String>((ref, id) async {
  final api = ref.watch(worldApiProvider);
  return api.fetch(id);
});

/// `GET /api/settings/status` — drives the "API key not configured" banner
/// on the dashboard.
final settingsStatusProvider = FutureProvider.autoDispose((ref) async {
  final api = ref.watch(settingsApiProvider);
  return api.status();
});
