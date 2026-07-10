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

import os
from typing import List, Optional

from .base import BaseAdapter
from .universal_adapter import UniversalModelAdapter


class GeminiAdapter(BaseAdapter):
    """
    Google Gemini Adapter - Backward compatible wrapper using UniversalModelAdapter.
    """

    def __init__(self, model: str = "gemini-1.5-flash") -> None:
        """Initialize Gemini adapter with specified model.

        Args:
            model: Gemini model name (default: 'gemini-1.5-flash')

        Note:
            Uses UniversalModelAdapter for enhanced functionality
        """
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY environment variable is not set. "
                "Set it with: export GOOGLE_API_KEY='your-key'"
            )

        self._adapter = UniversalModelAdapter(
            provider="gemini", model=model, api_key=api_key
        )
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate response using Gemini model.

        Args:
            prompt: Input prompt for Gemini model

        Returns:
            Generated response text

        Raises:
            Exception: If API call fails
            ValueError: If API key not set
        """
        return self._adapter.generate(prompt)

    # Additional v2 methods exposed for compatibility
    def generate_with_fallback(
        self, prompt: str, fallback_models: Optional[List[BaseAdapter]] = None
    ) -> str:
        """Generate with fallback support.

        Args:
            prompt: Input prompt
            fallback_models: List of fallback model configurations

        Returns:
            Generated response with fallback if primary fails
        """
        return self._adapter.generate_with_fallback(prompt, fallback_models)

    def get_provider_info(self) -> dict:
        """Get provider information.

        Returns:
            Dictionary with provider details including model, capabilities, etc.
        """
        return self._adapter.get_provider_info()
