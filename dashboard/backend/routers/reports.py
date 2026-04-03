# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Report endpoints — list, generate, and download reports."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.models.database import get_session
from dashboard.backend.models.schemas import (
    ReportGenerateRequest,
    ReportListResponse,
    ReportResponse,
)
from dashboard.backend.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    session: AsyncSession = Depends(get_session),
) -> ReportListResponse:
    """List all saved reports.

    Args:
        session: Injected database session.

    Returns:
        A list of report metadata objects.
    """
    return await report_service.list_reports(session)


@router.post("/generate", response_model=ReportResponse, status_code=201)
async def generate_report(
    body: ReportGenerateRequest,
    session: AsyncSession = Depends(get_session),
) -> ReportResponse:
    """Generate a report from an existing evaluation.

    Args:
        body: Report generation parameters (evaluation ID, format, title).
        session: Injected database session.

    Returns:
        Metadata for the newly generated report.

    Raises:
        HTTPException: 404 if the source evaluation is not found.
    """
    result = await report_service.generate_report(body, session)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation {body.evaluation_id} not found.",
        )
    return result


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    """Download a report file.

    Args:
        report_id: The report UUID.
        session: Injected database session.

    Returns:
        The report file as a streaming download.

    Raises:
        HTTPException: 404 if the report or its file is not found.
    """
    result = await report_service.get_report_file(report_id, session)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found or file missing.")

    path, media_type = result
    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=path.name,
    )
