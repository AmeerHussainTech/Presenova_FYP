import 'dart:async';
import 'package:flutter/material.dart';

class CoachProvider with ChangeNotifier {
  bool _isSessionActive = false;
  bool _isPaused = false;
  int _elapsedSeconds = 0;
  Timer? _timer;

  // Real-time Presentation Metrics
  double _currentWpm = 135.0;           // Words per minute (ideal: 130-150)
  double _volumeLevel = 0.65;          // 0.0 to 1.0 (decibel relative level)
  double _clarityScore = 88.0;         // 0 to 100
  int _fillerWordsCount = 2;           // count of 'um', 'uh', 'like'
  String _currentFeedback = "Pace is optimal. Maintain current eye level and vocal projection.";
  String _sentiment = "Confident & Engaging";

  // List of live coach suggestions
  final List<String> _liveSuggestions = [
    "Great volume! Keep your voice steady.",
    "Pause for 2 seconds after key arguments to emphasize points.",
    "Watch out for filler words like 'basically'.",
  ];

  bool get isSessionActive => _isSessionActive;
  bool get isPaused => _isPaused;
  int get elapsedSeconds => _elapsedSeconds;
  double get currentWpm => _currentWpm;
  double get volumeLevel => _volumeLevel;
  double get clarityScore => _clarityScore;
  int get fillerWordsCount => _fillerWordsCount;
  String get currentFeedback => _currentFeedback;
  String get sentiment => _sentiment;
  List<String> get liveSuggestions => _liveSuggestions;

  String get formattedTime {
    final minutes = (_elapsedSeconds ~/ 60).toString().padLeft(2, '0');
    final seconds = (_elapsedSeconds % 60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  void startSession() {
    _isSessionActive = true;
    _isPaused = false;
    _elapsedSeconds = 0;
    _fillerWordsCount = 0;
    _currentFeedback = "Listening to speech cadence and tone...";
    _liveSuggestions.clear();
    _liveSuggestions.add("Live AI Coach active. Start speaking when ready.");
    
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!_isPaused) {
        _elapsedSeconds++;
        _simulateLiveMetrics();
        notifyListeners();
      }
    });
    notifyListeners();
  }

  void pauseSession() {
    _isPaused = true;
    notifyListeners();
  }

  void resumeSession() {
    _isPaused = false;
    notifyListeners();
  }

  void stopSession() {
    _isSessionActive = false;
    _isPaused = false;
    _timer?.cancel();
    _timer = null;
    notifyListeners();
  }

  void _simulateLiveMetrics() {
    // Subtle real-time fluctuations simulating audio input and speech processing
    if (_elapsedSeconds % 4 == 0) {
      _currentWpm = 130 + (_elapsedSeconds % 7) * 3.5;
      _volumeLevel = 0.55 + ((_elapsedSeconds % 5) * 0.08);
      if (_volumeLevel > 0.95) _volumeLevel = 0.85;
    }

    if (_elapsedSeconds % 12 == 0) {
      final tips = [
        "Excellent pacing! Your audience can easily follow your ideas.",
        "Consider lowering speed slightly on technical slides.",
        "Clear articulation detected. Keep maintaining eye contact.",
        "Tone is authoritative and calm. Great presence.",
      ];
      final newTip = tips[(_elapsedSeconds ~/ 12) % tips.length];
      _currentFeedback = newTip;
      _liveSuggestions.insert(0, newTip);
      if (_liveSuggestions.length > 6) {
        _liveSuggestions.removeLast();
      }
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
