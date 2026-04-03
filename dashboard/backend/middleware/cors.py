# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""CORS configuration helper.

Development origins (``localhost:3000``, ``localhost:8080``) are always
allowed.  Additional origins can be supplied via the
``TRUSTEVAL_ALLOWED_ORIGINS`` environment variable as a comma-separated
list.  A wildcard (``*``) is intentionally never used so that
credentials and sensitive headers remain protected in production.
"""

from __future__ import annotations

import os
from typing import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Default dev origins — safe for local development.
_DEV_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]


def get_allowed_origins() -> list[str]:
    """Build the list of allowed CORS origins.

    Merges the built-in development origins with any extra origins
    defined in ``TRUSTEVAL_ALLOWED_ORIGINS`` (comma-separated).

    Returns:
        De-duplicated list of allowed origin strings.
    """
    extra = os.environ.get("TRUSTEVAL_ALLOWED_ORIGINS", "")
    origins = list(_DEV_ORIGINS)
    if extra:
        for origin in extra.split(","):
            origin = origin.strip()
            if origin and origin != "*":
                origins.append(origin)
    return list(dict.fromkeys(origins))  # de-dup, preserve order


def configure_cors(app: FastAPI) -> None:
    """Attach CORS middleware to the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
