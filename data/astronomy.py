"""Astronomy data placeholders."""

import pandas as pd

INTEGRATION_STATUS = "placeholder"


def load_exoplanet_catalog(source: str = "NASA Archive") -> pd.DataFrame:
    return pd.DataFrame(
        columns=["planet_name", "orbital_period", "transit_depth_ppm", "stellar_teff"]
    )


def load_light_curve_placeholder(target_id: str) -> pd.DataFrame:
    return pd.DataFrame(columns=["time", "flux", "flux_err"])
