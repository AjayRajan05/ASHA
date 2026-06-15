# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Execution profiles — hide internal pipeline stage mechanics."""

from __future__ import annotations

from enum import Enum
from typing import Tuple


class ExecutionProfile(Enum):
    """Which processing stages run inside the prompt runtime."""

    STANDARD = "standard"
    SECURITY_ONLY = "security_only"
    OPTIMIZE_ONLY = "optimize_only"
    PASSTHROUGH = "passthrough"


def profile_to_stages(profile: ExecutionProfile) -> Tuple[bool, bool, bool]:
    """Map profile to (security, compile, optimize) stage flags."""
    if profile == ExecutionProfile.STANDARD:
        return True, True, True
    if profile == ExecutionProfile.SECURITY_ONLY:
        return True, False, False
    if profile == ExecutionProfile.OPTIMIZE_ONLY:
        return False, False, True
    return False, False, False


def profile_from_mode(mode: str) -> ExecutionProfile:
    if mode.lower() == "off":
        return ExecutionProfile.PASSTHROUGH
    return ExecutionProfile.STANDARD
