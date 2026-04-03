# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Request / response logging middleware.

Logs every HTTP request with method, path, status code, and elapsed
time.  Sensitive headers (``Authorization``, ``X-TrustEval-Key``) are
redacted automatically.
"""

from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("trusteval.http")

_REDACTED_HEADERS = frozenset({"authorization", "x-trusteval-key", "cookie"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log inbound requests and outbound responses with timing."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Wrap the request lifecycle with structured logging.

        Args:
            request: The inbound HTTP request.
            call_next: Callable to forward the request down the stack.

        Returns:
            The downstream response with an ``X-Request-ID`` header attached.
        """
        request_id = str(uuid.uuid4())[:8]
        client = request.client.host if request.client else "unknown"

        logger.info(
            "[%s] %s %s %s from %s",
            request_id,
            request.method,
            request.url.path,
            dict(request.query_params) or "",
            client,
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("[%s] Unhandled exception during request processing", request_id)
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "[%s] %s %s -> %d (%.1f ms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        return response
