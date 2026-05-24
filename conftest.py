"""Pytest configuration — ensure local src/ is used before site-packages."""

import os
import sys
from pathlib import Path

import pytest

# Disable ML/safety classifier downloads during tests (fast, deterministic CI)
os.environ.setdefault("PRIVYSHA_DISABLE_ML", "1")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(autouse=True)
def _reset_auto_patch_state():
    """Prevent auto_patch tests from leaking global SDK patch state."""
    yield
    try:
        from privysha.utils.auto_patch import auto_patch, enable_auto_patch

        enable_auto_patch()
        auto_patch(enable=False)
    except Exception:
        pass
