"""Runtime configuration resolution for ANCHOR."""

from __future__ import annotations

import os
import sys
from typing import Optional


def resolve_interactive(explicit: Optional[bool] = None) -> bool:
    """
    Decide whether ANCHOR should prompt a human operator for approval.

    Priority: explicit argument > ASHA_ANCHOR_INTERACTIVE env > TTY detection.
    When running in an interactive terminal, human approval prompts are on by default.
    """
    if explicit is not None:
        return explicit
    env = os.getenv("ASHA_ANCHOR_INTERACTIVE")
    if env is not None:
        return env.strip().lower() in ("1", "true", "yes", "on")
    return sys.stdin.isatty()


def resolve_warn_policy(
    explicit: Optional[str] = None,
    *,
    interactive: bool,
) -> str:
    """Resolve warn policy; strict when human approval is active unless overridden."""
    env = os.getenv("ASHA_ANCHOR_WARN_POLICY")
    if env is not None:
        return env
    if explicit is not None:
        return explicit
    return "strict" if interactive else "permissive"
