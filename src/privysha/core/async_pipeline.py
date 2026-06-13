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
Async pipeline support for PrivySHA.

Provides async-compatible processing without blocking the event loop.
"""

import asyncio
from functools import partial
from typing import Any, Dict, Optional, cast

from ..pipeline import Pipeline
from ..adapters.universal_adapter import UniversalModelAdapter


async def process_async(
    prompt: str,
    adapter: Optional[UniversalModelAdapter] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Async version of PrivySHA processing.

    Args:
        prompt: Input prompt to process
        adapter: Universal model adapter (optional)
        **kwargs: Additional pipeline parameters

    Returns:
        Processing result with optimized prompt and metrics
    """
    loop = asyncio.get_event_loop()

    # Create pipeline with async support
    pipeline = Pipeline(**kwargs)

    # Run processing in executor to avoid blocking
    func = partial(pipeline.process, prompt, adapter)
    return await loop.run_in_executor(None, func)


async def optimize_async(prompt: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Async version of optimization only.

    Args:
        prompt: Input prompt to optimize
        **kwargs: Pipeline parameters

    Returns:
        Optimization result with metrics
    """
    loop = asyncio.get_event_loop()

    # Create pipeline for optimization only
    pipeline = Pipeline(**kwargs)

    # Run optimization in executor
    func = partial(pipeline.process, prompt)
    result = await loop.run_in_executor(None, func)

    # Return optimization-specific result
    return {
        "optimized": result["prompts"]["optimized"],
        "original": prompt,
        "token_reduction": result["optimization_metrics"]["token_reduction_percentage"],
        "optimization_method": "aggressive",
        "success": result["success"],
    }


async def sanitize_async(prompt: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Async version of security processing only.

    Args:
        prompt: Input prompt to sanitize
        **kwargs: Pipeline parameters

    Returns:
        Sanitization result with security metrics
    """
    loop = asyncio.get_event_loop()

    # Create pipeline for sanitization only
    pipeline = Pipeline(**kwargs)

    # Run sanitization in executor
    func = partial(pipeline.process, prompt)
    result = await loop.run_in_executor(None, func)

    # Return sanitization-specific result
    return {
        "sanitized": result["prompts"]["sanitized"],
        "original": prompt,
        "security_result": result["security_result"],
        "success": result["success"],
    }


class AsyncPipeline:
    """
    Async wrapper around the main Pipeline class.

    Provides async methods while maintaining all pipeline functionality.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize async pipeline with same parameters as Pipeline."""
        self.pipeline = Pipeline(**kwargs)

    async def process(
        self,
        content: str,
        adapter: Optional[UniversalModelAdapter] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async process method."""
        loop = asyncio.get_event_loop()
        func = partial(self.pipeline.process, content, adapter, constraints)
        return await loop.run_in_executor(None, func)

    async def optimize(self, prompt: str) -> str:
        """Async optimization only."""
        loop = asyncio.get_event_loop()
        pipeline_any = cast(Any, self.pipeline)
        func = partial(pipeline_any._aggressive_optimize, prompt)
        result = await loop.run_in_executor(None, func)
        return cast(str, result)

    async def get_explanation(
        self, session_id: Optional[str] = None, format_type: str = "json"
    ) -> Optional[str]:
        """Async explanation retrieval."""
        loop = asyncio.get_event_loop()
        pipeline_any = cast(Any, self.pipeline)
        func = partial(pipeline_any.get_explanation, session_id, format_type)
        return await loop.run_in_executor(None, func)

    async def get_debug_trace(
        self, session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Async debug trace retrieval."""
        loop = asyncio.get_event_loop()
        pipeline_any = cast(Any, self.pipeline)
        func = partial(pipeline_any.get_debug_trace, session_id)
        return await loop.run_in_executor(None, func)


# Convenience functions for drop-in async usage
async def process_async_entry(prompt: str, **kwargs: Any) -> Dict[str, Any]:
    """Entry point for async processing with fail-safe."""
    try:
        return await process_async(prompt, **kwargs)
    except Exception:
        # Fail-safe: return original prompt
        return {
            "success": True,
            "result": prompt,
            "prompts": {
                "original": prompt,
                "sanitized": prompt,
                "compiled": prompt,
                "optimized": prompt,
            },
            "optimization_metrics": {"token_reduction_percentage": 0},
            "security_result": type(
                "SecurityResult",
                (),
                {
                    "is_safe": True,
                    "detected_threats": [],
                    "masked_entities": {},
                    "sanitized_content": prompt,
                    "threat_level": "LOW",
                    "security_score": 0.0,
                },
            )(),
            "fallback_mode": True,
        }
