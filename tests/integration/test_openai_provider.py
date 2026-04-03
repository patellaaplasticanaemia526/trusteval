# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Integration tests for the OpenAI provider with mocked HTTP responses.

All tests use unittest.mock to simulate OpenAI SDK behaviour so no real
API calls are made.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from trusteval.providers.base import (
    ProviderAuthenticationError,
    ProviderModelError,
    ProviderRateLimitError,
)


# ---------------------------------------------------------------------------
# Helpers to build mock OpenAI response objects
# ---------------------------------------------------------------------------


def _make_chat_response(content: str = "Mock response", total_tokens: int = 50):
    """Build a mock ChatCompletion response object."""
    message = SimpleNamespace(content=content, role="assistant")
    choice = SimpleNamespace(message=message, index=0, finish_reason="stop")
    usage = SimpleNamespace(
        prompt_tokens=20, completion_tokens=30, total_tokens=total_tokens
    )
    return SimpleNamespace(choices=[choice], usage=usage, model="gpt-4o")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestOpenAIProviderGenerate:

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_generate_success(self, mock_openai_cls, mock_async_cls):
        """generate() should return the assistant's content on success."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_chat_response(
            "Paris is the capital of France."
        )
        mock_openai_cls.return_value = mock_client
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        provider._client = mock_client

        result = provider.generate("What is the capital of France?")
        assert result == "Paris is the capital of France."
        assert mock_client.chat.completions.create.call_count == 1

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_generate_rate_limit_retry(self, mock_openai_cls, mock_async_cls):
        """generate() should raise ProviderRateLimitError on HTTP 429."""
        import openai as real_openai

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = (
            real_openai.RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )
        )
        mock_openai_cls.return_value = mock_client
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        provider._client = mock_client

        with pytest.raises(ProviderRateLimitError):
            provider.generate("Test prompt")

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_generate_batch(self, mock_openai_cls, mock_async_cls):
        """generate_batch() should return a list of responses."""
        responses = [
            _make_chat_response("Response 1"),
            _make_chat_response("Response 2"),
            _make_chat_response("Response 3"),
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses
        mock_openai_cls.return_value = mock_client
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        provider._client = mock_client

        results = provider.generate_batch(["P1", "P2", "P3"])
        assert len(results) == 3
        assert results[0] == "Response 1"
        assert results[2] == "Response 3"

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_is_available(self, mock_openai_cls, mock_async_cls):
        """is_available() should return True when the API responds."""
        mock_client = MagicMock()
        mock_client.models.list.return_value = ["gpt-4o"]
        mock_openai_cls.return_value = mock_client
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        provider._client = mock_client

        assert provider.is_available() is True

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_is_available_failure(self, mock_openai_cls, mock_async_cls):
        """is_available() should return False when the API is unreachable."""
        mock_client = MagicMock()
        mock_client.models.list.side_effect = Exception("Connection failed")
        mock_openai_cls.return_value = mock_client
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        provider._client = mock_client

        assert provider.is_available() is False


class TestOpenAIProviderValidation:

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_invalid_api_key(self, mock_openai_cls, mock_async_cls):
        """Empty API key should raise ProviderAuthenticationError."""
        with pytest.raises(ProviderAuthenticationError):
            from trusteval.providers.openai_provider import OpenAIProvider
            OpenAIProvider(api_key="", model="gpt-4o")

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_invalid_model(self, mock_openai_cls, mock_async_cls):
        """Unsupported model should raise ProviderModelError."""
        with pytest.raises(ProviderModelError):
            from trusteval.providers.openai_provider import OpenAIProvider
            OpenAIProvider(api_key="sk-test", model="nonexistent-model-xyz")


class TestOpenAIProviderCost:

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_estimate_cost(self, mock_openai_cls, mock_async_cls):
        """estimate_cost should return a positive dollar amount."""
        mock_openai_cls.return_value = MagicMock()
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        cost = provider.estimate_cost(prompt_tokens=1000, completion_tokens=500)
        assert cost > 0.0

    @patch("openai.AsyncOpenAI")
    @patch("openai.OpenAI")
    def test_count_tokens_heuristic(self, mock_openai_cls, mock_async_cls):
        """count_tokens should return a reasonable estimate."""
        mock_openai_cls.return_value = MagicMock()
        mock_async_cls.return_value = MagicMock()

        from trusteval.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4o")
        tokens = provider.count_tokens("Hello, world! How are you today?")
        assert tokens > 0
