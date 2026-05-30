"""Platform metadata for Home page and development status."""

from content.case_studies import CASE_STUDIES
from content.domains import DOMAINS, DOMAIN_NAMES
from content.portfolio import PORTFOLIO_PROBLEMS
from content.themes import THEME_NAMES
from simulations.registry import SIMULATION_COUNT

VERSION = "2.1.1"

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
]

NUM_THEMES = len(THEME_NAMES)
NUM_DOMAINS = len(DOMAIN_NAMES)
NUM_PORTFOLIO = len(PORTFOLIO_PROBLEMS)
NUM_SIMULATIONS = SIMULATION_COUNT
NUM_CASE_STUDY_LIBRARY = len(CASE_STUDIES)
NUM_DOMAINS_WITH_CASE_STUDIES = sum(1 for d in DOMAINS.values() if d.get("case_studies"))
