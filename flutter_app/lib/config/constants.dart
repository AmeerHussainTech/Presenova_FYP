import 'package:flutter/material.dart';

class AppConstants {
  // Production Render Backend URL (with local dev fallback)
  static const String defaultApiBaseUrl = 'https://fyp-presenova.onrender.com/api';
  static const String defaultSocketUrl = 'https://fyp-presenova.onrender.com';
  
  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'auth_user';
  static const String apiUrlKey = 'custom_api_url';
}

class AppColors {
  // Deep space dark theme canvas
  static const Color background = Color(0xFF080B11);
  static const Color surface = Color(0xFF111827);
  static const Color surfaceElevated = Color(0xFF1E293B);
  static const Color surfaceGlass = Color(0x991E293B);

  // Brand purples & gradients
  static const Color primary = Color(0xFF8B5CF6);       // Vibrant Violet
  static const Color primaryLight = Color(0xFFA78BFA);  // Soft Purple
  static const Color primaryDark = Color(0xFF6D28D9);   // Deep Purple
  static const Color secondary = Color(0xFF06B6D4);     // Neon Cyan
  static const Color accent = Color(0xFFEC4899);        // Electric Pink

  // Status colors
  static const Color success = Color(0xFF10B981);       // Emerald Green
  static const Color warning = Color(0xFFF59E0B);       // Warm Amber
  static const Color error = Color(0xFFEF4444);         // Rose Red
  static const Color info = Color(0xFF3B82F6);          // Sky Blue

  // Text & Borders
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);
  static const Color border = Color(0x33A78BFA);
  static const Color borderSubtle = Color(0x1AFFFFFF);

  // Gradient presets
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, Color(0xFF6366F1)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0x331E293B), Color(0x110F172A)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient liveIndicatorGradient = LinearGradient(
    colors: [Color(0xFFEF4444), Color(0xFFF97316)],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );
}
