"""AI Training Lab — gradient descent and loss curves."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def run_ai_training_lab() -> None:
    st.markdown("#### Training controls")

    col1, col2 = st.columns(2)
    with col1:
        lr = st.slider("Learning rate", 0.001, 0.5, 0.08, step=0.001, key="ai_lr")
        steps = st.slider("Training steps", 10, 200, 60, key="ai_steps")
        noise = st.slider("Data noise", 0.0, 1.0, 0.3, step=0.05, key="ai_noise")
    with col2:
        start_x = st.slider("Start position x", -2.0, 2.0, 1.6, key="ai_x0")
        start_y = st.slider("Start position y", -2.0, 2.0, -1.0, key="ai_y0")
        show_path = st.checkbox("Show gradient path on surface", value=True, key="ai_path")

    xs = np.linspace(-2, 2, 80)
    ys = np.linspace(-2, 2, 80)
    X, Y = np.meshgrid(xs, ys)
    Z = (0.5 * X ** 2 + Y ** 2 + noise * np.sin(3 * X) * np.cos(2 * Y))

    x, y = start_x, start_y
    path_x, path_y, losses = [x], [y], []
    for _ in range(steps):
        z = 0.5 * x ** 2 + y ** 2 + noise * np.sin(3 * x) * np.cos(2 * y)
        losses.append(z)
        gx = x + noise * 3 * np.cos(3 * x) * np.cos(2 * y)
        gy = 2 * y - noise * 2 * np.sin(3 * x) * np.sin(2 * y)
        x -= lr * gx
        y -= lr * gy
        path_x.append(x)
        path_y.append(y)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    cf = axes[0].contourf(X, Y, Z, levels=30, cmap="viridis", alpha=0.9)
    if show_path:
        axes[0].plot(path_x, path_y, "r-o", markersize=3, linewidth=1.5, label="GD path")
        axes[0].scatter([path_x[0]], [path_y[0]], c="white", edgecolors="black", s=50, zorder=5)
        axes[0].scatter([path_x[-1]], [path_y[-1]], c="yellow", edgecolors="black", s=50, zorder=5)
    axes[0].set_title("Loss landscape (2D slice)")
    axes[0].set_xlabel("Parameter θ₁")
    axes[0].set_ylabel("Parameter θ₂")
    if show_path:
        axes[0].legend(loc="upper right")
    plt.colorbar(cf, ax=axes[0], fraction=0.046)

    axes[1].plot(range(len(losses)), losses, color="#6366f1", linewidth=2)
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Loss")
    axes[1].set_title("Loss decreasing over training")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    final_loss = losses[-1] if losses else 0
    converged = len(losses) > 5 and losses[-1] < losses[0] * 0.5

    m1, m2, m3 = st.columns(3)
    m1.metric("Starting loss", f"{losses[0]:.3f}" if losses else "—")
    m2.metric("Final loss", f"{final_loss:.3f}")
    m3.metric("Steps taken", steps)

    if lr > 0.25:
        st.error(
            "Learning rate is very high — the optimizer may overshoot and diverge. "
            "Try 0.01–0.1 for stable descent."
        )
    elif not converged and lr < 0.01:
        st.warning(
            "Learning rate is low — loss decreases slowly. "
            "Increase steps or raise learning rate slightly."
        )
    elif converged:
        st.success(
            f"Training converged — loss dropped from {losses[0]:.2f} to {final_loss:.2f}. "
            "This is exactly what happens inside neural networks: calculus (gradients) "
            "guides parameters toward lower error."
        )
    else:
        st.info(
            "Partial progress — try more steps or tune learning rate. "
            "Real AI training uses adaptive optimizers (Adam) and learning-rate schedules."
        )

    st.markdown("##### How this connects to ChatGPT and vision models")
    st.caption(
        "Large models have millions of parameters instead of two, but the principle is identical: "
        "compute loss, take gradient steps, repeat. **Backpropagation** is the chain rule from calculus."
    )
