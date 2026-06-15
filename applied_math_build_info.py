"""Deployed build identity for the Applied Math solver stack."""

from __future__ import annotations

import subprocess
from pathlib import Path

# Bump on each solver release; shown when git is unavailable.
GIT_COMMIT_PINNED = "ac897d9"
GIT_BRANCH_PINNED = "dev"
SOLVER_BUILD_MARKER = "2026-05-27-ami-reasoning-v2"
SOLVER_UI_VERSION = "2.8.0"
ROUTER_VERSION = "1.5.0"
SOLVER_CORE_VERSION = "2.7.0"


def _git_short_commit() -> str:
    try:
        root = Path(__file__).resolve().parent
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except Exception:
        pass
    return ""


def _git_branch() -> str:
    try:
        root = Path(__file__).resolve().parent
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except Exception:
        pass
    return GIT_BRANCH_PINNED


GIT_COMMIT = _git_short_commit() or GIT_COMMIT_PINNED
GIT_BRANCH = _git_branch()


def build_info_lines() -> list[str]:
    return [
        f"commit: `{GIT_COMMIT}`",
        f"branch: `{GIT_BRANCH}`",
        f"build marker: `{SOLVER_BUILD_MARKER}`",
        f"solver UI: `{SOLVER_UI_VERSION}`",
        f"router: `{ROUTER_VERSION}`",
        f"solver core: `{SOLVER_CORE_VERSION}`",
    ]


def build_info_caption() -> str:
    return " · ".join(
        [
            f"Applied Math Solver Build {SOLVER_BUILD_MARKER}",
            GIT_COMMIT,
            GIT_BRANCH,
            f"UI {SOLVER_UI_VERSION}",
        ]
    )
