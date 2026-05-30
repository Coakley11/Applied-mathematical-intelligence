"""Practical labs — guided decision and simulation workspaces."""

# Primary simulation labs (featured in main navigation)
PRIMARY_LAB_NAMES = [
    "Betting & Poker Lab",
    "Sports Prediction Lab",
    "Medicine & Disease Lab",
    "AI Learning Lab",
]

# Additional labs — accessible via Advanced reference
SECONDARY_LAB_NAMES = [
    "Weather & Forecasting Lab",
    "Space & Motion Lab",
    "Math Behind the Systems",
]

PRACTICAL_LAB_NAMES = PRIMARY_LAB_NAMES + SECONDARY_LAB_NAMES

ACTION_LABELS = {
    "Betting & Poker Lab": "Analyze a Bet",
    "Sports Prediction Lab": "Predict a Game",
    "Medicine & Disease Lab": "Model a Disease",
    "AI Learning Lab": "Train an AI",
    "Weather & Forecasting Lab": "Forecast Weather",
    "Space & Motion Lab": "Explore Space Motion",
    "Math Behind the Systems": "Understand the Math",
}

# What the user can actually do — shown on home cards
ACTION_DESCRIPTIONS = {
    "Betting & Poker Lab": "Check if a poker call or bet is mathematically worth it using expected value and pot odds.",
    "Sports Prediction Lab": "Compare team win probabilities to odds, adjust ratings, and forecast outcomes.",
    "Medicine & Disease Lab": "Simulate disease spread, tumor growth, and drug concentration in the body.",
    "AI Learning Lab": "Watch AI learn through gradient descent and train a mini neural network.",
    "Weather & Forecasting Lab": "See why forecasts get less certain over time and fit trends with confidence bands.",
    "Space & Motion Lab": "Predict orbits, detect planets from starlight dips, and calculate trajectories.",
    "Math Behind the Systems": "Explore how calculus, probability, statistics, and optimization power the labs.",
}

PRACTICAL_LABS = {
    "Betting & Poker Lab": {
        "icon": "♠",
        "action": "Analyze a Bet",
        "tagline": "Is this call or wager mathematically worth it?",
        "intro": (
            "Use expected value and pot odds to check poker decisions and casino bets. "
            "The math tells you what wins long-term — not what happens on one hand."
        ),
        "tools": [
            {"name": "Is This Call Worth It?", "runner_id": "lab_poker"},
            {"name": "Why the House Always Wins", "runner_id": "casino_edge"},
        ],
        "related_domains": [
            "Gambling, Poker & Decision Mathematics",
            "Casino Mathematics",
        ],
    },
    "Sports Prediction Lab": {
        "icon": "🏈",
        "action": "Predict a Game",
        "tagline": "Compare probabilities, find edge, and forecast team performance.",
        "intro": (
            "Translate odds into probabilities, check if a bet has positive expected value, "
            "and adjust team ratings when sample sizes are small."
        ),
        "tools": [
            {"name": "Is This Bet Worth It?", "runner_id": "lab_sports_betting"},
            {"name": "Separate Signal from Noise", "runner_id": "sports_shrinkage"},
            {"name": "Forecast a Trend", "runner_id": "lab_forecasting"},
        ],
        "related_domains": [
            "Sports Analytics",
            "Fantasy Sports",
            "Statistics & Prediction Systems",
        ],
    },
    "Medicine & Disease Lab": {
        "icon": "🧬",
        "action": "Model a Disease",
        "tagline": "Simulate outbreaks, tumor growth, and drug levels in the body.",
        "intro": (
            "See how diseases spread through populations, whether treatment beats tumor growth, "
            "and how drug concentration changes over time."
        ),
        "tools": [
            {"name": "Disease Spread Simulator", "runner_id": "epidemic_sir"},
            {"name": "Tumor Growth vs Treatment", "runner_id": "tumor_growth"},
            {"name": "Drug Concentration Over Time", "runner_id": "pharmacokinetics"},
        ],
        "related_domains": [
            "Epidemiology",
            "Medicine & Biological Modeling",
            "Drug Development & Pharmacokinetics",
        ],
    },
    "AI Learning Lab": {
        "icon": "🧠",
        "action": "Train an AI",
        "tagline": "Watch models learn and see what optimization actually does.",
        "intro": (
            "AI learns by minimizing error — gradient descent is the engine. "
            "Adjust learning rate and training steps to see convergence in action."
        ),
        "tools": [
            {"name": "How AI Learns", "runner_id": "lab_ai_training"},
            {"name": "Train a Mini Neural Network", "runner_id": "ai_ml_suite"},
        ],
        "related_domains": [
            "Artificial Intelligence",
            "Machine Learning",
        ],
    },
    "Weather & Forecasting Lab": {
        "icon": "🌤",
        "action": "Forecast Weather",
        "tagline": "Explore uncertainty cones and trend forecasting.",
        "intro": (
            "Forecasts are probabilistic, not certain. See how uncertainty grows with lead time "
            "and how to fit trends through noisy data."
        ),
        "tools": [
            {"name": "Why Forecasts Get Less Certain", "runner_id": "weather_uncertainty_cone"},
            {"name": "Separate Signal from Noise", "runner_id": "lab_forecasting"},
        ],
        "related_domains": [
            "Weather Forecasting",
            "Statistics & Prediction Systems",
        ],
    },
    "Space & Motion Lab": {
        "icon": "🚀",
        "action": "Explore Space Motion",
        "tagline": "Predict orbits, detect planets, and calculate trajectories.",
        "intro": (
            "Space missions depend on orbital mechanics and precise trajectory math. "
            "Explore how astronomers detect planets and how objects move under gravity."
        ),
        "tools": [
            {"name": "Predict an Orbit", "runner_id": "orbital_mechanics"},
            {"name": "Detect a Planet by Its Shadow", "runner_id": "exoplanet_transit"},
            {"name": "Calculate a Trajectory", "runner_id": "projectile"},
        ],
        "related_domains": [
            "Astronomy & Astrophysics",
            "Space Exploration",
        ],
    },
    "Math Behind the Systems": {
        "icon": "📐",
        "action": "Understand the Math",
        "tagline": "See how calculus, probability, statistics, and optimization connect to real problems.",
        "intro": (
            "Every lab uses mathematical systems — accumulation, uncertainty, pattern detection, "
            "optimization, simulation, and learning. Explore the tools and ideas behind them."
        ),
        "tools": [
            {"name": "Run Many Possible Futures", "runner_id": "monte_carlo_pi"},
            {"name": "Find the Best Decision", "runner_id": "lab_optimization"},
        ],
        "is_math_hub": True,
        "related_domains": [],
    },
}

NUM_PRACTICAL_LABS = len(PRACTICAL_LAB_NAMES)
ACTION_TO_LAB = {ACTION_LABELS[name]: name for name in PRACTICAL_LAB_NAMES}
