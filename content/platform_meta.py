"""Platform metadata for Home page and development status."""

from content.case_studies import CASE_STUDIES
from content.domains import DOMAINS, DOMAIN_NAMES
from content.portfolio import PORTFOLIO_PROBLEMS
from content.practical_labs import NUM_PRACTICAL_LABS, NUM_PRIMARY_ACTIONS
from content.themes import THEME_NAMES
from content.tool_guides import TOOL_GUIDES
from simulations.registry import SIMULATION_COUNT

VERSION = "3.4.0"

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
    "Playable poker practice mini-game in betting lab",
    "Plotly interactive charts for lab visualizations",
    "Shareable lab URLs via Streamlit multipage",
]

NUM_THEMES = len(THEME_NAMES)
NUM_DOMAINS = len(DOMAIN_NAMES)
NUM_PORTFOLIO = len(PORTFOLIO_PROBLEMS)
NUM_SIMULATIONS = SIMULATION_COUNT
NUM_TOOL_GUIDES = len(TOOL_GUIDES)
NUM_CASE_STUDY_LIBRARY = len(CASE_STUDIES)
NUM_DOMAINS_WITH_CASE_STUDIES = sum(1 for d in DOMAINS.values() if d.get("case_studies"))
