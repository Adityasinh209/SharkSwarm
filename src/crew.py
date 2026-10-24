import os
import time
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, LLM, Process, Task
from crewai.utilities.internal_instructor import InternalInstructor

from src.schemas import Evaluation, FinancialSketch, Financials, MonthRevenue, Pitch

# CrewAI's structured-output call does not forward max_tokens. Groq's free
# tier rejects any request that reserves more than 1000 output tokens.
_original_to_pydantic = InternalInstructor.to_pydantic


def _to_pydantic_with_limits(self):
    create = self._client.chat.completions.create

    def limited_create(*args, **kwargs):
        llm = self.llm
        if not isinstance(llm, str):
            cap = getattr(llm, "max_tokens", None)
            if cap and "max_tokens" not in kwargs:
                kwargs["max_tokens"] = cap
            key = getattr(llm, "api_key", None)
            if key and "api_key" not in kwargs:
                kwargs["api_key"] = key
        return create(*args, **kwargs)

    self._client.chat.completions.create = limited_create
    try:
        return _original_to_pydantic(self)
    finally:
        self._client.chat.completions.create = create


InternalInstructor.to_pydantic = _to_pydantic_with_limits

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env() -> None:
    load_dotenv(ENV_FILE)


load_env()

DEFAULT_MODEL = "qwen/qwen3.8-27b"
MISSING_KEY = (
    "GROQ_API_KEY is missing. Copy .env.example to .env and paste a key from "
    "https://console.groq.com/keys"
)


def groq_model_name() -> str:
    name = os.getenv("GROQ_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    if name.startswith("groq/"):
        return name
    return f"groq/{name}"


def api_key() -> str:
    load_env()
    return os.getenv("GROQ_API_KEY", "").strip()


def require_api_key() -> str:
    key = api_key()
    if not key:
        raise RuntimeError(MISSING_KEY)
    return key


def _llm(temperature: float) -> LLM:
    # Groq's free tier rejects a single call that reserves more than 1000 output tokens.
    return LLM(
        model=groq_model_name(),
        temperature=temperature,
        api_key=require_api_key(),
        max_tokens=450,
    )


def build_crew(on_task: Callable | None = None) -> Crew:
    founder = Agent(
        role="Visionary Founder",
        goal=(
            "Turn a raw startup idea into a concrete pitch a stranger could understand "
            "in one minute."
        ),
        backstory=(
            "You have shipped two early products and you write the way founders talk "
            "in a first meeting: specific customer, specific pain, specific product. "
            "You do not invent market statistics."
        ),
        llm=_llm(0.7),
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )
    officer = Agent(
        role="Financial Officer",
        goal=(
            "Attach a simple subscription model and a 12-month revenue sketch to the "
            "founder's pitch, with every figure tied to stated assumptions."
        ),
        backstory=(
            "You build back-of-the-envelope SaaS models. You label every number as an "
            "estimate. You never cite outside market research you were not given."
        ),
        llm=_llm(0.3),
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )
    capitalist = Agent(
        role="Venture Capitalist",
        goal=(
            "Stress-test the pitch and the financial sketch, then score the chance "
            "this becomes a real business."
        ),
        backstory=(
            "You have passed on more deals than you have funded. You look for fuzzy "
            "customers, pricing that ignores willingness to pay, and revenue math that "
            "does not follow from the assumptions. Praise is rare and must be earned. "
            "You still tell the founder what would change your mind."
        ),
        llm=_llm(0.4),
        allow_delegation=False,
        verbose=False,
        max_iter=2,
    )

    pitch_task = Task(
        description=(
            "The user described this startup idea:\n\n{idea}\n\n"
            "Write the pitch. Name the startup, state a one-line hook, explain the "
            "problem, the solution, who the customer is, and a brand identity.\n"
            "Brand name: a few words. Tone: at most 12 words. Tagline: at most 10 "
            "words. Do not use ellipsis. Stay inside what the idea supports. Do not "
            "add market-size claims or revenue numbers."
        ),
        expected_output=(
            "A Pitch object with startup_name, hook, problem, solution, "
            "target_audience, and brand (name, tone, tagline)."
        ),
        agent=founder,
        output_pydantic=Pitch,
    )
    financial_task = Task(
        description=(
            "Read the founder's pitch. Design a subscription business around it.\n"
            "Keep every text field under 25 words.\n"
            "Include 2 or 3 tiers: name, monthly price in USD, and who it is for.\n"
            "State starting paying customers, monthly growth as a fraction from 0 to 1, "
            "monthly churn as a fraction from 0 to 1, and one sentence on why.\n"
            "Give one blended monthly price in USD (the average a customer pays).\n"
            "Do not list monthly revenue. The app calculates the 12-month timeline.\n"
            "Call every figure an estimate. Do not invent third-party market data."
        ),
        expected_output=(
            "A FinancialSketch with monetization_summary, 2 or 3 tiers, assumptions, "
            "and blended_monthly_price_usd."
        ),
        agent=officer,
        context=[pitch_task],
        output_pydantic=FinancialSketch,
    )
    review_task = Task(
        description=(
            "Read the pitch and the financial sketch. Argue against them.\n"
            "Keep the roast under 70 words and each list item under 20 words.\n"
            "Name logical flaws and market or pricing weaknesses. The 12-month revenue "
            "is calculated from starting customers, growth, churn, and the blended price. "
            "If those assumptions are unbelievable, say so and lower the score.\n"
            "Write a roast the founder can use: direct, specific, and free of generic "
            "encouragement.\n"
            "List what evidence or product changes would raise the score.\n"
            "Set probability_of_success from 0 to 100. Use Pass when the idea is not "
            "investable yet, Interested when the problem is real but the plan is thin, "
            "and Invest only when both the customer and the model hold up."
        ),
        expected_output=(
            "An Evaluation object with roast, logical_flaws, market_weaknesses, "
            "what_would_raise_the_score, probability_of_success, and verdict "
            "(Pass, Interested, or Invest)."
        ),
        agent=capitalist,
        context=[pitch_task, financial_task],
        output_pydantic=Evaluation,
    )

    finished = {"count": 0}

    def after_task(output) -> None:
        if on_task is not None:
            on_task(output)
        finished["count"] += 1
        # Free-tier Groq allows 1000 output tokens per minute. Each call reserves
        # max_tokens, so back-to-back agents get rejected. Wait out the window.
        if finished["count"] < 3:
            time.sleep(45)

    return Crew(
        agents=[founder, officer, capitalist],
        tasks=[pitch_task, financial_task, review_task],
        process=Process.sequential,
        memory=False,
        verbose=False,
        task_callback=after_task,
    )


def _as_model(value, model_type):
    if isinstance(value, model_type):
        return value
    if value is None:
        raise RuntimeError(
            f"The crew did not return a {model_type.__name__}. Run the idea again."
        )
    if hasattr(value, "model_dump"):
        return model_type.model_validate(value.model_dump())
    return model_type.model_validate(value)


def run_evaluation(idea: str, on_task: Callable | None = None):
    text = idea.strip()
    if not text:
        raise RuntimeError("Enter a startup idea before running the crew.")
    require_api_key()
    result = build_crew(on_task).kickoff(inputs={"idea": text})
    outputs = result.tasks_output
    if len(outputs) < 3:
        raise RuntimeError("The crew finished before all three agents reported.")
    pitch = _as_model(outputs[0].pydantic, Pitch)
    sketch = _as_model(outputs[1].pydantic, FinancialSketch)
    evaluation = _as_model(outputs[2].pydantic, Evaluation)
    return pitch, project_financials(sketch), evaluation


def project_financials(sketch: FinancialSketch) -> Financials:
    """Build the 12-month timeline from the officer's assumptions."""
    assumptions = sketch.assumptions
    customers = float(assumptions.starting_customers)
    monthly = []
    for month in range(1, 13):
        monthly.append(
            MonthRevenue(
                month=month,
                revenue_usd=round(customers * sketch.blended_monthly_price_usd, 2),
            )
        )
        customers *= (1 + assumptions.monthly_growth_rate) * (
            1 - assumptions.monthly_churn_rate
        )
    return Financials(
        monetization_summary=sketch.monetization_summary,
        tiers=sketch.tiers,
        assumptions=assumptions,
        monthly_revenue=monthly,
        year_one_total_usd=round(sum(row.revenue_usd for row in monthly), 2),
    )
