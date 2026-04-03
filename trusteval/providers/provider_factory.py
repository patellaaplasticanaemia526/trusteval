# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Provider factory for creating and managing LLM provider instances.

The factory abstracts away provider-specific construction logic, handles
automatic API-key resolution from environment variables, and offers
convenience methods for listing available providers and testing
connectivity.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Type

from trusteval.providers.base import (
    BaseProvider,
    ProviderAuthenticationError,
    ProviderError,
)

logger = logging.getLogger(__name__)

# Registry mapping canonical provider names to their class import paths
# and default environment-variable names for API keys.
_PROVIDER_REGISTRY: Dict[str, Dict[str, str]] = {
    "openai": {
        "module": "trusteval.providers.openai_provider",
        "class": "OpenAIProvider",
        "env_key": "OPENAI_API_KEY",
        "description": "OpenAI GPT models via the Chat Completions API.",
    },
    "anthropic": {
        "module": "trusteval.providers.anthropic_provider",
        "class": "AnthropicProvider",
        "env_key": "ANTHROPIC_API_KEY",
        "description": "Anthropic Claude models via the Messages API.",
    },
    "gemini": {
        "module": "trusteval.providers.gemini_provider",
        "class": "GeminiProvider",
        "env_key": "GOOGLE_API_KEY",
        "description": "Google Gemini models via the Generative AI SDK.",
    },
    "huggingface": {
        "module": "trusteval.providers.huggingface_provider",
        "class": "HuggingFaceProvider",
        "env_key": "HUGGINGFACE_API_KEY",
        "description": (
            "HuggingFace models via the Inference API (remote) or "
            "transformers pipeline (local)."
        ),
    },
}


def _import_provider_class(provider_name: str) -> Type[BaseProvider]:
    """Dynamically import and return the provider class.

    Args:
        provider_name: Canonical name (e.g. ``"openai"``).

    Returns:
        The provider class (un-instantiated).

    Raises:
        ProviderError: If the provider name is unknown.
        ImportError: If the required SDK package is not installed.
    """
    entry = _PROVIDER_REGISTRY.get(provider_name)
    if entry is None:
        available = ", ".join(sorted(_PROVIDER_REGISTRY))
        raise ProviderError(
            f"Unknown provider '{provider_name}'. "
            f"Available providers: {available}"
        )

    import importlib

    module = importlib.import_module(entry["module"])
    cls: Type[BaseProvider] = getattr(module, entry["class"])
    return cls


class ProviderFactory:
    """Factory for constructing LLM provider instances.

    Centralises provider creation so that callers do not need to
    know concrete class names or environment-variable conventions.

    Example::

        factory = ProviderFactory()
        provider = factory.create("openai", model="gpt-4o")
        print(provider.generate("Hello!"))
    """

    @staticmethod
    def create(
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ) -> BaseProvider:
        """Create and return a configured provider instance.

        If *api_key* is not supplied, the factory reads the
        corresponding environment variable (e.g. ``OPENAI_API_KEY``).

        Args:
            provider: Canonical provider name — one of ``"openai"``,
                ``"anthropic"``, ``"gemini"``, ``"huggingface"``.
            model: Model identifier (e.g. ``"gpt-4o"``,
                ``"claude-3-sonnet-20240229"``).
            api_key: Optional API key.  When ``None`` the factory
                attempts to read it from the environment.
            **kwargs: Additional keyword arguments forwarded to the
                provider constructor as part of ``config``.

        Returns:
            A fully initialised ``BaseProvider`` subclass.

        Raises:
            ProviderError: If the provider name is unrecognised.
            ProviderAuthenticationError: If no API key can be resolved.
            ImportError: If the required SDK is missing.

        Example::

            # Reads OPENAI_API_KEY from the environment automatically.
            provider = ProviderFactory.create("openai", model="gpt-4o")
        """
        provider_name = provider.lower().strip()
        entry = _PROVIDER_REGISTRY.get(provider_name)
        if entry is None:
            available = ", ".join(sorted(_PROVIDER_REGISTRY))
            raise ProviderError(
                f"Unknown provider '{provider}'. "
                f"Available providers: {available}"
            )

        # Resolve API key: explicit arg -> environment variable.
        resolved_key = api_key or os.environ.get(entry["env_key"], "")
        if not resolved_key:
            raise ProviderAuthenticationError(
                f"No API key provided for '{provider_name}' and the "
                f"environment variable '{entry['env_key']}' is not set."
            )

        cls = _import_provider_class(provider_name)

        config = dict(kwargs) if kwargs else None
        instance = cls(api_key=resolved_key, model=model, config=config)

        logger.info(
            "ProviderFactory created %s (model=%s)",
            instance.get_provider_name(),
            model,
        )
        return instance

    @staticmethod
    def list_providers() -> List[Dict[str, Any]]:
        """List all registered providers with metadata.

        Returns:
            A list of dictionaries, each containing:

            - ``name`` — canonical provider name.
            - ``description`` — human-readable description.
            - ``env_key`` — environment variable used for the API key.
            - ``supported_models`` — list of model identifiers (loaded
              dynamically; empty if the SDK is not installed).

        Example::

            for p in ProviderFactory.list_providers():
                print(p["name"], p["supported_models"])
        """
        results: List[Dict[str, Any]] = []
        for name, entry in sorted(_PROVIDER_REGISTRY.items()):
            info: Dict[str, Any] = {
                "name": name,
                "description": entry["description"],
                "env_key": entry["env_key"],
                "supported_models": [],
            }
            try:
                cls = _import_provider_class(name)
                info["supported_models"] = list(cls.SUPPORTED_MODELS)
            except (ImportError, Exception):
                pass  # SDK not installed; models list stays empty.

            results.append(info)
        return results

    @staticmethod
    def test_connectivity(
        provider: str,
        api_key: Optional[str] = None,
    ) -> bool:
        """Test whether a provider is reachable with the given credentials.

        Creates a temporary provider instance using the first model in
        ``SUPPORTED_MODELS`` (or the raw provider name for HuggingFace)
        and calls ``is_available()``.

        Args:
            provider: Canonical provider name.
            api_key: Optional API key; resolved from the environment if
                ``None``.

        Returns:
            ``True`` if the provider responds successfully, ``False``
            otherwise.

        Example::

            if ProviderFactory.test_connectivity("openai"):
                print("OpenAI is reachable!")
        """
        provider_name = provider.lower().strip()
        entry = _PROVIDER_REGISTRY.get(provider_name)
        if entry is None:
            logger.warning("Unknown provider '%s' in test_connectivity", provider)
            return False

        resolved_key = api_key or os.environ.get(entry["env_key"], "")
        if not resolved_key:
            logger.warning(
                "No API key for '%s'; connectivity test skipped.", provider_name
            )
            return False

        try:
            cls = _import_provider_class(provider_name)
        except (ImportError, ProviderError):
            logger.debug(
                "Could not import provider class for '%s'", provider_name,
                exc_info=True,
            )
            return False

        # Pick a default model for the connectivity check.
        models = cls.SUPPORTED_MODELS
        default_model = models[0] if models else provider_name

        try:
            instance = cls(
                api_key=resolved_key, model=default_model, config={}
            )
            return instance.is_available()
        except Exception:
            logger.debug(
                "Connectivity test failed for '%s'", provider_name,
                exc_info=True,
            )
            return False
