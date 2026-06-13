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
Explainability layer with human-readable reasoning summaries.

Provides transparent explanations for PrivySHA decisions and processing steps.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class ExplanationStep:
    """Single step in processing explanation."""

    step_number: int
    step_name: str
    description: str
    action_taken: str
    reasoning: str
    confidence: float
    execution_time_ms: float
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]


@dataclass
class ProcessingExplanation:
    """Complete explanation of PrivySHA processing."""

    session_id: str
    total_processing_time_ms: float
    steps: List[ExplanationStep]
    summary: str
    risk_assessment: Dict[str, Any]
    optimization_decisions: Dict[str, Any]
    security_findings: Dict[str, Any]
    confidence_score: float
    human_readable_summary: str


class ExplainabilityEngine:
    """
    Explainability engine for generating human-readable reasoning summaries.

    Provides transparent explanations for:
    - Mode selection decisions
    - Security processing results
    - Optimization choices
    - Performance metrics
    """

    def __init__(self) -> None:
        self.explanations: Dict[str, ProcessingExplanation] = {}

    def generate_explanation(
        self,
        session_id: str,
        processing_result: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]] = None,
        security_result: Optional[Dict[str, Any]] = None,
        optimization_metrics: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
    ) -> ProcessingExplanation:
        """
        Generate comprehensive explanation for PrivySHA processing.

        Args:
            session_id: Processing session ID
            processing_result: Complete pipeline processing result
            risk_assessment: Risk assessment results
            security_result: Security processing results
            optimization_metrics: Optimization metrics
            performance_metrics: Performance metrics

        Returns:
            ProcessingExplanation with human-readable summary
        """
        steps = []
        current_step = 0

        # Step 1: Input Analysis
        current_step += 1
        input_analysis = self._explain_input_analysis(processing_result)
        steps.append(input_analysis)

        # Step 2: Mode Selection (if applicable)
        if risk_assessment:
            current_step += 1
            mode_selection = self._explain_mode_selection(risk_assessment)
            steps.append(mode_selection)

        # Step 3: Security Processing
        if security_result:
            current_step += 1
            security_explanation = self._explain_security_processing(
                security_result)
            steps.append(security_explanation)

        # Step 4: Optimization Processing
        if optimization_metrics:
            current_step += 1
            optimization_explanation = self._explain_optimization(
                optimization_metrics)
            steps.append(optimization_explanation)

        # Step 5: Performance Analysis
        if performance_metrics:
            current_step += 1
            performance_explanation = self._explain_performance(
                performance_metrics)
            steps.append(performance_explanation)

        # Generate summary
        summary = self._generate_summary(steps, processing_result)

        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(steps)

        explanation = ProcessingExplanation(
            session_id=session_id,
            total_processing_time_ms=(
                performance_metrics.get("total_pipeline_ms", 0.0)
                if performance_metrics
                else 0.0
            ),
            steps=steps,
            summary=summary,
            risk_assessment=risk_assessment or {},
            optimization_decisions=optimization_metrics or {},
            security_findings=security_result or {},
            confidence_score=confidence,
            human_readable_summary=self._generate_human_readable_summary(
                steps, processing_result
            ),
        )

        # Store explanation for later retrieval
        self.explanations[session_id] = explanation

        return explanation

    def _explain_input_analysis(
        self, processing_result: Dict[str, Any]
    ) -> ExplanationStep:
        """Explain input analysis step."""
        original_prompt = processing_result.get(
            "prompts", {}).get("original", "")

        return ExplanationStep(
            step_number=1,
            step_name="Input Analysis",
            description=f"Analyzed input prompt of {len(original_prompt)} characters",
            action_taken="Validated input and prepared for processing",
            reasoning=f"Input validation passed - prompt length: {len(original_prompt)}, content type: text",
            confidence=1.0,
            execution_time_ms=0.0,
            inputs={"original_prompt_length": len(original_prompt)},
            outputs={"validation_status": "passed"},
        )

    def _explain_mode_selection(
        self, risk_assessment: Dict[str, Any]
    ) -> ExplanationStep:
        """Explain mode selection step."""
        recommended_mode = risk_assessment.get("recommended_mode", "BALANCED")
        reasoning = risk_assessment.get(
            "auto_mode_reasoning", "Default balanced mode selected"
        )
        risk_score = risk_assessment.get("score", 0.0)
        confidence = risk_assessment.get("confidence", 0.8)

        return ExplanationStep(
            step_number=2,
            step_name="Mode Selection",
            description=f"Selected processing mode: {recommended_mode}",
            action_taken=f"Applied {recommended_mode} mode based on risk assessment",
            reasoning=reasoning,
            confidence=confidence,
            execution_time_ms=0.0,
            inputs={
                "risk_score": risk_score,
                "available_modes": ["STRICT", "BALANCED", "LITE", "AUTO", "OFF"],
            },
            outputs={
                "selected_mode": recommended_mode,
                "selection_confidence": confidence,
            },
        )

    def _explain_security_processing(
        self, security_result: Dict[str, Any]
    ) -> ExplanationStep:
        """Explain security processing step."""
        is_safe = security_result.get("is_safe", True)
        threats = security_result.get("detected_threats", [])
        masked_entities = security_result.get("masked_entities", {})
        threat_level = security_result.get("threat_level", "LOW")
        processing_time = security_result.get("processing_time_ms", 0.0)

        if is_safe:
            action_desc = "Content deemed safe, no threats detected"
            confidence = 0.9
        else:
            action_desc = f"Content blocked - {len(threats)} threats detected"
            confidence = 0.1

        return ExplanationStep(
            step_number=3,
            step_name="Security Processing",
            description=f"Security analysis completed with {len(threats)} threats and {len(masked_entities)} PII items",
            action_taken=action_desc,
            reasoning=f"Threat level: {threat_level}, PII masked: {len(masked_entities)} items",
            confidence=confidence,
            execution_time_ms=processing_time,
            inputs={
                "threats_detected": len(threats),
                "pii_items_found": len(masked_entities),
                "threat_level": threat_level,
            },
            outputs={
                "is_safe": is_safe,
                "threats_count": len(threats),
                "pii_masked_count": len(masked_entities),
            },
        )

    def _explain_optimization(
        self, optimization_metrics: Dict[str, Any]
    ) -> ExplanationStep:
        """Explain optimization step."""
        reduction_percentage = optimization_metrics.get(
            "token_reduction_percentage", 0.0
        )
        method = optimization_metrics.get("optimization_method", "unknown")
        source_length = optimization_metrics.get("source_length", 0)
        optimized_length = optimization_metrics.get("optimized_length", 0)
        execution_time = optimization_metrics.get("execution_time_ms", 0.0)

        if reduction_percentage > 0:
            action_desc = f"Optimized with {method} method, saved {reduction_percentage:.1f}% tokens"
            confidence = 0.8
        else:
            action_desc = f"No optimization applied - {method} method used"
            confidence = 0.6

        return ExplanationStep(
            step_number=4,
            step_name="Prompt Optimization",
            description=f"Optimization completed using {method} method",
            action_taken=action_desc,
            reasoning=f"Token reduction: {reduction_percentage:.1f}%, {source_length} → {optimized_length} characters",
            confidence=confidence,
            execution_time_ms=execution_time,
            inputs={"source_length": source_length,
                    "optimization_method": method},
            outputs={
                "token_reduction_percentage": reduction_percentage,
                "optimized_length": optimized_length,
                "optimization_method": method,
            },
        )

    def _explain_performance(
        self, performance_metrics: Dict[str, Any]
    ) -> ExplanationStep:
        """Explain performance analysis step."""
        total_time = performance_metrics.get("total_pipeline_ms", 0.0)
        security_time = performance_metrics.get("security_processing_ms", 0.0)
        optimization_time = performance_metrics.get("optimization_ms", 0.0)

        # Analyze performance
        if total_time > 100:
            performance_rating = "SLOW"
            confidence = 0.5
            recommendation = (
                "Consider increasing timeout or reducing processing complexity"
            )
        elif total_time > 50:
            performance_rating = "NORMAL"
            confidence = 0.8
            recommendation = "Performance within acceptable range"
        else:
            performance_rating = "FAST"
            confidence = 0.9
            recommendation = "Excellent performance, well within latency budget"

        return ExplanationStep(
            step_number=5,
            step_name="Performance Analysis",
            description=f"Performance analysis: {total_time:.1f}ms total processing time",
            action_taken=f"Rated performance as {performance_rating}",
            reasoning=f"Security: {security_time:.1f}ms, Optimization: {optimization_time:.1f}ms, Total: {total_time:.1f}ms",
            confidence=confidence,
            execution_time_ms=0.0,
            inputs={
                "total_time_ms": total_time,
                "security_time_ms": security_time,
                "optimization_time_ms": optimization_time,
            },
            outputs={
                "performance_rating": performance_rating,
                "recommendation": recommendation,
            },
        )

    def _calculate_overall_confidence(self, steps: List[ExplanationStep]) -> float:
        """Calculate overall confidence from all steps."""
        if not steps:
            return 0.0

        confidences = [
            step.confidence for step in steps if step.confidence > 0]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def _generate_summary(
        self, steps: List[ExplanationStep], processing_result: Dict[str, Any]
    ) -> str:
        """Generate technical summary of processing."""
        success = processing_result.get("success", False)

        if success:
            return f"Processing completed successfully in {len(steps)} steps"
        else:
            error = processing_result.get("error", "Unknown error")
            return f"Processing failed: {error}"

    def _generate_human_readable_summary(
        self, steps: List[ExplanationStep], processing_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable summary for non-technical users."""
        success = processing_result.get("success", False)

        if not success:
            error = processing_result.get("error", "Unknown error")
            return f"❌ Processing Failed: {error}"

        # Extract key metrics for summary
        optimization_metrics = processing_result.get(
            "optimization_metrics", {})
        reduction = optimization_metrics.get("token_reduction_percentage", 0)

        if reduction > 0:
            optimization_desc = f"✅ Saved {reduction:.1f}% tokens through optimization"
        else:
            optimization_desc = "ℹ️ No optimization applied"

        # Count security findings
        security_result = processing_result.get("security_result", {})
        threats = security_result.get("detected_threats", [])
        pii_count = len(security_result.get("masked_entities", {}))

        if threats:
            security_desc = f"🔒 Blocked {len(threats)} security threats"
        elif pii_count > 0:
            security_desc = f"🔐 Protected {pii_count} PII items"
        else:
            security_desc = "✅ No security issues found"

        # Performance summary
        performance_metrics = processing_result.get("performance_metrics", {})
        total_time = performance_metrics.get("total_pipeline_ms", 0)

        if total_time < 50:
            performance_desc = f"⚡ Fast processing ({total_time:.0f}ms)"
        elif total_time < 100:
            performance_desc = f"⏱️ Normal processing ({total_time:.0f}ms)"
        else:
            performance_desc = f"🐌 Slow processing ({total_time:.0f}ms)"

        return f"""
PrivySHA Processing Summary
========================

{security_desc}
{optimization_desc}
{performance_desc}

📊 Session: {processing_result.get('session_id', 'unknown')}
🎯 Result: {'Success' if success else 'Failed'}

Key Steps:
{chr(10).join(f"{i}. {step.step_name}: {step.description}" for i, step in enumerate(steps, 1))}

💡 For detailed technical information, use debug mode.
        """.strip()

    def get_explanation(self, session_id: str) -> Optional[ProcessingExplanation]:
        """Retrieve explanation for a specific session."""
        return self.explanations.get(session_id)

    def get_all_explanations(self) -> Dict[str, ProcessingExplanation]:
        """Get all stored explanations."""
        return self.explanations.copy()

    def clear_explanations(self) -> None:
        """Clear all stored explanations."""
        self.explanations.clear()

    def export_explanation(self, session_id: str, format_type: str = "json") -> str:
        """Export explanation in specified format."""
        explanation = self.get_explanation(session_id)
        if not explanation:
            return "No explanation found for session"

        if format_type.lower() == "json":
            return json.dumps(
                {
                    "session_id": explanation.session_id,
                    "total_processing_time_ms": explanation.total_processing_time_ms,
                    "confidence_score": explanation.confidence_score,
                    "summary": explanation.summary,
                    "steps": [
                        {
                            "step_number": step.step_number,
                            "step_name": step.step_name,
                            "description": step.description,
                            "action_taken": step.action_taken,
                            "reasoning": step.reasoning,
                            "confidence": step.confidence,
                            "execution_time_ms": step.execution_time_ms,
                            "inputs": step.inputs,
                            "outputs": step.outputs,
                        }
                        for step in explanation.steps
                    ],
                    "human_readable_summary": explanation.human_readable_summary,
                },
                indent=2,
            )

        elif format_type.lower() == "text":
            result = f"Session ID: {explanation.session_id}\n"
            result += (
                f"Total Processing Time: {explanation.total_processing_time_ms:.1f}ms\n"
            )
            result += f"Overall Confidence: {explanation.confidence_score:.2f}\n"
            result += f"Summary: {explanation.summary}\n\n"
            result += "Processing Steps:\n"
            for step in explanation.steps:
                result += f"{step.step_number}. {step.step_name}\n"
                result += f"   Description: {step.description}\n"
                result += f"   Action: {step.action_taken}\n"
                result += f"   Reasoning: {step.reasoning}\n"
                result += f"   Confidence: {step.confidence:.2f}\n"
                result += f"   Time: {step.execution_time_ms:.1f}ms\n\n"

            return result

        else:
            return "Unsupported format. Use 'json' or 'text'"
