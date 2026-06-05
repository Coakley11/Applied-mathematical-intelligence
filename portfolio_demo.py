"""Portfolio demo state loaders — Applied Mathematical Intelligence. Presentation only."""

from __future__ import annotations

import portfolio_polish as pp


def load_betting_demo(st) -> None:
    st.session_state["sb_tree_p"] = 58
    st.session_state["sb_a"] = "Knicks"
    st.session_state["sb_b"] = "Spurs"
    st.session_state["sb_pa"] = 58
    st.session_state["sb_fmt"] = "Decimal"
    st.session_state["sb_dec"] = 2.10
    st.session_state["sb_stake"] = 100
    st.session_state["sb_pick"] = "Knicks"
    st.session_state["sb_conf"] = 72
    pp.mark_demo_applied(st, "betting")


def load_ai_training_demo(st) -> None:
    st.session_state["ai_lr"] = 0.18
    st.session_state["ai_steps"] = 90
    st.session_state["ai_noise"] = 0.42
    st.session_state["ai_x0"] = 1.6
    st.session_state["ai_y0"] = -1.0
    st.session_state["ai_path"] = True
    st.session_state["ai_gap"] = 22
    pp.mark_demo_applied(st, "ai_training")


def load_disease_demo(st) -> None:
    st.session_state["sir_beta"] = 0.55
    st.session_state["sir_gamma"] = 0.10
    st.session_state["sir_days"] = 150
    pp.mark_demo_applied(st, "disease")


def apply_page_demo(st) -> None:
    if not pp.is_demo_mode(st):
        return
    vm = st.session_state.get("view_mode", "Home")
    if vm == "Analyze a Bet" and not pp.demo_applied(st, "betting"):
        load_betting_demo(st)
    elif vm == "Train an AI" and not pp.demo_applied(st, "ai_training"):
        load_ai_training_demo(st)
    elif vm == "Model a Disease" and not pp.demo_applied(st, "disease"):
        load_disease_demo(st)
