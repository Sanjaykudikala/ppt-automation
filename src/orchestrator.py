"""Orchestrator node — merges planner output with slot data."""

from typing import List

from src.models import OrchestratedSlide, Slide, SlideWithSlots


def orchestrate(planner_slides: List[Slide], slot_slides: List[SlideWithSlots]) -> List[OrchestratedSlide]:
    """
    Merge planner slides with their resolved slot blueprints.

    Parameters
    ----------
    planner_slides : list[Slide]
        Raw slides from the planner.
    slot_slides : list[SlideWithSlots]
        Slides with resolved slots from the slot fetcher.

    Returns
    -------
    list[OrchestratedSlide]
        Fully orchestrated slides ready for content generation.
    """
    slot_map = {slide.slide_id: slide.slots for slide in slot_slides}

    orchestrated = []
    for slide in planner_slides:
        if slide.slide_id not in slot_map:
            raise ValueError(f"Missing slots for slide_id {slide.slide_id}")

        orchestrated.append(
            OrchestratedSlide(
                slide_id=slide.slide_id,
                premise=slide.slide_premise,
                slots=slot_map[slide.slide_id],
            )
        )

    return orchestrated
