# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Business-logic layer for LLM evaluations.

Orchestrates evaluation runs, persistence, and comparison logic while
keeping the router layer thin.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.models.database import Evaluation
from dashboard.backend.models.schemas import (
    CompareResponse,
    EvaluationListResponse,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationStatus,
)

logger = logging.getLogger("trusteval.evaluation_service")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_response(row: Evaluation, websocket_url: Optional[str] = None) -> EvaluationResponse:
    """Convert a database row into an API response model.

    Args:
        row: An ``Evaluation`` ORM instance.
        websocket_url: Optional WebSocket URL for live progress updates.

    Returns:
        A fully populated ``EvaluationResponse``.
    """
    return EvaluationResponse(
        id=row.id,
        provider=row.provider,
        model=row.model,
        industry=row.industry,
        pillars=row.get_pillars(),
        status=EvaluationStatus(row.status),
        scores=row.get_scores(),
        summary=row.summary,
        estimated_seconds=row.estimated_seconds,
        websocket_url=websocket_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
        config=row.get_config(),
        error_message=row.error_message,
    )


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def run_evaluation(
    request: EvaluationRequest,
    session: AsyncSession,
    *,
    base_url: str = "",
) -> EvaluationResponse:
    """Create and kick-off a new evaluation run.

    The evaluation is persisted with ``pending`` status immediately so
    that callers can poll or subscribe via WebSocket.  The actual
    evaluation work is expected to be picked up by a background task or
    worker process.

    Args:
        request: Validated evaluation parameters from the API layer.
        session: Active async database session.
        base_url: The base URL of the running server (used to build the
            WebSocket URL).

    Returns:
        An ``EvaluationResponse`` with the newly created evaluation metadata.
    """
    eval_id = str(uuid.uuid4())
    now = datetime.utcnow()
    estimated = _estimate_duration(request)

    row = Evaluation(
        id=eval_id,
        provider=request.provider,
        model=request.model,
        industry=request.industry,
        status=EvaluationStatus.PENDING.value,
        estimated_seconds=estimated,
        created_at=now,
        updated_at=now,
    )
    row.set_pillars(request.pillars)
    row.set_config(request.config)

    session.add(row)
    await session.commit()
    await session.refresh(row)

    ws_url = f"{base_url}/ws/evaluations/{eval_id}" if base_url else None
    logger.info("Created evaluation %s (%s / %s / %s)", eval_id, request.provider, request.model, request.industry)
    return _row_to_response(row, websocket_url=ws_url)


async def get_evaluation(eval_id: str, session: AsyncSession) -> Optional[EvaluationResponse]:
    """Retrieve a single evaluation by its ID.

    Args:
        eval_id: The UUID string of the evaluation.
        session: Active async database session.

    Returns:
        The ``EvaluationResponse`` if found, otherwise ``None``.
    """
    result = await session.execute(select(Evaluation).where(Evaluation.id == eval_id))
    row = result.scalar_one_or_none()
    if row is None:
        return None
    return _row_to_response(row)


async def list_evaluations(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
) -> EvaluationListResponse:
    """Return a paginated list of evaluations ordered by creation date.

    Args:
        session: Active async database session.
        limit: Maximum number of records to return.
        offset: Number of records to skip.

    Returns:
        An ``EvaluationListResponse`` containing the page of results.
    """
    count_result = await session.execute(select(func.count()).select_from(Evaluation))
    total = count_result.scalar() or 0

    result = await session.execute(
        select(Evaluation)
        .order_by(Evaluation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()

    return EvaluationListResponse(
        total=total,
        limit=limit,
        offset=offset,
        evaluations=[_row_to_response(r) for r in rows],
    )


async def delete_evaluation(eval_id: str, session: AsyncSession) -> bool:
    """Delete an evaluation by ID.

    Args:
        eval_id: The UUID string of the evaluation.
        session: Active async database session.

    Returns:
        ``True`` if a record was deleted, ``False`` if not found.
    """
    result = await session.execute(select(Evaluation).where(Evaluation.id == eval_id))
    row = result.scalar_one_or_none()
    if row is None:
        return False
    await session.delete(row)
    await session.commit()
    logger.info("Deleted evaluation %s", eval_id)
    return True


async def compare_evaluations(
    id1: str,
    id2: str,
    session: AsyncSession,
) -> Optional[CompareResponse]:
    """Compare two evaluations side-by-side.

    Args:
        id1: First evaluation ID.
        id2: Second evaluation ID.
        session: Active async database session.

    Returns:
        A ``CompareResponse`` with both evaluations and computed
        differences, or ``None`` if either evaluation is missing.
    """
    eval1 = await get_evaluation(id1, session)
    eval2 = await get_evaluation(id2, session)

    if eval1 is None or eval2 is None:
        return None

    differences = _compute_differences(eval1.scores, eval2.scores)

    return CompareResponse(
        evaluation_1=eval1,
        evaluation_2=eval2,
        differences=differences,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _estimate_duration(request: EvaluationRequest) -> int:
    """Heuristic estimation of how long an evaluation will take.

    Args:
        request: The evaluation request.

    Returns:
        Estimated duration in seconds.
    """
    base = 30
    pillar_count = len(request.pillars) if request.pillars else 6  # assume all pillars
    return base + pillar_count * 10


def _compute_differences(scores1: dict[str, Any], scores2: dict[str, Any]) -> dict[str, Any]:
    """Compute per-key numeric deltas between two score dictionaries.

    Args:
        scores1: Scores from the first evaluation.
        scores2: Scores from the second evaluation.

    Returns:
        A dict mapping each key to its delta (score1 - score2) where
        both values are numeric, plus an ``only_in_1`` and ``only_in_2``
        list for keys unique to one side.
    """
    all_keys = set(scores1.keys()) | set(scores2.keys())
    deltas: dict[str, Any] = {}
    only_in_1: list[str] = []
    only_in_2: list[str] = []

    for key in sorted(all_keys):
        v1 = scores1.get(key)
        v2 = scores2.get(key)
        if v1 is not None and v2 is not None:
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                deltas[key] = round(v1 - v2, 4)
            else:
                deltas[key] = {"evaluation_1": v1, "evaluation_2": v2}
        elif v1 is not None:
            only_in_1.append(key)
        else:
            only_in_2.append(key)

    return {
        "score_deltas": deltas,
        "only_in_evaluation_1": only_in_1,
        "only_in_evaluation_2": only_in_2,
    }
