# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Input validation helpers used across the TrustEval SDK.

Each validator either returns the (possibly normalised) value on success or
raises ``trusteval.utils.exceptions.ValidationError`` with a descriptive
message.
"""

from __future__ import annotations

from typing import Any

from trusteval.utils.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_PILLARS: frozenset[str] = frozenset(
    {"hallucination", "bias", "pii", "toxicity"}
)

VALID_PROVIDERS: frozenset[str] = frozenset(
    {"openai", "anthropic", "google", "huggingface", "groq", "xai", "local"}
)

VALID_INDUSTRIES: frozenset[str] = frozenset(
    {"healthcare", "finance", "legal", "education", "general", "hr", "insurance"}
)


# ---------------------------------------------------------------------------
# Public validators
# ---------------------------------------------------------------------------


def validate_score(value: Any, field: str = "score") -> float:
    """Validate that *value* is a float in the range ``[0.0, 1.0]``.

    Args:
        value: The score to validate.
        field: Name used in the error message when validation fails.

    Returns:
        The validated score as a ``float``.

    Raises:
        ValidationError: If *value* is not numeric or outside [0, 1].
    """
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"{field} must be a number, got {type(value).__name__}",
            field=field,
            value=value,
        ) from exc

    if not (0.0 <= score <= 1.0):
        raise ValidationError(
            f"{field} must be between 0.0 and 1.0, got {score}",
            field=field,
            value=value,
        )
    return score


def validate_pillar_name(name: Any) -> str:
    """Validate and normalise a pillar name.

    Args:
        name: Pillar name string (case-insensitive).

    Returns:
        The normalised (lower-case) pillar name.

    Raises:
        ValidationError: If *name* is not one of the known pillars.
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Pillar name must be a string, got {type(name).__name__}",
            field="pillar",
            value=name,
        )
    normalised = name.strip().lower()
    if normalised not in VALID_PILLARS:
        raise ValidationError(
            f"Unknown pillar '{normalised}'. Valid pillars: {sorted(VALID_PILLARS)}",
            field="pillar",
            value=name,
        )
    return normalised


def validate_provider_name(name: Any) -> str:
    """Validate and normalise a provider name.

    Args:
        name: Provider name string (case-insensitive).

    Returns:
        The normalised (lower-case) provider name.

    Raises:
        ValidationError: If *name* is not one of the supported providers.
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Provider name must be a string, got {type(name).__name__}",
            field="provider",
            value=name,
        )
    normalised = name.strip().lower()
    if normalised not in VALID_PROVIDERS:
        raise ValidationError(
            f"Unknown provider '{normalised}'. Valid providers: {sorted(VALID_PROVIDERS)}",
            field="provider",
            value=name,
        )
    return normalised


def validate_industry(name: Any) -> str:
    """Validate and normalise an industry name.

    Args:
        name: Industry name string (case-insensitive).

    Returns:
        The normalised (lower-case) industry name.

    Raises:
        ValidationError: If *name* is not one of the supported industries.
    """
    if not isinstance(name, str):
        raise ValidationError(
            f"Industry name must be a string, got {type(name).__name__}",
            field="industry",
            value=name,
        )
    normalised = name.strip().lower()
    if normalised not in VALID_INDUSTRIES:
        raise ValidationError(
            f"Unknown industry '{normalised}'. Valid industries: {sorted(VALID_INDUSTRIES)}",
            field="industry",
            value=name,
        )
    return normalised


def validate_prompts(prompts: Any) -> list[str]:
    """Validate that *prompts* is a non-empty sequence of non-empty strings.

    Args:
        prompts: A single prompt string or a list/tuple of prompt strings.

    Returns:
        A list of validated prompt strings.

    Raises:
        ValidationError: If *prompts* is empty or contains non-string items.
    """
    if isinstance(prompts, str):
        prompts = [prompts]

    if not isinstance(prompts, (list, tuple)):
        raise ValidationError(
            f"Prompts must be a string or list of strings, got {type(prompts).__name__}",
            field="prompts",
            value=prompts,
        )

    if len(prompts) == 0:
        raise ValidationError(
            "Prompts list must not be empty",
            field="prompts",
        )

    validated: list[str] = []
    for idx, p in enumerate(prompts):
        if not isinstance(p, str):
            raise ValidationError(
                f"Prompt at index {idx} must be a string, got {type(p).__name__}",
                field=f"prompts[{idx}]",
                value=p,
            )
        stripped = p.strip()
        if not stripped:
            raise ValidationError(
                f"Prompt at index {idx} must not be empty or whitespace-only",
                field=f"prompts[{idx}]",
            )
        validated.append(stripped)
    return validated
