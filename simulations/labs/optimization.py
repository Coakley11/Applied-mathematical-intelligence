"""Optimization Lab — resource allocation under constraints."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def run_optimization_lab() -> None:
    from simulations.thinking_plots import plot_tradeoff_curve

    st.markdown("#### Objective vs constraint")
    obj_w = st.slider("Objective weight (explore)", 0.0, 1.0, 0.6, key="opt_trade_obj")
    tight = st.slider("Constraint tightness (explore)", 0.0, 1.0, 0.45, key="opt_trade_tight")
    plot_tradeoff_curve(obj_w, tight)

    st.markdown("---")
    st.markdown("#### Define your options")

    st.caption("Allocate a budget across projects. Each has a return and a risk score.")

    budget = st.slider("Total budget ($)", 1000, 50_000, 10_000, step=500, key="opt_budget")
    max_risk = st.slider("Maximum average risk allowed", 1.0, 10.0, 5.0, step=0.5, key="opt_risk")

    projects = [
        {"name": "Project A — Stable", "return": 0.06, "risk": 2.0, "min": 0, "max": 1.0},
        {"name": "Project B — Growth", "return": 0.10, "risk": 5.0, "min": 0, "max": 1.0},
        {"name": "Project C — Aggressive", "return": 0.14, "risk": 8.0, "min": 0, "max": 1.0},
    ]

    st.markdown("##### Manual allocation")
    weights = []
    cols = st.columns(3)
    for i, (proj, col) in enumerate(zip(projects, cols)):
        with col:
            w = st.slider(
                proj["name"],
                0, 100, 33 if i < 2 else 34,
                key=f"opt_w{i}",
            ) / 100
            weights.append(w)

    total_w = sum(weights)
    if total_w > 0:
        weights = [w / total_w for w in weights]
    else:
        weights = [1 / 3, 1 / 3, 1 / 3]

    port_return = sum(w * p["return"] for w, p in zip(weights, projects))
    port_risk = sum(w * p["risk"] for w, p in zip(weights, projects))
    expected_profit = budget * port_return

    st.markdown("---")
    st.markdown("#### Your allocation results")

    m1, m2, m3 = st.columns(3)
    m1.metric("Expected return", f"{port_return:.1%}")
    m2.metric("Average risk score", f"{port_risk:.1f}")
    m3.metric("Expected profit", f"${expected_profit:,.0f}")

    if port_risk <= max_risk:
        st.success(f"Risk constraint satisfied ({port_risk:.1f} ≤ {max_risk:.1f}).")
    else:
        st.error(f"Risk constraint violated ({port_risk:.1f} > {max_risk:.1f}). Reallocate toward Project A.")

    for w, p in zip(weights, projects):
        st.progress(w, text=f"{p['name']}: {w:.0%} (${budget * w:,.0f})")

    st.markdown("---")
    st.markdown("#### Optimal allocation (grid search)")

    best_return = -1.0
    best_weights = weights
    grid = np.linspace(0, 1, 21)
    feasible = []

    for w_a in grid:
        for w_b in grid:
            w_c = 1 - w_a - w_b
            if w_c < -0.001:
                continue
            w_c = max(0, w_c)
            total = w_a + w_b + w_c
            if total <= 0:
                continue
            wa, wb, wc = w_a / total, w_b / total, w_c / total
            ret = wa * projects[0]["return"] + wb * projects[1]["return"] + wc * projects[2]["return"]
            risk = wa * projects[0]["risk"] + wb * projects[1]["risk"] + wc * projects[2]["risk"]
            if risk <= max_risk:
                feasible.append((ret, risk, wa, wb, wc))
                if ret > best_return:
                    best_return = ret
                    best_weights = [wa, wb, wc]

    if feasible:
        st.success(
            f"**Optimal mix:** A {best_weights[0]:.0%} · B {best_weights[1]:.0%} · C {best_weights[2]:.0%} "
            f"→ return **{best_return:.1%}** within risk cap."
        )
    else:
        st.warning("No feasible allocation meets the risk constraint. Relax max risk or drop Project C.")

    rets, risks = zip(*[(r, k) for r, k, _, _, _ in feasible]) if feasible else ([], [])
    if feasible:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(risks, np.array(rets) * 100, alpha=0.4, s=30, color="#0ea5e9", label="Feasible")
        ax.scatter([port_risk], [port_return * 100], s=120, c="#ef4444", zorder=5, label="Your allocation")
        if feasible:
            ax.scatter(
                [sum(bw * p["risk"] for bw, p in zip(best_weights, projects))],
                [best_return * 100],
                s=120,
                c="#059669",
                marker="*",
                zorder=5,
                label="Optimal",
            )
        ax.set_xlabel("Average risk")
        ax.set_ylabel("Expected return (%)")
        ax.set_title("Feasible allocations under risk constraint")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

    st.caption(
        "Real optimizers (LP, QP, gradient methods) solve this at scale for supply chains, "
        "portfolios, and ML hyperparameter tuning."
    )
