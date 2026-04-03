# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Pydantic v2 request/response models for the TrustEval Dashboard API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EvaluationStatus(str, Enum):
    """Lifecycle states for an evaluation run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExportFormat(str, Enum):
    """Supported export / report formats."""

    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

class EvaluationRequest(BaseModel):
    """Body for POST /api/evaluations/run."""

    provider: str = Field(..., min_length=1, description="LLM provider name (e.g. openai, anthropic).")
    model: str = Field(..., min_length=1, description="Model identifier within the provider.")
    industry: str = Field(..., min_length=1, description="Target industry for the evaluation.")
    pillars: list[str] = Field(
        default_factory=list,
        description="Optional subset of trust pillars to evaluate. Empty means all.",
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific or evaluation-specific configuration overrides.",
    )

    @field_validator("provider", "model", "industry", mode="before")
    @classmethod
    def _strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class EvaluationResponse(BaseModel):
    """Response body returned after creating / fetching an evaluation."""

    id: str = Field(..., description="Unique evaluation identifier.")
    provider: str
    model: str
    industry: str
    pillars: list[str] = Field(default_factory=list)
    status: EvaluationStatus = EvaluationStatus.PENDING
    scores: dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    estimated_seconds: Optional[int] = None
    websocket_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    config: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class EvaluationListResponse(BaseModel):
    """Paginated list of evaluations."""

    total: int
    limit: int
    offset: int
    evaluations: list[EvaluationResponse]


# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------

class CompareRequest(BaseModel):
    """Body for POST /api/evaluations/compare."""

    evaluation_id_1: str = Field(..., description="First evaluation to compare.")
    evaluation_id_2: str = Field(..., description="Second evaluation to compare.")


class CompareResponse(BaseModel):
    """Side-by-side comparison result."""

    evaluation_1: EvaluationResponse
    evaluation_2: EvaluationResponse
    differences: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-pillar score deltas and notable divergences.",
    )


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class ProviderTestRequest(BaseModel):
    """Body for POST /api/providers/test."""

    provider: str = Field(..., min_length=1, description="Provider to test.")
    api_key: Optional[str] = Field(None, description="Optional API key override for the test.")
    config: dict[str, Any] = Field(default_factory=dict)


class ProviderInfo(BaseModel):
    """Metadata about a single supported provider."""

    name: str
    display_name: str
    models: list[str] = Field(default_factory=list)
    requires_api_key: bool = True
    status: str = "available"


class ProviderResponse(BaseModel):
    """Response for provider listing or connectivity test."""

    provider: str
    connected: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Industry
# ---------------------------------------------------------------------------

class IndustryInfo(BaseModel):
    """Details for a supported industry vertical."""

    name: str
    display_name: str
    description: str
    pillars: list[str] = Field(default_factory=list)
    regulations: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class ReportGenerateRequest(BaseModel):
    """Body for POST /api/reports/generate."""

    evaluation_id: str = Field(..., description="Source evaluation for the report.")
    format: ExportFormat = ExportFormat.PDF
    title: Optional[str] = None


class ReportResponse(BaseModel):
    """Metadata for a generated report."""

    id: str
    evaluation_id: str
    format: ExportFormat
    title: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime
    size_bytes: Optional[int] = None


class ReportListResponse(BaseModel):
    """Paginated report listing."""

    total: int
    reports: list[ReportResponse]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Minimal health-check payload."""

    status: str = "ok"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DetailedHealthResponse(HealthResponse):
    """Extended health information for ops dashboards."""

    database_connected: bool = False
    active_evaluations: int = 0
    uptime_seconds: float = 0.0
    python_version: str = ""
    system_info: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope."""

    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
