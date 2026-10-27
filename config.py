from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-api-key-here")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or os.getenv("Mistral_API_KEY", "your-api-key-here")

BATCH_SIZE = 5  # default; can be overridden per-model below

# Per-model batch size override (some models only support 1 image per call)
BATCH_SIZE_OVERRIDE = {
    "llama3.2-vision": 1,   # ollama llama3.2-vision = single-image only
    "pixtral-12b-2409": 2,  # Mistral free tier rate-limits at >2 images/request
}

# Cap images per scenario to control rate-limit + token budget.
# None = use all images. Integer = use last N images (most risk-informative frames).
IMAGES_PER_SCENARIO = 5

DATASET_PATH = "./Dataset/"

# Per-model throttle (seconds between requests) — RPM-driven
THROTTLE_SECONDS = {
    "gemini-3.1-flash-lite-preview": 4.5,   # RPM 15 → 4s + buffer
    "gpt-4o-mini": 0.5,
    "llama3.2-vision": 0,
    "pixtral-12b-2409": 1.2,                # Mistral free 1 RPS → 1s + buffer
}

# Retry backoff schedule (seconds) — applies to rate-limit and network errors
RETRY_DELAYS = [10, 30, 90, 180]

MODELS = [
    {"name": "gemini-3.1-flash-lite-preview", "API_KEY": GEMINI_API_KEY,  "enabled": True},
    {"name": "llama3.2-vision",               "API_KEY": None,            "enabled": False},
    {"name": "gpt-4o-mini",                   "API_KEY": OPENAI_API_KEY,  "enabled": False},
    {"name": "pixtral-12b-2409",              "API_KEY": MISTRAL_API_KEY, "enabled": False},
]
