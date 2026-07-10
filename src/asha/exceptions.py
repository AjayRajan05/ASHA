# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""ASHA public exceptions."""


class ASHAError(Exception):
    """Base exception for ASHA errors."""


class ASHAWrapError(ASHAError):
    """Raised when wrap_llm() cannot apply privacy protection."""


class ASHAProcessingError(ASHAError):
    """Raised when prompt processing fails in fail-closed mode."""


class ASHAAnchorBlocked(ASHAError):
    """Raised when ANCHOR blocks an agent action or tool call."""
