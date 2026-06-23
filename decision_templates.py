"""Field definitions and completeness scoring for each decision type."""

from __future__ import annotations

from typing import Any

FieldSpec = dict[str, Any]

PREDICTION_MARKET_BET_FIELDS: dict[str, FieldSpec] = {
    "title": {
        "label": "Market title",
        "required": True,
        "why": "Identifies what outcome you are betting on.",
        "input_type": "text",
    },
    "contract_side": {
        "label": "Contract side (Yes / No)",
        "required": True,
        "why": "Which side you would buy determines payout direction.",
        "input_type": "select",
        "options": ["Yes", "No"],
    },
    "price": {
        "label": "Contract price (¢ or $)",
        "required": True,
        "why": "Price sets cost and market-implied probability.",
        "input_type": "number",
    },
    "implied_probability": {
        "label": "Market implied probability",
        "required": False,
        "derived": True,
        "why": "Computed from price — shows what the market believes.",
        "input_type": "number",
    },
    "payout": {
        "label": "Payout if correct ($ per contract)",
        "required": False,
        "derived": True,
        "why": "Usually $1 per contract minus cost on prediction markets.",
        "input_type": "number",
    },
    "cost": {
        "label": "Cost per contract ($)",
        "required": False,
        "derived": True,
        "why": "What you pay per share/contract.",
        "input_type": "number",
    },
    "stake": {
        "label": "Your stake ($)",
        "required": True,
        "why": "Needed for expected profit/loss and position sizing.",
        "input_type": "number",
        "allow_estimate": True,
    },
    "user_probability": {
        "label": "Your probability estimate",
        "required": True,
        "why": "EV and edge depend on your belief vs the market.",
        "input_type": "percent",
        "allow_estimate": True,
    },
    "expiration": {
        "label": "Expiration / close date",
        "required": False,
        "why": "Time horizon affects capital lock-up and information value.",
        "input_type": "text",
    },
    "rules_summary": {
        "label": "Market rules summary",
        "required": False,
        "why": "Settlement rules can change what 'yes' actually means.",
        "input_type": "text",
    },
    "risk_tolerance": {
        "label": "Risk tolerance",
        "required": False,
        "why": "Conservative sizing caps Kelly-style recommendations.",
        "input_type": "select",
        "options": ["conservative", "moderate", "aggressive"],
        "allow_estimate": True,
    },
}

DECISION_FIELD_TEMPLATES: dict[str, dict[str, FieldSpec]] = {
    "prediction_market_bet": PREDICTION_MARKET_BET_FIELDS,
}


def get_field_template(decision_type: str) -> dict[str, FieldSpec]:
    return DECISION_FIELD_TEMPLATES.get(decision_type, {})


def required_fields(decision_type: str) -> list[str]:
    return [k for k, spec in get_field_template(decision_type).items() if spec.get("required")]


def optional_fields(decision_type: str) -> list[str]:
    tpl = get_field_template(decision_type)
    return [k for k, spec in tpl.items() if not spec.get("required") and not spec.get("derived")]


def derived_fields(decision_type: str) -> list[str]:
    tpl = get_field_template(decision_type)
    return [k for k, spec in tpl.items() if spec.get("derived")]


def _has_value(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    if isinstance(val, (int, float)):
        return True
    return bool(val)


def assess_completeness(
    decision_type: str,
    fields: dict[str, Any],
    *,
    user_provided: set[str] | None = None,
) -> dict[str, Any]:
    """Return extracted/missing lists, completeness %, and confidence label."""
    tpl = get_field_template(decision_type)
    user_provided = user_provided or set()

    extracted: list[str] = []
    missing: list[str] = []
    assumptions: list[str] = []
    missing_required: list[str] = []

    for key, spec in tpl.items():
        if spec.get("derived"):
            continue
        val = fields.get(key)
        if _has_value(val):
            extracted.append(key)
            if key in user_provided and spec.get("allow_estimate"):
                assumptions.append(key)
        elif spec.get("required"):
            missing.append(key)
            missing_required.append(key)

    req = [k for k, s in tpl.items() if s.get("required") and not s.get("derived")]
    filled_req = sum(1 for k in req if _has_value(fields.get(k)))
    completeness_pct = round(100 * filled_req / len(req), 1) if req else 100.0

    if missing_required:
        confidence = "low"
    elif assumptions:
        confidence = "medium"
    elif completeness_pct >= 90:
        confidence = "high"
    else:
        confidence = "medium"

    return {
        "extracted": extracted,
        "missing": missing,
        "missing_required": missing_required,
        "assumptions": assumptions,
        "completeness_pct": completeness_pct,
        "confidence": confidence,
        "can_solve": len(missing_required) == 0,
    }


def field_label(decision_type: str, field_key: str) -> str:
    spec = get_field_template(decision_type).get(field_key, {})
    return str(spec.get("label") or field_key.replace("_", " ").title())


def field_why(decision_type: str, field_key: str) -> str:
    spec = get_field_template(decision_type).get(field_key, {})
    return str(spec.get("why") or "")
