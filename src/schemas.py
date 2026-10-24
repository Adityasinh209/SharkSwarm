from typing import Literal

from pydantic import BaseModel, Field


class BrandIdentity(BaseModel):
    name: str = Field(description="Public brand name, a few words")
    tone: str = Field(description="How the brand sounds, at most 12 words, no ellipsis")
    tagline: str = Field(description="One short tagline, at most 10 words, no ellipsis")


class Pitch(BaseModel):
    startup_name: str
    hook: str = Field(description="One sentence that states the offer")
    problem: str = Field(description="The customer problem, in plain language")
    solution: str = Field(description="What the product does and why it is different")
    target_audience: str = Field(description="Who pays, and the situation they are in")
    brand: BrandIdentity


class PricingTier(BaseModel):
    name: str
    monthly_price_usd: float = Field(ge=0, description="Monthly price in US dollars")
    who_it_is_for: str


class Assumptions(BaseModel):
    starting_customers: int = Field(ge=0, description="Paying customers in month 1")
    monthly_growth_rate: float = Field(
        ge=0,
        le=1,
        description="New-customer growth as a fraction, such as 0.08 for 8 percent",
    )
    monthly_churn_rate: float = Field(
        ge=0,
        le=1,
        description="Customers lost each month as a fraction, such as 0.05 for 5 percent",
    )
    notes: str = Field(description="Why these assumptions are plausible for this idea")


class MonthRevenue(BaseModel):
    month: int = Field(ge=1, le=12)
    revenue_usd: float = Field(ge=0, description="Estimated revenue for that month")


class FinancialSketch(BaseModel):
    monetization_summary: str = Field(description="Two short sentences. Say the figures are estimates.")
    tiers: list[PricingTier] = Field(min_length=2, max_length=3)
    assumptions: Assumptions
    blended_monthly_price_usd: float = Field(
        ge=0,
        description="Average monthly price one paying customer pays, in USD",
    )


class Financials(BaseModel):
    monetization_summary: str
    tiers: list[PricingTier] = Field(min_length=2, max_length=3)
    assumptions: Assumptions
    monthly_revenue: list[MonthRevenue] = Field(min_length=12, max_length=12)
    year_one_total_usd: float = Field(
        ge=0,
        description="Sum of the 12 monthly revenue estimates",
    )


class Evaluation(BaseModel):
    roast: str = Field(description="Direct critique a founder can act on")
    logical_flaws: list[str] = Field(min_length=2, max_length=5)
    market_weaknesses: list[str] = Field(min_length=2, max_length=5)
    what_would_raise_the_score: list[str] = Field(min_length=2, max_length=4)
    probability_of_success: int = Field(ge=0, le=100)
    verdict: Literal["Pass", "Interested", "Invest"]
