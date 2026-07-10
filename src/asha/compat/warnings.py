# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Centralized deprecation warnings for legacy ASHA APIs."""

from __future__ import annotations

import warnings


def warn_deprecated(name: str, *, replacement: str, removed_in: str = "v1.0") -> None:
    warnings.warn(
        f"{name} is deprecated and will be removed in {removed_in}; use {replacement} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def warn_legacy_import(old_path: str, new_path: str) -> None:
    warnings.warn(
        f"{old_path} is deprecated and will be removed in v1.0; use {new_path} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def warn_pipeline() -> None:
    warnings.warn(
        "Pipeline was removed in v0.4.1; use process() instead.",
        DeprecationWarning,
        stacklevel=2,
    )


def warn_legacy_dict() -> None:
    warnings.warn(
        "legacy_dict helpers are deprecated; use ProcessResult fields or "
        "asha.compat.legacy_results.to_legacy_pipeline_dict explicitly.",
        DeprecationWarning,
        stacklevel=2,
    )
