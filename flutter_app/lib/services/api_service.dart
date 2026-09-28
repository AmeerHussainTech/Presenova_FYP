import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';

class ApiService {
  late final Dio dio;

  ApiService({String? baseUrl}) {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? AppConstants.defaultApiBaseUrl,
        connectTimeout: const Duration(seconds: 45),
        receiveTimeout: const Duration(seconds: 45),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Attach Interceptors for JWT & error normalization
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final prefs = await SharedPreferences.getInstance();
          final token = prefs.getString(AppConstants.tokenKey);
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException error, handler) async {
          // Normalize error messages
          String userFriendlyMessage = 'An unexpected network error occurred.';
          if (error.response?.data != null && error.response?.data is Map) {
            final data = error.response!.data as Map;
            userFriendlyMessage = data['message'] ?? data['error'] ?? userFriendlyMessage;
          } else if (error.type == DioExceptionType.connectionTimeout) {
            userFriendlyMessage = 'Server took too long to respond. The free Render instance may be waking up.';
          } else if (error.type == DioExceptionType.connectionError) {
            userFriendlyMessage = 'Unable to connect to server. Please check your internet connection.';
          }
          
          return handler.reject(
            DioException(
              requestOptions: error.requestOptions,
              response: error.response,
              type: error.type,
              error: userFriendlyMessage,
            ),
          );
        },
      ),
    );
  }
}
