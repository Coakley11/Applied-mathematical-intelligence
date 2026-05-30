# Applied Mathematical Intelligence

An advanced **applied mathematics laboratory** built with Streamlit.

> **Applied Mathematical Intelligence** shows how calculus, probability, statistics, optimization, simulation, and AI are used to model, predict, and improve real-world systems.

## Development Status (v2.1.1)

| Item | Count |
|------|-------|
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
| **Home** | Platform overview and stats |
| **Mathematical Thinking** | Signature cross-domain framework |
| **Mathematical Themes** | Six deep mathematical systems |
| **Applied Domains** | Case studies, simulations, data hooks |
| **Portfolio Lab** | GitHub/interview project specifications |

## Project Layout

```text
streamlit_app.py
components/          home, layout, thinking, styles
content/             themes, domains, domain_depth, case_studies, portfolio, platform_meta
simulations/         registry + domain-specific simulation modules
data/                placeholder loaders (finance, sports, health, elections, weather, astronomy)
scripts/             qa_check.py, push_changes.bat, push_changes.ps1
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
scripts\push_changes.bat "Your message"
```

Release: merge `dev` → `main` after QA passes and local smoke test.

## Disclaimer

Conceptual demonstrations only — not financial, medical, engineering, or forecasting advice.

## Author

Daniel Cohen
