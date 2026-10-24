**Project Title (Formal):**
SharkSwarm: A Multi-Agent System for Autonomous Business Plan Generation and Investment Risk Evaluation

**Project Title (Catchy):**
The AI Shark Tank: Multi-Agent Startup Pitch & Financial Roast Simulation

### Project Description

**1. Introduction & Objective:**
Evaluating the viability of a new business idea requires a diverse set of skills: creative product vision, pragmatic financial modeling, and critical risk assessment. This project aims to simulate this complex, multi-disciplinary process using Agentic AI. By leveraging a multi-agent orchestration framework (such as CrewAI or LangGraph), the system takes a single, raw user idea and autonomously expands it into a structured business pitch, generates a financial model, and conducts a rigorous investment critique.

**2. Problem Statement:**
Traditional AI chatbots process prompts in isolation, often resulting in generic or overly optimistic outputs when asked to evaluate business concepts. They lack the adversarial reasoning required to test an idea's actual feasibility. This project solves this by using a distributed agentic workflow where distinct AI personas collaborate and critique each other's outputs, mimicking a real-world venture capital evaluation process.

**3. Proposed Architecture & Workflow:**
The system is built on a sequential multi-agent architecture featuring three distinct AI personas:

* **Agent 1 (The Visionary Founder):** Ingests the user's raw idea and expands it into a comprehensive 3-part pitch outlining the core problem, the proposed solution, the target audience, and a brand identity.
* **Agent 2 (The Financial Officer):** Analyzes the Founder’s pitch to formulate a plausible monetization strategy. It generates a pricing model, designs subscription tiers, and projects a rough 12-month revenue timeline based on standard SaaS metrics.
* **Agent 3 (The Venture Capitalist / Reviewer):** Acts as the critical evaluator. It ingests the outputs of Agents 1 and 2, stress-tests the business plan for logical flaws and market weaknesses, provides a brutal "Roast" (constructive critique), and assigns a final data-driven "Probability of Success" score.

**4. Technology Stack:**

* **Agent Orchestration:** CrewAI or LangGraph (for state management and task routing).
* **Language Models:** Google Gemini, Groq, or OpenAI API (for agent reasoning).
* **Frontend UI:** Streamlit (to display the interactive tabs for the Pitch, Financials, and final Evaluation).
* **Programming Language:** Python.

**5. Expected Outcome & Innovation:**
The final deliverable will be an interactive web application where users can input any startup idea and instantly receive a holistic business evaluation. The project's core innovation lies in its demonstration of **role-based prompt engineering and adversarial multi-agent reasoning**, proving that separating tasks across specialized agents produces more nuanced, accurate, and entertaining results than a single LLM prompt.

The running app uses CrewAI and Groq. See [README.md](README.md).
