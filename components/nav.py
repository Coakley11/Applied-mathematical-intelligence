"""Shared navigation helpers — clickable home cards and session routing."""

import html

import streamlit as st

from content.practical_labs import (
    PRIMARY_ACTION_ICONS,
    PRIMARY_ACTION_TAGLINES,
    PRIMARY_ACTIONS,
)


def navigate_to(action: str) -> None:
    """Set sidebar navigation target and rerun."""
    st.session_state.view_mode = action
    st.rerun()


def render_action_button(action: str, key: str) -> None:
    """Compact action card — icon, title, one short line."""
    icon = PRIMARY_ACTION_ICONS[action]
    tagline = PRIMARY_ACTION_TAGLINES[action]
    is_flagship = action == "Solve a Problem"
    card_class = "ami-action-card ami-action-card-compact"
    if is_flagship:
        card_class += " ami-action-card-flagship"

    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="ami-action-icon">{html.escape(icon)}</div>
            <h3>{html.escape(action)}</h3>
            <p>{html.escape(tagline)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    label = "Open consultant →" if is_flagship else "Start →"
    if st.button(label, key=key, use_container_width=True, type="primary" if is_flagship else "secondary"):
        navigate_to(action)


def render_action_grid() -> None:
    """Flagship first, then 3+3 grid for remaining labs."""
    flagship = PRIMARY_ACTIONS[0]
    rest = PRIMARY_ACTIONS[1:]
    render_action_button(flagship, key="nav_flagship")

    st.markdown("")
    rows = [rest[:3], rest[3:]]
    for row_idx, row in enumerate(rows):
        cols = st.columns(len(row))
        for col_idx, action in enumerate(row):
            with cols[col_idx]:
                render_action_button(action, key=f"nav_card_{row_idx}_{col_idx}")
