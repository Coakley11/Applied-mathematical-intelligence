"""Public health / epidemiology data placeholders."""

import pandas as pd

INTEGRATION_STATUS = "placeholder"


def load_case_counts(region: str = "US") -> pd.DataFrame:
    """Schema: date, cases, deaths, hospitalizations."""
    return pd.DataFrame(columns=["date", "cases", "deaths", "hospitalizations"])


def load_vaccination_rates(region: str = "US") -> pd.DataFrame:
    return pd.DataFrame(columns=["date", "doses_per_capita", "fully_vaccinated_pct"])
