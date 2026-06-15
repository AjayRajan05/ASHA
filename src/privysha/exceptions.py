# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""PrivySHA public exceptions."""


class PrivySHAError(Exception):
    """Base exception for PrivySHA errors."""


class PrivySHAWrapError(PrivySHAError):
    """Raised when wrap_llm() cannot apply privacy protection."""


class PrivySHAProcessingError(PrivySHAError):
    """Raised when prompt processing fails in fail-closed mode."""
