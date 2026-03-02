"""End-to-end pipeline — orchestrates all steps from topic to final PPTX."""

import os
import logging
from typing import Callable, Optional

from src.config import get_llm
from src.planner import plan_presentation
from src.slot_fetcher import load_design_system, fetch_slots
from src.orchestrator import orchestrate
from src.worker import build_graph
from src.ppt_maker import create_empty_ppt
from src.image_handler import extract_image_requests, process_image_requests
from src.content_inserter import insert_content_into_ppt

logger = logging.getLogger(__name__)

# Path to design system JSON (relative to project root)
DESIGN_SYSTEM_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "finalfinalppt.json")


def run_pipeline(
    topic: str,
    num_slides: int,
    audience_type: str = "intermediate",
    output_dir: str = "output",
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> str:
    """
    Run the full PPT generation pipeline.

    Parameters
    ----------
    topic : str
        Topic for the presentation.
    num_slides : int
        Number of slides (5–20).
    audience_type : str
        One of 'beginner', 'intermediate', 'advanced'.
    output_dir : str
        Directory to save output files.
    on_progress : callable, optional
        Callback(progress_fraction, status_message) for UI updates.

    Returns
    -------
    str
        Path to the final PPTX file.
    """
    os.makedirs(output_dir, exist_ok=True)

    def _progress(frac: float, msg: str):
        if on_progress:
            on_progress(frac, msg)
        logger.info(f"[{frac:.0%}] {msg}")

    # ── Step 1: Load design system ──
    _progress(0.05, "Loading design system...")
    design_system = load_design_system(DESIGN_SYSTEM_PATH)

    # ── Step 2: Plan presentation ──
    _progress(0.10, "Planning slides with AI...")
    llm = get_llm()
    plan = plan_presentation(llm, topic, num_slides, audience_type)
    logger.info(f"Theme: {plan.theme}, Slides: {len(plan.slides)}")

    # ── Step 3: Fetch slots ──
    _progress(0.20, "Resolving layout slots...")
    slot_output = fetch_slots(plan.slides, design_system)

    # ── Step 4: Orchestrate ──
    _progress(0.25, "Orchestrating slide data...")
    orchestrator_output = orchestrate(plan.slides, slot_output)

    # Prepare slides_with_slots dict for LangGraph
    slides_with_slots = [
        {
            "slide_id": slide.slide_id,
            "premise": slide.premise,
            "slots": [
                {"slot_key": s.slot_key, "type": s.type, "w": s.w, "h": s.h}
                for s in slide.slots
            ],
        }
        for slide in orchestrator_output
    ]

    # ── Step 5: Create empty PPTX ──
    _progress(0.30, "Creating empty presentation template...")
    empty_ppt_path = os.path.join(output_dir, "empty_template.pptx")
    create_empty_ppt(plan, design_system, empty_ppt_path)

    # ── Step 6: Generate content (parallel workers) ──
    _progress(0.35, "Generating slide content with AI (this takes a moment)...")
    app = build_graph()
    result = app.invoke({
        "slides_with_slots": slides_with_slots,
        "completed_slides": [],
    })
    completed_slides = result["completed_slides"]

    # ── Step 7: Extract & download images ──
    _progress(0.70, "Downloading images from Unsplash...")
    image_requests = extract_image_requests(orchestrator_output, completed_slides)
    downloaded_images = process_image_requests(image_requests)

    # ── Step 8: Insert content into PPTX ──
    _progress(0.85, "Inserting content into presentation...")
    final_path = os.path.join(output_dir, "final_presentation.pptx")
    insert_content_into_ppt(
        ppt_path=empty_ppt_path,
        completed_slides=completed_slides,
        downloaded_images=downloaded_images,
        image_requests=image_requests,
        theme_name=plan.theme,
        design_system=design_system,
        output_path=final_path,
    )

    _progress(1.0, "Done! Presentation ready.")
    return final_path
