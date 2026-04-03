# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Data models for evaluation results.

``PillarResult`` captures per-pillar metrics and ``EvaluationResult``
aggregates them into a single trust-evaluation report that can be
exported as JSON, dict, or PDF.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from trusteval.core.scorer import compute_grade, compute_trust_level


# ---------------------------------------------------------------------------
# PillarResult
# ---------------------------------------------------------------------------


@dataclass
class PillarResult:
    """Result for a single evaluation pillar (e.g. hallucination, bias).

    Attributes:
        pillar: Name of the pillar.
        score: Normalised score in ``[0.0, 1.0]``.
        grade: Letter grade derived from *score*.
        passed: Whether the pillar meets the minimum passing threshold.
        details: Free-form details dict with pillar-specific metrics.
        test_count: Total number of test cases executed.
        pass_count: Number of test cases that passed.
        fail_count: Number of test cases that failed.
        flagged_items: List of individual items that were flagged.
        timestamp: ISO-8601 timestamp of when the pillar was evaluated.
    """

    pillar: str
    score: float
    grade: str = ""
    passed: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    test_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    flagged_items: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.grade:
            self.grade = compute_grade(self.score)
        if self.fail_count == 0 and self.test_count > 0:
            self.fail_count = self.test_count - self.pass_count
        self.passed = self.score >= 0.55  # C or above

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the pillar result to a plain dict."""
        return asdict(self)

    def summary(self) -> str:
        """Return a one-line human-readable summary.

        Returns:
            String like ``"hallucination: 0.87 (A) PASSED — 18/20 tests"``.
        """
        status = "PASSED" if self.passed else "FAILED"
        return (
            f"{self.pillar}: {self.score:.2f} ({self.grade}) {status} "
            f"— {self.pass_count}/{self.test_count} tests"
        )


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------


@dataclass
class EvaluationResult:
    """Aggregated result of a full TrustEval evaluation run.

    Attributes:
        evaluation_id: Unique UUID for this evaluation.
        provider: LLM provider name.
        model: Model identifier.
        industry: Target industry.
        overall_score: Weighted aggregate score in ``[0.0, 1.0]``.
        overall_grade: Letter grade for the overall score.
        trust_level: ``TRUSTED``, ``CONDITIONAL``, or ``UNTRUSTED``.
        pillars: Mapping of pillar name to its ``PillarResult``.
        metadata: Arbitrary metadata dict (SDK version, config hash, etc.).
        duration_seconds: Wall-clock time of the evaluation in seconds.
        timestamp: ISO-8601 timestamp of evaluation completion.
    """

    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = ""
    model: str = ""
    industry: str = ""
    overall_score: float = 0.0
    overall_grade: str = ""
    trust_level: str = ""
    pillars: Dict[str, PillarResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if not self.overall_grade and self.overall_score > 0:
            self.overall_grade = compute_grade(self.overall_score)
        if not self.trust_level and self.overall_grade:
            self.trust_level = compute_trust_level(self.overall_grade)

    # -- Serialisation -------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the full evaluation result to a plain dict.

        Returns:
            A JSON-compatible dictionary representation.
        """
        data = {
            "evaluation_id": self.evaluation_id,
            "provider": self.provider,
            "model": self.model,
            "industry": self.industry,
            "overall_score": self.overall_score,
            "overall_grade": self.overall_grade,
            "trust_level": self.trust_level,
            "pillars": {
                name: pr.to_dict() for name, pr in self.pillars.items()
            },
            "metadata": self.metadata,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }
        return data

    def to_json(self, indent: int = 2) -> str:
        """Serialise the evaluation result to a JSON string.

        Args:
            indent: JSON indentation level.

        Returns:
            Pretty-printed JSON string.
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def summary(self) -> str:
        """Return a multi-line human-readable summary of the evaluation.

        Returns:
            Formatted summary string suitable for console output.
        """
        lines = [
            "=" * 60,
            "TrustEval Evaluation Report",
            "=" * 60,
            f"  ID:          {self.evaluation_id}",
            f"  Provider:    {self.provider}",
            f"  Model:       {self.model}",
            f"  Industry:    {self.industry}",
            f"  Duration:    {self.duration_seconds:.1f}s",
            f"  Timestamp:   {self.timestamp}",
            "-" * 60,
            f"  Overall Score: {self.overall_score:.2f}  "
            f"Grade: {self.overall_grade}  "
            f"Trust: {self.trust_level}",
            "-" * 60,
            "  Pillar Breakdown:",
        ]
        for name, pr in self.pillars.items():
            lines.append(f"    {pr.summary()}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def export(self, path: str | Path, format: str = "pdf") -> Path:
        """Export the evaluation result to a file.

        Args:
            path: Destination file path.
            format: Output format — ``"pdf"``, ``"json"``, or ``"html"``.

        Returns:
            Resolved ``Path`` to the written file.

        Raises:
            ValueError: If *format* is not supported.
            IOError: If the file cannot be written.
        """
        path = Path(path)
        fmt = format.lower().strip()

        if fmt == "json":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.to_json(), encoding="utf-8")
            return path.resolve()

        if fmt == "html":
            html = self._render_html()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding="utf-8")
            return path.resolve()

        if fmt == "pdf":
            # Generate HTML then convert.  If weasyprint is unavailable,
            # fall back to writing an HTML file and note the limitation.
            html = self._render_html()
            try:
                from weasyprint import HTML as WeasyprintHTML  # type: ignore[import-untyped]
                path.parent.mkdir(parents=True, exist_ok=True)
                WeasyprintHTML(string=html).write_pdf(str(path))
                return path.resolve()
            except ImportError:
                # Fallback: write HTML with a .pdf-requested note
                fallback = path.with_suffix(".html")
                fallback.parent.mkdir(parents=True, exist_ok=True)
                fallback.write_text(html, encoding="utf-8")
                return fallback.resolve()

        raise ValueError(
            f"Unsupported export format '{fmt}'. Choose 'pdf', 'json', or 'html'."
        )

    # -- Private helpers -----------------------------------------------------

    def _render_html(self) -> str:
        """Render a self-contained HTML report."""
        pillar_rows = ""
        for name, pr in self.pillars.items():
            status = "PASS" if pr.passed else "FAIL"
            colour = "#22c55e" if pr.passed else "#ef4444"
            pillar_rows += (
                f"<tr>"
                f"<td>{pr.pillar}</td>"
                f"<td>{pr.score:.2f}</td>"
                f"<td>{pr.grade}</td>"
                f'<td style="color:{colour};font-weight:bold">{status}</td>'
                f"<td>{pr.pass_count}/{pr.test_count}</td>"
                f"</tr>\n"
            )

        trust_colour = {
            "TRUSTED": "#22c55e",
            "CONDITIONAL": "#f59e0b",
            "UNTRUSTED": "#ef4444",
        }.get(self.trust_level, "#6b7280")

        return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>TrustEval Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; }}
  h1 {{ border-bottom: 2px solid #1e293b; padding-bottom: .5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: .5rem; border-bottom: 1px solid #e2e8f0; }}
  th {{ background: #f8fafc; }}
  .badge {{ display: inline-block; padding: .25rem .75rem; border-radius: .375rem;
            color: #fff; font-weight: 700; background: {trust_colour}; }}
</style></head>
<body>
<h1>TrustEval Evaluation Report</h1>
<p><strong>ID:</strong> {self.evaluation_id}</p>
<p><strong>Provider:</strong> {self.provider} &mdash; <strong>Model:</strong> {self.model}</p>
<p><strong>Industry:</strong> {self.industry} &mdash; <strong>Duration:</strong> {self.duration_seconds:.1f}s</p>
<p><strong>Overall Score:</strong> {self.overall_score:.2f} ({self.overall_grade})
   <span class="badge">{self.trust_level}</span></p>
<h2>Pillar Breakdown</h2>
<table>
<tr><th>Pillar</th><th>Score</th><th>Grade</th><th>Status</th><th>Tests</th></tr>
{pillar_rows}
</table>
<footer><p style="color:#94a3b8;margin-top:2rem;font-size:.875rem">
Generated by TrustEval &mdash; {self.timestamp}</p></footer>
</body></html>"""
