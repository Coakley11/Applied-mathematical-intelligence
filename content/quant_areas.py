"""Seven real-world areas for quantitative problem solving."""

from content.worked_examples import CUSTOM_SUFFIX, get_example_questions

QUANT_AREAS: list[dict] = [
    {
        "id": "betting",
        "name": "Betting & Gambling",
        "icon": "♠",
        "pattern_id": "betting",
        "suggested_lab": "Analyze a Bet",
        "tagline": "Expected value, odds, and how much to risk.",
    },
    {
        "id": "sports",
        "name": "Sports Prediction",
        "icon": "🏈",
        "pattern_id": "sports",
        "suggested_lab": "Predict a Game",
        "tagline": "Win probability, props, and market edge.",
    },
    {
        "id": "medicine",
        "name": "Medicine & Healthcare",
        "icon": "🧬",
        "pattern_id": "medicine",
        "suggested_lab": "Model a Disease",
        "tagline": "Treatments, trials, and growth models.",
    },
    {
        "id": "ai",
        "name": "AI & Machine Learning",
        "icon": "🤖",
        "pattern_id": "ai",
        "suggested_lab": "Train an AI",
        "tagline": "Learning, loss, and generalization.",
    },
    {
        "id": "space",
        "name": "Space, Motion & Engineering",
        "icon": "🚀",
        "pattern_id": "space",
        "suggested_lab": "Advanced reference",
        "lab_hint": "Open **Advanced reference** → **Space & Motion Lab** for trajectories and orbits.",
        "tagline": "Motion, orbits, fuel, and constraints.",
    },
    {
        "id": "forecasting",
        "name": "Forecasting & Uncertainty",
        "icon": "🌦",
        "pattern_id": "weather",
        "suggested_lab": "Advanced reference",
        "lab_hint": "Open **Advanced reference** → **Weather & Forecasting Lab**.",
        "tagline": "Probabilities, lead time, and simulations.",
    },
    {
        "id": "abstract",
        "name": "Abstract Mathematical Problem Solving",
        "icon": "📐",
        "pattern_id": "abstract",
        "suggested_lab": "Solve a Problem",
        "tagline": "Structure before formulas.",
    },
]

QUANT_AREA_BY_ID = {a["id"]: a for a in QUANT_AREAS}

# Attach example question lists from worked_examples
for _a in QUANT_AREAS:
    _a["example_questions"] = get_example_questions(_a["id"])

ABSTRACT_PROBLEM_SOLVING = {
    "title": "Abstract Mathematical Problem Solving",
    "purpose": (
        "See the **structure** before the procedure: what are you predicting, comparing, "
        "optimizing, or explaining? Then pick probability, statistics, calculus, optimization, or simulation."
    ),
    "steps": [
        ("Real structure", "What is optimized, estimated, predicted, or compared?"),
        ("Variables", "Decisions vs. measurements vs. unknowns."),
        ("Constraints", "Budget, physics, time, rules."),
        ("Assumptions", "What must hold for the model to apply?"),
        ("Tool choice", "Probability, statistics, calculus, optimization, simulation."),
        ("Simplify", "Smallest model that still answers the question."),
    ],
    "translations": [
        ("Betting", "→ Expected value vs. implied probability."),
        ("Sports", "→ Probability forecast + uncertainty."),
        ("Medicine", "→ Treatment vs. control inference."),
        ("Rocket motion", "→ ODEs / energy / optimization."),
        ("AI", "→ Loss minimization on new data."),
        ("Weather", "→ Probabilistic forecasts widening over time."),
    ],
}
