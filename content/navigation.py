"""Primary navigation — problem-first actions and section routing."""

from content.practical_labs import (
    ACTION_DESCRIPTIONS,
    ACTION_LABELS,
    PRACTICAL_LABS,
    SECONDARY_LAB_NAMES,
)

# Seven large action cards on Home and primary sidebar entries (after Home)
PRIMARY_ACTIONS = [
    "Analyze a Bet",
    "Predict a Game",
    "Model a Disease",
    "Train an AI",
    "Optimize a Decision",
    "Analyze an Idea",
    "Explore Mathematical Thinking",
]

PRIMARY_ACTION_DESCRIPTIONS = {
    "Analyze a Bet": ACTION_DESCRIPTIONS["Betting & Poker Lab"],
    "Predict a Game": ACTION_DESCRIPTIONS["Sports Prediction Lab"],
    "Model a Disease": ACTION_DESCRIPTIONS["Medicine & Disease Lab"],
    "Train an AI": ACTION_DESCRIPTIONS["AI Learning Lab"],
    "Optimize a Decision": (
        "Define your objective, variables, and constraints — then build a mathematical framework "
        "to improve poker strategy, traffic, treatment outcomes, or any decision."
    ),
    "Analyze an Idea": (
        "Enter a business idea, invention, or strategy. Discover what variables matter, "
        "what to model, and which mathematical tools could help."
    ),
    "Explore Mathematical Thinking": (
        "Learn how mathematical thinkers approach problems — modeling, uncertainty, "
        "simplification, and turning real-world questions into math."
    ),
}

PRIMARY_ACTION_ICONS = {
    "Analyze a Bet": PRACTICAL_LABS["Betting & Poker Lab"]["icon"],
    "Predict a Game": PRACTICAL_LABS["Sports Prediction Lab"]["icon"],
    "Model a Disease": PRACTICAL_LABS["Medicine & Disease Lab"]["icon"],
    "Train an AI": PRACTICAL_LABS["AI Learning Lab"]["icon"],
    "Optimize a Decision": "⚙",
    "Analyze an Idea": "💡",
    "Explore Mathematical Thinking": "🧭",
}

PRIMARY_ACTION_LABELS = {
    "Analyze a Bet": "Betting & Poker Lab",
    "Predict a Game": "Sports Prediction Lab",
    "Model a Disease": "Medicine & Disease Lab",
    "Train an AI": "AI Learning Lab",
    "Optimize a Decision": "Optimization Workshop",
    "Analyze an Idea": "Idea & Invention Analysis",
    "Explore Mathematical Thinking": "Mathematical Thinking Lab",
}

# Maps sidebar action label → section type for streamlit_app dispatch
ACTION_SECTION_TYPES = {
    "Analyze a Bet": "lab",
    "Predict a Game": "lab",
    "Model a Disease": "lab",
    "Train an AI": "lab",
    "Optimize a Decision": "optimization",
    "Analyze an Idea": "idea",
    "Explore Mathematical Thinking": "thinking",
}

ACTION_TO_LAB = {
    ACTION_LABELS[name]: name
    for name in PRACTICAL_LABS
    if name not in SECONDARY_LAB_NAMES
}

NAV_HELP = {
    "Home": "Pick a real-world problem and start experimenting.",
    "Analyze a Bet": "Expected value, pot odds, and casino edge — is the decision worth it?",
    "Predict a Game": "Sports probabilities, odds, ratings, and trend forecasting.",
    "Model a Disease": "Disease spread, tumor growth, and drug concentration.",
    "Train an AI": "Gradient descent and neural network training.",
    "Optimize a Decision": "Define objectives, constraints, and build an optimization framework.",
    "Analyze an Idea": "Mathematical brainstorming for inventions, strategies, and systems.",
    "Explore Mathematical Thinking": "How quantitative thinkers approach any problem.",
    "Advanced reference": "Optional — extra labs, 32 domain case studies, and portfolio specs.",
}
