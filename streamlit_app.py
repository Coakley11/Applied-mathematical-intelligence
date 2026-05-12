# streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Applied Mathematical Intelligence",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================

st.title("Applied Mathematical Intelligence")
st.subheader("How Calculus, Probability, Statistics, Simulation, and AI Shape Real Systems")

st.markdown("""
This app is designed for people who already have a working understanding of mathematics.

It does **not** teach math like a basic textbook.

Instead, it shows how advanced mathematical ideas are used in real domains:
medicine, finance, AI, sports analytics, engineering, simulations, and prediction systems.
""")

# =====================================================
# SIDEBAR
# =====================================================

domain = st.sidebar.selectbox(
    "Choose a domain:",
    [
        "Home",
        "AI + Machine Learning Systems",
        "Finance + Risk Modeling",
        "Medicine + Biological Modeling",
        "Sports Analytics",
        "Engineering + Optimization",
        "Simulation Theory + Monte Carlo",
        "Statistics + Prediction Systems",
        "Excel / Portfolio Practice Problems"
    ]
)

math_lens = st.sidebar.selectbox(
    "Mathematical lens:",
    [
        "Calculus / Accumulation",
        "Probability / Uncertainty",
        "Statistics / Pattern Detection",
        "Optimization / Improvement",
        "Simulation / Alternate Futures",
        "AI / Learning Systems"
    ]
)

depth = st.sidebar.radio(
    "Depth level:",
    ["Professional Overview", "Technical Explanation", "Portfolio / Interview Framing"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Applied Mathematical Intelligence Prototype")


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def section(title):
    st.markdown("---")
    st.header(title)


def math_frame(big_idea, how_used, example):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Mathematical Idea")
        st.info(big_idea)

    with col2:
        st.subheader("How It Is Used")
        st.success(how_used)

    st.subheader("Concrete Example")
    st.markdown(example)


def plot_line(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)


def plot_scatter(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)


def show_practice_problem(title, prompt, excel_task, python_extension):
    with st.expander(title):
        st.markdown("### Applied Problem")
        st.write(prompt)

        st.markdown("### Excel Practice")
        st.write(excel_task)

        st.markdown("### Python / Data Extension")
        st.write(python_extension)


# =====================================================
# HOME PAGE
# =====================================================

if domain == "Home":
    section("Core Philosophy")

    st.markdown("""
    The purpose of this app is to show that higher mathematics is not just about symbolic manipulation.

    It is a way to model reality.

    The app focuses on five deep mathematical powers:

    1. **Calculus** — adding up continuous change  
    2. **Probability** — modeling uncertainty  
    3. **Statistics** — finding signal inside noisy data  
    4. **Optimization** — improving decisions under constraints  
    5. **Simulation** — exploring possible futures before they happen  
    """)

    st.markdown("""
    In each domain, the app asks:

    - What mathematical structure is hiding inside this system?
    - What variables matter?
    - What can be predicted?
    - What can be optimized?
    - What uncertainty remains?
    - How could this be modeled in Excel, Python, or AI?
    """)

    st.success("""
    This is meant to feel like a professional applied mathematics lab, not a school worksheet app.
    """)


# =====================================================
# AI + MACHINE LEARNING
# =====================================================

elif domain == "AI + Machine Learning Systems":
    section("AI + Machine Learning Systems")

    math_frame(
        big_idea="""
        AI systems are built from optimization, probability, statistics, and calculus.

        A model makes predictions, measures error, and updates itself repeatedly.
        Calculus enters through gradients. Statistics enters through pattern detection.
        Probability enters through uncertainty and prediction confidence.
        """,
        how_used="""
        Machine learning models use mathematical optimization to reduce prediction error.
        Neural networks adjust millions or billions of parameters by following gradients.
        The system does not “understand” in a human sense; it improves through repeated numerical adjustment.
        """,
        example="""
        Example: A model predicts housing prices.  
        It compares predicted price vs actual price, calculates error, and adjusts weights.

        In AI terms:

        - prediction = model output  
        - error = loss function  
        - improvement = gradient descent  
        - learning = repeated optimization  
        """
    )

    st.subheader("Gradient Descent Simulation")

    learning_rate = st.slider("Learning rate", 0.01, 0.50, 0.10)
    starting_x = st.slider("Starting parameter value", -10.0, 10.0, 8.0)
    steps = st.slider("Optimization steps", 5, 100, 40)

    x_values = [starting_x]
    losses = []

    x = starting_x

    for i in range(steps):
        loss = x ** 2
        gradient = 2 * x
        x = x - learning_rate * gradient

        losses.append(loss)
        x_values.append(x)

    plot_line(
        list(range(len(losses))),
        losses,
        "Loss Function During Optimization",
        "Step",
        "Loss"
    )

    st.markdown("""
    ### Interpretation

    This is a simplified version of what happens in machine learning.

    The model starts with a bad parameter value.  
    It calculates the slope of the loss function.  
    It moves in the direction that reduces error.

    In real AI models, this same idea happens across huge numbers of variables.
    """)

    show_practice_problem(
        "AI Practice Problem: Model Error Reduction",
        "Suppose an AI model predicts student test scores. For each student, you have actual score, predicted score, and error.",
        "Create columns for Actual Score, Predicted Score, Error, Squared Error, and Average Squared Error.",
        "Use Python to simulate different prediction errors and graph how model accuracy improves after each training round."
    )


# =====================================================
# FINANCE + RISK MODELING
# =====================================================

elif domain == "Finance + Risk Modeling":
    section("Finance + Risk Modeling")

    math_frame(
        big_idea="""
        Finance is not just arithmetic. It is probability over time.

        Investment returns are uncertain. Risk is not one number.
        A portfolio has many possible futures.
        """,
        how_used="""
        Calculus and probability appear in compound growth, option pricing, risk models,
        stochastic processes, and portfolio optimization.

        Statistics is used to estimate return, volatility, correlation, and downside risk.
        """,
        example="""
        Example: A $100,000 portfolio may have an expected return of 7%, but that does not mean
        it will grow by exactly 7%.

        A better model simulates many possible paths and studies the distribution of outcomes.
        """
    )

    st.subheader("Monte Carlo Portfolio Simulation")

    starting_value = st.number_input("Starting portfolio value", value=100000)
    expected_return = st.slider("Expected annual return", -0.10, 0.20, 0.07)
    volatility = st.slider("Annual volatility", 0.01, 0.50, 0.15)
    years = st.slider("Years", 1, 40, 20)
    simulations = st.slider("Number of simulations", 100, 3000, 1000)

    all_paths = []

    for _ in range(simulations):
        value = starting_value
        path = [value]

        for year in range(years):
            annual_return = np.random.normal(expected_return, volatility)
            value = value * (1 + annual_return)
            path.append(value)

        all_paths.append(path)

    all_paths = np.array(all_paths)
    final_values = all_paths[:, -1]

    fig, ax = plt.subplots()
    for i in range(min(100, simulations)):
        ax.plot(all_paths[i], alpha=0.15)

    ax.set_title("Simulated Portfolio Paths")
    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio Value")
    ax.grid(True)
    st.pyplot(fig)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Median Ending Value", f"${np.median(final_values):,.0f}")
    col2.metric("10th Percentile", f"${np.percentile(final_values, 10):,.0f}")
    col3.metric("90th Percentile", f"${np.percentile(final_values, 90):,.0f}")
    col4.metric("Probability of Loss", f"{np.mean(final_values < starting_value):.1%}")

    st.markdown("""
    ### Interpretation

    This shows finance as a probability distribution, not a single forecast.

    The deeper idea is that risk management is about the shape of possible outcomes:
    upside, downside, volatility, tail risk, and probability of ruin.
    """)

    show_practice_problem(
        "Finance Practice Problem: Portfolio Simulation",
        "You are comparing two portfolios. Portfolio A has higher expected return but higher volatility. Portfolio B has lower return but lower risk.",
        "Use Excel RAND/NORM.INV to simulate 30 years of returns for each portfolio. Compare median outcome, worst 10%, and probability of ending below the starting amount.",
        "Use Python to run 10,000 simulations and create a histogram of final portfolio values."
    )


# =====================================================
# MEDICINE + BIOLOGICAL MODELING
# =====================================================

elif domain == "Medicine + Biological Modeling":
    section("Medicine + Biological Modeling")

    math_frame(
        big_idea="""
        Biological systems often involve growth, decay, feedback, uncertainty, and competing rates.

        Calculus models continuous change.
        Statistics estimates treatment effects.
        Probability models patient uncertainty.
        """,
        how_used="""
        Medical researchers use mathematical models for tumor growth, drug concentration,
        treatment response, survival curves, clinical trials, and disease spread.
        """,
        example="""
        Example: A tumor may grow exponentially if untreated, but treatment may reduce the effective growth rate.

        The key question becomes:

        Is the treatment effect strong enough to overcome the natural growth rate?
        """
    )

    st.subheader("Tumor Growth vs Treatment Effect")

    initial_size = st.slider("Initial tumor size", 1.0, 20.0, 5.0)
    growth_rate = st.slider("Natural growth rate", 0.01, 0.25, 0.08)
    treatment_effect = st.slider("Treatment effect", 0.00, 0.25, 0.06)
    time_periods = st.slider("Time periods", 20, 200, 100)

    t = np.arange(time_periods)
    net_growth = growth_rate - treatment_effect
    tumor_size = initial_size * np.exp(net_growth * t)

    plot_line(
        t,
        tumor_size,
        "Tumor Growth Model",
        "Time",
        "Tumor Size"
    )

    if net_growth > 0:
        st.warning("The model suggests continued growth because the treatment effect is weaker than the growth rate.")
    elif net_growth < 0:
        st.success("The model suggests decline because the treatment effect is stronger than the growth rate.")
    else:
        st.info("The model suggests stability because treatment effect and growth rate are approximately balanced.")

    st.markdown("""
    ### Interpretation

    This is not a medical prediction tool.

    It is a mathematical demonstration of a key idea:
    biological outcomes often depend on competing rates of change.

    Calculus helps model the continuous change.
    Statistics helps estimate the rates.
    Probability helps represent uncertainty across different patients.
    """)

    show_practice_problem(
        "Medicine Practice Problem: Treatment Comparison",
        "A clinical trial compares Treatment A and Treatment B. Each patient has baseline tumor size, final tumor size, and treatment group.",
        "Use Excel to calculate percent change, average response by group, and standard deviation by group.",
        "Use Python to simulate patient-level variation and compare treatment groups using a t-test or confidence interval."
    )


# =====================================================
# SPORTS ANALYTICS
# =====================================================

elif domain == "Sports Analytics":
    section("Sports Analytics")

    math_frame(
        big_idea="""
        Sports performance is noisy. A player’s true ability is hidden beneath randomness,
        aging, injuries, teammates, coaching, and schedule effects.
        """,
        how_used="""
        Statistics estimates true talent. Regression models future production.
        Probability simulates game outcomes. Optimization helps with drafts, trades, and roster construction.
        """,
        example="""
        Example: A baseball player who hits 35 home runs may not truly be a 35-home-run talent.
        His result contains skill plus randomness.

        A projection system regresses extreme performances toward a more stable estimate.
        """
    )

    st.subheader("Aging Curve + Random Performance Noise")

    peak_age = st.slider("Peak age", 24, 34, 28)
    talent_level = st.slider("Base talent level", 40, 100, 70)
    noise_level = st.slider("Random year-to-year noise", 0, 20, 8)

    ages = np.arange(20, 41)
    true_curve = []

    for age in ages:
        decline = abs(age - peak_age) * 2.2
        true_ability = talent_level - decline
        true_curve.append(true_ability)

    observed = np.array(true_curve) + np.random.normal(0, noise_level, len(ages))

    fig, ax = plt.subplots()
    ax.plot(ages, true_curve, label="Estimated True Ability")
    ax.scatter(ages, observed, label="Observed Performance")
    ax.set_title("True Talent vs Observed Performance")
    ax.set_xlabel("Age")
    ax.set_ylabel("Performance Index")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("""
    ### Interpretation

    This demonstrates a major idea in sports analytics:

    observed performance is not the same as true talent.

    A good model separates:
    - skill
    - aging
    - randomness
    - environment
    - injury effects
    - sample size effects
    """)

    show_practice_problem(
        "Sports Practice Problem: Regression to the Mean",
        "A player has a career average of 20 points per game but scores 30 points per game over the first 10 games of a season.",
        "Use Excel to calculate a weighted projection using career average and current-season average.",
        "Use Python to simulate how small-sample hot streaks regress as more games are played."
    )


# =====================================================
# ENGINEERING + OPTIMIZATION
# =====================================================

elif domain == "Engineering + Optimization":
    section("Engineering + Optimization")

    math_frame(
        big_idea="""
        Engineering uses mathematics to design systems that work under constraints.

        Calculus models motion and change.
        Optimization finds efficient designs.
        Simulation tests systems before they are built.
        """,
        how_used="""
        Engineers use mathematical models for rockets, bridges, machines,
        traffic systems, energy systems, robotics, and autonomous vehicles.
        """,
        example="""
        Example: A rocket launch is not just about going upward.

        Engineers must optimize:
        - fuel
        - mass
        - velocity
        - trajectory
        - timing
        - gravitational effects
        """
    )

    st.subheader("Projectile Motion / Trajectory Model")

    velocity = st.slider("Initial velocity", 10, 200, 90)
    angle = st.slider("Launch angle", 10, 80, 45)
    gravity = 9.8

    angle_rad = np.radians(angle)
    t_flight = 2 * velocity * np.sin(angle_rad) / gravity
    t = np.linspace(0, t_flight, 200)

    x = velocity * np.cos(angle_rad) * t
    y = velocity * np.sin(angle_rad) * t - 0.5 * gravity * t ** 2

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Trajectory Simulation")
    ax.set_xlabel("Horizontal Distance")
    ax.set_ylabel("Height")
    ax.grid(True)
    st.pyplot(fig)

    st.metric("Approximate Range", f"{max(x):,.1f} meters")
    st.metric("Maximum Height", f"{max(y):,.1f} meters")

    st.markdown("""
    ### Interpretation

    This is a basic physics model, but the deeper idea is broader:

    Engineering problems often involve optimizing a system across many variables.
    Calculus gives the equations of motion.
    Optimization finds the best design.
    Simulation tests possible outcomes.
    """)

    show_practice_problem(
        "Engineering Practice Problem: Optimize Range",
        "For a fixed launch velocity, test different launch angles and find which angle maximizes horizontal range.",
        "Create an Excel table with angles from 5 to 85 degrees and calculate range for each angle.",
        "Use Python to graph angle vs range and identify the maximizing angle."
    )


# =====================================================
# SIMULATION THEORY
# =====================================================

elif domain == "Simulation Theory + Monte Carlo":
    section("Simulation Theory + Monte Carlo")

    math_frame(
        big_idea="""
        Simulation lets us study systems too complex for simple formulas.

        Instead of solving one exact equation, we generate many possible outcomes
        and study the distribution.
        """,
        how_used="""
        Monte Carlo methods are used in finance, medicine, sports, physics,
        AI, operations research, engineering, and risk analysis.
        """,
        example="""
        Example: Instead of asking, “What will happen?”

        A simulation asks:

        “What are the possible futures, and how likely are they?”
        """
    )

    st.subheader("Monte Carlo: Estimating π")

    n_points = st.slider("Number of random points", 100, 10000, 2000)

    x = np.random.uniform(-1, 1, n_points)
    y = np.random.uniform(-1, 1, n_points)

    inside = x ** 2 + y ** 2 <= 1
    pi_estimate = 4 * np.mean(inside)

    fig, ax = plt.subplots()
    ax.scatter(x[inside], y[inside], s=5, alpha=0.5, label="Inside Circle")
    ax.scatter(x[~inside], y[~inside], s=5, alpha=0.5, label="Outside Circle")
    ax.set_title("Monte Carlo Estimation of π")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.set_aspect("equal")
    st.pyplot(fig)

    st.metric("Estimated π", f"{pi_estimate:.5f}")

    st.markdown("""
    ### Interpretation

    This example is simple, but the method is powerful.

    The same logic can estimate:
    - investment risk
    - insurance losses
    - playoff odds
    - disease outcomes
    - engineering failure rates
    - AI model uncertainty
    """)

    show_practice_problem(
        "Simulation Practice Problem: Insurance Losses",
        "An insurance company wants to estimate total annual claims. Claim frequency and claim size are both random.",
        "Use Excel to simulate number of claims and average claim size across many years.",
        "Use Python to create a Monte Carlo model of total annual losses and calculate the 95th percentile loss."
    )


# =====================================================
# STATISTICS + PREDICTION
# =====================================================

elif domain == "Statistics + Prediction Systems":
    section("Statistics + Prediction Systems")

    math_frame(
        big_idea="""
        Statistics extracts signal from noise.

        It helps estimate hidden patterns, quantify uncertainty,
        and decide whether observed effects are meaningful.
        """,
        how_used="""
        Prediction systems use regression, classification, confidence intervals,
        hypothesis testing, correlation analysis, and Bayesian updating.
        """,
        example="""
        Example: A hospital wants to know whether a new treatment improves survival.

        Statistics helps decide whether the observed improvement is real
        or could plausibly be random variation.
        """
    )

    st.subheader("Regression With Noise")

    slope = st.slider("True relationship strength", -5.0, 5.0, 2.0)
    noise = st.slider("Noise level", 0.0, 30.0, 10.0)
    n = st.slider("Sample size", 20, 500, 100)

    x = np.random.uniform(0, 100, n)
    y = 25 + slope * x + np.random.normal(0, noise, n)

    coeffs = np.polyfit(x, y, 1)
    y_hat = coeffs[0] * x + coeffs[1]

    corr = np.corrcoef(x, y)[0, 1]

    fig, ax = plt.subplots()
    ax.scatter(x, y, alpha=0.6)
    ax.plot(np.sort(x), coeffs[0] * np.sort(x) + coeffs[1])
    ax.set_title("Regression Model With Noise")
    ax.set_xlabel("Input Variable")
    ax.set_ylabel("Outcome")
    ax.grid(True)
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    col1.metric("Estimated Slope", f"{coeffs[0]:.3f}")
    col2.metric("Correlation", f"{corr:.3f}")

    st.markdown("""
    ### Interpretation

    This shows why statistics matters.

    Real data is noisy.  
    The goal is not just to draw a line.  
    The goal is to estimate the hidden relationship beneath randomness.
    """)

    show_practice_problem(
        "Statistics Practice Problem: Predictive Model",
        "You have data on advertising spending and sales revenue. You want to estimate how much sales increase for each additional dollar of advertising.",
        "Use Excel scatterplots, correlation, and trendline equation.",
        "Use Python to fit a regression model and evaluate prediction error."
    )


# =====================================================
# EXCEL / PORTFOLIO PRACTICE
# =====================================================

elif domain == "Excel / Portfolio Practice Problems":
    section("Excel / Portfolio Practice Problems")

    st.markdown("""
    This section turns the app into a portfolio-building tool.

    The goal is not basic worksheets.  
    The goal is professional-style applied math practice that could be discussed in interviews.
    """)

    show_practice_problem(
        "1. Finance / Risk Simulation",
        "Model a portfolio with uncertain annual returns over 30 years.",
        "Use NORM.INV(RAND(), mean, standard deviation) to simulate yearly returns. Build 1,000 scenarios.",
        "Create a Python Monte Carlo simulation and calculate median, downside risk, and probability of loss."
    )

    show_practice_problem(
        "2. Actuarial Loss Modeling",
        "Estimate annual insurance losses using random claim counts and random claim sizes.",
        "Use Poisson-style frequency assumptions and average claim severity assumptions.",
        "Simulate total losses and calculate expected loss, standard deviation, and 95th percentile loss."
    )

    show_practice_problem(
        "3. Sports Projection Model",
        "Project player performance using career average, recent performance, age, and regression to the mean.",
        "Create weighted averages and age-adjusted projections.",
        "Build a Python function that outputs projected performance and uncertainty intervals."
    )

    show_practice_problem(
        "4. Medical Treatment Comparison",
        "Compare two treatments using patient-level outcome data.",
        "Calculate mean response, standard deviation, percent improvement, and confidence intervals.",
        "Run a statistical comparison and visualize the distribution of outcomes."
    )

    show_practice_problem(
        "5. AI Model Error Tracker",
        "Track how model error decreases over training rounds.",
        "Create columns for training round, prediction error, squared error, and moving average error.",
        "Simulate gradient descent and graph loss over time."
    )

    show_practice_problem(
        "6. Engineering Optimization",
        "Find the launch angle that maximizes projectile distance.",
        "Build a table of angles, horizontal distance, and max height.",
        "Use Python to optimize over a continuous range of possible angles."
    )

    st.success("""
    These problems can become separate Excel workbooks, Python notebooks, GitHub projects, or interview portfolio examples.
    """)


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.caption("Applied Mathematical Intelligence | Advanced Applied Math Systems Prototype")
