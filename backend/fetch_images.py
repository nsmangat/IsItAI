"""
Image fetching pipeline

Fetches a batch of AI-generated and real images, saving them locally for now
Test commands for the image fetchers:

    python fetch_images.py --ai 1 --real 1               # 1 of each
    python fetch_images.py --ai 5 --real 5               # 5 of each
    python fetch_images.py --ai 3                        # 3 AI only
    python fetch_images.py --real 2                      # 2 real only
    python fetch_images.py --ai 3 --no-rate-limit        # skip rate limit delays
"""

import argparse

from fetchers import PollinationsFetcher, UnsplashFetcher
from fetchers.base import FetchedImage


def fetch_images(ai_count: int = 0, real_count: int = 0, rate_limit: bool = True) -> list[FetchedImage]:

    if not rate_limit:
        print("WARNING: Rate limiting is disabled!\n")

    fetched_images: list[FetchedImage] = []

    if ai_count > 0:

        ai_fetcher = PollinationsFetcher(rate_limit=rate_limit)

        print(f"Fetching {ai_count} AI-generated image(s)...")

        for i in range(ai_count):
            print(f"--- AI Image {i + 1}/{ai_count} ---")
            result = ai_fetcher.fetch_one()
            if result:
                fetched_images.append(result)
            print()

    if real_count > 0:
        print("-" * 50)
        unsplash_fetcher = UnsplashFetcher(rate_limit=rate_limit)

        print(f"Fetching {real_count} real photo(s)...")

        for i in range(real_count):
            print(f"--- Real Image {i + 1}/{real_count} ---")
            result = unsplash_fetcher.fetch_one()
            if result:
                fetched_images.append(result)
            print()

    print("-" * 50)
    print(f"Finished. Fetched {len(fetched_images)}/{ai_count + real_count} image(s).")

    for img in fetched_images:
        label = "AI" if img.is_ai else "REAL"
        print(f"[{label}] {img.filepath.name} — {img.attribution[:60]}")

    return fetched_images


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Fetch AI and real images, currently from Pollinations.AI and Unsplash")
    parser.add_argument("--ai", type=int, default=0, help="Number of AI images to fetch")
    parser.add_argument("--real", type=int, default=0, help="Number of real images to fetch")
    parser.add_argument("--no-rate-limit", action="store_true", help="Disable rate limiting (use with caution)")
    args = parser.parse_args()

    # if no-rate-limit arg isn't passed, it'll be False, so have to do not to make it true
    # else if it is passed, it becomes true as arg, so in param need rate-limit to be false so do not True == False
    fetch_images(ai_count=args.ai, real_count=args.real, rate_limit=not args.no_rate_limit)
