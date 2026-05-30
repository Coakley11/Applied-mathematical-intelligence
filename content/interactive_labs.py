"""Interactive Labs — hands-on mathematical reasoning modules."""

LAB_NAMES = [
    "Poker Strategy Lab",
    "Sports Betting Lab",
    "Finance & Investing Lab",
    "Forecasting Lab",
    "Optimization Lab",
    "AI Training Lab",
]

INTERACTIVE_LABS = {
    "Poker Strategy Lab": {
        "icon": "♠",
        "badge": "Probability",
        "tagline": "Decide when to call, fold, or raise using expected value and pot odds.",
        "goal": "Evaluate a poker decision and see whether the math supports your action.",
        "math_idea": (
            "**Expected value (EV)** compares what you gain when you win against what you lose "
            "when you lose. **Pot odds** tell you the minimum win rate needed to justify a call. "
            "**Kelly criterion** sizes bets so you grow bankroll without risking ruin."
        ),
        "skill": "Decision-making under uncertainty — the same logic used in trading, insurance, and risk management.",
        "practice_challenge": (
            "Set win probability to 35%, pot to $200, call cost to $80. Calculate EV by hand, "
            "then compare pot odds to your equity. Would you call, fold, or raise?"
        ),
        "portfolio_project": (
            "Build a **Poker EV Calculator** in Python or Excel: inputs for win %, pot size, and "
            "call cost; outputs EV, pot odds, and a Kelly bet fraction. Add a simple Monte Carlo "
            "simulator showing bankroll paths under different sizing rules."
        ),
        "runner_id": "lab_poker",
    },
    "Sports Betting Lab": {
        "icon": "🏈",
        "badge": "Statistics",
        "tagline": "Compare teams, convert odds, and find bets with positive expected value.",
        "goal": "Determine whether a wager is mathematically favorable before you commit money.",
        "math_idea": (
            "**Implied probability** converts bookmaker odds into a win chance. "
            "**Expected value** = (win prob × profit) − (lose prob × stake). "
            "A positive EV bet is favorable long-term — but variance still causes losing streaks."
        ),
        "skill": "Translating odds into probabilities and separating edge from luck.",
        "practice_challenge": (
            "Team A has a 58% true win probability. Decimal odds are 1.85. "
            "Is this bet +EV on a $100 stake? What if odds were 1.70?"
        ),
        "portfolio_project": (
            "Create a **Sports EV Dashboard**: ingest win probabilities and market odds, "
            "flag +EV opportunities, and simulate a season of bets to show variance vs edge."
        ),
        "runner_id": "lab_sports_betting",
    },
    "Finance & Investing Lab": {
        "icon": "📈",
        "badge": "Simulation",
        "tagline": "Build a portfolio, run Monte Carlo paths, and compare risk vs reward.",
        "goal": "See how expected return, volatility, and time horizon shape long-term wealth outcomes.",
        "math_idea": (
            "Investment growth compounds small returns over time (calculus-like accumulation). "
            "**Monte Carlo simulation** generates thousands of possible futures. "
            "**Volatility** widens the distribution — higher return often means higher risk of loss."
        ),
        "skill": "Quantitative risk assessment — used by portfolio managers, actuaries, and CFOs.",
        "practice_challenge": (
            "Set expected return to 8%, volatility to 20%, and horizon to 20 years. "
            "What is the probability of ending below your starting capital? "
            "How does halving volatility change the 5th percentile outcome?"
        ),
        "portfolio_project": (
            "Build a **Portfolio Monte Carlo Tool** in Python: user inputs allocation, "
            "expected returns, and volatilities; outputs wealth distribution, VaR, and drawdown stats."
        ),
        "runner_id": "lab_finance",
    },
    "Forecasting Lab": {
        "icon": "📊",
        "badge": "Statistics",
        "tagline": "Fit a trend to noisy data and forecast the future with uncertainty bands.",
        "goal": "Separate signal from noise and produce a forecast you can defend with math.",
        "math_idea": (
            "**Linear regression** finds the best-fit trend through noisy observations. "
            "**R²** measures how much variance the trend explains. "
            "Forecast uncertainty grows with noise and with how far you extrapolate."
        ),
        "skill": "Evidence-based prediction — core to analytics, epidemiology, and business planning.",
        "practice_challenge": (
            "Generate data with slope 3 and noise σ=15. Increase sample size from 30 to 200. "
            "How does the estimated slope change? When does the forecast become trustworthy?"
        ),
        "portfolio_project": (
            "Build a **Forecasting Notebook**: load or generate time-series data, fit OLS trend, "
            "plot confidence bands, and backtest forecast error over a holdout period."
        ),
        "runner_id": "lab_forecasting",
    },
    "Optimization Lab": {
        "icon": "⚙",
        "badge": "Optimization",
        "tagline": "Allocate resources across options to maximize return under constraints.",
        "goal": "Find the best allocation when you cannot have everything — tradeoffs are real.",
        "math_idea": (
            "An **objective function** defines what you want to maximize (return, efficiency, profit). "
            "**Constraints** limit choices (budget, risk cap, capacity). "
            "The optimal solution sits where improving one goal would violate a constraint."
        ),
        "skill": "Structured decision-making — used in logistics, engineering, AI training, and finance.",
        "practice_challenge": (
            "You have $10,000 to split across three projects with returns 6%, 10%, and 14% "
            "and risk scores 2, 5, and 8. Maximize return while keeping average risk ≤ 5."
        ),
        "portfolio_project": (
            "Implement a **Resource Allocation Optimizer** using scipy or Excel Solver: "
            "multiple investments, budget constraint, and a risk ceiling. Visualize the efficient frontier."
        ),
        "runner_id": "lab_optimization",
    },
    "AI Training Lab": {
        "icon": "🧠",
        "badge": "AI / Calculus",
        "tagline": "Adjust learning rate and training steps to watch a model learn in real time.",
        "goal": "Understand how gradient descent minimizes loss — the engine behind modern AI.",
        "math_idea": (
            "**Gradient descent** moves parameters downhill on a loss surface (calculus: derivatives). "
            "**Learning rate** controls step size — too high diverges, too low crawls. "
            "**Noise** in data creates a bumpy landscape; optimization finds a good minimum anyway."
        ),
        "skill": "Understanding how AI models actually learn — essential for ML engineers and analysts.",
        "practice_challenge": (
            "Start with learning rate 0.3 and 20 steps — does the path converge? "
            "Drop to 0.05 and increase to 100 steps. Compare final loss values."
        ),
        "portfolio_project": (
            "Build a **Training Visualizer**: animate gradient descent on a 2D loss surface, "
            "compare learning rates, and plot loss vs epoch for a small neural network."
        ),
        "runner_id": "lab_ai_training",
    },
}

NUM_LABS = len(LAB_NAMES)
