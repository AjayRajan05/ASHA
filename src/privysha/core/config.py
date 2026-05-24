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
Global configuration and safety controls for PrivySHA.

Provides enterprise-required safety controls and deterministic mode.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PrivySHAConfig:
    """Global PrivySHA configuration."""

    # Global safety kill switch
    enabled: bool = True

    # Deterministic mode for reproducible results
    deterministic_mode: bool = False

    # Default timeout settings
    default_timeout_ms: int = 100

    # Default security level
    default_security_level: str = "medium"

    # Observability settings
    auto_observability: bool = True

    # Auto-patch settings
    auto_patch_providers: list = None

    # Performance settings
    cache_enabled: bool = False
    max_concurrent_requests: int = 10

    # ML and progressive enhancement settings
    enable_ml_models: bool = False
    pii_detection_mode: str = "rule"  # "rule", "hybrid", "ml_only"
    ml_model_download_size_mb: int = 0  # Track download size
    ml_auto_download: bool = False  # Never auto-download by default


# Global configuration instance
_global_config = PrivySHAConfig()


def get_config() -> PrivySHAConfig:
    """Get global PrivySHA configuration."""
    return _global_config


def set_config(config: PrivySHAConfig):
    """Set global PrivySHA configuration."""
    global _global_config
    _global_config = config


def update_from_env():
    """Update configuration from environment variables."""

    # Safety kill switch
    if os.getenv("PRIVYSHA_ENABLED", "").lower() in ["false", "0", "no"]:
        _global_config.enabled = False
    elif os.getenv("PRIVYSHA_ENABLED", "").lower() in ["true", "1", "yes"]:
        _global_config.enabled = True

    # Deterministic mode
    if os.getenv("PRIVYSHA_DETERMINISTIC", "").lower() in ["true", "1", "yes"]:
        _global_config.deterministic_mode = True

    # Auto-observability
    if os.getenv("PRIVYSHA_OBSERVABILITY", "").lower() in ["false", "0", "no"]:
        _global_config.auto_observability = False

    # Default timeout
    timeout_env = os.getenv("PRIVYSHA_TIMEOUT_MS")
    if timeout_env:
        try:
            _global_config.default_timeout_ms = int(timeout_env)
        except ValueError:
            pass

    # Default security level
    security_env = os.getenv("PRIVYSHA_SECURITY_LEVEL")
    if security_env:
        _global_config.default_security_level = security_env.lower()

    # Auto-patch providers
    providers_env = os.getenv("PRIVYSHA_AUTO_PATCH_PROVIDERS")
    if providers_env:
        _global_config.auto_patch_providers = [
            p.strip() for p in providers_env.split(",")
        ]


def is_enabled() -> bool:
    """Check if PrivySHA is globally enabled."""
    return _global_config.enabled


def set_enabled(enabled: bool):
    """Enable or disable PrivySHA globally."""
    _global_config.enabled = enabled


def is_deterministic() -> bool:
    """Check if deterministic mode is enabled."""
    return _global_config.deterministic_mode


def set_deterministic(deterministic: bool):
    """Enable or disable deterministic mode."""
    _global_config.deterministic_mode = deterministic


def get_timeout_ms() -> int:
    """Get default timeout in milliseconds."""
    return _global_config.default_timeout_ms


def set_timeout_ms(timeout_ms: int):
    """Set default timeout in milliseconds."""
    _global_config.default_timeout_ms = timeout_ms


def get_security_level() -> str:
    """Get default security level."""
    return _global_config.default_security_level


def set_security_level(level: str):
    """Set default security level."""
    _global_config.default_security_level = level.lower()


def is_observability_enabled() -> bool:
    """Check if auto-observability is enabled."""
    return _global_config.auto_observability


def set_observability(enabled: bool):
    """Enable or disable auto-observability."""
    _global_config.auto_observability = enabled


def get_config_summary() -> Dict[str, Any]:
    """Get comprehensive configuration summary."""
    return {
        "enabled": _global_config.enabled,
        "deterministic_mode": _global_config.deterministic_mode,
        "timeout_ms": _global_config.default_timeout_ms,
        "security_level": _global_config.default_security_level,
        "auto_observability": _global_config.auto_observability,
        "auto_patch_providers": _global_config.auto_patch_providers,
        "cache_enabled": _global_config.cache_enabled,
        "max_concurrent_requests": _global_config.max_concurrent_requests,
    }


# Initialize configuration from environment variables
update_from_env()
