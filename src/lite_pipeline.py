"""Sequential three-step pipeline for Vercel (no CrewAI — smaller serverless bundle)."""

import json
import os
import time
from collections.abc import Callable

import instructor
from litellm import completion

from src.env import require_api_key
from src.finance import project_financials
from src.schemas import Evaluation, FinancialSketch, Pitch


def _model_name() -> str:
    name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip() or "qwen/qwen3.8-27b"
    if name.startswith("groq/"):
        return name
    return f"groq/{name}"


def _structured(response_model, system: str, user: str, temperature: float):
    client = instructor.from_litellm(completion)
    return client.chat.completions.create(
        model=_model_name(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_model=response_model,
        max_tokens=450,
        temperature=temperature,
        api_key=require_api_key(),
    )


def _pause() -> None:
    time.sleep(40 if os.getenv("VERCEL") else 45)


def run_evaluation(idea: str, on_task: Callable | None = None):
    text = idea.strip()
    if not text:
        raise RuntimeError("Enter a startup idea before running the crew.")
    require_api_key()

    pitch = _structured(
        Pitch,
        system=(
            "You are the Visionary Founder. Turn a raw startup idea into a concrete pitch. "
            "Do not invent market statistics."
        ),
        user=(
            f"The user described this startup idea:\n\n{text}\n\n"
            "Write the pitch. Name the startup, state a one-line hook, explain the "
            "problem, the solution, who the customer is, and a brand identity.\n"
            "Brand name: a few words. Tone: at most 12 words. Tagline: at most 10 "
            "words. Do not use ellipsis. Stay inside what the idea supports. Do not "
            "add market-size claims or revenue numbers."
        ),
        temperature=0.7,
    )
    if on_task:
        on_task(None)
    _pause()

    pitch_json = json.dumps(pitch.model_dump(), indent=2)
    sketch = _structured(
        FinancialSketch,
        system=(
            "You are the Financial Officer. Label every number as an estimate. "
            "Do not cite outside market research."
        ),
        user=(
            f"Founder's pitch:\n{pitch_json}\n\n"
            "Design a subscription business around it.\n"
            "Keep every text field under 25 words.\n"
            "Include 2 or 3 tiers: name, monthly price in USD, and who it is for.\n"
            "State starting paying customers, monthly growth as a fraction from 0 to 1, "
            "monthly churn as a fraction from 0 to 1, and one sentence on why.\n"
            "Give one blended monthly price in USD (the average a customer pays).\n"
            "Do not list monthly revenue. The app calculates the 12-month timeline.\n"
            "Call every figure an estimate."
        ),
        temperature=0.3,
    )
    if on_task:
        on_task(None)
    _pause()

    sketch_json = json.dumps(sketch.model_dump(), indent=2)
    evaluation = _structured(
        Evaluation,
        system=(
            "You are a Venture Capitalist. Argue against the plan. Praise is rare. "
            "Still say what would change your mind."
        ),
        user=(
            f"Pitch:\n{pitch_json}\n\nFinancial sketch:\n{sketch_json}\n\n"
            "Keep the roast under 70 words and each list item under 20 words.\n"
            "Name logical flaws and market or pricing weaknesses. The 12-month revenue "
            "is calculated from starting customers, growth, churn, and the blended price. "
            "If those assumptions are unbelievable, say so and lower the score.\n"
            "Set probability_of_success from 0 to 100. Verdict: Pass, Interested, or Invest."
        ),
        temperature=0.4,
    )
    if on_task:
        on_task(None)

    return pitch, project_financials(sketch), evaluation
