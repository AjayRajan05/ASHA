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

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import BaseAdapter


class ClaudeAdapter(BaseAdapter):

    def __init__(self, model=None):
        """Initialize Claude adapter with specified model.

        Args:
            model: Claude model name (e.g., 'claude-3-sonnet-20240229')

        Raises:
            ImportError: If anthropic library not installed
            ValueError: If model name not provided
            ValueError: If ANTHROPIC_API_KEY not set
            RuntimeError: If client initialization fails
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic library is not installed. "
                "Install with: pip install anthropic"
            )

        if not model:
            raise ValueError(
                "Model name is required for Claude adapter. "
                "Example: ClaudeAdapter(model='claude-3-sonnet-20240229')"
            )

        self.model_name = model

        # Try to get API key from environment
        import os

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Set it with: export ANTHROPIC_API_KEY='your-key'"
            )

        try:
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Anthropic client: {e}. "
                "Check your API key and network connection."
            )

    def generate(self, prompt: str) -> str:
        """Generate response using Claude model.

        Args:
            prompt: Input prompt for Claude model

        Returns:
            Generated response text

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            return response.content[0].text.strip()

        except Exception as e:
            return f"Claude generation error: {str(e)}"
