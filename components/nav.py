"""Shared navigation helpers — clickable home cards and session routing."""

import html

import streamlit as st

from content.practical_labs import (
    PRIMARY_ACTION_DESCRIPTIONS,
    PRIMARY_ACTION_ICONS,
    PRIMARY_ACTION_LABELS,
    PRIMARY_ACTIONS,
)


def navigate_to(action: str) -> None:
    """Set sidebar navigation target and rerun."""
    st.session_state.view_mode = action
    st.rerun()


def render_action_button(action: str, key: str) -> None:
    """Large action card with click-to-navigate button."""
    icon = PRIMARY_ACTION_ICONS[action]
    label = PRIMARY_ACTION_LABELS[action]
    desc = PRIMARY_ACTION_DESCRIPTIONS[action]
    st.markdown(
        f"""
        <div class="ami-action-card">
            <div class="ami-action-icon">{html.escape(icon)}</div>
            <div class="ami-action-label">{html.escape(action)}</div>
            <h3>{html.escape(label)}</h3>
            <p>{html.escape(desc)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Open → {action}", key=key, use_container_width=True):
        navigate_to(action)


def render_action_grid() -> None:
    """3+3+1 grid of primary action cards."""
    rows = [PRIMARY_ACTIONS[:3], PRIMARY_ACTIONS[3:6], PRIMARY_ACTIONS[6:]]
    for row_idx, row in enumerate(rows):
        cols = st.columns(len(row))
        for col_idx, action in enumerate(row):
            with cols[col_idx]:
                render_action_button(action, key=f"nav_card_{row_idx}_{col_idx}")
