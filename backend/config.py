import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
IMAGE_SAVE_DIR = BASE_DIR / "images"
IMAGE_SAVE_DIR.mkdir(exist_ok=True)

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# Minimum seconds between requests per source to stay in free tier
POLLINATIONS_MIN_INTERVAL = 20   # Pollinations.ai doesn't look like it has strict rate limits
UNSPLASH_MIN_INTERVAL = 80       # 50 req/hr = 72s between requests, add some leeway just incase

# Prompts to generate images
# Aiming for generic photos and common scams like dating profiles, natural disaster for charity scams, and accidents
AI_GENERATED_IMAGE_PROMPTS = [
    "professional headshot of an attractive man in US Army dress uniform, confident smile, DSLR photo",
    "street photography of a busy city intersection at golden hour, 35mm film grain",
    "profile photo of a smiling male doctor in scrubs holding a stethoscope, hospital background",
    "candid photo of friends laughing at a coffee shop, shallow depth of field",
    "aerial drone shot of suburban neighborhood at sunrise, high resolution",
    "photo of a golden retriever playing fetch in a park, action shot, natural light",
    "professional food photography of a pasta dish on a wooden table, warm tones",
    "photo of a well-dressed businessman holding a phone showing large investment returns, professional setting",
    "landscape photo of a mountain lake at dawn with fog, wide angle lens",
    "street vendor selling fruit at an outdoor market, documentary photography style",
    "family portrait in a living room during holidays, warm indoor lighting",
    "aerial photo of flooded neighborhood with people on rooftops, disaster relief scene, news photography style",
    "photo of a teacher writing on a whiteboard in a classroom, candid shot",
    "sunset over the ocean with silhouettes of people on the beach, DSLR quality",
    "macro photography of dewdrops on a spider web, early morning light",
    "car crash with ambulance and police at the scene, non-gruesome and no NSFW material",
    "oil painting of a woman reading by a window, Dutch Golden Age style, canvas texture visible",
    "watercolor portrait of a street musician playing violin, loose brushwork, paper texture",
    "acrylic painting of a bustling farmers market, impressionist style, natural light",
    "charcoal sketch of an elderly man at a chess table in the park, realistic shading",
]
