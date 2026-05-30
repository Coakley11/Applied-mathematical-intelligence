"""Idea & Invention Analysis — mathematical brainstorming for concepts and strategies."""

IDEA_ANALYSIS = {
    "title": "Idea & Invention Analysis",
    "icon": "💡",
    "action": "Analyze an Idea",
    "tagline": "Mathematical brainstorming — what to model, measure, and optimize.",
    "intro": (
        "Bring a business idea, invention, strategy, machine, or system. "
        "This lab helps you think about it mathematically: what variables matter, "
        "what data you need, what could be modeled, and which tools apply."
    ),
}

ANALYSIS_DIMENSIONS = [
    {
        "title": "What variables matter?",
        "description": "Identify the quantities that drive success or failure.",
        "prompts": [
            "What is the core output you care about (revenue, accuracy, speed, survival rate)?",
            "What inputs control that output?",
            "Which variables are you ignoring that might matter?",
        ],
    },
    {
        "title": "What data is needed?",
        "description": "Determine what measurements would validate or improve the idea.",
        "prompts": [
            "What would you need to measure to know if this works?",
            "Do you have historical data, or do you need to run experiments?",
            "What is the minimum viable dataset to test the core hypothesis?",
        ],
    },
    {
        "title": "What could be optimized?",
        "description": "Find the levers where mathematics can improve outcomes.",
        "prompts": [
            "What tradeoffs exist (cost vs. quality, speed vs. accuracy)?",
            "Is there a resource allocation problem (time, money, attention)?",
            "Can you define a clear objective function?",
        ],
    },
    {
        "title": "What could be modeled?",
        "description": "Identify which parts of the system can be represented mathematically.",
        "prompts": [
            "Does the system change over time (growth, decay, accumulation)?",
            "Are outcomes uncertain (probabilistic)?",
            "Are there feedback loops or network effects?",
        ],
    },
    {
        "title": "What mathematical tools are useful?",
        "description": "Match problem structure to the right mathematical approach.",
        "prompts": [
            "Prediction problem → statistics, regression, machine learning",
            "Decision under uncertainty → probability, expected value, simulation",
            "Best choice problem → optimization, constraints, tradeoff analysis",
            "Dynamic system → calculus, differential equations, simulation",
        ],
    },
]

# Keyword-based hints for brainstorming (no external API)
IDEA_KEYWORDS = {
    "betting|poker|gambl|wager|odds|casino": {
        "variables": "Win probability, pot size, bet size, bankroll, opponent tendencies",
        "data": "Hand histories, odds offered, long-term ROI tracking",
        "optimize": "Bet sizing (Kelly criterion), hand selection thresholds, bluff frequency",
        "model": "Expected value calculations, variance modeling, Monte Carlo bankroll simulation",
        "tools": "Probability, expected value, game theory, optimization (Kelly)",
        "labs": "Analyze a Bet, Predict a Game",
    },
    "sport|game|team|player|forecast|predict": {
        "variables": "Team strength, sample size, home advantage, injury status, schedule strength",
        "data": "Historical results, player stats, betting market odds",
        "optimize": "Rating systems, forecast models, bet sizing when edge detected",
        "model": "Elo/rating systems, regression, shrinkage toward mean",
        "tools": "Statistics, probability, regression, forecasting",
        "labs": "Predict a Game",
    },
    "health|medic|cancer|tumor|drug|disease|treatment|clinical": {
        "variables": "Growth rate, treatment efficacy, drug concentration, side effects, population spread",
        "data": "Clinical trial results, patient biomarkers, epidemiological data",
        "optimize": "Dose scheduling, treatment protocols, resource allocation",
        "model": "SIR epidemic models, tumor growth ODEs, pharmacokinetics",
        "tools": "Calculus, statistics, differential equations, optimization",
        "labs": "Model a Disease",
    },
    "ai|machine learning|neural|model train|deep learn|algorithm": {
        "variables": "Loss, learning rate, model parameters, training data size, validation accuracy",
        "data": "Labeled training set, validation set, test set",
        "optimize": "Weight updates via gradient descent, hyperparameter tuning, architecture search",
        "model": "Loss functions, gradient flow, generalization bounds",
        "tools": "Calculus (gradients), linear algebra, statistics, optimization",
        "labs": "Train an AI",
    },
    "weather|forecast|climate|temperature|storm": {
        "variables": "Initial conditions, model parameters, lead time, ensemble spread",
        "data": "Historical observations, satellite data, model outputs",
        "optimize": "Ensemble weighting, data assimilation, lead time vs. accuracy tradeoff",
        "model": "Chaos dynamics, uncertainty cones, trend fitting with confidence bands",
        "tools": "Statistics, simulation, differential equations, probability",
        "labs": "Forecast Weather (Advanced reference)",
    },
    "space|orbit|rocket|traject|planet|satellite|astro": {
        "variables": "Velocity, mass, gravitational parameters, fuel, trajectory angle",
        "data": "Orbital measurements, telemetry, observational astronomy data",
        "optimize": "Fuel-optimal trajectories, launch windows, orbital transfers",
        "model": "Newtonian mechanics, orbital equations, N-body simulation",
        "tools": "Calculus, physics, numerical simulation, optimization",
        "labs": "Explore Space Motion (Advanced reference)",
    },
    "business|startup|revenue|market|customer|sales|profit": {
        "variables": "Conversion rate, customer acquisition cost, lifetime value, churn, pricing",
        "data": "Sales history, A/B test results, market research, cohort analysis",
        "optimize": "Pricing, ad spend allocation, inventory, staffing levels",
        "model": "Growth curves, cohort models, demand forecasting, unit economics",
        "tools": "Statistics, optimization, regression, simulation",
        "labs": "Optimize a Decision, Analyze an Idea",
    },
    "traffic|transport|route|logistic|supply chain|delivery": {
        "variables": "Flow rate, capacity, travel time, cost per mile, demand patterns",
        "data": "Traffic sensors, delivery records, GPS traces, demand history",
        "optimize": "Route planning, fleet allocation, warehouse location, scheduling",
        "model": "Network flow, queueing theory, vehicle routing problems",
        "tools": "Optimization, graph theory, simulation, statistics",
        "labs": "Optimize a Decision",
    },
    "invent|machine|device|engineer|design|hardware|product": {
        "variables": "Efficiency, material properties, dimensions, operating conditions, cost",
        "data": "Prototype measurements, material specs, stress tests, user feedback",
        "optimize": "Design parameters, material selection, operating point",
        "model": "Physics equations, finite element analysis, tolerance analysis",
        "tools": "Calculus, optimization, simulation, statistics (quality control)",
        "labs": "Optimize a Decision",
    },
    "invest|portfolio|stock|finance|trading|asset": {
        "variables": "Return, risk, correlation, liquidity, transaction costs",
        "data": "Price history, fundamentals, macro indicators",
        "optimize": "Portfolio weights, rebalancing, risk budgeting",
        "model": "Mean-variance optimization, factor models, Monte Carlo scenarios",
        "tools": "Statistics, optimization, probability, simulation",
        "labs": "Optimize a Decision, Advanced reference",
    },
}

DEFAULT_IDEA_HINTS = {
    "variables": "Start by naming the core output and the inputs you can control",
    "data": "What single measurement would tell you if the idea is working?",
    "optimize": "Look for tradeoffs — where does improving one thing hurt another?",
    "model": "Does the system change over time, involve uncertainty, or require a best choice?",
    "tools": "Prediction → statistics; Decision → probability; Best choice → optimization; Change over time → calculus",
    "labs": "Explore Mathematical Thinking, Optimize a Decision",
}
