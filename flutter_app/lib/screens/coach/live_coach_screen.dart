import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/constants.dart';
import '../../providers/coach_provider.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/glass_card.dart';

class LiveCoachScreen extends StatelessWidget {
  const LiveCoachScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final coach = Provider.of<CoachProvider>(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Live AI Coach',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: coach.isSessionActive
                                  ? (coach.isPaused ? AppColors.warning : AppColors.success)
                                  : AppColors.textMuted,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            coach.isSessionActive
                                ? (coach.isPaused ? 'Session Paused' : 'Live Rehearsal Active')
                                : 'Ready to Start',
                            style: TextStyle(
                              color: coach.isSessionActive
                                  ? (coach.isPaused ? AppColors.warning : AppColors.success)
                                  : AppColors.textMuted,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  if (coach.isSessionActive)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: AppColors.primaryLight.withOpacity(0.3)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.timer_outlined, color: AppColors.primaryLight, size: 16),
                          const SizedBox(width: 6),
                          Text(
                            coach.formattedTime,
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontWeight: FontWeight.w700,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 20),

              // Interactive HUD Viewport
              Container(
                height: 240,
                width: double.infinity,
                decoration: BoxDecoration(
                  gradient: const RadialGradient(
                    center: Alignment.center,
                    radius: 0.8,
                    colors: [Color(0xFF1E1B4B), Color(0xFF0F172A), AppColors.background],
                  ),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withOpacity(0.2),
                      blurRadius: 30,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Stack(
                  children: [
                    // Grid background lines
                    Positioned.fill(
                      child: Opacity(
                        opacity: 0.1,
                        child: GridPaper(
                          color: AppColors.primaryLight,
                          divisions: 2,
                          subdivisions: 1,
                        ),
                      ),
                    ),

                    // Central Audio Waveform Visualizer
                    Center(
                      child: coach.isSessionActive && !coach.isPaused
                          ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: List.generate(14, (index) {
                                final height = 18.0 +
                                    (coach.volumeLevel * 60.0 * (1 - (index - 7).abs() / 9.0)) +
                                    ((index % 3) * 6.0);
                                return AnimatedContainer(
                                  duration: const Duration(milliseconds: 250),
                                  margin: const EdgeInsets.symmetric(horizontal: 3),
                                  width: 4,
                                  height: height.clamp(12.0, 95.0),
                                  decoration: BoxDecoration(
                                    gradient: const LinearGradient(
                                      colors: [AppColors.secondary, AppColors.primaryLight],
                                      begin: Alignment.bottomCenter,
                                      end: Alignment.topCenter,
                                    ),
                                    borderRadius: BorderRadius.circular(4),
                                    boxShadow: [
                                      BoxShadow(
                                        color: AppColors.secondary.withOpacity(0.4),
                                        blurRadius: 6,
                                      ),
                                    ],
                                  ),
                                );
                              }),
                            )
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    color: AppColors.primary.withOpacity(0.12),
                                    shape: BoxShape.circle,
                                    border: Border.all(color: AppColors.primaryLight.withOpacity(0.3)),
                                  ),
                                  child: const Icon(Icons.mic_none_rounded, color: AppColors.primaryLight, size: 36),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  coach.isPaused ? 'Rehearsal Paused' : 'Tap Start to Rehearse',
                                  style: const TextStyle(
                                    color: AppColors.textPrimary,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  coach.isPaused
                                      ? 'Tap Resume to continue coaching'
                                      : 'Instant real-time pace & volume tips',
                                  style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                                ),
                              ],
                            ),
                    ),

                    // Top HUD overlays
                    if (coach.isSessionActive)
                      Positioned(
                        top: 14,
                        left: 16,
                        right: 16,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.white12),
                              ),
                              child: Text(
                                'PACE: ${coach.currentWpm.toInt()} WPM',
                                style: const TextStyle(
                                  color: AppColors.secondary,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.white12),
                              ),
                              child: Text(
                                'CLARITY: ${coach.clarityScore.toInt()}%',
                                style: const TextStyle(
                                  color: AppColors.success,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Action Controls (Start / Pause / Resume / Stop)
              if (!coach.isSessionActive) ...[
                CustomButton(
                  text: 'Start Live Coaching',
                  icon: Icons.play_arrow_rounded,
                  onPressed: () => coach.startSession(),
                ),
              ] else ...[
                Row(
                  children: [
                    Expanded(
                      child: CustomButton(
                        text: coach.isPaused ? 'Resume' : 'Pause',
                        icon: coach.isPaused ? Icons.play_arrow_rounded : Icons.pause_rounded,
                        isSecondary: true,
                        onPressed: () {
                          if (coach.isPaused) {
                            coach.resumeSession();
                          } else {
                            coach.pauseSession();
                          }
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Container(
                        height: 50,
                        decoration: BoxDecoration(
                          color: AppColors.error.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.error.withOpacity(0.5)),
                        ),
                        child: TextButton.icon(
                          onPressed: () => coach.stopSession(),
                          icon: const Icon(Icons.stop_rounded, color: AppColors.error),
                          label: const Text(
                            'End Session',
                            style: TextStyle(
                              color: AppColors.error,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 24),

              // Live Real-Time AI Prompt Cards
              Row(
                children: const [
                  Icon(Icons.auto_awesome_rounded, color: AppColors.primaryLight, size: 18),
                  SizedBox(width: 6),
                  Text(
                    'Real-Time Coach Suggestions',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              ...coach.liveSuggestions.map((suggestion) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 10.0),
                  child: GlassCard(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    borderColor: AppColors.primaryLight.withOpacity(0.2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          margin: const EdgeInsets.only(top: 2),
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: AppColors.primaryLight,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            suggestion,
                            style: const TextStyle(
                              color: AppColors.textPrimary,
                              fontSize: 13,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ],
          ),
        ),
      ),
    );
  }
}
