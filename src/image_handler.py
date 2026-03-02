"""Image handler — extracts image requests and downloads from Unsplash."""

import os
import re
from typing import List, Dict

import requests
from dotenv import load_dotenv

from src.json_parser import parse_llm_json
from src.models import OrchestratedSlide

load_dotenv()


def _make_safe_filename(text: str) -> str:
    """Convert a description into a safe filename."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    # Truncate to avoid overly long filenames
    return text[:80].strip("_") + ".jpg"


def extract_image_requests(
    orchestrator_output: List[OrchestratedSlide],
    completed_slides: List[Dict],
) -> List[Dict]:
    """
    Extract image slot requests from completed slides.

    Parameters
    ----------
    orchestrator_output : list[OrchestratedSlide]
        Orchestrated slides with slot info.
    completed_slides : list[dict]
        Worker output with generated content.

    Returns
    -------
    list[dict]
        Image requests with slide_id, slot_key, description, dimensions, orientation.
    """
    image_requests = []
    content_map = {}

    # Parse worker output
    for slide in completed_slides:
        raw_content = slide["content"]
        if isinstance(raw_content, str):
            slide_content = parse_llm_json(raw_content)
        else:
            slide_content = raw_content
        content_map[slide["slide_id"]] = slide_content

    # Walk orchestrator output
    for slide in orchestrator_output:
        slide_id = slide.slide_id
        if slide_id not in content_map:
            continue

        slide_content = content_map[slide_id]

        for slot in slide.slots:
            if slot.type != "image":
                continue

            slot_key = slot.slot_key
            if slot_key not in slide_content:
                continue

            w, h = slot.w, slot.h
            if h == 0:
                orientation = "landscape"
            else:
                ratio = w / h
                if ratio >= 1.3:
                    orientation = "landscape"
                elif ratio <= 0.8:
                    orientation = "portrait"
                else:
                    orientation = "squarish"

            image_requests.append({
                "slide_id": slide_id,
                "slot_key": slot_key,
                "description": slide_content[slot_key],
                "w": w,
                "h": h,
                "orientation": orientation,
            })

    return image_requests


def download_image_from_unsplash(
    description: str,
    orientation: str,
    save_dir: str = "images",
) -> str:
    """
    Download an image from Unsplash based on a description.

    Parameters
    ----------
    description : str
        Search query for the image.
    orientation : str
        One of 'landscape', 'portrait', 'squarish'.
    save_dir : str
        Directory to save downloaded images.

    Returns
    -------
    str
        Path to the downloaded image file.
    """
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise ValueError("UNSPLASH_ACCESS_KEY not found in environment")

    os.makedirs(save_dir, exist_ok=True)

    filename = _make_safe_filename(description)
    file_path = os.path.join(save_dir, filename)

    # Avoid re-downloading
    if os.path.exists(file_path):
        return file_path

    search_url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {
        "query": description,
        "orientation": orientation,
        "per_page": 1,
    }

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        raise ValueError(f"No image found for: {description}")

    image_url = results[0]["urls"]["regular"]
    img_response = requests.get(image_url)
    img_response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(img_response.content)

    return file_path


def process_image_requests(image_requests: List[Dict]) -> List[Dict]:
    """
    Download all requested images.

    Parameters
    ----------
    image_requests : list[dict]
        Image requests from extract_image_requests().

    Returns
    -------
    list[dict]
        Downloaded image info with file paths.
    """
    downloaded_images = []

    for img in image_requests:
        try:
            path = download_image_from_unsplash(
                description=img["description"],
                orientation=img["orientation"],
            )
            downloaded_images.append({
                "slide_id": img["slide_id"],
                "slot_key": img["slot_key"],
                "image_path": path,
                "w": img["w"],
                "h": img["h"],
                "orientation": img["orientation"],
            })
        except Exception as e:
            print(f"Warning: Failed to download image for slide {img['slide_id']}: {e}")

    return downloaded_images
