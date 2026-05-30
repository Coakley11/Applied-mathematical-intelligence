"""Sports analytics — shrinkage projection model."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def sports_shrinkage():
    st.markdown("**Empirical Bayes shrinkage** — blend career prior with noisy current-season sample.")
    career = st.slider("Career rate (per game)", 10, 40, 22, key="sp_career")
    season_obs = st.slider("Current season observed rate", 10, 45, 31, key="sp_obs")
    games = st.slider("Games played this season", 5, 82, 18, key="sp_g")
    career_games = st.slider("Career games (prior strength)", 100, 2000, 600, key="sp_cg")

    prior_weight = career_games / (career_games + games)
    posterior = prior_weight * career + (1 - prior_weight) * season_obs
    ci_width = 8 / np.sqrt(games)

    labels = ["Career prior", "Raw season", "Shrunk projection"]
    values = [career, season_obs, posterior]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=["#94a3b8", "#f59e0b", "#0ea5e9"])
    ax.errorbar(2, posterior, yerr=ci_width, fmt="none", color="black", capsize=6)
    ax.set_ylabel("Rate statistic")
    ax.set_title("Moneyball-Style Shrinkage Projection")
    ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.metric("Projection", f"{posterior:.1f}")
    st.metric("Prior weight on career", f"{prior_weight:.1%}")
    st.caption("Small samples overweight hot streaks; shrinkage prevents overpaying for noise.")
