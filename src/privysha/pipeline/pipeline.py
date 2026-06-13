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

from typing import Dict, List, Any, Optional, Union
import time
from .components import create_context, StageContext
from .stages import (
    SecurityStage,
    IRGenerationStage,
    RoutingStage,
    CompilationStage,
    OptimizationStage,
    GenerationStage,
    ResultStage,
)
from ..core.trace_context import TraceContext, LogLevel
from .policy_gate import should_passthrough, create_passthrough_result


class Pipeline:
    """
    Modular PrivySHA Pipeline with clean stage-based architecture.

    This implementation breaks down the monolithic pipeline into individual,
    maintainable stages while preserving all functionality and improving
    code organization.

    Processing Flow:
    1. Security Processing (PII detection, threat analysis)
    2. IR Generation (Intent extraction, entity recognition)
    3. Model Routing (Intelligent model selection)
    4. Prompt Compilation (IR to prompt conversion)
    5. Prompt Optimization (MSDPC token reduction)
    6. Model Generation (LLM API integration)
    7. Result Assembly (Metrics collection, final result)
    """

    def __init__(
        self,
        privacy: bool = True,
        token_budget: int = 1200,
        security_level: str = "MEDIUM",
        routing_strategy: str = "HYBRID",
        debug_enabled: bool = False,
        optimization_targets: Optional[List[str]] = None,
        fallback_mode: bool = True,
        timeout_ms: int = 0,
        deterministic: bool = False,
        policy_config: Optional[Dict[str, Any]] = None,
        pii_mode: str = "rule",
        reversible: bool = False,
    ) -> None:
        """
        Initialize modular pipeline with all stages.

        Args:
            privacy: Enable privacy features
            token_budget: Token budget for optimization
            security_level: Security processing level
            routing_strategy: Model routing strategy
            debug_enabled: Enable debug tracing
            optimization_targets: List of optimization targets
            fallback_mode: Enable fallback processing if components fail
            timeout_ms: Processing timeout in milliseconds (0 = disabled)
            deterministic: Enable deterministic processing
            policy_config: Policy configuration dictionary
            pii_mode: PII detection mode
        """
        # Store configuration
        self.config = {
            "privacy": privacy,
            "token_budget": token_budget,
            "security_level": security_level,
            "routing_strategy": routing_strategy,
            "debug_enabled": debug_enabled,
            "optimization_targets": optimization_targets or ["tokens", "accuracy"],
            "fallback_mode": fallback_mode,
            "timeout_ms": timeout_ms,
            "deterministic": deterministic,
            "policy_config": policy_config or {},
            "pii_mode": pii_mode,
            "preserve_format": True,
            "pii_masking": privacy,
            "threat_blocking": True,
            "debug_diff": debug_enabled,
            "reversible": reversible,
        }

        # Initialize all stages
        self.stages = {
            "security": SecurityStage(),
            "ir_generation": IRGenerationStage(),
            "routing": RoutingStage(),
            "compilation": CompilationStage(),
            "optimization": OptimizationStage(),
            "generation": GenerationStage(),
            "result": ResultStage(),
        }

        # Additional configuration for specific stages
        if policy_config:
            if hasattr(policy_config, "to_dict"):
                self.config.update(policy_config.to_dict())
            elif isinstance(policy_config, dict):
                self.config.update(policy_config)

    def process(
        self,
        content: str,
        adapter: Optional[Any] = None,
        constraints: Optional[Dict[str, Any]] = None,
        trace: bool = False,
        log_level: Union[str, LogLevel] = LogLevel.INFO,
        debug: bool = False,
        log_output: str = "console",
        log_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process content through complete modular pipeline with observability.

        Args:
            content: Input content to process
            adapter: Universal model adapter (optional)
            constraints: Additional processing constraints
            trace: Enable detailed stage tracing
            log_level: Logging level (ERROR, WARN, INFO, DEBUG)
            debug: Enable debug mode with diff output
            log_output: Output destination ("console", "file", "json")
            log_file: Log file path (if log_output="file")

        Returns:
            Complete processing result with all metrics and traces
        """
        # Input validation
        if content is None:
            raise ValueError("Content cannot be None")
        if not isinstance(content, str):
            raise TypeError("Content must be a string")
        if len(content.strip()) == 0:
            return self._create_empty_result(content)

        trace_context: Optional[TraceContext] = None

        if should_passthrough(self.config):
            result = create_passthrough_result(content, self.config)
            if trace or debug or log_level != LogLevel.INFO:
                trace_context = TraceContext(
                    input_prompt=content,
                    log_level=log_level,
                    trace_enabled=trace,
                    debug_enabled=debug,
                    log_output=log_output,
                    log_file=log_file,
                )
                result["trace"] = trace_context.get_trace_summary()
                result["metrics"] = trace_context.get_metrics()
            from ..utils.metrics_hook import record_from_pipeline_result

            record_from_pipeline_result(content, result)
            return result

        # Create trace context if observability is enabled
        if trace or debug or log_level != LogLevel.INFO:
            trace_context = TraceContext(
                input_prompt=content,
                log_level=log_level,
                trace_enabled=trace,
                debug_enabled=debug,
                log_output=log_output,
                log_file=log_file,
            )

        # Add adapter to config
        if adapter:
            self.config["model_adapter"] = adapter

        # Add constraints to config
        if constraints:
            self.config["routing_constraints"] = constraints

        # Create pipeline context
        context = create_context(
            original_content=content,
            config=self.config,
            debug_enabled=bool(self.config["debug_enabled"]) or debug,
            fallback_mode=bool(self.config["fallback_mode"]),
        )

        # Add trace context to pipeline context
        if trace_context:
            context.trace_context = trace_context

        # Process through all stages
        try:
            final_result = self._process_stages(context)

            # Add trace information if available
            if trace_context:
                final_result["trace"] = trace_context.get_trace_summary()
                final_result["metrics"] = trace_context.get_metrics()
                final_result["diff"] = trace_context.generate_diff(
                ) if debug else None

            from ..utils.metrics_hook import record_from_pipeline_result

            record_from_pipeline_result(content, final_result)
            return final_result

        except Exception as e:
            if self.config["debug_enabled"]:
                print(f"[Pipeline] Critical error: {e}")

            # Return error result with trace if available
            error_result = self._create_error_result(content, str(e), context)
            if trace_context:
                error_result["trace"] = trace_context.get_trace_summary()
                error_result["metrics"] = trace_context.get_metrics()

            return error_result

    def _process_stages(self, context: StageContext) -> Dict[str, Any]:
        """Process content through all pipeline stages."""
        stage_order = [
            "security",
            "ir_generation",
            "routing",
            "compilation",
            "optimization",
            "generation",
            "result",
        ]

        _timeout_val = self.config.get("timeout_ms", 0)
        if isinstance(_timeout_val, (int, float)):
            timeout_ms = int(_timeout_val)
        elif isinstance(_timeout_val, str) and _timeout_val.isdigit():
            timeout_ms = int(_timeout_val)
        else:
            timeout_ms = 0
        deadline = (
            time.perf_counter() + (timeout_ms / 1000.0) if timeout_ms > 0 else None
        )
        enforcer: Optional[Any] = None
        if timeout_ms > 0:
            from ..core.latency_budget import LatencyBudgetEnforcer

            enforcer = LatencyBudgetEnforcer(timeout_ms=timeout_ms)
            enforcer.start_timing()

        for stage_name in stage_order:
            if deadline is not None and time.perf_counter() >= deadline:
                if self.config["debug_enabled"]:
                    print(f"[Pipeline] Timeout exceeded before stage: {stage_name}")
                tc = getattr(context, "trace_context", None)
                if tc:
                    tc.log_warn(
                        stage=stage_name,
                        message="Pipeline deadline exceeded before stage",
                        reason="timeout",
                    )
                return self._create_timeout_result(context, stage_name)

            if enforcer and enforcer.should_skip_layer(
                stage_name, enforcer.accumulated_time
            ):
                tc = getattr(context, "trace_context", None)
                if tc:
                    tc.log_warn(
                        stage=stage_name,
                        message="Stage skipped due to latency budget",
                        reason="budget_exceeded",
                    )
                continue

            if self.config["debug_enabled"]:
                print(f"[Pipeline] Executing stage: {stage_name}")

            if enforcer:
                enforcer.start_layer(stage_name)

            stage = self.stages[stage_name]
            result = stage.process(context)

            if enforcer:
                elapsed = enforcer.end_layer(stage_name)
                if not enforcer.check_budget(stage_name, elapsed):
                    tc = getattr(context, "trace_context", None)
                    if tc:
                        tc.log_warn(
                            stage=stage_name,
                            message=f"Stage exceeded budget ({elapsed:.1f}ms)",
                            reason="stage_budget_exceeded",
                        )

            if not result.success:
                if self.config["debug_enabled"]:
                    print(
                        f"[Pipeline] Stage {stage_name} failed: {result.error}")

                if not self.config["fallback_mode"]:
                    raise RuntimeError(
                        f"Stage {stage_name} failed: {result.error}")

        # Return final result from result stage
        result_stage_data = context.get_stage_data("result_assembly")
        if result_stage_data and isinstance(result_stage_data, dict):
            return dict(result_stage_data)
        return self._create_fallback_result(context)

    def _create_timeout_result(
        self, context: StageContext, stage_name: str
    ) -> Dict[str, Any]:
        """Return a fail-safe result when the pipeline budget is exceeded."""
        security = context.security_result
        original = context.original_content
        sanitized = (
            security.sanitized_content if security else original
        )
        return {
            "success": True,
            "timed_out": True,
            "timeout_stage": stage_name,
            "session_id": context.session_id,
            "prompts": {
                "original": original,
                "sanitized": sanitized,
                "compiled": context.compiled_prompt or sanitized,
                "optimized": context.optimized_prompt or sanitized,
            },
            "security_result": security,
            "optimization_metrics": {"token_reduction_percentage": 0},
            "response": context.model_response,
            "stage_metrics": context.stage_metrics,
            "performance_metrics": {
                "total_pipeline_ms": context.get_total_execution_time(),
                "timeout_ms": self.config.get("timeout_ms", 0),
            },
            "processing_summary": context.get_processing_summary(),
        }

    def _create_empty_result(self, content: str) -> Dict[str, Any]:
        """Create result for empty input."""
        return {
            "success": True,
            "result": "",
            "prompts": {
                "original": content,
                "sanitized": content,
                "compiled": content,
                "optimized": content,
            },
            "optimization_metrics": {"token_reduction_percentage": 0},
            "security_result": {
                "is_safe": True,
                "detected_threats": [],
                "masked_entities": {},
                "sanitized_content": content,
                "threat_level": "LOW",
                "security_score": 0.0,
                "recommendations": [],
                "processing_time_ms": 0.0,
            },
            "performance_metrics": {"total_pipeline_ms": 0},
        }

    def _create_error_result(
        self, content: str, error: str, context: StageContext
    ) -> Dict[str, Any]:
        """Create result for processing error."""
        return {
            "success": False,
            "error": error,
            "session_id": context.session_id,
            "prompts": {
                "original": content,
                "sanitized": content,
                "compiled": content,
                "optimized": content,
            },
            "optimization_metrics": {"token_reduction_percentage": 0},
            "stage_metrics": context.stage_metrics,
            "performance_metrics": {
                "total_pipeline_ms": context.get_total_execution_time()
            },
        }

    def _create_fallback_result(self, context: StageContext) -> Dict[str, Any]:
        """Create fallback result when result stage fails."""
        security = context.security_result
        return {
            "success": True,
            "session_id": context.session_id,
            "prompts": {
                "original": context.original_content,
                "sanitized": (
                    security.sanitized_content
                    if security
                    else context.original_content
                ),
                "compiled": context.compiled_prompt or "",
                "optimized": context.optimized_prompt or context.original_content,
            },
            "security_result": security,
            "optimization_metrics": {"token_reduction_percentage": 0},
            "response": context.model_response,
            "stage_metrics": context.stage_metrics,
            "performance_metrics": {
                "total_pipeline_ms": context.get_total_execution_time()
            },
            "processing_summary": context.get_processing_summary(),
        }

    def get_stage_info(self) -> Dict[str, Any]:
        """Get information about all pipeline stages."""
        return {
            "stages": list(self.stages.keys()),
            "total_stages": len(self.stages),
            "configuration": self.config,
            "modular_architecture": True,
        }

    def configure_stage(self, stage_name: str, config: Dict[str, Any]) -> None:
        """
        Configure a specific pipeline stage.

        Args:
            stage_name: Name of the stage to configure
            config: Configuration dictionary for the stage
        """
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}")

        # Add stage-specific configuration
        stages_config = self.config.setdefault("stages", {})
        if isinstance(stages_config, dict):
            stages_config[stage_name] = config

    def get_stage_metrics(self, stage_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for a specific stage or all stages.

        Args:
            stage_name: Name of specific stage (optional)

        Returns:
            Stage metrics dictionary
        """
        # This would need to be implemented with a context from last run
        # For now, return empty dict
        return {}

    def reset(self) -> None:
        """Reset pipeline to initial state."""
        self.stages = {
            "security": SecurityStage(),
            "ir_generation": IRGenerationStage(),
            "routing": RoutingStage(),
            "compilation": CompilationStage(),
            "optimization": OptimizationStage(),
            "generation": GenerationStage(),
            "result": ResultStage(),
        }

    def __len__(self) -> int:
        """Return number of stages in pipeline."""
        return len(self.stages)

    def __getitem__(self, stage_name: str) -> Any:
        """Get a specific stage by name."""
        return self.stages.get(stage_name)

    def __contains__(self, stage_name: str) -> bool:
        """Check if stage exists in pipeline."""
        return stage_name in self.stages
