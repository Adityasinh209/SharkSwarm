import html

import streamlit as st

from src.crew import MISSING_KEY, api_key, run_evaluation

SAMPLES = {
    "Hostel meals": (
        "An app that matches college students with short-term hostel meal plans "
        "based on budget and diet."
    ),
    "Kirana surplus": (
        "A marketplace where neighborhood kirana stores share surplus inventory "
        "before it expires."
    ),
    "Freelance cash flow": (
        "A tool that turns a freelancer's messy invoices into a weekly cash-flow forecast."
    ),
}

STAGE_LABELS = (
    "Visionary Founder is writing the pitch",
    "Financial Officer is building the 12-month sketch",
    "Venture Capitalist is stress-testing the plan",
)


def redact(message: str) -> str:
    key = api_key()
    if key:
        message = message.replace(key, "[redacted]")
    return message


def render_pitch(pitch) -> None:
    st.subheader(pitch.startup_name)
    st.markdown(f"*{pitch.hook}*")
    st.markdown("**Problem**")
    st.write(pitch.problem)
    st.markdown("**Solution**")
    st.write(pitch.solution)
    st.markdown("**Target audience**")
    st.write(pitch.target_audience)
    brand = pitch.brand
    st.markdown("**Brand identity**")
    st.markdown(
        f"""
<div style="font-size:0.92rem;line-height:1.55;color:inherit;">
<p style="margin:0.35rem 0;"><strong>Brand</strong><br>{html.escape(brand.name)}</p>
<p style="margin:0.35rem 0;"><strong>Tone</strong><br>{html.escape(brand.tone)}</p>
<p style="margin:0.35rem 0;"><strong>Tagline</strong><br>{html.escape(brand.tagline)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_financials(financials) -> None:
    st.caption(
        "These figures are estimates generated from the assumptions below. "
        "They are not market research and not financial advice."
    )
    st.write(financials.monetization_summary)
    st.markdown("**Subscription tiers**")
    for tier in financials.tiers:
        st.markdown(
            f"**{tier.name}** — ${tier.monthly_price_usd:,.0f}/month. {tier.who_it_is_for}"
        )
    assumptions = financials.assumptions
    one, two, three = st.columns(3)
    one.metric("Starting customers", f"{assumptions.starting_customers:,}")
    two.metric("Monthly growth", f"{assumptions.monthly_growth_rate:.0%}")
    three.metric("Monthly churn", f"{assumptions.monthly_churn_rate:.0%}")
    st.write(assumptions.notes)
    st.markdown("**12-month revenue**")
    st.caption(
        "Calculated from starting customers, monthly growth, monthly churn, "
        "and the blended price."
    )
    st.dataframe(
        [
            {"Month": row.month, "Estimated revenue (USD)": round(row.revenue_usd, 2)}
            for row in financials.monthly_revenue
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.metric("Year-1 total (estimate)", f"${financials.year_one_total_usd:,.0f}")


def render_evaluation(evaluation) -> None:
    score, verdict = st.columns(2)
    score.metric("Probability of success", f"{evaluation.probability_of_success}/100")
    verdict.metric("Verdict", evaluation.verdict)
    st.markdown("**Roast**")
    st.write(evaluation.roast)
    left, right = st.columns(2)
    with left:
        st.markdown("**Logical flaws**")
        for item in evaluation.logical_flaws:
            st.markdown(f"- {item}")
    with right:
        st.markdown("**Market weaknesses**")
        for item in evaluation.market_weaknesses:
            st.markdown(f"- {item}")
    st.markdown("**What would raise the score**")
    for item in evaluation.what_would_raise_the_score:
        st.markdown(f"- {item}")


def apply_sample(text: str) -> None:
    st.session_state.idea = text


def main() -> None:
    st.set_page_config(page_title="SharkSwarm", page_icon="🦈", layout="wide")
    st.title("SharkSwarm")
    st.caption(
        "Three agents expand one idea into a pitch, a financial sketch, and a roast. "
        "A full run takes a few minutes. Revenue numbers are model estimates, not financial advice."
    )

    if "idea" not in st.session_state:
        st.session_state.idea = ""
    if "result" not in st.session_state:
        st.session_state.result = None

    st.text_area(
        "Startup idea",
        height=120,
        placeholder="Describe the product, who it is for, and the problem it solves.",
        key="idea",
    )
    sample_cols = st.columns(len(SAMPLES))
    for column, (label, text) in zip(sample_cols, SAMPLES.items()):
        column.button(label, on_click=apply_sample, args=(text,), use_container_width=True)

    if not api_key():
        st.warning(MISSING_KEY)

    run = st.button("Run the crew", type="primary", disabled=not api_key())
    if run:
        stage = {"index": 0}

        try:
            with st.status(f"{STAGE_LABELS[0]}…", expanded=True) as status:

                def tracked(_output) -> None:
                    stage["index"] += 1
                    finished = STAGE_LABELS[stage["index"] - 1]
                    status.write(f"{finished} — done")
                    if stage["index"] < len(STAGE_LABELS):
                        status.update(label=f"{STAGE_LABELS[stage['index']]}…")

                pitch, financials, evaluation = run_evaluation(
                    st.session_state.idea,
                    on_task=tracked,
                )
                status.update(label="All three agents finished", state="complete")
            st.session_state.result = (pitch, financials, evaluation)
        except Exception as exc:
            st.session_state.result = None
            st.error(redact(str(exc)))

    result = st.session_state.result
    if result is None:
        return

    pitch, financials, evaluation = result
    pitch_tab, money_tab, review_tab = st.tabs(["Pitch", "Financials", "Evaluation"])
    with pitch_tab:
        render_pitch(pitch)
    with money_tab:
        render_financials(financials)
    with review_tab:
        render_evaluation(evaluation)


if __name__ == "__main__":
    main()
