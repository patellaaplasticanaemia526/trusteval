# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""API-key authentication middleware.

Reads ``TRUSTEVAL_DASHBOARD_KEY`` from the environment and validates
incoming requests against the ``X-TrustEval-Key`` header. Routes under
``/api/health`` and ``/api/docs`` are exempted so monitoring and
documentation remain publicly reachable.

If no key is configured the middleware logs a warning and allows all
traffic through (local-only insecure mode).
"""

from __future__ import annotations

import logging
import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("trusteval.auth")

# Paths that never require authentication.
_PUBLIC_PREFIXES = (
    "/api/health",
    "/api/docs",
    "/api/redoc",
    "/openapi.json",
)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Enforce API-key authentication on protected endpoints.

    Args:
        app: The ASGI application to wrap.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Check the API key header before forwarding the request.

        Args:
            request: The inbound HTTP request.
            call_next: Callable to forward the request down the middleware stack.

        Returns:
            The downstream response, or a 401/403 JSON error.
        """
        # Allow public paths through without auth.
        path = request.url.path
        if any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES):
            return await call_next(request)

        # Allow WebSocket upgrade requests (auth handled at connection time).
        if request.headers.get("upgrade", "").lower() == "websocket":
            return await call_next(request)

        api_key = os.environ.get("TRUSTEVAL_DASHBOARD_KEY", "")

        if not api_key:
            # No key configured — local-only insecure mode.
            logger.warning(
                "TRUSTEVAL_DASHBOARD_KEY is not set. Running in local-only insecure mode. "
                "Set the environment variable to enable authentication."
            )
            return await call_next(request)

        provided_key = request.headers.get("X-TrustEval-Key", "")

        if not provided_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-TrustEval-Key header."},
            )

        if provided_key != api_key:
            logger.warning("Invalid API key from %s", request.client.host if request.client else "unknown")
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API key."},
            )

        return await call_next(request)
