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
Adapters module for ASHA.

Heavy provider adapters load lazily on first access to keep import time low.
"""

from importlib import import_module
from typing import Any, Tuple

from .base import BaseAdapter
from .factory import AdapterFactory

_LAZY_IMPORTS: dict[str, Tuple[str, str]] = {
    "OpenAIAdapter": (".openai_adapter", "OpenAIAdapter"),
    "ClaudeAdapter": (".claude_adapter", "ClaudeAdapter"),
    "HuggingFaceAdapter": (".hf_adapter", "HuggingFaceAdapter"),
    "OllamaAdapter": (".ollama_adapter", "OllamaAdapter"),
    "MockAdapter": (".mock_adapter", "MockAdapter"),
    "GeminiAdapter": (".gemini_adapter", "GeminiAdapter"),
    "GrokAdapter": (".grok_adapter", "GrokAdapter"),
    "UniversalModelAdapter": (".universal_adapter", "UniversalModelAdapter"),
}

__all__ = [
    "BaseAdapter",
    "AdapterFactory",
    "OpenAIAdapter",
    "ClaudeAdapter",
    "HuggingFaceAdapter",
    "OllamaAdapter",
    "MockAdapter",
    "GeminiAdapter",
    "GrokAdapter",
    "UniversalModelAdapter",
]


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        module = import_module(module_path, __name__)
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
