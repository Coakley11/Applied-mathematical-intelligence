"""Draft context diagnostics — send/hydration vs solver bundle consumption."""

from __future__ import annotations

from typing import Any


def _rows(val: Any) -> list[Any]:
    return val if isinstance(val, list) else []


def _position_counts(rows: list[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        pos = str(row.get("Primary Position") or row.get("position") or row.get("pos") or "?").upper()
        out[pos] = out.get(pos, 0) + 1
    return out


def _catcher_count(rows: list[Any]) -> int:
    return sum(1 for row in rows if isinstance(row, dict) and str(row.get("Primary Position", "")).upper() == "C")


def _player_names(rows: list[Any], limit: int = 4) -> list[str]:
    names: list[str] = []
    for row in rows[:limit]:
        if isinstance(row, dict):
            name = str(row.get("player") or row.get("Player") or row.get("fullName") or "").strip()
            if name:
                names.append(name)
        elif row:
            names.append(str(row).strip())
    return names


def build_draft_context_diagnostics(ctx: dict[str, Any], *, hydrate_source: str = "") -> dict[str, Any]:
    """Summarize available pool at hydration time (before solver bundle)."""
    snap = ctx.get("draft_snapshot") if isinstance(ctx.get("draft_snapshot"), dict) else {}
    proj = ctx.get("draft_projection") if isinstance(ctx.get("draft_projection"), dict) else {}
    pool_diag = ctx.get("player_pool_diagnostics") if isinstance(ctx.get("player_pool_diagnostics"), dict) else {}

    top_avail = _rows(ctx.get("available_players"))
    snap_avail = _rows(snap.get("available_players"))
    proj_avail = _rows(proj.get("available_players"))
    best = _rows(ctx.get("best_available") or snap.get("best_available_players") or proj.get("best_available"))

    hydrated_count = max(len(top_avail), len(snap_avail), len(proj_avail))
    hydrated_rows = top_avail or snap_avail or proj_avail

    return {
        "hydrate_source": hydrate_source or "unknown",
        "draft_context_source": hydrate_source or "unknown",
        "available_players_count_hydrated": hydrated_count,
        "available_players_top_level_count": len(top_avail),
        "draft_snapshot_available_players_count": len(snap_avail),
        "draft_projection_available_players_count": len(proj_avail),
        "best_available_count": len(best),
        "catchers_in_hydrated_available": _catcher_count(hydrated_rows),
        "hydrated_position_counts": _position_counts(hydrated_rows),
        "sample_hydrated_players": _player_names(hydrated_rows),
        "player_pool_source": pool_diag.get("player_pool_source"),
        "player_pool_cap": pool_diag.get("player_pool_cap"),
        "needed_positions": ctx.get("needed_positions") or snap.get("needed_positions") or proj.get("needed_positions"),
        "requested_position": pool_diag.get("requested_position"),
        "question_player_row_present": bool(ctx.get("question_player_row")),
        "question_player": ctx.get("question_player") or ctx.get("player"),
        "current_pick": ctx.get("current_pick") or snap.get("current_pick") or proj.get("current_pick"),
        "draft_round": ctx.get("draft_round") or snap.get("draft_round") or proj.get("draft_round"),
        "draft_snapshot_present": bool(snap),
    }


def build_solver_bundle_diagnostics(ctx: dict[str, Any]) -> dict[str, Any]:
    """Summarize what the draft solver actually reads via _draft_context_bundle."""
    try:
        from components.applied_math_solvers import _draft_context_bundle, _draft_question_mode, _resolve_focus_player

        bundle = _draft_context_bundle(ctx)
        avail = _rows(bundle.get("available"))
        names = _player_names(avail, limit=6)
        return {
            "bundle_available_count": len(avail),
            "bundle_catcher_count": _catcher_count(avail),
            "bundle_first_available_names": names,
            "bundle_sample_players": names,
            "bundle_position_counts": _position_counts(avail),
            "bundle_best_available_count": len(_rows(bundle.get("best_available"))),
            "bundle_recommended_count": len(_rows(bundle.get("recommendations"))),
            "bundle_pick": bundle.get("pick"),
            "bundle_round": bundle.get("round"),
            "draft_mode": _draft_question_mode(str(ctx.get("_debug_question") or "")),
            "focus_player": _resolve_focus_player(str(ctx.get("_debug_question") or ""), ctx, bundle),
        }
    except Exception as exc:
        return {"bundle_diagnostics_error": str(exc)}


def render_draft_context_diagnostics_block(st: Any, diag: dict[str, Any], *, title: str = "Draft pool diagnostics") -> None:
    if not diag:
        return
    st.markdown(f"**{title}**")
    for key, val in diag.items():
        if val is None or val == "" or val == {} or val == []:
            continue
        st.text(f"{key}: {val}")
