"""Poker and gambling mathematics — EV, pot odds, Kelly."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from simulations.plots import plot_line


def poker_quant_suite():
    tab1, tab2, tab3 = st.tabs(["Expected value", "Pot odds", "Kelly criterion"])

    with tab1:
        _expected_value()
    with tab2:
        _pot_odds()
    with tab3:
        _kelly_criterion()


def _expected_value():
    win = st.slider("Win probability (%)", 5, 95, 38, key="ev_w") / 100
    pot = st.slider("Total pot after call ($)", 40, 600, 180, key="ev_p")
    call = st.slider("Your call cost ($)", 5, 250, 60, key="ev_c")
    ev = win * pot - (1 - win) * call
    st.metric("Expected value of calling", f"${ev:+.2f}")
    st.latex(r"EV = P(win)\cdot pot - P(lose)\cdot call")
    if ev > 0:
        st.success("Profitable call over infinite identical spots.")
    else:
        st.warning("Negative EV — fold is the long-run correct play.")


def _pot_odds():
    st.markdown("Compare **pot odds** to your **equity** to justify a call.")
    pot = st.slider("Current pot ($)", 20, 400, 100, key="po_pot")
    call = st.slider("Bet to call ($)", 5, 200, 50, key="po_call")
    equity = st.slider("Your equity (%)", 5, 95, 32, key="po_eq") / 100

    pot_odds = call / (pot + call)
    st.metric("Pot odds (required equity)", f"{pot_odds:.1%}")
    st.metric("Your equity", f"{equity:.1%}")
    if equity > pot_odds:
        st.success("Equity exceeds pot odds — calling is mathematically justified.")
    else:
        st.warning("Equity below pot odds — fold unless implied odds rescue the spot.")


def _kelly_criterion():
    st.markdown("**Kelly bet sizing** — maximize long-run growth rate under edge and variance.")
    edge = st.slider("Per-bet edge (%)", 0.5, 15.0, 3.0, key="k_edge") / 100
    win_p = st.slider("Win rate if even-money", 0.45, 0.65, 0.53, key="k_wp")
    bankroll = st.number_input("Starting bankroll ($)", value=10_000, key="k_br")
    bets = st.slider("Bets simulated", 200, 5000, 1500, key="k_n")

    odds = 1.0
    kelly_f = (odds * win_p - (1 - win_p)) / odds
    kelly_f = max(0.0, min(kelly_f, 0.25))
    frac = st.slider("Bet fraction of bankroll", 0.01, 0.25, round(kelly_f, 3), key="k_frac")

    paths = {"Kelly (theoretical)": [], "Half-Kelly": [], "Fixed 5%": []}
    for label, f in [("Kelly (theoretical)", kelly_f), ("Half-Kelly", kelly_f / 2), ("Fixed 5%", 0.05)]:
        b = bankroll
        hist = [b]
        for _ in range(bets):
            if b <= 0:
                break
            wager = b * f
            b += wager * (edge + (win_p - 0.5) * 2) + np.random.normal(0, wager * 0.15)
            b = max(b, 0)
            hist.append(b)
        paths[label] = hist

    fig, ax = plt.subplots()
    for label, hist in paths.items():
        ax.plot(hist, alpha=0.8, label=label)
    ax.set_title("Bankroll Paths Under Different Sizing Rules")
    ax.set_xlabel("Bet number")
    ax.set_ylabel("Bankroll ($)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)
    st.metric("Full Kelly fraction", f"{kelly_f:.2%}")
