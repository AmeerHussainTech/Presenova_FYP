import 'package:dio/dio.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService;

  AuthService({ApiService? apiService}) : _apiService = apiService ?? ApiService();

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _apiService.dio.post(
        '/auth/login',
        data: {
          'email': email.trim().toLowerCase(),
          'password': password,
        },
      );
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw e.error?.toString() ?? 'Login failed';
    }
  }

  Future<Map<String, dynamic>> signup(String name, String email, String password) async {
    try {
      final response = await _apiService.dio.post(
        '/auth/signup',
        data: {
          'name': name.trim(),
          'email': email.trim().toLowerCase(),
          'password': password,
        },
      );
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw e.error?.toString() ?? 'Registration failed';
    }
  }

  Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await _apiService.dio.post(
        '/auth/forgot-password',
        data: {
          'email': email.trim().toLowerCase(),
        },
      );
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw e.error?.toString() ?? 'Password reset request failed';
    }
  }

  Future<Map<String, dynamic>> resetPassword(String token, String password) async {
    try {
      final response = await _apiService.dio.post(
        '/auth/reset-password',
        data: {
          'token': token.trim(),
          'password': password,
        },
      );
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw e.error?.toString() ?? 'Password update failed';
    }
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final response = await _apiService.dio.get('/auth/me');
      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      throw e.error?.toString() ?? 'Could not retrieve profile';
    }
  }

  Future<List<dynamic>> getUserHistory() async {
    try {
      final response = await _apiService.dio.get('/auth/history');
      final data = response.data;
      if (data is Map && data['reports'] is List) {
        return data['reports'] as List;
      }
      return [];
    } catch (_) {
      return [];
    }
  }
}
