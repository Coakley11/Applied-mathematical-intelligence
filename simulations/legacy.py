"""Established domain simulations (retained for specialized domains)."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from simulations.plots import plot_line


def pharmacokinetics():
    dose = st.slider("Dose (mg)", 50, 500, 200)
    elimination = st.slider("Elimination rate k", 0.05, 0.5, 0.15)
    hours = st.slider("Hours tracked", 12, 72, 48)
    t = np.linspace(0, hours, 200)
    concentration = (dose / 100) * np.exp(-elimination * t)
    plot_line(t, concentration, "Drug Concentration Over Time", "Hours", "Concentration (relative)")
    auc = float(np.trapezoid(concentration, t))
    st.metric("AUC (exposure)", f"{auc:.2f}")


def tumor_growth():
    initial = st.slider("Initial size", 1.0, 20.0, 5.0)
    growth = st.slider("Growth rate", 0.01, 0.25, 0.08)
    treatment = st.slider("Treatment effect", 0.0, 0.25, 0.06)
    periods = st.slider("Time periods", 20, 200, 100)
    t = np.arange(periods)
    net = growth - treatment
    size = initial * np.exp(net * t)
    plot_line(t, size, "Competing Growth vs Treatment", "Time", "Tumor Size")
    if net > 0:
        st.warning("Net growth positive — treatment weaker than proliferation.")
    elif net < 0:
        st.success("Net growth negative — treatment dominates.")


def epidemic_sir():
    population = 1_000_000
    beta = st.slider("Transmission rate β", 0.1, 1.2, 0.45)
    gamma = st.slider("Recovery rate γ", 0.05, 0.5, 0.12)
    days = st.slider("Days", 30, 200, 120)
    s, i, r = population - 1000, 1000, 0
    s_hist, i_hist, r_hist = [s], [i], [r]
    for _ in range(days):
        new_inf = beta * s * i / population
        new_rec = gamma * i
        s = max(0, s - new_inf)
        i = max(0, i + new_inf - new_rec)
        r += new_rec
        s_hist.append(s)
        i_hist.append(i)
        r_hist.append(r)
    t = np.arange(days + 1)
    plot_line(t, [i_hist, r_hist], "SIR Epidemic Dynamics", "Day", "People", legend_labels=["Infectious", "Recovered"])
    st.metric("Peak infectious", f"{max(i_hist):,.0f}")


def actuarial_losses():
    claims = st.slider("Expected claims per year", 50, 5000, 800)
    severity = st.slider("Mean severity ($)", 1000, 50000, 8000)
    years = st.slider("Years simulated", 100, 3000, 1000)
    totals = []
    for _ in range(years):
        n = np.random.poisson(claims)
        totals.append(np.sum(np.random.lognormal(np.log(severity), 0.6, n)))
    fig, ax = plt.subplots()
    ax.hist(totals, bins=40, alpha=0.85)
    ax.set_title("Annual Aggregate Loss Distribution")
    ax.set_xlabel("Total loss ($)")
    st.pyplot(fig)
    plt.close(fig)
    st.metric("95th percentile loss", f"${np.percentile(totals, 95):,.0f}")


def election_forecast():
    states = st.slider("Number of swing states", 3, 12, 5)
    win_prob = st.slider("Per-state win probability", 0.35, 0.65, 0.52)
    sims = st.slider("Simulations", 500, 5000, 2000)
    wins = sum(
        1 for _ in range(sims)
        if 230 + sum(np.random.rand(states) < win_prob) * (538 - 230) // states >= 270
    )
    st.metric("Win probability", f"{wins / sims:.1%}")


def election_forecast():
    states = st.slider("Number of swing states", 3, 12, 5)
    win_prob = st.slider("Per-state win probability", 0.35, 0.65, 0.52)
    sims = st.slider("Simulations", 500, 5000, 2000)
    wins = sum(
        1 for _ in range(sims)
        if 230 + sum(np.random.rand(states) < win_prob) * (538 - 230) // states >= 270
    )
    st.metric("Win probability", f"{wins / sims:.1%}")
    st.caption("Toy electoral model — illustrates probabilistic forecasting discipline.")


def genetic_drift():
    pop = st.slider("Population size", 20, 500, 100)
    gens = st.slider("Generations", 20, 300, 150)
    runs = st.slider("Independent populations", 5, 30, 12)
    fig, ax = plt.subplots()
    for _ in range(runs):
        p = 0.5
        hist = [p]
        for _ in range(gens):
            p = np.mean(np.random.rand(pop) < p)
            hist.append(p)
        ax.plot(hist, alpha=0.6)
    ax.set_title("Allele Frequency Under Genetic Drift")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def supply_chain():
    demand = st.slider("Mean daily demand", 50, 500, 200)
    lead = st.slider("Lead time (days)", 1, 30, 7)
    lead_std = st.slider("Lead time volatility", 0, 5, 2)
    days = st.slider("Days simulated", 30, 180, 90)
    inventory = 1500
    stockouts = 0
    inv_hist = []
    for _ in range(days):
        actual_lead = max(1, int(np.random.normal(lead, lead_std)))
        inventory += demand * actual_lead * (0.9 + 0.2 * np.random.rand()) - np.random.poisson(demand)
        if inventory < 0:
            stockouts += 1
            inventory = 0
        inv_hist.append(inventory)
    plot_line(np.arange(days), inv_hist, "Inventory Under Stochastic Lead Times", "Day", "Units")
    st.metric("Stockout days", stockouts)


def casino_edge():
    edge = st.slider("House edge (%)", 0.5, 10.0, 2.7) / 100
    bets = st.slider("Bets simulated", 1000, 50000, 10000)
    bankroll = np.cumsum(np.random.choice([10 * (1 - edge), -10], size=bets, p=[0.48, 0.52]))
    plot_line(np.arange(bets), bankroll, "House Profit Trajectory", "Bet #", "Cumulative $")


def recommendation():
    users = st.slider("Users", 5, 30, 12)
    items = st.slider("Items", 5, 30, 15)
    rank = st.slider("Latent dimensions", 1, 5, 2)
    ratings = np.random.randn(users, rank) @ np.random.randn(rank, items).T
    fig, ax = plt.subplots()
    im = ax.imshow(ratings, aspect="auto", cmap="RdYlBu_r")
    plt.colorbar(im, ax=ax)
    ax.set_title("Latent Structure in User–Item Matrix")
    st.pyplot(fig)
    plt.close(fig)


def signal_wave():
    freq = st.slider("Frequency (Hz)", 1, 20, 5)
    samples = st.slider("Samples", 100, 2000, 500)
    t = np.linspace(0, 1, samples)
    signal = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * (freq * 3) * t)
    fig, ax = plt.subplots(2, 1, figsize=(8, 6))
    ax[0].plot(t, signal)
    ax[0].set_title("Time Domain Signal")
    ax[1].stem(np.fft.rfftfreq(samples, 1 / samples)[:80], np.abs(np.fft.rfft(signal))[:80], basefmt=" ")
    ax[1].set_title("Frequency Spectrum (FFT)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
