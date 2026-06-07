# Applied Math Quality Validation — Round 2 (Math Coach)

**Date:** 2026-06-08  
**Build validated:** `2026-06-08-math-coach-v5` (UI 2.4.0)  
**Method:** Run each question through `solve_suite_question()` with realistic app context (full and partial). Scored **1–10 on user usefulness only** — not code, tests, or architecture.

**Scoring rubric**

| Score | Meaning |
|-------|---------|
| 9–10 | Teaches the math clearly, uses correct data, conclusion is actionable, controls change the answer meaningfully |
| 7–8 | Solid for exact-math questions; minor gaps in framing or missing one lever |
| 5–6 | Partially helpful — model explained but calculation thin, or controls don't fully compensate for missing data |
| 3–4 | Generic feel, wrong framing, or conclusion not trustworthy |
| 1–2 | Wrong route, wrong data, or effectively no answer |

---

## Executive summary

**Math Coach works well for narrow, numeric questions** where a dedicated solver exists:

- NBA stat chase (gap ÷ games)
- Baseball trend significance (slope + R² vs thresholds)
- Investment rebalance (drift vs threshold)
- Investment risk-return (Sharpe + volatility caps)

**Math Coach still fails or feels generic for broad questions** — player comparison, draft value, projection realism, matchup edge, probability reasonableness, concentration, macro sensitivity. These either fall through to **template stubs** or **generic fallback** with no real calculation.

**Biggest systemic gap:** Broad questions are routed to problem types that *describe* a model in prose but **do not execute it**. The user sees variables and a framework, not a worked example with their numbers.

---

## Validation set — question-by-question

### Baseball

---

#### 1. Is Lorenzo Cain's HR trend meaningful?

| Field | Value |
|-------|-------|
| **Problem type detected** | `baseball_trend_significance` — Trend significance |
| **Data received** | `trend_summary.slope=0.8`, `r2=0.15`, `direction=up`, `delta=3`, `player`, `metrics` |
| **Math model used** | Trend vs noise: meaningful if \|slope\| ≥ threshold AND R² ≥ threshold |
| **Variables used** | slope, R², delta, min_slope, min_r2 |
| **Conclusion** | “The trend is **up**, but only meaningful if R² is high enough — currently **0.15** vs **0.35** floor.” |
| **Confidence** | 58% (Medium) |
| **What assumptions matter** | R² threshold (noise filter); slope threshold (size of yearly change) |
| **What the user can change** | Minimum slope slider, minimum R² slider |
| **Score** | **8 / 10** |

**User usefulness:** Strong. Teaches slope vs R², shows plugged-in values, live verdict flips when thresholds change. Cain example (noisy positive slope) is exactly the kind of insight a user needs.

**Variant (strong trend):** slope=1.2, R²=0.64 → “Yes — meaningful” with live metrics. **Score 9/10.**

**Variant (missing slope/R²):** Partial answer + threshold sliders only. User cannot enter slope/R² hands-on. **Score 5/10.**

---

#### 2. Is Soto likely to surpass Judge?

| Field | Value |
|-------|-------|
| **Problem type detected** | `baseball_player_comparison` — Player comparison |
| **Data received (typical)** | `player_a=Juan Soto`, `player_b=Aaron Judge` only; `comparison_stats` missing |
| **Math model used (claimed)** | “Value gap = rate-stat difference adjusted for playing time and scarcity” |
| **Variables used (claimed)** | `value_i = rate stats per PA × playing-time projection` |
| **Conclusion (names only)** | “Possible but uncertain — rate stats not attached” |
| **Confidence** | 58% |
| **What assumptions matter** | Playing time, career length, scarce categories in league |
| **What the user can change** | **None** — no controls |
| **Score (names only)** | **3 / 10** |

**With comparison context attached** (`OPS: Soto 1.02 vs Judge 1.08`, `WAR`, `Age`):

| Field | Value |
|-------|-------|
| **Conclusion** | “**Juan Soto** leads on attached comparison stats” |
| **Calculation shown** | “Subtract rate-based value scores; weight scarce categories.” — **no numeric subtraction** |
| **Score (with stats)** | **4 / 10** |

**User usefulness:** Weak. The model is named but not run. “Surpass” implies **future** trajectory (age, playing time, projection) — the solver treats it as a static compare. **Bug:** when diff stats are attached, conclusion always says player_a leads even when Judge has higher OPS in the attached data.

**Broad-question diagnosis:** Generic framework. Not a math coach answer.

---

#### 3. Is this player worth a Round 2 draft pick?

| Field | Value |
|-------|-------|
| **Problem type detected** | `baseball_draft_decision` — Draft decision (router) |
| **Data received** | `player=Corbin Carroll`, `draft_projection="Round 1-2 borderline, ADP 18"`, `workflow=draft` |
| **Math model used (actual)** | **Generic fallback** — “Define measurable quantity, baseline, threshold” |
| **Variables used** | Generic placeholder only |
| **Conclusion** | “Best estimate unavailable — need numeric context” |
| **Confidence** | 53% |
| **What assumptions matter** | None surfaced |
| **What the user can change** | **None** |
| **Score** | **2 / 10** |

**User usefulness:** Router recognizes draft; **no draft solver exists**. ADP/projection in context is ignored. User gets the same generic stub as any unresolved type.

**Broad-question diagnosis:** Route label promises draft decision; delivery is generic.

---

#### 4. Is this projection realistic?

| Field | Value |
|-------|-------|
| **Problem type detected** | `baseball_generic` — Baseball decision analysis (confidence 0.35) |
| **Data received** | `player`, `metrics`, optional `trend_summary` or `projection` block |
| **Math model used (actual)** | Generic fallback |
| **Conclusion** | “Best estimate unavailable — need numeric context” |
| **What the user can change** | **None** |
| **Score** | **2 / 10** |

**Note:** Question lacks “trend” keyword, so even with HR trend data attached it does **not** route to trend solver. No shrinkage / regression-to-mean / rate-per-PA model exists for projections.

**Broad-question diagnosis:** No projection realism model implemented.

---

### NBA

---

#### 5. Will Brunson pass Allan Houston in playoff rebounds?

| Field | Value |
|-------|-------|
| **Problem type detected** | `nba_stat_chase` — NBA stat chase / rate needed |
| **Data received** | `stat_gap` (gap=24, current=30, target=54, games=6), `rate_needed=4.0` |
| **Math model used** | Rate-needed: required rate = gap ÷ games; compare to expected rate |
| **Variables used** | gap, games, required rate, expected rate, projected final |
| **Conclusion** | “Uncertain — depends on keeping **4.0** rebounds/game” (exact tie at required pace) |
| **Confidence** | 62% |
| **What assumptions matter** | Games remaining; expected per-game production; leader also adding stats (static gap) |
| **What the user can change** | Games remaining, expected stat/game, target total |
| **Score** | **8 / 10** |

**User usefulness:** Best-in-class Math Coach example. Clear calculation, live pass/fail, sensitivity on games remaining.

**Variant (missing games):** Defaults to 4 games, shows required rate 6.0, prompts controls. **Score 7/10.**

---

#### 6. How many games would Brunson need?

| Field | Value |
|-------|-------|
| **Problem type detected** | `nba_stat_chase` (same as #5) |
| **Data received** | Same stat_gap; no games_remaining |
| **Math model used** | Same rate-needed model |
| **Conclusion (actual)** | Pass/fail framing: “Probably no — needs **6.0**/game at 4 games…” |
| **What the user can change** | Same controls — but must **manually invert** games = gap ÷ expected rate |
| **Score** | **4 / 10** |

**User usefulness:** Wrong question shape. User asked **inverse** (“how many games?”); solver answers **forward** (“will he pass?”). Math is there but user must derive games themselves.

---

#### 7. Is this matchup edge meaningful?

| Field | Value |
|-------|-------|
| **Problem type detected** | `nba_matchup_edge` — Matchup edge |
| **Data received** | `team`, `opponent`, `matchup_advantages[]`, `injury_summary`, `series_probability=58%` |
| **Math model used (claimed)** | “Matchup edge — weight injuries and schematic advantages vs model probability” |
| **Variables used (claimed)** | edge, p (probability) |
| **Conclusion** | “Matchup assessed” + narrative concatenation of advantage/injury strings |
| **Calculation shown** | Qualitative rules only (“Large p without matching edge → optimism”) — **no numeric edge score** |
| **Confidence** | 78% |
| **What the user can change** | **None** |
| **Score** | **3 / 10** |

**User usefulness:** Does not answer “is the edge **meaningful**?” quantitatively. No threshold, no comparison of edge magnitude to probability swing. Reads like a context summary, not math coaching.

---

#### 8. Is this playoff probability reasonable?

| Field | Value |
|-------|-------|
| **Problem type detected** | `nba_win_probability` — Win probability reasonableness |
| **Data received** | `win_probability=62%`, `team`, optional `series_probability` |
| **Math model used (claimed)** | “Compare p to prior ±10pp” |
| **Conclusion (actual)** | Short answer is literally **“62%”** — not yes/no/borderline |
| **Calculation shown** | Template text; no prior computed, no ±10pp check executed |
| **What the user can change** | **None** |
| **Score** | **2 / 10** |

**User usefulness:** Fails the basic job. User asks “is this reasonable?” and gets the number repeated back.

---

### Investment

---

#### 9. Should I rebalance?

| Field | Value |
|-------|-------|
| **Problem type detected** | `investment_rebalance` — Rebalance decision |
| **Data received** | `rebalance_drift` (VTI +6pp, BND -4pp, …), `current_weights`, `target_weights` |
| **Math model used** | drift_i = current − target; rebalance if max \|drift\| ≥ threshold |
| **Variables used** | per-holding drift, drift_threshold, max_drift |
| **Conclusion** | “Yes — rebalance if threshold is **5pp** (max drift **6.0pp**).” |
| **Confidence** | 86% |
| **What assumptions matter** | Drift threshold; risk tolerance (conservative acts sooner) |
| **What the user can change** | Drift threshold slider, risk tolerance |
| **Score** | **9 / 10** |

**Variant (missing drift):** Explains model, threshold slider works, but no holdings to evaluate. **Score 5/10.**

---

#### 10. Is this return worth the volatility?

| Field | Value |
|-------|-------|
| **Problem type detected** | `investment_risk_return` — Risk-return tradeoff |
| **Data received** | `expected_return=8.2%`, `volatility=12.1%`, `sharpe_ratio=0.68` |
| **Math model used** | Sharpe ≈ return ÷ volatility vs user floors/caps |
| **Conclusion** | “Yes — **8.2%** return looks worth **12.1%** volatility at your thresholds.” |
| **Confidence** | 84% |
| **What assumptions matter** | Minimum Sharpe, acceptable volatility cap |
| **What the user can change** | Min Sharpe slider, acceptable volatility slider |
| **Score** | **8 / 10** |

**User usefulness:** Strong. Clear pass/fail, live metrics, sensitivity when vol cap tightens.

---

#### 11. How sensitive is this portfolio to recession assumptions?

| Field | Value |
|-------|-------|
| **Problem type detected** | `investment_macro_sensitivity` — Macro sensitivity |
| **Data received** | `macro_outlook`, `expected_return`, `volatility`, forward/historical notes |
| **Math model used (claimed)** | “Stress-test return/vol under macro scenario” |
| **Conclusion (actual)** | Echoes macro string: “Recession probability 30%; equity beta 1.1” |
| **Calculation shown** | “Compare base-case return/vol to recession scenario” — **not executed with numbers** |
| **What the user can change** | **None** |
| **Score** | **3 / 10** |

**User usefulness:** Has the inputs for a stress test but does not compute stressed return/vol or show delta. Not Math Coach — context echo.

---

#### 12. Is the portfolio too concentrated?

| Field | Value |
|-------|-------|
| **Problem type detected (actual)** | `investment_macro_sensitivity` — **WRONG** |
| **Expected route** | `investment_concentration` |
| **Root cause** | Router topic detector matches substring `"rate"` inside `"concentrated"` → macro topic wins before concentration check |
| **Data received** | `holdings`, `current_weights` (AAPL 28%, MSFT 22%, NVDA 18%, VTI 32%) |
| **Conclusion (actual)** | “Attach macro outlook” |
| **Score** | **1 / 10** |

**User usefulness:** Complete miss. User question ignored; no HHI, top-N weight, or concentration threshold model.

---

## Special focus — broad questions

| Question pattern | Routed model | Actually computed? | Useful as Math Coach? |
|------------------|--------------|--------------------|------------------------|
| Is Soto better / likely to surpass Judge? | Rate-stat value gap × playing time | **No** — prose + optional stat list | **No** — generic |
| Worth a Round 2 pick? | Draft decision (label only) | **No** — generic fallback | **No** |
| Is projection realistic? | baseball_generic | **No** | **No** |
| Is matchup edge meaningful? | Qualitative edge vs p | **No** numeric edge | **No** |
| Is probability reasonable? | Compare p to prior ±10pp | **No** prior computed | **No** |
| Too concentrated? | Macro sensitivity (**misrouted**) | **No** | **No** |
| Recession sensitivity? | Macro stress test | **No** stressed numbers | **No** |
| Is portfolio good / too risky? (generic) | risk_return if metrics present; else generic | Partial | **Sometimes** |

**Pattern:** Broad questions get **credible-sounding model names** in `math_idea` but **no worked calculation**, **no coach short answer**, and **no hands-on controls**. That is the main gap between product intent and current behavior.

**Exact-math questions** (chase, trend, rebalance, Sharpe) use the same UI pipeline but backed by real solvers — and score 7–9.

---

## Top 10 strongest question types

| Rank | Question type | Solver ID | Typical score | Why it works |
|------|---------------|-----------|---------------|--------------|
| 1 | Should I rebalance? (with drift) | `investment_rebalance` | 9 | Full drift math, live action, threshold controls |
| 2 | Is return worth the volatility? | `investment_risk_return` | 8 | Sharpe + caps, pass/fail dashboard |
| 3 | Is HR/stat trend meaningful? (slope+R² present) | `baseball_trend_significance` | 8–9 | Teaches trend vs noise; thresholds flip verdict |
| 4 | Will player pass leader in stat X? | `nba_stat_chase` | 8 | gap÷games, projected final, games/rate controls |
| 5 | Will player pass leader? (missing games) | `nba_stat_chase` | 7 | Defaults + hands-on games slider |
| 6 | Should I rebalance? (missing drift) | `investment_rebalance` | 5 | Model taught; threshold-only exploration |
| 7 | Is trend meaningful? (missing slope) | `baseball_trend_significance` | 5 | Model taught; thresholds only |
| 8 | Rebalance with conservative tolerance | `investment_rebalance` | 8 | Risk tolerance shifts action |
| 9 | Stat chase toss-up (rate ≈ required) | `nba_stat_chase` | 8 | Honest uncertainty + sensitivity |
| 10 | Risk-return borderline Sharpe | `investment_risk_return` | 7 | Borderline verdict + vol sensitivity |

---

## Top 10 weakest question types

| Rank | Question type | Solver ID | Typical score | Primary failure |
|------|---------------|-----------|---------------|-----------------|
| 1 | Is portfolio too concentrated? | Misrouted → `investment_macro_sensitivity` | 1 | **Routing bug** + no concentration solver |
| 2 | Is playoff/win probability reasonable? | `nba_win_probability` | 2 | Repeats p; no reasonableness check |
| 3 | Worth a Round N draft pick? | `baseball_draft_decision` → generic | 2 | No draft/ADP solver |
| 4 | Is projection realistic? | `baseball_generic` | 2 | No projection/shrinkage solver |
| 5 | How sensitive to recession? | `investment_macro_sensitivity` | 3 | No stress-test calculation |
| 6 | Is matchup edge meaningful? | `nba_matchup_edge` | 3 | Narrative only, no edge metric |
| 7 | Soto vs Judge / player surpass | `baseball_player_comparison` | 3–4 | Model not executed; wrong leader possible |
| 8 | How many games needed? (inverse chase) | `nba_stat_chase` | 4 | Wrong framing for question shape |
| 9 | Is portfolio good? (health only, no vol/ret) | `investment_generic` | 4 | Generic fallback |
| 10 | Historical outlier / comparison | `baseball_historical` | 4–5 | Peer comparison template; thin calculation |

---

## Weak-area themes

### 1. Generic feel
Draft, projection, generic baseball/investment, player compare (without structured stats), matchup edge, win probability, macro.

### 2. Wrong data used
- Concentration question → macro route (bug)
- Player compare → lists raw diff strings, doesn't parse OPS/WAR numerically
- Projection question → ignores projection block in context

### 3. Weak conclusions
- Win probability: conclusion = the input number
- Macro: conclusion = macro outlook string
- Player compare with stats: “player_a leads” regardless of data

### 4. Controls don't matter
No controls on: player compare, draft, projection, matchup, win prob, macro, concentration, historical.

Threshold-only controls when slope/drift missing can't complete the problem — user can explore thresholds but not fill missing inputs.

### 5. Model should be different
| User question | Better model |
|---------------|--------------|
| How many games needed? | Inverse: `games = gap ÷ expected_rate` (ceil to pass) |
| Surpass / better than | `Δ value = (rate_A − rate_B) × projected_PA`; controls: years, PA, aging |
| Draft pick worth it? | `ADP vs round threshold`; value over replacement |
| Projection realistic? | Shrinkage: `w × season_rate + (1−w) × career`; compare to projection |
| Matchup edge meaningful? | `edge_points` vs `Δ win_prob`; minimum edge threshold control |
| Probability reasonable? | `|p − p_prior| ≤ 10pp`; prior from Elo/record/injuries |
| Too concentrated? | HHI or top-3 weight sum vs threshold |
| Recession sensitivity? | `return_stressed = return − β × shock`; vol stress; controls: recession prob |

---

## Recommended next solver improvements (priority order)

### P0 — Fix correctness / routing (no new UI)

1. **Fix concentration routing bug** — do not match `"rate"` inside `"concentrated"`; route “concentrated” questions to `investment_concentration`.
2. **Fix player compare conclusion** — parse numeric stats; conclusion must reflect who actually leads; never default to player_a.
3. **Win probability stub** — compute reasonableness verdict (reasonable / high / low vs simple prior or ±10pp band); never echo p as short answer.

### P1 — Make broad questions executable (minimal new solvers)

4. **Concentration solver** — top-3 weight sum or HHI vs threshold; control: max single-name or top-3 %.
5. **Player compare coach** — subtract rate stats; “surpass” mode adds age/PA projection controls.
6. **Inverse NBA chase** — detect “how many games” phrasing; short answer = `ceil(gap / expected_rate)`.
7. **Macro stress solver** — `return_stressed`, `vol_stressed` from outlook; show delta; control: recession severity.

### P2 — Fill remaining app question types

8. **Draft decision solver** — ADP/round threshold vs projection tier; control: round number.
9. **Projection realism solver** — shrinkage toward career; compare to stated projection; control: shrinkage weight.
10. **Matchup edge solver** — numeric edge score vs probability; control: minimum meaningful edge.

### P3 — Missing-data hands-on inputs

11. Allow entering **slope/R²** when trend data missing (not just threshold sliders).
12. Allow entering **per-holding drift** when rebalance_drift missing.

---

## Verdict

**Math Coach direction is validated for exact-math suite questions** (rebalance, risk-return, trend, stat chase). A user can learn the model and experiment with assumptions.

**Not yet validated for broad suite questions**, which are common in real app usage (compare, draft, projection, probability, concentration, macro). These need **executable models** — not longer `math_idea` strings — before adding new features or UI redesign.

**Recommended next step:** Implement P0 + P1 (routing fix, concentration, player compare execution, win-prob verdict, inverse chase) and re-run this validation set. Target: no question in the validation set below **6/10**.

---

## Round 2 Re-validation (after P0 + P1 — build `2026-06-08-broad-solvers-p0p1-v6`)

| Question | Before | After | Notes |
|----------|--------|-------|-------|
| Is portfolio too concentrated? | 1/10 | **8/10** | Routes to `investment_concentration`; HHI + top-3 + controls |
| Soto surpass Judge (with stats) | 4/10 | **7/10** | Judge correctly leads; weighted score + category controls |
| Playoff probability reasonable? | 2/10 | **7/10** | Edge-band verdict, not echo; explains what makes it questionable |
| How many games would Brunson need? | 4/10 | **8/10** | `nba_inverse_stat_chase`; ceil(gap/rate) + sensitivity table |
| Recession sensitivity? | 3/10 | **7/10** | Base/mild/severe scenarios + stressed return/vol + controls |
| Is projection realistic? | 2/10 | **7/10** | `baseball_projection_realism`; gap vs baselines + tolerance controls |

**Still weak (unchanged this pass):**

| Question | Score | Gap |
|----------|-------|-----|
| Draft Round 2 worth it? | 2/10 | No draft solver (P2) |
| Matchup edge meaningful? | 3/10 | No numeric edge solver (P2) |
| Soto vs Judge (names only) | 4/10 | Partial — needs stats attached |
| Player compare “surpass” horizon | 5/10 | No playing-time projection controls yet |

**P0 bugs fixed:** concentration routing (`rate` word boundary); player compare numeric winner; win-prob reasonableness verdict.

**Verdict:** Broad-question quality improved from 1–4/10 to **6–8/10** on the six weakest validation cases. Safe to continue P2 (draft, matchup edge) before Return Insight or UI redesign.

---

## Appendix — validation harness

Reproduce solver output:

```bash
cd Applied-mathematical-intelligence
python -c "
from components.applied_math_solvers import solve_suite_question
route, r = solve_suite_question(
    'Will Brunson pass Allan Houston in playoff rebounds?',
    source_app='nba',
    context={'stat_gap': {'gap': 24, 'current_value': 30, 'target_value': 54, 'games_remaining': 6}, 'rate_needed': 4.0},
)
print(route.problem_type_id, r.short_answer, r.live_metrics)
"
```

Existing first-pass validation (separate path): `applied_math_quality_validation.py` — tests **first-pass analysis**, not rule-based solvers documented here.
