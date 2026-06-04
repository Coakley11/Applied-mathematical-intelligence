"""Interactive thinking workshop — walk users through mathematician-style reasoning."""

from __future__ import annotations

import re
from typing import Any

WORKSHOP_INTRO = (
    "Enter a question, bet, scenario, or idea — then pick a thinking lens. "
    "You will see structure, visuals, and sliders — not a lecture."
)

WORKSHOP_EXAMPLE_PROMPTS = [
    "I want to know if this sports bet is worth making.",
    "Is an Aaron Judge 30+ home run prop worth $200?",
    "What are the Mets' chances to make the playoffs?",
    "Treatment A vs Treatment B — which slows the tumor more?",
    "Why is training accuracy 92% but validation only 78%?",
    "How confident should we be in a 7-day weather forecast?",
    "Custom (type below)",
]

# Six primary interactive lenses (hands-on workshop)
WORKSHOP_MODES = [
    {
        "id": "abstraction",
        "name": "Abstraction",
        "icon": "🔭",
        "tagline": "What is the deeper structure underneath the story?",
    },
    {
        "id": "modeling",
        "name": "Modeling",
        "icon": "📐",
        "tagline": "Translate words into variables, rules, and outputs.",
    },
    {
        "id": "assumptions",
        "name": "Assumptions",
        "icon": "📋",
        "tagline": "Make hidden beliefs explicit — then stress-test them.",
    },
    {
        "id": "simplification",
        "name": "Simplification",
        "icon": "✂️",
        "tagline": "Find the smallest useful version of the problem.",
    },
    {
        "id": "uncertainty",
        "name": "Uncertainty",
        "icon": "🌫️",
        "tagline": "Name what you do not know and how sensitive the answer is.",
    },
    {
        "id": "optimization",
        "name": "Optimization",
        "icon": "⚖️",
        "tagline": "What are you maximizing, under what limits, at what cost?",
    },
]

_DOMAIN_PATTERNS: list[tuple[str, str]] = [
    (r"poker|gambl|wager|casino|pot odds|bet|odds|\+150|ev\b", "betting"),
    (r"sport|baseball|game|team|forecast|predict", "sports"),
    (r"cancer|tumor|treatment|drug|disease|medic|health|clinical", "medicine"),
    (r"ai|machine learning|neural|train|overfit|model learn", "ai"),
    (r"weather|forecast|rain|storm|climate|trend", "forecasting"),
    (r"optim|budget|allocat|tradeoff|maximize|minimize|constraint", "optimization"),
    (r"rocket|orbit|trajectory|space|launch", "space"),
]


def infer_problem_domain(problem: str) -> str:
    lower = problem.lower()
    for pattern, domain in _DOMAIN_PATTERNS:
        if re.search(pattern, lower):
            return domain
    return "general"


def _clip(problem: str, max_len: int = 80) -> str:
    p = problem.strip()
    if len(p) <= max_len:
        return p
    return p[: max_len - 1] + "…"


def get_mode_walkthrough(problem: str, mode_id: str) -> dict[str, Any]:
    """Build a problem-specific walkthrough for one thinking mode."""
    domain = infer_problem_domain(problem)
    short = _clip(problem) if problem.strip() else "your question"
    templates = _DOMAIN_CONTENT.get(domain, _DOMAIN_CONTENT["general"])
    base = templates.get(mode_id, templates["abstraction"])
    return {
        "domain": domain,
        "problem_short": short,
        "deeper_structure": base["deeper_structure"],
        "matters": base["matters"],
        "ignore": base["ignore"],
        "variables": base.get("variables", []),
        "unknowns": base.get("unknowns", []),
        "outputs": base.get("outputs", []),
        "assumptions": base.get("assumptions", []),
        "if_wrong": base.get("if_wrong", []),
        "simplest_model": base.get("simplest_model", ""),
        "can_ignore": base.get("can_ignore", []),
        "unknown_list": base.get("unknown_list", []),
        "confidence_prompt": base.get("confidence_prompt", ""),
        "sensitivity_note": base.get("sensitivity_note", ""),
        "objective": base.get("objective", ""),
        "constraints": base.get("constraints", []),
        "tradeoffs": base.get("tradeoffs", []),
        "applications": base.get("applications", []),
        "try_prompt": base.get("try_prompt", ""),
        "what_if": base.get("what_if", []),
        "suggested_lab": base.get("suggested_lab", ""),
    }


_DOMAIN_CONTENT: dict[str, dict[str, dict[str, Any]]] = {
    "betting": {
        "abstraction": {
            "deeper_structure": (
                "This is not really about sports or cards. It is **uncertainty + probability "
                "estimation + risk vs reward + decision making**."
            ),
            "matters": ["True win probability", "Payout / pot odds", "Stake size", "Long-run EV"],
            "ignore": ["Team colors", "Narrative streaks", "One-hand outcome"],
            "applications": ["Poker pot odds", "Sports +EV", "Insurance pricing", "A/B tests"],
            "try_prompt": "Estimate win % and compare to implied odds from the line.",
            "what_if": [
                ("Win probability is 5% lower than you think", "EV can flip from positive to negative."),
                ("You double stake size", "Same edge, but variance and ruin risk jump."),
                ("Opponent adapts", "Static win-rate assumption breaks."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
        "modeling": {
            "deeper_structure": "Model: **EV = P(win) × profit − P(lose) × stake**",
            "variables": ["Payout (decimal odds)", "Stake", "Your win probability", "Bankroll"],
            "unknowns": ["True probability", "Opponent behavior", "Future variance"],
            "outputs": ["Expected value ($)", "Edge vs market", "Risk of ruin (optional)"],
            "matters": ["Inputs you control vs estimate"],
            "ignore": ["Past lucky streak as 'skill'"],
            "applications": ["Pot odds calculator", "Kelly criterion", "Monte Carlo season"],
            "try_prompt": "Write EV with your numbers before placing the bet.",
            "what_if": [
                ("Use market implied prob instead of yours", "See if the bet is +EV for the market."),
                ("Add rake / vig", "Breakeven edge rises."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
        "assumptions": {
            "deeper_structure": "Every bet model assumes something about **probability, independence, and bankroll**.",
            "assumptions": [
                "Your win-probability estimate is stable across similar spots",
                "Outcomes are independent (no correlated parlays unless modeled)",
                "You can survive variance (bankroll assumption)",
                "Odds won't move before you act",
            ],
            "if_wrong": [
                "Overestimated edge → long-run loss despite 'feeling' smart",
                "Underestimated variance → ruin before edge appears",
                "Correlated bets → risk stacks silently",
            ],
            "matters": ["Document assumptions before clicking bet"],
            "ignore": ["Hot hand stories"],
            "applications": ["Line shopping", "Record keeping", "Confidence intervals on win rate"],
            "try_prompt": "List your top 3 assumptions — which one would hurt most if false?",
            "what_if": [
                ("Injury news drops before game", "Your probability assumption may be stale."),
                ("Small sample of past bets", "Win rate estimate has wide error bars."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
        "simplification": {
            "deeper_structure": "Simplest useful model: **one number — expected value per dollar wagered**.",
            "simplest_model": "EV per $1 = p × (odds − 1) − (1 − p). Ignore opponent names, media, streaks.",
            "can_ignore": ["Play-by-play", "Brand of sportsbook", "Emotional attachment to team"],
            "matters": ["p and payout only for a single bet decision"],
            "ignore": ["Multi-leg correlation unless you model it"],
            "applications": ["Binary bet decision", "Pot odds call/fold"],
            "try_prompt": "Can you decide with just p and decimal odds?",
            "what_if": [
                ("Add bankroll management", "Simple EV → Kelly fraction or flat stake rule."),
                ("Add multiple outcomes", "Need full distribution, not one p."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
        "uncertainty": {
            "deeper_structure": "You do not know **true p** — only a range. The decision should survive that range.",
            "unknown_list": ["True win probability", "Variance over next N bets", "Model error in estimate"],
            "confidence_prompt": "Give a range (e.g. 40–50%), not a fake precise 47.3%.",
            "sensitivity_note": "If EV is positive only at the top of your range, the bet is fragile.",
            "matters": ["Interval for p", "Sample size behind estimate"],
            "ignore": ["Exact cents of EV without sensitivity"],
            "applications": ["Monte Carlo bankroll paths", "Confidence bands on win rate"],
            "try_prompt": "Slide p across your range — when does EV cross zero?",
            "what_if": [
                ("Widen p by ±5%", "Does the bet stay +EV?"),
                ("Run 100-bet simulation", "See profit distribution, not one outcome."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
        "optimization": {
            "deeper_structure": "Usually maximize **long-run growth or EV** subject to **bankroll and risk tolerance**.",
            "objective": "Maximize expected log-wealth or EV over many similar decisions",
            "constraints": ["Bankroll cap", "Table limits", "Risk of ruin tolerance", "Time to play"],
            "tradeoffs": ["Bigger edge bets vs diversification", "Aggression vs survival", "Volume vs edge quality"],
            "matters": ["Objective must be named — profit today vs bankroll in 6 months"],
            "ignore": ["Max single-hand win without context"],
            "applications": ["Kelly betting", "Portfolio of +EV spots", "Stop-loss rules"],
            "try_prompt": "State: I maximize ___ subject to ___",
            "what_if": [
                ("Tighten ruin constraint", "Optimal stake size drops."),
                ("Add correlated bets", "Effective risk budget shrinks."),
            ],
            "suggested_lab": "Analyze a Bet",
        },
    },
    "sports": {
        "abstraction": {
            "deeper_structure": "Forecasting + **noisy measurement of strength** + comparing model to market.",
            "matters": ["True talent", "Sample size", "Home field", "Injuries"],
            "ignore": ["Narrative momentum", "Recency bias without data"],
            "applications": ["Elo ratings", "Market odds comparison", "Regression to mean"],
            "try_prompt": "Separate luck in last 5 games from estimated strength.",
            "what_if": [("Early season hot streak", "Ratings overreact — regress toward average.")],
            "suggested_lab": "Predict a Game",
        },
        "modeling": {
            "deeper_structure": "Model: **P(win) = f(team ratings, home, injuries)** compared to implied market prob.",
            "variables": ["Team strength metrics", "Home advantage", "Market line"],
            "unknowns": ["True talent gap", "Lineup changes"],
            "outputs": ["Win probability", "Edge vs closing line"],
            "matters": ["Inputs with data", "Clear output for decision"],
            "ignore": [],
            "applications": ["Logistic win model", "Point spread models"],
            "try_prompt": "List 3 inputs and one output probability.",
            "what_if": [("Double sample size", "Uncertainty on rating shrinks.")],
            "suggested_lab": "Predict a Game",
        },
        "assumptions": {
            "deeper_structure": "Assumes **stable talent**, **injury info is current**, **past predicts future**.",
            "assumptions": ["Ratings capture skill", "No major unmodeled lineup shock", "Market is not perfectly efficient"],
            "if_wrong": ["Injury news stale → wrong P(win)", "Playoff intensity differs → regular-season model fails"],
            "matters": [],
            "ignore": [],
            "applications": ["Holdout season validation"],
            "try_prompt": "Which assumption fails in playoffs vs regular season?",
            "what_if": [],
            "suggested_lab": "Predict a Game",
        },
        "simplification": {
            "deeper_structure": "Start with **single win probability** from one strength difference.",
            "simplest_model": "P(home win) from rating difference only.",
            "can_ignore": ["Player-level detail until base model works"],
            "matters": [],
            "ignore": [],
            "applications": ["Elo difference → win %"],
            "try_prompt": "Can one rating gap explain 80% of your decision?",
            "what_if": [],
            "suggested_lab": "Predict a Game",
        },
        "uncertainty": {
            "deeper_structure": "Small samples create **wide intervals** on true strength.",
            "unknown_list": ["True talent gap", "Injury impact size", "Late-season motivation"],
            "confidence_prompt": "Report P(win) as a band, e.g. 52–58%.",
            "sensitivity_note": "Edge vs market may disappear inside the band.",
            "matters": [],
            "ignore": [],
            "applications": ["Bootstrap seasons", "Prediction intervals"],
            "try_prompt": "Move win % ±3% — does bet still have edge?",
            "what_if": [],
            "suggested_lab": "Predict a Game",
        },
        "optimization": {
            "deeper_structure": "Maximize **long-run betting EV** or **prediction accuracy** under bankroll rules.",
            "objective": "Maximize CLV (closing line value) or calibrated accuracy",
            "constraints": ["Bankroll", "Max bets per day", "Correlation across parlays"],
            "tradeoffs": ["Model complexity vs overfit", "Bet volume vs edge size"],
            "matters": [],
            "ignore": [],
            "applications": ["Bet sizing", "Model selection"],
            "try_prompt": "What are you optimizing — accuracy or dollars?",
            "what_if": [],
            "suggested_lab": "Predict a Game",
        },
    },
    "medicine": {
        "abstraction": {
            "deeper_structure": "Competing **growth vs treatment rates** under toxicity and individual variation.",
            "matters": ["Tumor growth rate", "Treatment kill rate", "Toxicity ceiling"],
            "ignore": ["Anecdotal recovery stories without data"],
            "applications": ["PK/PD models", "SIR epidemics", "Dose-response curves"],
            "try_prompt": "Draw growth and kill on the same timeline.",
            "what_if": [("Higher dose", "More kill, more toxicity — tradeoff sharpens.")],
            "suggested_lab": "Model a Disease",
        },
        "modeling": {
            "deeper_structure": "dV/dt = **growth − treatment effect** (possibly with drug concentration).",
            "variables": ["Tumor volume", "Dose", "Drug concentration", "Growth rate"],
            "unknowns": ["Patient-specific response", "Resistance emergence"],
            "outputs": ["Volume over time", "Time to progression", "Toxicity score"],
            "matters": [],
            "ignore": [],
            "applications": ["Tumor simulator", "SIR lab"],
            "try_prompt": "Write the balance equation in words first.",
            "what_if": [],
            "suggested_lab": "Model a Disease",
        },
        "assumptions": {
            "deeper_structure": "Assumes **homogeneous response**, **constant parameters**, **measurable tumor burden**.",
            "assumptions": ["Exponential growth region", "Known dosing adherence", "Trial population represents patient"],
            "if_wrong": ["Heterogeneity → average outcome misleads", "Resistance → model drifts"],
            "matters": [],
            "ignore": [],
            "applications": ["Subgroup analysis", "Adaptive dosing"],
            "try_prompt": "Which patient subgroups break the average model?",
            "what_if": [],
            "suggested_lab": "Model a Disease",
        },
        "simplification": {
            "deeper_structure": "Compare **two rates**: does treatment shrink faster than growth?",
            "simplest_model": "If kill rate > growth rate → shrink; else grow.",
            "can_ignore": ["Spatial tumor geometry at first pass"],
            "matters": [],
            "ignore": [],
            "applications": ["Threshold dose rule"],
            "try_prompt": "One chart: volume vs time with/without treatment.",
            "what_if": [],
            "suggested_lab": "Model a Disease",
        },
        "uncertainty": {
            "deeper_structure": "Trial data gives **intervals**, not certainty — individual response varies.",
            "unknown_list": ["True response for this patient", "Long-term toxicity", "Resistance timing"],
            "confidence_prompt": "Use confidence intervals from trials, not point estimates alone.",
            "sensitivity_note": "Decision should account for worst plausible response.",
            "matters": [],
            "ignore": [],
            "applications": ["Uncertainty bands on survival curves"],
            "try_prompt": "Overlay plausible response bands on one curve.",
            "what_if": [],
            "suggested_lab": "Model a Disease",
        },
        "optimization": {
            "deeper_structure": "Maximize **benefit** (survival, shrinkage) subject to **toxicity and feasibility**.",
            "objective": "Maximize quality-adjusted survival or tumor control",
            "constraints": ["Max dose", "Organ toxicity limits", "Cost / access"],
            "tradeoffs": ["Aggressive dose vs side effects", "Speed vs durability"],
            "matters": [],
            "ignore": [],
            "applications": ["Dose-finding optimization"],
            "try_prompt": "Name objective and hardest constraint explicitly.",
            "what_if": [],
            "suggested_lab": "Model a Disease",
        },
    },
    "ai": {
        "abstraction": {
            "deeper_structure": "Pattern extraction from data with **generalization risk** (overfitting).",
            "matters": ["Train vs validation gap", "Loss curve shape", "Data size vs model size"],
            "ignore": ["Training accuracy alone"],
            "applications": ["Bias-variance tradeoff", "Regularization", "Early stopping"],
            "try_prompt": "Ask: would this model work on new data?",
            "what_if": [("More parameters", "Lower train loss, worse validation possible.")],
            "suggested_lab": "Train an AI",
        },
        "modeling": {
            "deeper_structure": "Minimize **loss** on parameters θ using data (X, y).",
            "variables": ["Weights θ", "Learning rate", "Training set", "Validation set"],
            "unknowns": ["Generalization error on deployment data"],
            "outputs": ["Train loss", "Validation loss", "Predictions"],
            "matters": [],
            "ignore": [],
            "applications": ["Gradient descent lab", "Train/val split visual"],
            "try_prompt": "Sketch inputs → model → loss → update rule.",
            "what_if": [],
            "suggested_lab": "Train an AI",
        },
        "assumptions": {
            "deeper_structure": "Assumes **IID samples**, **stationary distribution**, **labels are correct**.",
            "assumptions": ["Train and test from same distribution", "Enough data for model capacity", "Features carry signal"],
            "if_wrong": ["Distribution shift → deployment failure", "Label noise → memorization"],
            "matters": [],
            "ignore": [],
            "applications": ["Domain adaptation", "Data cleaning"],
            "try_prompt": "What changes in production that training never saw?",
            "what_if": [],
            "suggested_lab": "Train an AI",
        },
        "simplification": {
            "deeper_structure": "Start with **linear model + one metric** (validation loss).",
            "simplest_model": "y ≈ w·x + b; track error on held-out set.",
            "can_ignore": ["Architecture search until baseline works"],
            "matters": [],
            "ignore": [],
            "applications": ["Baseline before deep net"],
            "try_prompt": "Can a simpler model get 90% of the value?",
            "what_if": [],
            "suggested_lab": "Train an AI",
        },
        "uncertainty": {
            "deeper_structure": "Small data → **high variance** in learned weights and metrics.",
            "unknown_list": ["True generalization error", "Label noise rate", "Distribution shift magnitude"],
            "confidence_prompt": "Report metric ranges across folds or seeds.",
            "sensitivity_note": "If validation loss swings with seed, conclusion is fragile.",
            "matters": [],
            "ignore": [],
            "applications": ["Learning curves", "Error bars on metrics"],
            "try_prompt": "Change seed — does validation rank models the same way?",
            "what_if": [],
            "suggested_lab": "Train an AI",
        },
        "optimization": {
            "deeper_structure": "Minimize **loss** subject to **compute, latency, interpretability**.",
            "objective": "Minimize validation loss (or maximize F1, etc.)",
            "constraints": ["Training time", "Model size", "Fairness rules"],
            "tradeoffs": ["Accuracy vs speed", "Complexity vs overfit", "Precision vs recall"],
            "matters": [],
            "ignore": [],
            "applications": ["Hyperparameter search", "Early stopping"],
            "try_prompt": "What is the actual objective metric for deployment?",
            "what_if": [],
            "suggested_lab": "Train an AI",
        },
    },
    "forecasting": {
        "abstraction": {
            "deeper_structure": "Extrapolate **signal + noise** with widening uncertainty over time.",
            "matters": ["Trend", "Noise level", "Forecast horizon"],
            "ignore": ["Single-point precision far ahead"],
            "applications": ["Sales forecasting", "Weather ensembles", "Epidemic projections"],
            "try_prompt": "Separate signal (slope) from noise (scatter).",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
        "modeling": {
            "deeper_structure": "y(t) ≈ **a + b·t** with error bars growing with horizon.",
            "variables": ["Historical points", "Slope", "Noise σ", "Lead time"],
            "unknowns": ["Future shocks", "Structural breaks"],
            "outputs": ["Point forecast", "Prediction interval"],
            "matters": [],
            "ignore": [],
            "applications": ["Trend + cone of uncertainty"],
            "try_prompt": "Fit line — then draw cone, not just a point.",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
        "assumptions": {
            "deeper_structure": "Assumes **stable trend**, **similar noise**, **no regime change**.",
            "assumptions": ["Linear local trend", "Past variance predicts future", "No sudden policy shift"],
            "if_wrong": ["Break point → forecast systematically wrong"],
            "matters": [],
            "ignore": [],
            "applications": ["Change-point detection"],
            "try_prompt": "What event would invalidate the trend?",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
        "simplification": {
            "deeper_structure": "One **linear trend** plus **± band** from residual noise.",
            "simplest_model": "Last N points → slope; ±2σ cone forward.",
            "can_ignore": ["Seasonality until trend works"],
            "matters": [],
            "ignore": [],
            "applications": ["Quick back-of-envelope forecast"],
            "try_prompt": "Can you forecast with slope + noise only?",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
        "uncertainty": {
            "deeper_structure": "Uncertainty **grows with horizon** — chaos and model disagreement matter.",
            "unknown_list": ["Future slope", "Shock events", "Model spread"],
            "confidence_prompt": "Show intervals, not false point precision.",
            "sensitivity_note": "Decision should use worst-case band, not mean only.",
            "matters": [],
            "ignore": [],
            "applications": ["Ensemble fan charts", "Simulation paths"],
            "try_prompt": "Widen noise slider — watch interval explode.",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
        "optimization": {
            "deeper_structure": "Minimize **forecast error** or **decision cost** subject to **lead time and data cost**.",
            "objective": "Minimize MAE or maximize decision value from forecast",
            "constraints": ["Data collection budget", "Max lead time", "Communication clarity"],
            "tradeoffs": ["Longer horizon vs accuracy", "Simple vs ensemble models"],
            "matters": [],
            "ignore": [],
            "applications": ["Model weighting", "Cost of wrong inventory bet"],
            "try_prompt": "Who uses the forecast — what error hurts them?",
            "what_if": [],
            "suggested_lab": "Advanced reference",
        },
    },
    "optimization": {
        "abstraction": {
            "deeper_structure": "Choose **best feasible option** when you cannot maximize everything at once.",
            "matters": ["Objective", "Feasible region", "Tradeoff curve"],
            "ignore": ["Ranking options on one dimension only"],
            "applications": ["Portfolio allocation", "Route planning", "Resource budgets"],
            "try_prompt": "Name what 'best' means numerically.",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
        "modeling": {
            "deeper_structure": "max **f(x)** subject to **g(x) ≤ limits**.",
            "variables": ["Decision vector x", "Returns", "Risks"],
            "unknowns": ["True returns", "Future constraints"],
            "outputs": ["Optimal allocation", "Objective value"],
            "matters": [],
            "ignore": [],
            "applications": ["Budget split lab"],
            "try_prompt": "Write objective + one inequality constraint.",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
        "assumptions": {
            "deeper_structure": "Assumes **known returns**, **static constraints**, **linear tradeoffs** (often wrong).",
            "assumptions": ["Return estimates stable", "Risk scores comparable", "Budget fixed"],
            "if_wrong": ["Return miss → wrong allocation", "Risk underestimated → violation"],
            "matters": [],
            "ignore": [],
            "applications": ["Sensitivity on return inputs"],
            "try_prompt": "Which input moves the solution most?",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
        "simplification": {
            "deeper_structure": "Two options, one constraint — **compare ratios** before full solver.",
            "simplest_model": "Return per unit risk for each option; pick under cap.",
            "can_ignore": ["Thousands of variables at first"],
            "matters": [],
            "ignore": [],
            "applications": ["Greedy allocation heuristic"],
            "try_prompt": "Can you solve with 2 projects and 1 budget?",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
        "uncertainty": {
            "deeper_structure": "Returns are **estimates** — robust optimization uses ranges.",
            "unknown_list": ["True project returns", "Correlation between projects"],
            "confidence_prompt": "Run best/worst case on return assumptions.",
            "sensitivity_note": "Optimal mix may flip when returns move ±10%.",
            "matters": [],
            "ignore": [],
            "applications": ["Scenario analysis"],
            "try_prompt": "Perturb one return — does winner change?",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
        "optimization": {
            "deeper_structure": "This mode *is* the problem — state **objective**, **constraints**, **tradeoffs** clearly.",
            "objective": "Maximize return or minimize cost/risk",
            "constraints": ["Budget", "Risk cap", "Time", "Regulatory limits"],
            "tradeoffs": ["Return vs risk", "Speed vs quality", "Cost vs coverage"],
            "matters": [],
            "ignore": [],
            "applications": ["Pareto frontier", "Lagrange intuition"],
            "try_prompt": "Draw feasible region — what is the binding constraint?",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
    },
    "general": {
        "abstraction": {
            "deeper_structure": "Strip the story to **structure**: inputs → rules → outputs under uncertainty.",
            "matters": ["Core mechanism", "Decisions vs measurements"],
            "ignore": ["Decorative detail", "Jargon that hides the math"],
            "applications": ["EV decisions", "Dynamical systems", "Forecasting", "ML"],
            "try_prompt": "Describe the problem without domain words.",
            "what_if": [("Rephrase as betting problem", "Often reveals EV structure.")],
            "suggested_lab": "Solve a Problem",
        },
        "modeling": {
            "deeper_structure": "Write **variables**, **relationship**, **output**.",
            "variables": ["Inputs you control", "Inputs you observe", "Parameters to estimate"],
            "unknowns": ["Quantities you must guess or learn from data"],
            "outputs": ["The quantity that answers your question"],
            "matters": [],
            "ignore": [],
            "applications": ["Word problems → equations"],
            "try_prompt": "Fill: output = f(inputs, parameters).",
            "what_if": [],
            "suggested_lab": "Solve a Problem",
        },
        "assumptions": {
            "deeper_structure": "List beliefs that, if false, **break the conclusion**.",
            "assumptions": ["Independence", "Stability over time", "Representative data", "Correct objective"],
            "if_wrong": ["Model right for wrong world → confident wrong answer"],
            "matters": [],
            "ignore": [],
            "applications": ["Sensitivity analysis", "Scenario planning"],
            "try_prompt": "Pick the weakest assumption — test it first.",
            "what_if": [],
            "suggested_lab": "Solve a Problem",
        },
        "simplification": {
            "deeper_structure": "Smallest model that could still **change your decision**.",
            "simplest_model": "One equation or one comparison between two options.",
            "can_ignore": ["Secondary variables until baseline works"],
            "matters": [],
            "ignore": [],
            "applications": ["Back-of-envelope", "Fermi estimates"],
            "try_prompt": "Remove one variable — does the decision change?",
            "what_if": [],
            "suggested_lab": "Solve a Problem",
        },
        "uncertainty": {
            "deeper_structure": "Replace point guesses with **ranges** and ask if the decision survives.",
            "unknown_list": ["Parameter values", "Future events", "Model structure"],
            "confidence_prompt": "How wide is your plausible range?",
            "sensitivity_note": "If only the optimistic end supports your choice, be cautious.",
            "matters": [],
            "ignore": [],
            "applications": ["Monte Carlo", "Confidence intervals"],
            "try_prompt": "Vary the main parameter ±20% — stable conclusion?",
            "what_if": [],
            "suggested_lab": "Solve a Problem",
        },
        "optimization": {
            "deeper_structure": "Every 'best' needs **objective + constraints + tradeoffs**.",
            "objective": "What you maximize or minimize (be specific)",
            "constraints": ["Budget", "Time", "Rules", "Risk tolerance"],
            "tradeoffs": ["What you give up when you push one goal harder"],
            "matters": [],
            "ignore": [],
            "applications": ["Linear programming intuition", "Multi-objective choice"],
            "try_prompt": "Complete: maximize ___ subject to ___",
            "what_if": [],
            "suggested_lab": "Optimize a Decision",
        },
    },
}

# Fill sports/space/general gaps by copying general for missing keys per domain
for domain_id in ("sports", "medicine", "ai", "forecasting", "optimization", "betting"):
    dom = _DOMAIN_CONTENT[domain_id]
    gen = _DOMAIN_CONTENT["general"]
    for mode in WORKSHOP_MODES:
        mid = mode["id"]
        if mid not in dom:
            dom[mid] = dict(gen[mid])

_DOMAIN_CONTENT["space"] = dict(_DOMAIN_CONTENT["general"])
_DOMAIN_CONTENT["space"]["modeling"]["variables"] = [
    "Position", "Velocity", "Thrust", "Fuel mass", "Time"
]

# Public alias used by QA/smoke tests
DOMAIN_WALKTHROUGHS = _DOMAIN_CONTENT

_VISUAL_KIND = {
    "abstraction": "concept_map",
    "modeling": "model_flow",
    "assumptions": "assumption_tree",
    "simplification": "simple_model",
    "uncertainty": "uncertainty_band",
    "optimization": "tradeoff_curve",
}

WORKSHOP_STYLES = [
    {**mode, "visual": _VISUAL_KIND[mode["id"]]}
    for mode in WORKSHOP_MODES
]


def classify_problem(problem: str) -> dict[str, str]:
    """Classify free text into a domain key for workshop content."""
    return {"domain_key": infer_problem_domain(problem)}


def get_walkthrough(domain_key: str, style_id: str) -> dict[str, Any]:
    """Domain + style walkthrough (used by tests and legacy callers)."""
    dom = _DOMAIN_CONTENT.get(domain_key, _DOMAIN_CONTENT["general"])
    base = dom.get(style_id, dom.get("abstraction", {}))
    structures = base.get("matters") or []
    if not structures and base.get("deeper_structure"):
        structures = [base["deeper_structure"][:120]]
    return {
        "structures": structures,
        "matters": base.get("matters", []),
        "ignore": base.get("ignore", []),
        "variables": base.get("variables", []),
        "unknowns": base.get("unknowns", []),
        "outputs": base.get("outputs", []),
        "assumptions": base.get("assumptions", []),
        "applications": base.get("applications", []),
        "deeper_structure": base.get("deeper_structure", ""),
    }
