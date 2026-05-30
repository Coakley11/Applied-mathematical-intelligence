"""Interactive simulations for domain pages."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def plot_line(x, y, title, xlabel, ylabel, legend_labels=None):
    fig, ax = plt.subplots()
    if legend_labels and isinstance(y, list):
        for series, label in zip(y, legend_labels):
            ax.plot(x, series, label=label)
        ax.legend()
    else:
        ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def run_simulation(simulation_id: str | None) -> None:
    if not simulation_id:
        st.info("Simulation for this domain is in development.")
        return

    runners = {
        "gradient_descent": _gradient_descent,
        "monte_carlo_portfolio": _monte_carlo_portfolio,
        "tumor_growth": _tumor_growth,
        "pharmacokinetics": _pharmacokinetics,
        "sports_aging": _sports_aging,
        "projectile": _projectile,
        "monte_carlo_pi": _monte_carlo_pi,
        "regression_noise": _regression_noise,
        "epidemic_sir": _epidemic_sir,
        "bayesian_diagnosis": _bayesian_diagnosis,
        "climate_balance": _climate_balance,
        "election_forecast": _election_forecast,
        "recommendation": _recommendation,
        "poker_ev": _poker_ev,
        "casino_edge": _casino_edge,
        "genetic_drift": _genetic_drift,
        "orbital_mechanics": _orbital_mechanics,
        "supply_chain": _supply_chain,
        "actuarial_losses": _actuarial_losses,
        "signal_wave": _signal_wave,
    }

    runner = runners.get(simulation_id)
    if runner:
        runner()
    else:
        st.warning(f"Unknown simulation: {simulation_id}")


def _gradient_descent():
    learning_rate = st.slider("Learning rate", 0.01, 0.50, 0.10)
    starting_x = st.slider("Starting parameter", -10.0, 10.0, 8.0)
    steps = st.slider("Optimization steps", 5, 100, 40)

    x = starting_x
    losses = []
    for _ in range(steps):
        losses.append(x ** 2)
        x = x - learning_rate * (2 * x)

    plot_line(list(range(len(losses))), losses, "Training Loss Trajectory", "Step", "Loss")
    st.metric("Final parameter", f"{x:.4f}")
    st.metric("Final loss", f"{losses[-1]:.4f}")


def _monte_carlo_portfolio():
    starting_value = st.number_input("Starting portfolio ($)", value=100_000)
    expected_return = st.slider("Expected annual return", -0.10, 0.20, 0.07)
    volatility = st.slider("Annual volatility", 0.01, 0.50, 0.15)
    years = st.slider("Years", 1, 40, 20)
    simulations = st.slider("Simulations", 100, 2000, 800)

    paths = []
    for _ in range(simulations):
        value = starting_value
        path = [value]
        for _ in range(years):
            value *= 1 + np.random.normal(expected_return, volatility)
            path.append(value)
        paths.append(path)

    paths = np.array(paths)
    finals = paths[:, -1]

    fig, ax = plt.subplots()
    for i in range(min(80, simulations)):
        ax.plot(paths[i], alpha=0.12, color="steelblue")
    ax.set_title("Simulated Wealth Paths")
    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio Value ($)")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Median outcome", f"${np.median(finals):,.0f}")
    c2.metric("10th percentile", f"${np.percentile(finals, 10):,.0f}")
    c3.metric("90th percentile", f"${np.percentile(finals, 90):,.0f}")
    c4.metric("P(loss)", f"{np.mean(finals < starting_value):.1%}")


def _tumor_growth():
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
    else:
        st.info("Rates balanced — approximate stability.")


def _pharmacokinetics():
    dose = st.slider("Dose (mg)", 50, 500, 200)
    elimination = st.slider("Elimination rate k", 0.05, 0.5, 0.15)
    hours = st.slider("Hours tracked", 12, 72, 48)

    t = np.linspace(0, hours, 200)
    concentration = (dose / 100) * np.exp(-elimination * t)
    plot_line(t, concentration, "Drug Concentration Over Time", "Hours", "Concentration (relative)")

    auc = float(np.trapezoid(concentration, t))
    st.metric("AUC (exposure)", f"{auc:.2f}")
    st.caption("Area under the curve drives efficacy and toxicity decisions in clinical pharmacology.")


def _sports_aging():
    peak_age = st.slider("Peak age", 24, 34, 28)
    talent = st.slider("Base talent", 40, 100, 70)
    noise = st.slider("Observation noise", 0, 20, 8)

    ages = np.arange(20, 41)
    true = [max(20, talent - abs(a - peak_age) * 2.2) for a in ages]
    observed = np.array(true) + np.random.normal(0, noise, len(ages))

    fig, ax = plt.subplots()
    ax.plot(ages, true, label="Estimated true talent", linewidth=2)
    ax.scatter(ages, observed, label="Observed seasons", alpha=0.7)
    ax.set_title("Talent vs Noisy Performance")
    ax.set_xlabel("Age")
    ax.set_ylabel("Performance index")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def _projectile():
    velocity = st.slider("Initial velocity (m/s)", 10, 200, 90)
    angle = st.slider("Launch angle (°)", 10, 80, 45)
    g = 9.8
    rad = np.radians(angle)
    t_flight = 2 * velocity * np.sin(rad) / g
    t = np.linspace(0, t_flight, 200)
    x = velocity * np.cos(rad) * t
    y = velocity * np.sin(rad) * t - 0.5 * g * t ** 2

    plot_line(x, y, "Trajectory Under Gravity", "Distance (m)", "Height (m)")
    st.metric("Range", f"{max(x):.1f} m")
    st.metric("Max height", f"{max(y):.1f} m")


def _monte_carlo_pi():
    n = st.slider("Random points", 100, 8000, 2000)
    x = np.random.uniform(-1, 1, n)
    y = np.random.uniform(-1, 1, n)
    inside = x ** 2 + y ** 2 <= 1
    pi_est = 4 * np.mean(inside)

    fig, ax = plt.subplots()
    ax.scatter(x[inside], y[inside], s=4, alpha=0.5)
    ax.scatter(x[~inside], y[~inside], s=4, alpha=0.5)
    ax.set_aspect("equal")
    ax.set_title("Monte Carlo π Estimation")
    st.pyplot(fig)
    plt.close(fig)
    st.metric("π estimate", f"{pi_est:.5f}")


def _regression_noise():
    slope = st.slider("True slope", -5.0, 5.0, 2.0)
    noise = st.slider("Noise σ", 0.0, 30.0, 10.0)
    n = st.slider("Sample size", 20, 500, 120)

    x = np.random.uniform(0, 100, n)
    y = 25 + slope * x + np.random.normal(0, noise, n)
    coeffs = np.polyfit(x, y, 1)
    corr = np.corrcoef(x, y)[0, 1]

    fig, ax = plt.subplots()
    ax.scatter(x, y, alpha=0.6)
    xs = np.sort(x)
    ax.plot(xs, coeffs[0] * xs + coeffs[1], color="crimson")
    ax.set_title("Noisy Linear Relationship")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)

    c1, c2 = st.columns(2)
    c1.metric("Estimated slope", f"{coeffs[0]:.3f}")
    c2.metric("Correlation", f"{corr:.3f}")


def _epidemic_sir():
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
    plot_line(
        t,
        [i_hist, r_hist],
        "SIR Epidemic Dynamics (infectious & recovered)",
        "Day",
        "People",
        legend_labels=["Infectious", "Recovered"],
    )
    peak = max(i_hist)
    st.metric("Peak infectious", f"{peak:,.0f}")


def _bayesian_diagnosis():
    base = st.slider("Base disease rate (%)", 0.1, 30.0, 2.0) / 100
    sensitivity = st.slider("Test sensitivity", 0.5, 1.0, 0.92)
    specificity = st.slider("Test specificity", 0.5, 1.0, 0.88)

    p_pos = sensitivity * base + (1 - specificity) * (1 - base)
    post = (sensitivity * base) / p_pos if p_pos > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("P(disease)", f"{base:.2%}")
    c2.metric("P(positive test)", f"{p_pos:.2%}")
    c3.metric("P(disease | positive)", f"{post:.2%}")

    st.caption("Same structure applies to rain given radar, fraud given alerts, etc.")


def _climate_balance():
    forcing = st.slider("Radiative forcing (W/m² anomaly)", 0.0, 4.0, 2.0)
    feedback = st.slider("Feedback parameter", 0.5, 2.5, 1.2)
    years = st.slider("Years", 20, 150, 80)

    temp = [0.0]
    for _ in range(years):
        temp.append(temp[-1] + (forcing - feedback * temp[-1]) * 0.05)

    plot_line(np.arange(years + 1), temp, "Energy Balance Temperature Anomaly", "Year", "ΔT (relative)")
    st.caption("Simplified box model — real GCMs couple atmosphere, ocean, ice, and chemistry.")


def _election_forecast():
    states = st.slider("Number of swing states", 3, 12, 5)
    win_prob = st.slider("Per-state win probability", 0.35, 0.65, 0.52)
    sims = st.slider("Simulations", 500, 5000, 2000)

    electoral_votes = 270
    wins = 0
    for _ in range(sims):
        votes = 230 + sum(np.random.rand(states) < win_prob) * (538 - 230) // states
        if votes >= electoral_votes:
            wins += 1

    st.metric("Win probability", f"{wins / sims:.1%}")
    st.caption("Toy electoral college — illustrates probabilistic forecasting, not a live model.")


def _recommendation():
    users = st.slider("Users", 5, 30, 12)
    items = st.slider("Items", 5, 30, 15)
    rank = st.slider("Latent dimensions", 1, 5, 2)

    u = np.random.randn(users, rank)
    v = np.random.randn(items, rank)
    ratings = u @ v.T + np.random.normal(0, 0.5, (users, items))

    fig, ax = plt.subplots()
    im = ax.imshow(ratings, aspect="auto", cmap="RdYlBu_r")
    ax.set_title("Latent Structure in User–Item Matrix")
    ax.set_xlabel("Items")
    ax.set_ylabel("Users")
    plt.colorbar(im, ax=ax)
    st.pyplot(fig)
    plt.close(fig)


def _poker_ev():
    win_pct = st.slider("Win probability (%)", 5, 95, 40) / 100
    pot = st.slider("Pot size ($)", 20, 500, 120)
    call = st.slider("Cost to call ($)", 5, 200, 40)

    ev = win_pct * pot - (1 - win_pct) * call
    st.metric("Expected value of call", f"${ev:.2f}")
    if ev > 0:
        st.success("Positive EV — mathematically justified long run.")
    else:
        st.warning("Negative EV — folding is correct long run.")


def _casino_edge():
    edge = st.slider("House edge (%)", 0.5, 10.0, 2.7) / 100
    bets = st.slider("Bets simulated", 1000, 50000, 10000)
    wager = 10

    bankroll = np.cumsum(np.random.choice(
        [wager * (1 - edge), -wager],
        size=bets,
        p=[0.48, 0.52],
    ))
    plot_line(np.arange(bets), bankroll, "House Profit Trajectory (simulated)", "Bet #", "Cumulative $")


def _genetic_drift():
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
    ax.set_xlabel("Generation")
    ax.set_ylabel("Allele frequency")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def _orbital_mechanics():
    eccentricity = st.slider("Orbital eccentricity", 0.0, 0.8, 0.3)
    steps = st.slider("Time steps", 100, 1000, 400)

    theta = np.linspace(0, 4 * np.pi, steps)
    r = 1 / (1 + eccentricity * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.scatter([0], [0], color="gold", s=120, zorder=5)
    ax.set_aspect("equal")
    ax.set_title("Keplerian Orbit (scaled units)")
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)


def _supply_chain():
    demand = st.slider("Mean daily demand", 50, 500, 200)
    lead = st.slider("Lead time (days)", 1, 30, 7)
    lead_std = st.slider("Lead time volatility", 0, 5, 2)
    days = st.slider("Days simulated", 30, 180, 90)

    inventory = 1500
    stockouts = 0
    inv_hist = []

    for _ in range(days):
        actual_lead = max(1, int(np.random.normal(lead, lead_std)))
        received = demand * actual_lead * (0.9 + 0.2 * np.random.rand())
        daily = np.random.poisson(demand)
        inventory += received - daily
        if inventory < 0:
            stockouts += 1
            inventory = 0
        inv_hist.append(inventory)

    plot_line(np.arange(days), inv_hist, "Inventory Level Under Stochastic Lead Times", "Day", "Units")
    st.metric("Stockout days", stockouts)


def _actuarial_losses():
    claims = st.slider("Expected claims per year", 50, 5000, 800)
    severity = st.slider("Mean severity ($)", 1000, 50000, 8000)
    years = st.slider("Years simulated", 100, 3000, 1000)

    totals = []
    for _ in range(years):
        n = np.random.poisson(claims)
        total = np.sum(np.random.lognormal(np.log(severity), 0.6, n))
        totals.append(total)

    fig, ax = plt.subplots()
    ax.hist(totals, bins=40, alpha=0.85)
    ax.set_title("Annual Aggregate Loss Distribution")
    ax.set_xlabel("Total loss ($)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)
    plt.close(fig)

    st.metric("95th percentile loss", f"${np.percentile(totals, 95):,.0f}")
    st.metric("99th percentile loss", f"${np.percentile(totals, 99):,.0f}")


def _signal_wave():
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
