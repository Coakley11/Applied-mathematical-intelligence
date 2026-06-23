"""Extract structured fields from imported bet/market text, CSV, and OCR."""

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
_PERCENT_LINE = re.compile(
    r"^(.+?)\s+(\d{1,2}(?:\.\d+)?)\s*%?\s*$",
    re.I,
)
_MULTIPLIER_LINE = re.compile(
    r"^(.+?)\s+(\d+(?:\.\d+)?)\s*x\s*$",
    re.I,
)
_STANDALONE_MULTIPLIER = re.compile(r"\b(\d+(?:\.\d+)?)\s*x\b", re.I)
_VOLUME = re.compile(
    r"(?:volume|vol\.?|liquidity)\s*[:\s]*\$?\s*([\d,]+(?:\.\d+)?)",
    re.I,
)
_SPREAD_TOTAL = re.compile(
    r"(?:spread|total|over/under|o/u).{0,40}(\d+)\s*markets?",
    re.I,
)
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


def _parse_volume(text: str) -> float | None:
    m = _VOLUME.search(text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _parse_team_options(lines: list[str]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for line in lines:
        m = _PERCENT_LINE.match(line.strip())
        if not m:
            continue
        name = m.group(1).strip()
        if len(name) < 2 or name.lower() in ("yes", "no", "volume"):
            continue
        try:
            pct = float(m.group(2))
        except ValueError:
            continue
        if not (1 <= pct <= 99):
            continue
        options.append({"name": name, "implied_pct": pct, "implied_probability": pct / 100.0})
    return options


def _parse_multipliers(text: str, lines: list[str]) -> list[dict[str, Any]]:
    mults: list[dict[str, Any]] = []
    seen: set[float] = set()
    for line in lines:
        m = _MULTIPLIER_LINE.match(line.strip())
        if m:
            name = m.group(1).strip()
            try:
                val = float(m.group(2))
            except ValueError:
                continue
            if 1.01 <= val <= 50 and val not in seen:
                mults.append({"name": name, "multiplier": val})
                seen.add(val)
    for m in _STANDALONE_MULTIPLIER.finditer(text):
        try:
            val = float(m.group(1))
        except ValueError:
            continue
        if 1.01 <= val <= 50 and val not in seen:
            mults.append({"name": "", "multiplier": val})
            seen.add(val)
    return mults


def detect_bet_format(fields: dict[str, Any], text: str = "") -> str:
    """Classify bet pricing format from extracted fields."""
    explicit = str(fields.get("bet_format") or "").strip()
    if explicit:
        return explicit

    lower = text.lower()
    if fields.get("yes_price") is not None or fields.get("no_price") is not None:
        return "prediction_market"
    if _STANDALONE_CENTS.search(text) or "kalshi" in lower:
        return "prediction_market"
    if fields.get("multiplier") or fields.get("multipliers"):
        if fields.get("team_options"):
            return "moneyline_matchup"
        return "decimal_multiplier"
    if fields.get("team_options"):
        return "percentage_implied"
    if "spread" in lower or "total" in lower:
        return "spread_total"
    if fields.get("price") is not None:
        return "prediction_market"
    return "unknown"


def _infer_title(lines: list[str], team_options: list[dict[str, Any]]) -> str:
    if len(team_options) >= 2:
        return f"{team_options[0]['name']} vs {team_options[1]['name']}"
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
        if _PERCENT_LINE.match(clean) or _MULTIPLIER_LINE.match(clean):
            continue
        if re.search(r"volume|spread|total", clean, re.I):
            continue
        return clean[:200]
    return lines[0][:200] if lines else "Imported market"


def _detect_market_subtype(text: str) -> str:
    lower = text.lower()
    if re.search(r"\bspread\b", lower) and re.search(r"\btotal\b", lower):
        return "spread_and_total"
    if re.search(r"\bspread\b", lower):
        return "spread"
    if re.search(r"\btotal\b|\bover/under\b|\bo/u\b", lower):
        return "total"
    if re.search(r"\bmoneyline\b|\bml\b", lower):
        return "moneyline"
    if re.search(r"\bprediction\s+market\b|kalshi|calci", lower):
        return "prediction_market"
    return ""


def parse_prediction_market_text(raw: str) -> dict[str, Any]:
    """Parse Kalshi/Calci-style pasted text or OCR output into bet fields."""
    text = str(raw or "").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    team_options = _parse_team_options(lines)
    multipliers = _parse_multipliers(text, lines)
    uncertain: list[str] = []

    fields: dict[str, Any] = {
        "title": _infer_title(lines, team_options),
        "bet_format": "",
        "market_subtype": _detect_market_subtype(text),
        "contract_side": "",
        "selected_option": "",
        "price": None,
        "yes_price": None,
        "no_price": None,
        "multiplier": None,
        "decimal_odds": None,
        "team_options": team_options,
        "multipliers": multipliers,
        "volume": _parse_volume(text),
        "spread_total_markets": None,
        "expiration": "",
        "rules_summary": "",
        "stake": None,
        "user_probability": None,
        "source_excerpt": text[:800],
        "uncertain_fields": uncertain,
        "ocr_corrected": False,
    }

    st_match = _SPREAD_TOTAL.search(text)
    if st_match:
        try:
            fields["spread_total_markets"] = int(st_match.group(1))
        except ValueError:
            pass

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

    if team_options and fields["price"] is None:
        fields["bet_format"] = "percentage_implied"
        if len(team_options) == 1:
            fields["selected_option"] = team_options[0]["name"]
            fields["contract_side"] = team_options[0]["name"]
            fields["implied_probability"] = team_options[0]["implied_probability"]
        elif len(team_options) >= 2:
            uncertain.append("contract_side")
            uncertain.append("which_team")

    if multipliers:
        if not fields["bet_format"]:
            fields["bet_format"] = "moneyline_matchup" if team_options else "decimal_multiplier"
        named = [m for m in multipliers if m.get("name")]
        if len(named) == 1:
            fields["multiplier"] = named[0]["multiplier"]
            fields["decimal_odds"] = named[0]["multiplier"]
            fields["selected_option"] = named[0]["name"]
            if not fields["contract_side"]:
                fields["contract_side"] = named[0]["name"]
        elif len(multipliers) == 1:
            fields["multiplier"] = multipliers[0]["multiplier"]
            fields["decimal_odds"] = multipliers[0]["multiplier"]
        else:
            uncertain.append("multiplier")
            uncertain.append("which_multiplier")

    if not fields["bet_format"]:
        fields["bet_format"] = detect_bet_format(fields, text)

    if not fields["contract_side"]:
        lower = text.lower()
        if "buy yes" in lower or "yes contract" in lower:
            fields["contract_side"] = "Yes"
        elif "buy no" in lower or "no contract" in lower:
            fields["contract_side"] = "No"
        elif team_options and len(team_options) == 1:
            fields["contract_side"] = team_options[0]["name"]
        elif fields["bet_format"] == "prediction_market":
            fields["contract_side"] = "Yes"
        elif team_options:
            uncertain.append("contract_side")
        else:
            fields["contract_side"] = ""

    if fields["price"] is None and fields["yes_price"] is not None:
        fields["price"] = (
            fields["yes_price"] if fields["contract_side"] == "Yes" else fields.get("no_price")
        )

    if fields["bet_format"] == "percentage_implied" and fields.get("contract_side") and team_options:
        for opt in team_options:
            if opt["name"].lower() == str(fields["contract_side"]).lower():
                fields["implied_probability"] = opt["implied_probability"]
                break

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

    if fields["bet_format"] in ("decimal_multiplier", "moneyline_matchup") and not fields.get("multiplier"):
        uncertain.append("multiplier")
    if fields["bet_format"] == "percentage_implied" and not fields.get("implied_probability"):
        uncertain.append("implied_probability")

    fields["uncertain_fields"] = list(dict.fromkeys(uncertain))
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

    mult_raw = pick("multiplier", "decimal_odds", "odds")
    mult_val = None
    if mult_raw is not None:
        try:
            mult_val = float(str(mult_raw).replace("x", ""))
        except ValueError:
            pass

    fields: dict[str, Any] = {
        "title": str(pick("title", "market", "market_title", "question") or "Imported market"),
        "bet_format": str(pick("bet_format", "format") or ""),
        "contract_side": str(pick("side", "contract_side", "position", "team") or "Yes"),
        "price": _normalize_price_cents(pick("price", "yes_price", "contract_price", "cents")),
        "yes_price": _normalize_price_cents(pick("yes_price", "yes")),
        "no_price": _normalize_price_cents(pick("no_price", "no")),
        "multiplier": mult_val,
        "decimal_odds": mult_val,
        "volume": None,
        "expiration": str(pick("expiration", "close_date", "date") or ""),
        "rules_summary": str(pick("rules", "rules_summary") or ""),
        "stake": None,
        "user_probability": None,
        "team_options": [],
        "multipliers": [],
        "uncertain_fields": [],
        "source_excerpt": text[:500],
    }

    vol_raw = pick("volume", "liquidity")
    if vol_raw is not None:
        try:
            fields["volume"] = float(str(vol_raw).replace(",", ""))
        except ValueError:
            pass

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

    if not fields["bet_format"]:
        fields["bet_format"] = detect_bet_format(fields, text)

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


def apply_field_edits(fields: dict[str, Any], edits: dict[str, Any]) -> dict[str, Any]:
    """Merge user corrections and re-enrich derived values."""
    merged = dict(fields)
    merged.update(edits)
    if edits.get("contract_side") and merged.get("team_options"):
        for opt in merged["team_options"]:
            if str(opt.get("name", "")).lower() == str(edits["contract_side"]).lower():
                merged["selected_option"] = opt["name"]
                merged["implied_probability"] = opt.get("implied_probability")
                break
    if edits.get("multiplier"):
        merged["decimal_odds"] = float(edits["multiplier"])
    merged["ocr_corrected"] = True
    return enrich_bet_fields(merged)
