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

import requests
from typing import Any

from .base import BaseAdapter


class OllamaAdapter(BaseAdapter):

    def __init__(self, model: str = "llama3") -> None:
        """Initialize Ollama adapter with specified model.

        Args:
            model: Ollama model name (default: 'llama3')

        Note:
            Requires Ollama server running at http://localhost:11434
        """
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate response using Ollama model.

        Args:
            prompt: Input prompt for Ollama model

        Returns:
            Generated response text

        Raises:
            requests.RequestException: If Ollama server is not accessible
            KeyError: If response format is unexpected
        """
        url = "http://localhost:11434/api/generate"

        payload: dict[str, Any] = {"model": self.model, "prompt": prompt, "stream": False}

        try:
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            return str(r.json()["response"])
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to connect to Ollama server: {e}. "
                "Make sure Ollama is running at http://localhost:11434"
            )
        except KeyError as e:
            raise KeyError(
                f"Unexpected response format from Ollama: {e}. "
                "Check Ollama server version and compatibility"
            )
