"""Sports Betting Lab — EV, odds conversion, team comparison."""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from simulations.thinking_visuals import render_probability_tree


def _decimal_to_implied(decimal_odds: float) -> float:
    return 1.0 / decimal_odds if decimal_odds > 0 else 0.0


def _american_to_decimal(american: float) -> float:
    if american >= 100:
        return 1 + american / 100
    return 1 + 100 / abs(american)


def run_sports_betting_lab() -> None:
    st.markdown("#### Probability & payout picture")
    st.caption("Move sliders below — the tree and EV chart update as you explore.")

    preview_p = st.slider("Preview win % (tree)", 20, 80, 50, key="sb_tree_p") / 100
    preview_stake = 100
    preview_profit = 90
    from simulations.thinking_plots import plot_ev_bars, plot_probability_tree

    plot_probability_tree(preview_p, preview_stake, preview_profit)
    plot_ev_bars(preview_p, preview_profit, preview_stake)

    st.markdown("---")
    st.markdown("#### Compare two teams")

    col1, col2 = st.columns(2)
    with col1:
        team_a = st.text_input("Team A", value="Home Team", key="sb_a")
        prob_a = st.slider(f"{team_a} win probability (%)", 10, 90, 55, key="sb_pa") / 100
    with col2:
        team_b = st.text_input("Team B", value="Away Team", key="sb_b")
        prob_b = 1 - prob_a
        st.metric(f"{team_b} implied probability", f"{prob_b:.1%}")

    st.markdown("---")
    st.markdown("#### Bet analysis")

    odds_format = st.radio("Odds format", ["Decimal", "American"], horizontal=True, key="sb_fmt")
    if odds_format == "Decimal":
        decimal_odds = st.slider("Decimal odds for your pick", 1.10, 5.00, 1.90, step=0.05, key="sb_dec")
    else:
        american = st.slider("American odds", -300, 400, -110, step=5, key="sb_am")
        decimal_odds = _american_to_decimal(american)
        st.caption(f"Decimal equivalent: **{decimal_odds:.2f}**")

    stake = st.slider("Bet amount ($)", 10, 1000, 100, step=10, key="sb_stake")
    pick = st.radio("Your pick", [team_a, team_b], horizontal=True, key="sb_pick")
    win_prob = prob_a if pick == team_a else prob_b

    profit_if_win = stake * (decimal_odds - 1)
    ev = win_prob * profit_if_win - (1 - win_prob) * stake
    implied = _decimal_to_implied(decimal_odds)
    edge = win_prob - implied

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Expected value", f"${ev:+.2f}")
    m1.caption("Average profit per bet")
    m2.metric("Your win probability", f"{win_prob:.1%}")
    m3.metric("Market implied prob", f"{implied:.1%}")
    m4.metric("Edge", f"{edge:+.1%}")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        render_probability_tree(win_prob, decimal_odds, stake)
    with col_v2:
        probs = np.linspace(0.15, 0.85, 50)
        ev_curve = probs * profit_if_win - (1 - probs) * stake
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.plot(probs * 100, ev_curve, color="#6366f1", linewidth=2)
        ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1)
        ax.axvline(win_prob * 100, color="#059669", linestyle=":", linewidth=1.5, label="Your estimate")
        ax.scatter([win_prob * 100], [ev], color="#059669", s=60, zorder=5)
        ax.set_xlabel("Win probability (%)")
        ax.set_ylabel("EV ($)")
        ax.set_title("EV vs your probability estimate")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    if ev > 0:
        st.success(
            f"**Mathematically favorable** — positive EV of ${ev:+.2f} on a ${stake} bet. "
            f"Over many similar bets, you expect to profit. Short-term variance still causes losses."
        )
    elif ev > -stake * 0.02:
        st.warning(
            f"**Near break-even** — EV is ${ev:+.2f}. The market price is close to fair; "
            "no clear mathematical edge."
        )
    else:
        st.error(
            f"**Unfavorable bet** — EV is ${ev:+.2f}. The odds imply a higher win chance "
            "than your estimate supports."
        )

    confidence = st.slider("Your confidence in estimate (%)", 50, 95, 70, key="sb_conf") / 100
    sims = st.slider("Monte Carlo simulations", 500, 5000, 2000, key="sb_sims")

    outcomes = np.random.rand(sims) < win_prob
    profits = np.where(outcomes, profit_if_win, -stake)
    cumulative = np.cumsum(profits)

    st.markdown("##### Simulated betting season")
    rng = np.random.default_rng(42)
    batch_profits = []
    for _ in range(500):
        wins = rng.random(100) < win_prob
        batch_profits.append(np.sum(np.where(wins, profit_if_win, -stake)))

    c1, c2, c3 = st.columns(3)
    c1.metric("Sample profit (100 bets)", f"${cumulative[-1]:+.0f}")
    c2.metric("Win rate in sample", f"{outcomes.mean():.1%}")
    c3.metric("P(profit > 0) over 100 bets", f"{np.mean(np.array(batch_profits) > 0):.1%}")

    st.latex(r"EV = P(win) \cdot profit - P(lose) \cdot stake")
    st.caption(
        f"At {confidence:.0%} confidence, remember: even +EV bets lose "
        f"{(1-win_prob)*100:.0f}% of the time in any single wager."
    )

    st.warning(
        "**Educational only — not gambling or financial advice.** "
        "This lab teaches probability and EV reasoning. Never bet money you cannot afford to lose."
    )
