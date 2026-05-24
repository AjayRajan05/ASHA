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
PrivySHA - Drop-in Security & Optimization Layer for Any LLM App

Primary API (import directly):
    from privysha import process, wrap_llm, optimize, sanitize, Agent

Advanced components load lazily on first access, e.g.:
    from privysha import HybridPIIDetector
    from privysha.core.benchmark import BenchmarkHarness
"""

from importlib import import_module
from typing import Any, Tuple

__version__ = "1.0.1"

# ---------------------------------------------------------------------------
# Core public API — eager imports only (fast startup, stable surface)
# ---------------------------------------------------------------------------
from .agent import Agent
from .pipeline.pipeline import Pipeline
from .adapters.factory import AdapterFactory
from .utils.dropin import (
    process,
    wrap_llm,
    optimize,
    sanitize,
    process_async,
    optimize_async,
    sanitize_async,
)
from .utils.auto_patch import (
    auto_patch,
    get_patch_status,
    disable_auto_patch,
    enable_auto_patch,
)
from .utils.unmask import unmask

__all__ = [
    "__version__",
    # Drop-in utilities
    "process",
    "wrap_llm",
    "optimize",
    "sanitize",
    "process_async",
    "optimize_async",
    "sanitize_async",
    "unmask",
    "auto_patch",
    "get_patch_status",
    "disable_auto_patch",
    "enable_auto_patch",
    # Core classes
    "Agent",
    "Pipeline",
    "AdapterFactory",
    # Lazy-loaded (listed for IDE / tab-completion support)
    "UniversalWrapper",
    "PromptIR",
    "IntentType",
    "EntityType",
    "ConstraintType",
    "PrivacyLevel",
    "IRBuilder",
    "PromptCompiler",
    "PromptOptimizer",
    "SecurityLayer",
    "SecurityResult",
    "SecurityLevel",
    "ThreatType",
    "ModelRouter",
    "RoutingDecision",
    "RoutingStrategy",
    "ModelConfig",
    "ModelCapability",
    "PrivySHADebugger",
    "DebugTrace",
    "PipelineStage",
    "MetricsCollector",
    "UniversalModelAdapter",
    "PolicyConfig",
    "PolicyMode",
    "get_preset",
    "DiffEngine",
    "DiffResult",
    "ChangeType",
    "BenchmarkHarness",
    "BenchmarkResult",
    "BenchmarkSummary",
    "HybridPIIDetector",
    "PIIEntity",
    "HybridResult",
    "detect_pii",
    "SemanticTokenOptimizer",
    "OptimizationResult",
    "OptimizationLevel",
    "optimize_semantically",
    "SchemaValidationMode",
    "ValidationResult",
    "ValidationStatus",
    "validate_schema",
    "repair_json",
    "SafetyClassifier",
    "SafetyResult",
    "SafetyLevel",
    "classify_safety",
    "FastAPIMiddleware",
    "IntegrationConfig",
    "LangChainPromptTemplate",
    "PrivySHALLM",
    "PrivySHAInstructorClient",
    "OpenAIWrapper",
    "add_privysha_to_fastapi",
    "wrap_langchain_llm",
    "wrap_instructor_client",
    "wrap_openai_client",
    "privysha_process",
    "ToolChain",
    "PrivySHAInstructorComposer",
    "PrivySHAGuardrailsComposer",
    "PrivySHALangChainComposer",
    "compose_with_instructor",
    "compose_with_guardrails",
    "compose_with_langchain",
    "DebugTracer",
    "PipelineTrace",
    "StageTrace",
    "TraceStage",
    "TraceVisualizer",
    "TraceManager",
    "trace_manager",
    "start_trace",
    "trace_stage",
    "end_trace",
    "print_trace",
    "print_flow",
    "print_changes",
    "print_timing",
    "get_trace_stats",
    "MetricsDashboard",
    "UsageStats",
    "PerformanceMetrics",
    "dashboard",
    "record_request",
    "update_system_metrics",
    "show_dashboard",
    "show_trends",
    "show_security_report",
    "export_metrics",
    "TraceContext",
    "LogLevel",
    "StageChange",
    "PipelineMetrics",
    "ExplainabilityEngine",
    "ProcessingExplanation",
    "enable_otel",
]

# module_path relative to privysha package, attribute name
_LAZY_IMPORTS: dict[str, Tuple[str, str]] = {
    "UniversalWrapper": (".utils.wrapper", "UniversalWrapper"),
    "PromptIR": (".ir.prompt_ir", "PromptIR"),
    "IntentType": (".ir.prompt_ir", "IntentType"),
    "EntityType": (".ir.prompt_ir", "EntityType"),
    "ConstraintType": (".ir.prompt_ir", "ConstraintType"),
    "PrivacyLevel": (".ir.prompt_ir", "PrivacyLevel"),
    "IRBuilder": (".ir.ir_builder", "IRBuilder"),
    "PromptCompiler": (".compiler.prompt_compiler", "PromptCompiler"),
    "PromptOptimizer": (".compiler.optimizer_engine", "PromptOptimizer"),
    "SecurityLayer": (".security.security_layer", "SecurityLayer"),
    "SecurityResult": (".security.security_layer", "SecurityResult"),
    "SecurityLevel": (".security.security_layer", "SecurityLevel"),
    "ThreatType": (".security.security_layer", "ThreatType"),
    "ModelRouter": (".routing.model_router", "ModelRouter"),
    "RoutingDecision": (".routing.model_router", "RoutingDecision"),
    "RoutingStrategy": (".routing.model_router", "RoutingStrategy"),
    "ModelConfig": (".routing.model_router", "ModelConfig"),
    "ModelCapability": (".routing.model_router", "ModelCapability"),
    "PrivySHADebugger": (".debug.debugger", "PrivySHADebugger"),
    "DebugTrace": (".debug.debugger", "DebugTrace"),
    "PipelineStage": (".debug.debugger", "PipelineStage"),
    "MetricsCollector": (".core.metrics_dashboard", "MetricsCollector"),
    "UniversalModelAdapter": (".adapters.universal_adapter", "UniversalModelAdapter"),
    "PolicyConfig": (".core.policy_config", "PolicyConfig"),
    "PolicyMode": (".core.policy_config", "PolicyMode"),
    "get_preset": (".core.policy_config", "get_preset"),
    "DiffEngine": (".core.diff_engine", "DiffEngine"),
    "DiffResult": (".core.diff_engine", "DiffResult"),
    "ChangeType": (".core.diff_engine", "ChangeType"),
    "BenchmarkHarness": (".core.benchmark", "BenchmarkHarness"),
    "BenchmarkResult": (".core.benchmark", "BenchmarkResult"),
    "BenchmarkSummary": (".core.benchmark", "BenchmarkSummary"),
    "HybridPIIDetector": (".core.hybrid_pii", "HybridPIIDetector"),
    "PIIEntity": (".core.hybrid_pii", "PIIEntity"),
    "HybridResult": (".core.hybrid_pii", "HybridResult"),
    "detect_pii": (".core.hybrid_pii", "detect_pii"),
    "SemanticTokenOptimizer": (".core.semantic_optimizer", "SemanticTokenOptimizer"),
    "OptimizationResult": (".core.semantic_optimizer", "OptimizationResult"),
    "OptimizationLevel": (".core.semantic_optimizer", "OptimizationLevel"),
    "optimize_semantically": (".core.semantic_optimizer", "optimize_semantically"),
    "SchemaValidationMode": (".core.schema_validation", "SchemaValidationMode"),
    "ValidationResult": (".core.schema_validation", "ValidationResult"),
    "ValidationStatus": (".core.schema_validation", "ValidationStatus"),
    "validate_schema": (".core.schema_validation", "validate_schema"),
    "repair_json": (".core.schema_validation", "repair_json"),
    "SafetyClassifier": (".core.safety_classifier", "SafetyClassifier"),
    "SafetyResult": (".core.safety_classifier", "SafetyResult"),
    "SafetyLevel": (".core.safety_classifier", "SafetyLevel"),
    "classify_safety": (".core.safety_classifier", "classify_safety"),
    "FastAPIMiddleware": (".integrations.framework_adapters", "FastAPIMiddleware"),
    "IntegrationConfig": (".integrations.framework_adapters", "IntegrationConfig"),
    "LangChainPromptTemplate": (
        ".integrations.framework_adapters",
        "LangChainPromptTemplate",
    ),
    "PrivySHALLM": (".integrations.framework_adapters", "PrivySHALLM"),
    "PrivySHAInstructorClient": (
        ".integrations.framework_adapters",
        "PrivySHAInstructorClient",
    ),
    "OpenAIWrapper": (".integrations.framework_adapters", "OpenAIWrapper"),
    "add_privysha_to_fastapi": (
        ".integrations.framework_adapters",
        "add_privysha_to_fastapi",
    ),
    "wrap_langchain_llm": (".integrations.framework_adapters", "wrap_langchain_llm"),
    "wrap_instructor_client": (
        ".integrations.framework_adapters",
        "wrap_instructor_client",
    ),
    "wrap_openai_client": (".integrations.framework_adapters", "wrap_openai_client"),
    "privysha_process": (".integrations.framework_adapters", "privysha_process"),
    "ToolChain": (".integrations.composition_strategy", "ToolChain"),
    "PrivySHAInstructorComposer": (
        ".integrations.composition_strategy",
        "PrivySHAInstructorComposer",
    ),
    "PrivySHAGuardrailsComposer": (
        ".integrations.composition_strategy",
        "PrivySHAGuardrailsComposer",
    ),
    "PrivySHALangChainComposer": (
        ".integrations.composition_strategy",
        "PrivySHALangChainComposer",
    ),
    "compose_with_instructor": (
        ".integrations.composition_strategy",
        "compose_with_instructor",
    ),
    "compose_with_guardrails": (
        ".integrations.composition_strategy",
        "compose_with_guardrails",
    ),
    "compose_with_langchain": (
        ".integrations.composition_strategy",
        "compose_with_langchain",
    ),
    "DebugTracer": (".core.debug_trace", "DebugTracer"),
    "PipelineTrace": (".core.debug_trace", "PipelineTrace"),
    "StageTrace": (".core.debug_trace", "StageTrace"),
    "TraceStage": (".core.debug_trace", "TraceStage"),
    "TraceVisualizer": (".core.debug_trace", "TraceVisualizer"),
    "TraceManager": (".core.debug_trace", "TraceManager"),
    "trace_manager": (".core.debug_trace", "trace_manager"),
    "start_trace": (".core.debug_trace", "start_trace"),
    "trace_stage": (".core.debug_trace", "trace_stage"),
    "end_trace": (".core.debug_trace", "end_trace"),
    "print_trace": (".core.debug_trace", "print_trace"),
    "print_flow": (".core.debug_trace", "print_flow"),
    "print_changes": (".core.debug_trace", "print_changes"),
    "print_timing": (".core.debug_trace", "print_timing"),
    "get_trace_stats": (".core.debug_trace", "get_trace_stats"),
    "MetricsDashboard": (".core.metrics_dashboard", "MetricsDashboard"),
    "UsageStats": (".core.metrics_dashboard", "UsageStats"),
    "PerformanceMetrics": (".core.metrics_dashboard", "PerformanceMetrics"),
    "dashboard": (".core.metrics_dashboard", "dashboard"),
    "record_request": (".core.metrics_dashboard", "record_request"),
    "update_system_metrics": (".core.metrics_dashboard", "update_system_metrics"),
    "show_dashboard": (".core.metrics_dashboard", "show_dashboard"),
    "show_trends": (".core.metrics_dashboard", "show_trends"),
    "show_security_report": (".core.metrics_dashboard", "show_security_report"),
    "export_metrics": (".core.metrics_dashboard", "export_metrics"),
    "TraceContext": (".core.trace_context", "TraceContext"),
    "LogLevel": (".core.trace_context", "LogLevel"),
    "StageChange": (".core.trace_context", "StageChange"),
    "PipelineMetrics": (".core.trace_context", "PipelineMetrics"),
    "ExplainabilityEngine": (".core.explainability", "ExplainabilityEngine"),
    "ProcessingExplanation": (".core.explainability", "ProcessingExplanation"),
    "enable_otel": (".integrations.otel", "enable_otel"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        if name == "DebugTracer":
            import warnings

            warnings.warn(
                "DebugTracer is deprecated; use TraceContext instead "
                "(see docs/debugging.md).",
                DeprecationWarning,
                stacklevel=2,
            )
        module_path, attr = _LAZY_IMPORTS[name]
        module = import_module(module_path, __name__)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
