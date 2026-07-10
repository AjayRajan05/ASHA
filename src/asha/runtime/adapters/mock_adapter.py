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


class MockAdapter(BaseAdapter):
    """Mock adapter for testing purposes without requiring external LLM services"""

    def __init__(self, model: str = "mock") -> None:
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate a mock response based on the prompt content"""

        # Simple mock responses based on prompt content
        if "analyze" in prompt.lower():
            return "Mock analysis completed. Found patterns in the data."
        elif "dataset" in prompt.lower():
            return "Mock dataset processing complete."
        elif "anomalies" in prompt.lower():
            return "Mock anomaly detection finished. No anomalies detected."
        else:
            return "Mock response: Processing completed successfully."

        # In a real implementation, this would call an LLM API
        # return f"Mock response for: {prompt[:50]}..."
