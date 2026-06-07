# Applied Math Quality P2 — Conclusion Engine

**Last updated:** 2026-06-06  
**Status:** Implemented on `dev`  
**Deferred:** Return Insight to Source App (after solver trust is validated)

## Goal

Move from "here is a mathematical model" to "here is my best mathematical conclusion."

## Shipped

### Conclusion engine (`SolverResult` extensions)

- `conclusion` — short answer (e.g. "Likely yes", "Yes — rebalance")
- `confidence_pct` + `confidence_label` — user-visible confidence
- `reasons` — 1–4 bullet main reasons
- `pivot_assumption` — what assumption flips the answer
- `sensitivity_rows` — tabular what-if rows
- `model_note` — "We can model this as…" for broad questions
- `data_would_improve` — what to add when partial

### Answer-first UI order

1. Question  
2. Best conclusion  
3. Confidence  
4. Main reason  
5. Pivot assumption  
6. Model note / missing-data confidence help  
7. Expander: math, calculation, interpretation, assumptions  
8. Interactive controls  
9. Sensitivity table  

### Primary solvers updated

- NBA stat chase — pass confidence from pace vs required rate; games-remaining table
- Baseball trend — R² threshold table; meaningful/noisy/weak conclusions
- Investment rebalance — drift threshold table
- Investment risk-return — volatility cap table
- Baseball player compare — best-effort conclusion when stats missing (Soto vs Judge pattern)

### Success test questions

| Question | Expected feel |
|----------|----------------|
| Brunson stat chase | Answers yes/no with rate reason |
| Soto vs Judge | "Possible but uncertain" + what data helps |
| Trend significance | Yes/no on meaningful trend |
| Should I rebalance? | Yes/no with drift reason |
| Risk-return | Worth it or not with vol pivot |

## Not started (explicit defer)

- Return Insight to Source App
- Draft-decision dedicated solver
- Matchup auto-context without lazy load
