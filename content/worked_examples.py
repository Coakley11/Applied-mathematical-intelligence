"""Worked example flows — specific questions with analyst walkthroughs."""

from __future__ import annotations

CUSTOM_SUFFIX = "Custom question (type below)"


def _ex(
    area_id: str,
    pattern_id: str,
    question: str,
    asked: str,
    problem_kind: str,
    variables: list[str],
    assumptions: list[str],
    math_helps: str,
    worked_simple: str,
    interactive: str,
    deeper_math: dict[str, str],
    interpretation: str = "",
    recommendation: str = "",
    interactive_defaults: dict | None = None,
    math_translation: str = "",
    abstract_structure: dict | None = None,
) -> dict:
    out = {
        "area_id": area_id,
        "pattern_id": pattern_id,
        "question": question,
        "asked": asked,
        "problem_kind": problem_kind,
        "variables": variables,
        "assumptions": assumptions,
        "math_helps": math_helps,
        "worked_simple": worked_simple,
        "interactive": interactive,
        "interactive_defaults": interactive_defaults or {},
        "deeper_math": deeper_math,
        "interpretation": interpretation,
        "recommendation": recommendation,
    }
    if math_translation:
        out["math_translation"] = math_translation
    if abstract_structure:
        out["abstract_structure"] = abstract_structure
    return out


WORKED_EXAMPLES: list[dict] = [
    # --- Betting & Gambling ---
    _ex(
        "betting", "betting",
        "Is this +150 bet worth it if I think the true win probability is 45%?",
        "You want to know if the **long-run expected profit** is positive — not whether you will win once.",
        "**Expected value / probability decision** — compare your P(win) to the odds-implied probability.",
        ["Stake ($)", "Profit if win ($)", "Your P(win)", "Implied P(market)", "Expected value ($)"],
        ["Your 45% estimate is accurate", "Odds won't move before the bet", "You can repeat similar bets many times"],
        "Probability converts odds to implied chance; EV = P(win)×profit − P(lose)×stake.",
        (
            "At **+150**, implied probability ≈ 100/(150+100) = **40%**.\n\n"
            "If you stake **$100**, profit if win = $150, lose $100 if loss.\n\n"
            "EV = 0.45×150 − 0.55×100 = **$12.50** per bet.\n\n"
            "Since 45% > 40%, the bet is **+EV** at your estimate — but verify how you got 45%."
        ),
        "ev_bet",
        {
            "Probability": "Implied P from +150: 40%. Your edge = 45% − 40% = 5 percentage points.",
            "Expected value": "EV = Σ P(outcome)×payoff. Positive EV does not guarantee a win on one bet.",
            "Break-even": "Break-even P = stake / (stake + profit) ≈ 40% for +150.",
        },
        "A single loss does not disprove +EV; track many bets.",
        "Reasonable +EV at 45% — bet size should still respect bankroll variance.",
        {"p": 45, "odds": "+150", "stake": 100},
    ),
    _ex(
        "betting", "betting",
        "Should I risk $50 to win $120?",
        "You are comparing a **$50 risk** against a **$120 upside** — an EV and break-even probability question.",
        "**Expected value decision** — find the win probability that makes the bet fair, then compare to your estimate.",
        ["Amount risked ($50)", "Net profit if win ($120)", "P(win) you believe", "Break-even P"],
        ["Payout is fixed at $120 on win (total return $170)", "You lose exactly $50 on a loss", "No pushes or partial wins"],
        "Break-even P = risk / (risk + profit) = 50/170 ≈ **29.4%**. If your P(win) > 29.4%, EV is positive.",
        (
            "Profit if win = **$120** (you risk $50).\n\n"
            "Break-even: 50 / (50+120) = **29.4%**.\n\n"
            "If you think P(win) = 40%: EV = 0.40×120 − 0.60×50 = **+$18**.\n\n"
            "If you think P(win) = 25%: EV = 0.25×120 − 0.75×50 = **−$7.50** (don't bet)."
        ),
        "ev_bet",
        {"Expected value": "EV = P×120 − (1−P)×50.", "Risk": "Even +EV bets have losing streaks — size for survival."},
        "The question is really: is your probability above 29.4%?",
        "Estimate P(win) from data; if above break-even, +EV — then choose stake size.",
        {"p": 40, "odds": "+240", "stake": 50},
    ),
    _ex(
        "betting", "betting",
        "What is the break-even probability for these odds?",
        "You want the **minimum true win rate** that makes the wager neither +EV nor −EV long-term.",
        "**Inverse probability** from odds — solve for P where EV = 0.",
        ["American odds", "Stake", "Profit if win", "Break-even P"],
        ["Standard payout rules (no vig ignored unless stated)", "Single wager, no correlation to other bets"],
        "For +odds: break-even P = 100/(odds+100). For −odds: break-even P = |odds|/(|odds|+100).",
        (
            "**+150:** break-even P = 100/250 = **40%**.\n\n"
            "**−110:** break-even P = 110/210 ≈ **52.4%** (the book's vig is built in).\n\n"
            "You need a *higher* true chance than break-even to have +EV."
        ),
        "ev_bet",
        {"Vig": "Books set lines so break-even exceeds 50% on symmetric bets — that's the house edge."},
        "Break-even is the hurdle; your estimate must clear it with room for error.",
        "Convert odds first, then compare to your probability estimate.",
        {"p": 45, "odds": "+150", "stake": 100},
    ),
    _ex(
        "betting", "betting",
        "What is the expected value if I stake $100 at -110 and estimate a 55% win chance?",
        "Compute **dollar EV per bet** when you risk $110 to win $100 (typical −110 pricing).",
        "**Expected value** with American favorite odds.",
        ["Stake to win $100 (often $110)", "P(win) = 55%", "Profit if win", "Loss if lose"],
        ["−110 means bet $110 to win $100", "55% is your model, not the market's implied 52.4%"],
        "Implied P at −110 ≈ 52.4%. EV = P×100 − (1−P)×110.",
        (
            "At **−110**, you risk **$110** to win **$100**.\n\n"
            "EV = 0.55×100 − 0.45×110 = 55 − 49.5 = **+$5.50** per bet.\n\n"
            "Small edge — real-world tracking matters to confirm 55%."
        ),
        "ev_bet",
        {"Edge": "55% − 52.4% ≈ 2.6 points — modest; variance still dominates short runs."},
        "Positive EV here is thin — record results to validate.",
        "+EV at your inputs; don't oversize bets on thin edges.",
        {"p": 55, "odds": "-110", "stake": 110},
    ),
    _ex(
        "betting", "betting",
        "Is a 4-to-1 payout fair if I think I have a 25% chance?",
        "Check whether **market price matches** your probability — fair means break-even at your stated chance.",
        "**Fair odds comparison** — break-even P = 1/(1+4) = 20% for 4-to-1.",
        ["P(win) you believe (25%)", "Payout ratio (4:1)", "Break-even P (20%)"],
        ["4-to-1 means profit = 4× stake on win", "25% is your subjective or model-based estimate"],
        "Fair if your P equals break-even; +EV if yours is higher.",
        (
            "4-to-1 ⇒ break-even P = 1/5 = **20%**.\n\n"
            "You estimate **25%** ⇒ EV = 0.25×4S − 0.75×S = **+0.25S** per dollar staked.\n\n"
            "The offer is **better than fair** for you *if* 25% is right."
        ),
        "ev_bet",
        {"Calibration": "If you're often wrong about 25%, the edge disappears."},
        "Math says +EV; question is quality of the 25% estimate.",
        "Favorable vs. fair odds — still validate your probability.",
        {"p": 25, "odds": "+400", "stake": 100},
    ),
    _ex(
        "betting", "betting",
        "I want to bet $200 that Aaron Judge hits 30 home runs. Is it a good bet?",
        "You are risking **$200** on a **season prop** — compare your P(Judge ≥ 30 HR) to what the payout implies.",
        "**Expected value on a binary prop** — same logic as a moneyline, different story.",
        ["Stake ($200)", "Profit if prop hits", "Your P(30+ HR)", "Break-even P", "EV ($)"],
        ["Playing time and health folded into your probability", "Payout fixed at bet time", "No push on season totals"],
        "Break-even P = stake/(stake+profit). EV = P×profit − (1−P)×stake. Build P(30+) from rate × opportunities.",
        (
            "Example: risk **$200** to win **$180** (total return $380).\n\n"
            "Break-even P = 200/380 ≈ **52.6%**.\n\n"
            "If your model says **38%** for 30+ HR ⇒ **−EV**.\n\n"
            "If your model says **55%** ⇒ EV = 0.55×180 − 0.45×200 = **+$9**.\n\n"
            "Shrink hot starts toward career norms before trusting a high P."
        ),
        "ev_prop",
        {
            "Count models": "HR ≈ rate × plate appearances; uncertainty widens the distribution.",
            "Market": "Books aggregate many models — beating them needs edge, not narrative.",
        },
        "The bet is good only if your P(30+) clears break-even with margin for error.",
        "Build P(30+) from projected rate and games; compare to implied odds.",
        {"stake": 200, "profit": 180, "p": 38},
        math_translation=(
            "This is an **expected value** problem: compare payout to the probability the prop cashes."
        ),
        abstract_structure={
            "kind": "Decision under uncertainty — binary outcome (prop hits or not).",
            "comparing": "Your P(30+ HR) vs. break-even probability from the price.",
            "unknown": "True chance Judge reaches 30 HR this season.",
            "needs_estimate": "HR rate, playing time, park factors, injury risk.",
            "structure": "EV = P(win)×profit − P(lose)×stake.",
        },
    ),
    # --- Sports Prediction ---
    _ex(
        "sports", "sports",
        "Is an Aaron Judge 30+ home run prop bet reasonable?",
        "Estimate **P(Judge ≥ 30 HR)** and compare to what the prop price implies — an EV question on a season total.",
        "**Probability forecasting** + **prop pricing** (similar to betting EV).",
        ["Career/season HR rate", "Games remaining", "Health", "Park factors", "Prop payout"],
        ["Playing time roughly as expected", "Injury risk folded into your P", "Line reflects market's collective estimate"],
        "Binomial/Poisson approximations for counts; compare your P to implied P from odds.",
        (
            "Example sketch: if Judge needs 30 and you project **35 HR** with uncertainty, "
            "build a distribution (not just a point guess).\n\n"
            "If the book implies **25%** for 30+ but your model says **40%**, there may be edge.\n\n"
            "Shrink extreme early-season rates toward career norms."
        ),
        "ev_prop",
        {
            "Regression to mean": "Hot starts overstate true talent in small samples.",
            "Count models": "HR totals often modeled as rate × opportunities.",
        },
        "Prop bets are EV problems dressed as player narratives.",
        "Build P(30+) from rate × playing time; compare to implied odds.",
        {"stake": 200, "profit": 180, "p": 38},
    ),
    _ex(
        "sports", "sports",
        "How would I estimate the Knicks' chance to win tonight?",
        "Produce **P(Knicks win)** using team strength, home court, injuries, and rest — then compare to market odds if betting.",
        "**Probability forecasting** for a single game.",
        ["Team ratings (Elo, net rating)", "Home advantage", "Injury adjustments", "Back-to-back/rest"],
        ["Rating system calibrated on past seasons", "Injuries quantified (not just narrative)"],
        "Logistic win-probability models; start baseline ~50% home vs. similar team, adjust.",
        (
            "1. Baseline from rating difference (e.g. Elo ⇒ win%).\n"
            "2. Adjust **+3–4%** home if applicable.\n"
            "3. Subtract for key injuries (estimate points or rating lost).\n"
            "4. Report a **range** (e.g. 54–62%), not false precision.\n\n"
            "Example: baseline 58% → injury −5% ⇒ **~53%**."
        ),
        "ev_bet",
        {"Shrinkage": "Early-season extremes regress toward prior-year talent."},
        "One-game predictions are noisy — wide intervals are honest.",
        "Separate prediction from bet decision; betting needs edge vs. market.",
        {"p": 55, "odds": "-110", "stake": 100},
    ),
    _ex(
        "sports", "sports",
        "How do injuries change a win probability?",
        "Quantify how much **team strength drops** when a player is out, then shift P(win).",
        "**Sensitivity analysis** on a probability model.",
        ["Player value (WAR, plus-minus, rating points)", "Replacement level", "Opponent strength"],
        ["Linear adjustment is approximate", "Injuries to multiple players compound uncertainty"],
        "Adjust rating → recompute win probability (often logistic link from rating gap).",
        (
            "If the star is worth **+4 rating points** and the team drops from +2 to −2 vs. opponent:\n"
            "win% might move from **58% → 48%** (illustrative).\n\n"
            "Always widen uncertainty when injury news is fresh."
        ),
        "ev_bet",
        {"Uncertainty": "Minutes restrictions and game-time decisions add noise."},
        "Injuries shift the mean and widen the distribution.",
        "Update P(win) after quantifying impact — don't guess 'big injury = −10%'.",
        {"p": 48, "odds": "-110", "stake": 100},
    ),
    _ex(
        "sports", "sports",
        "My model says 58% but the market implies 52% — is there edge?",
        "Check if **58% − 52% = 6 points** is real edge or model overconfidence after EV math.",
        "**Expected value** vs. market-implied probability.",
        ["Your P(win)", "Implied P from odds", "Edge (percentage points)", "EV per dollar"],
        ["Your model is calibrated on past data", "Market is hard to beat consistently"],
        "EV > 0 when your P exceeds implied P enough to overcome vig.",
        (
            "Implied **52%** vs. model **58%** ⇒ apparent **6-point edge**.\n\n"
            "On −110, EV per $100 risked ≈ 0.58×91 − 0.42×100 (adjust for exact odds).\n\n"
            "Ask: has your model been **calibrated** out-of-sample?"
        ),
        "sports_edge",
        {"Closing line value": "Pros track whether their picks beat the closing line."},
        "Apparent edge ≠ guaranteed profit — validate model calibration.",
        "Possible edge — track bets and compare to closing odds.",
        {"model": 58, "market": 52, "injury": 0},
    ),
    _ex(
        "sports", "sports",
        "Is a rookie's hot first month predictive of full-season performance?",
        "Ask whether **small-sample stats** predict future performance — a statistics/regression question.",
        "**Regression to the mean** / shrinkage estimation.",
        ["First-month stat rate", "Sample size (PA, minutes)", "Prior (league average, draft position)"],
        ["Skill is somewhat stable", "Role/minutes may change"],
        "Shrink rookie stats toward league average; confidence intervals widen with small n.",
        (
            "Hot month often **overstates** true talent.\n\n"
            "Analyst move: estimate full-season rate as weighted blend: "
            "**w×hot_rate + (1−w)×prior**, with small w when n is small.\n\n"
            "Betting/on projections based only on one month is risky."
        ),
        "ev_bet",
        {"Shrinkage": "James-Stein / empirical Bayes pulls extremes toward the mean."},
        "Small samples exaggerate — shrink before predicting.",
        "Don't over-weight one hot month; use shrinkage.",
        {"p": 50, "odds": "+100", "stake": 100},
    ),
    # --- Medicine ---
    _ex(
        "medicine", "medicine",
        "How could we compare two cancer treatments?",
        "Compare **outcomes between groups** assigned to treatment A vs. B — causally, not by anecdote.",
        "**Statistical inference** / randomized controlled trial design.",
        ["Primary endpoint (survival, progression)", "Sample size", "Effect size", "p-value / confidence interval"],
        ["Random assignment", "Comparable groups at baseline", "Predefined endpoints"],
        "Hypothesis tests, hazard ratios, confidence intervals — control confounding.",
        (
            "1. Randomize patients to A or B.\n"
            "2. Predefine endpoint (e.g. median survival).\n"
            "3. Collect data; estimate **hazard ratio** with CI.\n"
            "4. Decide if difference is beyond chance (and clinically meaningful).\n\n"
            "Without randomization, confounders break the comparison."
        ),
        "growth",
        {
            "RCT": "Randomization balances known and unknown confounders in expectation.",
            "Survival analysis": "Kaplan-Meier curves and log-rank tests compare groups over time.",
        },
        "Treatment A 'better' stories need control-arm evidence.",
        "Design: randomized trial with predefined endpoint.",
        {"g": 10, "k": 12},
    ),
    _ex(
        "medicine", "medicine",
        "How does tumor growth change if treatment slows growth by 30%?",
        "Model **net growth rate** when therapy reduces proliferation — a rates-of-change question.",
        "**Calculus / growth model** — dV/dt = growth − kill.",
        ["Untreated growth rate", "Treatment effect (30% slowdown)", "Net rate", "Tumor volume over time"],
        ["Effect is proportional slowdown of growth component", "Kill rate separate from growth slowdown"],
        "Exponential or logistic growth models; net rate = g − k.",
        (
            "If untreated growth = **10%/month**, 30% slowdown ⇒ effective g = **7%/month**.\n\n"
            "If kill rate k = **8%/month**, net = 7 − 8 = **−1%/month** (shrinkage).\n\n"
            "If k = **5%/month**, net = **+2%/month** (still growing)."
        ),
        "growth",
        {"ODE": "dV/dt = (g − k)V is a simple exponential model."},
        "Slowing growth 30% is not the same as cure — net rate decides direction.",
        "Compute net growth rate; compare to zero.",
        {"g": 7, "k": 8},
    ),
    _ex(
        "medicine", "medicine",
        "How do clinical trials use statistics to decide if a treatment works?",
        "Test whether observed benefit is **unlikely under 'no effect'** (null hypothesis) given sample size.",
        "**Hypothesis testing** + **power** + **effect size**.",
        ["Null hypothesis", "p-value", "Confidence interval", "Power", "Sample size", "Endpoint"],
        ["Protocol set before data peeking", "Multiple endpoints controlled for false positives"],
        "t-tests, log-rank tests, Bayesian alternatives; pre-specify success criteria.",
        (
            "1. H₀: no difference vs. control.\n"
            "2. Collect n patients per arm.\n"
            "3. If p < α (e.g. 0.05) and effect clinically meaningful ⇒ evidence against H₀.\n\n"
            "**p-value** = P(data this extreme | H₀ true) — not P(H₀ false)."
        ),
        "growth",
        {"p-value": "Misinterpreted often — it is not P(treatment works).", "Power": "Enough n to detect clinically relevant effects."},
        "Statistics rule out chance; clinicians judge importance.",
        "Pre-register endpoint; report effect size + CI, not only p.",
        {"g": 10, "k": 14},
    ),
    _ex(
        "medicine", "medicine",
        "Is 60% tumor shrinkage without a control group convincing?",
        "Ask what shrinkage would occur **without** the drug — attribution requires comparison.",
        "**Causal inference** — missing control arm.",
        ["Treatment shrinkage rate", "Natural history / placebo shrinkage", "Sample size", "Bias"],
        ["60% is response in treated patients only", "No concurrent control"],
        "Need control arm or historical control with caveats; regression to mean in single arm.",
        (
            "**No** — 60% alone doesn't prove the drug caused it.\n\n"
            "Some tumors shrink spontaneously or from standard care.\n\n"
            "Convincing evidence: randomized control shows **higher** shrinkage or survival than control."
        ),
        "growth",
        {"Single-arm bias": "Enriched populations and measurement regression inflate apparent effects."},
        "Response rate without control is weak evidence.",
        "Require comparison group before claiming the drug works.",
        {"g": 10, "k": 6},
    ),
    # --- AI ---
    _ex(
        "ai", "ai",
        "Why is my training accuracy high but validation accuracy low?",
        "Diagnose **overfitting** — the model memorized training noise instead of learning general patterns.",
        "**Generalization gap** / bias-variance.",
        ["Training error", "Validation error", "Model complexity", "Data size", "Regularization"],
        ["Train/val split reflects deployment", "Same feature pipeline for both sets"],
        "Regularization, more data, simpler models, early stopping; train/val gap monitors fit.",
        (
            "Training **92%**, validation **78%** ⇒ **14-point gap**.\n\n"
            "Typical causes: too many parameters, too few examples, training too long.\n\n"
            "Fixes: dropout/L2, simpler architecture, augmentation, stop when val error rises."
        ),
        "ml_split",
        {
            "Bias-variance": "High variance ⇒ overfitting; high bias ⇒ underfitting.",
            "Early stopping": "Stop training when validation loss stops improving.",
        },
        "Memorization looks like learning on training data only.",
        "Treat as overfitting until proven otherwise; simplify or regularize.",
        {"tr": 92, "va": 78},
    ),
    _ex(
        "ai", "ai",
        "How does a model reduce error?",
        "Adjust parameters to **lower loss** on examples — optimization drives learning.",
        "**Optimization** minimizing a loss function.",
        ["Weights", "Loss L(y, ŷ)", "Learning rate", "Gradients"],
        ["Differentiable model", "Representative training sample"],
        "Gradient descent: w ← w − η∇L; backprop computes gradients in neural nets.",
        (
            "1. Predict ŷ = f(x; w).\n"
            "2. Compute loss (e.g. squared error, cross-entropy).\n"
            "3. Update w in direction that **reduces** loss.\n"
            "4. Repeat until validation loss plateaus.\n\n"
            "Goal: low loss on **new** data, not only training."
        ),
        "ml_split",
        {"Gradient descent": "Move parameters opposite the gradient of loss.", "Loss": "Defines what 'wrong' means."},
        "Training minimizes loss; success is low validation loss.",
        "Pick loss matching the task; monitor validation.",
        {"tr": 85, "va": 82},
    ),
    _ex(
        "ai", "ai",
        "How does learning rate affect training?",
        "Learning rate η controls **step size** in optimization — too big diverges, too small crawls.",
        "**Optimization dynamics** — sensitivity to hyperparameter η.",
        ["Learning rate η", "Loss curve", "Convergence", "Stability"],
        ["Smooth enough loss landscape locally", "Batch size interacts with η"],
        "Experiment with η on validation; learning rate schedules decay η over time.",
        (
            "**η too high:** loss spikes or NaN (overshoots minimum).\n"
            "**η too low:** needs many epochs; may stuck in slow progress.\n"
            "**Reasonable η:** training and validation loss decrease smoothly.\n\n"
            "Try 1e-3, 1e-4 for many nets; use a validation curve."
        ),
        "ml_split",
        {"Schedules": "Reduce η when progress stalls (step decay, cosine)."},
        "η is a knob on speed vs. stability.",
        "Tune on validation loss — not training loss alone.",
        {"tr": 88, "va": 85},
    ),
    _ex(
        "ai", "ai",
        "How much data do I need before trusting test accuracy?",
        "Enough **labeled examples** that test-set metrics have low variance and reflect deployment.",
        "**Sample size** + **evaluation design**.",
        ["Test set size", "Confidence interval on metric", "Class balance", "Distribution shift"],
        ["Test set held out once", "Examples i.i.d. (often approximate)"],
        "Binomial CI for accuracy; power analysis for detecting minimum acceptable performance.",
        (
            "Rule of thumb: **hundreds per class** minimum for simple classifiers; "
            "deep learning often needs **thousands+**.\n\n"
            "With n=50 test examples, accuracy has wide CI (e.g. 80% ± 11%).\n\n"
            "Use **validation** for tuning; **test once** at end."
        ),
        "ml_split",
        {"CI": "Wilson interval for proportions on test accuracy."},
        "Small test sets make metrics noisy.",
        "Report CI on test metric; don't tune on test.",
        {"tr": 90, "va": 84},
    ),
    # --- Space ---
    _ex(
        "space", "space",
        "How do you predict how high a rocket will go?",
        "Integrate **motion under gravity** (and thrust while engines burn) to find maximum altitude.",
        "**Kinematics / ODE** — velocity and position vs. time.",
        ["Initial velocity", "Thrust", "Mass (fuel burn)", "Gravity", "Drag (optional)"],
        ["1D vertical flight sketch", "Constant g approximation", "Drag ignored or simplified"],
        "v(t), y(t) from F=ma; burn phase then coast; peak when v=0.",
        (
            "Burn: a = (thrust − mg)/m; velocity increases.\n"
            "Coast: a = −g; velocity decreases.\n"
            "**Peak height** when v = 0 after coast.\n\n"
            "Rough energy: ½mv² ⇒ h ≈ v²/(2g) if no drag at coast start."
        ),
        "motion",
        {
            "Kinematics": "y = y₀ + v₀t − ½gt² (no thrust).",
            "Rocket equation": "Δv depends on exhaust velocity and mass ratio.",
        },
        "Peak altitude follows from thrust phase then ballistic coast.",
        "Model thrust burn, then set v=0 to find apex.",
        {"v": 500, "r": 6371},
    ),
    _ex(
        "space", "space",
        "How does launch angle affect trajectory?",
        "Launch angle splits initial velocity into **vertical and horizontal** components — shapes range and apex.",
        "**Projectile motion** / trajectory optimization.",
        ["Launch speed", "Launch angle θ", "Range", "Max height", "Time of flight"],
        ["No drag", "Flat earth local", "Uniform gravity"],
        "Range R ≈ v²sin(2θ)/g; max height from vertical component v sin θ.",
        (
            "θ = **45°** maximizes range on flat ground (no drag).\n"
            "θ > 45° ⇒ higher apex, shorter range.\n"
            "θ < 45° ⇒ lower apex, flatter arc.\n\n"
            "Orbits need horizontal speed, not just upward launch."
        ),
        "projectile",
        {"Components": "vx = v cos θ, vy = v sin θ.", "Orbits": "Need sufficient horizontal v for closed orbit."},
        "Angle trades height for distance.",
        "Pick θ for mission: range vs. altitude vs. orbit insertion.",
        {"v0": 800, "angle": 45, "g": 9.81},
    ),
    _ex(
        "space", "space",
        "How would you optimize fuel or path?",
        "Minimize **fuel use** subject to reaching target position/velocity — optimal control.",
        "**Optimization / calculus of variations**.",
        ["Fuel mass", "Thrust profile", "Trajectory", "Constraints (time, safety corridor)"],
        ["Gravity field known", "Simplified dynamics model"],
        "Optimal control (Pontryagin), numerical trajectory optimization, convex relaxations.",
        (
            "Formulate: minimize fuel s.t. final state = target.\n"
            "Trade **gravity turn** vs. direct ascent.\n"
            "Numerical solvers adjust thrust direction over time.\n\n"
            "Engineers iterate model ↔ simulation ↔ measurement."
        ),
        "motion",
        {"Rocket equation": "Δv = ve ln(m₀/mf).", "Numerical optimization": "Discretize path, optimize thrust schedule."},
        "Fuel optimization is constrained trajectory design.",
        "Define target state; optimize thrust program numerically.",
        {"v": 7800, "r": 6771},
    ),
    _ex(
        "space", "space",
        "What velocity is needed for a circular orbit at 400 km altitude?",
        "Find **circular orbital speed** where centripetal acceleration equals gravity at that radius.",
        "**Orbital mechanics** — balance v²/r and g(r).",
        ["Orbital radius r", "Earth mass M", "Circular speed v", "Altitude"],
        ["Point mass gravity", "No atmosphere", "Circular orbit"],
        "v = √(GM/r); at 400 km, r ≈ 6771 km.",
        (
            "r = R_Earth + 400 km ≈ **6,771,000 m**.\n"
            "v ≈ √(GM/r) ≈ **7,670 m/s** (~27,600 km/h).\n\n"
            "Wrong speed ⇒ elliptical orbit or re-entry."
        ),
        "motion",
        {"Vis-viva": "v² = GM(2/r − 1/a) generalizes ellipses.", "LEO": "Low Earth orbit ~7.8 km/s near 400 km."},
        "Circular speed fixed by radius.",
        "Use v = √(GM/r) with r = center-to-center distance.",
        {"v": 7670, "r": 6771},
    ),
    # --- Forecasting ---
    _ex(
        "forecasting", "weather",
        "How confident should we be in a weather forecast?",
        "Confidence should match **historical calibration** — how often 30% rain days actually rained.",
        "**Probabilistic forecasting** + **calibration**.",
        ["Lead time", "Ensemble spread", "Historical hit rate", "Forecast metric"],
        ["Forecast system stable", "User understands probabilistic meaning"],
        "Reliability diagrams; Brier score; ensemble spread as uncertainty proxy.",
        (
            "**Day 1:** often strong — narrow uncertainty.\n"
            "**Day 7+:** weak detail — wide ensembles.\n\n"
            "30% rain ⇒ about **3 in 10** similar days rain — not 'light rain for sure'.\n\n"
            "Trust **calibrated** probabilities, not single deterministic icons."
        ),
        "forecast_range",
        {
            "Calibration": "Predicted 30% should rain ~30% of the time.",
            "Chaos": "Small errors grow — limits long-range detail.",
        },
        "Confidence decreases with lead time.",
        "Check calibration; widen uncertainty at longer leads.",
        {"lead": 2},
    ),
    _ex(
        "forecasting", "weather",
        "How does uncertainty grow over time?",
        "Small errors in **initial conditions** amplify — forecast distributions widen with lead time.",
        "**Dynamical chaos** in weather models.",
        ["Lead time", "Ensemble spread", "Initial condition error"],
        ["Model captures large-scale physics", "Spread reflects realistic sensitivity"],
        "Ensemble weather prediction; variance often grows roughly with √t early on.",
        (
            "Illustrative band: **±5%** day 1 → **±15%** day 5 → **±30%** day 10 (schematic).\n\n"
            "Use **ensembles** (many model runs) to see range of futures.\n\n"
            "Point forecasts hide this — prefer intervals."
        ),
        "forecast_range",
        {"Ensembles": "Perturb initial conditions; cloud of outcomes.", "Lorenz": "Sensitive dependence."},
        "Never treat day-7 like day-1 precision.",
        "Report wider bands at longer leads.",
        {"lead": 7},
    ),
    _ex(
        "forecasting", "weather",
        "How do simulations create multiple possible futures?",
        "Run the model **many times** with slightly different starts or parameters — Monte Carlo / ensembles.",
        "**Simulation** / ensemble forecasting.",
        ["Initial conditions", "Model parameters", "Random shocks", "Outcome distribution"],
        ["Model structure fixed", "Perturbations sample realistic uncertainty"],
        "Monte Carlo: many trajectories ⇒ empirical distribution of outcomes.",
        (
            "1. Start from measured weather now (with noise).\n"
            "2. Integrate physics forward **50×** with tweaks.\n"
            "3. **Spread** of runs = uncertainty.\n\n"
            "Same idea in finance (scenario paths) and epidemics (SIR Monte Carlo)."
        ),
        "forecast_range",
        {"Monte Carlo": "Sample inputs → distribution of outputs.", "SIR": "Epidemic sims use same ensemble idea."},
        "One run is one possible future; many runs show risk.",
        "Use ensembles when a point forecast is misleading.",
        {"lead": 5},
    ),
    _ex(
        "forecasting", "weather",
        "A model says 30% rain — what does that mean for planning?",
        "It means **roughly 3 in 10** days with similar conditions had measurable rain — not 'unlikely'.",
        "**Probability interpretation** for decisions.",
        ["Event definition (rain amount)", "Forecast probability", "Cost of wrong prep"],
        ["Forecast is calibrated", "Your cost of umbrella vs. soak is yours"],
        "Decision theory: compare expected cost of actions under P(rain).",
        (
            "Outdoor wedding? Compare:\n"
            "- Cost(plan indoor | rain) × 0.30\n"
            "- Cost(plan outdoor | no rain) × 0.70\n\n"
            "**30%** can still justify backup if downside is large."
        ),
        "forecast_range",
        {"Expected cost": "Choose action minimizing expected loss."},
        "30% is material when stakes are asymmetric.",
        "Decide with expected cost — not gut feel on %. ",
        {"lead": 1},
    ),
    # --- Abstract ---
    _ex(
        "abstract", "abstract",
        "How do I turn a word problem into a mathematical structure?",
        "Extract **goal, quantities, relationships, limits** — then assign symbols.",
        "**Mathematical modeling** — translation step.",
        ["Objective (maximize, predict, compare)", "Knowns", "Unknowns", "Constraints"],
        ["Problem is well-posed", "One primary question"],
        "Template: maximize/minimize f(x) s.t. g(x) ≤ c; or estimate P(event).",
        (
            "1. Underline the **question** (one sentence).\n"
            "2. List **nouns that vary** (variables).\n"
            "3. Write **relationships** in words, then symbols.\n"
            "4. Note **limits** (budget, time, rules).\n\n"
            "Example: 'best bet' ⇒ maximize EV subject to bankroll."
        ),
        "structure",
        {"Modeling cycle": "Real world → math → solution → interpret."},
        "Words hide structure — expose goal and variables first.",
        "Write objective, variables, constraints before formulas.",
        {},
    ),
    _ex(
        "abstract", "abstract",
        "How do I know whether a problem is about probability, optimization, calculus, or statistics?",
        "Match **verbs and goals** to tool families.",
        "**Tool classification**.",
        ["Question type", "Data available", "Time/evolution", "Uncertainty"],
        ["One primary tool often dominates first pass"],
        "Probability: chance/EV; Statistics: data→estimate; Calculus: change; Optimization: best choice.",
        (
            "| Clue | Tool |\n"
            "|------|------|\n"
            "| odds, chance, bet | **Probability / EV** |\n"
            "| best, maximize, allocate | **Optimization** |\n"
            "| rate, growth, motion | **Calculus / ODE** |\n"
            "| sample, trial, noise | **Statistics** |\n"
            "| many scenarios | **Simulation** |"
        ),
        "structure",
        {"Hybrid": "Real problems mix tools — start with the dominant structure."},
        "The question's goal picks the first tool.",
        "Classify goal first; combine tools only as needed.",
        {},
    ),
    _ex(
        "abstract", "abstract",
        "How do I simplify a complicated problem before solving it?",
        "Remove detail until a **smallest model** still answers the question.",
        "**Simplification / abstraction**.",
        ["Core lever", "Negligible effects", "Time horizon", "Linear vs. nonlinear"],
        ["Dropped effects are second-order", "Simple model testable"],
        "Start linear/static; add nonlinearities only when baseline fails.",
        (
            "1. Answer in one sentence — what number/decision?\n"
            "2. Keep **3–5 variables** max at first.\n"
            "3. Ignore effects <10% unless critical.\n"
            "4. Solve simple version; **stress-test** assumptions.\n\n"
            "Add complexity only when wrong answers matter."
        ),
        "structure",
        {"Occam": "Simplest adequate model wins for communication and speed."},
        "Complexity is earned, not assumed.",
        "Strip to 3–5 variables; validate before adding detail.",
        {},
    ),
    _ex(
        "abstract", "abstract",
        "What's the difference between predicting and optimizing?",
        "**Predicting** estimates what will happen; **optimizing** chooses the best action given a goal.",
        "**Conceptual distinction** — often sequential steps.",
        ["State variables", "Decision variables", "Objective", "Constraints"],
        ["Model of world is approximate", "Objective matches real goal"],
        "Predict ŷ = f(x); optimize x* = argmax g(x) s.t. constraints.",
        (
            "**Predict:** 'What is P(win)?' or 'What is demand next month?'\n\n"
            "**Optimize:** 'What price maximizes profit?' or 'What bet size maximizes log wealth?'\n\n"
            "Often: **predict first** (forecast demand), **then optimize** (set inventory)."
        ),
        "structure",
        {"Link": "Optimization uses predictions as inputs."},
        "Don't optimize until the objective and constraints are clear.",
        "Predict the world, then optimize your choice.",
        {},
    ),
]

WORKED_BY_QUESTION: dict[str, dict] = {ex["question"]: ex for ex in WORKED_EXAMPLES}

AREA_EXAMPLE_QUESTIONS: dict[str, list[str]] = {}
for _area in ("betting", "sports", "medicine", "ai", "space", "forecasting", "abstract"):
    AREA_EXAMPLE_QUESTIONS[_area] = [
        ex["question"] for ex in WORKED_EXAMPLES if ex["area_id"] == _area
    ] + [CUSTOM_SUFFIX]


def get_worked_example(question: str, area_id: str) -> dict | None:
    """Look up worked flow by exact question text."""
    if question in WORKED_BY_QUESTION:
        return WORKED_BY_QUESTION[question]
    return None


def get_example_questions(area_id: str) -> list[str]:
    return AREA_EXAMPLE_QUESTIONS.get(area_id, [CUSTOM_SUFFIX])
