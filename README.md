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

## Run locally (Streamlit)

```bash
streamlit run streamlit_app.py
```

Type an idea, or use one of the sample ideas, then run the crew. The page shows three stages while the crew runs, then opens tabs for the pitch, the financials, and the evaluation.

## Deploy on Vercel

Vercel cannot host Streamlit as a long-running server. Production on Vercel uses:

- **`public/`** — static web UI (same three tabs as Streamlit)
- **`api/evaluate.py`** — serverless Python route that runs the CrewAI pipeline

### Steps

1. Import [github.com/Adityasinh209/SharkSwarm](https://github.com/Adityasinh209/SharkSwarm) in the [Vercel dashboard](https://vercel.com/new).
2. Leave the default framework preset (static `public/` + Python functions).
3. Add environment variables (Production and Preview):
   - `GROQ_API_KEY` — your Groq key
   - `GROQ_MODEL` — optional, default `qwen/qwen3.8-27b`
4. Deploy.

### Limits

- A full crew run takes **about 2–3 minutes** (three Groq calls plus short pauses for free-tier rate limits).
- **`memory`** in [`vercel.json`](vercel.json) must be **2048 MB or less** on the free Hobby plan (we use 2048).
- **`maxDuration`** is set to **300** seconds in config, but Hobby often allows only **short** function timeouts (often ~10s). A 2–3 minute crew run may still fail on Hobby even after deploy succeeds; Pro/team plans or Railway/Render are safer for this app.
- The Python bundle includes CrewAI and LiteLLM; the first deploy or cold start can be slow. If the deployment exceeds Vercel’s size limit, use local Streamlit or a container host (Railway, Render) instead.

### Test locally with Vercel CLI

```bash
npm i -g vercel
vercel env pull .env.local   # or keep using .env for GROQ_API_KEY
vercel dev
```

Open the URL shown, submit an idea, and confirm `/api/evaluate` returns JSON.

## How the agents hand off work

1. **Visionary Founder** expands the raw idea into a problem, solution, audience, and brand.
2. **Financial Officer** reads that pitch and builds subscription tiers plus a 12-month revenue sketch. Every figure must follow from stated assumptions (starting customers, growth, churn).
3. **Venture Capitalist** reads both earlier outputs, argues against them, and returns a score from 0 to 100 plus a verdict: Pass, Interested, or Invest.

Delegation and crew memory are off so each persona stays in its role and the demo does not need an embedding database. The formal write-up is in [SYNOPSIS.md](SYNOPSIS.md).
