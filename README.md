# Applied Mathematical Intelligence

An advanced **applied mathematics laboratory** built with Streamlit.

> **Applied Mathematical Intelligence** shows how calculus, probability, statistics, optimization, simulation, and AI are used to model, predict, and improve real-world systems.

## Development Status (v2.2.0)

| Item | Count |
|------|-------|
| **Interactive labs** | **6** |
| Mathematical themes | 6 |
| Mathematical Thinking pillars | 10 |
| Applied domains | 32 |
| Simulation engines | 23 |
| Domains with case studies | 16 |
| Case studies in library | 13 |
| Portfolio projects | 12 |
| Data modules (placeholders) | 6 |

Run QA before merging: `python scripts/qa_check.py` and `python scripts/smoke_test.py`

## Navigation

| Sidebar | Purpose |
|---------|---------|
| **Home** | Platform overview, stats, and explore tiles |
| **Interactive Labs** | Hands-on poker, sports EV, finance, forecasting, optimization, AI training |
| **Mathematical Thinking** | Signature cross-domain framework |
| **Mathematical Themes** | Six deep mathematical systems |
| **Applied Domains** | Case studies, simulations, data hooks |
| **Portfolio Lab** | GitHub/interview project specifications |

## Interactive Labs

Each lab follows a consistent structure:

1. **What you are trying to do** — clear goal
2. **Math idea used** — probability, statistics, optimization, etc.
3. **Interactive controls** — sliders, decisions, simulations
4. **Result / recommendation** — mathematically grounded feedback
5. **Practice challenge** — test your understanding
6. **Portfolio project idea** — build something for GitHub/interviews

| Lab | Focus |
|-----|-------|
| Poker Strategy Lab | EV, pot odds, Kelly criterion |
| Sports Betting Lab | Odds conversion, +EV detection |
| Finance & Investing Lab | Monte Carlo portfolio paths |
| Forecasting Lab | Trend fit, uncertainty bands |
| Optimization Lab | Resource allocation under constraints |
| AI Training Lab | Gradient descent, loss curves |

## Project Layout

```text
streamlit_app.py
components/          home, labs, layout, thinking, styles
content/             themes, domains, interactive_labs, portfolio, platform_meta
simulations/         registry + domain sims + simulations/labs/ (interactive labs)
data/                placeholder loaders (finance, sports, health, elections, weather, astronomy)
scripts/             qa_check.py, smoke_test.py, push_changes.bat, push_changes.ps1
```

## Installation

```bash
git clone https://github.com/Coakley11/Applied-mathematical-intelligence.git
cd Applied-mathematical-intelligence
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Optional real-data packages: `pip install -r requirements-data.txt`

## Requirements

- **requirements.txt** — core app (streamlit, pandas, numpy, matplotlib)
- **requirements-data.txt** — optional yfinance, requests for future data wiring

## Development Workflow

| Branch | Purpose |
|--------|---------|
| `main` | Stable production (Streamlit Cloud) |
| `dev` | Active development |

```bash
git checkout dev
git pull origin dev
# edit …
python scripts/qa_check.py
python scripts/smoke_test.py
scripts\push_changes.bat "Your message"
```

Release: merge `dev` → `main` after QA passes and local smoke test.

## Disclaimer

Conceptual demonstrations only — not financial, medical, engineering, gambling, or forecasting advice.

## Author

Daniel Cohen
