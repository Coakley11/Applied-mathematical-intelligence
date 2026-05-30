"""Poker Strategy Lab — EV, pot odds, decision simulator."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

HAND_RANKS = [
    ("Royal Flush", "A♠ K♠ Q♠ J♠ 10♠", "Top straight flush"),
    ("Straight Flush", "Five consecutive, same suit", "Very rare — near-certain win"),
    ("Four of a Kind", "Four cards same rank", "Dominates almost all hands"),
    ("Full House", "Three + pair", "Strong made hand"),
    ("Flush", "Five same suit", "Beats straight and below"),
    ("Straight", "Five consecutive ranks", "Mid-strength made hand"),
    ("Three of a Kind", "Three same rank", "Often wins at showdown"),
    ("Two Pair", "Two different pairs", "Common winning hand"),
    ("One Pair", "Two same rank", "Weak unless kicker helps"),
    ("High Card", "No combination", "Lowest showdown value"),
]


def run_poker_lab() -> None:
    st.markdown("#### Hand rankings (quick reference)")
    with st.expander("Poker hand strength — lowest to highest", expanded=False):
        for rank, example, note in HAND_RANKS:
            st.markdown(f"**{rank}** — {example} · {note}")

    st.markdown("---")
    st.markdown("#### Decision simulator")

    col1, col2 = st.columns(2)
    with col1:
        win_prob = st.slider("Your win probability (%)", 5, 95, 42, key="pk_win") / 100
        pot_before = st.slider("Pot before your action ($)", 50, 500, 150, key="pk_pot")
        bet_to_call = st.slider("Bet you must call ($)", 10, 200, 75, key="pk_call")
    with col2:
        raise_amount = st.slider("Optional raise size ($)", 0, 300, 0, key="pk_raise")
        action = st.radio(
            "Your decision",
            ["Fold", "Call", "Raise"],
            horizontal=True,
            key="pk_action",
        )

    pot_after_call = pot_before + bet_to_call
    ev_call = win_prob * pot_after_call - (1 - win_prob) * bet_to_call
    pot_odds = bet_to_call / (pot_before + bet_to_call)

    if action == "Fold":
        ev_action = 0.0
        verdict = "Neutral — you forfeit the pot but lose nothing more."
        color = "info"
    elif action == "Call":
        ev_action = ev_call
        if ev_call > 0:
            verdict = f"Good call — positive EV of ${ev_call:+.2f} over many identical spots."
            color = "success"
        else:
            verdict = f"Bad call — negative EV of ${ev_call:+.2f}. Fold is better long-run."
            color = "error"
    else:
        fold_equity = 0.15
        pot_if_fold = pot_before + raise_amount * 0.5
        ev_raise = (
            fold_equity * pot_if_fold
            + (1 - fold_equity) * (win_prob * (pot_before + bet_to_call + raise_amount) - raise_amount)
            - (1 - win_prob) * (bet_to_call + raise_amount)
        )
        ev_action = ev_raise
        if ev_raise > ev_call and ev_raise > 0:
            verdict = f"Raise is best — EV ${ev_raise:+.2f} beats calling (${ev_call:+.2f})."
            color = "success"
        elif ev_raise > 0:
            verdict = f"Raise is +EV (${ev_raise:+.2f}) but calling may be simpler."
            color = "success"
        else:
            verdict = f"Raise is −EV (${ev_raise:+.2f}). Consider folding or calling."
            color = "warning"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("EV of your action", f"${ev_action:+.2f}")
    m2.metric("EV if you call", f"${ev_call:+.2f}")
    m3.metric("Pot odds (min equity)", f"{pot_odds:.1%}")
    m4.metric("Your equity", f"{win_prob:.1%}")

    if color == "success":
        st.success(verdict)
    elif color == "error":
        st.error(verdict)
    elif color == "warning":
        st.warning(verdict)
    else:
        st.info(verdict)

    if win_prob > pot_odds:
        st.caption("Your equity exceeds pot odds — a call is mathematically justified.")
    else:
        st.caption("Your equity is below pot odds — you need implied odds or a better spot.")

    st.markdown("---")
    st.markdown("#### Kelly bankroll sizing")
    edge = max(win_prob - pot_odds, 0)
    kelly = edge / (1 - pot_odds) if pot_odds < 1 else 0
    kelly = min(kelly, 0.25)
    bankroll = st.number_input("Bankroll ($)", value=5000, step=500, key="pk_br")
    bets = st.slider("Simulated hands", 100, 2000, 500, key="pk_bets")

    paths = {}
    for label, frac in [("Full Kelly", kelly), ("Half Kelly", kelly / 2), ("Fixed 2%", 0.02)]:
        b = float(bankroll)
        hist = [b]
        for _ in range(bets):
            if b <= 0:
                break
            wager = b * frac
            if np.random.rand() < win_prob:
                b += wager * (pot_after_call / bet_to_call - 1) if bet_to_call else wager
            else:
                b -= wager
            hist.append(max(b, 0))
        paths[label] = hist

    fig, ax = plt.subplots(figsize=(8, 3.5))
    for label, hist in paths.items():
        ax.plot(hist, label=label, linewidth=1.8)
    ax.set_xlabel("Hand #")
    ax.set_ylabel("Bankroll ($)")
    ax.set_title("Bankroll paths under different sizing rules")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.caption(f"Suggested Kelly fraction: **{kelly:.1%}** of bankroll per spot (cap at 25%).")
    st.warning(
        "Educational simulation only — not gambling advice. "
        "Real poker involves position, ranges, and opponent modeling."
    )
