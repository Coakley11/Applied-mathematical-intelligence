"""Mathematical Thinking — signature cross-domain intelligence page."""

MATHEMATICAL_THINKING = {
    "title": "Mathematical Thinking",
    "tagline": (
        "How quantitative intelligence works across every domain in this platform — "
        "a systems view of modeling reality, not a lesson in symbols."
    ),
    "introduction": """
    Professional applied mathematics is not a collection of formulas. It is a **repeatable way of thinking**
    about complex systems: represent the structure, quantify uncertainty, simulate futures, optimize decisions,
    and update beliefs when data arrives. The same cognitive stack appears in finance, epidemiology, AI,
    astronomy, and logistics — only the symbols and data change.
    """,
    "pillars": [
        {
            "name": "Modeling reality",
            "summary": "Translate a messy situation into variables, relationships, and constraints that capture what actually drives outcomes.",
            "insight": "A model is a deliberate lie that reveals truth — it ignores noise to expose mechanism.",
            "domains": "SIR models in epidemiology, balance sheets in finance, equations of motion in aerospace.",
        },
        {
            "name": "Approximation",
            "summary": "Exact solutions are rare. Professionals use linearization, numerical methods, and asymptotics to get usable answers.",
            "insight": "The question is not exactitude but **controlled error** relative to the decision at stake.",
            "domains": "Finite elements in engineering, Euler steps in climate boxes, gradient steps in AI training.",
        },
        {
            "name": "Abstraction",
            "summary": "Strip domain detail to see isomorphism — gambling EV, option pricing, and A/B tests share expectation structures.",
            "insight": "Abstraction lets you transfer methods across fields faster than reinventing intuition.",
            "domains": "Graph algorithms in social networks and logistics; matrix factorization in recommendations and genetics.",
        },
        {
            "name": "Prediction",
            "summary": "Forecast distributions, not certainties. Point estimates without uncertainty mislead institutions.",
            "insight": "A 70% chance is a statement about **many worlds**, not weakness of knowledge.",
            "domains": "Election models, hurricane cones, demand forecasting, model validation loss.",
        },
        {
            "name": "Optimization",
            "summary": "Choose the best feasible action under an objective — minimize cost, maximize utility, minimize loss.",
            "insight": "Every 'best' implies a tradeoff surface; constraints define what is achievable.",
            "domains": "Portfolio weights, rocket fuel, ad bidding, neural network training.",
        },
        {
            "name": "Uncertainty",
            "summary": "Randomness and incomplete information are first-class. Probability quantifies what could happen.",
            "insight": "Base rates matter. Tail events dominate solvency. Bayes updates beliefs sequentially.",
            "domains": "Insurance, medical testing, poker, credit risk, calibrated AI outputs.",
        },
        {
            "name": "Simulation",
            "summary": "When systems are too complex for closed forms, sample many futures and study the distribution.",
            "insight": "Simulation makes assumptions explicit and stress-tests policies before reality does.",
            "domains": "Monte Carlo finance, wargaming, climate ensembles, playoff odds.",
        },
        {
            "name": "Continuous change",
            "summary": "Calculus tracks rates and accumulation — small flows integrate into large structural shifts.",
            "insight": "Compare competing rates (growth vs treatment, forcing vs feedback) before comparing levels.",
            "domains": "Pharmacokinetics, tumor dynamics, climate energy balance, gradient flow in ML.",
        },
        {
            "name": "Signal vs noise",
            "summary": "Statistics separates structure from randomness — shrinkage, regularization, and sample size discipline.",
            "insight": "Extremes regress; models must generalize out-of-sample, not memorize history.",
            "domains": "Sports projections, clinical trials, econometrics, training vs validation error.",
        },
        {
            "name": "AI as mathematical pattern optimization",
            "summary": "Modern AI is large-scale pattern extraction via differentiable optimization and probabilistic prediction.",
            "insight": "Neural networks do not replace mathematics — they **automate** representation learning inside the same stack.",
            "domains": "Language models, vision, ranking, scientific ML emulators.",
        },
    ],
    "synthesis": """
    Mathematical intelligence is **layered**. You model the system (structure), approximate dynamics (calculus/simulation),
    detect patterns (statistics), quantify doubt (probability), choose actions (optimization), and — increasingly —
    learn representations (AI). Weakness in any layer propagates: a perfect optimizer on a wrong model still fails.

    This platform is organized so you can move vertically (deepen one mathematical system) and horizontally
    (see the same stack in finance, health, or space). That is how quantitative professionals actually think.
    """,
    "professional_questions": [
        "What is the state variable, and what rate changes it?",
        "What decision would change if the tail risk doubled?",
        "Where could this model be wrong structurally, not just parametrically?",
        "What would falsify this prediction in new data?",
        "What optimization objective does the organization actually reward?",
    ],
}
