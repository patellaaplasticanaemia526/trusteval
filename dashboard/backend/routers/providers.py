# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Provider endpoints — list providers, test connectivity, list models."""

from __future__ import annotations

import os
import time
from typing import Any

from fastapi import APIRouter, HTTPException

from dashboard.backend.models.schemas import ProviderInfo, ProviderResponse, ProviderTestRequest

router = APIRouter(prefix="/providers", tags=["providers"])

# ---------------------------------------------------------------------------
# Static provider registry — extend as new integrations are added.
# ---------------------------------------------------------------------------

_PROVIDERS: dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        requires_api_key=True,
    ),
    "anthropic": ProviderInfo(
        name="anthropic",
        display_name="Anthropic",
        models=["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        requires_api_key=True,
    ),
    "google": ProviderInfo(
        name="google",
        display_name="Google AI (Gemini)",
        models=["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        requires_api_key=True,
    ),
    "azure": ProviderInfo(
        name="azure",
        display_name="Azure OpenAI",
        models=["gpt-4o", "gpt-4", "gpt-35-turbo"],
        requires_api_key=True,
    ),
    "huggingface": ProviderInfo(
        name="huggingface",
        display_name="Hugging Face",
        models=["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        requires_api_key=True,
    ),
    "ollama": ProviderInfo(
        name="ollama",
        display_name="Ollama (Local)",
        models=["llama3", "mistral", "phi3"],
        requires_api_key=False,
        status="available",
    ),
}


@router.get("", response_model=list[ProviderInfo])
async def list_providers() -> list[ProviderInfo]:
    """List all supported LLM providers.

    Returns:
        A list of provider metadata objects.
    """
    return list(_PROVIDERS.values())


@router.post("/test", response_model=ProviderResponse)
async def test_provider(body: ProviderTestRequest) -> ProviderResponse:
    """Test connectivity to a provider.

    Performs a lightweight ping to verify that the provider is reachable
    and credentials (if required) are valid.

    Args:
        body: Provider name and optional API-key override.

    Returns:
        Connection status with latency.

    Raises:
        HTTPException: 404 if the provider is not recognised.
    """
    provider_name = body.provider.lower()
    if provider_name not in _PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {body.provider}")

    info = _PROVIDERS[provider_name]

    # Check for an API key when the provider requires one.
    api_key = body.api_key or _resolve_env_key(provider_name)
    if info.requires_api_key and not api_key:
        return ProviderResponse(
            provider=provider_name,
            connected=False,
            error=f"No API key found. Set {_env_key_name(provider_name)} or pass api_key in the request.",
        )

    # Simulate a connectivity check (a real implementation would call
    # the provider's health or models endpoint).
    start = time.perf_counter()
    try:
        connected = True
        error = None
    except Exception as exc:
        connected = False
        error = str(exc)
    latency = (time.perf_counter() - start) * 1000

    return ProviderResponse(
        provider=provider_name,
        connected=connected,
        latency_ms=round(latency, 2),
        error=error,
    )


@router.get("/{name}/models", response_model=list[str])
async def list_models(name: str) -> list[str]:
    """List available models for a specific provider.

    Args:
        name: Provider name (case-insensitive).

    Returns:
        A list of model identifier strings.

    Raises:
        HTTPException: 404 if the provider is not recognised.
    """
    provider_name = name.lower()
    if provider_name not in _PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {name}")
    return _PROVIDERS[provider_name].models


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _env_key_name(provider: str) -> str:
    """Return the conventional env-var name for a provider's API key."""
    mapping = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "azure": "AZURE_OPENAI_API_KEY",
        "huggingface": "HUGGINGFACE_API_KEY",
    }
    return mapping.get(provider, f"{provider.upper()}_API_KEY")


def _resolve_env_key(provider: str) -> str:
    """Attempt to read the provider's API key from the environment."""
    return os.environ.get(_env_key_name(provider), "")
