# Applied Mathematical Intelligence (AMI)

**A decision-analysis and reasoning platform** built with Python and Streamlit. AMI applies mathematics, probability, statistics, forecasting, optimization, simulation, and AI-assisted reasoning to real-world decisions — from bets and games to disease models, optimization problems, and open-ended ideas.

**Live demo:** [applied-mathematical-intelligence.streamlit.app](https://applied-mathematical-intelligence-8l8bqrzpp6fghaj7xuig53.streamlit.app)  
**Deploy branch:** `dev` · **Entry point:** `streamlit_app.py` · **Version:** 3.6.1

Built as part of the **Daniel Cohen AI Suite** (shared workspace auth, cloud persistence, Command Center handoffs, and cross-app insight return).

---

## Executive Summary

Most analytics tools answer one narrow question. **AMI is a general-purpose mathematical decision engine** — bring a problem, decision, prediction, strategy, or idea, and the platform helps you think about it quantitatively.

AMI combines:

- Interactive simulation labs across sports, medicine, AI, weather, and finance
- Structured problem-solving workflows with solver-backed reasoning
- Optimization workshops and idea/invention analysis
- LLM-assisted analytical questions routed to and from **Command Center**
- Account-owned workspace isolation so each user's page state, questions, and insights stay private

The app is designed as a portfolio piece demonstrating **systems design, mathematical modeling, AI-assisted workflows, and cross-application integration** — not a static textbook or course.

---

## At a Glance

| | |
|---|---|
| **Project type** | Full-stack Python decision-analysis platform |
| **Tech stack** | Python 3.11+ · Streamlit · NumPy/SciPy · Plotly · optional Supabase · suite shared modules |
| **Core domains** | Sports prediction · betting/poker · epidemiology · AI training · optimization · idea analysis · mathematical thinking |
| **Key analytics methods** | Expected value · probability models · forecasting · Monte Carlo · optimization · sensitivity analysis · LLM-assisted reasoning |
| **Primary users** | Self-directed learners · portfolio reviewers · suite users arriving from Baseball, Music, Investment, NBA, FutureLens |
| **Current status** | v3.6.1 — 8 primary action labs · 23+ simulation engines · account-owned workspace isolation on `dev` |

---

## For Employers & Reviewers

AMI demonstrates end-to-end ownership of a **multi-domain analytics product**:

| Skill area | Evidence in AMI |
|------------|-----------------|
| **Systems design** | Shared suite infrastructure (auth, workspace, cloud, deep links) across 7+ sibling apps |
| **Analytics architecture** | Simulation registry, practical labs, solver routing, persistence protocol |
| **Mathematical modeling** | EV engines, disease SIR models, optimization workshops, forecasting labs |
| **AI-assisted workflows** | Analytical question blobs, insight return to source apps, Command Center handoff |
| **Product development** | Beginner-friendly lab structure (what/why/run/read/math/try/portfolio) |
| **Cross-application integration** | Resume launch, scoped cloud keys, AMI context from Music/Baseball/Investment |

Inspect `tests/test_workspace_account_ownership.py` and `tests/test_workspace_ami.py` without running the full UI.

---

## Core Capabilities

| Capability | What it does |
|------------|--------------|
| **Solve a Problem** | Pick a domain area, ask a quantitative question, work through structured mathematical tools |
| **Explore a Math Idea** | Enter a concept (derivative, EV, Bayes, quadratic) and see real-world applications |
| **Analyze a Bet** | Expected-value checks on poker calls, casino bets, and wagering decisions |
| **Predict a Game** | Compare win probabilities to market odds; find forecasting edge |
| **Optimize a Decision** | Improve a strategy or process via optimization workshop controls |
| **Analyze an Idea** | Measure and model an invention or concept — what to quantify first |
| **Model a Disease** | Simulate outbreaks, tumor growth, pharmacokinetics, and treatment scenarios |
| **Train an AI** | Watch models learn in real time with interactive training simulations |

Additional labs (Weather, Space, Math Systems) and 32 advanced reference domains live under **Advanced reference**.

---

## Analytics & AI Methods

| Method | Use in AMI |
|--------|------------|
| **Expected Value** | Betting lab, poker call analysis, decision framing |
| **Probability Models** | Sports prediction, Bayesian reasoning, game outcome forecasts |
| **Forecasting** | Time-series and scenario projections across labs |
| **Scenario Analysis** | Multi-path what-if exploration in simulations |
| **Monte Carlo Simulation** | Uncertainty propagation in finance and risk labs |
| **Decision Trees** | Structured choice analysis in optimization workshop |
| **Optimization** | Strategy improvement, portfolio-style decision tuning |
| **Risk Analysis** | Tail risk, sensitivity, and downside framing |
| **Sensitivity Analysis** | Parameter sweeps across simulation engines |
| **Statistical Modeling** | Regression, correlation, and inference in practical labs |
| **LLM-assisted reasoning** | Analytical questions, insight return, Command Center routing |

---

## Technical Architecture

```
streamlit_app.py                        # Entry: bootstrap → auth → restore → nav
components/                             # Home, labs, workshop, idea explorer, solvers
applied_intelligence_persistent_state.py # Disk + cloud sync via sync_workspace_protocol
simulations/registry.py                 # 23+ simulation engines
content/                                # Labs, domains, case studies, tool guides
├── suite_workspace.py                  # bootstrap_suite_workspace, scoped cloud keys
├── suite_workspace_registry.py         # Account-owned workspace registry
├── suite_auth.py                       # Real Accounts + ownership enforcement
├── suite_user_persistence.py           # Workspace-scoped state_file_path
├── suite_resume_launch.py              # Deep-link / resume from Command Center
└── applied_math_return_insight.py      # Insight return to source apps
```

**Persistence paths**

| Layer | Path / key |
|-------|------------|
| Active workspace (account) | `data/workspaces/_active/{owner_user_id}.json` |
| Ownership registry | `data/workspaces/_ownership_registry.json` |
| App state | `data/workspaces/{workspace_id}/applied_intelligence_user_state.json` |
| Cloud | Supabase scoped via `applied_intelligence__{workspace}` |
| Saved items | Question blobs, insights, dismissals — all workspace-scoped |

**Startup order (account-owned workspace v2)**

1. `bootstrap_suite_workspace(st)` — auth restore → ownership clamp → workspace init
2. `apply_suite_auth_gate(st)`
3. `hydrate_applied_intelligence_from_url(st)` (deep-link path)
4. `restore_applied_intelligence_disk_shell(st)` → `prepare_applied_intelligence_workspace(st)`
5. `apply_suite_resume_launch(st, "applied_intelligence")`

---

## Screenshots

> Enable portfolio screenshot mode in the sidebar before capturing.

| # | Page | Filename (placeholder) | What to show |
|---|------|------------------------|--------------|
| 1 | Home Dashboard | `screenshots/01-home-dashboard.png` | Primary action cards |
| 2 | Decision Analysis | `screenshots/02-solve-a-problem.png` | Problem-solving lab with solver |
| 3 | Prediction Models | `screenshots/03-predict-a-game.png` | Sports prediction simulation |
| 4 | Mathematical Explorer | `screenshots/04-explore-math-idea.png` | Math idea → application mapping |
| 5 | Command Center Integration | `screenshots/05-command-center-handoff.png` | AMI question from sibling app + return insight |

---

## Why This Project Is Different

| Typical math/calc app | AMI |
|----------------------|-----|
| Single formula or chart | Multi-domain decision engine |
| Static examples | 23+ interactive simulation engines |
| Isolated tool | Suite-integrated with Command Center + 6 sibling apps |
| One user, one state | Account-owned workspace isolation per login |
| Textbook structure | Action-first labs: what → why → run → read → math → try |

AMI is a **general-purpose mathematical decision platform**, not a single-purpose calculator.

---

## Portfolio Value

AMI shows that you can:

- Design a **modular simulation registry** extensible across domains
- Build **persistence that survives Streamlit reruns** with workspace-scoped disk + cloud sync
- Integrate **LLM-assisted reasoning** without losing structured mathematical context
- Ship **cross-app intelligence** — questions and insights flow between AMI and Baseball, Music, Investment, NBA, FutureLens
- Enforce **account-owned workspace isolation** so `coakley11` never loads Daniel's saved state

A hiring manager can grasp scope and sophistication in **2–3 minutes** from this README plus the live demo.

---

## Local Setup

### Requirements

- **Python 3.11+**
- `pip install -r requirements.txt`

### Run locally

```bash
git clone https://github.com/Coakley11/Applied-mathematical-intelligence.git
cd Applied-mathematical-intelligence
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Optional environment variables

| Variable | Purpose |
|----------|---------|
| `SUITE_SUPABASE_URL` | Cloud persistence |
| `SUITE_SUPABASE_ANON_KEY` | Supabase client |
| `SUITE_AUTH_ENABLED` | Real Account sign-in |

Configure secrets in `.streamlit/secrets.toml` (see `.streamlit/secrets.toml.example`).

### Streamlit Cloud

- **Branch:** `dev`
- **Main file:** `streamlit_app.py`

### QA scripts

```bash
python scripts/qa_check.py
python scripts/smoke_test.py
```

---

## Roadmap

**Near term**
- [ ] Manual Daniel/Ariel/coakley11 workspace validation on deployed `dev`
- [ ] Cross-device AMI UI state restore (Sprint D P3)

**Medium term**
- [ ] **Real Problem Importer** — ingest user problems from external sources
- [ ] **Decision Templates** — reusable analysis frameworks per domain
- [ ] **Kalshi / prediction market workflows** — structured market-analysis paths
- [ ] **Cross-app Command Center intelligence** — richer aggregation of suite activity
- [ ] **AMI-driven analysis of Music, Baseball, Investment, and Future Lens activity** — contextual solvers from sibling app state

---

## Testing

```bash
python -m pytest tests/test_workspace_account_ownership.py tests/test_workspace_ami.py -q
```

Workspace isolation acceptance: `coakley11` → `coakley11` workspace; foreign `?suite_workspace=daniel` rejected for non-admin accounts; cloud keys scoped as `applied_intelligence__{workspace}`.

---

## Disclaimer

Educational simulations only — not medical, gambling, financial, or forecasting advice.

## Author

Daniel Cohen
