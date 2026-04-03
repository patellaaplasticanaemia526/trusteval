# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Health-check endpoints — basic liveness and detailed system status."""

from __future__ import annotations

import platform
import sys
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.models.database import Evaluation, get_session
from dashboard.backend.models.schemas import DetailedHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

# Track application start time for uptime calculation.
_START_TIME: float = time.time()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic liveness probe — no authentication required.

    Returns:
        Minimal status payload with version and timestamp.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health(
    session: AsyncSession = Depends(get_session),
) -> DetailedHealthResponse:
    """Detailed system health for ops dashboards.

    Checks database connectivity and reports runtime information.

    Args:
        session: Injected database session.

    Returns:
        Extended health payload including database status and system info.
    """
    # Database connectivity check.
    db_ok = False
    active_evals = 0
    try:
        await session.execute(text("SELECT 1"))
        db_ok = True

        result = await session.execute(
            select(func.count())
            .select_from(Evaluation)
            .where(Evaluation.status.in_(["pending", "running"]))
        )
        active_evals = result.scalar() or 0
    except Exception:
        db_ok = False

    uptime = time.time() - _START_TIME

    return DetailedHealthResponse(
        status="ok" if db_ok else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        database_connected=db_ok,
        active_evaluations=active_evals,
        uptime_seconds=round(uptime, 2),
        python_version=sys.version,
        system_info={
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
        },
    )
