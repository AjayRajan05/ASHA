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
Debug Trace System - Phase 5 Developer Addiction

Complete observability pipeline:
RAW → SANITIZED → IR → OPTIMIZED → SAFE → OUTPUT

Features:
- Full pipeline trace with timing
- Stage-by-stage transformation tracking
- Performance metrics collection
- Visual trace formatting
- Export capabilities

Makes developers LOVE using PrivySHA through complete transparency.
"""

import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class TraceStage(Enum):
    """Pipeline stages for tracing."""

    RAW = "raw"
    SANITIZED = "sanitized"
    IR_GENERATION = "ir_generation"
    MODEL_ROUTING = "model_routing"
    PROMPT_COMPILATION = "prompt_compilation"
    OPTIMIZATION = "optimization"
    SAFETY_CHECK = "safety_check"
    FINAL_OUTPUT = "final_output"


@dataclass
class StageTrace:
    """Trace information for a single stage."""

    stage: TraceStage
    input_content: str
    output_content: str
    success: bool
    error: Optional[str]
    execution_time_ms: float
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class PipelineTrace:
    """Complete pipeline trace."""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_time_ms: float
    stages: List[StageTrace]
    success: bool
    final_output: Optional[str]
    error: Optional[str]
    performance_metrics: Dict[str, Any]
    metadata: Dict[str, Any]


class DebugTracer:
    """
    Advanced debug tracer for complete pipeline observability.

    Provides detailed tracing of every transformation step:
    RAW → SANITIZED → IR → OPTIMIZED → SAFE → OUTPUT
    """

    def __init__(
        self, enable_timing: bool = True, enable_metadata: bool = True
    ) -> None:
        """Initialize debug tracer."""
        self.enable_timing = enable_timing
        self.enable_metadata = enable_metadata
        self.current_trace: Optional[PipelineTrace] = None
        self.trace_history: List[PipelineTrace] = []
        self.session_counter = 0

    def start_trace(
        self, initial_content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new pipeline trace.

        Returns:
            Session ID for the trace
        """
        self.session_counter += 1
        session_id = f"trace_{int(time.time())}_{self.session_counter}"

        self.current_trace = PipelineTrace(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            total_time_ms=0.0,
            stages=[],
            success=False,
            final_output=None,
            error=None,
            performance_metrics={},
            metadata=metadata or {},
        )

        # Add initial RAW stage
        self.add_stage(
            TraceStage.RAW,
            initial_content,
            initial_content,
            True,
            None,
            {"description": "Initial input content"},
        )

        return session_id

    def add_stage(
        self,
        stage: TraceStage,
        input_content: str,
        output_content: str,
        success: bool,
        error: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a stage trace."""
        if not self.current_trace:
            return

        stage_trace = StageTrace(
            stage=stage,
            input_content=input_content,
            output_content=output_content,
            success=success,
            error=error,
            execution_time_ms=0.0,  # Will be calculated if timing enabled
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        # Calculate execution time if timing enabled and we have previous stage
        if self.enable_timing and self.current_trace.stages:
            prev_stage = self.current_trace.stages[-1]
            time_diff = (
                stage_trace.timestamp - prev_stage.timestamp
            ).total_seconds() * 1000
            stage_trace.execution_time_ms = time_diff

        self.current_trace.stages.append(stage_trace)

    def finalize_trace(
        self, final_output: Optional[str] = None, error: Optional[str] = None
    ) -> PipelineTrace:
        """Finalize the current trace."""
        if not self.current_trace:
            return PipelineTrace(
                session_id="no_trace",
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_time_ms=0.0,
                stages=[],
                success=False,
                final_output=None,
                error="No trace started",
                performance_metrics={},
                metadata={},
            )

        self.current_trace.end_time = datetime.now()
        self.current_trace.total_time_ms = (
            self.current_trace.end_time - self.current_trace.start_time
        ).total_seconds() * 1000
        self.current_trace.success = error is None
        self.current_trace.final_output = final_output
        self.current_trace.error = error

        # Calculate performance metrics
        self.current_trace.performance_metrics = self._calculate_performance_metrics()

        # Add to history
        self.trace_history.append(self.current_trace)

        # Store reference and reset current
        completed_trace = self.current_trace
        self.current_trace = None

        return completed_trace

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from trace."""
        if not self.current_trace or not self.current_trace.stages:
            return {}

        stages = self.current_trace.stages

        # Stage timings
        stage_timings: Dict[str, List[float]] = {}
        for stage in stages:
            if stage.stage.value not in stage_timings:
                stage_timings[stage.stage.value] = []
            stage_timings[stage.stage.value].append(stage.execution_time_ms)

        # Calculate averages
        avg_stage_timings = {}
        for stage_name, timings in stage_timings.items():
            avg_stage_timings[stage_name] = (
                sum(timings) / len(timings) if timings else 0
            )

        # Token analysis
        token_analysis = self._analyze_tokens()

        # Success rates
        success_rates = self._calculate_success_rates()

        return {
            "stage_timings": avg_stage_timings,
            "token_analysis": token_analysis,
            "success_rates": success_rates,
            "total_stages": len(stages),
            "successful_stages": len([s for s in stages if s.success]),
            "failed_stages": len([s for s in stages if not s.success]),
        }

    def _analyze_tokens(self) -> Dict[str, Any]:
        """Analyze token changes across stages."""
        if not self.current_trace or not self.current_trace.stages:
            return {}

        token_changes: List[Dict[str, Any]] = []
        prev_tokens = 0

        for stage in self.current_trace.stages:
            if stage.output_content:
                tokens = len(stage.output_content.split())
                if prev_tokens > 0:
                    change = tokens - prev_tokens
                    token_changes.append(
                        {
                            "stage": stage.stage.value,
                            "tokens": tokens,
                            "change": change,
                            "change_percentage": (
                                (change / prev_tokens * 100) if prev_tokens > 0 else 0
                            ),
                        }
                    )
                prev_tokens = tokens

        negative_changes = [
            int(tc["change"]) for tc in token_changes if int(tc["change"]) < 0
        ]
        return {
            "token_changes": token_changes,
            "total_token_change": sum(int(tc["change"]) for tc in token_changes),
            "max_token_reduction": min(negative_changes, default=0),
        }

    def _calculate_success_rates(self) -> Dict[str, Any]:
        """Calculate success rates by stage type."""
        if not self.current_trace or not self.current_trace.stages:
            return {}

        stage_stats = {}
        for stage in self.current_trace.stages:
            stage_name = stage.stage.value
            if stage_name not in stage_stats:
                stage_stats[stage_name] = {"total": 0, "success": 0}

            stage_stats[stage_name]["total"] += 1
            if stage.success:
                stage_stats[stage_name]["success"] += 1

        # Calculate success rates
        success_rates = {}
        for stage_name, stats in stage_stats.items():
            success_rates[stage_name] = (
                stats["success"] / stats["total"] if stats["total"] > 0 else 0
            )

        return success_rates

    def get_trace_summary(
        self, session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get summary of a specific trace or latest trace."""
        if session_id:
            trace = next(
                (t for t in self.trace_history if t.session_id == session_id), None
            )
        elif self.trace_history:
            trace = self.trace_history[-1]
        else:
            return None

        if not trace:
            return None

        return {
            "session_id": trace.session_id,
            "success": trace.success,
            "total_time_ms": trace.total_time_ms,
            "stages_completed": len(trace.stages),
            "final_output_length": len(trace.final_output) if trace.final_output else 0,
            "has_errors": trace.error is not None,
            "performance_summary": trace.performance_metrics,
        }

    def export_trace(
        self, session_id: Optional[str] = None, format_type: str = "json"
    ) -> Optional[str]:
        """Export trace in specified format."""
        if session_id:
            trace = next(
                (t for t in self.trace_history if t.session_id == session_id), None
            )
        elif self.trace_history:
            trace = self.trace_history[-1]
        else:
            return None

        if not trace:
            return None

        if format_type == "json":
            return self._export_json(trace)
        elif format_type == "readable":
            return self._export_readable(trace)
        elif format_type == "compact":
            return self._export_compact(trace)
        else:
            return self._export_json(trace)

    def _export_json(self, trace: PipelineTrace) -> str:
        """Export trace as JSON."""
        # Convert datetime objects to strings
        trace_dict = asdict(trace)
        trace_dict["start_time"] = trace.start_time.isoformat()
        trace_dict["end_time"] = trace.end_time.isoformat(
        ) if trace.end_time else None

        for stage in trace_dict["stages"]:
            stage["timestamp"] = stage["timestamp"].isoformat()

        return json.dumps(trace_dict, indent=2)

    def _export_readable(self, trace: PipelineTrace) -> str:
        """Export trace as readable format."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"PRIVYSHA DEBUG TRACE - {trace.session_id}")
        lines.append("=" * 80)
        lines.append(
            f"Start Time: {trace.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Time: {trace.total_time_ms:.2f}ms")
        lines.append(f"Success: {trace.success}")
        lines.append(f"Stages: {len(trace.stages)}")

        if trace.error:
            lines.append(f"Error: {trace.error}")

        lines.append("")
        lines.append("STAGE TRANSFORMATIONS:")
        lines.append("-" * 40)

        for i, stage in enumerate(trace.stages, 1):
            lines.append(f"{i}. {stage.stage.value.upper()}")
            lines.append(f"   Success: {stage.success}")
            lines.append(f"   Time: {stage.execution_time_ms:.2f}ms")

            if stage.error:
                lines.append(f"   Error: {stage.error}")

            # Show content transformation
            if stage.input_content != stage.output_content:
                lines.append(
                    f"   Input:  {stage.input_content[:100]}{'...' if len(stage.input_content) > 100 else ''}"
                )
                lines.append(
                    f"   Output: {stage.output_content[:100]}{'...' if len(stage.output_content) > 100 else ''}"
                )
            else:
                lines.append(
                    f"   Content: {stage.output_content[:100]}{'...' if len(stage.output_content) > 100 else ''}"
                )

            if stage.metadata:
                for key, value in stage.metadata.items():
                    lines.append(f"   {key}: {value}")

            lines.append("")

        if trace.performance_metrics:
            lines.append("PERFORMANCE METRICS:")
            lines.append("-" * 40)
            for key, value in trace.performance_metrics.items():
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  {sub_key}: {sub_value}")
                else:
                    lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def _export_compact(self, trace: PipelineTrace) -> str:
        """Export trace as compact format."""
        summary = self.get_trace_summary(trace.session_id)
        if not summary:
            return ""

        lines = [
            f"Trace: {trace.session_id}",
            f"Time: {trace.total_time_ms:.1f}ms",
            f"Success: {trace.success}",
            f"Stages: {len(trace.stages)}",
        ]

        return " | ".join(lines)

    def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics for all traces."""
        if not self.trace_history:
            return {}

        total_traces = len(self.trace_history)
        successful_traces = len([t for t in self.trace_history if t.success])
        failed_traces = total_traces - successful_traces

        # Calculate average times
        times = [t.total_time_ms for t in self.trace_history]
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0

        # Stage statistics
        stage_counts: Dict[str, int] = {}
        for trace in self.trace_history:
            for stage in trace.stages:
                stage_name = stage.stage.value
                stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1

        return {
            "total_traces": total_traces,
            "successful_traces": successful_traces,
            "failed_traces": failed_traces,
            "success_rate": successful_traces / total_traces if total_traces > 0 else 0,
            "avg_time_ms": avg_time,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "stage_usage": stage_counts,
            "trace_history_size": len(self.trace_history),
        }


class TraceVisualizer:
    """Visual formatter for debug traces."""

    @staticmethod
    def format_pipeline_flow(trace: PipelineTrace) -> str:
        """Format the pipeline flow visually."""
        if not trace.stages:
            return "No stages in trace"

        lines = []
        lines.append("PIPELINE FLOW:")
        lines.append(
            "RAW → SANITIZED → IR → ROUTING → COMPILE → OPTIMIZE → SAFE → OUTPUT"
        )
        lines.append("")

        # Create flow diagram
        flow_stages = [
            "raw",
            "sanitized",
            "ir_generation",
            "model_routing",
            "prompt_compilation",
            "optimization",
            "safety_check",
            "final_output",
        ]

        flow_line = ""
        for stage_name in flow_stages:
            stage = next(
                (s for s in trace.stages if s.stage.value == stage_name), None)
            if stage:
                if stage.success:
                    flow_line += f"✅{stage.stage.value[:3].upper()}→"
                else:
                    flow_line += f"❌{stage.stage.value[:3].upper()}→"
            else:
                flow_line += f"⚪{stage_name[:3].upper()}→"

        lines.append(flow_line.rstrip("→"))
        lines.append("")

        # Add stage details
        for stage in trace.stages:
            status = "✅" if stage.success else "❌"
            lines.append(
                f"{status} {stage.stage.value}: {stage.execution_time_ms:.1f}ms"
            )

        return "\n".join(lines)

    @staticmethod
    def format_content_changes(trace: PipelineTrace) -> str:
        """Format content changes across stages."""
        if not trace.stages:
            return "No stages in trace"

        lines = []
        lines.append("CONTENT TRANSFORMATIONS:")
        lines.append("-" * 50)

        for i, stage in enumerate(trace.stages):
            if i == 0:
                continue  # Skip first stage (no previous content)

            prev_stage = trace.stages[i - 1]

            if prev_stage.output_content != stage.output_content:
                lines.append(f"{stage.stage.value.upper()}:")
                lines.append(
                    f"  Before: {prev_stage.output_content[:80]}{'...' if len(prev_stage.output_content) > 80 else ''}"
                )
                lines.append(
                    f"  After:  {stage.output_content[:80]}{'...' if len(stage.output_content) > 80 else ''}"
                )
                lines.append(
                    f"  Change: {len(stage.output_content) - len(prev_stage.output_content):+d} chars"
                )
                lines.append("")

        if len(lines) == 2:  # Only header
            lines.append("No content changes detected")

        return "\n".join(lines)

    @staticmethod
    def format_timing_breakdown(trace: PipelineTrace) -> str:
        """Format timing breakdown."""
        if not trace.stages:
            return "No stages in trace"

        lines = []
        lines.append("TIMING BREAKDOWN:")
        lines.append("-" * 30)

        total_time = sum(s.execution_time_ms for s in trace.stages)

        for stage in trace.stages:
            percentage = (
                (stage.execution_time_ms / total_time * 100) if total_time > 0 else 0
            )
            bar_length = int(percentage / 5)  # 5% per character
            bar = "█" * bar_length + "░" * (20 - bar_length)
            lines.append(
                f"{stage.stage.value:15}: {bar} {percentage:5.1f}% ({stage.execution_time_ms:6.1f}ms)"
            )

        lines.append(f"{'TOTAL':15}: {'█' * 20} 100.0% ({total_time:6.1f}ms)")

        return "\n".join(lines)


class TraceManager:
    """
    High-level trace management interface.

    Provides easy access to tracing functionality with
    automatic integration points.
    """

    def __init__(self) -> None:
        """Initialize trace manager."""
        self.tracer = DebugTracer()
        self.visualizer = TraceVisualizer()
        self.auto_trace = True

    def enable_auto_trace(self) -> None:
        """Enable automatic tracing."""
        self.auto_trace = True

    def disable_auto_trace(self) -> None:
        """Disable automatic tracing."""
        self.auto_trace = False

    def start_session(self, content: str, **kwargs: Any) -> str:
        """Start a new tracing session."""
        if not self.auto_trace:
            return "disabled"

        return self.tracer.start_trace(content, kwargs)

    def trace_stage(
        self,
        stage: str,
        input_content: str,
        output_content: str,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Trace a stage execution."""
        if not self.auto_trace:
            return

        try:
            stage_enum = TraceStage(stage)
            self.tracer.add_stage(
                stage_enum, input_content, output_content, success, error, kwargs
            )
        except ValueError:
            # Invalid stage name, skip
            pass

    def end_session(
        self, final_output: Optional[str] = None, error: Optional[str] = None
    ) -> Optional[PipelineTrace]:
        """End current tracing session."""
        if not self.auto_trace:
            return None

        return self.tracer.finalize_trace(final_output, error)

    def print_trace(
        self, session_id: Optional[str] = None, format_type: str = "readable"
    ) -> None:
        """Print trace in specified format."""
        if not self.auto_trace:
            print("Auto-tracing is disabled")
            return

        trace_export = self.tracer.export_trace(session_id, format_type)
        if trace_export:
            print(trace_export)
        else:
            print("No trace found")

    def print_flow(self, session_id: Optional[str] = None) -> None:
        """Print visual pipeline flow."""
        if not self.auto_trace:
            print("Auto-tracing is disabled")
            return

        if session_id:
            trace = next(
                (t for t in self.tracer.trace_history if t.session_id == session_id),
                None,
            )
        elif self.tracer.trace_history:
            trace = self.tracer.trace_history[-1]
        else:
            print("No trace found")
            return

        if trace:
            print(self.visualizer.format_pipeline_flow(trace))

    def print_changes(self, session_id: Optional[str] = None) -> None:
        """Print content changes."""
        if not self.auto_trace:
            print("Auto-tracing is disabled")
            return

        if session_id:
            trace = next(
                (t for t in self.tracer.trace_history if t.session_id == session_id),
                None,
            )
        elif self.tracer.trace_history:
            trace = self.tracer.trace_history[-1]
        else:
            print("No trace found")
            return

        if trace:
            print(self.visualizer.format_content_changes(trace))

    def print_timing(self, session_id: Optional[str] = None) -> None:
        """Print timing breakdown."""
        if not self.auto_trace:
            print("Auto-tracing is disabled")
            return

        if session_id:
            trace = next(
                (t for t in self.tracer.trace_history if t.session_id == session_id),
                None,
            )
        elif self.tracer.trace_history:
            trace = self.tracer.trace_history[-1]
        else:
            print("No trace found")
            return

        if trace:
            print(self.visualizer.format_timing_breakdown(trace))

    def get_stats(self) -> Dict[str, Any]:
        """Get tracing statistics."""
        return self.tracer.get_trace_statistics()


# Global trace manager instance
trace_manager = TraceManager()


# Convenience functions for easy access
def start_trace(content: str, **kwargs: Any) -> str:
    """Start a new trace session."""
    return trace_manager.start_session(content, **kwargs)


def trace_stage(
    stage: str, input_content: str, output_content: str, **kwargs: Any
) -> None:
    """Trace a stage execution."""
    trace_manager.trace_stage(stage, input_content, output_content, **kwargs)


def end_trace(
    final_output: Optional[str] = None, error: Optional[str] = None
) -> Optional[PipelineTrace]:
    """End current trace session."""
    return trace_manager.end_session(final_output, error)


def print_trace(
    session_id: Optional[str] = None, format_type: str = "readable"
) -> None:
    """Print trace in specified format."""
    trace_manager.print_trace(session_id, format_type)


def print_flow(session_id: Optional[str] = None) -> None:
    """Print pipeline flow visualization."""
    trace_manager.print_flow(session_id)


def print_changes(session_id: Optional[str] = None) -> None:
    """Print content changes."""
    trace_manager.print_changes(session_id)


def print_timing(session_id: Optional[str] = None) -> None:
    """Print timing breakdown."""
    trace_manager.print_timing(session_id)


def get_trace_stats() -> Dict[str, Any]:
    """Get trace statistics."""
    return trace_manager.get_stats()


# Quick test function
def test_debug_trace() -> None:
    """Test debug trace system."""
    print("Testing Debug Trace System:")
    print("=" * 50)

    # Start trace
    session_id = start_trace("Contact john@email.com for support")
    print(f"Started trace: {session_id}")

    # Trace stages
    trace_stage(
        "sanitized",
        "Contact john@email.com for support",
        "Contact [EMAIL_HASH]_abc123 for support",
    )

    trace_stage(
        "optimization",
        "Contact [EMAIL_HASH]_abc123 for support",
        "Contact [EMAIL_HASH]_abc123 for support",
    )

    trace_stage(
        "safety_check",
        "Contact [EMAIL_HASH]_abc123 for support",
        "Contact [EMAIL_HASH]_abc123 for support",
    )

    # End trace
    trace_result = end_trace("Contact [EMAIL_HASH]_abc123 for support")

    # Print different views
    print("\n🔍 FLOW VISUALIZATION:")
    print_flow()

    print("\n📊 TIMING BREAKDOWN:")
    print_timing()

    print("\n📈 TRACE STATISTICS:")
    stats = get_trace_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_debug_trace()
