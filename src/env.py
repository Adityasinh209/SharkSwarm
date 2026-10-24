import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

MISSING_KEY = (
    "GROQ_API_KEY is missing. Add it in the Vercel project Environment Variables "
    "(Production and Preview), then redeploy."
)


def load_env() -> None:
    load_dotenv(ENV_FILE)


def api_key() -> str:
    load_env()
    return os.getenv("GROQ_API_KEY", "").strip()


def require_api_key() -> str:
    key = api_key()
    if not key:
        raise RuntimeError(MISSING_KEY)
    return key
