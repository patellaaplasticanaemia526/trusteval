# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""OpenAI provider implementation using the openai SDK v1.x.

Supports both synchronous and asynchronous generation, token counting,
cost estimation, and automatic retry on rate-limit errors.
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
# Keys: model prefix -> (prompt_cost_per_1k, completion_cost_per_1k).
_PRICING: Dict[str, tuple[float, float]] = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4-turbo": (0.01, 0.03),
    "gpt-4": (0.03, 0.06),
    "gpt-3.5-turbo-16k": (0.003, 0.004),
    "gpt-3.5-turbo": (0.0015, 0.002),
}


class OpenAIProvider(BaseProvider):
    """Provider connector for the OpenAI Chat Completions API.

    Uses the ``openai`` Python SDK >= 1.0.  Both sync
    (``provider.generate()``) and async (``provider.agenerate()``)
    interfaces are provided.

    Attributes:
        SUPPORTED_MODELS: List of model identifiers accepted by this
            provider.

    Example::

        provider = OpenAIProvider(
            api_key="sk-...",
            model="gpt-4o",
            config={"temperature": 0.7, "max_tokens": 512},
        )
        answer = provider.generate("What is 2 + 2?")
    """

    SUPPORTED_MODELS: List[str] = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]

    def __init__(
        self,
        api_key: str,
        model: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the OpenAI provider.

        Args:
            api_key: OpenAI API key (usually starts with ``sk-``).
            model: One of the ``SUPPORTED_MODELS``.
            config: Optional generation defaults (``temperature``,
                ``max_tokens``, ``top_p``, etc.).

        Raises:
            ProviderAuthenticationError: If *api_key* is empty.
            ProviderModelError: If *model* is not supported.
            ImportError: If the ``openai`` package is not installed.
        """
        super().__init__(api_key=api_key, model=model, config=config)

        try:
            import openai  # noqa: F811
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for OpenAIProvider. "
                "Install it with: pip install openai>=1.0"
            ) from exc

        self._client = openai.OpenAI(api_key=self.api_key)
        self._async_client = openai.AsyncOpenAI(api_key=self.api_key)

    # ------------------------------------------------------------------
    # Synchronous generation
    # ------------------------------------------------------------------

    @default_retry
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a chat completion synchronously.

        Args:
            prompt: User message text.
            **kwargs: Overrides for ``temperature``, ``max_tokens``,
                ``top_p``, ``system`` (system message), etc.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            ProviderRateLimitError: On HTTP 429.
            ProviderAuthenticationError: On HTTP 401 / 403.
            ProviderError: On any other API failure.
        """
        import openai as _openai

        params = self._build_params(prompt, **kwargs)
        try:
            response = self._client.chat.completions.create(**params)
        except _openai.RateLimitError as exc:
            raise ProviderRateLimitError(
                f"OpenAI rate limit exceeded: {exc}"
            ) from exc
        except _openai.AuthenticationError as exc:
            raise ProviderAuthenticationError(
                f"OpenAI authentication failed: {exc}"
            ) from exc
        except _openai.APIConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to OpenAI: {exc}"
            ) from exc
        except _openai.APIError as exc:
            raise ProviderError(f"OpenAI API error: {exc}") from exc

        text = response.choices[0].message.content or ""
        self._record_response(response)
        return text

    @default_retry
    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate completions for multiple prompts sequentially.

        Args:
            prompts: List of user messages.
            **kwargs: Generation overrides applied to every request.

        Returns:
            List of assistant replies in the same order as *prompts*.
        """
        results: list[str] = []
        for prompt in prompts:
            results.append(self.generate(prompt, **kwargs))
        return results

    # ------------------------------------------------------------------
    # Asynchronous generation
    # ------------------------------------------------------------------

    async def agenerate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a chat completion asynchronously.

        Args:
            prompt: User message text.
            **kwargs: Generation overrides.

        Returns:
            The assistant's reply.

        Raises:
            ProviderRateLimitError: On HTTP 429.
            ProviderAuthenticationError: On HTTP 401 / 403.
            ProviderError: On any other API failure.
        """
        import openai as _openai

        params = self._build_params(prompt, **kwargs)
        try:
            response = await self._async_client.chat.completions.create(**params)
        except _openai.RateLimitError as exc:
            raise ProviderRateLimitError(
                f"OpenAI rate limit exceeded: {exc}"
            ) from exc
        except _openai.AuthenticationError as exc:
            raise ProviderAuthenticationError(
                f"OpenAI authentication failed: {exc}"
            ) from exc
        except _openai.APIConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to OpenAI: {exc}"
            ) from exc
        except _openai.APIError as exc:
            raise ProviderError(f"OpenAI API error: {exc}") from exc

        text = response.choices[0].message.content or ""
        self._record_response(response)
        return text

    async def agenerate_batch(
        self, prompts: list[str], **kwargs: Any
    ) -> list[str]:
        """Generate completions concurrently for multiple prompts.

        Uses ``asyncio.gather`` for concurrency; callers should manage
        concurrency limits externally if needed.

        Args:
            prompts: List of user messages.
            **kwargs: Generation overrides.

        Returns:
            List of replies matching the input order.
        """
        tasks = [self.agenerate(prompt, **kwargs) for prompt in prompts]
        return list(await asyncio.gather(*tasks))

    # ------------------------------------------------------------------
    # Token counting & cost estimation
    # ------------------------------------------------------------------

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in *text* for the active model.

        Uses ``tiktoken`` when available; falls back to a rough
        word-based heuristic.

        Args:
            text: The input string to tokenise.

        Returns:
            Estimated token count.
        """
        try:
            import tiktoken

            try:
                encoding = tiktoken.encoding_for_model(self.model)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Rough heuristic: ~4 characters per token on average.
            return max(1, len(text) // 4)

    def estimate_cost(
        self, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Estimate the cost in USD for a request.

        Args:
            prompt_tokens: Number of prompt (input) tokens.
            completion_tokens: Number of completion (output) tokens.

        Returns:
            Estimated cost in US dollars.
        """
        # Find the best matching pricing entry.
        pricing = _PRICING.get(self.model)
        if pricing is None:
            for prefix, costs in _PRICING.items():
                if self.model.startswith(prefix):
                    pricing = costs
                    break
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
    # Connectivity check
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check whether the OpenAI API is reachable.

        Sends a minimal models-list request. Returns ``True`` on success,
        ``False`` otherwise.
        """
        try:
            self._client.models.list()
            return True
        except Exception:
            logger.debug("OpenAI availability check failed", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_params(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Assemble the parameters dict for a chat completion call.

        Args:
            prompt: User message.
            **kwargs: Per-call overrides.

        Returns:
            Dict ready for ``client.chat.completions.create()``.
        """
        merged = self._merge_config(**kwargs)

        system_message = merged.pop("system", None)
        messages: list[Dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        # Forward recognised generation params.
        for key in ("temperature", "max_tokens", "top_p", "frequency_penalty",
                     "presence_penalty", "stop", "n", "seed"):
            if key in merged:
                params[key] = merged[key]

        return params

    def _record_response(self, response: Any) -> None:
        """Extract usage information from an API response and update counters.

        Args:
            response: The ``ChatCompletion`` response object.
        """
        usage = getattr(response, "usage", None)
        if usage:
            total = getattr(usage, "total_tokens", 0) or 0
            self._track_usage(tokens=total)

            prompt_tok = getattr(usage, "prompt_tokens", 0) or 0
            completion_tok = getattr(usage, "completion_tokens", 0) or 0
            cost = self.estimate_cost(prompt_tok, completion_tok)
            logger.debug(
                "OpenAI usage — prompt: %d, completion: %d, cost: $%.6f",
                prompt_tok,
                completion_tok,
                cost,
            )
