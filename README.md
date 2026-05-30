# Applied Mathematical Intelligence

A **decision-making and simulation laboratory** built with Streamlit.

> Pick a goal — invest, bet, forecast, train AI, or simulate a system. Use the tools first; math appears when it helps you decide.

## Development Status (v2.3.0)

| Item | Count |
|------|-------|
| **Practical labs** | **5** |
| Simulation tools | 23 |
| Reference domains | 32 |
| Math themes | 6 |
| Portfolio projects | 12 |

Run QA before merging: `python scripts/qa_check.py` and `python scripts/smoke_test.py`

## What do you want to do?

| Action | Lab |
|--------|-----|
| **Invest money** | Investing & Wealth Lab |
| **Analyze a bet** | Betting, Poker & Decision Lab |
| **Forecast the future** | Prediction & Forecasting Lab |
| **Train an AI** | AI & Optimization Lab |
| **Simulate a system** | Strategy & Simulation Lab |

Each lab is **tool-first**: interactive simulators in tabs, math explained in expanders, not lectures upfront.

## Navigation

| Sidebar | Purpose |
|---------|---------|
| **Home** | Action cards — what do you want to do? |
| **5 practical labs** | Hands-on decision and simulation workspaces |
| **Reference library** | Optional — domains, themes, thinking, portfolio specs |

## Project Layout

```text
streamlit_app.py
components/          home, practical_labs, reference, layout, styles
content/             practical_labs, domains, themes, portfolio, platform_meta
simulations/         registry + labs/ (interactive tools)
data/                placeholder loaders
scripts/             qa_check.py, smoke_test.py
```

## Installation

```bash
git clone https://github.com/Coakley11/Applied-mathematical-intelligence.git
cd Applied-mathematical-intelligence
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Development Workflow

| Branch | Purpose |
|--------|---------|
| `main` | Stable production (Streamlit Cloud) |
| `dev` | Active development |

```bash
git checkout dev
python scripts/qa_check.py
python scripts/smoke_test.py
```

## Disclaimer

Educational simulations only — not financial, medical, gambling, or forecasting advice.

## Author

Daniel Cohen
