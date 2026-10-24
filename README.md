# SharkSwarm

A Streamlit app that turns one startup idea into a pitch, a 12-month financial sketch, and a venture-capital roast. Three CrewAI agents run in order on Groq: Visionary Founder, Financial Officer, then Venture Capitalist.

Revenue numbers are labeled estimates from the model's assumptions. They are not market research and not financial advice.

## Setup

1. Create a free API key at [console.groq.com/keys](https://console.groq.com/keys).
2. Copy the environment file and paste the key:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```
GROQ_API_KEY=your-key-here
GROQ_MODEL=qwen/qwen3.8-27b
```

`GROQ_MODEL` is optional. The app prefixes it with `groq/` for CrewAI. Pick a model your key can access (see [console.groq.com/docs/models](https://console.groq.com/docs/models)). `qwen/qwen3.8-27b` works well with CrewAI structured outputs on the free tier.

If you see `CacheableResult` import errors after `pip install -U`, keep `litellm>=1.93.0,<1.106` as pinned in `requirements.txt` (CrewAI uses MCP 1.x).

## Run

```bash
streamlit run app.py
```

Type an idea, or use one of the sample ideas, then run the crew. The page shows three stages while the crew runs, then opens tabs for the pitch, the financials, and the evaluation.

## How the agents hand off work

1. **Visionary Founder** expands the raw idea into a problem, solution, audience, and brand.
2. **Financial Officer** reads that pitch and builds subscription tiers plus a 12-month revenue sketch. Every figure must follow from stated assumptions (starting customers, growth, churn).
3. **Venture Capitalist** reads both earlier outputs, argues against them, and returns a score from 0 to 100 plus a verdict: Pass, Interested, or Invest.

Delegation and crew memory are off so each persona stays in its role and the demo does not need an embedding database. The formal write-up is in [SYNOPSIS.md](SYNOPSIS.md).
