"""
Visual Balance Analysis Module

Analyzes the visual composition and layout balance of a presentation:
- Text-to-visual element ratio per slide
- Overcrowded vs. sparse slide detection
- Charts, images, tables distribution
- Overall visual balance score
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class VisualBalance:
    """Visual balance metrics for the full presentation."""
    total_slides: int
    slides_with_images: int
    slides_with_charts: int
    slides_with_tables: int
    slides_text_only: int
    avg_elements_per_slide: float
    overcrowded_slides: list[int] = field(default_factory=list)   # slide numbers with >8 elements
    sparse_slides: list[int] = field(default_factory=list)        # slide numbers with 0 visuals & <20 words
    text_to_visual_ratio: float = 0.0   # 1.0 = all text; 0.0 = all visual
    balance_score: int = 0              # 0-100


def analyze_visual_balance(slides: list[dict]) -> VisualBalance:
    """Compute visual balance metrics from slide data.

    Args:
        slides: List of slide dicts from ppt_processor.extract_slides() or
                build_slides_from_text() — must contain 'textboxes', 'tables',
                'charts', 'images' (int or list) keys.

    Returns:
        VisualBalance dataclass instance.
    """
    if not slides:
        return VisualBalance(
            total_slides=0,
            slides_with_images=0,
            slides_with_charts=0,
            slides_with_tables=0,
            slides_text_only=0,
            avg_elements_per_slide=0.0,
            balance_score=50,
        )

    total = len(slides)
    with_images = 0
    with_charts = 0
    with_tables = 0
    text_only = 0
    overcrowded: list[int] = []
    sparse: list[int] = []
    total_elements = 0

    for slide in slides:
        slide_num = slide.get("slide_number", 0)

        # Normalize counts — accept both int fields and list-of-data fields
        img_count = _count_field(slide, "images", "images_data")
        chart_count = _count_field(slide, "charts", "charts_data")
        table_count = _count_field(slide, "tables", "tables_data")
        tb_count = len(slide.get("textboxes", []))

        if img_count > 0:
            with_images += 1
        if chart_count > 0:
            with_charts += 1
        if table_count > 0:
            with_tables += 1

        visual_elements = img_count + chart_count + table_count
        total_element_count = tb_count + visual_elements
        total_elements += total_element_count

        if visual_elements == 0:
            text_only += 1

        if total_element_count > 8:
            overcrowded.append(slide_num)

        # Sparse: no visuals AND very little text
        slide_text = " ".join(
            (p.get("text", "") if isinstance(p, dict) else str(p))
            for tb in slide.get("textboxes", [])
            for p in tb.get("paragraphs", [])
        )
        if visual_elements == 0 and len(slide_text.split()) < 20:
            sparse.append(slide_num)

    avg_elements = round(total_elements / total, 1)
    visual_slide_count = with_images + with_charts + with_tables
    text_to_visual = round(1.0 - (visual_slide_count / total), 2)

    # Score: ideal mix is 30-70% visual slides, low overcrowding/sparse
    score = 100
    if overcrowded:
        score -= min(30, len(overcrowded) * 5)
    if sparse:
        score -= min(20, len(sparse) * 4)
    if text_to_visual > 0.9:
        score -= 15  # almost no visuals
    elif text_to_visual < 0.1:
        score -= 10  # almost no text
    score = max(0, min(100, score))

    return VisualBalance(
        total_slides=total,
        slides_with_images=with_images,
        slides_with_charts=with_charts,
        slides_with_tables=with_tables,
        slides_text_only=text_only,
        avg_elements_per_slide=avg_elements,
        overcrowded_slides=overcrowded,
        sparse_slides=sparse,
        text_to_visual_ratio=text_to_visual,
        balance_score=score,
    )


def _count_field(slide: dict, int_key: str, list_key: str) -> int:
    """Return count from either an int field or a list field."""
    val = slide.get(int_key, 0)
    if isinstance(val, int):
        return val
    # Fallback: count list-based data field
    return len(slide.get(list_key, []))
