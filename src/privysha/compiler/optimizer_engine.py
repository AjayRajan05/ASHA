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

from typing import Dict, List, Any, Tuple, Optional
from ..ir.prompt_ir import PromptIR
from ..core.safety_constraints import SafetyConstraints
from ..core.format_lock import FormatLock
from .msdpc import MSDPCOptimizer


class PromptOptimizer:
    """
    Prompt Optimizer Engine - Clean wrapper around MSDPC

    This class provides backward compatibility while delegating
    all optimization work to the Multi-Stage Deterministic Prompt Compiler.
    """

    def __init__(self, use_msdpc: bool = True):
        """
        Initialize optimizer with MSDPC.

        Args:
            use_msdpc: Always use MSDPC (legacy mode deprecated)
        """
        if not use_msdpc:
            raise DeprecationWarning(
                "Legacy optimizer is deprecated. Use MSDPC instead."
            )

        self.use_msdpc = True
        self.msdpc_optimizer = MSDPCOptimizer()
        self.safety_constraints = SafetyConstraints()
        self.format_lock = FormatLock()

    def optimize(
        self,
        prompt: str,
        ir: PromptIR,
        optimization_targets: Optional[List[str]] = None,
        optimization_level: int = 2,
        preserve_format: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize prompt using MSDPC.

        Args:
            prompt: Original prompt
            ir: Prompt IR for context (not used by MSDPC but kept for compatibility)
            optimization_targets: List of optimization targets (not used by MSDPC)
            optimization_level: Optimization level (not used by MSDPC)
            preserve_format: Whether to preserve format structure

        Returns:
            Tuple of (optimized_prompt, optimization_metrics)
        """
        # Configure MSDPC based on format preservation
        structure = self.format_lock.detect_structure(prompt)
        if preserve_format and structure in ("json", "code"):
            legacy_metrics = {
                "original_tokens": len(prompt.split()),
                "optimized_tokens": len(prompt.split()),
                "token_reduction": 0,
                "token_reduction_percentage": 0.0,
                "optimizations_applied": ["format_lock_skipped"],
                "token_savings": 0,
                "cost_savings": 0.0,
                "quality_score": 1.0,
                "structure_type": structure,
                "format_lock_applied": {"skipped_optimization": True},
                "safety_violations": [],
                "msdpc_used": False,
                "msdpc_metrics": {
                    "clarity_score": 1.0,
                    "structure_score": 1.0,
                    "efficiency_score": 1.0,
                    "intent_preserved": True,
                    "processing_time_ms": 0.0,
                },
            }
            return prompt, legacy_metrics

        enable_structure = (
            not preserve_format or structure == "plain"
        )
        enable_output_shaping = True  # Always enable output shaping for better results

        self.msdpc_optimizer.configure(
            enable_structure_building=enable_structure,
            enable_output_shaping=enable_output_shaping,
            enable_templates=False,  # Keep templates disabled for minimal changes
            target_reduction=0.4,  # 40% target reduction
        )

        # Apply MSDPC optimization
        optimized_prompt, msdpc_metrics = self.msdpc_optimizer.optimize(prompt)

        # Apply safety constraints check
        is_safe, violations = self.safety_constraints.check_safety(
            prompt, optimized_prompt
        )
        if not is_safe:
            # Revert to original if safety violations detected
            optimized_prompt = prompt
            msdpc_metrics.stages_applied.append(
                "reverted_due_to_safety_violations")

        # Convert MSDPC metrics to legacy format for compatibility
        legacy_metrics = {
            "original_tokens": msdpc_metrics.original_tokens,
            "optimized_tokens": msdpc_metrics.optimized_tokens,
            "token_reduction": msdpc_metrics.original_tokens
            - msdpc_metrics.optimized_tokens,
            "token_reduction_percentage": msdpc_metrics.token_reduction_percentage,
            "optimizations_applied": msdpc_metrics.stages_applied,
            "token_savings": msdpc_metrics.original_tokens
            - msdpc_metrics.optimized_tokens,
            "cost_savings": 0.0,  # Would need model info for calculation
            "quality_score": (
                msdpc_metrics.clarity_score
                + msdpc_metrics.structure_score
                + msdpc_metrics.efficiency_score
            )
            / 3,
            "structure_type": (
                self.format_lock.detect_structure(prompt)
                if preserve_format
                else "plain"
            ),
            "format_lock_applied": {},
            "safety_violations": violations if not is_safe else [],
            "msdpc_used": True,
            "msdpc_metrics": {
                "clarity_score": msdpc_metrics.clarity_score,
                "structure_score": msdpc_metrics.structure_score,
                "efficiency_score": msdpc_metrics.efficiency_score,
                "intent_preserved": msdpc_metrics.intent_preserved,
                "processing_time_ms": msdpc_metrics.processing_time_ms,
            },
        }

        return optimized_prompt, legacy_metrics

    def get_optimization_summary(self, metrics: Dict[str, Any]) -> str:
        """
        Generate human-readable optimization summary.

        Args:
            metrics: Optimization metrics from optimize() call

        Returns:
            Formatted summary string
        """
        if metrics.get("msdpc_used", False):
            # MSDPC summary
            msdpc_metrics = metrics.get("msdpc_metrics", {})
            summary = f"""
MSDPC Optimization Summary:
============================
Token Reduction: {metrics['token_reduction_percentage']:.1f}%
Original Tokens: {metrics['original_tokens']}
Optimized Tokens: {metrics['optimized_tokens']}
Processing Time: {msdpc_metrics.get('processing_time_ms', 0):.1f}ms

Quality Scores:
- Clarity: {msdpc_metrics.get('clarity_score', 0):.2f}
- Structure: {msdpc_metrics.get('structure_score', 0):.2f}
- Efficiency: {msdpc_metrics.get('efficiency_score', 0):.2f}
- Intent Preserved: {'✅' if msdpc_metrics.get('intent_preserved', False) else '❌'}

Stages Applied: {', '.join(metrics.get('optimizations_applied', []))}

Performance Classification:
"""
            if metrics["token_reduction_percentage"] > 50:
                summary += "🔥 EXCELLENT (50%+ reduction)\n"
            elif metrics["token_reduction_percentage"] > 30:
                summary += "✅ GOOD (30-50% reduction)\n"
            elif metrics["token_reduction_percentage"] > 15:
                summary += "⚠️ MODERATE (15-30% reduction)\n"
            else:
                summary += "❌ NEEDS IMPROVEMENT (<15% reduction)\n"
        else:
            # Legacy optimizer summary (should not happen)
            summary = f"""
Legacy Optimization Summary:
==========================
Token Reduction: {metrics['token_reduction_percentage']:.1f}%
Original Tokens: {metrics['original_tokens']}
Optimized Tokens: {metrics['optimized_tokens']}
Quality Score: {metrics.get('quality_score', 1.0):.2f}

Optimizations Applied: {', '.join(metrics.get('optimizations_applied', []))}
Structure Type: {metrics.get('structure_type', 'unknown')}

Performance Classification:
"""
            if metrics["token_reduction_percentage"] > 15:
                summary += "✅ GOOD (>15% reduction)\n"
            elif metrics["token_reduction_percentage"] > 8:
                summary += "⚠️ MODERATE (8-15% reduction)\n"
            else:
                summary += "❌ NEEDS IMPROVEMENT (<8% reduction)\n"

        return summary.strip()

    def configure_msdpc(
        self,
        enable_structure_building: bool = True,
        enable_output_shaping: bool = True,
        enable_templates: bool = False,
        target_reduction: float = 0.4,
    ) -> None:
        """
        Configure MSDPC optimizer settings.

        Args:
            enable_structure_building: Enable structural rewriting
            enable_output_shaping: Enable output shaping
            enable_templates: Enable template engine
            target_reduction: Target token reduction percentage
        """
        if self.use_msdpc and hasattr(self, "msdpc_optimizer"):
            self.msdpc_optimizer.configure(
                enable_structure_building=enable_structure_building,
                enable_output_shaping=enable_output_shaping,
                enable_templates=enable_templates,
                target_reduction=target_reduction,
            )
        else:
            raise RuntimeError("MSDPC is not enabled.")

    def switch_to_msdpc(self) -> None:
        """Switch to MSDPC optimizer (already enabled by default)."""
        if not self.use_msdpc:
            self.use_msdpc = True
            self.msdpc_optimizer = MSDPCOptimizer()

    def switch_to_legacy(self) -> None:
        """Legacy mode is deprecated."""
        raise DeprecationWarning(
            "Legacy optimizer is deprecated. Use MSDPC instead.")

    def benchmark_optimization(self, prompt: str, ir: PromptIR) -> Dict[str, Any]:
        """Benchmark optimization performance using MSDPC."""
        results: Dict[str, Any] = {"msdpc_enabled": self.use_msdpc, "benchmark_results": {}}

        # Test different optimization strategies
        strategies = ["tokens", "speed", "accuracy", "cost"]

        for strategy in strategies:
            optimized, metrics = self.optimize(prompt, ir, [strategy])
            results["benchmark_results"][strategy] = {
                "optimized_prompt": optimized,
                "metrics": metrics,
                "token_reduction": metrics["token_reduction_percentage"],
                "quality_impact": metrics.get("quality_score", 1.0),
            }

        # Find best overall strategy
        best_strategy = max(
            strategies, key=lambda s: results["benchmark_results"][s]["token_reduction"]
        )
        results["best_strategy"] = best_strategy
        results["recommendations"] = self.get_optimization_recommendations(ir)

        return results

    def get_optimization_recommendations(self, ir: PromptIR) -> List[str]:
        """Get optimization recommendations based on IR analysis."""
        recommendations = []

        # Intent-based recommendations
        if ir.intent.value == "analyze":
            recommendations.append("Focus on key insights and patterns")
        elif ir.intent.value == "summarize":
            recommendations.append("Emphasize main points and conclusions")
        elif ir.intent.value == "generate":
            recommendations.append("Specify output format and requirements")

        # Complexity-based recommendations
        complexity = ir.get_complexity_level()
        if complexity == "high":
            recommendations.append(
                "Break down complex task into simpler sub-tasks")
            recommendations.append("Consider using comprehensive optimization")
        elif complexity == "low":
            recommendations.append("Minimal optimization should be sufficient")

        return recommendations
