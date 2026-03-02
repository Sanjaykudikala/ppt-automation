"""Slot fetcher — resolves layout slot blueprints from the design system."""

import json
from typing import List

from src.models import Slide, SlotBlueprint, SlideWithSlots


def load_design_system(json_path: str) -> dict:
    """Load the design system JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_slots(slides: List[Slide], design_system: dict) -> List[SlideWithSlots]:
    """
    Resolve slot blueprints for each slide based on its layout.

    Parameters
    ----------
    slides : list[Slide]
        Slides from the planner output.
    design_system : dict
        The loaded design system JSON.

    Returns
    -------
    list[SlideWithSlots]
        Slides with resolved slot blueprints.
    """
    resolved_slides = []
    layouts = design_system["layouts"]

    for slide in slides:
        layout_name = slide.layout

        if layout_name not in layouts:
            raise ValueError(f"Layout '{layout_name}' not found in design system")

        layout_slots = layouts[layout_name]["slots"]
        slot_blueprints = []

        for slot_key, slot_def in layout_slots.items():
            slot_type = slot_def.get("type")

            # Skip shape slots (decorative only)
            if slot_type == "shape":
                continue

            slot_blueprints.append(
                SlotBlueprint(
                    slot_key=slot_key,
                    type=slot_type,
                    w=float(slot_def["w"]),
                    h=float(slot_def["h"]),
                )
            )

        resolved_slides.append(
            SlideWithSlots(
                slide_id=slide.slide_id,
                premise=slide.slide_premise,
                slots=slot_blueprints,
            )
        )

    return resolved_slides
