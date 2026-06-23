"""AMI Problem Importer — paste, extract, clarify, analyze, save."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from decision_history import delete_import_entry, list_import_history, save_import_entry
from decision_math import enrich_bet_fields, solve_decision
from decision_parser import extract_fields
from decision_registry import DECISION_TYPES, ENABLED_DECISION_TYPES, get_decision_label, is_enabled
from decision_router import route_imported_problem
from decision_templates import assess_completeness, field_label, field_why, get_field_template


def render_ami_importer() -> None:
    """Full importer workflow: import → extract → clarify → solve → save."""
    st.markdown("#### AMI Problem Importer")
    st.caption(
        "Paste a Kalshi/Calci bet, upload CSV, or enter manually. "
        "AMI extracts what it can, asks for what's missing, then runs decision math — not gambling advice."
    )

    _init_importer_state()

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


def _render_import_workflow() -> None:
    stage = st.session_state.get("imp_stage", "import")

    st.markdown("**1 · Import**")
    source = st.radio(
        "Input method",
        ["Paste text", "Upload CSV", "Manual entry"],
        horizontal=True,
        key="imp_source_radio",
    )
    source_map = {"Paste text": "text", "Upload CSV": "csv", "Manual entry": "manual"}
    source_type = source_map[source]
    st.session_state["imp_source_type"] = source_type

    raw_input = ""
    if source == "Paste text":
        raw_input = st.text_area(
            "Paste bet / market text",
            value=st.session_state.get("imp_paste_buffer", ""),
            height=140,
            placeholder=(
                "Example:\n"
                "Will the Knicks make the playoffs?\n"
                "Yes: 42¢\n"
                "No: 58¢\n"
                "Expires: Dec 31, 2026"
            ),
            key="imp_paste_input",
        )
    elif source == "Upload CSV":
        uploaded = st.file_uploader("CSV file", type=["csv"], key="imp_csv_upload")
        if uploaded is not None:
            raw_input = uploaded.read().decode("utf-8", errors="replace")
            st.code(raw_input[:500], language="csv")
        else:
            st.caption("Expected columns: title, side, price (or yes_price/no_price), stake, user_probability")
    else:
        with st.form("imp_manual_form", border=True):
            st.markdown("**Manual bet entry**")
            m_title = st.text_input("Market title", key="imp_m_title")
            m_side = st.selectbox("Side", ["Yes", "No"], key="imp_m_side")
            m_price = st.number_input("Price (¢)", min_value=1.0, max_value=99.0, value=50.0, key="imp_m_price")
            m_stake = st.number_input("Stake ($)", min_value=1.0, value=100.0, key="imp_m_stake")
            m_prob = st.slider("Your probability (%)", 5, 95, 50, key="imp_m_prob")
            if st.form_submit_button("Use manual entry"):
                raw_input = (
                    f"{m_title}\n{m_side}: {m_price:.0f}¢\n"
                    f"stake: ${m_stake:.0f}\nmy estimate: {m_prob}%"
                )
                st.session_state["imp_manual_raw"] = raw_input

        raw_input = st.session_state.get("imp_manual_raw", "")

    type_options = list(ENABLED_DECISION_TYPES) + [
        k for k in DECISION_TYPES if not is_enabled(k)
    ]
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
            if not raw_input.strip() and source != "Manual entry":
                st.warning("Paste or upload content first.")
                return
            if source == "Manual entry" and not raw_input.strip():
                st.warning("Submit the manual entry form first.")
                return

            route = route_imported_problem(raw_input, source_type=source_type, hint=hint)
            dtype = route["decision_type"]
            if not is_enabled(dtype):
                st.error(f"{get_decision_label(dtype)} is not available yet — Phase 0 supports prediction market bets.")
                return

            fields = extract_fields(raw_input, dtype, source_type=source_type)
            st.session_state["imp_raw_input"] = raw_input
            st.session_state["imp_decision_type"] = dtype
            st.session_state["imp_fields"] = fields
            st.session_state["imp_route"] = route
            st.session_state["imp_user_provided"] = set()
            st.session_state["imp_analysis"] = None
            st.session_state["imp_stage"] = "clarify"

        _render_post_extract()


def _render_post_extract() -> None:
    fields = dict(st.session_state.get("imp_fields") or {})
    dtype = str(st.session_state.get("imp_decision_type") or "prediction_market_bet")
    user_provided: set[str] = set(st.session_state.get("imp_user_provided") or set())

    if dtype == "prediction_market_bet":
        fields = enrich_bet_fields(fields)

    completeness = assess_completeness(dtype, fields, user_provided=user_provided)

    st.markdown("---")
    st.markdown("**2 · Extract**")
    route = st.session_state.get("imp_route") or {}
    c1, c2, c3 = st.columns(3)
    c1.metric("Decision type", get_decision_label(dtype))
    c2.metric("Route confidence", f"{float(route.get('confidence', 0)):.0%}")
    c3.metric("Completeness", f"{completeness['completeness_pct']:.0f}%")

    with st.expander("Extracted fields", expanded=True):
        if fields:
            for k, v in fields.items():
                if v is not None and str(v).strip() != "":
                    st.text(f"{field_label(dtype, k)}: {v}")
        else:
            st.caption("No fields extracted yet.")

    st.markdown("**3 · Missing information**")
    _render_confidence_panel(completeness, dtype)

    if completeness["missing"]:
        _render_clarification_form(dtype, fields, completeness["missing"], user_provided)
        fields = dict(st.session_state.get("imp_fields") or {})
        completeness = assess_completeness(dtype, fields, user_provided=user_provided)
    else:
        st.success("All required fields present — ready to analyze.")

    st.markdown("---")
    st.markdown("**4 · Analyze**")
    st.caption(completeness.get("confidence", "low").title() + " confidence — assumptions are labeled in results.")

    can_solve = completeness.get("can_solve", False)
    if st.button("Run decision analysis", type="primary", disabled=not can_solve, key="imp_solve_btn"):
        analysis = solve_decision(dtype, fields)
        st.session_state["imp_analysis"] = analysis
        st.session_state["imp_stage"] = "results"

    analysis = st.session_state.get("imp_analysis")
    if analysis:
        _render_analysis_results(dtype, fields, analysis, completeness)

        st.markdown("---")
        st.markdown("**5 · Save**")
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
            )
            st.success(f"Saved — {entry['id'][:8]}…")
            try:
                from applied_intelligence_activity import log_problem_solved

                log_problem_solved(
                    topic=str(fields.get("title") or "Imported bet"),
                    area="importer",
                    interactive="prediction_market_bet",
                )
            except Exception:
                pass


def _render_confidence_panel(completeness: dict[str, Any], dtype: str) -> None:
    conf = completeness.get("confidence", "low")
    color = {"high": "normal", "medium": "off", "low": "inverse"}.get(conf, "off")
    st.metric("Confidence level", conf.title(), delta=f"{completeness['completeness_pct']:.0f}% complete", delta_color=color)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Extracted**")
        if completeness["extracted"]:
            for k in completeness["extracted"]:
                st.markdown(f"- {field_label(dtype, k)}")
        else:
            st.caption("None yet")
    with col2:
        st.markdown("**Still needed**")
        if completeness["missing"]:
            for k in completeness["missing"]:
                st.markdown(f"- {field_label(dtype, k)}")
        else:
            st.caption("Nothing required missing")

    if completeness.get("assumptions"):
        st.info(
            "Assumptions (user estimates): "
            + ", ".join(field_label(dtype, k) for k in completeness["assumptions"])
        )


def _render_clarification_form(
    dtype: str,
    fields: dict[str, Any],
    missing: list[str],
    user_provided: set[str],
) -> None:
    st.warning("AMI needs a few values before it can analyze — we won't guess these for you.")
    tpl = get_field_template(dtype)

    with st.form("imp_clarify_form", border=True):
        updates: dict[str, Any] = {}
        for key in missing:
            spec = tpl.get(key, {})
            label = field_label(dtype, key)
            why = field_why(dtype, key)
            st.markdown(f"**{label}** — _{why}_")
            itype = spec.get("input_type", "text")
            if itype == "select":
                opts = spec.get("options", [])
                updates[key] = st.selectbox(label, opts, key=f"imp_clarify_{key}")
            elif itype == "percent":
                default = 50
                if fields.get(key) is not None:
                    v = float(fields[key])
                    default = int(v * 100) if v <= 1 else int(v)
                updates[key] = st.slider(label, 5, 95, default, key=f"imp_clarify_{key}") / 100.0
            elif itype == "number":
                default = float(fields.get(key) or 100.0)
                updates[key] = st.number_input(label, min_value=0.01, value=default, key=f"imp_clarify_{key}")
            else:
                updates[key] = st.text_input(label, value=str(fields.get(key) or ""), key=f"imp_clarify_{key}")

        submitted = st.form_submit_button("Apply answers")
        if submitted:
            merged = dict(fields)
            merged.update(updates)
            if dtype == "prediction_market_bet":
                merged = enrich_bet_fields(merged)
            st.session_state["imp_fields"] = merged
            user_provided.update(missing)
            st.session_state["imp_user_provided"] = user_provided
            st.rerun()


def _render_analysis_results(
    dtype: str,
    fields: dict[str, Any],
    analysis: dict[str, Any],
    completeness: dict[str, Any],
) -> None:
    st.markdown("---")
    st.markdown("**Decision analysis**")
    st.caption(analysis.get("disclaimer", ""))

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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Implied probability", f"{float(analysis.get('implied_probability', 0)):.1%}")
    m2.metric("Break-even P", f"{float(analysis.get('break_even_probability', 0)):.1%}")
    m3.metric("EV (per contract)", f"${float(analysis.get('ev_per_contract', 0)):+.3f}")
    m4.metric("Expected ROI", f"{float(analysis.get('expected_roi', 0)):+.1%}")

    m5, m6, m7 = st.columns(3)
    m5.metric("EV (total)", f"${float(analysis.get('ev_total', 0)):+.2f}")
    m6.metric("Downside risk", f"${float(analysis.get('downside_risk', 0)):.2f}")
    m7.metric("Upside", f"${float(analysis.get('upside', 0)):.2f}")

    if dtype == "prediction_market_bet":
        _render_bet_visuals(fields, analysis)

    with st.expander("Assumptions & what to verify"):
        st.markdown(f"**Assumptions:** {exp.get('assumptions', '')}")
        st.markdown(f"**Risks:** {exp.get('risks', '')}")
        st.markdown("**Check before acting:**")
        for item in analysis.get("information_to_verify") or []:
            st.markdown(f"- {item}")
        for item in analysis.get("assumptions_checked") or []:
            st.caption(f"✓ {item}")

    with st.expander("Sensitivity — what changes if your probability shifts?"):
        sens = analysis.get("sensitivity") or []
        if sens:
            probs = [r["user_probability"] for r in sens]
            evs = [r["ev_per_contract"] for r in sens]
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.plot(probs, evs, color="#6366f1", linewidth=2)
            ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1)
            user_p = fields.get("user_probability")
            if user_p is not None:
                up = float(user_p) * 100 if float(user_p) <= 1 else float(user_p)
                ax.axvline(up, color="#059669", linestyle=":", linewidth=1.5, label="Your estimate")
            ax.set_xlabel("Your probability (%)")
            ax.set_ylabel("EV per contract ($)")
            ax.set_title("Sensitivity — EV vs your probability")
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

            st.dataframe(
                [{"Your P (%)": r["user_probability"], "EV/contract": r["ev_per_contract"], "EV total": r["ev_total"], "+EV?": r["favorable"]} for r in sens],
                use_container_width=True,
                hide_index=True,
            )


def _render_bet_visuals(fields: dict[str, Any], analysis: dict[str, Any]) -> None:
    p_user = float(fields.get("user_probability") or analysis.get("implied_probability") or 0.5)
    if p_user > 1:
        p_user /= 100.0
    profit = float(analysis.get("profit_if_win") or 0)
    cost = float(fields.get("cost") or 0.5)

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

            plot_ev_bars(p_user, profit, cost)
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
            st.caption(f"Type: {get_decision_label(str(entry.get('decision_type', '')))} · Source: {entry.get('source_type')}")
            if entry.get("analysis"):
                st.markdown(f"**Verdict:** {entry['analysis'].get('verdict_label', '—')}")
            if st.button("Reload", key=f"imp_reload_{eid}"):
                st.session_state["imp_fields"] = dict(entry.get("fields") or {})
                st.session_state["imp_decision_type"] = entry.get("decision_type")
                st.session_state["imp_raw_input"] = entry.get("raw_input", "")
                st.session_state["imp_analysis"] = entry.get("analysis")
                st.session_state["imp_stage"] = "clarify"
                st.rerun()
            if st.button("Delete", key=f"imp_del_{eid}"):
                delete_import_entry(eid)
                st.rerun()
