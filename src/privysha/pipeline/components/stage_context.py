"""
Stage context utilities for data sharing between pipeline stages
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import uuid
import time


@dataclass
class StageContext:
    """Shared context between pipeline stages."""

    original_content: str
    session_id: str
    config: Dict[str, Any]
    debug_enabled: bool
    fallback_mode: bool

    # Stage-specific data
    security_result: Optional[Any] = None
    ir: Optional[Any] = None
    routing_decision: Optional[Any] = None
    compiled_prompt: Optional[str] = None
    optimized_prompt: Optional[str] = None
    model_response: Optional[str] = None

    # Metrics collection
    stage_metrics: Dict[str, Any] = field(default_factory=dict)

    # Observability (optional — set by pipeline when tracing is enabled)
    trace_context: Optional[Any] = None

    # Processing metadata
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    def get_stage_data(self, stage_name: str) -> Any:
        """
        Get data from a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Stage data or None if not found
        """
        return self.stage_metrics.get(stage_name, {}).get("data")

    def set_stage_data(self, stage_name: str, data: Any):
        """
        Set data for a specific stage.

        Args:
            stage_name: Name of the stage
            data: Data to store
        """
        if stage_name not in self.stage_metrics:
            self.stage_metrics[stage_name] = {}

        self.stage_metrics[stage_name]["data"] = data

    def get_stage_metrics(self, stage_name: str) -> Dict[str, Any]:
        """
        Get metrics for a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Stage metrics or empty dict
        """
        return self.stage_metrics.get(stage_name, {})

    def add_stage_metric(self, stage_name: str, key: str, value: Any):
        """
        Add a metric for a specific stage.

        Args:
            stage_name: Name of the stage
            key: Metric key
            value: Metric value
        """
        if stage_name not in self.stage_metrics:
            self.stage_metrics[stage_name] = {}

        if "metrics" not in self.stage_metrics[stage_name]:
            self.stage_metrics[stage_name]["metrics"] = {}

        self.stage_metrics[stage_name]["metrics"][key] = value

    def get_total_execution_time(self) -> float:
        """
        Get total execution time for all completed stages.

        Returns:
            Total execution time in milliseconds
        """
        total_time = 0.0

        for stage_data in self.stage_metrics.values():
            if isinstance(stage_data, dict) and "execution_time_ms" in stage_data:
                total_time += stage_data["execution_time_ms"]

        return total_time

    def _is_stage_metrics_entry(self, stage_data: Any) -> bool:
        """Return True if stage_data is a per-stage metrics dict."""
        return isinstance(stage_data, dict) and "success" in stage_data

    def get_successful_stages(self) -> list:
        """
        Get list of successfully completed stages.

        Returns:
            List of stage names
        """
        successful = []

        for stage_name, stage_data in self.stage_metrics.items():
            if self._is_stage_metrics_entry(stage_data) and stage_data.get("success", False):
                successful.append(stage_name)

        return successful

    def get_failed_stages(self) -> list:
        """
        Get list of failed stages.

        Returns:
            List of stage names
        """
        failed = []

        for stage_name, stage_data in self.stage_metrics.items():
            if self._is_stage_metrics_entry(stage_data) and not stage_data.get(
                "success", False
            ):
                failed.append(stage_name)

        return failed

    def has_fallbacks(self) -> bool:
        """
        Check if any stage used fallback processing.

        Returns:
            True if any fallback was used
        """
        for stage_data in self.stage_metrics.values():
            if self._is_stage_metrics_entry(stage_data) and stage_data.get(
                "fallback_used", False
            ):
                return True

        return False

    def finalize(self):
        """Finalize the context with end time."""
        self.end_time = time.time()

    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the entire processing pipeline.

        Returns:
            Processing summary dictionary
        """
        return {
            "session_id": self.session_id,
            "total_execution_time_ms": self.get_total_execution_time(),
            "successful_stages": self.get_successful_stages(),
            "failed_stages": self.get_failed_stages(),
            "fallbacks_used": self.has_fallbacks(),
            "stage_count": len(self.stage_metrics),
            "processing_time_seconds": (self.end_time or time.time()) - self.start_time,
        }


def create_context(
    original_content: str,
    config: Dict[str, Any],
    debug_enabled: bool = False,
    fallback_mode: bool = True,
) -> StageContext:
    """
    Create a new stage context.

    Args:
        original_content: Original input content
        config: Pipeline configuration
        debug_enabled: Enable debug mode
        fallback_mode: Enable fallback processing

    Returns:
        New StageContext instance
    """
    session_id = str(uuid.uuid4())

    return StageContext(
        original_content=original_content,
        session_id=session_id,
        config=config,
        debug_enabled=debug_enabled,
        fallback_mode=fallback_mode,
    )
