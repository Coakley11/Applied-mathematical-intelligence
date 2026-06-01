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
    try:
        from suite_activity_client import record_activity

        record_activity(
            "applied_intelligence",
            "page_view",
            page=action,
            metrics={"lesson": action},
            summary=f"Applied Intelligence: {action}",
            resume_key=f"section:{action}",
            resume_title=f"Continue: {action}",
            local_state={"page": action, "lesson": action},
        )
    except Exception:
        pass
    st.rerun()


def render_action_button(action: str, key: str) -> None:
    """Compact action card — icon, title, one short line."""
    icon = PRIMARY_ACTION_ICONS[action]
    tagline = PRIMARY_ACTION_TAGLINES[action]
    is_flagship = action in ("Solve a Problem", "Explore a Math Idea")
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
    if action == "Solve a Problem":
        label = "Solve a problem →"
    elif action == "Explore a Math Idea":
        label = "Explore a math idea →"
    else:
        label = "Start →"
    btn_type = "primary" if is_flagship else "secondary"
    if st.button(label, key=key, use_container_width=True, type=btn_type):
        navigate_to(action)


def render_action_grid() -> None:
    """Two entry paths, then labs."""
    entry = PRIMARY_ACTIONS[:2]
    rest = PRIMARY_ACTIONS[2:]
    c1, c2 = st.columns(2)
    with c1:
        render_action_button(entry[0], key="nav_flagship_solve")
    with c2:
        render_action_button(entry[1], key="nav_flagship_explore")

    st.markdown("")
    rows = [rest[:3], rest[3:]]
    for row_idx, row in enumerate(rows):
        cols = st.columns(len(row))
        for col_idx, action in enumerate(row):
            with cols[col_idx]:
                render_action_button(action, key=f"nav_card_{row_idx}_{col_idx}")
