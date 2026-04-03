# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""FastAPI application entry-point for the TrustEval Dashboard backend.

Run with::

    uvicorn dashboard.backend.main:app --reload
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from dashboard.backend.middleware.auth import APIKeyAuthMiddleware
from dashboard.backend.middleware.cors import configure_cors
from dashboard.backend.middleware.logging import RequestLoggingMiddleware
from dashboard.backend.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from dashboard.backend.models.database import create_tables, dispose_engine
from dashboard.backend.routers import evaluations, health, industries, providers, reports

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("trusteval.app")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events.

    On startup the database tables are created (if absent).  On shutdown
    the async engine is disposed gracefully.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control back to the framework for the application's lifetime.
    """
    logger.info("TrustEval Dashboard starting up...")
    await create_tables()
    logger.info("Database tables verified.")
    yield
    logger.info("TrustEval Dashboard shutting down...")
    await dispose_engine()
    logger.info("Database connections closed.")


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TrustEval API",
    description="Enterprise LLM Evaluation & Responsible AI Framework — by Antrixsh Gupta",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    contact={"name": "Antrixsh Gupta", "url": "https://www.linkedin.com/in/antrixshgupta"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Middleware (order matters — outermost first)
# ---------------------------------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(APIKeyAuthMiddleware)
configure_cors(app)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router, prefix="/api")
app.include_router(evaluations.router, prefix="/api")
app.include_router(providers.router, prefix="/api")
app.include_router(industries.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------

# In-memory registry of active WebSocket connections per evaluation.
_ws_connections: dict[str, list[WebSocket]] = {}


@app.websocket("/ws/evaluations/{eval_id}")
async def evaluation_progress(websocket: WebSocket, eval_id: str) -> None:
    """WebSocket endpoint for real-time evaluation progress updates.

    Clients connect to ``/ws/evaluations/{eval_id}`` to receive
    JSON-encoded progress messages as the evaluation runs.

    Args:
        websocket: The WebSocket connection.
        eval_id: The evaluation UUID to subscribe to.
    """
    await websocket.accept()
    logger.info("WebSocket connected for evaluation %s", eval_id)

    if eval_id not in _ws_connections:
        _ws_connections[eval_id] = []
    _ws_connections[eval_id].append(websocket)

    try:
        # Send an initial acknowledgement.
        await websocket.send_json({
            "type": "connected",
            "evaluation_id": eval_id,
            "message": "Subscribed to evaluation progress.",
        })

        # Keep the connection open, waiting for the client to close or
        # for the server to push updates via broadcast_progress().
        while True:
            data = await websocket.receive_text()
            # Clients may send a ping; echo it back.
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for evaluation %s", eval_id)
    finally:
        _ws_connections.get(eval_id, []).remove(websocket) if websocket in _ws_connections.get(eval_id, []) else None
        if eval_id in _ws_connections and not _ws_connections[eval_id]:
            del _ws_connections[eval_id]


async def broadcast_progress(eval_id: str, payload: dict) -> None:
    """Broadcast a progress update to all WebSocket subscribers.

    Args:
        eval_id: The evaluation UUID.
        payload: JSON-serialisable progress data to send.
    """
    connections = _ws_connections.get(eval_id, [])
    dead: list[WebSocket] = []
    for ws in connections:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.remove(ws)


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Redirect root requests to the API documentation.

    Returns:
        A JSON hint pointing to the docs URL.
    """
    return {
        "message": "TrustEval API — visit /api/docs for interactive documentation.",
        "docs": "/api/docs",
    }
