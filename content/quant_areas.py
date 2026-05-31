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
        "name": "Modeling Real Systems",
        "icon": "📐",
        "pattern_id": "abstract",
        "suggested_lab": "Solve a Problem",
        "tagline": "Variables, assumptions, constraints, uncertainty — before formulas.",
    },
]

QUANT_AREA_BY_ID = {a["id"]: a for a in QUANT_AREAS}

for _a in QUANT_AREAS:
    _a["example_questions"] = get_example_questions(_a["id"])

MODELING_REAL_SYSTEMS = {
    "title": "Modeling Real Systems",
    "purpose": (
        "Turn a real situation into **variables**, choose a **model**, state **assumptions** and "
        "**constraints**, quantify **uncertainty**, then use probability, optimization, calculus, or "
        "**simulation**. This thread connects betting, sports, medicine, AI, space, and forecasting."
    ),
    "steps": [
        ("Real structure", "What is predicted, compared, optimized, or explained?"),
        ("Variables", "Decisions you control vs. measurements vs. unknowns."),
        ("Choose a model", "Simplest relationship that answers the question."),
        ("Assumptions", "What must hold for the model to apply?"),
        ("Constraints", "Budget, physics, time, rules, safety."),
        ("Uncertainty", "Ranges, distributions, scenarios — not false precision."),
        ("Compute & test", "Calculate, simulate, compare to data; falsify one claim."),
    ],
    "translations": [
        ("Betting", "→ EV vs. implied probability; bankroll under variance."),
        ("Sports", "→ Forecast P(win) + injury adjustments vs. market."),
        ("Medicine", "→ Growth/treatment rates; trials vs. control."),
        ("AI", "→ Loss minimization + generalization gap."),
        ("Rocket / motion", "→ ODEs, trajectories, fuel optimization."),
        ("Weather", "→ Ensemble spread widening with lead time."),
        ("General", "→ Same skeleton: objective, inputs, constraints, noise."),
    ],
}

# Backward-compatible alias for imports
ABSTRACT_PROBLEM_SOLVING = MODELING_REAL_SYSTEMS
