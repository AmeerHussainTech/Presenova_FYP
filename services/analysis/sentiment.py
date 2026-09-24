"""
Sentiment & Tone Analysis Module

Analyzes the sentiment and tone of presentation text:
- Overall sentiment polarity (positive / neutral / negative)
- Formality / professionalism score
- Academic vs. casual tone classification
- Key positive and negative signal words
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Lightweight word lists (no external deps) ──────────────────────────────
_POSITIVE_SIGNALS = {
    "achieve", "improve", "enhance", "success", "effective", "efficient",
    "innovative", "solution", "benefit", "advantage", "opportunity",
    "significant", "excellent", "outstanding", "valuable", "robust",
    "reliable", "proven", "accurate", "comprehensive", "optimal",
}

_NEGATIVE_SIGNALS = {
    "fail", "problem", "issue", "challenge", "difficult", "complex",
    "poor", "lack", "limited", "inadequate", "inefficient", "error",
    "risk", "threat", "obstacle", "weakness", "concern", "deficiency",
}

_FORMAL_MARKERS = {
    "therefore", "furthermore", "however", "consequently", "subsequently",
    "moreover", "nevertheless", "hence", "thus", "accordingly",
    "in addition", "in conclusion", "in contrast", "as a result",
    "it is evident", "it can be observed", "this study", "this research",
}

_CASUAL_MARKERS = {
    "basically", "kind of", "sort of", "you know", "like", "stuff",
    "things", "gonna", "wanna", "pretty much", "a lot", "lots",
}


@dataclass
class SentimentAnalysis:
    """Sentiment and tone metrics for presentation text."""
    overall_sentiment: str            # "positive" | "neutral" | "negative"
    sentiment_confidence: float       # 0.0 – 1.0
    formality_score: int              # 0-100  (100 = very formal / academic)
    tone: str                         # "academic" | "professional" | "casual"
    positive_word_count: int
    negative_word_count: int
    key_positive_words: list[str] = field(default_factory=list)
    key_negative_words: list[str] = field(default_factory=list)
    readability_level: str = "intermediate"  # "simple" | "intermediate" | "advanced"


def analyze_sentiment_and_tone(text: str) -> SentimentAnalysis:
    """Analyze sentiment and tone of presentation text.

    Args:
        text: Plain text extracted from the presentation document.

    Returns:
        SentimentAnalysis dataclass instance.
    """
    if not text or not text.strip():
        return SentimentAnalysis(
            overall_sentiment="neutral",
            sentiment_confidence=0.5,
            formality_score=50,
            tone="professional",
            positive_word_count=0,
            negative_word_count=0,
        )

    words_raw = re.findall(r'\b\w+\b', text.lower())
    word_count = max(len(words_raw), 1)
    word_set = set(words_raw)

    # ── Sentiment ──────────────────────────────────────────────────────────
    pos_hits = [w for w in _POSITIVE_SIGNALS if w in word_set]
    neg_hits = [w for w in _NEGATIVE_SIGNALS if w in word_set]

    pos_score = len(pos_hits) / word_count * 100
    neg_score = len(neg_hits) / word_count * 100

    if pos_score > neg_score + 0.5:
        sentiment = "positive"
        confidence = round(min(0.95, 0.5 + (pos_score - neg_score) * 5), 2)
    elif neg_score > pos_score + 0.5:
        sentiment = "negative"
        confidence = round(min(0.95, 0.5 + (neg_score - pos_score) * 5), 2)
    else:
        sentiment = "neutral"
        confidence = round(0.5 + abs(pos_score - neg_score), 2)

    # ── Formality ──────────────────────────────────────────────────────────
    text_lower = text.lower()
    formal_count = sum(1 for m in _FORMAL_MARKERS if m in text_lower)
    casual_count = sum(1 for m in _CASUAL_MARKERS if m in text_lower)

    formality_score = 50
    formality_score += min(40, formal_count * 5)
    formality_score -= min(40, casual_count * 8)
    formality_score = max(0, min(100, formality_score))

    # Average word length as a proxy for vocabulary sophistication
    avg_word_len = sum(len(w) for w in words_raw) / word_count
    if avg_word_len > 6.5:
        formality_score = min(100, formality_score + 10)
    elif avg_word_len < 4.5:
        formality_score = max(0, formality_score - 10)

    # ── Tone classification ────────────────────────────────────────────────
    if formality_score >= 70:
        tone = "academic"
    elif formality_score >= 40:
        tone = "professional"
    else:
        tone = "casual"

    # ── Readability (simple heuristic — avg sentence length) ─────────────
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_len = word_count / max(len(sentences), 1)
    if avg_sentence_len < 12:
        readability = "simple"
    elif avg_sentence_len < 22:
        readability = "intermediate"
    else:
        readability = "advanced"

    return SentimentAnalysis(
        overall_sentiment=sentiment,
        sentiment_confidence=confidence,
        formality_score=formality_score,
        tone=tone,
        positive_word_count=len(pos_hits),
        negative_word_count=len(neg_hits),
        key_positive_words=pos_hits[:5],
        key_negative_words=neg_hits[:5],
        readability_level=readability,
    )
