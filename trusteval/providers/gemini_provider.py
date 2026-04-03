# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Google Gemini provider implementation using the google-generativeai SDK.

Supports synchronous and asynchronous generation for the Gemini family
of models with retry logic on transient failures.
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


class GeminiProvider(BaseProvider):
    """Provider connector for the Google Gemini (Generative AI) API.

    Uses the ``google-generativeai`` Python SDK.  Generation parameters
    such as ``temperature`` and ``max_output_tokens`` are forwarded via
    a ``GenerationConfig`` object.

    Attributes:
        SUPPORTED_MODELS: Gemini model identifiers accepted by this
            provider.

    Example::

        provider = GeminiProvider(
            api_key="AIza...",
            model="gemini-1.5-pro",
            config={"temperature": 0.5, "max_output_tokens": 1024},
        )
        answer = provider.generate("Explain relativity in simple terms.")
    """

    SUPPORTED_MODELS: List[str] = [
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]

    def __init__(
        self,
        api_key: str,
        model: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the Gemini provider.

        Args:
            api_key: Google AI API key.
            model: One of the ``SUPPORTED_MODELS``.
            config: Optional generation defaults (``temperature``,
                ``max_output_tokens``, ``top_p``, ``top_k``, etc.).

        Raises:
            ProviderAuthenticationError: If *api_key* is empty.
            ProviderModelError: If *model* is not supported.
            ImportError: If ``google-generativeai`` is not installed.
        """
        super().__init__(api_key=api_key, model=model, config=config)

        try:
            import google.generativeai as genai  # noqa: F811
        except ImportError as exc:
            raise ImportError(
                "The 'google-generativeai' package is required for "
                "GeminiProvider.  Install it with: "
                "pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self.api_key)
        self._genai = genai
        self._model_instance = genai.GenerativeModel(model_name=self.model)

    # ------------------------------------------------------------------
    # Synchronous generation
    # ------------------------------------------------------------------

    @default_retry
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate content synchronously.

        Args:
            prompt: User message text.
            **kwargs: Overrides for ``temperature``, ``max_output_tokens``,
                ``top_p``, ``top_k``, ``system`` (system instruction), etc.

        Returns:
            The model's reply as a plain string.

        Raises:
            ProviderRateLimitError: On resource-exhausted / 429 errors.
            ProviderAuthenticationError: On permission / auth errors.
            ProviderError: On any other API failure.
        """
        generation_config, system_instruction = self._build_generation_config(
            **kwargs
        )

        model = self._get_model(system_instruction)

        try:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
            )
        except Exception as exc:
            self._raise_mapped(exc)

        text = self._extract_text(response)

        # Track usage if available.
        usage_meta = getattr(response, "usage_metadata", None)
        if usage_meta:
            total = (
                getattr(usage_meta, "prompt_token_count", 0)
                + getattr(usage_meta, "candidates_token_count", 0)
            )
            self._track_usage(tokens=total)

        return text

    @default_retry
    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate completions for multiple prompts sequentially.

        Args:
            prompts: List of user messages.
            **kwargs: Generation overrides applied to every request.

        Returns:
            List of model replies matching input order.
        """
        return [self.generate(prompt, **kwargs) for prompt in prompts]

    # ------------------------------------------------------------------
    # Asynchronous generation
    # ------------------------------------------------------------------

    async def agenerate(self, prompt: str, **kwargs: Any) -> str:
        """Generate content asynchronously.

        The ``google-generativeai`` SDK exposes
        ``generate_content_async`` for non-blocking calls.

        Args:
            prompt: User message text.
            **kwargs: Generation overrides.

        Returns:
            The model's reply.
        """
        generation_config, system_instruction = self._build_generation_config(
            **kwargs
        )
        model = self._get_model(system_instruction)

        try:
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )
        except Exception as exc:
            self._raise_mapped(exc)

        text = self._extract_text(response)

        usage_meta = getattr(response, "usage_metadata", None)
        if usage_meta:
            total = (
                getattr(usage_meta, "prompt_token_count", 0)
                + getattr(usage_meta, "candidates_token_count", 0)
            )
            self._track_usage(tokens=total)

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
        """Check whether the Gemini API is reachable.

        Sends a minimal generation request and checks for a valid
        response.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        try:
            response = self._model_instance.generate_content(
                "ping",
                generation_config=self._genai.GenerationConfig(
                    max_output_tokens=1
                ),
            )
            return bool(response)
        except Exception:
            logger.debug("Gemini availability check failed", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_generation_config(
        self, **kwargs: Any
    ) -> tuple[Any, Optional[str]]:
        """Build a ``GenerationConfig`` from merged settings.

        Args:
            **kwargs: Per-call overrides.

        Returns:
            A tuple of (``GenerationConfig``, optional system instruction).
        """
        merged = self._merge_config(**kwargs)
        system_instruction = merged.pop("system", None)

        config_kwargs: Dict[str, Any] = {}
        for key in (
            "temperature",
            "max_output_tokens",
            "top_p",
            "top_k",
            "candidate_count",
            "stop_sequences",
        ):
            if key in merged:
                config_kwargs[key] = merged[key]

        generation_config = self._genai.GenerationConfig(**config_kwargs)
        return generation_config, system_instruction

    def _get_model(self, system_instruction: Optional[str] = None) -> Any:
        """Return a ``GenerativeModel`` instance, optionally with a system
        instruction.

        If *system_instruction* is ``None``, the pre-built instance is
        reused to avoid unnecessary object creation.

        Args:
            system_instruction: Optional system-level prompt.

        Returns:
            A ``GenerativeModel`` object.
        """
        if system_instruction:
            return self._genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
            )
        return self._model_instance

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Extract plain text from a Gemini response.

        Handles both single-candidate and multi-part responses.

        Args:
            response: The response object from ``generate_content``.

        Returns:
            Concatenated text content.

        Raises:
            ProviderError: If no text content could be extracted (e.g.
                the response was blocked by safety filters).
        """
        try:
            return response.text
        except ValueError:
            pass

        # Attempt to concatenate text parts from the first candidate.
        candidates = getattr(response, "candidates", None)
        if candidates:
            parts = getattr(candidates[0].content, "parts", [])
            texts = [p.text for p in parts if hasattr(p, "text")]
            if texts:
                return "".join(texts)

        # Check for safety-filter blocks.
        prompt_feedback = getattr(response, "prompt_feedback", None)
        if prompt_feedback:
            block_reason = getattr(prompt_feedback, "block_reason", None)
            if block_reason:
                raise ProviderError(
                    f"Gemini blocked the request: {block_reason}"
                )

        raise ProviderError(
            "Gemini returned an empty or unparseable response."
        )

    @staticmethod
    def _raise_mapped(exc: Exception) -> None:
        """Map Google SDK exceptions to TrustEval provider exceptions.

        Args:
            exc: The original exception from the SDK.

        Raises:
            ProviderRateLimitError: On resource-exhausted errors.
            ProviderAuthenticationError: On permission errors.
            ProviderConnectionError: On connectivity errors.
            ProviderError: On all other errors.
        """
        exc_name = type(exc).__name__.lower()
        exc_str = str(exc).lower()

        if "resourceexhausted" in exc_name or "429" in exc_str:
            raise ProviderRateLimitError(
                f"Gemini rate limit exceeded: {exc}"
            ) from exc
        if "permissiondenied" in exc_name or "403" in exc_str or "401" in exc_str:
            raise ProviderAuthenticationError(
                f"Gemini authentication failed: {exc}"
            ) from exc
        if "unavailable" in exc_name or "connection" in exc_name:
            raise ProviderConnectionError(
                f"Could not connect to Gemini: {exc}"
            ) from exc

        raise ProviderError(f"Gemini API error: {exc}") from exc
