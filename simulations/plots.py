"""Shared plotting helpers for simulations."""

import matplotlib.pyplot as plt
import streamlit as st


def plot_line(x, y, title, xlabel, ylabel, legend_labels=None):
    fig, ax = plt.subplots()
    if legend_labels and isinstance(y, list):
        for series, label in zip(y, legend_labels):
            ax.plot(x, series, label=label)
        ax.legend()
    else:
        ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    st.pyplot(fig)
    plt.close(fig)
