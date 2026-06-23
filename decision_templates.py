"""Field definitions and completeness scoring for each decision type."""

from __future__ import annotations

from typing import Any

FieldSpec = dict[str, Any]

BET_FORMAT_OPTIONS = [
    "prediction_market",
    "decimal_multiplier",
    "moneyline_matchup",
    "percentage_implied",
    "spread_total",
]

MARKET_SUBTYPE_OPTIONS = [
    "",
    "prediction_market",
    "moneyline",
    "spread",
    "total",
    "spread_and_total",
]

PREDICTION_MARKET_BET_FIELDS: dict[str, FieldSpec] = {
    "title": {
        "label": "Market title",
        "required": True,
        "why": "Identifies what outcome you are betting on.",
        "input_type": "text",
        "editable": True,
    },
    "bet_format": {
        "label": "Bet format",
        "required": True,
        "why": "Determines which EV formula applies (¢ price vs multiplier vs %).",
        "input_type": "select",
        "options": BET_FORMAT_OPTIONS,
        "editable": True,
    },
    "market_subtype": {
        "label": "Market type (moneyline / spread / total / prediction)",
        "required": False,
        "why": "Spread/total markets may need a different side than moneyline.",
        "input_type": "select",
        "options": MARKET_SUBTYPE_OPTIONS,
        "editable": True,
    },
    "contract_side": {
        "label": "Side / team you are considering",
        "required": True,
        "why": "Which outcome you would bet on.",
        "input_type": "text",
        "editable": True,
    },
    "price": {
        "label": "Contract price (¢) — prediction markets",
        "required": False,
        "why": "Yes/No price in cents sets cost and implied probability.",
        "input_type": "number",
        "editable": True,
        "formats": ["prediction_market"],
    },
    "multiplier": {
        "label": "Payout multiplier (e.g. 1.93x)",
        "required": False,
        "why": "Decimal odds: break-even P = 1/multiplier.",
        "input_type": "number",
        "editable": True,
        "formats": ["decimal_multiplier", "moneyline_matchup", "spread_total"],
    },
    "implied_probability": {
        "label": "Market implied probability",
        "required": False,
        "derived": True,
        "why": "Computed from price or multiplier — shows market belief.",
        "input_type": "percent",
    },
    "payout": {
        "label": "Payout if correct ($ per contract)",
        "required": False,
        "derived": True,
        "why": "Usually $1 per contract on prediction markets.",
        "input_type": "number",
    },
    "cost": {
        "label": "Cost per contract ($)",
        "required": False,
        "derived": True,
        "why": "What you pay per share/contract.",
        "input_type": "number",
    },
    "volume": {
        "label": "Volume / liquidity",
        "required": False,
        "why": "Context for how tradable the market is — not direct EV input.",
        "input_type": "number",
        "editable": True,
    },
    "spread_total_markets": {
        "label": "Related spread/total markets count",
        "required": False,
        "why": "Signals multiple related lines on the same event.",
        "input_type": "number",
        "editable": True,
    },
    "stake": {
        "label": "Your stake ($)",
        "required": True,
        "why": "Needed for expected profit/loss and position sizing.",
        "input_type": "number",
        "allow_estimate": True,
        "editable": True,
    },
    "user_probability": {
        "label": "Your probability estimate",
        "required": True,
        "why": "EV and edge depend on your belief vs the market.",
        "input_type": "percent",
        "allow_estimate": True,
        "editable": True,
    },
    "expiration": {
        "label": "Expiration / close date",
        "required": False,
        "why": "Time horizon affects capital lock-up.",
        "input_type": "text",
        "editable": True,
    },
    "rules_summary": {
        "label": "Market rules summary",
        "required": False,
        "why": "Settlement rules can change what a win means.",
        "input_type": "text",
        "editable": True,
    },
    "risk_tolerance": {
        "label": "Risk tolerance",
        "required": False,
        "why": "Conservative sizing caps Kelly-style recommendations.",
        "input_type": "select",
        "options": ["conservative", "moderate", "aggressive"],
        "allow_estimate": True,
        "editable": True,
    },
}

DECISION_FIELD_TEMPLATES: dict[str, dict[str, FieldSpec]] = {
    "prediction_market_bet": PREDICTION_MARKET_BET_FIELDS,
}


def get_field_template(decision_type: str) -> dict[str, FieldSpec]:
    return DECISION_FIELD_TEMPLATES.get(decision_type, {})


def editable_fields(decision_type: str) -> list[str]:
    tpl = get_field_template(decision_type)
    return [k for k, spec in tpl.items() if spec.get("editable") and not spec.get("derived")]


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
    if isinstance(val, (list, dict)):
        return bool(val)
    return bool(val)


def _required_for_format(fields: dict[str, Any], key: str, spec: FieldSpec) -> bool:
    if not spec.get("required"):
        return False
    fmt = str(fields.get("bet_format") or "prediction_market")
    allowed = spec.get("formats")
    if allowed and fmt not in allowed:
        return False
    if key == "price" and fmt != "prediction_market":
        return False
    if key == "multiplier" and fmt in ("prediction_market", "percentage_implied"):
        return False
    if key == "contract_side":
        return True
    if key == "bet_format":
        return True
    if key == "title":
        return True
    if key in ("stake", "user_probability"):
        return True
    return bool(spec.get("required"))


def assess_completeness(
    decision_type: str,
    fields: dict[str, Any],
    *,
    user_provided: set[str] | None = None,
) -> dict[str, Any]:
    """Return extracted/missing/uncertain lists, completeness %, and confidence."""
    tpl = get_field_template(decision_type)
    user_provided = user_provided or set()
    uncertain = list(fields.get("uncertain_fields") or [])

    extracted: list[str] = []
    missing: list[str] = []
    assumptions: list[str] = []
    missing_required: list[str] = []

    bet_format = str(fields.get("bet_format") or "unknown")

    for key, spec in tpl.items():
        if spec.get("derived"):
            continue
        val = fields.get(key)
        if _has_value(val):
            extracted.append(key)
            if key in user_provided and spec.get("allow_estimate"):
                assumptions.append(key)
        elif _required_for_format(fields, key, spec):
            missing.append(key)
            missing_required.append(key)

    if bet_format == "prediction_market" and not _has_value(fields.get("price")):
        if "price" not in missing:
            missing.append("price")
            missing_required.append("price")
    elif bet_format in ("decimal_multiplier", "moneyline_matchup", "spread_total"):
        if not _has_value(fields.get("multiplier")) and not _has_value(fields.get("implied_probability")):
            if "multiplier" not in missing:
                missing.append("multiplier")
                missing_required.append("multiplier")
    elif bet_format == "percentage_implied":
        if not _has_value(fields.get("implied_probability")) and not _has_value(fields.get("contract_side")):
            if "contract_side" not in missing:
                missing.append("contract_side")
                missing_required.append("contract_side")

    req_keys = list(dict.fromkeys(missing_required + [k for k, s in tpl.items() if _required_for_format(fields, k, s)]))
    filled_req = sum(1 for k in req_keys if _has_value(fields.get(k)))
    completeness_pct = round(100 * filled_req / len(req_keys), 1) if req_keys else 100.0

    if missing_required or uncertain:
        confidence = "low" if missing_required else "medium"
    elif assumptions:
        confidence = "medium"
    elif completeness_pct >= 90:
        confidence = "high"
    else:
        confidence = "medium"

    return {
        "extracted": extracted,
        "missing": list(dict.fromkeys(missing)),
        "missing_required": list(dict.fromkeys(missing_required)),
        "uncertain": uncertain,
        "assumptions": assumptions,
        "completeness_pct": completeness_pct,
        "confidence": confidence,
        "can_solve": len(missing_required) == 0,
        "bet_format": bet_format,
    }


def field_label(decision_type: str, field_key: str) -> str:
    spec = get_field_template(decision_type).get(field_key, {})
    return str(spec.get("label") or field_key.replace("_", " ").title())


def field_why(decision_type: str, field_key: str) -> str:
    spec = get_field_template(decision_type).get(field_key, {})
    return str(spec.get("why") or "")


def clarification_questions(fields: dict[str, Any]) -> list[dict[str, str]]:
    """Targeted follow-up questions based on what's missing or ambiguous."""
    questions: list[dict[str, str]] = []
    fmt = str(fields.get("bet_format") or "")

    if not _has_value(fields.get("contract_side")):
        questions.append({
            "id": "contract_side",
            "question": "Which side or team are you considering?",
            "why": "EV depends on which outcome you would bet on.",
        })
    if not _has_value(fields.get("stake")):
        questions.append({
            "id": "stake",
            "question": "How much do you want to stake ($)?",
            "why": "Needed for total EV and risk sizing.",
        })
    if not _has_value(fields.get("user_probability")):
        questions.append({
            "id": "user_probability",
            "question": "What is your estimated true probability?",
            "why": "Your belief vs the market drives edge and EV.",
        })
    if fmt in ("decimal_multiplier", "moneyline_matchup") and not _has_value(fields.get("multiplier")):
        questions.append({
            "id": "multiplier",
            "question": "What payout multiplier applies to your side (e.g. 1.90x)?",
            "why": "Break-even probability = 1 / multiplier.",
        })
    if not fmt or fmt == "unknown":
        questions.append({
            "id": "bet_format",
            "question": "Is this a prediction market (¢ price), moneyline (%), spread, total, or multiplier odds?",
            "why": "Different formats use different EV formulas.",
        })
    if "which_multiplier" in (fields.get("uncertain_fields") or []):
        questions.append({
            "id": "multiplier",
            "question": "Multiple multipliers were found — which applies to your pick?",
            "why": "Each side may have a different payout.",
        })
    if not _has_value(fields.get("expiration")):
        questions.append({
            "id": "expiration",
            "question": "What time horizon or expiration applies?",
            "why": "Capital is locked until settlement.",
        })
    return questions
