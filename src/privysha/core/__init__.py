"""
Core - Critical infrastructure for PII detection, security, and optimization.

Heavy submodules load lazily on first attribute access to keep import time low.
"""

from importlib import import_module
from typing import Any, Dict, Tuple

# Lightweight modules — safe to import eagerly
from .policy_config import PolicyConfig, PolicyMode, get_preset
from .diff_engine import DiffEngine, DiffResult, ChangeType
from .trace_context import TraceContext, LogLevel, StageChange, PipelineMetrics

_LAZY_IMPORTS: Dict[str, Tuple[str, str]] = {
    "BenchmarkHarness": (".benchmark", "BenchmarkHarness"),
    "BenchmarkResult": (".benchmark", "BenchmarkResult"),
    "BenchmarkSummary": (".benchmark", "BenchmarkSummary"),
    "HybridPIIDetector": (".hybrid_pii", "HybridPIIDetector"),
    "PIIEntity": (".hybrid_pii", "PIIEntity"),
    "HybridResult": (".hybrid_pii", "HybridResult"),
    "detect_pii": (".hybrid_pii", "detect_pii"),
    "SemanticTokenOptimizer": (".semantic_optimizer", "SemanticTokenOptimizer"),
    "OptimizationResult": (".semantic_optimizer", "OptimizationResult"),
    "OptimizationLevel": (".semantic_optimizer", "OptimizationLevel"),
    "optimize_semantically": (".semantic_optimizer", "optimize_semantically"),
    "SchemaValidationMode": (".schema_validation", "SchemaValidationMode"),
    "ValidationResult": (".schema_validation", "ValidationResult"),
    "ValidationStatus": (".schema_validation", "ValidationStatus"),
    "validate_schema": (".schema_validation", "validate_schema"),
    "repair_json": (".schema_validation", "repair_json"),
    "SafetyClassifier": (".safety_classifier", "SafetyClassifier"),
    "SafetyResult": (".safety_classifier", "SafetyResult"),
    "SafetyLevel": (".safety_classifier", "SafetyLevel"),
    "ThreatType": (".safety_classifier", "ThreatType"),
    "classify_safety": (".safety_classifier", "classify_safety"),
    "DebugTracer": (".debug_trace", "DebugTracer"),
    "PipelineTrace": (".debug_trace", "PipelineTrace"),
    "StageTrace": (".debug_trace", "StageTrace"),
    "TraceStage": (".debug_trace", "TraceStage"),
    "TraceVisualizer": (".debug_trace", "TraceVisualizer"),
    "TraceManager": (".debug_trace", "TraceManager"),
    "trace_manager": (".debug_trace", "trace_manager"),
    "start_trace": (".debug_trace", "start_trace"),
    "trace_stage": (".debug_trace", "trace_stage"),
    "end_trace": (".debug_trace", "end_trace"),
    "print_trace": (".debug_trace", "print_trace"),
    "print_flow": (".debug_trace", "print_flow"),
    "print_changes": (".debug_trace", "print_changes"),
    "print_timing": (".debug_trace", "print_timing"),
    "get_trace_stats": (".debug_trace", "get_trace_stats"),
    "MetricsDashboard": (".metrics_dashboard", "MetricsDashboard"),
    "MetricsCollector": (".metrics_dashboard", "MetricsCollector"),
    "UsageStats": (".metrics_dashboard", "UsageStats"),
    "PerformanceMetrics": (".metrics_dashboard", "PerformanceMetrics"),
    "dashboard": (".metrics_dashboard", "dashboard"),
    "record_request": (".metrics_dashboard", "record_request"),
    "update_system_metrics": (".metrics_dashboard", "update_system_metrics"),
    "show_dashboard": (".metrics_dashboard", "show_dashboard"),
    "show_trends": (".metrics_dashboard", "show_trends"),
    "show_security_report": (".metrics_dashboard", "show_security_report"),
    "export_metrics": (".metrics_dashboard", "export_metrics"),
    "ExplainabilityEngine": (".explainability", "ExplainabilityEngine"),
    "ProcessingExplanation": (".explainability", "ProcessingExplanation"),
    "RiskAnalyzer": (".risk_analyzer", "RiskAnalyzer"),
    "EnhancedRiskAnalyzer": (".risk_analyzer", "EnhancedRiskAnalyzer"),
}

__all__ = [
    "PolicyConfig",
    "PolicyMode",
    "get_preset",
    "DiffEngine",
    "DiffResult",
    "ChangeType",
    "TraceContext",
    "LogLevel",
    "StageChange",
    "PipelineMetrics",
    *sorted(_LAZY_IMPORTS.keys()),
]


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        module = import_module(module_path, __name__)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
