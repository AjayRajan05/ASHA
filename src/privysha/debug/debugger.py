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

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from ..ir.prompt_ir import PromptIR
from ..security.security_layer import SecurityResult
from ..routing.model_router import RoutingDecision


@dataclass
class PipelineStage:
    """Information about a pipeline stage execution."""

    stage_name: str
    input_data: str
    output_data: str
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class DebugTrace:
    """Complete debug trace of prompt processing."""

    session_id: str
    timestamp: datetime
    original_prompt: str
    stages: List[PipelineStage]
    ir_representation: Optional[PromptIR]
    security_result: Optional[SecurityResult]
    routing_decision: Optional[RoutingDecision]
    final_response: Optional[str]
    total_execution_time_ms: float
    token_metrics: Dict[str, int]
    cost_metrics: Dict[str, float]
    performance_metrics: Dict[str, Any]
    errors: List[str]


class PrivySHADebugger:
    """
    Comprehensive debugger and observability system for PrivySHA.

    Provides:
    - Full pipeline tracing
    - Performance metrics
    - Token and cost tracking
    - Error analysis
    - Visual debugging output
    - Export capabilities
    """

    def __init__(self, enabled: bool = True, trace_level: str = "detailed"):
        """Initialize debugger with configuration."""
        self.enabled = enabled
        self.trace_level = trace_level  # "basic", "standard", "detailed"
        self.current_trace = None
        self.trace_history = []
        self.performance_baseline = {}
        self.metrics_collector = MetricsCollector()

    def start_trace(self, prompt: str) -> str:
        """Start a new debug trace session."""
        if not self.enabled:
            return ""

        session_id = self._generate_session_id()
        self.current_trace = DebugTrace(
            session_id=session_id,
            timestamp=datetime.now(),
            original_prompt=prompt,
            stages=[],
            ir_representation=None,
            security_result=None,
            routing_decision=None,
            final_response=None,
            total_execution_time_ms=0.0,
            token_metrics={},
            cost_metrics={},
            performance_metrics={},
            errors=[],
        )

        return session_id

    def add_stage(
        self,
        stage_name: str,
        input_data: str,
        output_data: str,
        success: bool = True,
        error_message: str = None,
        metadata: Dict[str, Any] = None,
    ) -> float:
        """Add a pipeline stage to the current trace."""
        if not self.enabled or not self.current_trace:
            return 0.0

        # Calculate execution time (simplified - would use actual timing)
        execution_time = self._estimate_stage_time(
            stage_name, input_data, output_data)

        stage = PipelineStage(
            stage_name=stage_name,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time,
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )

        self.current_trace.stages.append(stage)

        if not success:
            self.current_trace.errors.append(
                f"Stage {stage_name} failed: {error_message}"
            )

        return execution_time

    def set_ir_representation(self, ir: PromptIR):
        """Set the IR representation for the current trace."""
        if self.enabled and self.current_trace:
            self.current_trace.ir_representation = ir

    def set_security_result(self, security_result: SecurityResult):
        """Set the security result for the current trace."""
        if self.enabled and self.current_trace:
            self.current_trace.security_result = security_result

    def set_routing_decision(self, routing_decision: RoutingDecision):
        """Set the routing decision for the current trace."""
        if self.enabled and self.current_trace:
            self.current_trace.routing_decision = routing_decision

    def set_final_response(self, response: str):
        """Set the final response for the current trace."""
        if self.enabled and self.current_trace:
            self.current_trace.final_response = response

    def finalize_trace(self) -> Optional[DebugTrace]:
        """Finalize the current trace and calculate metrics."""
        if not self.enabled or not self.current_trace:
            return None

        # Calculate total execution time
        self.current_trace.total_execution_time_ms = sum(
            stage.execution_time_ms for stage in self.current_trace.stages
        )

        # Calculate token metrics
        self.current_trace.token_metrics = self._calculate_token_metrics()

        # Calculate cost metrics
        self.current_trace.cost_metrics = self._calculate_cost_metrics()

        # Calculate performance metrics
        self.current_trace.performance_metrics = self._calculate_performance_metrics()

        # Add to history
        self.trace_history.append(self.current_trace)

        # Return completed trace
        completed_trace = self.current_trace
        self.current_trace = None

        return completed_trace

    def get_trace_summary(self, trace: DebugTrace = None) -> Dict[str, Any]:
        """Get a summary of the trace."""
        if trace is None:
            trace = self.current_trace

        if not trace:
            return {"error": "No trace available"}

        summary = {
            "session_id": trace.session_id,
            "timestamp": trace.timestamp.isoformat(),
            "total_stages": len(trace.stages),
            "successful_stages": sum(1 for stage in trace.stages if stage.success),
            "failed_stages": sum(1 for stage in trace.stages if not stage.success),
            "total_execution_time_ms": trace.total_execution_time_ms,
            "has_errors": len(trace.errors) > 0,
            "error_count": len(trace.errors),
        }

        # Add IR summary if available
        if trace.ir_representation:
            summary["ir_summary"] = {
                "intent": trace.ir_representation.intent.value,
                "entity": trace.ir_representation.entity.value,
                "complexity_level": trace.ir_representation.get_complexity_level(),
                "privacy_level": trace.ir_representation.privacy.value,
            }

        # Add security summary if available
        if trace.security_result:
            summary["security_summary"] = {
                "is_safe": trace.security_result.is_safe,
                "threat_level": trace.security_result.threat_level.value,
                "security_score": trace.security_result.security_score,
                "entities_masked": len(trace.security_result.masked_entities),
            }

        # Add routing summary if available
        if trace.routing_decision:
            summary["routing_summary"] = {
                "selected_model": trace.routing_decision.selected_model.name,
                "provider": trace.routing_decision.selected_model.provider,
                "strategy": trace.routing_decision.routing_strategy.value,
                "confidence": trace.routing_decision.confidence_score,
                "estimated_cost": trace.routing_decision.estimated_cost,
            }

        return summary

    def get_detailed_trace(self, trace: DebugTrace = None) -> Dict[str, Any]:
        """Get detailed trace information."""
        if trace is None:
            trace = self.current_trace

        if not trace:
            return {"error": "No trace available"}

        detailed = {
            "session_info": {
                "session_id": trace.session_id,
                "timestamp": trace.timestamp.isoformat(),
                "trace_level": self.trace_level,
            },
            "original_prompt": trace.original_prompt,
            "pipeline_stages": [],
            "final_response": trace.final_response,
            "metrics": {
                "execution": {
                    "total_time_ms": trace.total_execution_time_ms,
                    "stage_times": {
                        stage.stage_name: stage.execution_time_ms
                        for stage in trace.stages
                    },
                },
                "tokens": trace.token_metrics,
                "costs": trace.cost_metrics,
                "performance": trace.performance_metrics,
            },
            "errors": trace.errors,
        }

        # Add detailed stage information
        for stage in trace.stages:
            stage_info = {
                "name": stage.stage_name,
                "success": stage.success,
                "execution_time_ms": stage.execution_time_ms,
                "input_length": len(stage.input_data),
                "output_length": len(stage.output_data),
            }

            if self.trace_level == "detailed":
                stage_info["input_preview"] = (
                    stage.input_data[:100] + "..."
                    if len(stage.input_data) > 100
                    else stage.input_data
                )
                stage_info["output_preview"] = (
                    stage.output_data[:100] + "..."
                    if len(stage.output_data) > 100
                    else stage.output_data
                )

            if stage.error_message:
                stage_info["error"] = stage.error_message

            if stage.metadata:
                stage_info["metadata"] = stage.metadata

            detailed["pipeline_stages"].append(stage_info)

        # Add IR details if available
        if trace.ir_representation:
            detailed["ir_analysis"] = trace.ir_representation.to_dict()

        # Add security details if available
        if trace.security_result:
            detailed["security_analysis"] = {
                "is_safe": trace.security_result.is_safe,
                "threat_level": trace.security_result.threat_level.value,
                "security_score": trace.security_result.security_score,
                "detected_threats": [
                    t.value for t in trace.security_result.detected_threats
                ],
                "masked_entities": trace.security_result.masked_entities,
                "recommendations": trace.security_result.recommendations,
                "processing_time_ms": trace.security_result.processing_time_ms,
            }

        # Add routing details if available
        if trace.routing_decision:
            detailed["routing_analysis"] = {
                "selected_model": {
                    "name": trace.routing_decision.selected_model.name,
                    "provider": trace.routing_decision.selected_model.provider,
                    "capability": trace.routing_decision.selected_model.capability.value,
                    "specializations": trace.routing_decision.selected_model.specializations,
                },
                "strategy": trace.routing_decision.routing_strategy.value,
                "confidence_score": trace.routing_decision.confidence_score,
                "reasoning": trace.routing_decision.reasoning,
                "alternatives": [
                    alt.name for alt in trace.routing_decision.alternative_models
                ],
                "estimated_cost": trace.routing_decision.estimated_cost,
                "estimated_latency": trace.routing_decision.estimated_latency,
            }

        return detailed

    def print_debug_trace(
        self, trace: DebugTrace = None, format_type: str = "readable"
    ) -> str:
        """Print debug trace in specified format."""
        if trace is None:
            trace = self.current_trace

        if not trace:
            return "No trace available"

        if format_type == "readable":
            return self._format_readable_trace(trace)
        elif format_type == "json":
            return json.dumps(self.get_detailed_trace(trace), indent=2, default=str)
        elif format_type == "compact":
            return self._format_compact_trace(trace)
        else:
            return "Unknown format type"

    def _format_readable_trace(self, trace: DebugTrace) -> str:
        """Format trace in human-readable format."""
        output = []
        output.append("=" * 60)
        output.append(f"PRIVYSHA DEBUG TRACE - Session: {trace.session_id}")
        output.append(
            f"Timestamp: {trace.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(
            f"Total Execution Time: {trace.total_execution_time_ms:.2f}ms")
        output.append("=" * 60)

        output.append(f"\nORIGINAL PROMPT:")
        output.append(f"'{trace.original_prompt}'")

        output.append(f"\nPIPELINE STAGES ({len(trace.stages)} stages):")
        for i, stage in enumerate(trace.stages, 1):
            status = "✓" if stage.success else "✗"
            output.append(
                f"\n{i}. {stage.stage_name} {status} ({stage.execution_time_ms:.2f}ms)"
            )

            if self.trace_level in ["standard", "detailed"]:
                output.append(
                    f"   Input:  '{stage.input_data[:50]}{'...' if len(stage.input_data) > 50 else ''}'"
                )
                output.append(
                    f"   Output: '{stage.output_data[:50]}{'...' if len(stage.output_data) > 50 else ''}'"
                )

            if stage.error_message:
                output.append(f"   ERROR: {stage.error_message}")

        # IR Analysis
        if trace.ir_representation:
            ir = trace.ir_representation
            output.append(f"\nINTERMEDIATE REPRESENTATION:")
            output.append(f"Intent: {ir.intent.value}")
            output.append(f"Entity: {ir.entity.value}")
            output.append(f"Privacy: {ir.privacy.value}")
            output.append(f"Complexity: {ir.get_complexity_level()}")
            output.append(f"Constraints: {[c.value for c in ir.constraints]}")

        # Security Analysis
        if trace.security_result:
            sec = trace.security_result
            output.append(f"\nSECURITY ANALYSIS:")
            status = "SAFE" if sec.is_safe else "UNSAFE"
            output.append(f"Status: {status}")
            output.append(f"Threat Level: {sec.threat_level.value}")
            output.append(f"Security Score: {sec.security_score:.2f}")
            output.append(f"Entities Masked: {len(sec.masked_entities)}")

            if sec.detected_threats:
                output.append(
                    f"Detected Threats: {[t.value for t in sec.detected_threats]}"
                )

        # Routing Analysis
        if trace.routing_decision:
            routing = trace.routing_decision
            output.append(f"\nROUTING DECISION:")
            output.append(
                f"Selected Model: {routing.selected_model.name} ({routing.selected_model.provider})"
            )
            output.append(f"Strategy: {routing.routing_strategy.value}")
            output.append(f"Confidence: {routing.confidence_score:.2f}")
            output.append(f"Estimated Cost: ${routing.estimated_cost:.6f}")
            output.append(f"Reasoning: {routing.reasoning}")

        # Metrics
        output.append(f"\nMETRICS:")
        output.append(f"Token Metrics: {trace.token_metrics}")
        output.append(
            f"Cost Metrics: ${trace.cost_metrics.get('total_cost', 0):.6f}")
        output.append(f"Performance: {trace.performance_metrics}")

        # Errors
        if trace.errors:
            output.append(f"\nERRORS ({len(trace.errors)}):")
            for error in trace.errors:
                output.append(f"• {error}")

        # Final Response
        if trace.final_response:
            output.append(f"\nFINAL RESPONSE:")
            response_preview = (
                trace.final_response[:200] + "..."
                if len(trace.final_response) > 200
                else trace.final_response
            )
            output.append(f"'{response_preview}'")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _format_compact_trace(self, trace: DebugTrace) -> str:
        """Format trace in compact format."""
        lines = [
            f"Session: {trace.session_id}",
            f"Time: {trace.total_execution_time_ms:.1f}ms",
            f"Stages: {len(trace.stages)}",
            f"Errors: {len(trace.errors)}",
        ]

        if trace.ir_representation:
            lines.append(f"Intent: {trace.ir_representation.intent.value}")

        if trace.security_result:
            lines.append(
                f"Security: {trace.security_result.threat_level.value}")

        if trace.routing_decision:
            lines.append(
                f"Model: {trace.routing_decision.selected_model.name}")

        return " | ".join(lines)

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    def _estimate_stage_time(
        self, stage_name: str, input_data: str, output_data: str
    ) -> float:
        """Estimate stage execution time (simplified)."""
        base_times = {
            "parsing": 50,
            "sanitization": 30,
            "security": 100,
            "ir_generation": 80,
            "compilation": 60,
            "optimization": 70,
            "routing": 40,
            "generation": 500,  # LLM generation takes longest
        }

        base_time = base_times.get(stage_name, 100)

        # Adjust based on data size
        size_factor = max(1.0, len(input_data) / 1000)

        return base_time * size_factor

    def _calculate_token_metrics(self) -> Dict[str, int]:
        """Calculate token metrics for the trace."""
        if not self.current_trace:
            return {}

        metrics = {
            "original_tokens": self._estimate_tokens(self.current_trace.original_prompt)
        }

        # Add tokens from each stage
        for stage in self.current_trace.stages:
            stage_tokens = self._estimate_tokens(stage.output_data)
            metrics[f"{stage.stage_name}_tokens"] = stage_tokens

        # Calculate total tokens processed
        metrics["total_tokens_processed"] = sum(
            self._estimate_tokens(stage.input_data)
            + self._estimate_tokens(stage.output_data)
            for stage in self.current_trace.stages
        )

        return metrics

    def _calculate_cost_metrics(self) -> Dict[str, float]:
        """Calculate cost metrics for the trace."""
        if not self.current_trace:
            return {}

        total_cost = 0.0

        # Add routing cost if available
        if self.current_trace.routing_decision:
            total_cost += self.current_trace.routing_decision.estimated_cost

        return {
            "total_cost": total_cost,
            "cost_per_token": total_cost
            / max(1, self.current_trace.token_metrics.get("total_tokens_processed", 1)),
        }

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics for the trace."""
        if not self.current_trace:
            return {}

        stages = self.current_trace.stages
        successful_stages = [s for s in stages if s.success]

        return {
            "success_rate": len(successful_stages) / max(1, len(stages)),
            "avg_stage_time": sum(s.execution_time_ms for s in stages)
            / max(1, len(stages)),
            "slowest_stage": (
                max(stages, key=lambda s: s.execution_time_ms).stage_name
                if stages
                else None
            ),
            "fastest_stage": (
                min(stages, key=lambda s: s.execution_time_ms).stage_name
                if stages
                else None
            ),
            "pipeline_efficiency": self._calculate_pipeline_efficiency(),
        }

    def _calculate_pipeline_efficiency(self) -> float:
        """Calculate pipeline efficiency score."""
        if not self.current_trace or not self.current_trace.stages:
            return 0.0

        # Efficiency based on success rate and time distribution
        success_rate = len([s for s in self.current_trace.stages if s.success]) / len(
            self.current_trace.stages
        )

        # Time efficiency (penalize stages that take too long)
        total_time = sum(
            s.execution_time_ms for s in self.current_trace.stages)
        avg_time = total_time / len(self.current_trace.stages)
        time_variance = sum(
            (s.execution_time_ms - avg_time) ** 2 for s in self.current_trace.stages
        ) / len(self.current_trace.stages)
        time_efficiency = max(0, 1.0 - (time_variance / (avg_time**2)))

        return (success_rate * 0.7) + (time_efficiency * 0.3)

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation."""
        return int(len(text.split()) * 1.3)

    def export_trace(self, trace: DebugTrace = None, format_type: str = "json") -> str:
        """Export trace in specified format."""
        if trace is None:
            trace = self.current_trace

        if not trace:
            return ""

        if format_type == "json":
            return json.dumps(self.get_detailed_trace(trace), indent=2, default=str)
        elif format_type == "csv":
            return self._export_csv(trace)
        else:
            return self.print_debug_trace(trace, format_type)

    def _export_csv(self, trace: DebugTrace) -> str:
        """Export trace as CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Stage",
                "Success",
                "Execution_Time_ms",
                "Input_Length",
                "Output_Length",
                "Error",
            ]
        )

        # Stage data
        for stage in trace.stages:
            writer.writerow(
                [
                    stage.stage_name,
                    stage.success,
                    stage.execution_time_ms,
                    len(stage.input_data),
                    len(stage.output_data),
                    stage.error_message or "",
                ]
            )

        return output.getvalue()

    def get_performance_baseline(self) -> Dict[str, Any]:
        """Get performance baseline from historical data."""
        if not self.trace_history:
            return {}

        # Calculate averages
        avg_execution_time = sum(
            t.total_execution_time_ms for t in self.trace_history
        ) / len(self.trace_history)
        avg_success_rate = sum(
            len([s for s in t.stages if s.success]) / max(1, len(t.stages))
            for t in self.trace_history
        ) / len(self.trace_history)

        return {
            "avg_execution_time_ms": avg_execution_time,
            "avg_success_rate": avg_success_rate,
            "total_traces": len(self.trace_history),
            "trace_frequency": len(self.trace_history)
            / max(
                1,
                (datetime.now() -
                 self.trace_history[0].timestamp).total_seconds()
                / 3600,
            ),  # per hour
        }


class MetricsCollector:
    """Collects and aggregates metrics across traces."""

    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_execution_time": 0.0,
            "stage_performance": {},
        }

    def collect_from_trace(self, trace: DebugTrace):
        """Collect metrics from a completed trace."""
        self.metrics["total_requests"] += 1

        if len(trace.errors) == 0:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

        self.metrics["total_tokens"] += trace.token_metrics.get(
            "total_tokens_processed", 0
        )
        self.metrics["total_cost"] += trace.cost_metrics.get("total_cost", 0.0)

        # Update average execution time
        current_avg = self.metrics["avg_execution_time"]
        new_time = trace.total_execution_time_ms
        count = self.metrics["total_requests"]
        self.metrics["avg_execution_time"] = (
            current_avg * (count - 1) + new_time
        ) / count

        # Stage performance
        for stage in trace.stages:
            stage_name = stage.stage_name
            if stage_name not in self.metrics["stage_performance"]:
                self.metrics["stage_performance"][stage_name] = {
                    "total_executions": 0,
                    "total_time": 0.0,
                    "success_count": 0,
                }

            stage_metrics = self.metrics["stage_performance"][stage_name]
            stage_metrics["total_executions"] += 1
            stage_metrics["total_time"] += stage.execution_time_ms
            if stage.success:
                stage_metrics["success_count"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.metrics.copy()
