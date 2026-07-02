import json

from google import genai
from google.genai import types

import config
from fetchers.base import FetchedImage
from rate_limiter import RateLimiter
from .base import Analysis, ImageAnalyzer, Signal

ANALYSIS_PROMPT = """You are helping build a quiz that teaches people (especially elderly users) \
to spot AI-generated images used in scams. Examine the attached image, which is known to be \
AI-generated, and identify visible tell-tale signs of AI generation (e.g. warped text, extra or \
missing fingers, asymmetric or malformed ears/eyes, unnatural skin texture, inconsistent shadows \
or reflections, nonsensical background objects).

Respond with ONLY minified JSON matching this exact schema, no markdown fences or commentary:
{
  "is_ai": true,
  "confidence": <float 0-1, how confident you are this image is AI-generated>,
  "signals": [
    {
      "tell": "<short label for the artifact>",
      "explanation": "<educational explanation of why this is a common AI tell>",
      "coordinates": {"x": <int>, "y": <int>, "width": <int>, "height": <int>},
      "severity": "high" | "medium" | "low"
    }
  ]
}

Coordinates are pixel offsets from the top-left of the image, sized for a bounding box around \
the specific artifact. If you find no clear signals, return an empty signals array. Treat each \
analysis individually, so don't include findings or similarities of the previous image analysis \
with the current image being analyzed."""

"""Analyzes images for AI-generation tells using Google Gemini Vision"""
class GeminiAnalyzer(ImageAnalyzer):

    def __init__(self, rate_limiter: RateLimiter | None = None, rate_limit: bool = True):

        if not config.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY not set. "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to .env"
            )

        if rate_limiter is None:
            rate_limiter = RateLimiter(config.GEMINI_MIN_INTERVAL, enabled=rate_limit)

        super().__init__(rate_limiter)
        
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    def analyze(self, image: FetchedImage) -> Analysis | None:

        print(f"[Gemini] Analyzing {image.filepath.name}...")
        self.rate_limiter.calculate_wait_time_between_requests()

        # Gemini API call
        try:
            image_bytes = image.filepath.read_bytes()
            response = self._client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    ANALYSIS_PROMPT,
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
        except Exception as e:
            print(f"Gemini request failed: {e}")
            return None

        try:
            data = json.loads(response.text)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Failed to parse Gemini response: {e}")
            return None

        # extract each signal or tell for AI generation based on Gemini analysis
        # get - key to look for, custom fallback
        signals = [
            Signal(
                tell=s.get("tell", ""),
                explanation=s.get("explanation", ""),
                coordinates=s.get("coordinates", {}),
                severity=s.get("severity", ""),
            )
            for s in data.get("signals", [])
        ]

        print(f"Confidence {data.get('confidence', 0):.2f}, {len(signals)} signal(s) found")

        return Analysis(
            image=image,
            is_ai=data.get("is_ai", True),
            confidence=data.get("confidence", -1),
            signals=signals,
        )
