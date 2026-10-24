const SAMPLES = {
  "Hostel meals":
    "An app that matches college students with short-term hostel meal plans based on budget and diet.",
  "Kirana surplus":
    "A marketplace where neighborhood kirana stores share surplus inventory before it expires.",
  "Freelance cash flow":
    "A tool that turns a freelancer's messy invoices into a weekly cash-flow forecast.",
};

const STAGES = [
  "Visionary Founder is writing the pitch…",
  "Financial Officer is building the 12-month sketch…",
  "Venture Capitalist is stress-testing the plan…",
];

const ideaEl = document.getElementById("idea");
const runBtn = document.getElementById("run");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const warningEl = document.getElementById("key-warning");
const resultsEl = document.getElementById("results");
const samplesEl = document.getElementById("samples");

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function setError(message) {
  if (!message) {
    errorEl.classList.add("hidden");
    errorEl.textContent = "";
    return;
  }
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
}

function renderSamples() {
  for (const [label, text] of Object.entries(SAMPLES)) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;
    btn.addEventListener("click", () => {
      ideaEl.value = text;
    });
    samplesEl.appendChild(btn);
  }
}

function renderPitch(pitch) {
  const b = pitch.brand;
  return `
    <h2>${escapeHtml(pitch.startup_name)}</h2>
    <p><em>${escapeHtml(pitch.hook)}</em></p>
    <h3>Problem</h3>
    <p>${escapeHtml(pitch.problem)}</p>
    <h3>Solution</h3>
    <p>${escapeHtml(pitch.solution)}</p>
    <h3>Target audience</h3>
    <p>${escapeHtml(pitch.target_audience)}</p>
    <h3>Brand identity</h3>
    <div class="brand-block">
      <p><strong>Brand</strong><br>${escapeHtml(b.name)}</p>
      <p><strong>Tone</strong><br>${escapeHtml(b.tone)}</p>
      <p><strong>Tagline</strong><br>${escapeHtml(b.tagline)}</p>
    </div>
  `;
}

function renderFinancials(fin) {
  const a = fin.assumptions;
  const tiers = fin.tiers
    .map(
      (t) =>
        `<li><strong>${escapeHtml(t.name)}</strong> — $${t.monthly_price_usd.toLocaleString()}/month. ${escapeHtml(t.who_it_is_for)}</li>`
    )
    .join("");
  const rows = fin.monthly_revenue
    .map(
      (r) =>
        `<tr><td>${r.month}</td><td>$${Number(r.revenue_usd).toLocaleString(undefined, { maximumFractionDigits: 2 })}</td></tr>`
    )
    .join("");
  return `
    <p class="muted">These figures are estimates from the assumptions below. They are not market research or financial advice.</p>
    <p>${escapeHtml(fin.monetization_summary)}</p>
    <h3>Subscription tiers</h3>
    <ul>${tiers}</ul>
    <div class="metrics">
      <div class="metric"><span>Starting customers</span><strong>${a.starting_customers.toLocaleString()}</strong></div>
      <div class="metric"><span>Monthly growth</span><strong>${Math.round(a.monthly_growth_rate * 100)}%</strong></div>
      <div class="metric"><span>Monthly churn</span><strong>${Math.round(a.monthly_churn_rate * 100)}%</strong></div>
    </div>
    <p>${escapeHtml(a.notes)}</p>
    <h3>12-month revenue</h3>
    <p class="muted">Calculated from starting customers, growth, churn, and the blended price.</p>
    <table><thead><tr><th>Month</th><th>Estimated revenue (USD)</th></tr></thead><tbody>${rows}</tbody></table>
    <div class="metrics">
      <div class="metric"><span>Year-1 total (estimate)</span><strong>$${Number(fin.year_one_total_usd).toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong></div>
    </div>
  `;
}

function renderEvaluation(ev) {
  const list = (items) => items.map((i) => `<li>${escapeHtml(i)}</li>`).join("");
  return `
    <div class="metrics">
      <div class="metric"><span>Probability of success</span><strong>${ev.probability_of_success}/100</strong></div>
      <div class="metric"><span>Verdict</span><strong>${escapeHtml(ev.verdict)}</strong></div>
    </div>
    <h3>Roast</h3>
    <p>${escapeHtml(ev.roast)}</p>
    <div class="two-col">
      <div><h3>Logical flaws</h3><ul>${list(ev.logical_flaws)}</ul></div>
      <div><h3>Market weaknesses</h3><ul>${list(ev.market_weaknesses)}</ul></div>
    </div>
    <h3>What would raise the score</h3>
    <ul>${list(ev.what_would_raise_the_score)}</ul>
  `;
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab");
  const panels = {
    pitch: document.getElementById("pitch"),
    financials: document.getElementById("financials"),
    evaluation: document.getElementById("evaluation"),
  };
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      Object.values(panels).forEach((p) => p.classList.add("hidden"));
      panels[tab.dataset.tab].classList.remove("hidden");
    });
  });
}

async function checkReady() {
  try {
    const res = await fetch("/api/evaluate");
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(`API returned ${res.status} (not JSON). ${text.slice(0, 120)}`);
    }
    if (!res.ok) {
      throw new Error(data.error || `API error ${res.status}`);
    }
    if (!data.ready) {
      warningEl.textContent = data.message || "GROQ_API_KEY is not configured on the server.";
      warningEl.classList.remove("hidden");
      runBtn.disabled = true;
      return;
    }
    warningEl.classList.add("hidden");
    runBtn.disabled = false;
  } catch (err) {
    warningEl.textContent =
      err.message || "Could not reach /api/evaluate. Check the deployment logs.";
    warningEl.classList.remove("hidden");
    runBtn.disabled = true;
  }
}

async function runCrew() {
  setError("");
  const idea = ideaEl.value.trim();
  if (!idea) {
    setError("Enter a startup idea before running the crew.");
    return;
  }
  runBtn.disabled = true;
  statusEl.classList.remove("hidden");
  statusEl.textContent = STAGES[0];
  let stage = 0;
  const ticker = setInterval(() => {
    stage = Math.min(stage + 1, STAGES.length - 1);
    statusEl.textContent = STAGES[stage];
  }, 45000);

  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "The crew failed.");
    }
    document.getElementById("pitch").innerHTML = renderPitch(data.pitch);
    document.getElementById("financials").innerHTML = renderFinancials(data.financials);
    document.getElementById("evaluation").innerHTML = renderEvaluation(data.evaluation);
    resultsEl.classList.remove("hidden");
    statusEl.textContent = "All three agents finished.";
  } catch (err) {
    setError(err.message || String(err));
    statusEl.classList.add("hidden");
  } finally {
    clearInterval(ticker);
    runBtn.disabled = false;
  }
}

renderSamples();
setupTabs();
checkReady();
runBtn.addEventListener("click", runCrew);
