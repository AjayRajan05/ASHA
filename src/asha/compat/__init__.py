# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Opt-in legacy dict conversion for migration tooling."""

from .legacy_results import (
    process_result_to_legacy_dict,
    timeout_legacy_dict,
    to_legacy_pipeline_dict,
)
from .warnings import warn_legacy_dict, warn_legacy_import

__all__ = [
    "process_result_to_legacy_dict",
    "to_legacy_pipeline_dict",
    "timeout_legacy_dict",
    "warn_legacy_dict",
    "warn_legacy_import",
]
