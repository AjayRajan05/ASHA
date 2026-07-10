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
from .base import BaseAdapter


class GrokAdapter(BaseAdapter):
    """
    Grok (xAI) adapter using OpenAI-compatible API interface.
    """

    def __init__(self, model: str = "grok-beta") -> None:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )

        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise ValueError("GROK_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate response using Grok model."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            content = response.choices[0].message.content
            return (content or "").strip()
        except Exception as e:
            raise RuntimeError(f"Grok generation failed: {str(e)}")
