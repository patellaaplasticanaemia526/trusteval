# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Base provider abstract class for all LLM provider implementations.

Defines the interface that every provider must implement, along with
shared retry logic and utility methods.
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Any, Dict, List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider-related errors."""


class ProviderAuthenticationError(ProviderError):
    """Raised when API authentication fails."""


class ProviderRateLimitError(ProviderError):
    """Raised when the provider rate-limits the request."""


class ProviderConnectionError(ProviderError):
    """Raised when the provider cannot be reached."""


class ProviderModelError(ProviderError):
    """Raised when the requested model is invalid or unavailable."""


# Default retry decorator used by concrete providers.
# Retries up to 5 times with exponential back-off (1 s -> 2 s -> 4 s -> …)
# on transient rate-limit and connection errors.
default_retry = retry(
    retry=retry_if_exception_type((ProviderRateLimitError, ProviderConnectionError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    before_sleep=lambda retry_state: logger.warning(
        "Retry attempt %s after %s – sleeping %.1f s",
        retry_state.attempt_number,
        retry_state.outcome.exception().__class__.__name__,
        retry_state.next_action.sleep,  # type: ignore[union-attr]
    ),
    reraise=True,
)


class BaseProvider(abc.ABC):
    """Abstract base class for LLM provider connectors.

    Every concrete provider (OpenAI, Anthropic, …) must sub-class this and
    implement the abstract methods.  Shared functionality – retry logic,
    name helpers, configuration merging – lives here.

    Attributes:
        api_key: The API key used for authentication.
        model: The model identifier (e.g. ``"gpt-4"``).
        config: Optional dictionary of extra configuration values that
            are forwarded to the underlying SDK.

    Example::

        provider = OpenAIProvider(api_key="sk-...", model="gpt-4")
        response = provider.generate("Explain quantum computing.")
    """

    SUPPORTED_MODELS: List[str] = []
    """Class-level list of model identifiers this provider supports."""

    def __init__(
        self,
        api_key: str,
        model: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the provider.

        Args:
            api_key: Authentication key for the provider API.
            model: Model identifier to use for generation.
            config: Optional extra configuration forwarded to the SDK
                (e.g. ``temperature``, ``max_tokens``).

        Raises:
            ProviderAuthenticationError: If *api_key* is empty / ``None``.
            ProviderModelError: If *model* is not in ``SUPPORTED_MODELS``.
        """
        if not api_key:
            raise ProviderAuthenticationError(
                f"{self.get_provider_name()} requires a valid API key."
            )

        if self.SUPPORTED_MODELS and model not in self.SUPPORTED_MODELS:
            raise ProviderModelError(
                f"Model '{model}' is not supported by {self.get_provider_name()}. "
                f"Supported models: {self.SUPPORTED_MODELS}"
            )

        self.api_key: str = api_key
        self.model: str = model
        self.config: Dict[str, Any] = config or {}

        # Bookkeeping
        self._request_count: int = 0
        self._total_tokens_used: int = 0
        self._created_at: float = time.time()

        logger.info(
            "Initialised %s with model=%s", self.get_provider_name(), self.model
        )

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a single completion from the model.

        Args:
            prompt: The user prompt / instruction.
            **kwargs: Provider-specific overrides (``temperature``,
                ``max_tokens``, etc.).

        Returns:
            The generated text.

        Raises:
            ProviderError: On any API or processing error.
        """

    @abc.abstractmethod
    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate completions for a list of prompts.

        The default expectation is sequential execution; concrete providers
        may override with concurrent / batched implementations.

        Args:
            prompts: A list of prompt strings.
            **kwargs: Provider-specific overrides.

        Returns:
            A list of generated strings, one per input prompt.

        Raises:
            ProviderError: On any API or processing error.
        """

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check whether the provider is reachable and the API key is valid.

        Returns:
            ``True`` if a lightweight connectivity check succeeds.
        """

    # ------------------------------------------------------------------
    # Concrete helpers
    # ------------------------------------------------------------------

    def get_provider_name(self) -> str:
        """Return a human-readable provider name derived from the class name.

        Returns:
            Provider name string, e.g. ``"OpenAIProvider"``.
        """
        return self.__class__.__name__

    def get_model_name(self) -> str:
        """Return the active model identifier.

        Returns:
            The *model* string passed at construction time.
        """
        return self.model

    def get_supported_models(self) -> list[str]:
        """Return the list of models this provider supports.

        Returns:
            A copy of ``SUPPORTED_MODELS``.
        """
        return list(self.SUPPORTED_MODELS)

    def _merge_config(self, **kwargs: Any) -> Dict[str, Any]:
        """Merge instance-level *config* with per-call **kwargs*.

        Per-call values take precedence over instance-level defaults.

        Args:
            **kwargs: Per-call overrides.

        Returns:
            Merged configuration dictionary.
        """
        merged = dict(self.config)
        merged.update(kwargs)
        return merged

    def _track_usage(self, tokens: int = 0) -> None:
        """Update internal usage counters.

        Args:
            tokens: Number of tokens consumed by the latest request.
        """
        self._request_count += 1
        self._total_tokens_used += tokens

    @property
    def usage_summary(self) -> Dict[str, Any]:
        """Return a snapshot of accumulated usage statistics.

        Returns:
            Dictionary with keys ``request_count``, ``total_tokens``,
            ``uptime_seconds``.
        """
        return {
            "provider": self.get_provider_name(),
            "model": self.model,
            "request_count": self._request_count,
            "total_tokens": self._total_tokens_used,
            "uptime_seconds": round(time.time() - self._created_at, 2),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.get_provider_name()}(model={self.model!r}, "
            f"requests={self._request_count})>"
        )
