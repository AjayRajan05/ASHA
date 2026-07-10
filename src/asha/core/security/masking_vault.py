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

"""In-memory reversible PII masking vault (opt-in only)."""

from typing import Dict, Optional


class MaskingVault:
    """Maps mask tokens to original values for opt-in reversible masking."""

    def __init__(self) -> None:
        self._token_to_original: Dict[str, str] = {}
        self._original_to_token: Dict[str, str] = {}

    def register(self, token: str, original: str) -> None:
        if not token or not original:
            return
        self._token_to_original[token] = original
        self._original_to_token[original] = token

    def lookup(self, token: str) -> Optional[str]:
        return self._token_to_original.get(token)

    def to_dict(self) -> Dict[str, str]:
        """Return token -> original mapping (for API responses)."""
        return dict(self._token_to_original)

    def clear(self) -> None:
        self._token_to_original.clear()
        self._original_to_token.clear()

    def __len__(self) -> int:
        return len(self._token_to_original)


# Module-level vault used when reversible=True on a single request
_active_vault: Optional[MaskingVault] = None


def get_active_vault() -> Optional[MaskingVault]:
    return _active_vault


def set_active_vault(vault: Optional[MaskingVault]) -> None:
    global _active_vault
    _active_vault = vault
