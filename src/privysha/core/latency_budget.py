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
Latency budget enforcer for PrivySHA.

Ensures hard timeout enforcement at pipeline level for real-time applications.
"""

import time
from typing import Dict, Optional, Callable


class LatencyBudgetEnforcer:
    """
    Hard latency budget enforcement for production safety.

    This is MANDATORY for real-time applications - prevents
    PrivySHA from exceeding acceptable processing times.
    """

    def __init__(self, timeout_ms: int = 100):
        """
        Initialize latency budget enforcer.

        Args:
            timeout_ms: Total timeout budget in milliseconds
        """
        self.timeout_ms = timeout_ms
        self.layer_budgets = {
            "security": 30,  # 30ms for security processing
            "optimization": 50,  # 50ms for optimization
            "routing": 10,  # 10ms for model routing
            "compilation": 10,  # 10ms for prompt compilation
            "generation": 0,  # Variable - depends on LLM response time
            "total": timeout_ms,  # Total budget
        }
        self.start_time = 0.0
        self.layer_start_times = {}
        self.accumulated_time = 0.0
        self.budget_exceeded = False
        self.skipped_layers = []

    def start_timing(self):
        """Start timing the overall operation."""
        self.start_time = time.time()
        self.accumulated_time = 0.0
        self.budget_exceeded = False
        self.skipped_layers = []
        self.layer_start_times = {}

    def start_layer(self, layer_name: str):
        """Start timing a specific pipeline layer."""
        self.layer_start_times[layer_name] = time.time()

    def end_layer(self, layer_name: str) -> float:
        """End timing a specific layer and return elapsed time."""
        if layer_name not in self.layer_start_times:
            return 0.0

        elapsed_ms = (time.time() - self.layer_start_times[layer_name]) * 1000
        self.accumulated_time += elapsed_ms
        del self.layer_start_times[layer_name]

        return elapsed_ms

    def check_budget(self, operation: str, elapsed_ms: float) -> bool:
        """
        Check if operation exceeded its budget.

        Args:
            operation: Operation name
            elapsed_ms: Elapsed time in milliseconds

        Returns:
            True if within budget, False if exceeded
        """
        budget = self.layer_budgets.get(operation, self.timeout_ms)
        return elapsed_ms <= budget

    def should_skip_layer(self, layer: str, elapsed_ms: float) -> bool:
        """
        Determine if layer should be skipped due to time constraints.

        Args:
            layer: Layer name to potentially skip
            elapsed_ms: Time already spent

        Returns:
            True if layer should be skipped
        """
        remaining_budget = self.layer_budgets["total"] - self.accumulated_time
        layer_budget = self.layer_budgets.get(layer, 0)

        return remaining_budget < layer_budget

    def get_remaining_budget(self) -> float:
        """Get remaining budget in milliseconds."""
        elapsed_ms = (time.time() - self.start_time) * 1000
        remaining = self.layer_budgets["total"] - elapsed_ms
        return max(0.0, remaining)

    def get_budget_status(self) -> Dict[str, any]:
        """
        Get comprehensive budget status.

        Returns:
            Dictionary with budget status information
        """
        elapsed_ms = (time.time() - self.start_time) * 1000
        remaining_ms = self.get_remaining_budget()

        return {
            "total_budget_ms": self.layer_budgets["total"],
            "elapsed_ms": elapsed_ms,
            "remaining_ms": remaining_ms,
            "budget_exceeded": self.budget_exceeded,
            "utilization_percentage": (elapsed_ms / self.layer_budgets["total"]) * 100,
            "skipped_layers": self.skipped_layers,
            "layer_budgets": self.layer_budgets.copy(),
            "recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> list:
        """Get budget-based recommendations."""
        recommendations = []

        elapsed_ms = (time.time() - self.start_time) * 1000
        utilization = (elapsed_ms / self.layer_budgets["total"]) * 100

        if utilization > 80:
            recommendations.append(
                "High utilization - consider increasing timeout")

        if len(self.skipped_layers) > 0:
            recommendations.append(
                f"Skipped layers: {', '.join(self.skipped_layers)}")

        if self.get_remaining_budget() < 20:
            recommendations.append(
                "Low remaining budget - optimization may be incomplete"
            )

        return recommendations

    def enforce_timeout(self, fallback_func: Optional[Callable] = None):
        """
        Enforce timeout and return fallback if exceeded.

        Args:
            fallback_func: Function to call for fallback result

        Returns:
            Fallback result if timeout exceeded, None otherwise
        """
        elapsed_ms = (time.time() - self.start_time) * 1000

        if elapsed_ms > self.timeout_ms:
            self.budget_exceeded = True
            if fallback_func:
                return fallback_func()
            else:
                return None

        return None

    def create_fallback_result(
        self, original_prompt: str, reason: str = "timeout"
    ) -> Dict[str, any]:
        """
        Create a fallback result for timeout scenarios.

        Args:
            original_prompt: Original prompt that couldn't be processed
            reason: Reason for fallback

        Returns:
            Fallback result dictionary
        """
        return {
            "success": False,
            "error": f"Timeout exceeded: {reason}",
            "fallback_used": True,
            "result": original_prompt,
            "processing_time_ms": (time.time() - self.start_time) * 1000,
            "budget_status": self.get_budget_status(),
        }


class PipelineTimer:
    """
    Context manager for timing pipeline operations with budget enforcement.
    """

    def __init__(self, enforcer: LatencyBudgetEnforcer, layer_name: str):
        self.enforcer = enforcer
        self.layer_name = layer_name
        self.start_time = 0.0

    def __enter__(self):
        """Enter context and start timing."""
        self.enforcer.start_layer(self.layer_name)
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and check budget."""
        elapsed_ms = self.enforcer.end_layer(self.layer_name)

        # Check if this layer exceeded its budget
        if not self.enforcer.check_budget(self.layer_name, elapsed_ms):
            # Mark that this layer should be skipped in future
            self.enforcer.skipped_layers.append(self.layer_name)

        return False  # Don't suppress exceptions
