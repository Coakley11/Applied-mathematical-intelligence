"""Supported decision types for the AMI Problem Importer."""

from __future__ import annotations

from typing import Any

DECISION_TYPES: dict[str, dict[str, Any]] = {
    "prediction_market_bet": {
        "label": "Prediction market / bet",
        "description": "Kalshi, Calci, or similar yes/no contract",
        "phase": 0,
        "enabled": True,
    },
    "investment": {
        "label": "Stock / ETF investment",
        "description": "Buy, hold, or sell an investment",
        "phase": 2,
        "enabled": False,
    },
    "job_offer": {
        "label": "Job offer decision",
        "description": "Compare compensation and lifestyle factors",
        "phase": 2,
        "enabled": False,
    },
    "loan_financing": {
        "label": "Car loan / financing",
        "description": "Loan terms, payments, and alternatives",
        "phase": 2,
        "enabled": False,
    },
    "purchase_decision": {
        "label": "Purchase decision",
        "description": "Buy vs wait, price comparison",
        "phase": 2,
        "enabled": False,
    },
    "tax_payment": {
        "label": "Tax / payment decision",
        "description": "Timing, deductions, payment strategy",
        "phase": 2,
        "enabled": False,
    },
    "general_optimization": {
        "label": "General optimization",
        "description": "Maximize or minimize under constraints",
        "phase": 2,
        "enabled": False,
    },
}

ENABLED_DECISION_TYPES = tuple(k for k, v in DECISION_TYPES.items() if v.get("enabled"))


def get_decision_label(decision_type: str) -> str:
    meta = DECISION_TYPES.get(decision_type, {})
    return str(meta.get("label") or decision_type.replace("_", " ").title())


def is_enabled(decision_type: str) -> bool:
    return bool(DECISION_TYPES.get(decision_type, {}).get("enabled"))
