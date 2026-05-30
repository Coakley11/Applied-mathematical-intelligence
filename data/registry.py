"""Registry of external data sources and integration status."""

from __future__ import annotations

from typing import Any

DATA_SOURCES: dict[str, dict[str, Any]] = {
    "finance": {
        "label": "Markets & portfolios",
        "provider": "yfinance (Yahoo Finance)",
        "install_hint": "pip install yfinance pandas",
        "module": "data.finance",
        "functions": ["load_equity_prices", "load_portfolio_returns"],
        "example_tickers": ["SPY", "QQQ", "TLT"],
    },
    "sports": {
        "label": "Sports performance",
        "provider": "Open CSV / sportsreference / custom scrapes",
        "install_hint": "pandas; domain-specific CSV paths",
        "module": "data.sports",
        "functions": ["load_player_season_stats", "load_team_results"],
        "example_datasets": ["MLB batting seasons", "NBA player game logs"],
    },
    "public_health": {
        "label": "Public health & epidemiology",
        "provider": "CDC / OWID / state health APIs",
        "install_hint": "pandas requests",
        "module": "data.public_health",
        "functions": ["load_case_counts", "load_vaccination_rates"],
        "example_datasets": ["Daily cases by region", "Hospitalization series"],
    },
    "elections": {
        "label": "Election polling & results",
        "provider": "FiveThirtyEight open data / state SOS files",
        "install_hint": "pandas",
        "module": "data.elections",
        "functions": ["load_polls", "load_historical_results"],
        "example_datasets": ["State polls CSV", "County results"],
    },
    "weather": {
        "label": "Weather & climate",
        "provider": "NOAA / NASA GISTEMP / Copernicus",
        "install_hint": "pandas xarray (advanced)",
        "module": "data.weather",
        "functions": ["load_forecast_grid", "load_temperature_anomaly"],
        "example_datasets": ["Station daily Tmax", "Global anomaly index"],
    },
    "astronomy": {
        "label": "Astronomy & astrophysics",
        "provider": "NASA Exoplanet Archive / SDSS",
        "install_hint": "pandas astroquery (optional)",
        "module": "data.astronomy",
        "functions": ["load_exoplanet_catalog", "load_light_curve_placeholder"],
        "example_datasets": ["Kepler candidate table", "Transit light curves"],
    },
}


def list_sources() -> list[str]:
    return list(DATA_SOURCES.keys())


def describe_source(key: str) -> dict[str, Any] | None:
    return DATA_SOURCES.get(key)
