import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config/config.dart';
import 'api_exception.dart';
import 'token_storage.dart';

/// Holds the Dio instance the rest of the app shares.
///
/// Three things are wired up here:
///   1. Base URL from `AppConfig` (allows `--dart-define=API_BASE_URL=…`).
///   2. `_AuthInterceptor` — adds `Authorization: Bearer <token>` to every
///      request, and on 401 clears the token + bumps `authChangeNotifier`
///      so the router can redirect to login.
///   3. `_JsonRpcUnwrapInterceptor` — mirrors `app.js#unwrapJsonRpcResponse`.
///      When the response body has `{jsonrpc: "2.0", result: …}` shape, the
///      interceptor swaps `response.data` for the bare `result`. Most
///      endpoints return plain JSON; this only fires on the
///      JSON-RPC-shaped ones (MCP-style routes).
class ApiClient {
  ApiClient({required this.dio});

  final Dio dio;
}

/// Listenable that flips when auth state changes (sign-in OR sign-out).
/// `GoRouter` watches this via `refreshListenable` to re-evaluate redirects.
final authChangeNotifier = ValueNotifier<int>(0);
void bumpAuth() => authChangeNotifier.value++;

final dioProvider = Provider<Dio>((ref) {
  final config = ref.watch(appConfigProvider);
  final tokens = ref.watch(tokenStorageProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: config.effectiveBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 120),
      contentType: 'application/json',
      responseType: ResponseType.json,
      // The narrative endpoint can return >1s of text; tolerate large bodies.
      validateStatus: (status) => status != null && status < 500,
    ),
  );

  dio.interceptors.add(_AuthInterceptor(tokens: tokens));
  dio.interceptors.add(_JsonRpcUnwrapInterceptor());

  return dio;
});

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(dio: ref.watch(dioProvider));
});

class _AuthInterceptor extends Interceptor {
  _AuthInterceptor({required this.tokens});

  final TokenStorage tokens;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await tokens.readToken();
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onResponse(
    Response response,
    ResponseInterceptorHandler handler,
  ) async {
    if (response.statusCode == 401) {
      await tokens.clearAll();
      bumpAuth();
    }
    handler.next(response);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      await tokens.clearAll();
      bumpAuth();
    }
    handler.next(err);
  }
}

class _JsonRpcUnwrapInterceptor extends Interceptor {
  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final body = response.data;
    if (body is Map<String, dynamic> &&
        body['jsonrpc'] == '2.0' &&
        body.containsKey('result')) {
      response.data = body['result'];
    }
    handler.next(response);
  }
}

/// Common error-shaping for endpoint methods. Converts Dio's noisy
/// exception surface into the much smaller `ApiException` we surface to UI.
ApiException toApiException(Object error, {String fallback = 'Request failed'}) {
  if (error is DioException) {
    final status = error.response?.statusCode;
    final body = error.response?.data;
    String? message;
    if (body is Map<String, dynamic>) {
      message = body['error'] as String? ?? body['detail'] as String?;
    } else if (body is String && body.isNotEmpty) {
      message = body;
    }
    return ApiException(
      message ?? error.message ?? fallback,
      statusCode: status,
      cause: error,
    );
  }
  return ApiException(error.toString(), cause: error);
}
