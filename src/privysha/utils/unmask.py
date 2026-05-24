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

"""Restore masked PII in text using a reversible masking map."""

import re
from typing import Dict, Union


def unmask(text: str, masking_map: Dict[str, str]) -> str:
    """
    Replace mask tokens in text with original values.

    Args:
        text: Text containing mask tokens (e.g. from LLM output)
        masking_map: token -> original value mapping from process(..., reversible=True)

    Returns:
        Text with mask tokens restored to originals
    """
    if not text or not masking_map:
        return text

    restored = text
    # Replace longest tokens first to avoid partial collisions
    for token in sorted(masking_map.keys(), key=len, reverse=True):
        original = masking_map[token]
        if token in restored:
            restored = restored.replace(token, original)

    return restored


def unmask_with_pattern(text: str, masking_map: Dict[str, str]) -> str:
    """
    Unmask using regex for hash-suffixed tokens like [EMAIL_HASH]_abc12345.
    """
    if not text or not masking_map:
        return text

    restored = text
    for token, original in masking_map.items():
        pattern = re.escape(token)
        restored = re.sub(pattern, original, restored)
    return restored
