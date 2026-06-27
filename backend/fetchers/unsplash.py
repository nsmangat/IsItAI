import uuid

import requests

import config
from rate_limiter import RateLimiter
from .base import FetchedImage, ImageFetcher

"""
Get real photographs from the Unsplash API
"""

class UnsplashFetcher(ImageFetcher):

    API_URL = "https://api.unsplash.com/photos/random"

    # Topics that produce realistic, everyday photos — good counterparts
    # to the AI prompts so users can't guess based on subject matter alone.
    TOPICS = [
        "people", "nature", "architecture", "food-drink",
        "street-photography", "animals", "travel", "natural-disaster", 
        "car-accident", "art",
    ]

    def __init__(self, rate_limiter: RateLimiter | None = None):

        if rate_limiter is None:
            rate_limiter = RateLimiter(config.UNSPLASH_MIN_INTERVAL)

        super().__init__(rate_limiter)
        self._topic_index = 0

    def _next_topic(self) -> str:
        topic = self.TOPICS[self._topic_index % len(self.TOPICS)]
        self._topic_index += 1
        return topic

    def fetch_one(self) -> FetchedImage | None:

        if not config.UNSPLASH_ACCESS_KEY:
            raise RuntimeError(
                "UNSPLASH_ACCESS_KEY not set. "
                "Get a free key at https://unsplash.com/developers "
                "and add it to .env"
            )

        topic = self._next_topic()

        print(f"[Unsplash] Fetching real photo (topic: {topic})")
        self.rate_limiter.calculate_wait_time_between_requests()

        try:
            # First get random photo metadata from the API based on the photo topic
            response = requests.get(
                self.API_URL,
                params={
                    "client_id": config.UNSPLASH_ACCESS_KEY,
                    "query": topic,
                    "orientation": "squarish",                    
                },
                timeout=30,
            )
            
            response.raise_for_status()
            data = response.json()

            # Then download the actual image (regular size ≈ 1080px wide)
            # and extract info to comply with Unsplash's guidelines
            image_url = data["urls"]["regular"]
            photographer = data["user"]["name"]
            unsplash_link = data["links"]["html"]
            download_location = data["links"]["download_location"]

            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()

            # Unsplash guidelines require triggering this endpoint to track downloads
            # Might have to make this async later depending on number of requests being sent, 
            # but should be fine for now 
            requests.get(
                download_location, 
                params={
                    "client_id": config.UNSPLASH_ACCESS_KEY}, 
                    timeout=5
                    )
            
        except requests.exceptions.RequestException as e:
            print(f"FAILED: {e}")
            return None

        # Saving actual image 
        filename = f"real_{uuid.uuid4().hex[:10]}.jpg"
        filepath = config.IMAGE_SAVE_DIR / filename

        with open(filepath, "wb") as f:
            f.write(img_response.content)

        # Unsplash TOS requires attribution
        attribution = f"Photo by {photographer} on Unsplash ({unsplash_link})"
        print(f"Saved image successfully: {filepath.name}, ({len(img_response.content) / 1024:.0f} KB)")
        print(f"Credit: {attribution}")

        return FetchedImage(
            filepath=filepath,
            source="unsplash",
            is_ai=False,
            source_url=unsplash_link,
            attribution=attribution,
        )
