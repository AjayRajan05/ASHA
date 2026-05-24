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

"""Policy gate helpers for deterministic pipeline passthrough behavior."""

from typing import Any, Dict


def should_passthrough(config: Dict[str, Any]) -> bool:
    """
    Return True when the pipeline should skip all processing.

    Passthrough when mode is OFF or when PII, injection detection, and
    optimization are all disabled.
    """
    mode = config.get("mode", "")
    if isinstance(mode, str) and mode.lower() == "off":
        return True

    enable_pii = config.get("enable_pii_detection", True)
    enable_injection = config.get("enable_injection_detection", True)
    enable_optimization = config.get("enable_optimization", True)

    if not enable_pii and not enable_injection and not enable_optimization:
        return True

    return False


def security_disabled(config: Dict[str, Any]) -> bool:
    """Return True when security processing should be skipped."""
    enable_pii = config.get("enable_pii_detection", True)
    enable_injection = config.get("enable_injection_detection", True)
    pii_masking = config.get("pii_masking", config.get("privacy", True))
    if not pii_masking:
        enable_pii = False
    return not enable_pii and not enable_injection


def optimization_disabled(config: Dict[str, Any]) -> bool:
    """Return True when optimization should be skipped."""
    return not config.get("enable_optimization", True)


def modification_disabled(config: Dict[str, Any]) -> bool:
    """Return True when IR/compilation should not transform content."""
    return config.get("allow_modification") is False


def create_passthrough_result(content: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Build a complete pipeline result with unchanged content."""
    return {
        "success": True,
        "passthrough": True,
        "policy_mode": config.get("mode", "off"),
        "prompts": {
            "original": content,
            "sanitized": content,
            "compiled": content,
            "optimized": content,
        },
        "security_result": {
            "is_safe": True,
            "detected_threats": [],
            "masked_entities": {},
            "sanitized_content": content,
            "threat_level": "LOW",
            "security_score": 0.0,
            "recommendations": [],
            "processing_time_ms": 0.0,
            "skipped": True,
        },
        "optimization_metrics": {"token_reduction_percentage": 0},
        "performance_metrics": {"total_pipeline_ms": 0},
        "stage_metrics": {},
    }
