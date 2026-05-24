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
Drop-in utility functions (NEW - CRITICAL FOR ADOPTION)
from .dropin import process, wrap_llm, optimize, sanitize
from .auto_patch import auto_patch, get_patch_status, disable_auto_patch, enable_auto_patch

These functions provide the CRITICAL adoption path:
- process() - One-line prompt processing
- wrap_llm() - Wrap any LLM client
- optimize() - Token optimization only
- sanitize() - Security only

This is the "non-invasive augmentation layer" that makes PrivySHA
feel like a utility, not a system replacement.
"""

from typing import Dict, Any, Union, Optional

from ..adapters.factory import AdapterFactory
from ..security.security_layer import SecurityLevel
from ..core.async_pipeline import process_async as _process_async
from .wrapper import wrap_llm as _wrap_llm
from .dropin_privacy import (
    security_field as _security_field,
    finalize_privacy_output as _finalize_privacy_output,
    privacy_fallback as _privacy_fallback,
    extract_pii_types as _extract_pii_types,
    build_security_summary as _build_security_summary,
    masked_entity_count as _masked_entity_count,
    get_sanitized_content as _get_sanitized_content,
)
from .metrics_hook import record_process_metrics
import difflib


def _normalize_security_level(level: Union[str, SecurityLevel]) -> str:
    """Convert security level input to pipeline config string (e.g. 'MEDIUM')."""
    if isinstance(level, SecurityLevel):
        return level.name
    return str(level).upper()


def _coerce_process_output(processed: Any, fallback: str) -> str:
    """Normalize process() return value to a prompt string."""
    if isinstance(processed, str):
        return processed
    if isinstance(processed, dict):
        if processed.get("optimized"):
            return str(processed["optimized"])
        prompts = processed.get("prompts", {})
        if isinstance(prompts, dict) and prompts.get("optimized"):
            return str(prompts["optimized"])
    return fallback


def apply_stage_processing(
    prompt: str,
    token_budget: int,
    context_config: Optional[Dict[str, Any]],
    verbose: bool,
) -> str:
    """
    Apply enhanced stage-based processing to prompt using the modular pipeline.

    Args:
        prompt: Input prompt to process
        token_budget: Token budget for optimization
        context_config: Configuration for context injection
        verbose: Enable verbose logging

    Returns:
        Processed prompt string
    """
    try:
        from ..pipeline.pipeline import Pipeline

        # Initialize the modular pipeline
        pipeline = Pipeline(
            token_budget=token_budget,
            debug_enabled=verbose,
            policy_config=(
                {"context_config": context_config} if context_config else None
            ),
        )

        # Process the prompt
        result = pipeline.process(prompt)

        if result.get("success", False):
            return result.get("prompts", {}).get("optimized", prompt)

        return prompt

    except Exception as e:
        if verbose:
            print(f"[STAGES] Modular pipeline processing failed: {e}")
        # Fail-safe: return original prompt
        return prompt


def generate_text_diff(original: str, modified: str) -> str:
    """Generate a readable diff between original and modified text."""
    if original == modified:
        return "No changes made"

    # Generate unified diff
    diff_lines = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            modified.splitlines(keepends=True),
            fromfile="original",
            tofile="modified",
            lineterm="",
        )
    )

    if not diff_lines:
        return "No changes made"

    return "\n".join(diff_lines)


def process(
    prompt: str,
    privacy: bool = True,
    token_budget: int = 1200,
    return_metrics: bool = False,
    debug: bool = False,
    security_level: str = "medium",
    verbose: bool = False,
    use_stages: bool = False,
    context_config: Optional[Dict[str, Any]] = None,
    debug_mode: bool = False,
    mode: str = "balanced",
    pii_mode: str = "rule",
    reversible: bool = False,
    security_fail_closed: bool = False,
    # Observability parameters
    trace: bool = False,
    log_level: str = "INFO",
    log_output: str = "console",
    log_file: Optional[str] = None,
    # Reliability parameters
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Process a prompt through PrivySHA optimization pipeline.

    This is the PRIMARY drop-in function for adoption.

    Args:
        prompt: Input prompt to process
        privacy: Enable privacy features (default: True)
        token_budget: Token budget for optimization (default: 1200)
        return_metrics: Return optimization metrics (default: False)
        debug: Enable detailed debug metrics (default: False)
        security_level: Security level - "low", "medium", "high" (default: "medium")
        verbose: Enable logging output (default: False - silent for production)
        use_stages: Enable enhanced stage-based processing (default: False)
        context_config: Configuration for context injection (default: None)
        debug_mode: Enable comprehensive debugging with PrivySHADebugger (default: False)
        mode: Policy mode - "strict", "balanced", "lite", "off" (default: "balanced")
        pii_mode: PII detection mode - "rule", "hybrid", "ml_only" (default: "rule")
                  - "rule": Rule-based only (lightweight, no downloads)
                  - "hybrid": Rules + ML (requires pip install privysha[ml])
                  - "ml_only": ML only (experimental, requires pip install privysha[ml])
        trace: Enable detailed stage tracing (default: False)
        log_level: Logging level - "ERROR", "WARN", "INFO", "DEBUG" (default: "INFO")
        log_output: Output destination - "console", "file", "json" (default: "console")
        log_file: Log file path (if log_output="file") (default: None)

    Returns:
        Optimized prompt string or dict with metrics

    Examples:
        >>> from privysha import process
        >>> result = process("Hey bro analyze dataset with john@email.com")
        >>> print(result)
        "Analyze dataset for anomalies (PII masked)"

        >>> # With enhanced stages
        >>> result = process("Analyze data", use_stages=True,
        ...                context_config={"role": "data scientist"})
        >>> print(result)
        "Analyze data for insights (with context injection)"

        >>> # With ML-enhanced PII detection (requires pip install privysha[ml])
        >>> result = process("Contact john@email.com for details", pii_mode="hybrid")
        >>> print(result)
        "Contact [HASHED_EMAIL] for details"

        >>> # With metrics
        >>> result = process("prompt", return_metrics=True)
        >>> print(result["optimized"])
        >>> print(result["token_reduction"])

        >>> # With debug metrics (THE ADDICTIVE PART!)
        >>> result = process("prompt", debug=True)
        >>> print(result.metrics)
        {
            "tokens_saved": 32,
            "cost_reduction": "18%",
            "pii_detected": ["email"],
            "risk_level": "low"
        }

        >>> # With observability tracing (NEW!)
        >>> result = process("Contact john@email.com", trace=True, debug=True)
        >>> print(result["trace"]["final_output"])
        "Contact [EMAIL]_x92k"
        >>> print(result["diff"])
        - Contact john@email.com
        + Contact [EMAIL]_x92k

        >>> # With structured logging
        >>> result = process("Analyze data", trace=True, log_level="DEBUG",
        ...                log_output="json", log_file="privysha.log")
        >>> print(result["metrics"])
        {
            "total_latency_ms": 12.4,
            "stages_run": 4,
            "tokens_saved": 5,
            "pii_detected": 1,
            "changes_made": 2,
            "errors": 0
        }
    """
    if not prompt or not isinstance(prompt, str):
        if return_metrics or debug:
            return {
                "optimized": "",
                "original": prompt or "",
                "token_reduction": 0,
                "security_result": {"is_safe": False, "error": "Invalid prompt"},
                "error": "Invalid prompt input",
                "metrics": {
                    "tokens_saved": 0,
                    "cost_reduction": "0%",
                    "pii_detected": [],
                    "risk_level": "high",
                    "threats_blocked": 0,
                    "processing_time_ms": 0,
                },
            }
        return ""

    try:
        # Initialize debugger if debug mode is enabled
        debugger = None
        if debug_mode:
            from ..debug.debugger import PrivySHADebugger

            debugger = PrivySHADebugger()
            debugger.start_session(prompt)
            if verbose:
                print("[DEBUG] Started comprehensive debugging session")

        # Enhanced stage-based processing if enabled
        if use_stages:
            if debugger:
                debugger.add_stage(
                    "stage_processing", prompt, "Applying stage-based processing"
                )
            prompt = apply_stage_processing(
                prompt, token_budget, context_config, verbose
            )
            if debugger:
                debugger.complete_stage("stage_processing", prompt)

        if debugger:
            debugger.add_stage("pipeline_processing", prompt,
                               "Starting main pipeline")

        # Create policy configuration from mode
        from ..core.policy_config import PolicyConfig, PolicyMode

        if mode.lower() == "off":
            policy_config = PolicyConfig.from_mode(PolicyMode.OFF)
            privacy = False
        elif mode.lower() == "strict":
            policy_config = PolicyConfig.from_mode(PolicyMode.STRICT)
        elif mode.lower() == "lite":
            policy_config = PolicyConfig.from_mode(PolicyMode.LITE)
        else:  # balanced (default)
            policy_config = PolicyConfig.from_mode(PolicyMode.BALANCED)

        policy_config.security_fail_closed = security_fail_closed

        # Override with legacy parameters if provided
        if not privacy:
            policy_config.pii_masking = False
            policy_config.enable_pii_detection = False
        if debug_mode or debug:
            policy_config.debug_diff = True

        # Validate pii_mode
        from ..core.ml_utils import validate_pii_mode, check_pii_mode_feasibility

        pii_mode = validate_pii_mode(pii_mode)

        # Check if pii_mode is feasible
        feasibility = check_pii_mode_feasibility(pii_mode)
        if not feasibility["feasible"]:
            if feasibility["requires_ml"]:
                # Graceful fallback to rule-based mode with warning
                if verbose:
                    print(
                        f"Warning: {feasibility['installation_instructions']}")
                    print("Falling back to rule-based PII detection")
                pii_mode = "rule"
            else:
                raise ValueError(
                    f"Invalid PII mode '{mode}'. Valid modes: 'rule', 'hybrid', 'ml_only'. "
                    f"ML mode requires: pip install privysha[ml]"
                )

        from ..pipeline.pipeline import Pipeline

        # Create pipeline with policy configuration and pii_mode
        pipeline = Pipeline(
            privacy=privacy,
            token_budget=token_budget,
            security_level=_normalize_security_level(security_level),
            debug_enabled=debug or debug_mode,
            fallback_mode=True,
            policy_config=policy_config,
            pii_mode=pii_mode,
            reversible=reversible,
        )

        def _run_pipeline() -> Any:
            return pipeline.process(
                content=prompt,
                trace=trace,
                log_level=log_level,
                debug=debug or debug_mode,
                log_output=log_output,
                log_file=log_file,
            )

        # Retry + timeout support
        import concurrent.futures as _cf

        _last_exc: Optional[Exception] = None
        result = None
        for _attempt in range(max_retries + 1):
            try:
                if timeout_seconds is not None:
                    with _cf.ThreadPoolExecutor(max_workers=1) as _pool:
                        _future = _pool.submit(_run_pipeline)
                        try:
                            result = _future.result(timeout=timeout_seconds)
                        except _cf.TimeoutError:
                            raise TimeoutError(
                                f"process() timed out after {timeout_seconds}s"
                            )
                else:
                    result = _run_pipeline()
                break
            except TimeoutError:
                raise  # never retry on timeout
            except Exception as _exc:
                _last_exc = _exc
                if _attempt == max_retries:
                    raise
                if verbose:
                    print(
                        f"[PrivySHA] process() attempt {_attempt + 1} failed "
                        f"({type(_exc).__name__}), retrying..."
                    )

        if debugger:
            debugger.complete_stage(
                "pipeline_processing", result.get(
                    "prompts", {}).get("optimized", "")
            )

        # Use pipeline output when prompts are available even if success=False
        prompts = result.get("prompts", {})
        optimized = prompts.get("optimized") or prompts.get("sanitized") or prompt
        if not result.get("success", True) and not optimized:
            raise Exception("Pipeline processing failed")

        # Calculate enhanced metrics for the "oh sh*t" moment
        original_tokens = len(prompt.split()) * 1.3  # Rough estimate
        optimized_tokens = len(optimized.split()) * 1.3
        tokens_saved = int(original_tokens - optimized_tokens)

        # Calculate cost reduction using real-world token pricing
        # Current pricing (as of 2026):
        # GPT-4o: $0.005/1K input, $0.015/1K output
        # GPT-3.5-turbo: $0.001/1K input, $0.002/1K output
        # Claude-3.5-sonnet: $0.003/1K input, $0.015/1K output
        # Gemini-1.5-flash: $0.000075/1K input, $0.0003/1K output
        # Gemini-1.5-pro: $0.0025/1K input, $0.01/1K output

        # Use Gemini pricing as default (most cost-effective)
        input_cost_per_1k = 0.000075  # Gemini-1.5-flash input
        output_cost_per_1k = 0.0003  # Gemini-1.5-flash output

        # For prompt optimization, we'll use input pricing
        original_cost = (original_tokens / 1000) * input_cost_per_1k
        optimized_cost = (optimized_tokens / 1000) * input_cost_per_1k
        cost_reduction_percentage = (
            ((original_cost - optimized_cost) / original_cost) * 100
            if original_cost > 0
            else 0
        )

        # Extract PII types from security result or detect from processed output
        security_result = result.get("security_result")
        pii_enabled = privacy and policy_config.pii_masking
        pii_types = _extract_pii_types(
            security_result, prompt, pii_enabled, processed_text=optimized
        )

        # Calculate risk level
        detected_threats = _security_field(security_result, "detected_threats", []) or []
        threats_count = len(detected_threats)
        if threats_count > 2:
            risk_level = "high"
        elif threats_count > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Calculate processing time
        processing_time = result.get("performance_metrics", {}).get(
            "total_pipeline_ms", 0
        )

        enhanced_metrics = {
            "tokens_saved": tokens_saved,
            "cost_reduction": f"{cost_reduction_percentage:.1f}%",
            "pii_detected": pii_types,
            "risk_level": risk_level,
            "threats_blocked": threats_count,
            "processing_time_ms": processing_time,
            "token_reduction_percentage": result["optimization_metrics"].get(
                "token_reduction_percentage", 0
            ),
            "security_score": 100 - (threats_count * 10),  # Simple scoring
            "optimization_score": min(
                100,
                result["optimization_metrics"].get(
                    "token_reduction_percentage", 0) * 2,
            ),
        }
        masking_map = _security_field(security_result, "masking_map", {}) or {}
        if reversible and privacy and not masking_map:
            from ..security.service import run_security_only

            vault_result = run_security_only(
                prompt, security_level=SecurityLevel.MEDIUM, reversible=True
            )
            masking_map = vault_result.masking_map or {}
        if reversible and masking_map:
            enhanced_metrics["masking_map"] = masking_map

        # Warn when the optimizer rewrites a prompt that had no PII and no threats.
        # This surprises users who expect clean prompts to pass through unchanged.
        if (
            verbose
            and optimized != prompt
            and not pii_types
            and threats_count == 0
            and mode not in ("off",)
        ):
            import warnings as _warnings
            _warnings.warn(
                "process() rewrote a prompt that contained no PII and no threats. "
                "To opt out of optimization for safe prompts use mode='off' or "
                "pass trust_input=True to optimize().",
                UserWarning,
                stacklevel=2,
            )

        if return_metrics or debug:
            response = {
                "optimized": _finalize_privacy_output(result, privacy),
                "original": result["prompts"]["original"],
                "token_reduction": result["optimization_metrics"].get(
                    "token_reduction_percentage", 0
                ),
                "security_result": _build_security_summary(security_result),
                "performance_metrics": result["performance_metrics"],
                "metrics": enhanced_metrics,
            }
            if reversible and masking_map:
                response["masking_map"] = masking_map

            if debug:
                # Add even more detailed debug info
                response["debug"] = {
                    "pipeline_stages": [
                        {
                            "stage": "ir_generation",
                            "time_ms": result["performance_metrics"].get(
                                "ir_generation_ms", 0
                            ),
                            "success": True,
                        },
                        {
                            "stage": "security_processing",
                            "time_ms": result["performance_metrics"].get(
                                "security_processing_ms", 0
                            ),
                            "success": _security_field(security_result, "is_safe", True),
                        },
                        {
                            "stage": "prompt_optimization",
                            "time_ms": result["performance_metrics"].get(
                                "optimization_ms", 0
                            ),
                            "success": True,
                        },
                    ],
                    "model_routing": result.get("routing_decision", {}),
                    "session_id": result.get("session_id", "unknown"),
                }

            # Add comprehensive debug trace if debugger was used
            if debugger:
                debugger.end_session(result["prompts"]["optimized"])
                debug_trace = debugger.get_trace()
                response["comprehensive_debug"] = {
                    "session_id": debug_trace.session_id,
                    "total_execution_time_ms": debug_trace.total_execution_time_ms,
                    "stages": [
                        {
                            "stage_name": stage.stage_name,
                            "execution_time_ms": stage.execution_time_ms,
                            "success": stage.success,
                            "input_length": len(stage.input_data),
                            "output_length": len(stage.output_data),
                        }
                        for stage in debug_trace.stages
                    ],
                    "token_metrics": debug_trace.token_metrics,
                    "final_response": debug_trace.final_response,
                }

            # Add observability trace if available
            if trace or debug or log_level != "INFO":
                if "trace" in result:
                    response["trace"] = result["trace"]
                if "metrics" in result:
                    response["pipeline_metrics"] = result["metrics"]
                if "diff" in result and result["diff"]:
                    response["diff"] = result["diff"]

            return response

        return _finalize_privacy_output(result, privacy)

    except Exception as e:
        # Fallback: still mask PII when privacy is enabled
        fallback = _privacy_fallback(
            prompt, privacy, security_fail_closed=security_fail_closed
        )
        record_process_metrics(
            prompt=prompt,
            optimized=fallback,
            latency_ms=0,
            success=False,
            tokens_saved=0,
            threats_blocked=0,
            pii_detected=_extract_pii_types(None, prompt, privacy),
        )
        if return_metrics or debug:
            pii_types = _extract_pii_types(None, prompt, privacy)
            response = {
                "optimized": fallback,
                "original": prompt,
                "token_reduction": 0,
                "security_result": {
                    "is_safe": True,
                    "error": str(e),
                    "masked_entities": {},
                    "pii_detected": pii_types,
                },
                "error": "Pipeline processing failed",
                "errors": ["pipeline_processing_failed"],
                "metrics": {
                    "tokens_saved": 0,
                    "cost_reduction": "0%",
                    "pii_detected": pii_types,
                    "risk_level": "medium",
                    "threats_blocked": 0,
                    "processing_time_ms": 0,
                },
            }
            if debug:
                response["fallback_reason"] = "pipeline_processing_failed"
                response["original_error"] = {
                    "type": type(e).__name__,
                    "message": str(e),
                }
            return response
        return fallback


# Async support functions
async def process_async(
    prompt: str,
    privacy: bool = True,
    token_budget: int = 1200,
    return_metrics: bool = False,
    debug: bool = False,
    security_level: str = "medium",
    security_fail_closed: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Async version of process function.

    Args:
        prompt: Input prompt to process
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        return_metrics: Return optimization metrics
        debug: Enable detailed debug metrics
        security_level: Security level

    Returns:
        Optimized prompt string or dict with metrics
    """
    if not prompt or not isinstance(prompt, str):
        if return_metrics or debug:
            return {
                "optimized": "",
                "original": prompt or "",
                "token_reduction": 0,
                "security_result": {"is_safe": False, "error": "Invalid prompt"},
                "error": "Invalid prompt input",
                "metrics": {"pii_detected": []},
                "async": True,
            }
        return ""

    try:
        result = await _process_async(
            prompt, privacy=privacy, token_budget=token_budget
        )

        # Use pipeline output when available (tolerate success=False with usable prompts)
        prompts = result.get("prompts", {})
        optimized = prompts.get("optimized") or prompts.get("sanitized") or prompt
        if not result.get("success", True) and not optimized:
            raise Exception("Async pipeline processing failed")

        if return_metrics or debug:
            return {
                "optimized": optimized,
                "original": prompts.get("original", prompt),
                "token_reduction": result.get("optimization_metrics", {}).get(
                    "token_reduction_percentage", 0
                ),
                "security_result": _build_security_summary(
                    result.get("security_result")
                ),
                "performance_metrics": result.get("performance_metrics", {}),
                "metrics": {
                    "pii_detected": _extract_pii_types(
                        result.get("security_result"), prompt, privacy
                    ),
                },
                "async": True,
            }

        return optimized

    except Exception:
        fallback = _privacy_fallback(
            prompt, privacy, security_fail_closed=security_fail_closed
        )
        record_process_metrics(
            prompt=prompt,
            optimized=fallback,
            latency_ms=0,
            success=False,
            pii_detected=_extract_pii_types(None, prompt, privacy),
        )
        if return_metrics or debug:
            pii_types = _extract_pii_types(None, prompt, privacy)
            return {
                "optimized": fallback,
                "original": prompt,
                "token_reduction": 0,
                "security_result": {
                    "is_safe": True,
                    "error": "Async processing failed",
                    "masked_entities": {},
                    "pii_detected": pii_types,
                },
                "error": "Async processing failed",
                "metrics": {"pii_detected": pii_types},
                "async": True,
                "fallback": True,
            }
        return fallback


async def optimize_async(
    prompt: str,
    token_budget: int = 1200,
    return_metrics: bool = False,
    privacy_mode: str = "strict",
    trust_input: bool = False,
    debug: bool = False,
) -> Union[str, Dict[str, Any]]:
    try:
        if trust_input:
            optimized = prompt
            token_reduction = 0.0
            pii_masked = False
        else:
            privacy = privacy_mode != "off"
            result = await _process_async(
                prompt, privacy=privacy, token_budget=token_budget
            )
            prompts = result.get("prompts", {})
            optimized = prompts.get("optimized") or prompts.get("sanitized") or prompt
            token_reduction = result.get("optimization_metrics", {}).get(
                "token_reduction_percentage", 0
            )
            pii_masked = _masked_entity_count(result.get("security_result")) > 0

        response_data = {
            "optimized": optimized,
            "original": prompt,
            "token_reduction": token_reduction,
            "pii_masked": pii_masked,
            "privacy_mode": privacy_mode,
            "trust_input": trust_input,
            "async": True,
        }

        return response_data if return_metrics or debug else optimized

    except Exception:
        fallback = _privacy_fallback(prompt, privacy_mode != "off")
        if return_metrics or debug:
            return {
                "optimized": fallback,
                "original": prompt,
                "token_reduction": 0,
                "pii_masked": False,
                "privacy_mode": privacy_mode,
                "trust_input": trust_input,
                "async": True,
                "fallback": True,
            }
        return fallback


async def sanitize_async(
    prompt: str, return_details: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    Async version of sanitize function.

    Args:
        prompt: Input prompt to sanitize
        return_details: Return security analysis details

    Returns:
        Sanitized prompt string or dict with security details
    """
    import asyncio
    from functools import partial

    from ..security.service import run_security_only

    try:
        loop = asyncio.get_event_loop()
        security_result = await loop.run_in_executor(
            None,
            partial(run_security_only, prompt, security_level=SecurityLevel.HIGH),
        )
        sanitized = security_result.sanitized_content

        if return_details:
            summary = _build_security_summary(security_result)
            return {
                "sanitized": sanitized,
                "original": prompt,
                "is_safe": summary["is_safe"],
                "threats": summary["threats"],
                "masked_entities": summary["masked_entities"],
                "pii_detected": _extract_pii_types(security_result, prompt, True),
                "async": True,
            }

        return sanitized

    except Exception:
        # FAIL-SAFE: Return original prompt
        if return_details:
            return {
                "sanitized": prompt,
                "original": prompt,
                "is_safe": True,
                "threats": [],
                "masked_entities": {},
                "async": True,
                "fallback": True,
            }
        return prompt


def wrap_llm(
    client: Any,
    privacy: bool = True,
    token_budget: int = 1200,
    auto_detect: bool = True,
    mode: str = "balanced",
) -> Any:
    """
    Wrap any LLM client with PrivySHA security and optimization.

    This is the CRITICAL wrapper function for existing systems.
    Now supports async, streaming, and fail-safe execution.

    Args:
        client: Any LLM client (OpenAI, Anthropic, etc.)
        privacy: Enable privacy features (default: True)
        token_budget: Token budget for optimization (default: 1200)
        auto_detect: Auto-detect client type (default: True)
        mode: Processing mode ("balanced", "strict", "lite", "auto")

    Returns:
        Wrapped client with same interface

    Examples:
        >>> from privysha import wrap_llm
        >>> import openai
        >>> client = openai.OpenAI()
        >>> secure_client = wrap_llm(client)
        >>> response = secure_client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Hey bro analyze with john@email.com"}]
        ... )

        >>> # Streaming support
        >>> response = secure_client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Analyze this"}],
        ...     stream=True
        ... )
        >>> for chunk in response:
        ...     print(chunk)

        >>> # Async support
        >>> async def main():
        ...     response = await secure_client.chat.completions.acreate(
        ...         messages=[{"role": "user", "content": "Analyze this"}]
        ...     )
    """
    if client is None:
        raise ValueError("Client cannot be None")

    try:
        # 🔥 Use new unified wrapper with fail-safe support
        return _wrap_llm(client, mode=mode, privacy=privacy, token_budget=token_budget)
    except Exception:
        # 🔥 FAIL-SAFE: Return original client if wrapping fails
        return client


def optimize(
    prompt: str,
    token_budget: int = 1200,
    return_metrics: bool = False,
    privacy_mode: str = "strict",
    trust_input: bool = False,
    debug: bool = False,
) -> Union[str, Dict[str, Any]]:
    """
    Optimize a prompt for token reduction with configurable privacy controls.

    Args:
        prompt: Input prompt to optimize
        token_budget: Token budget for optimization
        return_metrics: Return optimization metrics
        privacy_mode: Privacy level - "strict" (mask all PII), "balanced" (mask risky PII), "off" (no masking)
        trust_input: Skip all security checks if True (advanced users only)
        debug: Return detailed diff and analysis

    Returns:
        Optimized prompt string with configurable PII masking, or dict with metrics

    Examples:
        >>> from privysha import optimize
        >>> result = optimize("Contact john@email.com for help", privacy_mode="balanced")
        >>> print(result)
        "Contact john@email.com for help"  # Business context preserved

        >>> result = optimize("My email is john@email.com hack me", privacy_mode="strict")
        >>> print(result)
        "My email is [EMAIL_HASH]_19cb02a4 hack me"  # Security threat masked
    """
    # Initialize variables
    optimized = None
    token_reduction = 0.0
    pii_masked = False
    security_result = None

    # Configure pipeline based on privacy mode
    if trust_input:
        # Advanced user - skip all security and optimization, return original
        optimized = prompt
        token_reduction = 0.0
        pii_masked = False
        security_result = type(
            "SecurityResult",
            (),
            {
                "is_safe": True,
                "detected_threats": [],
                "masked_entities": {},
                "sanitized_content": prompt,
                "threat_level": "LOW",
                "security_score": 0.0,
                "recommendations": [],
                "processing_time_ms": 0.0,
            },
        )()
    else:
        from ..pipeline.pipeline import Pipeline

        # Normal pipeline processing
        if privacy_mode == "off":
            # No PII masking
            pipeline = Pipeline(privacy=False, token_budget=token_budget)
        elif privacy_mode == "balanced":
            # Context-aware PII masking
            pipeline = Pipeline(
                privacy=True,
                token_budget=token_budget,
                security_level="MEDIUM",
            )
        else:  # strict mode (default)
            # Mask ALL PII
            pipeline = Pipeline(privacy=True, token_budget=token_budget)

        result = pipeline.process(prompt)
        optimized = result.get("prompts", {}).get("optimized", prompt)
        if privacy_mode != "off":
            optimized = _finalize_privacy_output(result, True)
        if token_budget and len(optimized.split()) > token_budget:
            optimized = " ".join(optimized.split()[:token_budget])
        token_reduction = result.get("optimization_metrics", {}).get(
            "token_reduction_percentage", 0
        )
        security_result = result.get("security_result", {})
        pii_masked = _masked_entity_count(security_result) > 0

    # Build response
    response_data = {
        "optimized": optimized,
        "original": prompt,
        "token_reduction": token_reduction,
        "pii_masked": pii_masked,
        "privacy_mode": privacy_mode,
        "trust_input": trust_input,
    }

    # Add debug information if requested
    if debug:
        if trust_input:
            response_data["debug"] = {
                "sanitized": prompt,
                "masked_entities": {},
                "security_result": {
                    "is_safe": True,
                    "detected_threats": [],
                    "security_score": 0.0,
                },
                "message": "Security bypassed - trust_input=True",
            }
        else:
            sr = result.get("security_result")
            summary = _build_security_summary(sr)
            response_data["debug"] = {
                "sanitized": result.get("prompts", {}).get("sanitized", prompt),
                "masked_entities": summary["masked_entities"],
                "security_result": {
                    "is_safe": summary["is_safe"],
                    "detected_threats": summary["threats"],
                    "security_score": summary["security_score"],
                },
            }

        # Generate diff
        if prompt != optimized:
            response_data["diff"] = generate_text_diff(prompt, optimized)
        else:
            response_data["diff"] = "No changes made"

    return response_data if return_metrics or debug else optimized


def sanitize(
    prompt: str,
    return_details: bool = False,
    reversible: bool = False,
    security_fail_closed: bool = False,
    max_retries: int = 0,
    timeout_seconds: Optional[float] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Sanitize a prompt for security only (PII masking, threat detection).

    Args:
        prompt: Input prompt to sanitize
        return_details: Return security analysis details

    Returns:
        Sanitized prompt string or dict with security details

    Examples:
        >>> from privysha import sanitize
        >>> result = sanitize("Contact john@email.com for analysis")
        >>> print(result)
        "Contact [EMAIL] for analysis"
    """
    from ..security.service import run_security_only
    from ..utils.dropin_privacy import SECURITY_FAIL_CLOSED_PLACEHOLDER
    import concurrent.futures as _cf

    def _run_security() -> Any:
        return run_security_only(
            prompt, security_level=SecurityLevel.HIGH, reversible=reversible
        )

    try:
        _last_exc: Optional[Exception] = None
        security_result = None
        for _attempt in range(max_retries + 1):
            try:
                if timeout_seconds is not None:
                    with _cf.ThreadPoolExecutor(max_workers=1) as _pool:
                        _future = _pool.submit(_run_security)
                        try:
                            security_result = _future.result(timeout=timeout_seconds)
                        except _cf.TimeoutError:
                            raise TimeoutError(
                                f"sanitize() timed out after {timeout_seconds}s"
                            )
                else:
                    security_result = _run_security()
                break
            except TimeoutError:
                raise
            except Exception as _exc:
                _last_exc = _exc
                if _attempt == max_retries:
                    raise
    except Exception:
        if security_fail_closed:
            if return_details:
                return {
                    "sanitized": SECURITY_FAIL_CLOSED_PLACEHOLDER,
                    "original": prompt,
                    "is_safe": False,
                    "threats": [],
                    "masked_entities": {},
                    "pii_detected": [],
                    "fail_closed": True,
                }
            return SECURITY_FAIL_CLOSED_PLACEHOLDER
        if return_details:
            return {
                "sanitized": prompt,
                "original": prompt,
                "is_safe": True,
                "threats": [],
                "masked_entities": {},
                "pii_detected": [],
                "fallback": True,
            }
        return prompt

    if return_details:
        summary = _build_security_summary(security_result)
        details = {
            "sanitized": summary["sanitized_content"],
            "original": prompt,
            "is_safe": summary["is_safe"],
            "threats": summary["threats"],
            "masked_entities": summary["masked_entities"],
            "pii_detected": _extract_pii_types(security_result, prompt, True),
        }
        if reversible and security_result.masking_map:
            details["masking_map"] = security_result.masking_map
        return details

    return _get_sanitized_content(security_result, prompt)


class SecureLLMWrapper:
    """
    Wrapper that makes any LLM client secure and optimized.

    This wrapper maintains the exact same interface as the original client
    but adds PrivySHA processing automatically.
    """

    def __init__(
        self,
        client: Any,
        privacy: bool = True,
        token_budget: int = 1200,
        auto_detect: bool = True,
    ) -> None:
        if client is None:
            raise ValueError("Client cannot be None")

        self.client = client
        self.privacy = privacy
        self.token_budget = token_budget
        self.auto_detect = auto_detect
        self.client_type = self._detect_client_type() if auto_detect else "unknown"

        # Initialize pipeline with error handling
        try:
            from ..pipeline.pipeline import Pipeline

            self.pipeline = Pipeline(
                privacy=privacy, token_budget=token_budget)
        except Exception as e:
            # Fallback: create minimal pipeline
            self.pipeline = None
            self._pipeline_error = str(e)

    def _detect_client_type(self) -> str:
        """Detect the type of LLM client."""
        client_class = self.client.__class__.__module__.lower()
        client_name = self.client.__class__.__name__.lower()

        if "openai" in client_class or "openai" in client_name:
            return "openai"
        elif "anthropic" in client_class or "anthropic" in client_name:
            return "anthropic"
        elif "grok" in client_class or "xai" in client_class:
            return "grok"
        elif (
            "gemini" in client_class
            or "google" in client_class
            or "generativeai" in client_class
        ):
            return "gemini"
        elif "huggingface" in client_class or "transformers" in client_class:
            return "huggingface"
        elif "ollama" in client_class:
            return "ollama"
        else:
            return "unknown"

    def __getattr__(self, name):
        """Delegate all other method calls to the original client."""
        try:
            attr = getattr(self.client, name)
            if callable(attr):
                # If it's a method, wrap it to process prompts
                def wrapped_method(*args, **kwargs):
                    # Extract prompt from arguments based on client type
                    prompt = self._extract_prompt_from_args(args, kwargs)
                    if prompt:
                        # Process prompt through PrivySHA
                        if self.pipeline:
                            processed = self.pipeline.process(prompt)
                            optimized_prompt = processed["prompts"]["optimized"]
                            # Replace prompt in args
                            args = self._replace_prompt_in_args(
                                args, optimized_prompt)
                    # Call original method
                    return attr(*args, **kwargs)

                return wrapped_method
            else:
                return attr
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __call__(self, *args, **kwargs):
        """Make the wrapper callable."""
        if hasattr(self.client, "__call__"):
            # Extract prompt from arguments
            prompt = self._extract_prompt_from_args(args, kwargs)
            if prompt:
                # Process prompt through PrivySHA
                if self.pipeline:
                    processed = self.pipeline.process(prompt)
                    optimized_prompt = processed["prompts"]["optimized"]
                    # Replace prompt in args
                    args = self._replace_prompt_in_args(args, optimized_prompt)
            # Call original client
            return self.client(*args, **kwargs)
        else:
            raise TypeError(
                f"'{self.__class__.__name__}' object is not callable")

    def _extract_prompt_from_args(self, args, kwargs):
        """Extract prompt from arguments based on common patterns."""
        # Check for prompt in common positions
        if args:
            # First argument is usually the prompt
            if isinstance(args[0], str):
                return args[0]
            # Check for messages list
            if isinstance(args[0], list) and args[0]:
                first_msg = args[0][0]
                if isinstance(first_msg, dict) and "content" in first_msg:
                    return first_msg["content"]

        # Check kwargs for common prompt keys
        for key in ["prompt", "content", "message", "text"]:
            if key in kwargs and isinstance(kwargs[key], str):
                return kwargs[key]

        return None

    def _replace_prompt_in_args(self, args, new_prompt):
        """Replace prompt in arguments with optimized prompt."""
        if not args:
            return args

        new_args = list(args)

        # Replace first argument if it's a string prompt
        if isinstance(new_args[0], str):
            new_args[0] = new_prompt
        # Replace in messages list
        elif isinstance(new_args[0], list) and new_args[0]:
            first_msg = new_args[0][0]
            if isinstance(first_msg, dict) and "content" in first_msg:
                new_args[0][0]["content"] = new_prompt

        return tuple(new_args)

    def _is_generation_method(self, method_name: str) -> bool:
        """Check if a method is an LLM generation method."""
        generation_methods = [
            "chat",
            "completions",
            "generate",
            "create",
            "messages",
            "acreate",
            "aget",
            "stream",
        ]
        return any(gen in method_name.lower() for gen in generation_methods)

    def _wrap_generation_method(self, method):
        """Wrap generation method to process prompts."""

        def wrapped_method(*args, **kwargs):
            # Extract prompt from arguments
            prompt = self._extract_prompt_from_args(args, kwargs)
            if prompt:
                # Process prompt through PrivySHA
                if self.pipeline:
                    processed = self.pipeline.process(prompt)
                    optimized_prompt = processed["prompts"]["optimized"]
                    # Replace prompt in args
                    args = self._replace_prompt_in_args(args, optimized_prompt)
            # Call original method
            return method(*args, **kwargs)

        return wrapped_method

    def _extract_prompt(self, args, kwargs) -> Optional[str]:
        """Extract prompt from various LLM client call patterns."""
        # OpenAI pattern: messages=[{"role": "user", "content": "..."}]
        if "messages" in kwargs:
            messages = kwargs["messages"]
            if messages and isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        return msg.get("content", "")

        # Anthropic pattern: messages=[{"role": "user", "content": "..."}]
        # Same as OpenAI

        # Simple prompt pattern
        if "prompt" in kwargs:
            return kwargs["prompt"]

        # Input pattern (some clients use 'input')
        if "input" in kwargs:
            input_val = kwargs["input"]
            if isinstance(input_val, str):
                return input_val
            elif isinstance(input_val, list) and input_val:
                return str(input_val[0])

        # Positional arguments
        if args and isinstance(args[0], str):
            return args[0]

        return None

    def _replace_prompt(self, args, kwargs, new_prompt: str):
        """Replace the original prompt with the optimized one."""
        # OpenAI/Anthropic pattern
        if "messages" in kwargs:
            messages = kwargs["messages"]
            if messages and isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        msg["content"] = new_prompt
                        break

        # Simple prompt pattern
        if "prompt" in kwargs:
            kwargs["prompt"] = new_prompt

        # Input pattern
        if "input" in kwargs:
            input_val = kwargs["input"]
            if isinstance(input_val, str):
                kwargs["input"] = new_prompt
            elif isinstance(input_val, list) and input_val:
                kwargs["input"] = [new_prompt] + input_val[1:]

        # Positional arguments
        if args and isinstance(args[0], str):
            args = (new_prompt,) + args[1:]

        return args, kwargs

    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the wrapped client."""
        return {
            "client_type": self.client_type,
            "client_class": type(self.client).__name__,
            "client_module": type(self.client).__module__,
            "privacy_enabled": self.privacy,
            "token_budget": self.token_budget,
            "pipeline_active": self.pipeline is not None,
        }


# Convenience function for quick setup
def quick_setup(
    provider: str = "openai", model: str = "gpt-4o-mini", privacy: bool = True
) -> "SecureLLMWrapper":
    """
    Quick setup for common providers.

    Args:
        provider: Provider name (openai, anthropic, etc.)
        model: Model name
        privacy: Enable privacy features

    Returns:
        Configured secure LLM wrapper

    Examples:
        >>> from privysha import quick_setup
        >>> client = quick_setup("openai", "gpt-4o-mini")
        >>> response = client.chat.completions.create(
        ...     messages=[{"role": "user", "content": "Analyze dataset"}]
        ... )
    """
    adapter = AdapterFactory.create_universal(provider=provider, model=model)
    return SecureLLMWrapper(adapter, privacy=privacy)
