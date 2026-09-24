"""
Delivery Impact Analysis Module

Analyzes how the written text supports strong spoken delivery:
- Action verb density (energetic vs. passive language)
- Passive voice prevalence
- Audience engagement signals (rhetorical questions, direct address)
- Technical jargon density
- Overall delivery impact score
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Word lists ─────────────────────────────────────────────────────────────
_ACTION_VERBS = {
    "demonstrate", "implement", "develop", "analyze", "improve", "create",
    "build", "design", "test", "evaluate", "measure", "optimize", "deploy",
    "integrate", "achieve", "solve", "address", "deliver", "increase",
    "reduce", "identify", "compare", "validate", "propose", "present",
    "show", "highlight", "explain", "describe", "outline", "summarize",
}

_PASSIVE_PATTERNS = [
    r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
    r'\b(has|have|had)\s+been\s+\w+ed\b',
]

_ENGAGEMENT_PATTERNS = [
    r'\?',                                  # questions
    r'\byou\b',                             # direct address
    r'\bwe\b',                              # inclusive language
    r'\blet\s+us\b',
    r'\bconsider\b',
    r'\bimagine\b',
    r'\bthink\s+about\b',
]


@dataclass
class DeliveryImpact:
    """Delivery impact metrics derived from presentation text."""
    action_verb_count: int
    action_verb_density: float          # per 100 words
    passive_voice_instances: int
    passive_voice_percentage: float
    audience_engagement_signals: int
    jargon_word_count: int
    clarity_score: int                  # 0-100
    delivery_score: int                 # 0-100
    strengths: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)


def analyze_delivery_impact(text: str) -> DeliveryImpact:
    """Analyze delivery impact metrics from presentation text.

    Args:
        text: Plain text extracted from the presentation document.

    Returns:
        DeliveryImpact dataclass instance.
    """
    if not text or not text.strip():
        return DeliveryImpact(
            action_verb_count=0,
            action_verb_density=0.0,
            passive_voice_instances=0,
            passive_voice_percentage=0.0,
            audience_engagement_signals=0,
            jargon_word_count=0,
            clarity_score=50,
            delivery_score=50,
        )

    words = re.findall(r'\b\w+\b', text.lower())
    word_count = max(len(words), 1)
    word_set = set(words)
    text_lower = text.lower()

    # ── Action verbs ───────────────────────────────────────────────────────
    action_hits = [v for v in _ACTION_VERBS if v in word_set]
    action_count = len(action_hits)
    action_density = round(action_count / word_count * 100, 2)

    # ── Passive voice ──────────────────────────────────────────────────────
    passive_count = sum(
        len(re.findall(pattern, text_lower)) for pattern in _PASSIVE_PATTERNS
    )
    passive_pct = round(passive_count / word_count * 100, 2)

    # ── Audience engagement ────────────────────────────────────────────────
    engagement = sum(
        len(re.findall(pat, text_lower)) for pat in _ENGAGEMENT_PATTERNS
    )

    # ── Jargon density (heuristic: words > 10 chars not in common vocabulary) ──
    jargon_words = [w for w in words if len(w) > 10]
    jargon_count = len(jargon_words)

    # ── Scores ─────────────────────────────────────────────────────────────
    clarity_score = 80
    if passive_pct > 15:
        clarity_score -= 20
    elif passive_pct > 8:
        clarity_score -= 10
    if jargon_count / word_count > 0.08:
        clarity_score -= 10
    clarity_score = max(0, min(100, clarity_score))

    delivery_score = 60
    delivery_score += min(25, int(action_density * 3))
    delivery_score += min(15, engagement)
    delivery_score -= min(25, int(passive_pct * 1.5))
    delivery_score = max(0, min(100, delivery_score))

    # ── Narrative feedback ─────────────────────────────────────────────────
    strengths: list[str] = []
    improvements: list[str] = []

    if action_density >= 2.0:
        strengths.append("Strong use of action verbs drives clear messaging.")
    else:
        improvements.append("Increase action verb usage (e.g., 'demonstrate', 'implement') for more energetic delivery.")

    if engagement >= 3:
        strengths.append("Good audience engagement through questions and direct address.")
    else:
        improvements.append("Add rhetorical questions or 'you'/'we' language to engage the audience.")

    if passive_pct < 5:
        strengths.append("Minimal passive voice — text reads actively and clearly.")
    elif passive_pct > 12:
        improvements.append(f"High passive voice ({passive_pct:.1f}%) — rewrite key sentences in active voice.")

    return DeliveryImpact(
        action_verb_count=action_count,
        action_verb_density=action_density,
        passive_voice_instances=passive_count,
        passive_voice_percentage=passive_pct,
        audience_engagement_signals=engagement,
        jargon_word_count=jargon_count,
        clarity_score=clarity_score,
        delivery_score=delivery_score,
        strengths=strengths[:3],
        improvements=improvements[:3],
    )
