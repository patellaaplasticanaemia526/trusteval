# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Abstract base class for all TrustEval report generators.

Concrete reporters must implement ``generate()`` and may override the
helper formatting methods to customise presentation.
"""

from __future__ import annotations

import abc
from pathlib import Path
from typing import Any, Dict


class BaseReporter(abc.ABC):
    """Base class that all report generators inherit from.

    Args:
        evaluation_result: A dict (or dict-like object) containing the
            full evaluation output.  Expected top-level keys include
            ``overall_score``, ``grade``, ``trust_level``,
            ``pillar_results``, ``metadata``, and optionally
            ``flagged_items`` and ``test_cases``.

    Subclasses must implement :meth:`generate`.
    """

    def __init__(self, evaluation_result: Dict[str, Any]) -> None:
        if not isinstance(evaluation_result, dict):
            raise TypeError(
                f"evaluation_result must be a dict, got {type(evaluation_result).__name__}"
            )
        self.result = evaluation_result

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def generate(self, output_path: str | Path) -> str:
        """Generate the report and write it to *output_path*.

        Args:
            output_path: Filesystem path where the report will be saved.

        Returns:
            The absolute path to the generated report file as a string.
        """

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def format_score(score: float | int | None) -> str:
        """Format a numeric score for display.

        Args:
            score: A score in ``[0.0, 1.0]`` or ``None``.

        Returns:
            A percentage string like ``"87.3%"``, or ``"N/A"`` if the
            score is ``None``.
        """
        if score is None:
            return "N/A"
        return f"{float(score) * 100:.1f}%"

    @staticmethod
    def format_grade(grade: str | None) -> str:
        """Format a letter grade for display.

        Args:
            grade: A letter grade (``"A"``-``"F"``) or ``None``.

        Returns:
            The grade string, or ``"N/A"`` if not available.
        """
        if grade is None:
            return "N/A"
        return str(grade).upper()

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def _get_pillar_results(self) -> list[Dict[str, Any]]:
        """Extract pillar results as a list of dicts.

        Returns:
            List of pillar result dicts, each expected to contain at
            least ``name`` and ``score``.
        """
        raw = self.result.get("pillar_results", {})
        if isinstance(raw, dict):
            return [
                {"name": name, **data}
                for name, data in raw.items()
            ]
        if isinstance(raw, list):
            return list(raw)
        return []

    def _get_flagged_items(self) -> list[Dict[str, Any]]:
        """Extract flagged items from the result.

        Returns:
            List of flagged-item dicts.
        """
        items = self.result.get("flagged_items", [])
        return list(items) if isinstance(items, list) else []

    def _get_test_cases(self) -> list[Dict[str, Any]]:
        """Extract individual test-case results.

        Returns:
            List of test-case dicts.
        """
        cases = self.result.get("test_cases", [])
        return list(cases) if isinstance(cases, list) else []

    def _get_metadata(self) -> Dict[str, Any]:
        """Extract evaluation metadata.

        Returns:
            Metadata dict (provider, model, timestamp, etc.).
        """
        meta = self.result.get("metadata", {})
        return dict(meta) if isinstance(meta, dict) else {}

    def _ensure_parent_dir(self, output_path: Path) -> None:
        """Create the parent directory of *output_path* if needed.

        Args:
            output_path: Target file path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
