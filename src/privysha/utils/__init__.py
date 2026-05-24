# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
PrivySHA Utilities

Contains utility functions and helper classes that make PrivySHA
feel like a utility layer rather than a system replacement.
"""

from .dropin import process, wrap_llm, optimize, sanitize, SecureLLMWrapper, quick_setup
from .auto_patch import (
    auto_patch,
    get_patch_status,
    disable_auto_patch,
    enable_auto_patch,
)
from .pii_detector import PIIDetector

__all__ = [
    # Drop-in utilities (CRITICAL FOR ADOPTION)
    "process",
    "wrap_llm",
    "optimize",
    "sanitize",
    "SecureLLMWrapper",
    "quick_setup",
    # Auto-patch utilities
    "auto_patch",
    "get_patch_status",
    "disable_auto_patch",
    "enable_auto_patch",
    # Utility classes
    "PIIDetector",
]
