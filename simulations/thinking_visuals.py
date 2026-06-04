"""Matplotlib visuals for the interactive thinking workshop."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def _show(fig) -> None:
    st.pyplot(fig)
    plt.close(fig)


def render_concept_map(center: str, nodes: list[str], title: str = "Concept map") -> None:
    """Radial concept map — center idea linked to structural concepts."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.text(0, 0, center, ha="center", va="center", fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#e0e7ff", edgecolor="#6366f1"))
    n = len(nodes)
    for i, label in enumerate(nodes):
        angle = 2 * np.pi * i / n - np.pi / 2
        x, y = 1.1 * np.cos(angle), 1.1 * np.sin(angle)
        ax.plot([0, x * 0.85], [0, y * 0.85], color="#94a3b8", linewidth=1.5, zorder=1)
        ax.text(
            x, y, label, ha="center", va="center", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#f1f5f9", edgecolor="#cbd5e1"),
        )
    _show(fig)


def render_probability_tree(p_win: float, payout: float, stake: float = 100.0) -> None:
    """Simple bet outcome tree with EV annotation."""
    lose_p = 1 - p_win
    profit = stake * (payout - 1)
    ev = p_win * profit - lose_p * stake

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(f"Probability tree — EV = ${ev:+.0f} on ${stake:.0f} stake", fontweight="bold")

    ax.text(5, 5.2, "Place bet", ha="center", fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#fef3c7"))
    ax.plot([5, 2.5], [4.8, 3.5], "k-", lw=1.5)
    ax.plot([5, 7.5], [4.8, 3.5], "k-", lw=1.5)
    ax.text(2.5, 3.0, f"Win\n{p_win:.0%}\n+${profit:.0f}", ha="center", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="#d1fae5"))
    ax.text(7.5, 3.0, f"Lose\n{lose_p:.0%}\n−${stake:.0f}", ha="center", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="#fee2e2"))
    ax.text(5, 0.8, f"E[profit] = {p_win:.0%}×{profit:.0f} − {lose_p:.0%}×{stake:.0f} = ${ev:+.0f}",
            ha="center", fontsize=9, style="italic")
    _show(fig)


def render_sensitivity_bars(base_value: float, deltas: list[tuple[str, float]]) -> None:
    """Tornado-style sensitivity — how outcome shifts when inputs move."""
    labels = [d[0] for d in deltas]
    values = [d[1] for d in deltas]
    colors = ["#059669" if v >= 0 else "#dc2626" for v in values]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(labels))))
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, values, color=colors, alpha=0.85)
    ax.axvline(0, color="#64748b", linewidth=1)
    ax.axvline(base_value, color="#6366f1", linestyle="--", linewidth=1.5, label="Base case")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Change in outcome")
    ax.set_title("What changes if… (sensitivity)")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    _show(fig)


def render_tradeoff_curve(x_label: str = "Risk", y_label: str = "Return") -> None:
    """Feasible frontier sketch for optimization mode."""
    risk = np.linspace(1, 10, 50)
    frontier = 0.04 + 0.012 * risk - 0.0004 * risk ** 2
    dominated = 0.03 + 0.008 * risk

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(risk, frontier, color="#059669", linewidth=2.5, label="Efficient frontier")
    ax.scatter(risk[::5], dominated[::5], color="#94a3b8", s=40, alpha=0.7, label="Dominated options")
    ax.fill_between(risk, dominated, frontier, where=(frontier > dominated), alpha=0.15, color="#059669")
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title("Tradeoff: higher return usually needs more risk")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    _show(fig)


def render_model_flow(inputs: list[str], output: str, title: str = "Model diagram") -> None:
    """Inputs → box → output flowchart."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title(title, fontweight="bold")

    for i, inp in enumerate(inputs[:4]):
        y = 3.2 - i * 0.9
        ax.text(1.5, y, inp, ha="center", va="center", fontsize=8,
                bbox=dict(boxstyle="round", facecolor="#e0f2fe"))
        ax.annotate("", xy=(4.2, 2), xytext=(2.8, y),
                    arrowprops=dict(arrowstyle="->", color="#64748b", lw=1))

    ax.text(5.5, 2, "Model\nf(·)", ha="center", va="center", fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ede9fe", edgecolor="#7c3aed", linewidth=2))
    ax.annotate("", xy=(8, 2), xytext=(7, 2), arrowprops=dict(arrowstyle="->", color="#64748b", lw=2))
    ax.text(8.8, 2, output, ha="center", va="center", fontsize=9, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="#d1fae5"))
    _show(fig)


def render_uncertainty_cone(
    slope: float = 2.0,
    intercept: float = 50.0,
    noise: float = 12.0,
    n_hist: int = 40,
    n_fwd: int = 20,
    seed: int = 7,
) -> None:
    """Forecast-style uncertainty cone for uncertainty thinking mode."""
    rng = np.random.default_rng(seed)
    t_hist = np.arange(n_hist)
    y_hist = intercept + slope * t_hist + rng.normal(0, noise, n_hist)
    coeffs = np.polyfit(t_hist, y_hist, 1)
    est_slope, est_intercept = coeffs[0], coeffs[1]

    t_future = np.arange(n_hist, n_hist + n_fwd)
    y_forecast = est_slope * t_future + est_intercept
    se = noise * np.sqrt(1 + (t_future - np.mean(t_hist)) ** 2 / np.sum((t_hist - np.mean(t_hist)) ** 2))
    upper = y_forecast + 1.96 * se
    lower = y_forecast - 1.96 * se

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(t_hist, y_hist, alpha=0.45, s=20, color="#64748b", label="Observed")
    ax.plot(t_hist, est_slope * t_hist + est_intercept, color="#0ea5e9", lw=2, label="Fit")
    ax.plot(t_future, y_forecast, "--", color="#059669", lw=2, label="Forecast")
    ax.fill_between(t_future, lower, upper, alpha=0.25, color="#059669", label="Uncertainty band")
    ax.axvline(n_hist - 0.5, color="#94a3b8", linestyle=":")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title("Uncertainty grows as you look further ahead")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    _show(fig)


def render_learning_curves(train_frac: float = 0.15, val_gap: float = 0.08) -> None:
    """Train vs validation curves for AI / overfitting intuition."""
    epochs = np.arange(1, 51)
    train = 1.0 * np.exp(-train_frac * epochs) + 0.05
    val = 1.0 * np.exp(-train_frac * 0.7 * epochs) + 0.05 + val_gap * (1 - np.exp(-0.08 * epochs))

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(epochs, train, label="Training loss", color="#6366f1", lw=2)
    ax.plot(epochs, val, label="Validation loss", color="#f59e0b", lw=2)
    ax.set_xlabel("Training step")
    ax.set_ylabel("Loss")
    ax.set_title("Train vs validation — watch the gap")
    ax.legend()
    ax.grid(True, alpha=0.3)
    if val[-1] > train[-1] * 1.15:
        ax.axvspan(30, 50, alpha=0.12, color="#ef4444", label="_gap")
        ax.text(38, max(val[35], train[35]), "Possible\noverfitting", fontsize=8, color="#b91c1c")
    _show(fig)


def render_tumor_comparison(growth: float, kill: float, days: int = 60) -> None:
    """Treatment vs no-treatment curves for medicine mode."""
    t = np.linspace(0, days, days + 1)
    v_none = 100 * np.exp(growth * t / 100)
    v_tx = 100 * np.exp((growth - kill) * t / 100)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, v_none, label="No treatment", color="#ef4444", lw=2)
    ax.plot(t, v_tx, label="With treatment", color="#059669", lw=2)
    ax.fill_between(t, v_tx, v_none, where=(v_none > v_tx), alpha=0.15, color="#059669")
    ax.set_xlabel("Days")
    ax.set_ylabel("Relative tumor burden")
    ax.set_title("Growth rate vs treatment kill rate")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _show(fig)
