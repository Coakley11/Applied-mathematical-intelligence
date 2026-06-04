"""Matplotlib visuals for the interactive thinking workshop and lab enhancements."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def _show(fig: plt.Figure) -> None:
    st.pyplot(fig)
    plt.close(fig)


def plot_structure_map(
    structures: list[str],
    matters: list[str],
    noise_level: int,
) -> None:
    """Concept map: core structures vs details that matter."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.add_patch(plt.Rectangle((0.5, 3.2), 9, 2.2, fill=True, facecolor="#e0f2fe", edgecolor="#0284c7", lw=2))
    ax.text(5, 4.6, "Deeper structure", ha="center", fontsize=12, fontweight="bold")
    for i, s in enumerate(structures[:4]):
        ax.text(5, 4.0 - i * 0.45, f"• {s}", ha="center", fontsize=9)

    ax.add_patch(plt.Rectangle((0.5, 0.5), 4.2, 2.2, fill=True, facecolor="#dcfce7", edgecolor="#16a34a", lw=1.5))
    ax.text(2.6, 2.3, "Details that matter", ha="center", fontsize=10, fontweight="bold")
    for i, m in enumerate(matters[:4]):
        ax.text(2.6, 1.7 - i * 0.35, f"• {m}", ha="center", fontsize=8)

    fade = min(1.0, noise_level / 100)
    ax.add_patch(
        plt.Rectangle(
            (5.3, 0.5), 4.2, 2.2,
            fill=True,
            facecolor=(1, 0.9, 0.9, 0.3 + 0.7 * (1 - fade)),
            edgecolor="#dc2626",
            lw=1.5,
            linestyle="--",
        )
    )
    ax.text(7.4, 2.3, f"Noise stripped ({noise_level}%)", ha="center", fontsize=10, fontweight="bold")
    ax.set_title("Abstraction — separate structure from story", fontsize=11)
    _show(fig)


def plot_model_diagram(
    variables: list[str],
    unknowns: list[str],
    output_label: str,
    input_strength: float,
) -> None:
    """Flow: inputs → rule → output."""
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    for i, v in enumerate(variables[:3]):
        ax.add_patch(plt.Rectangle((0.3 + i * 2.2, 1.2), 1.8, 1.2, facecolor="#dbeafe", edgecolor="#2563eb"))
        ax.text(1.2 + i * 2.2, 1.8, v[:18], ha="center", va="center", fontsize=7, wrap=True)

    ax.annotate("", xy=(7.2, 2), xytext=(6.2, 2), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(6.7, 2.35, f"×{input_strength:.1f}", ha="center", fontsize=9)

    ax.add_patch(plt.Rectangle((7.2, 1.0), 2.2, 2.0, facecolor="#fef3c7", edgecolor="#d97706", lw=2))
    ax.text(8.3, 2.0, "Model\nrule", ha="center", va="center", fontsize=9, fontweight="bold")

    ax.annotate("", xy=(9.5, 2), xytext=(9.4, 2), arrowprops=dict(arrowstyle="->", lw=2))
    ax.add_patch(plt.Rectangle((0.3, 0.1), 5.5, 0.7, facecolor="#f3f4f6", edgecolor="#9ca3af"))
    ax.text(3.0, 0.45, f"Unknowns: {', '.join(unknowns[:2])}", ha="center", fontsize=7)
    ax.text(8.3, 3.5, f"Output: {output_label[:24]}", ha="center", fontsize=9, fontweight="bold")
    ax.set_title("Modeling — variables and relationships", fontsize=11)
    _show(fig)


def plot_assumption_tree(
    assumptions: list[str],
    stress_pct: int,
) -> None:
    """Decision tree style: assumptions → outcome sensitivity."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.5, "Your model", ha="center", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#e0e7ff"))

    n = min(len(assumptions), 4)
    xs = np.linspace(1.5, 8.5, n) if n else [5]
    for i, (x, a) in enumerate(zip(xs, assumptions[:4])):
        ax.plot([5, x], [4.0, 2.8], color="#64748b", lw=1)
        color = "#fecaca" if stress_pct > 50 and i == 0 else "#d1fae5"
        ax.add_patch(plt.Rectangle((x - 0.9, 1.8), 1.8, 0.9, facecolor=color, edgecolor="#475569"))
        ax.text(x, 2.25, a[:16], ha="center", fontsize=7)

    impact = stress_pct / 100
    ax.text(5, 0.8, f"If top assumption fails → outcome shifts ~{impact:.0%}", ha="center", fontsize=10,
            color="#b91c1c" if impact > 0.5 else "#15803d")
    ax.set_title("Assumptions — explicit and testable", fontsize=11)
    _show(fig)


def plot_complexity_layers(full_count: int, simple_count: int) -> None:
    """Layers stripped away by simplification."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    labels = ["Full problem", "Useful core", "Decision-ready"]
    counts = [full_count, (full_count + simple_count) // 2, simple_count]
    colors = ["#94a3b8", "#60a5fa", "#22c55e"]
    bars = ax.barh(labels, counts, color=colors)
    ax.set_xlabel("Variables / factors counted")
    ax.set_title("Simplification — fewer levers, same decision")
    for bar, c in zip(bars, counts):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2, str(c), va="center")
    ax.set_xlim(0, max(full_count + 2, 6))
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    _show(fig)


def plot_uncertainty_band(
    low_pct: float,
    mid_pct: float,
    high_pct: float,
    estimate_pct: float,
) -> None:
    """Probability or outcome band with point estimate."""
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axhspan(0.3, 0.7, xmin=(low_pct / 100), xmax=(high_pct / 100), alpha=0.25, color="#059669", label="Plausible range")
    ax.axvline(mid_pct, color="#0ea5e9", lw=2, linestyle="--", label="Best guess")
    ax.axvline(estimate_pct, color="#6366f1", lw=3, label="Your slider")
    ax.axvline(low_pct, color="#94a3b8", lw=1, linestyle=":")
    ax.axvline(high_pct, color="#94a3b8", lw=1, linestyle=":")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Probability or outcome (%)")
    ax.set_yticks([])
    ax.set_title("Uncertainty — ranges beat false precision")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    _show(fig)


def plot_tradeoff_curve(
    objective_weight: float,
    constraint_tight: float,
) -> None:
    """Feasible region vs objective — optimization tradeoff."""
    x = np.linspace(0, 1, 50)
    feasible = x <= (1 - constraint_tight * 0.5)
    obj = objective_weight * x - (1 - objective_weight) * (1 - x) ** 2
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.fill_between(x, 0, obj, where=feasible, alpha=0.3, color="#22c55e", label="Feasible")
    ax.plot(x, obj, color="#2563eb", lw=2, label="Objective value")
    ax.axvline(1 - constraint_tight * 0.5, color="#dc2626", linestyle="--", label="Constraint boundary")
    ax.set_xlabel("Resource allocated to goal A")
    ax.set_ylabel("Objective score")
    ax.set_title("Optimization — objective vs constraint")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    _show(fig)


def plot_probability_tree(
    p_win: float,
    stake: float,
    profit: float,
) -> None:
    """Simple binary outcome tree for betting EV."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.text(5, 5.5, "Bet decision tree", ha="center", fontweight="bold")
    ax.text(5, 4.5, "Place bet", ha="center", bbox=dict(boxstyle="round", facecolor="#e0e7ff"))
    ax.plot([5, 2.5], [4.2, 3.2], "k-")
    ax.plot([5, 7.5], [4.2, 3.2], "k-")
    ax.text(2.5, 2.8, f"Win ({p_win:.0%})\n+${profit:.0f}", ha="center",
            bbox=dict(boxstyle="round", facecolor="#dcfce7"))
    ax.text(7.5, 2.8, f"Lose ({1-p_win:.0%})\n−${stake:.0f}", ha="center",
            bbox=dict(boxstyle="round", facecolor="#fee2e2"))
    ev = p_win * profit - (1 - p_win) * stake
    ax.text(5, 1.2, f"EV = ${ev:+.2f}", ha="center", fontsize=11, color="#1d4ed8" if ev > 0 else "#b91c1c")
    _show(fig)


def plot_ev_bars(p_win: float, profit: float, stake: float) -> None:
    """Compare win vs lose contributions to EV."""
    ev_win = p_win * profit
    ev_lose = -(1 - p_win) * stake
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(["Win contribution", "Lose contribution", "Net EV"], [ev_win, ev_lose, ev_win + ev_lose],
           color=["#22c55e", "#ef4444", "#6366f1"])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("Dollars")
    ax.set_title("Expected value breakdown")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    _show(fig)


def plot_treatment_comparison(
    growth: float,
    treatment: float,
    weeks: int,
) -> None:
    """Tumor growth vs treatment curves."""
    t = np.arange(0, weeks + 1)
    no_tx = np.exp(growth * t / 10)
    with_tx = np.exp((growth - treatment) * t / 10)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(t, no_tx, label="No treatment", color="#ef4444", lw=2)
    ax.plot(t, with_tx, label="With treatment", color="#22c55e", lw=2)
    ax.fill_between(t, with_tx, no_tx, alpha=0.15, color="#22c55e")
    ax.set_xlabel("Week")
    ax.set_ylabel("Relative tumor burden")
    ax.set_title("Treatment comparison — growth vs kill rate")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    _show(fig)


def plot_train_val_gap(train_acc: float, val_acc: float) -> None:
    """Train vs validation — overfitting visual."""
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.bar(["Train", "Validation"], [train_acc, val_acc], color=["#6366f1", "#f59e0b"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Accuracy %")
    gap = train_acc - val_acc
    ax.set_title(f"Train vs validation (gap: {gap:.0f} pts)")
    if gap > 15:
        ax.text(0.5, 0.95, "Overfitting risk", transform=ax.transAxes, ha="center", color="#b91c1c")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    _show(fig)
