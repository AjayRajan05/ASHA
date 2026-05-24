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
ML utilities for progressive enhancement architecture.

Handles ML dependency checking, lazy loading, and graceful fallbacks.
"""

import warnings
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class MLDependencyStatus:
    """Status of ML dependencies."""

    spacy_available: bool = False
    transformers_available: bool = False
    torch_available: bool = False
    accelerate_available: bool = False
    all_available: bool = False
    missing_packages: list = None

    def __post_init__(self):
        if self.missing_packages is None:
            self.missing_packages = []


def check_ml_dependencies() -> MLDependencyStatus:
    """Check availability of ML dependencies with auto-detection."""
    status = MLDependencyStatus()

    # Check spaCy
    try:
        import spacy  # noqa: F401

        status.spacy_available = True
    except ImportError:
        status.missing_packages.append("spacy")

    # Check transformers
    try:
        import transformers  # noqa: F401

        status.transformers_available = True
    except ImportError:
        status.missing_packages.append("transformers")

    # Check torch
    try:
        import torch  # noqa: F401

        status.torch_available = True
    except ImportError:
        status.missing_packages.append("torch")

    # Check accelerate
    try:
        import accelerate  # noqa: F401

        status.accelerate_available = True
    except ImportError:
        status.missing_packages.append("accelerate")

    # Set overall availability
    status.all_available = all(
        [
            status.spacy_available,
            status.transformers_available,
            status.torch_available,
            status.accelerate_available,
        ]
    )

    return status


def get_ml_installation_instructions() -> str:
    """Get installation instructions for missing ML dependencies."""
    return (
        "ML features require additional dependencies. "
        "Install with: pip install privysha[ml]"
    )


def validate_pii_mode(pii_mode: str) -> str:
    """Validate and normalize PII detection mode."""
    valid_modes = ["rule", "hybrid", "ml_only"]
    if pii_mode not in valid_modes:
        raise ValueError(
            f"Invalid pii_mode '{pii_mode}'. Valid options: {valid_modes}")
    return pii_mode


def check_pii_mode_feasibility(pii_mode: str) -> Dict[str, Any]:
    """Check if PII mode is feasible with current dependencies."""
    ml_status = check_ml_dependencies()

    if pii_mode == "rule":
        return {"feasible": True, "requires_ml": False, "status": "available"}

    elif pii_mode in ["hybrid", "ml_only"]:
        if not ml_status.all_available:
            return {
                "feasible": False,
                "requires_ml": True,
                "status": "missing_dependencies",
                "missing_packages": ml_status.missing_packages,
                "installation_instructions": get_ml_installation_instructions(),
            }
        else:
            return {"feasible": True, "requires_ml": True, "status": "available"}

    return {"feasible": False, "requires_ml": False, "status": "invalid_mode"}


class MLLoader:
    """Lazy ML model loader with proper error handling."""

    def __init__(self, pii_mode: str = "rule"):
        self.pii_mode = validate_pii_mode(pii_mode)
        self.ml_status = check_ml_dependencies()
        self._ml_models_loaded = False
        self._load_attempted = False

    def is_ml_required(self) -> bool:
        """Check if ML models are required for current mode."""
        return self.pii_mode in ["hybrid", "ml_only"]

    def is_ml_available(self) -> bool:
        """Check if ML dependencies are available."""
        return self.ml_status.all_available

    def can_use_ml(self) -> bool:
        """Check if ML can be used (required + available)."""
        return self.is_ml_required() and self.is_ml_available()

    def ensure_ml_loaded(self, force_reload: bool = False) -> bool:
        """
        Ensure ML models are loaded if needed.

        Returns:
            True if ML models are loaded and ready, False otherwise.
        """
        if not self.is_ml_required():
            return True  # ML not required for this mode

        if not self.is_ml_available():
            return False  # ML dependencies not available

        if self._ml_models_loaded and not force_reload:
            return True  # Already loaded

        if self._load_attempted and not force_reload:
            return False  # Already failed to load

        try:
            self._load_ml_models()
            self._ml_models_loaded = True
            self._load_attempted = True
            return True
        except Exception as e:
            self._load_attempted = True
            warnings.warn(f"Failed to load ML models: {e}")
            return False

    def _load_ml_models(self):
        """Load ML models - to be implemented by specific classes."""
        # This will be overridden by specific implementations

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of ML loader status."""
        return {
            "pii_mode": self.pii_mode,
            "ml_required": self.is_ml_required(),
            "ml_available": self.is_ml_available(),
            "ml_loaded": self._ml_models_loaded,
            "load_attempted": self._load_attempted,
            "can_use_ml": self.can_use_ml(),
            "missing_packages": (
                self.ml_status.missing_packages
                if not self.ml_status.all_available
                else []
            ),
        }
