"""Pydantic models for the PPT automation pipeline."""

import operator
from typing import Annotated, Any, Dict, List, Literal, TypedDict

from pydantic import BaseModel, Field

# ──────────────────────────────────────────────
# Theme & Layout enums
# ──────────────────────────────────────────────

ThemeOptions = Literal[
    "executive_dark",
    "swiss_minimalist",
    "tech_brutalist",
    "nordic_serene",
    "cyber_punk",
    "editorial_vogue",
    "industrial_loft",
    "startup_bold",
    "classic_heritage",
    "the_ghost",
]

LayoutOptions = Literal[
    # Title & Hero
    "title_hero_centered",
    "title_split_accent_left",
    "title_minimal_right_aligned",
    "title_frame_centered_box",
    "title_asymmetric_impact_diagonal",
    # Content & Narrative
    "content_narrative_single_column",
    "content_bullets_with_sidebar_title",
    "content_bullets_header_bar",
    "content_narrative_right_offset",
    "content_bullets_centered_narrow",
    "content_text_over_ghost_title",
    # Section Breaks
    "section_highlight_giant_number",
    "section_minimal_centered",
    "section_bottom_anchor_line",
    "section_dark_background_reveal",
    "section_clean_geometric_center",
    "section_horizon_divider_clean",
    "section_block_anchor_footer",
    "section_editorial_corner_accent",
    # Two-Column & Comparison
    "two_column_asymmetric_golden_ratio",
    "two_column_split_cards",
    "two_column_mirrored_paragraphs",
    "two_column_list_with_callout",
    "two_column_staggered_text",
    "two_column_centered_divider",
    "two_column_clean_bullets",
    "compare_three_column_grid",
    "compare_four_quadrant_grid",
    "compare_t_shape_columns",
    "compare_split_high_contrast",
    "compare_two_floating_boxes",
    # Impact & Image
    "impact_quote_master",
    "impact_top_banner_minimal",
    "impact_centered_huge_text",
    "image_full_with_bottom_caption",
    "image_sidebar_with_left_text",
    "image_centered_inset_with_caption",
    "image_storyteller_text_left",
    "image_technical_bullets_right",
    "image_full_bleed_background",
    "image_gallery_framed_portrait",
    "image_panorama_with_dual_captions",
    "image_text_overlap_depth",
    "image_split_dual_overlay",
    "gallery_dual_image_feature",
    "gallery_triple_image_portfolio",
    "editorial_sidebar_image_left",
]

SlotType = Literal["text", "paragraph", "bullets", "image"]

# ──────────────────────────────────────────────
# Planner models
# ──────────────────────────────────────────────


class Slide(BaseModel):
    slide_id: int
    slide_premise: str = Field(
        description="A detailed description of what this slide will cover and its visual intent."
    )
    layout: LayoutOptions = Field(
        description="The layout that best supports the visual intent described in the premise."
    )


class PresentationPlan(BaseModel):
    theme: ThemeOptions = Field(
        description="The aesthetic theme that matches the overall topic."
    )
    slides: List[Slide]


# ──────────────────────────────────────────────
# Slot models
# ──────────────────────────────────────────────


class SlotBlueprint(BaseModel):
    slot_key: str
    type: SlotType
    w: float
    h: float


class SlideWithSlots(BaseModel):
    slide_id: int
    premise: str
    slots: List[SlotBlueprint]


class OrchestratedSlide(BaseModel):
    slide_id: int
    premise: str
    slots: List[SlotBlueprint]


# ──────────────────────────────────────────────
# LangGraph state models
# ──────────────────────────────────────────────


class GraphState(TypedDict):
    slides_with_slots: List[Dict[str, Any]]
    completed_slides: Annotated[List[Dict[str, Any]], operator.add]


class WorkerState(TypedDict):
    slide_id: int
    premise: str
    slots: List[Dict[str, Any]]
