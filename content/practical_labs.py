"""Practical labs — action-first decision and simulation workspaces."""

PRACTICAL_LAB_NAMES = [
    "Investing & Wealth Lab",
    "Betting, Poker & Decision Lab",
    "Prediction & Forecasting Lab",
    "AI & Optimization Lab",
    "Strategy & Simulation Lab",
]

# Short action labels for navigation and home cards
ACTION_LABELS = {
    "Investing & Wealth Lab": "Invest money",
    "Betting, Poker & Decision Lab": "Analyze a bet",
    "Prediction & Forecasting Lab": "Forecast the future",
    "AI & Optimization Lab": "Train an AI",
    "Strategy & Simulation Lab": "Simulate a system",
}

PRACTICAL_LABS = {
    "Investing & Wealth Lab": {
        "icon": "📈",
        "action": "Invest money",
        "tagline": "Build a portfolio, stress-test risk, and compare long-term outcomes.",
        "goal": "Decide how to allocate capital when returns are uncertain and compounding matters.",
        "math_tools": ["Monte Carlo simulation", "Compounding", "Volatility", "Efficient frontier"],
        "tools": [
            {
                "name": "Portfolio simulator",
                "runner_id": "lab_finance",
                "description": "Set allocation, return, and volatility — see thousands of possible futures.",
            },
            {
                "name": "Risk & drawdown",
                "runner_id": "finance_quant_suite",
                "description": "Tail-risk distribution, efficient frontier, and drawdown paths.",
            },
        ],
        "practice_challenge": (
            "Allocate 60% stocks / 40% bonds with 9% / 4% expected returns. "
            "Run 15-year simulation — what is P(wealth below start)?"
        ),
        "related_domains": [
            "Quantitative Finance",
            "Hedge Funds & Alternative Risk",
            "Actuarial Science",
            "Simulation & Monte Carlo Methods",
        ],
    },
    "Betting, Poker & Decision Lab": {
        "icon": "♠",
        "action": "Analyze a bet",
        "tagline": "Test whether a call, fold, or wager is mathematically sound.",
        "goal": "Make decisions under uncertainty using expected value, pot odds, and bankroll math.",
        "math_tools": ["Expected value", "Pot odds", "Kelly criterion", "Implied probability"],
        "tools": [
            {
                "name": "Poker decision simulator",
                "runner_id": "lab_poker",
                "description": "Call, fold, or raise — get EV feedback and Kelly sizing.",
            },
            {
                "name": "Sports bet analyzer",
                "runner_id": "lab_sports_betting",
                "description": "Convert odds, compute edge, simulate a betting season.",
            },
            {
                "name": "Casino edge explorer",
                "runner_id": "casino_edge",
                "description": "See how house edge grinds bankroll over many bets.",
            },
        ],
        "practice_challenge": (
            "Win probability 42%, pot $180, call $70. Calculate EV and pot odds by hand, "
            "then verify in the poker simulator."
        ),
        "related_domains": [
            "Gambling, Poker & Decision Mathematics",
            "Casino Mathematics",
            "Sports Analytics",
            "Fantasy Sports",
        ],
    },
    "Prediction & Forecasting Lab": {
        "icon": "📊",
        "action": "Forecast the future",
        "tagline": "Fit trends, quantify uncertainty, and stress-test predictions.",
        "goal": "Produce forecasts you can defend — with confidence intervals, not false precision.",
        "math_tools": ["Regression", "Confidence intervals", "Signal vs noise", "Scenario simulation"],
        "tools": [
            {
                "name": "Trend forecaster",
                "runner_id": "lab_forecasting",
                "description": "Generate noisy data, fit a trend, forecast with uncertainty bands.",
            },
            {
                "name": "Election scenario model",
                "runner_id": "election_forecast",
                "description": "Simulate swing-state outcomes and electoral vote totals.",
            },
            {
                "name": "Weather uncertainty cone",
                "runner_id": "weather_uncertainty_cone",
                "description": "Explore forecast spread as lead time increases.",
            },
            {
                "name": "Sports rating shrinkage",
                "runner_id": "sports_shrinkage",
                "description": "Adjust team estimates toward the mean with limited data.",
            },
        ],
        "practice_challenge": (
            "In the trend forecaster, set noise σ=20 and n=50. "
            "How wide are the 95% bands 10 steps ahead vs 30 steps?"
        ),
        "related_domains": [
            "Election Forecasting",
            "Weather Forecasting",
            "Sports Analytics",
            "Statistics & Prediction Systems",
        ],
    },
    "AI & Optimization Lab": {
        "icon": "🧠",
        "action": "Train an AI",
        "tagline": "Watch models learn, tune parameters, and optimize under constraints.",
        "goal": "Understand what AI is optimizing — and how gradient descent finds better solutions.",
        "math_tools": ["Gradient descent", "Loss minimization", "Constraint optimization", "Learning rate"],
        "tools": [
            {
                "name": "AI training playground",
                "runner_id": "lab_ai_training",
                "description": "Adjust learning rate and steps — watch loss decrease on a surface.",
            },
            {
                "name": "Neural network trainer",
                "runner_id": "ai_ml_suite",
                "description": "Toy network learning a decision boundary with backpropagation.",
            },
            {
                "name": "Resource optimizer",
                "runner_id": "lab_optimization",
                "description": "Allocate budget across projects under a risk constraint.",
            },
        ],
        "practice_challenge": (
            "Set learning rate 0.08 and 60 steps in the AI playground. "
            "Then try 0.25 — does the path diverge?"
        ),
        "related_domains": [
            "Artificial Intelligence",
            "Machine Learning",
            "Robotics",
            "Internet Recommendation Systems",
        ],
    },
    "Strategy & Simulation Lab": {
        "icon": "🔬",
        "action": "Simulate a system",
        "tagline": "Run what-if scenarios, compare choices, and explore alternate futures.",
        "goal": "Model complex systems when closed-form answers fail — disease, supply chains, losses.",
        "math_tools": ["Monte Carlo", "Differential equations", "Stochastic simulation", "Scenario analysis"],
        "tools": [
            {
                "name": "Disease spread (SIR)",
                "runner_id": "epidemic_sir",
                "description": "Adjust transmission and recovery — see epidemic curves.",
            },
            {
                "name": "Supply chain stress test",
                "runner_id": "supply_chain",
                "description": "Stochastic demand and lead times — count stockout days.",
            },
            {
                "name": "Insurance loss model",
                "runner_id": "actuarial_losses",
                "description": "Simulate aggregate claims and tail percentiles.",
            },
            {
                "name": "Monte Carlo explorer",
                "runner_id": "monte_carlo_pi",
                "description": "Random sampling converging on a stable estimate.",
            },
        ],
        "practice_challenge": (
            "In the SIR model, raise β from 0.45 to 0.65. "
            "How does peak infectious change? What policy lever is γ?"
        ),
        "related_domains": [
            "Epidemiology",
            "Supply Chain Optimization",
            "Actuarial Science",
            "Climate Modeling",
        ],
    },
}

NUM_PRACTICAL_LABS = len(PRACTICAL_LAB_NAMES)

# Map action label → lab name for navigation
ACTION_TO_LAB = {ACTION_LABELS[name]: name for name in PRACTICAL_LAB_NAMES}
