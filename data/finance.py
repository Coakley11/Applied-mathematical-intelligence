"""Finance data placeholders — wire yfinance when ready."""

from __future__ import annotations

from typing import Any

import pandas as pd

INTEGRATION_STATUS = "placeholder"
PROVIDER = "yfinance"


def load_equity_prices(
    tickers: list[str],
    start: str = "2018-01-01",
    end: str | None = None,
) -> pd.DataFrame:
    """
    Returns OHLCV panel (MultiIndex columns) for tickers.

    Live integration:
        import yfinance as yf
        return yf.download(tickers, start=start, end=end)
    """
    return pd.DataFrame(
        {
            "status": [INTEGRATION_STATUS],
            "provider": [PROVIDER],
            "tickers": [",".join(tickers)],
            "start": [start],
            "end": [end or "today"],
            "message": ["Install yfinance and replace placeholder with yf.download"],
        }
    )


def load_portfolio_returns(
    tickers: list[str],
    weights: list[float] | None = None,
    start: str = "2018-01-01",
) -> pd.DataFrame:
    """Daily portfolio returns from weighted asset returns (placeholder schema)."""
    w = weights or [1 / len(tickers)] * len(tickers)
    return pd.DataFrame(
        {
            "status": [INTEGRATION_STATUS],
            "tickers": [tickers],
            "weights": [w],
            "start": [start],
            "columns_expected": [["date", "portfolio_return", "asset_returns"]],
        }
    )


def integration_notes() -> dict[str, Any]:
    return {
        "status": INTEGRATION_STATUS,
        "provider": PROVIDER,
        "install": "pip install yfinance",
        "docs": "https://github.com/ranaroussi/yfinance",
    }
