"""
Pacing & Transitions Analysis Module

Analyzes the content pacing across slides:
- Word count distribution per slide (dense vs. sparse)
- Pacing variance (smooth vs. erratic density changes)
- Estimated presentation duration
- Transition smoothness (topic continuity signals)
"""

import logging
import math
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Approximate speaking rate for pacing estimation
_SPEAKING_WPM = 130


@dataclass
class PacingAnalysis:
    """Pacing and transition metrics for the full presentation."""
    avg_words_per_slide: float
    word_count_variance: float          # standard deviation of per-slide word counts
    dense_slides: list[int] = field(default_factory=list)   # slide numbers > avg + 1 std
    sparse_slides: list[int] = field(default_factory=list)  # slide numbers < avg - 1 std
    estimated_presentation_minutes: float = 0.0
    transition_smoothness_score: int = 50   # 0-100 (100 = very smooth density flow)
    pacing_score: int = 50                  # 0-100 overall pacing quality


def analyze_pacing_and_transitions(slides: list[dict]) -> PacingAnalysis:
    """Compute pacing quality metrics from slide data.

    Args:
        slides: List of slide dicts — must contain 'textboxes' key.

    Returns:
        PacingAnalysis dataclass instance.
    """
    if not slides:
        return PacingAnalysis(
            avg_words_per_slide=0.0,
            word_count_variance=0.0,
        )

    # Collect per-slide word counts
    word_counts: list[int] = []
    for slide in slides:
        slide_text = " ".join(
            (p.get("text", "") if isinstance(p, dict) else str(p))
            for tb in slide.get("textboxes", [])
            for p in tb.get("paragraphs", [])
        )
        word_counts.append(len(slide_text.split()))

    total_words = sum(word_counts)
    slide_count = len(slides)
    avg_words = total_words / slide_count

    # Standard deviation
    variance_sum = sum((wc - avg_words) ** 2 for wc in word_counts)
    std_dev = math.sqrt(variance_sum / slide_count)

    # Identify outlier slides
    dense: list[int] = []
    sparse: list[int] = []
    for slide, wc in zip(slides, word_counts):
        sn = slide.get("slide_number", 0)
        if wc > avg_words + std_dev:
            dense.append(sn)
        elif wc < avg_words - std_dev and wc < 15:
            sparse.append(sn)

    # Estimated duration
    est_minutes = round(total_words / _SPEAKING_WPM, 1)

    # Transition smoothness — measures how abrupt changes are between consecutive slides
    abrupt_transitions = 0
    for i in range(1, len(word_counts)):
        prev, curr = word_counts[i - 1], word_counts[i]
        if prev > 0 and abs(curr - prev) / max(prev, 1) > 1.0:
            abrupt_transitions += 1

    smoothness = 100 - min(60, abrupt_transitions * 10)
    smoothness = max(0, smoothness)

    # Overall pacing score
    pacing_score = 100
    # Penalise high variance (erratic pacing)
    if std_dev > avg_words * 0.6:
        pacing_score -= 20
    # Penalise too many dense slides (audience overload)
    if len(dense) > slide_count * 0.4:
        pacing_score -= 20
    # Penalise too many sparse slides (thin content)
    if len(sparse) > slide_count * 0.3:
        pacing_score -= 15
    pacing_score = max(0, min(100, pacing_score))

    return PacingAnalysis(
        avg_words_per_slide=round(avg_words, 1),
        word_count_variance=round(std_dev, 1),
        dense_slides=dense,
        sparse_slides=sparse,
        estimated_presentation_minutes=est_minutes,
        transition_smoothness_score=smoothness,
        pacing_score=pacing_score,
    )
