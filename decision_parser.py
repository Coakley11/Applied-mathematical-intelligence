"""Extract structured fields from imported bet/market text and CSV."""

from __future__ import annotations

import csv
import io
import re
from typing import Any

from decision_math import enrich_bet_fields

_TITLE_SKIP = re.compile(
    r"^(kalshi|calci|market|event|buy|sell|order|position)\b",
    re.I,
)
_YES_NO_PRICE = re.compile(
    r"\b(yes|no)\b[:\s]*\$?\s*(\d{1,2})(?:\s*¢|\s*cents?|\s*%|\s*\$0?\.(\d{2}))?",
    re.I,
)
_STANDALONE_CENTS = re.compile(r"(\d{1,2})\s*¢", re.I)
_DOLLAR_PRICE = re.compile(r"\$\s*0?\.(\d{2})\b")
_PERCENT_PRICE = re.compile(r"(\d{1,3})\s*%")
_EXPIRATION = re.compile(
    r"(?:expires?|closes?|settlement|end(?:s)?)\s*[:\s]*([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})",
    re.I,
)
_STAKE_INLINE = re.compile(
    r"(?:stake|bet(?:ting)?|wager|invest(?:ing)?|amount)\s*[:\s]*\$?\s*(\d+(?:\.\d{1,2})?)",
    re.I,
)
_USER_PROB = re.compile(
    r"(?:my\s+(?:estimate|probability|chance)|i\s+think|believe|true\s+(?:prob|probability|chance))\s*[:\s]*(\d{1,3})\s*%?",
    re.I,
)
_RULES = re.compile(r"(?:rules?|settlement|resolution)\s*[:\s]*(.+)", re.I)


def _normalize_price_cents(raw: str | int | float | None) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        v = float(raw)
        if 0 < v <= 1:
            return round(v * 100, 2)
        if 0 < v <= 100:
            return round(v, 2)
        return None
    text = str(raw).strip().replace("$", "")
    if not text:
        return None
    if text.endswith("¢") or "cent" in text.lower():
        m = re.search(r"(\d{1,2})", text)
        return float(m.group(1)) if m else None
    if text.startswith("0."):
        return round(float(text) * 100, 2)
    try:
        v = float(text)
        if 0 < v <= 1:
            return round(v * 100, 2)
        if 0 < v <= 100:
            return round(v, 2)
    except ValueError:
        pass
    return None


def _infer_title(lines: list[str]) -> str:
    for line in lines:
        clean = line.strip()
        if len(clean) < 8:
            continue
        if _TITLE_SKIP.match(clean):
            continue
        if re.match(r"^https?://", clean):
            continue
        if re.fullmatch(r"(yes|no)\s*:?\s*\d+", clean, re.I):
            continue
        return clean[:200]
    return lines[0][:200] if lines else "Imported market"


def parse_prediction_market_text(raw: str) -> dict[str, Any]:
    """Parse Kalshi/Calci-style pasted text into bet fields."""
    text = str(raw or "").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    fields: dict[str, Any] = {
        "title": _infer_title(lines),
        "contract_side": "",
        "price": None,
        "yes_price": None,
        "no_price": None,
        "expiration": "",
        "rules_summary": "",
        "stake": None,
        "user_probability": None,
        "source_excerpt": text[:500],
    }

    for m in _YES_NO_PRICE.finditer(text):
        side = m.group(1).capitalize()
        cents = _normalize_price_cents(m.group(2))
        if m.group(3):
            cents = _normalize_price_cents(f"0.{m.group(3)}")
        if side == "Yes":
            fields["yes_price"] = cents
        else:
            fields["no_price"] = cents
        if not fields["contract_side"] and cents is not None:
            fields["contract_side"] = side
            fields["price"] = cents

    if fields["price"] is None:
        for m in _STANDALONE_CENTS.finditer(text):
            fields["price"] = float(m.group(1))
            break

    if fields["price"] is None:
        dm = _DOLLAR_PRICE.search(text)
        if dm:
            fields["price"] = float(dm.group(1))

    if fields["price"] is None:
        pm = _PERCENT_PRICE.search(text)
        if pm:
            fields["price"] = float(pm.group(1))

    if not fields["contract_side"]:
        lower = text.lower()
        if "buy yes" in lower or "yes contract" in lower:
            fields["contract_side"] = "Yes"
        elif "buy no" in lower or "no contract" in lower:
            fields["contract_side"] = "No"
        else:
            fields["contract_side"] = "Yes"

    if fields["price"] is None and fields["yes_price"] is not None:
        fields["price"] = fields["yes_price"] if fields["contract_side"] == "Yes" else fields.get("no_price")

    em = _EXPIRATION.search(text)
    if em:
        fields["expiration"] = em.group(1).strip()

    rm = _RULES.search(text)
    if rm:
        fields["rules_summary"] = rm.group(1).strip()[:300]

    sm = _STAKE_INLINE.search(text)
    if sm:
        fields["stake"] = float(sm.group(1))

    um = _USER_PROB.search(text)
    if um:
        fields["user_probability"] = float(um.group(1)) / 100.0

    return enrich_bet_fields(fields)


def parse_prediction_market_csv(raw: str) -> dict[str, Any]:
    """Parse a simple CSV with bet columns."""
    text = str(raw or "").strip()
    if not text:
        return parse_prediction_market_text("")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return parse_prediction_market_text(text)

    row = rows[0]
    norm = {k.strip().lower().replace(" ", "_"): v for k, v in row.items() if k}

    def pick(*keys: str) -> Any:
        for k in keys:
            if k in norm and str(norm[k]).strip():
                return norm[k]
        return None

    fields: dict[str, Any] = {
        "title": str(pick("title", "market", "market_title", "question") or "Imported market"),
        "contract_side": str(pick("side", "contract_side", "position") or "Yes").capitalize(),
        "price": _normalize_price_cents(pick("price", "yes_price", "contract_price", "cents")),
        "yes_price": _normalize_price_cents(pick("yes_price", "yes")),
        "no_price": _normalize_price_cents(pick("no_price", "no")),
        "expiration": str(pick("expiration", "close_date", "date") or ""),
        "rules_summary": str(pick("rules", "rules_summary") or ""),
        "stake": None,
        "user_probability": None,
        "source_excerpt": text[:500],
    }

    stake_raw = pick("stake", "amount", "wager")
    if stake_raw is not None:
        try:
            fields["stake"] = float(str(stake_raw).replace("$", ""))
        except ValueError:
            pass

    prob_raw = pick("user_probability", "probability", "my_probability", "estimate")
    if prob_raw is not None:
        try:
            p = float(str(prob_raw).replace("%", ""))
            fields["user_probability"] = p / 100.0 if p > 1 else p
        except ValueError:
            pass

    if fields["price"] is None:
        if fields["contract_side"] == "Yes" and fields["yes_price"] is not None:
            fields["price"] = fields["yes_price"]
        elif fields["contract_side"] == "No" and fields["no_price"] is not None:
            fields["price"] = fields["no_price"]

    return enrich_bet_fields(fields)


def extract_fields(
    raw_input: str,
    decision_type: str,
    *,
    source_type: str = "text",
) -> dict[str, Any]:
    """Dispatch extraction by decision type and source format."""
    if decision_type == "prediction_market_bet":
        if source_type == "csv":
            return parse_prediction_market_csv(raw_input)
        return parse_prediction_market_text(raw_input)
    return {"title": raw_input[:120], "source_excerpt": raw_input[:500]}
