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
FastAPI integration for PrivySHA

Provides middleware for automatic prompt security and optimization
in FastAPI applications.
"""

from typing import Any

from .middleware import PrivySHAMiddleware


def add_privysha_middleware(app: Any, **kwargs: Any) -> None:
    """
    Convenience function to add PrivySHA middleware to FastAPI app.

    Args:
        app: FastAPI application instance
        **kwargs: Additional arguments for PrivySHAMiddleware
    """
    app.add_middleware(PrivySHAMiddleware, **kwargs)


__all__ = ["PrivySHAMiddleware", "add_privysha_middleware"]
