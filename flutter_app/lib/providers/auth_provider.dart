import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService = AuthService();

  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;
  Map<String, dynamic>? _user;
  String? _token;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String? get successMessage => _successMessage;
  Map<String, dynamic>? get user => _user;
  String? get token => _token;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;

  AuthProvider() {
    _loadSession();
  }

  Future<void> _loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(AppConstants.tokenKey);
    final userJson = prefs.getString(AppConstants.userKey);
    if (userJson != null) {
      try {
        _user = jsonDecode(userJson);
      } catch (_) {}
    }
    notifyListeners();
  }

  void clearMessages() {
    _errorMessage = null;
    _successMessage = null;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _authService.login(email, password);
      _token = res['access_token'];
      _user = res['user'];

      final prefs = await SharedPreferences.getInstance();
      if (_token != null) {
        await prefs.setString(AppConstants.tokenKey, _token!);
      }
      if (_user != null) {
        await prefs.setString(AppConstants.userKey, jsonEncode(_user));
      }
      if (res['refresh_token'] != null) {
        await prefs.setString(AppConstants.refreshTokenKey, res['refresh_token']);
      }

      _isLoading = false;
      _successMessage = 'Login successful!';
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> signup(String name, String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _authService.signup(name, email, password);
      _token = res['access_token'];
      _user = res['user'];

      final prefs = await SharedPreferences.getInstance();
      if (_token != null) {
        await prefs.setString(AppConstants.tokenKey, _token!);
      }
      if (_user != null) {
        await prefs.setString(AppConstants.userKey, jsonEncode(_user));
      }

      _isLoading = false;
      _successMessage = 'Account created successfully!';
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<String?> forgotPassword(String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _authService.forgotPassword(email);
      _isLoading = false;
      _successMessage = res['message'] ?? 'Password reset instructions generated.';
      notifyListeners();
      // Return dev token if available for testing
      return res['dev_reset_token'];
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }

  Future<bool> resetPassword(String token, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _authService.resetPassword(token, password);
      _isLoading = false;
      _successMessage = res['message'] ?? 'Password updated successfully!';
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.tokenKey);
    await prefs.remove(AppConstants.refreshTokenKey);
    await prefs.remove(AppConstants.userKey);
    notifyListeners();
  }
}
