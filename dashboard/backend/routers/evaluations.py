# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Evaluation endpoints — create, list, detail, delete, compare, export."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.middleware.rate_limit import limiter
from dashboard.backend.models.database import get_session
from dashboard.backend.models.schemas import (
    CompareRequest,
    CompareResponse,
    EvaluationListResponse,
    EvaluationRequest,
    EvaluationResponse,
    ExportFormat,
)
from dashboard.backend.services import evaluation_service

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/run", response_model=EvaluationResponse, status_code=201)
@limiter.limit("10/minute")
async def run_evaluation(
    request: Request,
    body: EvaluationRequest,
    session: AsyncSession = Depends(get_session),
) -> EvaluationResponse:
    """Start a new evaluation run.

    Args:
        request: The raw Starlette request (needed by slowapi).
        body: Validated evaluation parameters.
        session: Injected database session.

    Returns:
        The newly created evaluation with ID, status, estimated time,
        and WebSocket URL for live progress.
    """
    base_url = str(request.base_url).rstrip("/").replace("http", "ws", 1)
    result = await evaluation_service.run_evaluation(body, session, base_url=base_url)
    return result


@router.get("", response_model=EvaluationListResponse)
async def list_evaluations(
    limit: int = Query(20, ge=1, le=100, description="Page size."),
    offset: int = Query(0, ge=0, description="Number of records to skip."),
    session: AsyncSession = Depends(get_session),
) -> EvaluationListResponse:
    """List all evaluations with pagination.

    Args:
        limit: Maximum results per page.
        offset: Number of results to skip.
        session: Injected database session.

    Returns:
        A paginated list of evaluations.
    """
    return await evaluation_service.list_evaluations(session, limit=limit, offset=offset)


@router.get("/{eval_id}", response_model=EvaluationResponse)
async def get_evaluation(
    eval_id: str,
    session: AsyncSession = Depends(get_session),
) -> EvaluationResponse:
    """Get a single evaluation by ID.

    Args:
        eval_id: The evaluation UUID.
        session: Injected database session.

    Returns:
        The evaluation detail.

    Raises:
        HTTPException: 404 if the evaluation does not exist.
    """
    result = await evaluation_service.get_evaluation(eval_id, session)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Evaluation {eval_id} not found.")
    return result


@router.delete("/{eval_id}", status_code=204)
async def delete_evaluation(
    eval_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete an evaluation by ID.

    Args:
        eval_id: The evaluation UUID.
        session: Injected database session.

    Raises:
        HTTPException: 404 if the evaluation does not exist.
    """
    deleted = await evaluation_service.delete_evaluation(eval_id, session)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Evaluation {eval_id} not found.")


@router.post("/compare", response_model=CompareResponse)
async def compare_evaluations(
    body: CompareRequest,
    session: AsyncSession = Depends(get_session),
) -> CompareResponse:
    """Compare two evaluations side-by-side.

    Args:
        body: The two evaluation IDs to compare.
        session: Injected database session.

    Returns:
        A comparison payload with both evaluations and their deltas.

    Raises:
        HTTPException: 404 if either evaluation is missing.
    """
    result = await evaluation_service.compare_evaluations(
        body.evaluation_id_1, body.evaluation_id_2, session
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="One or both evaluations not found.",
        )
    return result


@router.get("/{eval_id}/export")
async def export_evaluation(
    eval_id: str,
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format."),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """Export evaluation results in the requested format.

    Args:
        eval_id: The evaluation UUID.
        format: Desired export format (pdf, json, csv).
        session: Injected database session.

    Returns:
        A streaming file download.

    Raises:
        HTTPException: 404 if the evaluation does not exist.
    """
    from dashboard.backend.models.database import Evaluation as EvalModel
    from sqlalchemy import select

    result = await session.execute(select(EvalModel).where(EvalModel.id == eval_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Evaluation {eval_id} not found.")

    from dashboard.backend.services.report_service import _render_report

    content = _render_report(row, format)

    media_map = {
        ExportFormat.PDF: "application/pdf",
        ExportFormat.JSON: "application/json",
        ExportFormat.CSV: "text/csv",
    }

    import io

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_map[format],
        headers={
            "Content-Disposition": f'attachment; filename="evaluation_{eval_id[:8]}.{format.value}"'
        },
    )
