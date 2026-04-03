# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""LLM provider connectors for the TrustEval evaluation framework.

This package exposes a unified interface to multiple LLM backends
(OpenAI, Anthropic, Google Gemini, HuggingFace) through the
:class:`BaseProvider` abstract class and the :class:`ProviderFactory`
convenience factory.

Quick start::

    from trusteval.providers import ProviderFactory

    provider = ProviderFactory.create("openai", model="gpt-4o")
    answer = provider.generate("What is 2 + 2?")

Exports:
    BaseProvider: Abstract base class for all providers.
    ProviderFactory: Factory for creating provider instances.
    OpenAIProvider: OpenAI Chat Completions connector.
    AnthropicProvider: Anthropic Claude Messages connector.
    GeminiProvider: Google Gemini Generative AI connector.
    HuggingFaceProvider: HuggingFace Inference API / local connector.
    ProviderError: Base exception for provider errors.
    ProviderAuthenticationError: Authentication failure.
    ProviderRateLimitError: Rate-limit / throttling error.
    ProviderConnectionError: Network connectivity error.
    ProviderModelError: Invalid or unsupported model.
"""

from trusteval.providers.base import (
    BaseProvider,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderModelError,
    ProviderRateLimitError,
)
from trusteval.providers.provider_factory import ProviderFactory

# Lazy imports for concrete providers — avoids hard dependency on every SDK.


def __getattr__(name: str):
    """Lazily import concrete provider classes on first access.

    This prevents ``ImportError`` at package-import time when only a
    subset of provider SDKs are installed.
    """
    _lazy_imports = {
        "OpenAIProvider": "trusteval.providers.openai_provider",
        "AnthropicProvider": "trusteval.providers.anthropic_provider",
        "GeminiProvider": "trusteval.providers.gemini_provider",
        "HuggingFaceProvider": "trusteval.providers.huggingface_provider",
    }

    if name in _lazy_imports:
        import importlib

        module = importlib.import_module(_lazy_imports[name])
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseProvider",
    "ProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "HuggingFaceProvider",
    "ProviderError",
    "ProviderAuthenticationError",
    "ProviderRateLimitError",
    "ProviderConnectionError",
    "ProviderModelError",
]
