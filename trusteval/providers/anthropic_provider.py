# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Anthropic provider implementation using the anthropic SDK.

Handles the Claude message format and supports both synchronous and
asynchronous generation with retry on transient failures.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from trusteval.providers.base import (
    BaseProvider,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderRateLimitError,
    default_retry,
)

logger = logging.getLogger(__name__)

# Approximate per-token pricing (USD) as of early 2025.
_PRICING: Dict[str, tuple[float, float]] = {
    "claude-3-opus-20240229": (0.015, 0.075),
    "claude-3-sonnet-20240229": (0.003, 0.015),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
    "claude-2.1": (0.008, 0.024),
}


class AnthropicProvider(BaseProvider):
    """Provider connector for the Anthropic Messages API.

    Uses the ``anthropic`` Python SDK.  Both sync and async interfaces
    are provided.  The Claude message format (``role``/``content`` blocks)
    is handled transparently.

    Attributes:
        SUPPORTED_MODELS: Claude model identifiers accepted by this
            provider.

    Example::

        provider = AnthropicProvider(
            api_key="sk-ant-...",
            model="claude-3-sonnet-20240229",
            config={"max_tokens": 1024},
        )
        answer = provider.generate("Summarise this article.")
    """

    SUPPORTED_MODELS: List[str] = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
    ]

    # Anthropic requires max_tokens; fall back to a sensible default.
    _DEFAULT_MAX_TOKENS: int = 4096

    def __init__(
        self,
        api_key: str,
        model: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the Anthropic provider.

        Args:
            api_key: Anthropic API key.
            model: One of the ``SUPPORTED_MODELS``.
            config: Optional generation defaults (``max_tokens``,
                ``temperature``, ``system``, etc.).

        Raises:
            ProviderAuthenticationError: If *api_key* is empty.
            ProviderModelError: If *model* is not supported.
            ImportError: If the ``anthropic`` package is not installed.
        """
        super().__init__(api_key=api_key, model=model, config=config)

        try:
            import anthropic  # noqa: F811
        except ImportError as exc:
            raise ImportError(
                "The 'anthropic' package is required for AnthropicProvider. "
                "Install it with: pip install anthropic"
            ) from exc

        self._client = anthropic.Anthropic(api_key=self.api_key)
        self._async_client = anthropic.AsyncAnthropic(api_key=self.api_key)

    # ------------------------------------------------------------------
    # Synchronous generation
    # ------------------------------------------------------------------

    @default_retry
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a message completion synchronously.

        Args:
            prompt: User message text.
            **kwargs: Overrides for ``temperature``, ``max_tokens``,
                ``system`` (system prompt), ``top_p``, ``top_k``, etc.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            ProviderRateLimitError: On HTTP 429.
            ProviderAuthenticationError: On HTTP 401 / 403.
            ProviderError: On any other API failure.
        """
        import anthropic as _anthropic

        params = self._build_params(prompt, **kwargs)
        try:
            response = self._client.messages.create(**params)
        except _anthropic.RateLimitError as exc:
            raise ProviderRateLimitError(
                f"Anthropic rate limit exceeded: {exc}"
            ) from exc
        except _anthropic.AuthenticationError as exc:
            raise ProviderAuthenticationError(
                f"Anthropic authentication failed: {exc}"
            ) from exc
        except _anthropic.APIConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to Anthropic: {exc}"
            ) from exc
        except _anthropic.APIError as exc:
            raise ProviderError(f"Anthropic API error: {exc}") from exc

        text = self._extract_text(response)
        self._record_response(response)
        return text

    @default_retry
    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate completions for multiple prompts sequentially.

        Args:
            prompts: List of user messages.
            **kwargs: Generation overrides applied to every request.

        Returns:
            List of assistant replies matching input order.
        """
        return [self.generate(prompt, **kwargs) for prompt in prompts]

    # ------------------------------------------------------------------
    # Asynchronous generation
    # ------------------------------------------------------------------

    async def agenerate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a message completion asynchronously.

        Args:
            prompt: User message text.
            **kwargs: Generation overrides.

        Returns:
            The assistant's reply.
        """
        import anthropic as _anthropic

        params = self._build_params(prompt, **kwargs)
        try:
            response = await self._async_client.messages.create(**params)
        except _anthropic.RateLimitError as exc:
            raise ProviderRateLimitError(
                f"Anthropic rate limit exceeded: {exc}"
            ) from exc
        except _anthropic.AuthenticationError as exc:
            raise ProviderAuthenticationError(
                f"Anthropic authentication failed: {exc}"
            ) from exc
        except _anthropic.APIConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to Anthropic: {exc}"
            ) from exc
        except _anthropic.APIError as exc:
            raise ProviderError(f"Anthropic API error: {exc}") from exc

        text = self._extract_text(response)
        self._record_response(response)
        return text

    async def agenerate_batch(
        self, prompts: list[str], **kwargs: Any
    ) -> list[str]:
        """Generate completions concurrently for multiple prompts.

        Args:
            prompts: List of user messages.
            **kwargs: Generation overrides.

        Returns:
            List of replies matching input order.
        """
        tasks = [self.agenerate(prompt, **kwargs) for prompt in prompts]
        return list(await asyncio.gather(*tasks))

    # ------------------------------------------------------------------
    # Connectivity check
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check whether the Anthropic API is reachable.

        Sends a minimal message request with ``max_tokens=1``.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        try:
            self._client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            logger.debug("Anthropic availability check failed", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Cost estimation
    # ------------------------------------------------------------------

    def estimate_cost(
        self, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Estimate the cost in USD for a request.

        Args:
            prompt_tokens: Number of input tokens.
            completion_tokens: Number of output tokens.

        Returns:
            Estimated cost in US dollars.
        """
        pricing = _PRICING.get(self.model)
        if pricing is None:
            logger.warning(
                "No pricing data for model '%s'; returning 0.0", self.model
            )
            return 0.0

        prompt_cost, completion_cost = pricing
        return (
            (prompt_tokens / 1000) * prompt_cost
            + (completion_tokens / 1000) * completion_cost
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_params(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Assemble parameters for ``messages.create()``.

        Args:
            prompt: User message.
            **kwargs: Per-call overrides.

        Returns:
            Dict ready for the Anthropic SDK call.
        """
        merged = self._merge_config(**kwargs)

        params: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": merged.pop("max_tokens", self._DEFAULT_MAX_TOKENS),
            "messages": [{"role": "user", "content": prompt}],
        }

        # Optional system prompt (Anthropic accepts it as a top-level param).
        system_prompt = merged.pop("system", None)
        if system_prompt:
            params["system"] = system_prompt

        # Forward other recognised params.
        for key in ("temperature", "top_p", "top_k", "stop_sequences",
                     "metadata", "stream"):
            if key in merged:
                params[key] = merged[key]

        return params

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Extract plain text from an Anthropic ``Message`` response.

        The Anthropic SDK returns content as a list of ``ContentBlock``
        objects.  This helper concatenates the ``text`` blocks.

        Args:
            response: The ``Message`` object returned by the SDK.

        Returns:
            Concatenated text content.
        """
        parts: list[str] = []
        for block in getattr(response, "content", []):
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "".join(parts)

    def _record_response(self, response: Any) -> None:
        """Extract usage information and update internal counters.

        Args:
            response: The ``Message`` object returned by the SDK.
        """
        usage = getattr(response, "usage", None)
        if usage:
            input_tok = getattr(usage, "input_tokens", 0) or 0
            output_tok = getattr(usage, "output_tokens", 0) or 0
            total = input_tok + output_tok
            self._track_usage(tokens=total)

            cost = self.estimate_cost(input_tok, output_tok)
            logger.debug(
                "Anthropic usage — input: %d, output: %d, cost: $%.6f",
                input_tok,
                output_tok,
                cost,
            )
