"""AI / ML simulations — loss landscape and training dynamics."""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from simulations.plots import plot_line


def ai_ml_suite():
    tab1, tab2 = st.tabs(["Gradient descent landscape", "Neural training dynamics"])

    with tab1:
        _gradient_landscape()
    with tab2:
        _neural_training()


def _gradient_landscape():
    st.markdown("**2D loss surface** — visualize how gradient descent navigates curvature.")
    lr = st.slider("Learning rate", 0.001, 0.3, 0.08, key="gl_lr")
    steps = st.slider("Steps", 10, 120, 50, key="gl_steps")
    x0 = st.slider("Start x", -2.0, 2.0, 1.5, key="gl_x0")
    y0 = st.slider("Start y", -2.0, 2.0, -1.2, key="gl_y0")

    xs = np.linspace(-2, 2, 80)
    ys = np.linspace(-2, 2, 80)
    X, Y = np.meshgrid(xs, ys)
    Z = 0.4 * X ** 2 + Y ** 2 + 0.3 * np.sin(3 * X) * np.cos(2 * Y)

    x, y = x0, y0
    path_x, path_y = [x], [y]
    for _ in range(steps):
        gx = 0.8 * x + 0.9 * np.cos(3 * x) * np.cos(2 * y)
        gy = 2 * y - 0.6 * np.sin(3 * x) * np.sin(2 * y)
        x -= lr * gx
        y -= lr * gy
        path_x.append(x)
        path_y.append(y)

    fig, ax = plt.subplots()
    ax.contourf(X, Y, Z, levels=30, cmap="viridis", alpha=0.85)
    ax.plot(path_x, path_y, "r-o", markersize=3, linewidth=1.5, label="GD path")
    ax.scatter([path_x[0]], [path_y[0]], c="white", edgecolors="black", s=60, label="Start")
    ax.scatter([path_x[-1]], [path_y[-1]], c="yellow", edgecolors="black", s=60, label="End")
    ax.legend()
    ax.set_title("Gradient Descent on a Non-Convex Surface")
    st.pyplot(fig)
    plt.close(fig)


def _neural_training():
    st.markdown("**Toy neural network** — ReLU hidden layer learning XOR-like boundary.")
    epochs = st.slider("Training epochs", 20, 500, 200, key="nn_ep")
    lr = st.slider("Learning rate", 0.01, 1.0, 0.35, key="nn_lr")
    hidden = st.slider("Hidden units", 2, 16, 8, key="nn_h")

    rng = np.random.default_rng(7)
    X = rng.uniform(-1, 1, (120, 2))
    y = ((X[:, 0] * X[:, 1]) > 0).astype(float).reshape(-1, 1)

    W1 = rng.normal(0, 0.5, (2, hidden))
    b1 = np.zeros((1, hidden))
    W2 = rng.normal(0, 0.5, (hidden, 1))
    b2 = np.zeros((1, 1))

    train_loss = []
    val_loss = []
    split = 90

    for ep in range(epochs):
        h = np.maximum(0, X @ W1 + b1)
        pred = 1 / (1 + np.exp(-(h @ W2 + b2)))
        loss = -np.mean(y * np.log(pred + 1e-8) + (1 - y) * np.log(1 - pred + 1e-8))
        train_loss.append(loss)
        if ep % 5 == 0:
            hv = np.maximum(0, X[split:] @ W1 + b1)
            pv = 1 / (1 + np.exp(-(hv @ W2 + b2)))
            vl = -np.mean(
                y[split:] * np.log(pv + 1e-8) + (1 - y[split:]) * np.log(1 - pv + 1e-8)
            )
            val_loss.append((ep, vl))

        err = pred - y
        dW2 = h.T @ err / len(X)
        db2 = np.mean(err, axis=0, keepdims=True)
        dh = err @ W2.T
        dh[h <= 0] = 0
        dW1 = X.T @ dh / len(X)
        db1 = np.mean(dh, axis=0, keepdims=True)
        W2 -= lr * dW2
        b2 -= lr * db2
        W1 -= lr * dW1
        b1 -= lr * db1

    plot_line(range(len(train_loss)), train_loss, "Cross-Entropy Loss (training)", "Epoch", "Loss")
    if val_loss:
        ve, vl = zip(*val_loss)
        st.line_chart({"validation_loss": vl}, x=ve)

    h = np.maximum(0, X @ W1 + b1)
    pred = 1 / (1 + np.exp(-(h @ W2 + b2)))
    acc = np.mean((pred > 0.5) == y)
    st.metric("Training accuracy", f"{acc:.1%}")
    st.caption("Illustrates forward pass, backpropagation (chain rule), and generalization gap monitoring.")
