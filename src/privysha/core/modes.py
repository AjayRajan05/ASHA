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
Processing modes for PrivySHA.

Defines different processing modes for security and optimization.
"""

from enum import Enum
from typing import Dict, Any


class ProcessingMode(Enum):
    """Processing modes for PrivySHA."""

    OFF = "off"
    LITE = "lite"
    BALANCED = "balanced"
    STRICT = "strict"
    AUTO = "auto"

    @classmethod
    def get_default(cls) -> "ProcessingMode":
        """Get default processing mode."""
        return cls.BALANCED

    def get_security_level(self) -> str:
        """Get security level for this mode."""
        mapping = {
            ProcessingMode.OFF: "low",
            ProcessingMode.LITE: "low",
            ProcessingMode.BALANCED: "medium",
            ProcessingMode.STRICT: "high",
            ProcessingMode.AUTO: "medium",
        }
        return mapping.get(self, "medium")

    def get_optimization_level(self) -> str:
        """Get optimization level for this mode."""
        mapping = {
            ProcessingMode.OFF: "none",
            ProcessingMode.LITE: "light",
            ProcessingMode.BALANCED: "standard",
            ProcessingMode.STRICT: "aggressive",
            ProcessingMode.AUTO: "standard",
        }
        return mapping.get(self, "standard")


def get_mode_config(mode: ProcessingMode) -> Dict[str, Any]:
    """Get configuration for a processing mode."""
    configs = {
        ProcessingMode.OFF: {
            "privacy": False,
            "security_level": "low",
            "optimization_level": "none",
            "token_budget": 999999,
        },
        ProcessingMode.LITE: {
            "privacy": False,
            "security_level": "low",
            "optimization_level": "light",
            "token_budget": 2000,
        },
        ProcessingMode.BALANCED: {
            "privacy": True,
            "security_level": "medium",
            "optimization_level": "standard",
            "token_budget": 1200,
        },
        ProcessingMode.STRICT: {
            "privacy": True,
            "security_level": "high",
            "optimization_level": "aggressive",
            "token_budget": 800,
        },
        ProcessingMode.AUTO: {
            "privacy": True,
            "security_level": "medium",
            "optimization_level": "standard",
            "token_budget": 1200,
        },
    }

    return configs.get(mode, configs[ProcessingMode.BALANCED])


def validate_mode(mode: str) -> ProcessingMode:
    """Validate and convert string to ProcessingMode."""
    try:
        return ProcessingMode(mode.lower())
    except ValueError:
        return ProcessingMode.BALANCED
