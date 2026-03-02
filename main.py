"""PPT Automation — CLI entry point."""

import sys
from src.pipeline import run_pipeline


def main():
    topic = input("Enter presentation topic: ").strip()
    num_slides = int(input("Number of slides (5-20): ").strip())
    audience = input("Audience type (beginner/intermediate/advanced): ").strip()

    print(f"\nGenerating {num_slides}-slide presentation about '{topic}'...")
    print(f"Audience level: {audience}\n")

    def on_progress(frac, msg):
        print(f"  [{frac:.0%}] {msg}")

    final_path = run_pipeline(
        topic=topic,
        num_slides=num_slides,
        audience_type=audience,
        on_progress=on_progress,
    )

    print(f"\n✅ Done! Presentation saved to: {final_path}")


if __name__ == "__main__":
    main()
