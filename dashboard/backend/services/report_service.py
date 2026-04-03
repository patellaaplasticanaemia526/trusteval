# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Business-logic layer for report generation and retrieval.

Reports are generated from completed evaluations and persisted as files
under ``~/.trusteval/reports/``.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.models.database import Evaluation, Report
from dashboard.backend.models.schemas import (
    ExportFormat,
    ReportGenerateRequest,
    ReportListResponse,
    ReportResponse,
)

logger = logging.getLogger("trusteval.report_service")

_REPORTS_DIR = Path.home() / ".trusteval" / "reports"
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_response(row: Report) -> ReportResponse:
    """Convert a database row into an API response model.

    Args:
        row: A ``Report`` ORM instance.

    Returns:
        A populated ``ReportResponse``.
    """
    return ReportResponse(
        id=row.id,
        evaluation_id=row.evaluation_id,
        format=ExportFormat(row.format),
        title=row.title,
        file_path=row.file_path,
        created_at=row.created_at,
        size_bytes=row.size_bytes,
    )


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def generate_report(
    request: ReportGenerateRequest,
    session: AsyncSession,
) -> Optional[ReportResponse]:
    """Generate a report file from a completed evaluation.

    The report is written to ``~/.trusteval/reports/<id>.<ext>`` and a
    metadata row is stored in the database.

    Args:
        request: Validated report-generation parameters.
        session: Active async database session.

    Returns:
        A ``ReportResponse`` on success, or ``None`` if the source
        evaluation cannot be found.
    """
    # Fetch the source evaluation.
    result = await session.execute(
        select(Evaluation).where(Evaluation.id == request.evaluation_id)
    )
    eval_row = result.scalar_one_or_none()
    if eval_row is None:
        return None

    report_id = str(uuid.uuid4())
    ext = request.format.value
    file_name = f"{report_id}.{ext}"
    file_path = _REPORTS_DIR / file_name

    # Build the report content.
    content_bytes = _render_report(eval_row, request.format, request.title)
    file_path.write_bytes(content_bytes)

    now = datetime.utcnow()
    title = request.title or f"Report for evaluation {request.evaluation_id[:8]}"

    row = Report(
        id=report_id,
        evaluation_id=request.evaluation_id,
        format=ext,
        title=title,
        file_path=str(file_path),
        size_bytes=len(content_bytes),
        created_at=now,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)

    logger.info("Generated %s report %s for evaluation %s", ext, report_id, request.evaluation_id)
    return _row_to_response(row)


async def list_reports(session: AsyncSession) -> ReportListResponse:
    """Return all reports ordered by creation date descending.

    Args:
        session: Active async database session.

    Returns:
        A ``ReportListResponse`` containing every report.
    """
    count_result = await session.execute(select(func.count()).select_from(Report))
    total = count_result.scalar() or 0

    result = await session.execute(
        select(Report).order_by(Report.created_at.desc())
    )
    rows = result.scalars().all()

    return ReportListResponse(
        total=total,
        reports=[_row_to_response(r) for r in rows],
    )


async def get_report_file(report_id: str, session: AsyncSession) -> Optional[tuple[Path, str]]:
    """Resolve a report's on-disk file path and media type.

    Args:
        report_id: The UUID of the report.
        session: Active async database session.

    Returns:
        A ``(Path, media_type)`` tuple if the report exists and the file
        is present, otherwise ``None``.
    """
    result = await session.execute(select(Report).where(Report.id == report_id))
    row = result.scalar_one_or_none()
    if row is None or not row.file_path:
        return None

    path = Path(row.file_path)
    if not path.exists():
        logger.warning("Report file missing on disk: %s", path)
        return None

    media_map = {
        "pdf": "application/pdf",
        "json": "application/json",
        "csv": "text/csv",
    }
    media_type = media_map.get(row.format, "application/octet-stream")
    return path, media_type


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def _render_report(eval_row: Evaluation, fmt: ExportFormat, title: Optional[str] = None) -> bytes:
    """Render report content in the requested format.

    Args:
        eval_row: The evaluation ORM instance.
        fmt: Desired output format.
        title: Optional human-readable title.

    Returns:
        Raw bytes of the rendered report.
    """
    if fmt == ExportFormat.JSON:
        return _render_json(eval_row, title)
    elif fmt == ExportFormat.CSV:
        return _render_csv(eval_row, title)
    else:
        # PDF — produce a simple text-based placeholder (a real
        # implementation would use a PDF library like reportlab).
        return _render_pdf_placeholder(eval_row, title)


def _render_json(eval_row: Evaluation, title: Optional[str]) -> bytes:
    """Render the evaluation as a JSON report."""
    payload = {
        "title": title or f"Evaluation Report — {eval_row.id[:8]}",
        "generated_at": datetime.utcnow().isoformat(),
        "evaluation": {
            "id": eval_row.id,
            "provider": eval_row.provider,
            "model": eval_row.model,
            "industry": eval_row.industry,
            "pillars": eval_row.get_pillars(),
            "status": eval_row.status,
            "scores": eval_row.get_scores(),
            "summary": eval_row.summary,
            "created_at": eval_row.created_at.isoformat() if eval_row.created_at else None,
        },
    }
    return json.dumps(payload, indent=2).encode("utf-8")


def _render_csv(eval_row: Evaluation, title: Optional[str]) -> bytes:
    """Render the evaluation scores as a CSV report."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["pillar", "score"])
    scores = eval_row.get_scores()
    for key, value in sorted(scores.items()):
        writer.writerow([key, value])
    return buf.getvalue().encode("utf-8")


def _render_pdf_placeholder(eval_row: Evaluation, title: Optional[str]) -> bytes:
    """Produce a plain-text placeholder for PDF reports.

    A production system would replace this with proper PDF rendering
    (e.g., via ``reportlab`` or ``weasyprint``).
    """
    lines = [
        title or f"Evaluation Report — {eval_row.id[:8]}",
        "=" * 60,
        f"Provider : {eval_row.provider}",
        f"Model    : {eval_row.model}",
        f"Industry : {eval_row.industry}",
        f"Status   : {eval_row.status}",
        "",
        "Scores:",
    ]
    for k, v in sorted(eval_row.get_scores().items()):
        lines.append(f"  {k}: {v}")
    if eval_row.summary:
        lines.extend(["", "Summary:", eval_row.summary])
    lines.append(f"\nGenerated at {datetime.utcnow().isoformat()}")
    return "\n".join(lines).encode("utf-8")
