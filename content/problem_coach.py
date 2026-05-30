"""Problem coach — scoring, experts, challenges, and problem library."""

EXPERT_PERSPECTIVES = [
    {
        "role": "Mathematician",
        "icon": "📐",
        "primary_concern": "Structure and abstraction",
        "questions": [
            "What structure exists beneath this messy situation?",
            "What can be modeled with variables and relationships?",
            "What can be simplified without losing the core mechanism?",
        ],
        "lens": "Looks for abstract structure — the same math appears in many domains.",
        "personality": "Strips away noise to find the core relationship. Asks: 'What's the simplest true model?'",
    },
    {
        "role": "Statistician",
        "icon": "📊",
        "primary_concern": "Data quality and uncertainty",
        "questions": [
            "What uncertainty exists in your estimates?",
            "What data would you need to reduce that uncertainty?",
            "How much of what you see is signal vs. random noise?",
        ],
        "lens": "Focuses on data quality, sample size, and honest uncertainty ranges.",
        "personality": "Demands evidence and sample sizes. Won't trust a claim without error bars.",
    },
    {
        "role": "Actuary",
        "icon": "🛡",
        "primary_concern": "Tail risk and long-run survival",
        "questions": [
            "What risks matter most — especially tail risks?",
            "What distributions describe the possible outcomes?",
            "Can the system survive a bad scenario, not just an average one?",
        ],
        "lens": "Thinks in distributions and long-run solvency, not single outcomes.",
        "personality": "Plans for the worst case, not just the average. Asks: 'Can you survive a bad year?'",
    },
    {
        "role": "Data Scientist",
        "icon": "🔬",
        "primary_concern": "Generalization and feature relevance",
        "questions": [
            "What features (variables) actually drive the outcome?",
            "What predictions can you make and test on new data?",
            "Would your approach work out-of-sample, or only on history?",
        ],
        "lens": "Separates patterns that generalize from patterns that overfit.",
        "personality": "Obsessed with holdout validation. Distrusts anything that only works on training data.",
    },
    {
        "role": "AI Researcher",
        "icon": "🤖",
        "primary_concern": "Objective function and learnability",
        "questions": [
            "What objective (loss function) are you implicitly optimizing?",
            "What patterns could be learned automatically from data?",
            "How would you know if the model failed on new examples?",
        ],
        "lens": "Frames problems as optimization — find parameters that minimize error.",
        "personality": "Asks what you're optimizing and whether the data supports learning that target.",
    },
    {
        "role": "Engineer",
        "icon": "⚙",
        "primary_concern": "Feasibility and constraints",
        "questions": [
            "What are the physical or operational constraints?",
            "What tolerances and safety margins apply?",
            "Can you build, test, and iterate a prototype cheaply?",
        ],
        "lens": "Focuses on feasibility, constraints, and building something that works in reality.",
        "personality": "Wants something that works in the real world, not just on paper. Prototype fast, measure always.",
        "approach": "Define requirements → model constraints → prototype → measure → iterate.",
    },
]

# Add approach field to existing experts for comparison view
for _expert in EXPERT_PERSPECTIVES:
    if "approach" not in _expert:
        _expert["approach"] = _expert["lens"]

CHALLENGE_QUESTIONS = [
    {
        "id": "assumptions",
        "question": "What assumptions are you making that might not be true?",
        "coach": "Every model assumes something. Name yours so you can test them.",
    },
    {
        "id": "missing_info",
        "question": "What information might be missing from your analysis?",
        "coach": "Missing data often hides in plain sight — confounders, selection bias, unknown unknowns.",
    },
    {
        "id": "could_go_wrong",
        "question": "What could go wrong if you're wrong?",
        "coach": "Tail risks and downside scenarios deserve explicit thought.",
    },
    {
        "id": "test_idea",
        "question": "How would you test this idea with real data or a small experiment?",
        "coach": "A falsifiable test separates thinking from guessing.",
    },
    {
        "id": "model_wrong",
        "question": "How would you know if your model is wrong?",
        "coach": "Define what result would surprise you enough to change course.",
    },
]

PROBLEM_LIBRARY = [
    {
        "category": "Betting",
        "icon": "♠",
        "title": "Is this bet worth making?",
        "problem": "I found a bet at +150 odds and think my team has a 45% chance to win. Should I bet?",
        "thinking": "First clarify the question: not 'will I win?' but 'does this bet have positive expected value long-term?'",
        "model": "Compare your 45% estimate to the implied probability from +150 odds (~40%). If yours is higher, EV may be positive.",
        "math_link": "Expected value = P(win) × profit − P(lose) × stake. Probability converts odds to a fair benchmark.",
        "lab": "Analyze a Bet",
    },
    {
        "category": "Sports",
        "icon": "🏈",
        "title": "How would you predict next season?",
        "problem": "I want to forecast how my favorite baseball team will perform next season.",
        "thinking": "Separate true talent from luck in last season's results. Small samples exaggerate extremes.",
        "model": "Start with a baseline (league average), adjust for roster changes, shrink last year's stats toward the mean.",
        "math_link": "Regression to the mean and shrinkage estimators prevent overreacting to noise.",
        "lab": "Predict a Game",
    },
    {
        "category": "Medicine",
        "icon": "🧬",
        "title": "How would you evaluate a new treatment?",
        "problem": "A new cancer drug shrinks tumors in 60% of trial patients. Is it working?",
        "thinking": "Compared to what? You need a control group. Ask about side effects and duration, not just response rate.",
        "model": "Compare treatment vs. control survival or tumor volume over time — not just a single percentage.",
        "math_link": "Growth vs. kill rates (calculus), trial statistics, and tradeoffs between efficacy and toxicity.",
        "lab": "Model a Disease",
    },
    {
        "category": "AI",
        "icon": "🧠",
        "title": "How would you improve prediction accuracy?",
        "problem": "My AI model gets 85% accuracy on training data but only 70% on new data.",
        "thinking": "The gap screams overfitting. The model memorized training noise instead of learning general patterns.",
        "model": "Minimize loss on held-out validation data, not training data. Simpler model or more regularization.",
        "math_link": "Optimization (gradient descent), loss functions, and the bias-variance tradeoff.",
        "lab": "Train an AI",
    },
    {
        "category": "Business",
        "icon": "💼",
        "title": "How would you increase profits?",
        "problem": "I run an online store and want to increase profit without raising prices.",
        "thinking": "Profit = revenue − cost. Which lever has the highest impact — conversion, retention, or cost reduction?",
        "model": "Identify the bottleneck metric. Optimize the constraint that binds first.",
        "math_link": "Optimization under budget constraints, A/B testing (statistics), and sensitivity analysis.",
        "lab": "Analyze an Idea",
    },
    {
        "category": "Traffic",
        "icon": "🚗",
        "title": "How would you reduce congestion?",
        "problem": "Commute times on Main Street peak at 45 minutes. How do we fix it?",
        "thinking": "Is the bottleneck capacity, demand timing, or routing? Measure before proposing solutions.",
        "model": "Flow = min(demand, capacity). Adjust signals, routing, or demand shift (pricing/timing).",
        "math_link": "Network flow, queueing theory, and simulation of traffic scenarios.",
        "lab": "Optimize a Decision",
    },
    {
        "category": "Weather",
        "icon": "🌤",
        "title": "How would you improve forecasts?",
        "problem": "Weather apps disagree on tomorrow's rain chance. Which should I trust?",
        "thinking": "Forecasts are probabilistic. Compare calibration over time, not one prediction. Uncertainty grows with lead time.",
        "model": "Ensemble multiple models, weight by past accuracy, widen confidence intervals for longer horizons.",
        "math_link": "Probability distributions, chaos dynamics, and statistical calibration of predictions.",
        "lab": "Advanced reference",
    },
]

SCORE_DIMENSIONS = [
    ("objective_clarity", "Objective clarity", 1),
    ("variables", "Variable identification", 2),
    ("constraints", "Constraints", 3),
    ("uncertainty", "Uncertainty awareness", 4),
    ("data", "Data availability", 5),
    ("model", "Model completeness", 6),
]
