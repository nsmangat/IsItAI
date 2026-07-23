from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from fetchers.base import FetchedImage
from rate_limiter import RateLimiter

"""Single AI-generation tell found in an image, with a bounding box for the frontend overlay"""
@dataclass
class Signal:

    tell: str           # short label, i.e. "warped text"
    explanation: str    # educational description of why this is a common sign of an AI generated image
    coordinates: dict   # {"x": int, "y": int, "width": int, "height": int} - normalized 0-1000, not raw pixels
    severity: str       # "high", "medium", or "low" - How obvious the specific tell is,
                        # not to be confused with confidence which is overall score of the picture

"""Result of analyzing a single image for signs of AI generation"""
@dataclass
class Analysis:

    image: FetchedImage
    is_ai: bool
    confidence: float
    signals: list[Signal] = field(default_factory=list)

""" Base class for all image analyzers
    May use different analysis providers in the future, but most of them need a method to manage
    rate limits and a method to actually call the api and analyze the image
"""
class ImageAnalyzer(ABC):

    def __init__(self, rate_limiter: RateLimiter):

        self.rate_limiter = rate_limiter

    @abstractmethod
    def analyze(self, image: FetchedImage) -> Analysis | None:
        
        """ Analyze a single image for AI-generation tells
            Returns analysis metadata, or None if the request failed
        """
        ...
