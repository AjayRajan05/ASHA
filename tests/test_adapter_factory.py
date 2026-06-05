import os

import pytest
from unittest.mock import patch

from privysha.adapters.factory import AdapterFactory
from privysha.adapters.openai_adapter import OpenAIAdapter
from privysha.adapters.ollama_adapter import OllamaAdapter
from privysha.adapters.mock_adapter import MockAdapter
from privysha.adapters.claude_adapter import ClaudeAdapter


class TestAdapterFactory:
    """Tests for AdapterFactory.create() routing (v0.2 API)."""

    def test_create_mock(self):
        adapter = AdapterFactory.create("mock")
        assert isinstance(adapter, MockAdapter)
        assert adapter.model == "mock"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_create_gpt_model(self):
        pytest.importorskip("openai")
        adapter = AdapterFactory.create("gpt-4")
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.model == "gpt-4"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_create_gpt_model_variations(self):
        pytest.importorskip("openai")
        for model in ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini", "gpt-4-turbo"]:
            adapter = AdapterFactory.create(model)
            assert isinstance(adapter, OpenAIAdapter)
            assert adapter.model == model

    def test_create_ollama_model(self):
        adapter = AdapterFactory.create("llama3")
        assert isinstance(adapter, OllamaAdapter)
        assert adapter.model == "llama3"

    def test_create_ollama_model_variations(self):
        for model in ["llama3", "codellama"]:
            adapter = AdapterFactory.create(model)
            assert isinstance(adapter, OllamaAdapter)
            assert adapter.model == model

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"})
    def test_create_claude_model(self):
        pytest.importorskip("anthropic")
        adapter = AdapterFactory.create("claude-3-sonnet")
        assert isinstance(adapter, ClaudeAdapter)
        assert adapter.model_name == "claude-3-sonnet"

    def test_create_unsupported_model_raises(self):
        with pytest.raises(ValueError, match="Unsupported provider/model"):
            AdapterFactory.create("")

        with pytest.raises(ValueError, match="Unsupported provider/model"):
            AdapterFactory.create("mistral")

        with pytest.raises(ValueError, match="Unsupported provider/model"):
            AdapterFactory.create("qwen")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_create_gpt_is_case_insensitive(self):
        pytest.importorskip("openai")
        adapter = AdapterFactory.create("GPT-4")
        assert isinstance(adapter, OpenAIAdapter)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_create_gpt_prefix_routing(self):
        pytest.importorskip("openai")
        assert isinstance(AdapterFactory.create("gpt"), OpenAIAdapter)
        assert isinstance(AdapterFactory.create("gpt-custom"), OpenAIAdapter)

        with pytest.raises(ValueError, match="Unsupported provider/model"):
            AdapterFactory.create("my-gpt-model")
