"""Seven real-world areas for quantitative problem solving."""

QUANT_AREAS: list[dict] = [
    {
        "id": "betting",
        "name": "Betting & Gambling",
        "icon": "♠",
        "pattern_id": "betting",
        "suggested_lab": "Analyze a Bet",
        "tagline": "Expected value, odds, and how much to risk.",
        "example_questions": [
            "Is this bet worth making?",
            "What are the odds implied by +150?",
            "What is the expected value of this wager?",
            "How much should I risk on this decision?",
            "What is the probability I need to break even?",
            "Someone offered me $200 at 4-to-1 — is that fair?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "sports",
        "name": "Sports Prediction",
        "icon": "🏈",
        "pattern_id": "sports",
        "suggested_lab": "Predict a Game",
        "tagline": "Win probability, projections, and injury context.",
        "example_questions": [
            "Who is more likely to win this game?",
            "Is this player projection reasonable?",
            "How likely is a team to make the playoffs?",
            "Someone offered me $200 if Aaron Judge hits 30 home runs. Is this a good bet?",
            "How do injuries or past performance affect the prediction?",
            "Does my estimated win chance beat the market odds?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "medicine",
        "name": "Medicine & Healthcare",
        "icon": "🧬",
        "pattern_id": "medicine",
        "suggested_lab": "Model a Disease",
        "tagline": "Treatments, trials, growth models, and statistics.",
        "example_questions": [
            "How do you compare two treatments fairly?",
            "How could a cancer treatment be modeled?",
            "How does tumor growth change over time?",
            "How do clinical trials use statistics?",
            "Is a 60% tumor response rate enough to say the drug works?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "ai",
        "name": "AI & Machine Learning",
        "icon": "🤖",
        "pattern_id": "ai",
        "suggested_lab": "Train an AI",
        "tagline": "Learning, loss, optimization, and generalization.",
        "example_questions": [
            "How does a model learn from data?",
            "Why does a model make mistakes on new examples?",
            "How do loss functions and optimization work?",
            "How does training data affect predictions?",
            "Is high training accuracy enough?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "space",
        "name": "Space, Motion & Engineering",
        "icon": "🚀",
        "pattern_id": "space",
        "suggested_lab": "Advanced reference",
        "lab_hint": "In **Advanced reference**, open the **Space & Motion Lab** for orbit and trajectory tools.",
        "tagline": "Trajectories, fuel, motion, and constraints.",
        "example_questions": [
            "How do you predict a rocket trajectory?",
            "How do you optimize fuel or flight path?",
            "How do calculus and differential equations model motion?",
            "How do engineers use constraints in design?",
            "What velocity is needed to reach orbit?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "forecasting",
        "name": "Forecasting & Uncertainty",
        "icon": "🌦",
        "pattern_id": "weather",
        "suggested_lab": "Advanced reference",
        "lab_hint": "In **Advanced reference**, open the **Weather & Forecasting Lab**.",
        "tagline": "Predictions, confidence, and simulations.",
        "example_questions": [
            "How do you predict a future outcome with uncertainty?",
            "How do confidence levels work in forecasts?",
            "Why do forecasts get worse further ahead?",
            "How do simulations help explore possible futures?",
            "Is a 70% chance of rain the same as certainty?",
            "Custom question (type below)",
        ],
    },
    {
        "id": "abstract",
        "name": "Abstract Mathematical Problem Solving",
        "icon": "📐",
        "pattern_id": "abstract",
        "suggested_lab": "Solve a Problem",
        "tagline": "Find the structure before the procedure.",
        "example_questions": [
            "How do I turn a word problem into a math problem?",
            "What mathematical structure is hidden in this question?",
            "What am I optimizing, estimating, or comparing?",
            "What tool fits — probability, statistics, calculus, or optimization?",
            "Custom question (type below)",
        ],
    },
]

QUANT_AREA_BY_ID = {a["id"]: a for a in QUANT_AREAS}

ABSTRACT_PROBLEM_SOLVING = {
    "title": "Abstract Mathematical Problem Solving",
    "purpose": (
        "Learn to see the **structure** of a problem before reaching for a formula. "
        "Most applied questions are really one of a few types: estimate a probability, "
        "compare options, optimize under constraints, or model change over time."
    ),
    "steps": [
        ("Real structure", "What is being optimized, estimated, predicted, or compared?"),
        ("Variables", "What are inputs, outputs, decisions, and unknowns?"),
        ("Constraints", "What limits the answer — budget, physics, time, rules?"),
        ("Hidden assumptions", "What must be true for your approach to work?"),
        ("Tool choice", "Probability, statistics, calculus, optimization, or simulation?"),
        ("Simplify first", "What is the smallest model that still answers the question?"),
    ],
    "translations": [
        ("Betting question", "→ Expected value: compare your probability to the market price."),
        ("Sports prediction", "→ Probability forecasting: estimate P(outcome), report uncertainty."),
        ("Treatment comparison", "→ Statistical inference: treatment vs. control, not anecdotes."),
        ("Rocket motion", "→ Calculus / differential equations: position, velocity, acceleration."),
        ("AI model", "→ Optimization: minimize loss on new data, not memorization."),
        ("Weather forecast", "→ Probabilistic forecasting: distributions widen with lead time."),
    ],
}
