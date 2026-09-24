"""
Narrative Structure Analysis Module

Analyzes the narrative flow and story arc of a presentation:
- Presence of introduction, body, and conclusion sections
- Logical section balance (intro not too long, conclusion present)
- Story arc score (problem → solution → outcome)
- Logical flow score
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Title keyword signals for section detection
_INTRO_SIGNALS = re.compile(
    r'\b(introduction|intro|background|overview|agenda|outline|context|'
    r'motivation|problem|objective|aim|purpose)\b',
    re.IGNORECASE,
)
_CONCLUSION_SIGNALS = re.compile(
    r'\b(conclusion|summary|takeaway|key\s+point|wrap.up|recap|closing|'
    r'thank\s+you|future\s+work|next\s+step|recommendation|result|finding)\b',
    re.IGNORECASE,
)
_PROBLEM_SIGNALS = re.compile(
    r'\b(problem|challenge|issue|gap|pain\s+point|limitation|difficulty)\b',
    re.IGNORECASE,
)
_SOLUTION_SIGNALS = re.compile(
    r'\b(solution|approach|method|framework|system|architecture|design|'
    r'implementation|methodology|proposal)\b',
    re.IGNORECASE,
)
_OUTCOME_SIGNALS = re.compile(
    r'\b(result|outcome|finding|evaluation|experiment|performance|accuracy|'
    r'impact|improvement|achievement)\b',
    re.IGNORECASE,
)


@dataclass
class NarrativeStructure:
    """Narrative structure metrics for the presentation."""
    has_introduction: bool
    has_body: bool
    has_conclusion: bool
    has_problem_statement: bool
    has_solution: bool
    has_outcome: bool
    intro_slide_count: int
    body_slide_count: int
    conclusion_slide_count: int
    story_arc_score: int            # 0-100 (problem → solution → outcome)
    logical_flow_score: int         # 0-100 (intro → body → conclusion order)
    section_balance_score: int      # 0-100 (proportional section lengths)
    narrative_score: int            # 0-100 overall
    missing_sections: list[str] = field(default_factory=list)


def analyze_narrative_structure(slides: list[dict]) -> NarrativeStructure:
    """Analyze narrative structure of a presentation from slide data.

    Args:
        slides: List of slide dicts — must contain 'title' and 'textboxes' keys.

    Returns:
        NarrativeStructure dataclass instance.
    """
    if not slides:
        return NarrativeStructure(
            has_introduction=False,
            has_body=False,
            has_conclusion=False,
            has_problem_statement=False,
            has_solution=False,
            has_outcome=False,
            intro_slide_count=0,
            body_slide_count=0,
            conclusion_slide_count=0,
            story_arc_score=0,
            logical_flow_score=0,
            section_balance_score=0,
            narrative_score=0,
        )

    total = len(slides)
    intro_indices: list[int] = []
    conclusion_indices: list[int] = []
    body_indices: list[int] = []
    has_problem = False
    has_solution = False
    has_outcome = False

    for idx, slide in enumerate(slides):
        title = slide.get("title", "")
        slide_text = title + " " + " ".join(
            (p.get("text", "") if isinstance(p, dict) else str(p))
            for tb in slide.get("textboxes", [])
            for p in tb.get("paragraphs", [])
        )

        is_intro = bool(_INTRO_SIGNALS.search(slide_text))
        is_conclusion = bool(_CONCLUSION_SIGNALS.search(slide_text))

        if _PROBLEM_SIGNALS.search(slide_text):
            has_problem = True
        if _SOLUTION_SIGNALS.search(slide_text):
            has_solution = True
        if _OUTCOME_SIGNALS.search(slide_text):
            has_outcome = True

        if is_intro and idx < total * 0.4:
            intro_indices.append(idx)
        elif is_conclusion and idx >= total * 0.6:
            conclusion_indices.append(idx)
        else:
            body_indices.append(idx)

    has_introduction = len(intro_indices) > 0
    has_conclusion = len(conclusion_indices) > 0
    has_body = len(body_indices) > 0

    # ── Story arc score ────────────────────────────────────────────────────
    arc_score = 0
    if has_problem:
        arc_score += 34
    if has_solution:
        arc_score += 33
    if has_outcome:
        arc_score += 33

    # ── Logical flow score ─────────────────────────────────────────────────
    flow_score = 50
    if has_introduction:
        flow_score += 20
    if has_conclusion:
        flow_score += 20
    if has_body:
        flow_score += 10
    flow_score = min(100, flow_score)

    # ── Section balance score ──────────────────────────────────────────────
    balance_score = 100
    intro_ratio = len(intro_indices) / total
    conc_ratio = len(conclusion_indices) / total
    body_ratio = len(body_indices) / total

    # Ideal: intro 10-30%, body 50-75%, conclusion 10-25%
    if intro_ratio > 0.35:
        balance_score -= 15  # too much intro
    if conc_ratio > 0.30:
        balance_score -= 15  # too long conclusion
    if body_ratio < 0.4:
        balance_score -= 20  # insufficient body
    if not has_introduction:
        balance_score -= 15
    if not has_conclusion:
        balance_score -= 15
    balance_score = max(0, balance_score)

    # ── Overall narrative score ────────────────────────────────────────────
    narrative_score = round((arc_score * 0.4) + (flow_score * 0.35) + (balance_score * 0.25))
    narrative_score = max(0, min(100, narrative_score))

    # ── Missing sections ───────────────────────────────────────────────────
    missing: list[str] = []
    if not has_introduction:
        missing.append("Introduction / Background slide")
    if not has_conclusion:
        missing.append("Conclusion / Summary slide")
    if not has_problem:
        missing.append("Problem Statement")
    if not has_solution:
        missing.append("Methodology / Solution")
    if not has_outcome:
        missing.append("Results / Outcomes")

    return NarrativeStructure(
        has_introduction=has_introduction,
        has_body=has_body,
        has_conclusion=has_conclusion,
        has_problem_statement=has_problem,
        has_solution=has_solution,
        has_outcome=has_outcome,
        intro_slide_count=len(intro_indices),
        body_slide_count=len(body_indices),
        conclusion_slide_count=len(conclusion_indices),
        story_arc_score=arc_score,
        logical_flow_score=flow_score,
        section_balance_score=balance_score,
        narrative_score=narrative_score,
        missing_sections=missing,
    )
