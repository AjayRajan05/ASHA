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

from .base import BaseAdapter


class ModelAdapter(BaseAdapter):

    def __init__(self, model: str = "mock") -> None:
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate mock response for testing purposes."""
        # placeholder model execution
        return f"[{self.model} RESPONSE]\nProcessed Prompt:\n{prompt}"
