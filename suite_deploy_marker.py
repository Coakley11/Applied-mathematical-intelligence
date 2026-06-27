"""Deploy marker for Applied Mathematical Intelligence — commit at runtime."""

from __future__ import annotations

import os
import subprocess
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_DEPLOY_COMMIT_FILE = _ROOT / "deploy_commit.txt"

_ENV_COMMIT_KEYS = (
    "STREAMLIT_CLOUD_COMMIT",
    "SOURCE_VERSION",
    "COMMIT_SHA",
    "GIT_COMMIT",
    "GITHUB_SHA",
)

_ENV_BRANCH_KEYS = (
    "STREAMLIT_CLOUD_BRANCH",
    "GITHUB_REF_NAME",
    "GIT_BRANCH",
)


@lru_cache(maxsize=1)
def resolve_git_commit_short() -> str:
    for key in _ENV_COMMIT_KEYS:
        val = os.environ.get(key, "").strip()
        if val:
            return val[:7] if len(val) > 7 else val
    if _DEPLOY_COMMIT_FILE.is_file():
        for line in _DEPLOY_COMMIT_FILE.read_text(encoding="utf-8").splitlines():
            token = line.strip().split("#", 1)[0].strip()
            if token and token.lower() != "unknown":
                return token[:7] if len(token) > 7 else token
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        ).strip()
    except Exception:
        pass
    return "unknown"


@lru_cache(maxsize=1)
def resolve_git_branch() -> str:
    for key in _ENV_BRANCH_KEYS:
        val = os.environ.get(key, "").strip()
        if val:
            return val.replace("refs/heads/", "")
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        ).strip()
    except Exception:
        pass
    return "dev"


def format_build_label() -> str:
    return f"ami-dev-{resolve_git_commit_short()}"


GIT_COMMIT_SHORT = resolve_git_commit_short()
GIT_BRANCH = resolve_git_branch()
