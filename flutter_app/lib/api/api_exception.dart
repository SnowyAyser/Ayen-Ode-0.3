/// Thrown by the API layer when a request fails in a way the UI should
/// surface. Holds the original `DioException` (for diagnostics) and a
/// best-effort error message extracted from the server response.
class ApiException implements Exception {
  ApiException(this.message, {this.statusCode, this.cause});

  final String message;
  final int? statusCode;
  final Object? cause;

  @override
  String toString() =>
      'ApiException(${statusCode ?? '-'}: $message)';
}
