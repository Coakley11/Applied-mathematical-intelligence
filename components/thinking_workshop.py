"""Interactive thinking workshop — explore ideas by lens, not by lecture."""

from __future__ import annotations

import streamlit as st

from components.nav import navigate_to
from content.thinking_workshop import (
    WORKSHOP_EXAMPLE_PROMPTS,
    WORKSHOP_INTRO,
    WORKSHOP_MODES,
    get_mode_walkthrough,
    infer_problem_domain,
)
from simulations.thinking_visuals import (
    render_concept_map,
    render_learning_curves,
    render_model_flow,
    render_probability_tree,
    render_sensitivity_bars,
    render_tradeoff_curve,
    render_tumor_comparison,
    render_uncertainty_cone,
)


def render_thinking_quick_cards() -> None:
    """Compact lens picker — links topic library to the six workshop modes."""
    st.caption("Six thinking lenses — open **Interactive workshop** to apply them to your problem.")
    cols = st.columns(len(WORKSHOP_MODES))
    for col, mode in zip(cols, WORKSHOP_MODES):
        with col:
            st.markdown(
                f"<div style='text-align:center;padding:0.5rem;border:1px solid #e2e8f0;"
                f"border-radius:8px;background:#f8fafc;'>"
                f"<div style='font-size:1.4rem'>{mode['icon']}</div>"
                f"<strong>{mode['name']}</strong><br/>"
                f"<span style='font-size:0.75rem;color:#64748b'>{mode['tagline'][:42]}…</span>"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_thinking_workshop() -> None:
    """Full interactive workshop for mathematical thinking styles."""
    st.markdown("#### Interactive thinking workshop")
    st.caption(WORKSHOP_INTRO)

    example = st.selectbox(
        "Start from an example (or type your own)",
        WORKSHOP_EXAMPLE_PROMPTS,
        key="tw_example_pick",
    )
    custom = ""
    if example.endswith("Custom (type below)"):
        custom = st.text_area(
            "Your question, problem, or scenario",
            placeholder="e.g. I want to know if this sports bet is worth making.",
            key="tw_custom_problem",
            height=80,
        )
    problem = custom.strip() if custom.strip() else example.replace("Custom (type below)", "").strip()
    if not problem or problem == "Custom (type below)":
        problem = st.text_input(
            "Or describe your problem here",
            value=st.session_state.get("tw_problem", ""),
            placeholder="Enter a question, bet, scenario, or mathematical idea…",
            key="tw_problem_input",
        )
    else:
        st.session_state.tw_problem = problem

    if problem and not problem.startswith("Custom"):
        st.session_state.tw_problem = problem

    domain = infer_problem_domain(problem or "")
    if problem:
        st.caption(f"Detected context: **{domain.replace('_', ' ').title()}** — walkthrough adapts to your words.")

    st.markdown("##### Pick a thinking lens")
    mode_cols = st.columns(len(WORKSHOP_MODES))
    mode_ids = [m["id"] for m in WORKSHOP_MODES]
    default_mode = st.session_state.get("tw_mode", "abstraction")
    if default_mode not in mode_ids:
        default_mode = "abstraction"

    for col, mode in zip(mode_cols, WORKSHOP_MODES):
        with col:
            if st.button(
                f"{mode['icon']} {mode['name']}",
                key=f"tw_btn_{mode['id']}",
                use_container_width=True,
                type="primary" if mode["id"] == default_mode else "secondary",
            ):
                st.session_state.tw_mode = mode["id"]
                default_mode = mode["id"]

    active = next(m for m in WORKSHOP_MODES if m["id"] == st.session_state.get("tw_mode", default_mode))
    st.markdown(f"**{active['icon']} {active['name']}** — *{active['tagline']}*")

    if not (problem or "").strip():
        st.info("Enter a problem above, then pick a lens to see your personalized thinking walkthrough.")
        _render_demo_panels(active["id"], "general")
        return

    walk = get_mode_walkthrough(problem, active["id"])
    _render_walkthrough(problem, active["id"], walk)


def _render_walkthrough(problem: str, mode_id: str, walk: dict) -> None:
    short = walk["problem_short"]

    tab_visual, tab_explore, tab_apply, tab_try, tab_whatif = st.tabs(
        ["Visual", "Explore", "Real-world", "Try it yourself", "What changes if…"]
    )

    with tab_visual:
        _render_visual_panel(mode_id, walk)

    with tab_explore:
        st.markdown(f"**Your problem:** {short}")
        st.markdown(walk["deeper_structure"])
        if walk.get("matters"):
            st.markdown("**What details matter**")
            for m in walk["matters"]:
                st.markdown(f"- {m}")
        if walk.get("ignore"):
            st.markdown("**What you can often ignore (for now)**")
            for ig in walk["ignore"]:
                st.markdown(f"- {ig}")

        if mode_id == "modeling" and walk.get("variables"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Variables**")
                for v in walk["variables"]:
                    st.markdown(f"- {v}")
            with c2:
                st.markdown("**Unknowns**")
                for u in walk.get("unknowns", []):
                    st.markdown(f"- {u}")
            with c3:
                st.markdown("**Outputs**")
                for o in walk.get("outputs", []):
                    st.markdown(f"- {o}")

        if mode_id == "assumptions" and walk.get("assumptions"):
            st.markdown("**Assumptions being made**")
            for a in walk["assumptions"]:
                st.markdown(f"- {a}")
            if walk.get("if_wrong"):
                st.markdown("**If they are wrong**")
                for w in walk["if_wrong"]:
                    st.warning(w)

        if mode_id == "simplification" and walk.get("simplest_model"):
            st.success(f"**Simplest useful version:** {walk['simplest_model']}")
            if walk.get("can_ignore"):
                st.markdown("**Can ignore (at first)**")
                for c in walk["can_ignore"]:
                    st.markdown(f"- {c}")

        if mode_id == "uncertainty":
            if walk.get("unknown_list"):
                st.markdown("**What we do not know**")
                for u in walk["unknown_list"]:
                    st.markdown(f"- {u}")
            if walk.get("confidence_prompt"):
                st.info(walk["confidence_prompt"])
            if walk.get("sensitivity_note"):
                st.caption(walk["sensitivity_note"])

        if mode_id == "optimization":
            if walk.get("objective"):
                st.markdown(f"**Objective:** {walk['objective']}")
            if walk.get("constraints"):
                st.markdown("**Constraints**")
                for c in walk["constraints"]:
                    st.markdown(f"- {c}")
            if walk.get("tradeoffs"):
                st.markdown("**Tradeoffs**")
                for t in walk["tradeoffs"]:
                    st.markdown(f"- {t}")

    with tab_apply:
        st.markdown("**Where this shows up in the real world**")
        for app in walk.get("applications", []):
            st.markdown(f"- {app}")
        lab = walk.get("suggested_lab", "")
        if lab and lab != "Solve a Problem":
            if st.button(f"Open lab: {lab}", key=f"tw_lab_{mode_id}"):
                navigate_to(lab)

    with tab_try:
        st.markdown(walk.get("try_prompt", "Use the controls below to experiment."))
        _render_try_it(mode_id, walk)

    with tab_whatif:
        st.markdown("Drag sliders or read scenarios — notice when your conclusion **flips**.")
        _render_what_if(mode_id, walk)
        items = walk.get("what_if", [])
        if items:
            st.markdown("**Scenarios to consider**")
            for label, effect in items:
                with st.expander(label, expanded=False):
                    st.markdown(effect)


def _render_visual_panel(mode_id: str, walk: dict) -> None:
    domain = walk.get("domain", "general")
    if mode_id == "abstraction":
        nodes = walk.get("matters") or ["Structure", "Uncertainty", "Decision"]
        render_concept_map("Deeper structure", nodes[:6], "What is this really about?")
    elif mode_id == "modeling":
        inputs = walk.get("variables") or ["Inputs", "Parameters"]
        output = (walk.get("outputs") or ["Answer"])[0]
        render_model_flow(inputs[:4], output)
    elif mode_id == "assumptions":
        labels = [a[:28] + "…" if len(a) > 28 else a for a in (walk.get("assumptions") or ["Assumption"])[:5]]
        deltas = [(lbl, 1.0 if i % 2 == 0 else -0.8) for i, lbl in enumerate(labels)]
        render_sensitivity_bars(0.0, deltas)
        st.caption("Bars show direction of impact if an assumption fails — explore exact sizes in Try it.")
    elif mode_id == "simplification":
        render_concept_map(
            "Simple model",
            (walk.get("can_ignore") or ["Extra detail"])[:4],
            "Strip to what moves the decision",
        )
    elif mode_id == "uncertainty":
        if domain in ("forecasting", "general"):
            noise = st.slider("Noise in data (explore)", 2.0, 30.0, 12.0, key="tw_vis_noise")
            render_uncertainty_cone(noise=noise)
        elif domain == "betting":
            p = st.slider("Win probability %", 30, 70, 45, key="tw_vis_p") / 100
            render_probability_tree(p, 2.5)
        elif domain == "medicine":
            render_tumor_comparison(0.8, 1.2)
        elif domain == "ai":
            render_learning_curves()
        else:
            render_uncertainty_cone()
    elif mode_id == "optimization":
        render_tradeoff_curve()
    else:
        render_concept_map("Thinking lens", ["Explore", "Test", "Decide"])


def _render_try_it(mode_id: str, walk: dict) -> None:
    domain = walk.get("domain", "general")

    if domain in ("betting", "sports") or mode_id in ("modeling", "uncertainty", "optimization"):
        st.markdown("##### Bet / decision calculator")
        c1, c2, c3 = st.columns(3)
        with c1:
            p = st.slider("Your win probability %", 20, 80, 45, key="tw_try_p") / 100
        with c2:
            odds = st.slider("Decimal odds", 1.2, 4.0, 2.5, step=0.05, key="tw_try_odds")
        with c3:
            stake = st.slider("Stake ($)", 10, 500, 100, key="tw_try_stake")
        profit = stake * (odds - 1)
        ev = p * profit - (1 - p) * stake
        implied = 1 / odds if odds > 0 else 0
        st.metric("Expected value", f"${ev:+.2f}")
        st.metric("Edge vs implied prob", f"{(p - implied):+.1%}")
        if mode_id == "uncertainty":
            render_probability_tree(p, odds, stake)
        if ev > 0:
            st.success("Positive EV at these settings.")
        else:
            st.error("Negative EV — changing assumptions may flip this.")

    if domain == "medicine" and mode_id in ("modeling", "simplification", "uncertainty"):
        g = st.slider("Tumor growth rate", 0.2, 2.0, 1.0, key="tw_tumor_g")
        k = st.slider("Treatment kill rate", 0.0, 2.5, 1.3, key="tw_tumor_k")
        render_tumor_comparison(g, k)

    if domain == "ai" and mode_id in ("uncertainty", "modeling", "assumptions"):
        gap = st.slider("Overfitting gap (val − train)", 0.0, 0.25, 0.1, key="tw_ai_gap")
        render_learning_curves(val_gap=gap)

    if domain == "forecasting" or mode_id == "uncertainty":
        noise = st.slider("Forecast noise σ", 2.0, 25.0, 12.0, key="tw_fc_noise")
        render_uncertainty_cone(noise=noise)

    if mode_id == "optimization":
        render_tradeoff_curve()
        b = st.slider("Budget ($)", 1000, 20000, 10000, key="tw_opt_b")
        ra = st.slider("Return A", 0.04, 0.14, 0.06, key="tw_ra")
        rb = st.slider("Return B", 0.04, 0.18, 0.11, key="tw_rb")
        w = st.slider("Weight on B", 0, 100, 50, key="tw_wb") / 100
        port = (1 - w) * ra + w * rb
        st.metric("Portfolio return", f"{port:.2%}", f"on ${b:,.0f} budget → ${b * port:,.0f} expected")


def _render_what_if(mode_id: str, walk: dict) -> None:
    if mode_id == "uncertainty":
        base_p = st.slider("Base win %", 35, 55, 45, key="tw_wi_base") / 100
        delta = st.slider("Uncertainty on p (±%)", 1, 15, 5, key="tw_wi_delta") / 100
        odds = st.slider("Decimal odds (what-if)", 1.5, 3.0, 2.0, key="tw_wi_odds")
        stake = 100.0
        scenarios = [
            ("Low p", base_p - delta),
            ("Base", base_p),
            ("High p", base_p + delta),
        ]
        deltas = []
        for name, prob in scenarios:
            prob = max(0.05, min(0.95, prob))
            ev = prob * stake * (odds - 1) - (1 - prob) * stake
            deltas.append((name, ev))
        render_sensitivity_bars(deltas[1][1], [(d[0], d[1] - deltas[1][1]) for d in deltas])
    elif mode_id == "optimization":
        render_tradeoff_curve()
    elif mode_id == "assumptions":
        n_fail = st.slider("How many assumptions fail?", 0, 4, 1, key="tw_asm_fail")
        render_sensitivity_bars(
            0.0,
            [(f"Assumption {i+1} wrong", -0.4 * (i + 1)) for i in range(n_fail)],
        )
    else:
        shift = st.slider("Perturb main parameter (%)", -30, 30, 0, key="tw_gen_shift")
        render_sensitivity_bars(0.0, [("Parameter shock", shift / 10.0), ("Noise doubles", -0.5 if shift >= 0 else 0.5)])


def _render_demo_panels(mode_id: str, domain: str) -> None:
    """Static demos when no problem entered yet."""
    st.markdown("##### Preview (enter your problem above for a personalized walkthrough)")
    demo_walk = get_mode_walkthrough(
        "I want to know if this sports bet is worth making.", mode_id
    )
    _render_visual_panel(mode_id, demo_walk)


def render_thinking_quick_cards() -> None:
    """Compact six-lens preview for the topic library tab."""
    cols = st.columns(3)
    for i, mode in enumerate(WORKSHOP_MODES):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{mode['icon']} {mode['name']}**")
                st.caption(mode["tagline"])
