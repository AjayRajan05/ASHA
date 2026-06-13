"""
Metrics collection utilities for pipeline stages
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class StageMetrics:
    """Metrics for a single stage execution."""

    stage_name: str
    success: bool
    execution_time_ms: float
    input_size: int
    output_size: int
    custom_metrics: Dict[str, Any]
    error: Optional[str] = None
    fallback_used: bool = False


class MetricsCollector:
    """Collects and aggregates metrics across pipeline stages."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.stage_metrics: List[StageMetrics] = []
        self.pipeline_start_time = time.time()
        self.pipeline_end_time: Optional[float] = None

    def add_stage_metrics(
        self,
        stage_name: str,
        success: bool,
        execution_time_ms: float,
        input_size: int,
        output_size: int,
        custom_metrics: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        fallback_used: bool = False,
    ) -> None:
        """
        Add metrics for a stage execution.

        Args:
            stage_name: Name of the stage
            success: Whether stage succeeded
            execution_time_ms: Execution time in milliseconds
            input_size: Size of input data
            output_size: Size of output data
            custom_metrics: Custom stage-specific metrics
            error: Error message if failed
            fallback_used: Whether fallback was used
        """
        metrics = StageMetrics(
            stage_name=stage_name,
            success=success,
            execution_time_ms=execution_time_ms,
            input_size=input_size,
            output_size=output_size,
            custom_metrics=custom_metrics or {},
            error=error,
            fallback_used=fallback_used,
        )

        self.stage_metrics.append(metrics)

    def finalize_pipeline(self) -> None:
        """Mark pipeline as complete."""
        self.pipeline_end_time = time.time()

    def get_total_execution_time(self) -> float:
        """Get total execution time for all stages."""
        return sum(m.execution_time_ms for m in self.stage_metrics)

    def get_pipeline_duration(self) -> float:
        """Get total pipeline duration."""
        end_time = self.pipeline_end_time or time.time()
        return (end_time - self.pipeline_start_time) * 1000

    def get_successful_stages(self) -> List[str]:
        """Get list of successful stage names."""
        return [m.stage_name for m in self.stage_metrics if m.success]

    def get_failed_stages(self) -> List[str]:
        """Get list of failed stage names."""
        return [m.stage_name for m in self.stage_metrics if not m.success]

    def get_stages_with_fallbacks(self) -> List[str]:
        """Get list of stages that used fallbacks."""
        return [m.stage_name for m in self.stage_metrics if m.fallback_used]

    def get_stage_metrics(self, stage_name: str) -> Optional[StageMetrics]:
        """Get metrics for a specific stage."""
        for metrics in self.stage_metrics:
            if metrics.stage_name == stage_name:
                return metrics
        return None

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of the pipeline."""
        successful_count = len(self.get_successful_stages())
        failed_count = len(self.get_failed_stages())
        fallback_count = len(self.get_stages_with_fallbacks())

        # Calculate stage-specific performance
        stage_performance = {}
        for metrics in self.stage_metrics:
            stage_performance[metrics.stage_name] = {
                "success": metrics.success,
                "execution_time_ms": metrics.execution_time_ms,
                "input_size": metrics.input_size,
                "output_size": metrics.output_size,
                "size_reduction": (
                    (metrics.input_size - metrics.output_size) / metrics.input_size
                    if metrics.input_size > 0
                    else 0
                ),
                "fallback_used": metrics.fallback_used,
                "error": metrics.error,
            }

        return {
            "total_stages": len(self.stage_metrics),
            "successful_stages": successful_count,
            "failed_stages": failed_count,
            "stages_with_fallbacks": fallback_count,
            "success_rate": (
                successful_count /
                len(self.stage_metrics) if self.stage_metrics else 0
            ),
            "total_execution_time_ms": self.get_total_execution_time(),
            "pipeline_duration_ms": self.get_pipeline_duration(),
            "average_stage_time_ms": (
                self.get_total_execution_time() / len(self.stage_metrics)
                if self.stage_metrics
                else 0
            ),
            "stage_performance": stage_performance,
        }

    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality-related metrics."""
        quality_metrics: Dict[str, List[Any]] = {}

        # Collect custom metrics from all stages
        for metrics in self.stage_metrics:
            if metrics.custom_metrics:
                for key, value in metrics.custom_metrics.items():
                    if key not in quality_metrics:
                        quality_metrics[key] = []
                    quality_metrics[key].append(value)

        # Calculate averages for numeric metrics
        averaged_metrics = {}
        for key, values in quality_metrics.items():
            if all(isinstance(v, (int, float)) for v in values):
                averaged_metrics[key] = {
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
            else:
                averaged_metrics[key] = {
                    "values": values, "count": len(values)}

        return averaged_metrics

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics in a structured format."""
        return {
            "pipeline_summary": self.get_performance_summary(),
            "quality_metrics": self.get_quality_metrics(),
            "detailed_metrics": [
                {
                    "stage_name": m.stage_name,
                    "success": m.success,
                    "execution_time_ms": m.execution_time_ms,
                    "input_size": m.input_size,
                    "output_size": m.output_size,
                    "custom_metrics": m.custom_metrics,
                    "error": m.error,
                    "fallback_used": m.fallback_used,
                }
                for m in self.stage_metrics
            ],
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.stage_metrics.clear()
        self.pipeline_start_time = time.time()
        self.pipeline_end_time = None


def calculate_size_reduction(input_size: int, output_size: int) -> float:
    """
    Calculate percentage reduction in size.

    Args:
        input_size: Original size
        output_size: Reduced size

    Returns:
        Percentage reduction (0.0 to 1.0)
    """
    if input_size == 0:
        return 0.0

    return (input_size - output_size) / input_size


def calculate_throughput(items_processed: int, time_ms: float) -> float:
    """
    Calculate throughput (items per second).

    Args:
        items_processed: Number of items processed
        time_ms: Processing time in milliseconds

    Returns:
        Throughput in items per second
    """
    if time_ms == 0:
        return 0.0

    return (items_processed / time_ms) * 1000
