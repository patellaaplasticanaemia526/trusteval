# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Rate-limiting middleware using slowapi.

Limits:
    * ``POST /api/evaluations/run`` — 10 requests / minute per IP.
    * All other ``GET /api/*`` endpoints — 100 requests / minute per IP.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# ---------------------------------------------------------------------------
# Limiter singleton — importable by routers that need custom limits.
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Return a JSON 429 response when a rate limit is exceeded.

    Args:
        request: The triggering request.
        exc: The rate-limit exception raised by slowapi.

    Returns:
        A ``429 Too Many Requests`` JSON response.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": str(exc.detail),
        },
    )
