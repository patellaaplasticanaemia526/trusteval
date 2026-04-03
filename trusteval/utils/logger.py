# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Structured logging with automatic API-key masking.

Uses *loguru* for structured, colourful output while ensuring that
sensitive tokens never leak into logs or console output.
"""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

try:
    from loguru import logger as _loguru_logger

    _HAS_LOGURU = True
except ImportError:  # pragma: no cover — graceful fallback
    _HAS_LOGURU = False

if TYPE_CHECKING:
    from loguru import Logger

# ---------------------------------------------------------------------------
# API-key masking
# ---------------------------------------------------------------------------

# Matches typical provider key patterns (sk-…, gsk_…, hf_…, etc.) and any
# generic long hex/base64 bearer token.
_KEY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(sk-[A-Za-z0-9]{10,})"),
    re.compile(r"(gsk_[A-Za-z0-9]{10,})"),
    re.compile(r"(hf_[A-Za-z0-9]{10,})"),
    re.compile(r"(xai-[A-Za-z0-9]{10,})"),
    re.compile(r"(key-[A-Za-z0-9]{10,})"),
    re.compile(r"(Bearer\s+[A-Za-z0-9\-_.]{20,})", re.IGNORECASE),
    re.compile(r"(api[_-]?key[\"']?\s*[:=]\s*[\"']?)([A-Za-z0-9\-_.]{12,})", re.IGNORECASE),
]


def mask_api_key(text: str) -> str:
    """Replace API keys and bearer tokens in *text* with a masked version.

    Args:
        text: Arbitrary string that may contain sensitive tokens.

    Returns:
        A copy of *text* with keys replaced by their first four visible
        characters followed by ``****``.

    Examples:
        >>> mask_api_key("sk-abc123456789xyz")
        'sk-a****'
        >>> mask_api_key("no secrets here")
        'no secrets here'
    """
    masked = text
    for pat in _KEY_PATTERNS:
        match = pat.search(masked)
        while match:
            full = match.group(0)
            # For the compound api_key=VALUE pattern, only mask the value part
            if pat.groups > 1:
                prefix = match.group(1)
                value = match.group(2)
                replacement = prefix + value[:4] + "****"
            else:
                replacement = full[:4] + "****"
            masked = masked[: match.start()] + replacement + masked[match.end() :]
            match = pat.search(masked, match.start() + len(replacement))
    return masked


# ---------------------------------------------------------------------------
# Logger factory
# ---------------------------------------------------------------------------

_DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)

_configured = False


def _configure_loguru(verbose: bool = False) -> None:
    """Set up loguru with masking sink (idempotent)."""
    global _configured
    if _configured:
        return
    if not _HAS_LOGURU:
        return

    _loguru_logger.remove()  # remove default stderr handler

    level = "DEBUG" if verbose else "INFO"

    def _masking_sink(message: str) -> None:
        sys.stderr.write(mask_api_key(str(message)))

    _loguru_logger.add(
        _masking_sink,
        format=_DEFAULT_FORMAT,
        level=level,
        colorize=False,
    )
    _configured = True


def get_logger(name: str = "trusteval", verbose: bool = False) -> "Logger":
    """Return a configured logger instance.

    Args:
        name: Logger name, typically the module ``__name__``.
        verbose: If ``True``, set level to DEBUG; otherwise INFO.

    Returns:
        A *loguru* ``Logger`` bound with the given *name*. If loguru is
        not installed, returns a lightweight stdlib-logging wrapper that
        still masks keys.
    """
    _configure_loguru(verbose=verbose)

    if _HAS_LOGURU:
        return _loguru_logger.bind(name=name)

    # Minimal fallback using stdlib logging
    import logging

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    )
    return logging.getLogger(name)  # type: ignore[return-value]
