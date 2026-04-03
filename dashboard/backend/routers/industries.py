# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Industry endpoints — list industries, get details, get pillars."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from dashboard.backend.models.schemas import IndustryInfo

router = APIRouter(prefix="/industries", tags=["industries"])

# ---------------------------------------------------------------------------
# Static industry registry — extend as new verticals are onboarded.
# ---------------------------------------------------------------------------

_INDUSTRIES: dict[str, IndustryInfo] = {
    "healthcare": IndustryInfo(
        name="healthcare",
        display_name="Healthcare & Life Sciences",
        description=(
            "Evaluation framework tailored for clinical decision support, "
            "medical documentation, and patient-facing AI applications."
        ),
        pillars=["safety", "fairness", "privacy", "robustness", "explainability", "compliance"],
        regulations=["HIPAA", "FDA AI/ML Guidance", "EU MDR"],
    ),
    "finance": IndustryInfo(
        name="finance",
        display_name="Financial Services",
        description=(
            "Risk-aware evaluation for credit decisioning, fraud detection, "
            "and customer-facing financial advisory AI."
        ),
        pillars=["fairness", "robustness", "explainability", "compliance", "privacy", "security"],
        regulations=["ECOA", "FCRA", "SR 11-7", "EU AI Act"],
    ),
    "legal": IndustryInfo(
        name="legal",
        display_name="Legal & Compliance",
        description=(
            "Evaluation of LLMs used for contract analysis, legal research, "
            "and regulatory compliance workflows."
        ),
        pillars=["accuracy", "fairness", "explainability", "robustness", "confidentiality"],
        regulations=["ABA Model Rules", "GDPR", "EU AI Act"],
    ),
    "education": IndustryInfo(
        name="education",
        display_name="Education & EdTech",
        description=(
            "Assessment of AI tutors, grading assistants, and content "
            "generation tools in educational settings."
        ),
        pillars=["safety", "fairness", "accuracy", "privacy", "accessibility"],
        regulations=["FERPA", "COPPA", "Section 508"],
    ),
    "government": IndustryInfo(
        name="government",
        display_name="Government & Public Sector",
        description=(
            "Evaluation for citizen-facing AI services, policy analysis, "
            "and public safety applications."
        ),
        pillars=["fairness", "transparency", "safety", "robustness", "accountability", "privacy"],
        regulations=["EO 14110", "NIST AI RMF", "EU AI Act"],
    ),
    "general": IndustryInfo(
        name="general",
        display_name="General Purpose",
        description=(
            "Broad-spectrum evaluation suitable for any domain, covering "
            "the core responsible-AI pillars."
        ),
        pillars=["safety", "fairness", "robustness", "privacy", "explainability", "accuracy"],
        regulations=["NIST AI RMF", "ISO 42001", "EU AI Act"],
    ),
}


@router.get("", response_model=list[IndustryInfo])
async def list_industries() -> list[IndustryInfo]:
    """List all supported industry verticals.

    Returns:
        A list of industry metadata objects.
    """
    return list(_INDUSTRIES.values())


@router.get("/{name}/info", response_model=IndustryInfo)
async def get_industry_info(name: str) -> IndustryInfo:
    """Get detailed information about a specific industry.

    Args:
        name: Industry name (case-insensitive).

    Returns:
        Full industry metadata including description and regulations.

    Raises:
        HTTPException: 404 if the industry is not recognised.
    """
    key = name.lower()
    if key not in _INDUSTRIES:
        raise HTTPException(status_code=404, detail=f"Unknown industry: {name}")
    return _INDUSTRIES[key]


@router.get("/{name}/pillars", response_model=list[str])
async def get_industry_pillars(name: str) -> list[str]:
    """Get the trust pillars applicable to a specific industry.

    Args:
        name: Industry name (case-insensitive).

    Returns:
        An ordered list of pillar names.

    Raises:
        HTTPException: 404 if the industry is not recognised.
    """
    key = name.lower()
    if key not in _INDUSTRIES:
        raise HTTPException(status_code=404, detail=f"Unknown industry: {name}")
    return _INDUSTRIES[key].pillars
