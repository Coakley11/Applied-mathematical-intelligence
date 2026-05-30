"""Election forecasting data placeholders."""

import pandas as pd

INTEGRATION_STATUS = "placeholder"


def load_polls(state: str, cycle: int = 2024) -> pd.DataFrame:
    """Schema: pollster, date, sample, margin, candidate_a, candidate_b."""
    return pd.DataFrame(
        columns=["pollster", "date", "sample", "margin", "candidate_a", "candidate_b"]
    )


def load_historical_results(state: str) -> pd.DataFrame:
    return pd.DataFrame(columns=["year", "dem_pct", "rep_pct", "margin"])
