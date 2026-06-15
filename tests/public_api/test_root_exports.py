# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Public API freeze tests."""

from __future__ import annotations

import pytest

import privysha


def test_root_eager_exports_frozen() -> None:
    expected = {"process", "sanitize", "optimize", "Agent", "__version__"}
    assert set(privysha.__all__) == expected


def test_root_export_count_at_most_ten() -> None:
    assert len(privysha.__all__) <= 10


def test_primary_apis_callable() -> None:
    assert callable(privysha.process)
    assert callable(privysha.sanitize)
    assert callable(privysha.optimize)
    assert callable(privysha.Agent)


def test_moved_symbols_not_eager() -> None:
    import importlib
    import sys

    saved = {
        key: module
        for key, module in sys.modules.items()
        if key == "privysha" or key.startswith("privysha.")
    }
    try:
        for key in saved:
            sys.modules.pop(key, None)
        mod = importlib.import_module("privysha")
        assert "Processor" not in mod.__dict__
        assert "wrap_llm" not in mod.__dict__
        assert "ProcessResult" not in mod.__dict__
        assert "Pipeline" not in mod.__dict__
    finally:
        sys.modules.update(saved)


@pytest.mark.parametrize(
    "name",
    ["Processor", "wrap_llm", "Pipeline", "ProcessResult", "auto_patch"],
)
def test_lazy_symbols_raise_attribute_error(name: str) -> None:
    with pytest.raises(AttributeError):
        getattr(privysha, name)


def test_no_getattr_shim() -> None:
    assert not hasattr(privysha, "__getattr__")
