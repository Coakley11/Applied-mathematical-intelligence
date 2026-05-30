# Applied Mathematical Intelligence

An advanced **applied mathematics laboratory** built with Streamlit.

> **Applied Mathematical Intelligence** shows how calculus, probability, statistics, optimization, simulation, and AI are used to model, predict, and improve real-world systems.

This is **not** a textbook or worksheet app. It is a quantitative reasoning platform for exploring how professional fields use mathematics to make predictions, manage risk, and build intelligent systems.

## Development Status

| Item | Count / value |
|------|----------------|
| **Current version** | 2.1.0 |
| **Mathematical themes** | 6 |
| **Mathematical Thinking** | Signature cross-domain framework page |
| **Applied domains** | 32 (16 with unique simulations + case studies) |
| **Simulation engines** | 19 (domain-specific suites + specialized tools) |
| **Portfolio projects** | 12 (full interview/GitHub specifications) |
| **Data modules** | 6 placeholder loaders (`data/`) |

### Roadmap

- Real-world datasets (sports, markets, public health)
- Unique simulations per domain
- Plotly interactive charts
- Bayesian inference demos
- Streamlit multipage URLs for shareable links
- Neural network training visualizations
- Exportable notebook scaffolds from Portfolio Lab

## Navigation (in the app)

| Sidebar section | What it is |
|-----------------|------------|
| **Mathematical Thinking** | Signature page — modeling, uncertainty, optimization, simulation, AI as one stack |
| **Mathematical Themes** | Deep math systems — calculus, probability, statistics, optimization, simulation, AI |
| **Applied Domains** | Professional fields with **case studies**, **unique simulations**, and **data hooks** |
| **Portfolio Lab** | Full project specs: question, data, methods, visuals, Excel/Python, GitHub README |

Use **Mathematical lens** and **Depth level** to frame how content is presented.

## Project Layout

```text
streamlit_app.py
components/home.py, layout.py, thinking.py, styles.py
content/themes.py, domains.py, domain_depth.py, case_studies.py
content/mathematical_thinking.py, portfolio.py, platform_meta.py
simulations/registry.py, finance_risk.py, poker_math.py, ai_learning.py, ...
data/finance.py, sports.py, public_health.py, elections.py, weather.py, astronomy.py
scripts/push_changes.bat
```

## Installation

```bash
git clone https://github.com/Coakley11/Applied-mathematical-intelligence.git
cd Applied-mathematical-intelligence
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Technologies

- Python · Streamlit · NumPy · Matplotlib

## Deployment (Streamlit Cloud)

```text
Main file path: streamlit_app.py
Branch: main          # production — stable releases only
```

Point Streamlit Cloud at **`main`**. Develop on **`dev`**, merge when stable.

---

## Development Workflow

Use **Cursor + terminal Git** as your primary workflow. GitHub Desktop is optional.

### Branch strategy

| Branch | Purpose |
|--------|---------|
| **`main`** | Stable production version (Streamlit Cloud, public demos) |
| **`dev`** | Active development — all new features land here first |

**Rule:** Build and test on `dev`. Merge into `main` only when features are stable.

### First-time setup — create `dev`

```bash
git checkout main
git pull origin main
git checkout -b dev
git push -u origin dev
```

### Daily workflow (on `dev`)

```bash
git checkout dev
git pull origin dev

# … edit in Cursor …

git add .
git commit -m "description of changes"
git push
```

Or use the helper script from the repo root:

```bat
scripts\push_changes.bat "Added new simulations"
```

PowerShell:

```powershell
.\scripts\push_changes.ps1 "Added new simulations"
```

### Switch between branches

```bash
git checkout dev          # development
git checkout main         # production read-only locally
git pull origin dev       # update dev
git pull origin main      # update main
```

### Release: merge `dev` → `main`

```bash
git checkout main
git pull origin main
git merge dev
git push origin main
```

Optional: open a pull request on GitHub for review before merging:

```bash
gh pr create --base main --head dev --title "Release: summary" --body "Summary of changes"
gh pr merge
```

### Test before merging

1. Run locally: `streamlit run streamlit_app.py`
2. Click through **Home**, at least one **Theme**, one **Domain**, and **Portfolio Lab**
3. Confirm simulations render without errors
4. Merge only when the app runs cleanly on your machine

### Cursor workflow (no GitHub Desktop)

| Task | Where |
|------|--------|
| Edit code | Cursor editor |
| Terminal | Cursor integrated terminal (`Ctrl+`` `) |
| Stage & commit | `git add` / `git commit` or `scripts\push_changes.bat` |
| Push | `git push` |
| Pull requests | `gh pr create` in terminal (GitHub CLI) |

Ensure Git is configured in Cursor’s terminal (same as system Git). Remote: `origin` → `https://github.com/Coakley11/Applied-mathematical-intelligence.git`.

---

## Disclaimer

Conceptual and educational demonstrations only — not financial, medical, engineering, or forecasting advice.

## Author

Daniel Cohen
