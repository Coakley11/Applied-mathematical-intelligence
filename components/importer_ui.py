"""AMI Problem Importer — paste, screenshot, extract, review, clarify, analyze, save."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import streamlit as st

from components.clipboard_image_paste import (
    clipboard_paste_available,
    data_url_to_bytes,
    extension_for_mime,
    image_bytes_meta,
    render_clipboard_paste_zone,
    render_paste_button,
)
from decision_history import delete_import_entry, list_import_history, save_import_entry
from decision_math import enrich_bet_fields, enrich_poker_fields, solve_decision
from decision_ocr import extract_text_from_image, ocr_availability, ocr_fallback_message
from decision_parser import apply_field_edits, extract_fields
from decision_registry import DECISION_TYPES, ENABLED_DECISION_TYPES, get_decision_label, is_enabled
from decision_router import route_imported_problem
from decision_templates import (
    BET_FORMAT_OPTIONS,
    POKER_ACTION_OPTIONS,
    POSITION_OPTIONS,
    STREET_OPTIONS,
    assess_completeness,
    clarification_questions,
    field_label,
    field_why,
    get_field_template,
)


def render_ami_importer() -> None:
    """Full importer workflow."""
    st.markdown("#### AMI Problem Importer")
    st.caption(
        "Paste prediction-market text, a poker hand spot, paste a screenshot (Ctrl+V), upload, or enter manually. "
        "Review extracted fields, fill gaps, then run decision math — not gambling advice."
    )

    _init_importer_state()
    ocr_info = ocr_availability()
    if not ocr_info.get("ready"):
        st.caption(f"ℹ️ {ocr_info['note']}")

    tab_import, tab_history = st.tabs(["Import & analyze", "History"])
    with tab_import:
        _render_import_workflow()
    with tab_history:
        _render_history_panel()


def _init_importer_state() -> None:
    st.session_state.setdefault("imp_stage", "import")
    st.session_state.setdefault("imp_fields", {})
    st.session_state.setdefault("imp_user_provided", set())
    st.session_state.setdefault("imp_decision_type", "prediction_market_bet")
    st.session_state.setdefault("imp_source_type", "text")
    st.session_state.setdefault("imp_raw_input", "")
    st.session_state.setdefault("imp_review_confirmed", False)


def _render_import_workflow() -> None:
    stage = st.session_state.get("imp_stage", "import")

    st.markdown("**1 · Import**")
    source = st.radio(
        "Input method",
        ["Paste text", "Screenshot / image", "Upload CSV", "Manual entry"],
        horizontal=True,
        key="imp_source_radio",
    )
    source_map = {
        "Paste text": "text",
        "Screenshot / image": "image",
        "Upload CSV": "csv",
        "Manual entry": "manual",
    }
    source_type = source_map[source]
    st.session_state["imp_source_type"] = source_type

    raw_input = ""
    if source == "Paste text":
        raw_input = st.text_area(
            "Paste bet / market text",
            value=st.session_state.get("imp_paste_buffer", ""),
            height=140,
            placeholder=(
                "Prediction market:\nWill the Knicks make the playoffs?\nYes: 42¢  No: 58¢\n\n"
                "Poker hand:\nTexas Hold'em. Hero has Ah Kh. Board: Qh Jh 2c. Pot $100. "
                "Villain bets $50. Call $50. Estimate equity 40%."
            ),
            key="imp_paste_input",
        )
    elif source == "Screenshot / image":
        raw_input = _render_image_import()
    elif source == "Upload CSV":
        uploaded = st.file_uploader("CSV file", type=["csv"], key="imp_csv_upload")
        if uploaded is not None:
            raw_input = uploaded.read().decode("utf-8", errors="replace")
            st.code(raw_input[:500], language="csv")
        else:
            st.caption("Columns: title, side, price, multiplier, stake, user_probability, volume")
    else:
        raw_input = _render_manual_entry(hint)

    type_options = list(ENABLED_DECISION_TYPES) + [k for k in DECISION_TYPES if not is_enabled(k)]
    type_labels = [f"{get_decision_label(t)}{' (coming soon)' if not is_enabled(t) else ''}" for t in type_options]
    selected_idx = st.selectbox(
        "Decision type (auto-detect or override)",
        range(len(type_options)),
        format_func=lambda i: type_labels[i],
        key="imp_type_select",
    )
    hint = type_options[selected_idx] if is_enabled(type_options[selected_idx]) else ""

    col_a, col_b = st.columns(2)
    with col_a:
        extract_clicked = st.button("Extract & route", type="primary", key="imp_extract_btn")
    with col_b:
        reset_clicked = st.button("Reset", key="imp_reset_btn")

    if reset_clicked:
        for k in list(st.session_state.keys()):
            if str(k).startswith("imp_"):
                del st.session_state[k]
        _init_importer_state()
        st.rerun()

    if extract_clicked or stage != "import":
        if extract_clicked:
            if not raw_input.strip() and source not in ("Manual entry", "Screenshot / image"):
                st.warning("Paste or upload content first.")
                return
            if source == "Manual entry" and not raw_input.strip():
                st.warning("Submit the manual entry form first.")
                return
            if source == "Screenshot / image" and not raw_input.strip() and not st.session_state.get("imp_image_bytes"):
                st.warning("Paste a screenshot (Ctrl+V), upload an image, or provide OCR/pasted text.")
                return

            route = route_imported_problem(raw_input, source_type=source_type, hint=hint)
            dtype = route["decision_type"]
            if not is_enabled(dtype):
                st.error(f"{get_decision_label(dtype)} is not available yet.")
                return

            fields = extract_fields(raw_input, dtype, source_type="text" if source_type == "image" else source_type)
            st.session_state["imp_raw_input"] = raw_input
            st.session_state["imp_decision_type"] = dtype
            st.session_state["imp_fields"] = fields
            st.session_state["imp_route"] = route
            st.session_state["imp_user_provided"] = set()
            st.session_state["imp_analysis"] = None
            st.session_state["imp_review_confirmed"] = False
            st.session_state["imp_stage"] = "review"

        _render_post_extract()


def _apply_import_image(
    image_bytes: bytes,
    *,
    filename: str,
    mime: str,
    source: str,
    auto_ocr: bool = True,
) -> None:
    """Store image in session and optionally run OCR immediately."""
    if not image_bytes:
        return
    meta = image_bytes_meta(image_bytes, filename=filename, mime=mime, source=source)
    img_hash = meta.get("sha256") or str(hash(image_bytes))
    try:
        from decision_ocr import image_metadata

        meta = {**meta, **image_metadata(image_bytes, filename=filename, mime=mime)}
        img_hash = meta.get("sha256", img_hash)
    except Exception:
        pass

    prev_hash = str(st.session_state.get("imp_image_hash") or "")
    st.session_state["imp_image_bytes"] = image_bytes
    st.session_state["imp_image_meta"] = meta
    st.session_state["imp_image_hash"] = img_hash
    st.session_state["imp_image_source"] = source

    if auto_ocr and img_hash != prev_hash:
        ocr_result = extract_text_from_image(image_bytes, filename=filename, mime=mime)
        st.session_state["imp_ocr_result"] = ocr_result
        if ocr_result.get("success"):
            st.session_state["imp_image_manual_text"] = ocr_result.get("text", "")
        st.session_state["imp_ocr_auto_ran"] = True


def _render_image_import() -> str:
    """Screenshot clipboard paste, optional paste button, file upload, OCR + text fallback."""
    clip_info = clipboard_paste_available()
    tab_clipboard, tab_upload = st.tabs(["Clipboard paste", "File upload"])

    with tab_clipboard:
        st.caption(clip_info["note"])
        st.markdown("**Snipping Tool workflow:** capture → Copy → click box below → **Ctrl+V**")
        data_url = render_clipboard_paste_zone(
            label="Click here, then Ctrl+V to paste screenshot",
            key="imp_clipboard_paste_zone",
        )
        if data_url:
            image_bytes, mime = data_url_to_bytes(data_url)
            if image_bytes:
                ext = extension_for_mime(mime)
                _apply_import_image(
                    image_bytes,
                    filename=f"clipboard-paste.{ext}",
                    mime=mime,
                    source="clipboard_paste",
                    auto_ocr=True,
                )

        paste_btn = render_paste_button(key="imp_paste_button")
        if paste_btn:
            image_bytes, mime, filename = paste_btn
            _apply_import_image(
                image_bytes,
                filename=filename,
                mime=mime,
                source="clipboard_button",
                auto_ocr=True,
            )
        elif not clip_info["paste_button"]:
            st.caption("Optional: `pip install streamlit-paste-button` adds a clipboard button fallback.")

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload screenshot or photo",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            key="imp_image_upload",
        )
        if uploaded is not None:
            upload_bytes = uploaded.getvalue()
            upload_hash = str(hash(upload_bytes))
            if upload_hash != str(st.session_state.get("imp_upload_hash") or ""):
                st.session_state["imp_upload_hash"] = upload_hash
                _apply_import_image(
                    upload_bytes,
                    filename=uploaded.name,
                    mime=uploaded.type or "image/png",
                    source="file_upload",
                    auto_ocr=True,
                )

    image_bytes = st.session_state.get("imp_image_bytes")
    image_meta = st.session_state.get("imp_image_meta") or {}
    if image_bytes:
        src = image_meta.get("source", "image")
        st.image(image_bytes, caption=f"Market screenshot ({src})", use_container_width=True)
        col_ocr, col_clear = st.columns(2)
        with col_ocr:
            if st.button("Run OCR on image", key="imp_ocr_btn"):
                ocr_result = extract_text_from_image(
                    image_bytes,
                    filename=str(image_meta.get("filename") or "screenshot.png"),
                    mime=str(image_meta.get("mime") or "image/png"),
                )
                st.session_state["imp_ocr_result"] = ocr_result
                if ocr_result.get("success"):
                    st.session_state["imp_image_manual_text"] = ocr_result.get("text", "")
                    st.success(f"OCR extracted {len(ocr_result['text'])} characters.")
                else:
                    st.warning(ocr_fallback_message(ocr_result))
        with col_clear:
            if st.button("Clear image", key="imp_clear_image_btn"):
                for k in (
                    "imp_image_bytes", "imp_image_meta", "imp_image_hash", "imp_image_source",
                    "imp_ocr_result", "imp_upload_hash", "imp_ocr_auto_ran",
                ):
                    st.session_state.pop(k, None)
                st.rerun()

        ocr_result = st.session_state.get("imp_ocr_result") or {}
        if st.session_state.get("imp_ocr_auto_ran"):
            if ocr_result.get("success"):
                st.caption("OCR ran automatically on paste/upload.")
            else:
                st.warning(ocr_fallback_message(ocr_result))

    ocr_result = st.session_state.get("imp_ocr_result") or {}
    ocr_text = str(ocr_result.get("text") or "")

    manual_label = "Paste or correct visible text from screenshot"
    if ocr_text:
        manual_label = "Review / correct OCR text (or paste if OCR failed)"

    corrected = st.text_area(
        manual_label,
        value=ocr_text or st.session_state.get("imp_image_manual_text", ""),
        height=160,
        placeholder="Paste what you see: team names, %, multipliers, volume, Yes/No prices…",
        key="imp_image_text_area",
    )
    st.session_state["imp_image_manual_text"] = corrected
    st.session_state["imp_extracted_text"] = corrected
    return corrected.strip()


def _render_manual_entry(hint: str = "") -> str:
    if hint == "poker_hand_decision":
        with st.form("imp_poker_manual_form", border=True):
            st.markdown("**Manual poker hand entry**")
            p_game = st.selectbox("Game", ["texas_holdem", "omaha"], key="imp_p_game")
            p_street = st.selectbox("Street", STREET_OPTIONS, index=1, key="imp_p_street")
            p_hero = st.text_input("Hero hand", value="Ah Kh", key="imp_p_hero")
            p_board = st.text_input("Board", value="", key="imp_p_board")
            p_pot = st.number_input("Pot ($)", min_value=0.0, value=100.0, key="imp_p_pot")
            p_vbet = st.number_input("Villain bet ($)", min_value=0.0, value=50.0, key="imp_p_vbet")
            p_call = st.number_input("Amount to call ($)", min_value=0.0, value=50.0, key="imp_p_call")
            p_eq = st.slider("Equity estimate (%)", 5, 95, 40, key="imp_p_eq")
            if st.form_submit_button("Use manual entry"):
                parts = [
                    "Texas Hold'em" if p_game == "texas_holdem" else "Omaha",
                    f"Hero has {p_hero}.",
                ]
                if p_board.strip():
                    parts.append(f"Board: {p_board}.")
                parts.append(p_street.capitalize() + ".")
                parts.append(f"Pot ${p_pot:.0f}. Villain bets ${p_vbet:.0f}. Call ${p_call:.0f}.")
                parts.append(f"Estimate equity {p_eq}%.")
                st.session_state["imp_manual_raw"] = "\n".join(parts)
        return st.session_state.get("imp_manual_raw", "")

    with st.form("imp_manual_form", border=True):
        st.markdown("**Manual bet entry**")
        m_format = st.selectbox("Bet format", BET_FORMAT_OPTIONS, key="imp_m_format")
        m_title = st.text_input("Market title", key="imp_m_title")
        m_side = st.text_input("Side / team", value="Yes", key="imp_m_side")
        m_price = st.number_input("Price (¢) — prediction markets", min_value=0.0, max_value=99.0, value=0.0, key="imp_m_price")
        m_mult = st.number_input("Multiplier (e.g. 1.90) — decimal odds", min_value=0.0, value=0.0, step=0.01, key="imp_m_mult")
        m_stake = st.number_input("Proposed stake ($)", min_value=1.0, value=100.0, key="imp_m_stake")
        m_bankroll = st.number_input("Bankroll ($)", min_value=0.0, value=0.0, step=50.0, key="imp_m_bankroll")
        m_prob = st.slider("Your probability (%)", 5, 95, 50, key="imp_m_prob")
        if st.form_submit_button("Use manual entry"):
            parts = [m_title, f"side: {m_side}", f"stake: ${m_stake:.0f}", f"my estimate: {m_prob}%"]
            if m_bankroll > 0:
                parts.append(f"bankroll: ${m_bankroll:.0f}")
            if m_format == "prediction_market" and m_price > 0:
                parts.insert(1, f"{m_side}: {m_price:.0f}¢")
            if m_mult > 1:
                parts.insert(2, f"{m_side} {m_mult:.2f}x")
            raw = "\n".join(parts)
            st.session_state["imp_manual_raw"] = raw
    return st.session_state.get("imp_manual_raw", "")


def _enrich_fields(dtype: str, fields: dict[str, Any]) -> dict[str, Any]:
    if dtype == "poker_hand_decision":
        return enrich_poker_fields(fields)
    return enrich_bet_fields(fields)


def _render_post_extract() -> None:
    fields = dict(st.session_state.get("imp_fields") or {})
    dtype = str(st.session_state.get("imp_decision_type") or "prediction_market_bet")
    raw_provided = st.session_state.get("imp_user_provided") or set()
    user_provided: set[str] = set(raw_provided) if not isinstance(raw_provided, set) else raw_provided
    stage = st.session_state.get("imp_stage", "review")

    fields = _enrich_fields(dtype, fields)

    st.markdown("---")
    st.markdown("**2 · Extract**")
    route = st.session_state.get("imp_route") or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Decision type", get_decision_label(dtype))
    if dtype == "poker_hand_decision":
        c2.metric("Street", str(fields.get("street") or "—").replace("_", " "))
    else:
        c2.metric("Bet format", str(fields.get("bet_format") or "—").replace("_", " "))
    c3.metric("Route confidence", f"{float(route.get('confidence', 0)):.0%}")
    c4.metric("OCR", "yes" if st.session_state.get("imp_ocr_result", {}).get("success") else "n/a")
    if st.session_state.get("imp_image_meta", {}).get("source") == "clipboard_paste":
        st.caption("Image source: clipboard paste (Ctrl+V)")

    _render_extracted_summary(fields, dtype)

    st.markdown("**3 · Review & edit parsed fields**")
    st.caption("Correct anything OCR or parsing got wrong before analysis.")
    if dtype == "poker_hand_decision":
        fields = _render_poker_field_review_form(fields)
    else:
        fields = _render_field_review_form(dtype, fields)
    st.session_state["imp_fields"] = fields
    fields = _enrich_fields(dtype, fields)

    completeness = assess_completeness(dtype, fields, user_provided=user_provided)

    st.markdown("**4 · Missing information & confidence**")
    _render_confidence_panel(completeness, dtype, fields)

    if completeness.get("missing_required"):
        _render_clarification_form(dtype, fields, completeness["missing_required"], user_provided, fields)
        fields = _enrich_fields(dtype, dict(st.session_state.get("imp_fields") or {}))
        user_provided = set(st.session_state.get("imp_user_provided") or set())
        completeness = assess_completeness(dtype, fields, user_provided=user_provided)
    elif completeness.get("can_solve"):
        st.success("All required fields present — ready to analyze.")

    st.markdown("---")
    st.markdown("**5 · Analyze**")
    can_solve = completeness.get("can_solve", False)
    if st.button("Run decision analysis", type="primary", disabled=not can_solve, key="imp_solve_btn"):
        analysis = solve_decision(dtype, fields)
        st.session_state["imp_analysis"] = analysis
        st.session_state["imp_stage"] = "results"

    analysis = st.session_state.get("imp_analysis")
    if analysis and analysis.get("verdict") != "incomplete":
        if dtype == "poker_hand_decision":
            _render_poker_analysis_results(fields, analysis, completeness)
        else:
            _render_analysis_results(dtype, fields, analysis, completeness)

        st.markdown("---")
        st.markdown("**6 · Save**")
        notes = st.text_input("Notes (optional)", key="imp_save_notes")
        if st.button("Save to history", key="imp_save_btn"):
            entry = save_import_entry(
                source_type=str(st.session_state.get("imp_source_type") or "text"),
                decision_type=dtype,
                raw_input=str(st.session_state.get("imp_raw_input") or ""),
                fields=fields,
                analysis=analysis,
                completeness=completeness,
                user_notes=notes,
                image_meta=st.session_state.get("imp_image_meta"),
                ocr_text=str((st.session_state.get("imp_ocr_result") or {}).get("text") or ""),
                corrected_fields=fields if fields.get("ocr_corrected") else None,
            )
            st.success(f"Saved — {entry['id'][:8]}…")
            try:
                from applied_intelligence_activity import log_problem_solved

                log_problem_solved(
                    topic=str(fields.get("title") or "Imported problem"),
                    area="importer",
                    interactive=dtype,
                )
            except Exception:
                pass
    elif analysis and analysis.get("verdict") == "incomplete":
        st.warning(analysis.get("explanation", {}).get("summary", "Complete missing fields first."))


def _render_extracted_summary(fields: dict[str, Any], dtype: str) -> None:
    with st.expander("Raw extraction summary", expanded=False):
        if dtype == "poker_hand_decision":
            if fields.get("hero_hand"):
                st.markdown(f"**Hero:** {fields['hero_hand']}")
            if fields.get("board"):
                st.markdown(f"**Board:** {fields['board']}")
            if fields.get("pot_size") is not None:
                st.metric("Pot", f"${float(fields['pot_size']):,.2f}")
            if fields.get("amount_to_call") is not None:
                st.metric("To call", f"${float(fields['amount_to_call']):,.2f}")
            if fields.get("hero_equity") is not None:
                eq = float(fields["hero_equity"])
                st.metric("Equity est.", f"{eq * 100 if eq <= 1 else eq:.0f}%")
        if fields.get("team_options"):
            st.markdown("**Teams / options**")
            for opt in fields["team_options"]:
                st.markdown(f"- {opt['name']}: {opt.get('implied_pct', 0):.0f}%")
        if fields.get("multipliers"):
            st.markdown("**Multipliers**")
            for m in fields["multipliers"]:
                label = m.get("name") or "(unnamed)"
                st.markdown(f"- {label}: {m['multiplier']:.2f}x")
        if fields.get("volume"):
            st.metric("Volume", f"{float(fields['volume']):,.0f}")
        if fields.get("spread_total_markets"):
            st.caption(f"Spread/total: {fields['spread_total_markets']} related markets detected")
        if fields.get("source_excerpt"):
            st.text(fields["source_excerpt"][:600])


def _review_widget_signature(fields: dict[str, Any]) -> str:
    keys = (
        "title", "bet_format", "contract_side", "price", "multiplier",
        "stake", "bankroll", "user_probability", "risk_tolerance",
    )
    return "|".join(f"{k}={fields.get(k)!r}" for k in keys)


def _seed_review_widgets(fields: dict[str, Any]) -> None:
    """Keep review widgets aligned with saved imp_fields after Apply."""
    sig = _review_widget_signature(fields)
    if st.session_state.get("imp_review_seed_sig") == sig:
        return
    st.session_state["imp_rev_title"] = str(fields.get("title") or "")
    fmt = str(fields.get("bet_format") or BET_FORMAT_OPTIONS[0])
    st.session_state["imp_rev_format"] = fmt if fmt in BET_FORMAT_OPTIONS else BET_FORMAT_OPTIONS[0]
    st.session_state["imp_rev_side"] = str(fields.get("contract_side") or "")
    st.session_state["imp_rev_price"] = float(fields.get("price") or 0.0)
    st.session_state["imp_rev_mult"] = float(fields.get("multiplier") or fields.get("decimal_odds") or 0.0)
    st.session_state["imp_rev_vol"] = float(fields.get("volume") or 0.0)
    st.session_state["imp_rev_stake"] = float(fields.get("stake") or 100.0)
    st.session_state["imp_rev_bankroll"] = float(fields.get("bankroll") or 0.0)
    rt = str(fields.get("risk_tolerance") or "moderate")
    st.session_state["imp_rev_risk_tol"] = rt if rt in ("conservative", "moderate", "aggressive") else "moderate"
    up = fields.get("user_probability")
    if up is not None:
        pct = float(up) * 100 if float(up) <= 1 else float(up)
        st.session_state["imp_rev_prob"] = int(pct)
    else:
        st.session_state.setdefault("imp_rev_prob", 50)
    st.session_state["imp_rev_exp"] = str(fields.get("expiration") or "")
    st.session_state["imp_rev_rules"] = str(fields.get("rules_summary") or "")
    st.session_state["imp_review_seed_sig"] = sig


def _collect_review_edits() -> dict[str, Any]:
    """Read review panel widget values from session state."""
    edits: dict[str, Any] = {
        "title": str(st.session_state.get("imp_rev_title") or "").strip(),
        "bet_format": str(st.session_state.get("imp_rev_format") or BET_FORMAT_OPTIONS[0]),
        "contract_side": str(st.session_state.get("imp_rev_side") or "").strip(),
        "price": float(st.session_state.get("imp_rev_price") or 0.0),
        "multiplier": float(st.session_state.get("imp_rev_mult") or 0.0),
        "volume": float(st.session_state.get("imp_rev_vol") or 0.0),
        "stake": float(st.session_state.get("imp_rev_stake") or 0.0),
        "bankroll": float(st.session_state.get("imp_rev_bankroll") or 0.0),
        "risk_tolerance": str(st.session_state.get("imp_rev_risk_tol") or "moderate"),
        "user_probability": float(st.session_state.get("imp_rev_prob") or 50) / 100.0,
        "expiration": str(st.session_state.get("imp_rev_exp") or "").strip(),
        "rules_summary": str(st.session_state.get("imp_rev_rules") or "").strip(),
    }
    if edits["price"] == 0:
        edits.pop("price")
    if edits["multiplier"] == 0:
        edits.pop("multiplier")
    if edits["volume"] == 0:
        edits.pop("volume")
    if edits.get("bankroll", 0) == 0:
        edits.pop("bankroll")
    return edits


def _render_field_review_form(dtype: str, fields: dict[str, Any]) -> dict[str, Any]:
    team_names = [o["name"] for o in fields.get("team_options") or []]
    side_options = team_names + ["Yes", "No"]
    current_side = str(fields.get("contract_side") or "")
    if current_side and current_side not in side_options:
        side_options = [current_side] + side_options

    _seed_review_widgets(fields)

    with st.container(border=True):
        st.text_input("Market title", key="imp_rev_title")
        st.selectbox("Bet format", BET_FORMAT_OPTIONS, key="imp_rev_format")
        if side_options:
            if current_side in side_options and "imp_rev_side" not in st.session_state:
                st.session_state["imp_rev_side"] = current_side
            st.selectbox(
                "Side / team you are considering",
                side_options,
                key="imp_rev_side",
            )
        else:
            st.text_input("Side / team", key="imp_rev_side")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("Price (¢)", min_value=0.0, max_value=99.0, step=1.0, key="imp_rev_price")
        with col2:
            st.number_input("Multiplier (x)", min_value=0.0, step=0.01, key="imp_rev_mult")
        with col3:
            st.number_input("Volume", min_value=0.0, step=1.0, key="imp_rev_vol")

        col4, col5, col6 = st.columns(3)
        with col4:
            st.number_input("Proposed stake ($)", min_value=0.0, step=1.0, key="imp_rev_stake")
        with col5:
            st.number_input("Bankroll ($)", min_value=0.0, step=50.0, key="imp_rev_bankroll")
        with col6:
            st.slider("Your probability (%)", 5, 95, key="imp_rev_prob")

        col7, col8 = st.columns(2)
        with col7:
            st.selectbox(
                "Risk tolerance",
                ("conservative", "moderate", "aggressive"),
                key="imp_rev_risk_tol",
                help="Caps recommended stake vs Kelly (conservative ≈ quarter Kelly, moderate ≈ half, aggressive ≈ full).",
            )
        with col8:
            st.caption("Bankroll + tolerance drive Kelly sizing and whether your stake is too large.")

        st.text_input("Expiration", key="imp_rev_exp")
        st.text_area("Rules", key="imp_rev_rules")

        if st.button("Apply field corrections", type="primary", key="imp_review_apply"):
            merged = apply_field_edits(fields, _collect_review_edits())
            st.session_state["imp_fields"] = merged
            st.session_state["imp_review_confirmed"] = True
            st.session_state["imp_review_seed_sig"] = _review_widget_signature(merged)
            provided = set(st.session_state.get("imp_user_provided") or set())
            provided.update(_collect_review_edits().keys())
            st.session_state["imp_user_provided"] = provided
            st.rerun()

    return dict(st.session_state.get("imp_fields") or fields)


def _poker_review_signature(fields: dict[str, Any]) -> str:
    keys = ("hero_hand", "board", "pot_size", "amount_to_call", "hero_equity", "street")
    return "|".join(f"{k}={fields.get(k)!r}" for k in keys)


def _seed_poker_review_widgets(fields: dict[str, Any]) -> None:
    sig = _poker_review_signature(fields)
    if st.session_state.get("imp_poker_seed_sig") == sig:
        return
    st.session_state["imp_p_title"] = str(fields.get("title") or "")
    st.session_state["imp_p_street"] = str(fields.get("street") or "flop")
    st.session_state["imp_p_hero"] = str(fields.get("hero_hand") or "")
    st.session_state["imp_p_board"] = str(fields.get("board") or "")
    st.session_state["imp_p_pot"] = float(fields.get("pot_size") or 0.0)
    st.session_state["imp_p_vbet"] = float(fields.get("villain_bet_size") or 0.0)
    st.session_state["imp_p_call"] = float(fields.get("amount_to_call") or 0.0)
    st.session_state["imp_p_hstack"] = float(fields.get("hero_stack") or 0.0)
    st.session_state["imp_p_vstack"] = float(fields.get("villain_stack") or 0.0)
    st.session_state["imp_p_vrange"] = str(fields.get("villain_range") or "")
    eq = fields.get("hero_equity")
    if eq is not None:
        pct = float(eq) * 100 if float(eq) <= 1 else float(eq)
        st.session_state["imp_p_eq"] = int(pct)
    else:
        st.session_state.setdefault("imp_p_eq", 40)
    pos = str(fields.get("position") or "")
    st.session_state["imp_p_pos"] = pos if pos in POSITION_OPTIONS else ""
    st.session_state["imp_p_action"] = str(fields.get("current_action") or "call")
    st.session_state["imp_poker_seed_sig"] = sig


def _collect_poker_review_edits() -> dict[str, Any]:
    edits: dict[str, Any] = {
        "title": str(st.session_state.get("imp_p_title") or "").strip(),
        "street": str(st.session_state.get("imp_p_street") or "flop"),
        "hero_hand": str(st.session_state.get("imp_p_hero") or "").strip(),
        "board": str(st.session_state.get("imp_p_board") or "").strip(),
        "pot_size": float(st.session_state.get("imp_p_pot") or 0.0),
        "villain_bet_size": float(st.session_state.get("imp_p_vbet") or 0.0),
        "amount_to_call": float(st.session_state.get("imp_p_call") or 0.0),
        "hero_stack": float(st.session_state.get("imp_p_hstack") or 0.0),
        "villain_stack": float(st.session_state.get("imp_p_vstack") or 0.0),
        "villain_range": str(st.session_state.get("imp_p_vrange") or "").strip(),
        "hero_equity": float(st.session_state.get("imp_p_eq") or 40) / 100.0,
        "position": str(st.session_state.get("imp_p_pos") or ""),
        "current_action": str(st.session_state.get("imp_p_action") or "call"),
        "decision_type": "poker_hand_decision",
    }
    if edits["pot_size"] == 0:
        edits.pop("pot_size")
    if edits["amount_to_call"] == 0 and edits.get("villain_bet_size", 0) == 0:
        edits.pop("amount_to_call")
    elif edits["amount_to_call"] == 0 and edits.get("villain_bet_size"):
        edits["amount_to_call"] = edits["villain_bet_size"]
    if edits.get("villain_bet_size") == 0:
        edits.pop("villain_bet_size", None)
    if edits["hero_stack"] == 0:
        edits.pop("hero_stack")
    if edits["villain_stack"] == 0:
        edits.pop("villain_stack")
    return edits


def _render_poker_field_review_form(fields: dict[str, Any]) -> dict[str, Any]:
    _seed_poker_review_widgets(fields)
    if st.session_state.get("imp_p_street") not in STREET_OPTIONS:
        st.session_state["imp_p_street"] = "flop"

    with st.container(border=True):
        st.text_input("Hand label", key="imp_p_title")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("Street", list(STREET_OPTIONS), key="imp_p_street")
        with c2:
            st.selectbox("Position", list(POSITION_OPTIONS), key="imp_p_pos")
        with c3:
            st.selectbox("Decision facing", list(POKER_ACTION_OPTIONS), key="imp_p_action")

        c4, c5 = st.columns(2)
        with c4:
            st.text_input("Hero hand", key="imp_p_hero", placeholder="Ah Kh")
        with c5:
            st.text_input("Board", key="imp_p_board", placeholder="Qh Jh 2c")

        c6, c7, c8 = st.columns(3)
        with c6:
            st.number_input("Pot ($)", min_value=0.0, step=1.0, key="imp_p_pot")
        with c7:
            st.number_input("Villain bet ($)", min_value=0.0, step=1.0, key="imp_p_vbet")
        with c8:
            st.number_input("Amount to call ($)", min_value=0.0, step=1.0, key="imp_p_call")

        c9, c10, c11 = st.columns(3)
        with c9:
            st.slider("Equity estimate (%)", 5, 95, key="imp_p_eq")
        with c10:
            st.number_input("Hero stack ($)", min_value=0.0, step=1.0, key="imp_p_hstack")
        with c11:
            st.number_input("Villain stack ($)", min_value=0.0, step=1.0, key="imp_p_vstack")

        st.text_area("Villain range estimate", key="imp_p_vrange", placeholder="e.g. top pair+, flush draws")

        if st.button("Apply field corrections", type="primary", key="imp_poker_review_apply"):
            merged = apply_field_edits(fields, _collect_poker_review_edits())
            st.session_state["imp_fields"] = merged
            st.session_state["imp_review_confirmed"] = True
            st.session_state["imp_poker_seed_sig"] = _poker_review_signature(merged)
            provided = set(st.session_state.get("imp_user_provided") or set())
            provided.update(_collect_poker_review_edits().keys())
            st.session_state["imp_user_provided"] = provided
            st.rerun()

    return dict(st.session_state.get("imp_fields") or fields)


def _render_confidence_panel(completeness: dict[str, Any], dtype: str, fields: dict[str, Any]) -> None:
    conf = completeness.get("confidence", "low")
    color = {"high": "normal", "medium": "off", "low": "inverse"}.get(conf, "off")
    st.metric("Confidence", conf.title(), delta=f"{completeness['completeness_pct']:.0f}% complete", delta_color=color)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Extracted**")
        for k in completeness.get("extracted") or []:
            st.markdown(f"- {field_label(dtype, k)}")
        if not completeness.get("extracted"):
            st.caption("None yet")
    with col2:
        st.markdown("**Still needed**")
        for k in completeness.get("missing") or []:
            st.markdown(f"- {field_label(dtype, k)}")
        if not completeness.get("missing"):
            st.caption("Nothing required missing")
    with col3:
        st.markdown("**Uncertain**")
        uncertain = completeness.get("uncertain") or fields.get("uncertain_fields") or []
        for k in uncertain:
            st.markdown(f"- {field_label(dtype, k) if k in get_field_template(dtype) else k.replace('_', ' ')}")
        if not uncertain:
            st.caption("None flagged")

    if completeness.get("assumptions"):
        st.info("Assumptions: " + ", ".join(field_label(dtype, k) for k in completeness["assumptions"]))

    for q in clarification_questions(fields, decision_type=dtype):
        if q["id"] in (completeness.get("missing") or []) or q["id"] in (fields.get("uncertain_fields") or []):
            st.caption(f"❓ {q['question']} — _{q['why']}_")


def _render_clarification_form(
    dtype: str,
    fields: dict[str, Any],
    missing: list[str],
    user_provided: set[str],
    all_fields: dict[str, Any],
) -> None:
    if not missing:
        return
    st.warning("AMI still needs a few values — fill any that are blank below, or use **Apply field corrections** above.")
    tpl = get_field_template(dtype)

    with st.form("imp_clarify_form", border=True):
        updates: dict[str, Any] = {}
        for key in missing:
            spec = tpl.get(key, {})
            label = field_label(dtype, key)
            why = field_why(dtype, key)
            st.markdown(f"**{label}** — _{why}_")
            itype = spec.get("input_type", "text")
            existing = fields.get(key)
            if itype == "select":
                opts = list(spec.get("options", []))
                if key == "contract_side" and all_fields.get("team_options"):
                    opts = [o["name"] for o in all_fields["team_options"]] + opts
                default_idx = opts.index(existing) if existing in opts else 0
                updates[key] = st.selectbox(label, opts, index=default_idx, key=f"imp_clarify_{key}")
            elif itype == "percent":
                default = 50
                if existing is not None:
                    v = float(existing)
                    default = int(v * 100) if v <= 1 else int(v)
                updates[key] = st.slider(label, 5, 95, default, key=f"imp_clarify_{key}") / 100.0
            elif itype == "number":
                default = float(existing) if existing is not None else (100.0 if key == "stake" else 1.9)
                updates[key] = st.number_input(label, min_value=0.01, value=default, key=f"imp_clarify_{key}")
            else:
                updates[key] = st.text_input(label, value=str(existing or ""), key=f"imp_clarify_{key}")

        if st.form_submit_button("Apply answers"):
            merged = apply_field_edits(fields, updates)
            st.session_state["imp_fields"] = merged
            if dtype == "poker_hand_decision":
                st.session_state["imp_poker_seed_sig"] = _poker_review_signature(merged)
            else:
                st.session_state["imp_review_seed_sig"] = _review_widget_signature(merged)
            user_provided.update(missing)
            user_provided.update(updates.keys())
            st.session_state["imp_user_provided"] = user_provided
            st.rerun()


def _render_poker_analysis_results(
    fields: dict[str, Any],
    analysis: dict[str, Any],
    completeness: dict[str, Any],
) -> None:
    st.markdown("---")
    st.markdown("**Poker decision analysis**")
    st.caption(analysis.get("disclaimer", ""))
    st.caption(f"Street: **{fields.get('street', '—')}** · Confidence: **{completeness.get('confidence', '—')}**")

    exp = analysis.get("explanation") or {}
    verdict = analysis.get("verdict_label", "")
    if analysis.get("verdict") in ("call_favorable", "marginal_call"):
        st.success(verdict)
    elif analysis.get("verdict") == "marginal_fold":
        st.info(verdict)
    else:
        st.warning(verdict)

    if exp.get("summary"):
        st.markdown(exp["summary"])
    if exp.get("break_even_note"):
        st.markdown(exp["break_even_note"])
    if exp.get("decision_rule"):
        st.markdown(exp["decision_rule"])
    if exp.get("uncertainty"):
        st.info(exp["uncertainty"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pot", f"${float(analysis.get('pot_size', 0)):.2f}")
    m2.metric("To call", f"${float(analysis.get('amount_to_call', 0)):.2f}")
    m3.metric("Break-even equity", f"{float(analysis.get('break_even_equity', 0)):.1%}")
    m4.metric("Your equity", f"{float(analysis.get('hero_equity', 0)):.1%}")

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("EV (call)", f"${float(analysis.get('ev_call', 0)):+.2f}")
    m6.metric("EV (fold)", f"${float(analysis.get('ev_fold', 0)):+.2f}")
    m7.metric("Pot odds", str(analysis.get("pot_odds_display") or "—"))
    m8.metric("Recommendation", str(analysis.get("recommendation", "—")).upper())

    if analysis.get("raise_scenario"):
        rs = analysis["raise_scenario"]
        st.caption(f"Raise scenario: to **${rs.get('raise_to')}**, EV if called **${rs.get('ev_if_called'):+.2f}** — {rs.get('note', '')}")

    _render_poker_visuals(fields, analysis)

    with st.expander("Assumptions & what to verify"):
        st.markdown(f"**Assumptions:** {exp.get('assumptions', '')}")
        st.markdown(f"**Risks:** {exp.get('risks', '')}")
        for item in analysis.get("information_to_verify") or []:
            st.markdown(f"- {item}")
        for item in analysis.get("assumptions_checked") or []:
            st.caption(f"✓ {item}")


def _render_poker_visuals(fields: dict[str, Any], analysis: dict[str, Any]) -> None:
    sens = analysis.get("sensitivity") or []
    call_amt = float(analysis.get("amount_to_call") or 0)
    pot_after = float(analysis.get("pot_after_call") or 0)
    equity = float(analysis.get("hero_equity") or 0.4)
    break_even = float(analysis.get("break_even_equity") or 0)

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        try:
            from simulations.thinking_plots import plot_probability_tree
            plot_probability_tree(equity, call_amt, max(pot_after - call_amt, 0))
        except Exception:
            pass
    with col_v2:
        if sens:
            eqs = [r["equity_pct"] for r in sens]
            evs = [r["ev_call"] for r in sens]
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.plot(eqs, evs, color="#6366f1", linewidth=2)
            ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1)
            ax.axvline(break_even * 100, color="#dc2626", linestyle=":", linewidth=1.5, label="Break-even")
            ax.axvline(equity * 100, color="#059669", linestyle=":", linewidth=1.5, label="Your equity")
            ax.set_xlabel("Equity (%)")
            ax.set_ylabel("EV of call ($)")
            ax.set_title("Sensitivity — EV vs equity")
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

    st.markdown("**Equity sensitivity**")
    st.dataframe(
        [
            {
                "Equity (%)": r["equity_pct"],
                "EV (call)": r["ev_call"],
                "Recommend": r["recommendation"],
            }
            for r in sens
        ],
        use_container_width=True,
        hide_index=True,
    )


def _render_analysis_results(
    dtype: str,
    fields: dict[str, Any],
    analysis: dict[str, Any],
    completeness: dict[str, Any],
) -> None:
    st.markdown("---")
    st.markdown("**Decision analysis**")
    st.caption(analysis.get("disclaimer", ""))
    st.caption(f"Bet format: **{analysis.get('bet_format', fields.get('bet_format', '—'))}** · Confidence: **{completeness.get('confidence', '—')}**")

    exp = analysis.get("explanation") or {}
    verdict = analysis.get("verdict_label", "")
    if analysis.get("verdict") == "mathematically_favorable":
        st.success(verdict)
    elif analysis.get("verdict") == "marginal":
        st.info(verdict)
    else:
        st.warning(verdict)

    if exp.get("summary"):
        st.markdown(exp["summary"])
    if exp.get("worth_it_probability"):
        st.markdown(exp["worth_it_probability"])

    unit = "contract" if analysis.get("bet_format") == "prediction_market" else "bet"
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Implied probability", f"{float(analysis.get('implied_probability', 0)):.1%}")
    m2.metric("Break-even P", f"{float(analysis.get('break_even_probability', 0)):.1%}")
    m3.metric(f"EV (per {unit})", f"${float(analysis.get('ev_per_contract', 0)):+.3f}")
    m4.metric("Kelly (full)", f"{float(analysis.get('kelly_fraction', 0)):.1%}")

    m5, m6, m7 = st.columns(3)
    m5.metric("EV (total)", f"${float(analysis.get('ev_total', 0)):+.2f}")
    m6.metric("Edge", f"{float(analysis.get('edge', 0)):+.1%}")
    m7.metric("Expected ROI", f"{float(analysis.get('expected_roi', 0)):+.1%}")

    m8, m9, m10 = st.columns(3)
    m8.metric("Downside risk", f"${float(analysis.get('downside_risk', 0)):.2f}")
    m9.metric("Upside", f"${float(analysis.get('upside', 0)):.2f}")
    sizing = analysis.get("stake_sizing") or {}
    stake_pct = sizing.get("stake_pct_of_bankroll")
    m10.metric(
        "Stake % of bankroll",
        f"{float(stake_pct):.1%}" if stake_pct is not None else "—",
    )

    _render_stake_sizing_panel(analysis)

    if analysis.get("multiplier"):
        st.caption(f"Multiplier used: **{float(analysis['multiplier']):.2f}x**")

    _render_bet_visuals(fields, analysis)

    with st.expander("Assumptions & what to verify"):
        st.markdown(f"**Assumptions:** {exp.get('assumptions', '')}")
        st.markdown(f"**Risks:** {exp.get('risks', '')}")
        for item in analysis.get("information_to_verify") or []:
            st.markdown(f"- {item}")
        for item in analysis.get("assumptions_checked") or []:
            st.caption(f"✓ {item}")

    with st.expander("Sensitivity — what changes if your probability shifts?"):
        sens = analysis.get("sensitivity") or []
        if sens:
            probs = [r["user_probability"] for r in sens]
            evs = [r["ev_total"] for r in sens]
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.plot(probs, evs, color="#6366f1", linewidth=2)
            ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1)
            user_p = fields.get("user_probability")
            if user_p is not None:
                up = float(user_p) * 100 if float(user_p) <= 1 else float(user_p)
                ax.axvline(up, color="#059669", linestyle=":", linewidth=1.5, label="Your estimate")
            ax.set_xlabel("Your probability (%)")
            ax.set_ylabel("EV ($)")
            ax.set_title("Sensitivity — EV vs your probability")
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)
            st.dataframe(
                [{"Your P (%)": r["user_probability"], "EV": r["ev_total"], "+EV?": r["favorable"]} for r in sens],
                use_container_width=True,
                hide_index=True,
            )


def _render_stake_sizing_panel(analysis: dict[str, Any]) -> None:
    sizing = analysis.get("stake_sizing") or {}
    if not sizing:
        return

    with st.container(border=True):
        st.markdown("**Bankroll & stake sizing**")
        if sizing.get("stake_warning") and sizing.get("stake_warning_message"):
            st.warning(sizing["stake_warning_message"])
        elif sizing.get("stake_assessment") == "too_small":
            st.info(sizing.get("stake_assessment_label", ""))
        elif sizing.get("stake_assessment") == "reasonable":
            st.success(sizing.get("stake_assessment_label", ""))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Full Kelly", f"{float(sizing.get('kelly_fraction', 0)):.1%}")
        c2.metric("Half Kelly", f"{float(sizing.get('half_kelly_fraction', 0)):.1%}")
        c3.metric("Quarter Kelly", f"{float(sizing.get('quarter_kelly_fraction', 0)):.1%}")
        c4.metric(
            "Risk rating",
            str(sizing.get("risk_rating_label") or "—"),
        )

        if sizing.get("has_bankroll"):
            rec = sizing.get("recommended_stakes") or {}
            d1, d2, d3 = st.columns(3)
            d1.metric("Conservative stake", f"${float(rec.get('conservative') or 0):,.2f}")
            d2.metric("Moderate stake", f"${float(rec.get('moderate') or 0):,.2f}")
            d3.metric("Aggressive stake", f"${float(rec.get('aggressive') or 0):,.2f}")

            k1, k2, k3 = st.columns(3)
            k1.metric("Full Kelly $", f"${float(sizing.get('kelly_stake') or 0):,.2f}")
            k2.metric("Half Kelly $", f"${float(sizing.get('half_kelly_stake') or 0):,.2f}")
            k3.metric("Quarter Kelly $", f"${float(sizing.get('quarter_kelly_stake') or 0):,.2f}")
        else:
            st.caption(
                "Enter **bankroll** in the review panel to see dollar stakes and whether your proposed bet is oversized."
            )

        if sizing.get("sizing_explanation"):
            st.markdown(sizing["sizing_explanation"])


def _render_bet_visuals(fields: dict[str, Any], analysis: dict[str, Any]) -> None:
    p_user = float(fields.get("user_probability") or analysis.get("implied_probability") or 0.5)
    if p_user > 1:
        p_user /= 100.0
    profit = float(analysis.get("profit_if_win") or 0)
    cost = float(fields.get("cost") or fields.get("stake") or 0.5)
    if analysis.get("bet_format") != "prediction_market":
        cost = float(fields.get("stake") or 100)

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        try:
            from simulations.thinking_plots import plot_probability_tree
            plot_probability_tree(p_user, cost, profit)
        except Exception:
            pass
    with col_v2:
        try:
            from simulations.thinking_plots import plot_ev_bars
            plot_ev_bars(p_user, profit, cost if analysis.get("bet_format") == "prediction_market" else float(fields.get("stake") or cost))
        except Exception:
            pass


def _render_history_panel() -> None:
    entries = list_import_history()
    if not entries:
        st.info("No imported problems saved yet.")
        return

    for entry in entries[:20]:
        title = str(entry.get("fields", {}).get("title") or "Imported problem")
        ts = str(entry.get("timestamp") or "")[:19]
        eid = str(entry.get("id") or "")
        with st.expander(f"{title[:60]} — {ts}", expanded=False):
            src = entry.get("source_type")
            st.caption(f"Type: {get_decision_label(str(entry.get('decision_type', '')))} · Source: {src}")
            if entry.get("image_meta"):
                st.caption(f"Image: {entry['image_meta'].get('filename', '—')} ({entry['image_meta'].get('size_bytes', 0)} bytes)")
            if entry.get("ocr_text"):
                st.text(entry["ocr_text"][:200])
            if entry.get("analysis"):
                st.markdown(f"**Verdict:** {entry['analysis'].get('verdict_label', '—')}")
            if st.button("Reload", key=f"imp_reload_{eid}"):
                st.session_state["imp_fields"] = dict(entry.get("fields") or {})
                st.session_state["imp_decision_type"] = entry.get("decision_type")
                st.session_state["imp_raw_input"] = entry.get("raw_input", "")
                st.session_state["imp_analysis"] = entry.get("analysis")
                st.session_state["imp_image_meta"] = entry.get("image_meta")
                st.session_state["imp_stage"] = "review"
                st.rerun()
            if st.button("Delete", key=f"imp_del_{eid}"):
                delete_import_entry(eid)
                st.rerun()
