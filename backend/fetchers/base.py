from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from rate_limiter import RateLimiter

"""Data required for each image"""
@dataclass
class FetchedImage:
    

    filepath: Path
    source: str        # API like "pollinations" or "unsplash"
    is_ai: bool        # True for AI-generated, False for real photos
    source_url: str    # Original URL or prompt used
    attribution: str   # Credit info (required by Unsplash TOS)

""" Base class for all image source fetchers
    May use different image sources in the future, but all of them need a method to manage limit rates
    and a method to actually call the api, get the image and save it 
"""
class ImageFetcher(ABC):
    

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter

    @abstractmethod
    def fetch_one(self) -> FetchedImage | None:
        """ Fetch a single image and save it to disk
            Returns image metadata, or None if the request failed
        """
        ...
