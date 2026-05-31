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
        "start_here": "Pick a tool below, set your numbers, and run the simulation. The app tells you whether the decision is worth it long-term.",
        "start_steps": [
            "Open **Is This Call Worth It?** for poker decisions.",
            "Enter pot size, call amount, and your win chance.",
            "Read the verdict — positive expected value means the call wins over time.",
        ],
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
        "start_here": "Start with **Is This Bet Worth It?** — enter the odds and your estimated win chance to see if there's an edge.",
        "start_steps": [
            "Convert betting odds to an implied probability.",
            "Compare that to your own win estimate.",
            "If your estimate is higher, the bet may have positive expected value.",
        ],
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
        "start_here": "Pick a scenario — disease outbreak, tumor vs treatment, or drug levels — then move the sliders and watch what changes.",
        "start_steps": [
            "Open **Disease Spread Simulator** to model an outbreak.",
            "Adjust infection and recovery rates.",
            "See how many people are susceptible, infected, or recovered over time.",
        ],
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
        "start_here": "Open **How AI Learns**, pick a learning rate, and watch the model improve step by step.",
        "start_steps": [
            "Start with a moderate learning rate.",
            "Run training and watch the loss drop.",
            "Try too high or too low — see why the rate matters.",
        ],
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

# ---------------------------------------------------------------------------
# Primary navigation (sidebar + home action cards)
# ---------------------------------------------------------------------------

PRIMARY_ACTIONS = [
    "Solve a Problem",
    "Analyze a Bet",
    "Predict a Game",
    "Model a Disease",
    "Train an AI",
    "Optimize a Decision",
    "Analyze an Idea",
]

PRIMARY_ACTION_TAGLINES = {
    "Solve a Problem": "Seven areas — betting, sports, medicine, AI, space, forecasting, abstract.",
    "Analyze a Bet": "Is this call or wager worth it?",
    "Predict a Game": "Find edge in odds and forecasts.",
    "Model a Disease": "Simulate spread, growth, and treatment.",
    "Train an AI": "Watch a model learn in real time.",
    "Optimize a Decision": "Improve a strategy or process.",
    "Analyze an Idea": "See what to measure and model.",
}

PRIMARY_ACTION_DESCRIPTIONS = {
    "Solve a Problem": "Describe your problem — get guided questions, not instant answers.",
    "Analyze a Bet": "Run expected-value checks on poker calls and casino bets.",
    "Predict a Game": "Compare win probabilities to the odds on the board.",
    "Model a Disease": "Explore outbreaks, tumor growth, and drug levels.",
    "Train an AI": "Adjust learning rate and watch training unfold.",
    "Optimize a Decision": "Pick a problem, define the goal, try an optimizer.",
    "Analyze an Idea": "Type an idea — get variables, data, and next steps.",
}

PRIMARY_ACTION_ICONS = {
    "Solve a Problem": "🧠",
    "Analyze a Bet": PRACTICAL_LABS["Betting & Poker Lab"]["icon"],
    "Predict a Game": PRACTICAL_LABS["Sports Prediction Lab"]["icon"],
    "Model a Disease": PRACTICAL_LABS["Medicine & Disease Lab"]["icon"],
    "Train an AI": PRACTICAL_LABS["AI Learning Lab"]["icon"],
    "Optimize a Decision": "⚙",
    "Analyze an Idea": "💡",
}

PRIMARY_ACTION_LABELS = {
    "Solve a Problem": "Mathematical Problem Solving Lab",
    "Analyze a Bet": "Betting & Poker Lab",
    "Predict a Game": "Sports Prediction Lab",
    "Model a Disease": "Medicine & Disease Lab",
    "Train an AI": "AI Learning Lab",
    "Optimize a Decision": "Optimization Workshop",
    "Analyze an Idea": "Idea & Invention Analysis",
}

ACTION_SECTION_TYPES = {
    "Solve a Problem": "problem_solving",
    "Analyze a Bet": "lab",
    "Predict a Game": "lab",
    "Model a Disease": "lab",
    "Train an AI": "lab",
    "Optimize a Decision": "optimization",
    "Analyze an Idea": "idea",
}

NAV_HELP = {
    "Home": "Pick a problem and jump in.",
    "Solve a Problem": "Pick an area → ask a quantitative question → work the math.",
    "Analyze a Bet": "Check expected value and pot odds.",
    "Predict a Game": "Compare probabilities to betting odds.",
    "Model a Disease": "Simulate spread, tumors, and drug levels.",
    "Train an AI": "Watch gradient descent train a model.",
    "Optimize a Decision": "Define your goal and find the best mix.",
    "Analyze an Idea": "Brainstorm variables, data, and tools.",
    "Advanced reference": "Optional reading — skip if you're just getting started.",
}

NUM_PRIMARY_ACTIONS = len(PRIMARY_ACTIONS)

# Sidebar action label → lab name (primary simulation labs only)
ACTION_TO_LAB = {
    ACTION_LABELS[name]: name
    for name in PRACTICAL_LABS
    if name not in SECONDARY_LAB_NAMES
}
