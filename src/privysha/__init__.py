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
PrivySHA - Drop-in Security & Optimization Layer for Any LLM App

Primary API (import directly):
    from privysha import process, sanitize, optimize, Agent

Advanced components live in subpackages:
    from privysha.runtime import PromptProcessor
    from privysha.integrations import wrap_llm
    from privysha.types import ProcessResult
"""

__version__ = "0.4.1"

from .runtime.agent import Agent
from .runtime.anchor.runtime import anchor
from .utils.dropin import (
    optimize,
    process,
    sanitize,
)

__all__ = [
    "__version__",
    "process",
    "sanitize",
    "optimize",
    "Agent",
    "anchor",
]
