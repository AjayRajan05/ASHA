"""Tests for global PrivySHA configuration."""

from __future__ import annotations

import pytest

from privysha.core import config as config_module
from privysha.core.config import (
    PrivySHAConfig,
    get_config,
    get_config_summary,
    get_security_level,
    get_timeout_ms,
    is_deterministic,
    is_enabled,
    is_observability_enabled,
    set_config,
    set_deterministic,
    set_enabled,
    set_observability,
    set_security_level,
    set_timeout_ms,
    update_from_env,
)


@pytest.fixture
def restore_config():
    saved = config_module._global_config
    yield
    config_module._global_config = saved


@pytest.fixture
def fresh_config(restore_config):
    cfg = PrivySHAConfig()
    set_config(cfg)
    return cfg


def test_get_config_returns_global_instance(fresh_config):
    assert get_config() is fresh_config


def test_set_config_replaces_global(restore_config):
    custom = PrivySHAConfig(enabled=False, default_timeout_ms=250)
    set_config(custom)
    assert get_config() is custom
    assert get_config().enabled is False
    assert get_timeout_ms() == 250


def test_enabled_helpers(fresh_config):
    assert is_enabled() is True
    set_enabled(False)
    assert is_enabled() is False
    set_enabled(True)
    assert is_enabled() is True


def test_deterministic_helpers(fresh_config):
    assert is_deterministic() is False
    set_deterministic(True)
    assert is_deterministic() is True


def test_timeout_and_security_level(fresh_config):
    set_timeout_ms(500)
    assert get_timeout_ms() == 500
    set_security_level("HIGH")
    assert get_security_level() == "high"


def test_observability_helpers(fresh_config):
    assert is_observability_enabled() is True
    set_observability(False)
    assert is_observability_enabled() is False


def test_get_config_summary(fresh_config):
    set_enabled(True)
    set_deterministic(False)
    set_timeout_ms(100)
    set_security_level("medium")
    summary = get_config_summary()
    assert summary["enabled"] is True
    assert summary["deterministic_mode"] is False
    assert summary["timeout_ms"] == 100
    assert summary["security_level"] == "medium"
    assert summary["auto_observability"] is True
    assert summary["cache_enabled"] is False


def test_update_from_env_enabled(monkeypatch, fresh_config):
    monkeypatch.setenv("PRIVYSHA_ENABLED", "false")
    update_from_env()
    assert is_enabled() is False
    monkeypatch.setenv("PRIVYSHA_ENABLED", "true")
    update_from_env()
    assert is_enabled() is True


def test_update_from_env_timeout_and_providers(monkeypatch, fresh_config):
    monkeypatch.setenv("PRIVYSHA_TIMEOUT_MS", "750")
    monkeypatch.setenv("PRIVYSHA_AUTO_PATCH_PROVIDERS", "openai, anthropic")
    monkeypatch.setenv("PRIVYSHA_SECURITY_LEVEL", "strict")
    monkeypatch.setenv("PRIVYSHA_DETERMINISTIC", "yes")
    monkeypatch.setenv("PRIVYSHA_OBSERVABILITY", "0")
    update_from_env()
    assert get_timeout_ms() == 750
    assert get_config().auto_patch_providers == ["openai", "anthropic"]
    assert get_security_level() == "strict"
    assert is_deterministic() is True
    assert is_observability_enabled() is False


def test_update_from_env_invalid_timeout_ignored(monkeypatch, fresh_config):
    set_timeout_ms(100)
    monkeypatch.setenv("PRIVYSHA_TIMEOUT_MS", "not-a-number")
    update_from_env()
    assert get_timeout_ms() == 100
