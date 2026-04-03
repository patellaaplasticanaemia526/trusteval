# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""HuggingFace provider supporting both remote Inference API and local
model loading via the ``transformers`` library.

Auto-detection logic:
  - Paths starting with ``./`` or ``/`` or containing ``\\`` are treated as
    **local** models loaded via ``transformers.pipeline``.
  - All other identifiers (e.g. ``"meta-llama/Llama-2-7b-chat-hf"``) are
    sent to the **HuggingFace Inference API**.
"""

from __future__ import annotations

import logging
import os
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

_HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/{model}"


def _is_local_path(model: str) -> bool:
    """Determine whether *model* refers to a local filesystem path.

    Args:
        model: Model identifier or path.

    Returns:
        ``True`` if *model* looks like a filesystem path.
    """
    return (
        model.startswith("./")
        or model.startswith("/")
        or model.startswith("..\\")
        or model.startswith(".\\")
        or os.sep == "\\" and "\\" in model
        or os.path.isdir(model)
    )


class HuggingFaceProvider(BaseProvider):
    """Provider connector supporting HuggingFace models.

    Operates in one of two modes, chosen automatically based on the
    *model* string:

    * **Remote** — calls the `HuggingFace Inference API
      <https://huggingface.co/docs/api-inference/>`_ using a simple
      HTTP client (``requests``).
    * **Local** — loads the model and tokeniser from disk using
      ``transformers.pipeline("text-generation", ...)``.

    The ``SUPPORTED_MODELS`` list is intentionally left empty because
    HuggingFace hosts tens of thousands of models; validation is
    performed at call time instead.

    Example (remote)::

        provider = HuggingFaceProvider(
            api_key="hf_...",
            model="meta-llama/Llama-2-7b-chat-hf",
        )
        answer = provider.generate("What is gravity?")

    Example (local)::

        provider = HuggingFaceProvider(
            api_key="unused",
            model="./local_models/my-finetuned-llama",
            config={"max_new_tokens": 256, "device": "cuda"},
        )
        answer = provider.generate("Summarise this document.")
    """

    SUPPORTED_MODELS: List[str] = []  # Open-ended; validated at runtime.

    def __init__(
        self,
        api_key: str,
        model: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the HuggingFace provider.

        For **local** models the *api_key* is not used for authentication
        but must still be a non-empty string (pass any placeholder value).

        Args:
            api_key: HuggingFace API token for remote inference, or a
                placeholder string for local models.
            model: A HuggingFace Hub identifier (``"org/model"``) for
                remote mode, or a filesystem path for local mode.
            config: Optional generation defaults (``max_new_tokens``,
                ``temperature``, ``device``, etc.).

        Raises:
            ProviderAuthenticationError: If *api_key* is empty.
            ImportError: If required packages are missing.
        """
        # BaseProvider validates api_key and model against SUPPORTED_MODELS.
        # Since SUPPORTED_MODELS is empty the model check is skipped.
        # We still need a non-empty api_key for the base-class guard;
        # for local models callers can pass a dummy value.
        if not api_key:
            raise ProviderAuthenticationError(
                "HuggingFaceProvider requires a non-empty api_key "
                "(use a placeholder for local models)."
            )

        # Skip BaseProvider.__init__'s model validation by setting
        # attributes directly – we validate mode-specific requirements below.
        self.api_key = api_key
        self.model = model
        self.config: Dict[str, Any] = config or {}
        self._request_count = 0
        self._total_tokens_used = 0

        import time
        self._created_at = time.time()

        self._is_local: bool = _is_local_path(model)
        self._pipeline: Any = None  # Lazy-loaded for local models.
        self._session: Any = None  # Lazy-loaded requests.Session for remote.

        if self._is_local:
            logger.info(
                "HuggingFaceProvider initialised in LOCAL mode: %s", model
            )
        else:
            logger.info(
                "HuggingFaceProvider initialised in REMOTE mode: %s", model
            )

    # ------------------------------------------------------------------
    # Synchronous generation
    # ------------------------------------------------------------------

    @default_retry
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text from the model.

        Dispatches to the remote Inference API or a local
        ``transformers`` pipeline based on the model identifier.

        Args:
            prompt: User message / instruction.
            **kwargs: Generation overrides (``max_new_tokens``,
                ``temperature``, ``top_p``, etc.).

        Returns:
            Generated text string.

        Raises:
            ProviderRateLimitError: On HTTP 429 from the Inference API.
            ProviderAuthenticationError: On HTTP 401 / 403.
            ProviderConnectionError: On network failures.
            ProviderError: On any other failure.
        """
        if self._is_local:
            return self._generate_local(prompt, **kwargs)
        return self._generate_remote(prompt, **kwargs)

    @default_retry
    def generate_batch(self, prompts: list[str], **kwargs: Any) -> list[str]:
        """Generate completions for multiple prompts.

        Local mode leverages the pipeline's native batching support.
        Remote mode iterates sequentially.

        Args:
            prompts: List of prompt strings.
            **kwargs: Generation overrides.

        Returns:
            List of generated strings.
        """
        if self._is_local:
            return self._generate_batch_local(prompts, **kwargs)
        return [self.generate(prompt, **kwargs) for prompt in prompts]

    # ------------------------------------------------------------------
    # Connectivity check
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check provider availability.

        For remote mode, pings the Inference API endpoint.  For local
        mode, verifies the model directory exists and is loadable.

        Returns:
            ``True`` if the provider is ready to serve requests.
        """
        if self._is_local:
            return os.path.isdir(self.model)

        try:
            import requests

            url = _HF_INFERENCE_URL.format(model=self.model)
            resp = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            return resp.status_code in (200, 503)  # 503 = model loading
        except Exception:
            logger.debug("HuggingFace availability check failed", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Remote (Inference API) helpers
    # ------------------------------------------------------------------

    def _get_session(self) -> Any:
        """Return a ``requests.Session`` with auth headers, creating one
        lazily.

        Returns:
            Configured ``requests.Session``.
        """
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session

    def _generate_remote(self, prompt: str, **kwargs: Any) -> str:
        """Send a prompt to the HuggingFace Inference API.

        Args:
            prompt: User message.
            **kwargs: Generation overrides.

        Returns:
            Generated text.
        """
        import requests as _requests

        merged = self._merge_config(**kwargs)
        url = _HF_INFERENCE_URL.format(model=self.model)

        payload: Dict[str, Any] = {"inputs": prompt}
        parameters: Dict[str, Any] = {}
        for key in (
            "max_new_tokens",
            "temperature",
            "top_p",
            "top_k",
            "repetition_penalty",
            "do_sample",
            "return_full_text",
        ):
            if key in merged:
                parameters[key] = merged[key]

        # Default: do not echo the prompt back.
        parameters.setdefault("return_full_text", False)
        if parameters:
            payload["parameters"] = parameters

        # Allow waiting for model to load (cold-start).
        wait_for_model = merged.get("wait_for_model", True)
        if wait_for_model:
            payload["options"] = {"wait_for_model": True}

        session = self._get_session()
        timeout = merged.get("timeout", 120)

        try:
            resp = session.post(url, json=payload, timeout=timeout)
        except _requests.ConnectionError as exc:
            raise ProviderConnectionError(
                f"Could not connect to HuggingFace: {exc}"
            ) from exc
        except _requests.Timeout as exc:
            raise ProviderConnectionError(
                f"HuggingFace request timed out: {exc}"
            ) from exc

        if resp.status_code == 429:
            raise ProviderRateLimitError(
                f"HuggingFace rate limit exceeded: {resp.text}"
            )
        if resp.status_code in (401, 403):
            raise ProviderAuthenticationError(
                f"HuggingFace authentication failed ({resp.status_code}): "
                f"{resp.text}"
            )
        if resp.status_code != 200:
            raise ProviderError(
                f"HuggingFace API error ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        text = self._parse_remote_response(data)
        self._track_usage()
        return text

    @staticmethod
    def _parse_remote_response(data: Any) -> str:
        """Parse the JSON response from the Inference API.

        The API returns different shapes depending on the model type.
        This method handles the common cases:
        - ``[{"generated_text": "..."}]``
        - ``[{"generated_text": ["..."]}]``
        - raw string

        Args:
            data: Parsed JSON response.

        Returns:
            Extracted text.

        Raises:
            ProviderError: If the response cannot be parsed.
        """
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            if isinstance(item, dict):
                gen_text = item.get("generated_text", "")
                if isinstance(gen_text, list):
                    return str(gen_text[0]) if gen_text else ""
                return str(gen_text)
            return str(item)
        if isinstance(data, dict):
            if "error" in data:
                raise ProviderError(f"HuggingFace API error: {data['error']}")
            return str(data.get("generated_text", ""))
        if isinstance(data, str):
            return data

        raise ProviderError(
            f"Unexpected HuggingFace response format: {type(data)}"
        )

    # ------------------------------------------------------------------
    # Local (transformers pipeline) helpers
    # ------------------------------------------------------------------

    def _get_pipeline(self) -> Any:
        """Return the ``transformers`` text-generation pipeline, loading
        it lazily on first use.

        Returns:
            A ``transformers.Pipeline`` instance.

        Raises:
            ImportError: If ``transformers`` or ``torch`` is missing.
            ProviderError: If the model cannot be loaded.
        """
        if self._pipeline is not None:
            return self._pipeline

        try:
            import torch  # noqa: F401
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError as exc:
            raise ImportError(
                "The 'transformers' and 'torch' packages are required for "
                "local HuggingFace models.  Install them with: "
                "pip install transformers torch"
            ) from exc

        device = self.config.get("device", "cpu")
        torch_dtype_str = self.config.get("torch_dtype", "auto")

        # Resolve dtype string.
        dtype_map = {
            "auto": "auto",
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(torch_dtype_str, "auto")

        logger.info("Loading local model from %s (device=%s)...", self.model, device)

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model)  # nosec B615
            model = AutoModelForCausalLM.from_pretrained(  # nosec B615
                self.model,
                torch_dtype=torch_dtype,
                device_map=device if device != "cpu" else None,
            )
            self._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=None if device != "cpu" and model.device.type != "cpu" else device,
            )
        except Exception as exc:
            raise ProviderError(
                f"Failed to load local model from '{self.model}': {exc}"
            ) from exc

        logger.info("Local model loaded successfully.")
        return self._pipeline

    def _generate_local(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using a local ``transformers`` pipeline.

        Args:
            prompt: User message.
            **kwargs: Generation overrides.

        Returns:
            Generated text.
        """
        merged = self._merge_config(**kwargs)
        pipe = self._get_pipeline()

        gen_kwargs: Dict[str, Any] = {}
        for key in (
            "max_new_tokens",
            "temperature",
            "top_p",
            "top_k",
            "do_sample",
            "repetition_penalty",
            "num_return_sequences",
        ):
            if key in merged:
                gen_kwargs[key] = merged[key]

        gen_kwargs.setdefault("max_new_tokens", 256)

        try:
            outputs = pipe(prompt, **gen_kwargs)
        except Exception as exc:
            raise ProviderError(
                f"Local generation failed: {exc}"
            ) from exc

        if outputs and isinstance(outputs, list):
            text = outputs[0].get("generated_text", "")
            # The pipeline echoes the prompt by default; strip it.
            if text.startswith(prompt):
                text = text[len(prompt):]
            self._track_usage()
            return text.strip()

        raise ProviderError("Local pipeline returned an empty result.")

    def _generate_batch_local(
        self, prompts: list[str], **kwargs: Any
    ) -> list[str]:
        """Generate for multiple prompts using the local pipeline's
        native batching.

        Args:
            prompts: List of prompt strings.
            **kwargs: Generation overrides.

        Returns:
            List of generated strings.
        """
        merged = self._merge_config(**kwargs)
        pipe = self._get_pipeline()

        gen_kwargs: Dict[str, Any] = {}
        for key in (
            "max_new_tokens",
            "temperature",
            "top_p",
            "top_k",
            "do_sample",
            "repetition_penalty",
        ):
            if key in merged:
                gen_kwargs[key] = merged[key]
        gen_kwargs.setdefault("max_new_tokens", 256)

        try:
            outputs = pipe(prompts, **gen_kwargs)
        except Exception as exc:
            raise ProviderError(
                f"Local batch generation failed: {exc}"
            ) from exc

        results: list[str] = []
        for idx, output_group in enumerate(outputs):
            if isinstance(output_group, list) and output_group:
                text = output_group[0].get("generated_text", "")
            elif isinstance(output_group, dict):
                text = output_group.get("generated_text", "")
            else:
                text = ""
            # Strip echoed prompt.
            if text.startswith(prompts[idx]):
                text = text[len(prompts[idx]):]
            results.append(text.strip())
            self._track_usage()

        return results
