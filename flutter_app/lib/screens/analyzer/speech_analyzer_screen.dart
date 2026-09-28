import 'package:flutter/material.dart';
import '../../config/constants.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/glass_card.dart';
import '../../widgets/metric_badge.dart';

class SpeechAnalyzerScreen extends StatefulWidget {
  const SpeechAnalyzerScreen({Key? key}) : super(key: key);

  @override
  State<SpeechAnalyzerScreen> createState() => _SpeechAnalyzerScreenState();
}

class _SpeechAnalyzerScreenState extends State<SpeechAnalyzerScreen> {
  bool _isRecording = false;
  bool _hasAnalysis = true; // default demo report shown
  int _recordSeconds = 0;

  void _toggleRecording() {
    setState(() {
      _isRecording = !_isRecording;
      if (!_isRecording) {
        _hasAnalysis = true;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              const Text(
                'Speech Analyzer',
                style: TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 2),
              const Text(
                'Record or upload audio to analyze pace, fillers & cadence',
                style: TextStyle(
                  color: AppColors.textMuted,
                  fontSize: 13,
                ),
              ),
              const SizedBox(height: 20),

              // Recording Hub Card
              GlassCard(
                padding: const EdgeInsets.symmetric(vertical: 24.0, horizontal: 20.0),
                child: Column(
                  children: [
                    GestureDetector(
                      onTap: _toggleRecording,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: _isRecording
                              ? const LinearGradient(colors: [Colors.redAccent, Colors.red])
                              : AppColors.primaryGradient,
                          boxShadow: [
                            BoxShadow(
                              color: (_isRecording ? Colors.red : AppColors.primary).withOpacity(0.4),
                              blurRadius: _isRecording ? 30 : 16,
                              spreadRadius: _isRecording ? 4 : 0,
                            ),
                          ],
                        ),
                        child: Icon(
                          _isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                          color: Colors.white,
                          size: 38,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _isRecording ? 'Listening & Analyzing...' : 'Tap Mic to Start Recording',
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _isRecording
                          ? 'Speak naturally at your normal presentation pitch'
                          : 'Or select a recorded audio file (.wav, .m4a, .mp3)',
                      style: const TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 12,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 18),
                    OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('File picker ready: select speech audio')),
                        );
                      },
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: AppColors.primaryLight.withOpacity(0.3)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      ),
                      icon: const Icon(Icons.upload_file_rounded, size: 18, color: AppColors.primaryLight),
                      label: const Text(
                        'Upload Audio File',
                        style: TextStyle(color: AppColors.textPrimary, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Comprehensive Metrics Report
              if (_hasAnalysis) ...[
                const Text(
                  'Analysis Breakdown',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 12),

                // Metrics Grid
                GridView.count(
                  crossAxisCount: 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  childAspectRatio: 1.5,
                  children: const [
                    MetricBadge(
                      label: 'Speaking Speed',
                      value: '142',
                      unit: 'wpm (Ideal)',
                      score: 95,
                      icon: Icons.speed_rounded,
                    ),
                    MetricBadge(
                      label: 'Filler Frequency',
                      value: '3',
                      unit: 'Total ("um", "like")',
                      score: 85,
                      icon: Icons.filter_alt_off_rounded,
                    ),
                    MetricBadge(
                      label: 'Pronunciation Clarity',
                      value: '93%',
                      unit: 'High',
                      score: 93,
                      icon: Icons.verified_rounded,
                    ),
                    MetricBadge(
                      label: 'Vocal Variety',
                      value: '8.4',
                      unit: '/10 Dynamic',
                      score: 84,
                      icon: Icons.graphic_eq_rounded,
                    ),
                  ],
                ),
                const SizedBox(height: 18),

                // AI Recommendations Card
                GlassCard(
                  padding: const EdgeInsets.all(18),
                  borderColor: AppColors.primaryLight.withOpacity(0.3),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: const [
                          Icon(Icons.lightbulb_outline_rounded, color: Colors.amber, size: 20),
                          SizedBox(width: 8),
                          Text(
                            'AI Speaking Recommendations',
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontWeight: FontWeight.w700,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _buildBulletPoint('Your average speed of 142 WPM falls directly within the optimal academic conference range (130-150 WPM).'),
                      _buildBulletPoint('You used "um" 2 times during slide transitions. Replacing filler sounds with deliberate 1-second silences will project greater authority.'),
                      _buildBulletPoint('Volume consistency was solid with no inaudible trailing at the end of sentences.'),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 6),
            width: 5,
            height: 5,
            decoration: const BoxDecoration(
              color: AppColors.secondary,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 13,
                height: 1.45,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
