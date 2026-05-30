"""Platform metadata for Home page and development status."""

from content.domains import DOMAIN_NAMES
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEME_NAMES
from simulations.registry import SIMULATION_COUNT

VERSION = "2.1.0"

FEATURED_DOMAINS = [
    "Quantitative Finance",
    "Epidemiology",
    "Artificial Intelligence",
    "Drug Development & Pharmacokinetics",
    "Autonomous Vehicles",
    "Climate Modeling",
    "Election Forecasting",
    "Machine Learning",
]

ROADMAP = [
    "Wire yfinance and public CSV loaders into domain simulations",
    "Per-domain case study PDF exports for portfolio",
    "Plotly interactive charts replacing static matplotlib where valuable",
    "Bayesian inference notebooks linked from Portfolio Lab",
    "Streamlit multipage URLs for shareable domain links",
    "Calibration dashboards for ML and forecasting projects",
]

# Re-export live counts
NUM_DOMAINS = len(DOMAIN_NAMES)
NUM_THEMES = len(THEME_NAMES)
NUM_PORTFOLIO = len(PORTFOLIO_PROBLEMS)
NUM_SIMULATIONS = SIMULATION_COUNT
