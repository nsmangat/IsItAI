import random
import uuid
from urllib.parse import quote

import requests

import config
from rate_limiter import RateLimiter
from .base import FetchedImage, ImageFetcher


"""
Fetches AI-generated images from Pollinations.ai
API returns raw image bytes for a given text prompt
"""
class PollinationsFetcher(ImageFetcher):

    BASE_URL = "https://image.pollinations.ai/prompt"

    def __init__(self, rate_limiter: RateLimiter | None = None):

        if rate_limiter is None:
            rate_limiter = RateLimiter(config.POLLINATIONS_MIN_INTERVAL)

        super().__init__(rate_limiter)
        self._used_prompts: list[str] = []


    # Exhausting all prompts for now, maybe change later 
    def _pick_prompt(self) -> str:

        available_prompts = [p for p in config.AI_GENERATED_IMAGE_PROMPTS if p not in self._used_prompts]

        if not available_prompts:
            self._used_prompts.clear()
            available_prompts = config.AI_GENERATED_IMAGE_PROMPTS

        prompt = random.choice(available_prompts)
        self._used_prompts.append(prompt)

        return prompt


    def fetch_one(self) -> FetchedImage | None:

        prompt = self._pick_prompt()
        encoded_prompt = quote(prompt) # URL encoding for the spaces in the prompt

        # Random seed ensures we get a unique image even for repeated prompts
        seed = random.randint(1, 999999)
        url = f"{self.BASE_URL}/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"

        print(f"[Pollinations] Fetching AI image...")
        print(f"Prompt: {prompt}")

        self.rate_limiter.calculate_wait_time_between_requests()

        # Using the whole RequestException to catch timeout errors as well 
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

        filename = f"ai_img_{uuid.uuid4().hex[:10]}.jpg"
        filepath = config.IMAGE_SAVE_DIR / filename

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"Saved image successfully: {filepath.name} ({len(response.content) / 1024:.0f} KB)")

        return FetchedImage(
            filepath=filepath,
            source="pollinations",
            is_ai=True,
            source_url=url,
            attribution=f"AI-generated via Pollinations.ai | Prompt: {prompt}",
        )
