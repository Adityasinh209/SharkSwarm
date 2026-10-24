from src.schemas import FinancialSketch, Financials, MonthRevenue


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
