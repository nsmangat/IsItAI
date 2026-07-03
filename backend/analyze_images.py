"""
Image analysis pipeline

Runs Gemini Vision over already-fetched AI images to detect AI-generation tells,
saving the structured result as a JSON file next to each image.


Test commands:

    python analyze_images.py                 # analyze any images without a result file yet
    python analyze_images.py --limit 2       # analyze at most 2 images
    python analyze_images.py --force         # re-analyze everything, even if corresponding result files are present
    python analyze_images.py --no-rate-limit
"""

import argparse
import json
from dataclasses import asdict

import config
from analyzers import GeminiAnalyzer
from analyzers.base import Analysis
from fetchers.base import FetchedImage


def _get_images() -> list[FetchedImage]:

    return [
        FetchedImage(filepath=filepath, source="pollinations", is_ai=True, source_url="", attribution="")
        for filepath in sorted(config.AI_POLLINATIONS_DIR.glob("*.jpg"))
    ]


def _result_path(image: FetchedImage):
    return image.filepath.with_suffix(".json")

# Convert the analysis data into a JSON file 
def _save_analysis(analysis: Analysis) -> None:

    data = {
        "is_ai": analysis.image.is_ai,
        "confidence": analysis.confidence,
        "signals": [asdict(s) for s in analysis.signals],
    }

    with open(_result_path(analysis.image), "w") as f:
        json.dump(data, f, indent=2)


def analyze_images(force: bool = False, rate_limit: bool = True, limit: int | None = None) -> list[Analysis]:

    if not rate_limit:
        print("WARNING: Rate limiting is disabled!\n")

    images = _get_images()

    # Get the images that still need to be analyzed i.e. don't have associated JSON analysis file 
    if not force:
        images = [img for img in images if not _result_path(img).exists()]

    if limit is not None:
        images = images[:limit]

    if not images:
        print("No images to analyze.")
        return []

    analyzer = GeminiAnalyzer(rate_limit=rate_limit)

    results: list[Analysis] = []

    for i, image in enumerate(images):
        print(f"Image {i + 1}/{len(images)}: {image.filepath.name}")
        analysis = analyzer.analyze(image)
        if analysis:
            _save_analysis(analysis)
            results.append(analysis)
        print()

    print("-" * 50)
    print(f"Finished. Analyzed {len(results)}/{len(images)} image(s).")

    for analysis in results:
        print(f"{analysis.image.filepath.name} — confidence {analysis.confidence:.2f}, {len(analysis.signals)} signal(s)")

    return results


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Analyze fetched images with Gemini Vision for signs of AI-generation")
    parser.add_argument("--force", action="store_true", help="Re-analyze images that already have a result file")
    parser.add_argument("--no-rate-limit", action="store_true", help="Disable rate limiting")
    parser.add_argument("--limit", type=int, default=None, help="Analyze at most this many images")
    args = parser.parse_args()

    analyze_images(force=args.force, rate_limit=not args.no_rate_limit, limit=args.limit)
