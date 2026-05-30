"""Weather and climate data placeholders."""

import pandas as pd

INTEGRATION_STATUS = "placeholder"


def load_forecast_grid(station_id: str) -> pd.DataFrame:
    """Schema: lead_hour, temp, wind, precip_prob."""
    return pd.DataFrame(columns=["lead_hour", "temp", "wind", "precip_prob"])


def load_temperature_anomaly(dataset: str = "GISTEMP") -> pd.DataFrame:
    return pd.DataFrame(columns=["year", "anomaly_c", "lower_ci", "upper_ci"])
