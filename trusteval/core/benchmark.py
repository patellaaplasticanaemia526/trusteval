# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Base benchmark suite for loading and executing test cases.

Concrete benchmark implementations (e.g. ``HallucinationBenchmark``)
inherit from ``BenchmarkSuite`` and override the detection/scoring
methods while reusing the shared test-case lifecycle.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from trusteval.utils.exceptions import BenchmarkLoadError


# ---------------------------------------------------------------------------
# Test-case container
# ---------------------------------------------------------------------------


@dataclass
class TestCase:
    """A single benchmark test case.

    Attributes:
        id: Unique identifier for the test case.
        prompt: The input prompt to send to the LLM.
        expected: Expected or reference output (may be ``None``).
        metadata: Arbitrary metadata (category, difficulty, source, etc.).
    """

    id: str
    prompt: str
    expected: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Result of executing a single test case.

    Attributes:
        test_case_id: ID of the originating ``TestCase``.
        passed: Whether the test case passed.
        score: Normalised score in ``[0.0, 1.0]``.
        response: The raw LLM response text.
        details: Pillar-specific detail dict (e.g. detected entities).
    """

    test_case_id: str
    passed: bool
    score: float
    response: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# BenchmarkSuite base class
# ---------------------------------------------------------------------------


class BenchmarkSuite(ABC):
    """Abstract base class for pillar-specific benchmark suites.

    Subclasses must implement ``evaluate_response`` to judge a single
    LLM response against a test case.  The base class provides helpers
    for loading test cases from JSON and orchestrating the full run.

    Args:
        name: Human-readable benchmark name.
        pillar: The trust pillar this benchmark evaluates.
    """

    def __init__(self, name: str, pillar: str) -> None:
        self.name = name
        self.pillar = pillar
        self._test_cases: List[TestCase] = []
        self._results: List[TestResult] = []

    # -- Test case loading ---------------------------------------------------

    def load_test_cases(self, source: str | Path | List[Dict[str, Any]]) -> List[TestCase]:
        """Load test cases from a JSON file or an in-memory list.

        Args:
            source: Either a path to a JSON file whose root is a list of
                test-case dicts, or a Python list of such dicts.  Each dict
                must contain at least ``"id"`` and ``"prompt"`` keys.

        Returns:
            The list of loaded ``TestCase`` objects.

        Raises:
            BenchmarkLoadError: If the source cannot be read or parsed.
        """
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.is_file():
                raise BenchmarkLoadError(
                    f"Benchmark file not found: {path}",
                    benchmark=self.name,
                )
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                raise BenchmarkLoadError(
                    f"Failed to parse benchmark file: {exc}",
                    benchmark=self.name,
                ) from exc
        elif isinstance(source, list):
            raw = source
        else:
            raise BenchmarkLoadError(
                f"Unsupported source type: {type(source).__name__}",
                benchmark=self.name,
            )

        if not isinstance(raw, list):
            raise BenchmarkLoadError(
                "Benchmark source must be a list of test-case dicts.",
                benchmark=self.name,
            )

        cases: List[TestCase] = []
        for idx, item in enumerate(raw):
            if not isinstance(item, dict):
                raise BenchmarkLoadError(
                    f"Test case at index {idx} is not a dict.",
                    benchmark=self.name,
                )
            tc_id = item.get("id", f"{self.pillar}_{idx:04d}")
            prompt = item.get("prompt")
            if not prompt:
                raise BenchmarkLoadError(
                    f"Test case '{tc_id}' is missing a 'prompt' field.",
                    benchmark=self.name,
                )
            cases.append(
                TestCase(
                    id=str(tc_id),
                    prompt=str(prompt),
                    expected=item.get("expected"),
                    metadata=item.get("metadata", {}),
                )
            )

        self._test_cases = cases
        return cases

    # -- Execution -----------------------------------------------------------

    @abstractmethod
    def evaluate_response(self, test_case: TestCase, response: str) -> TestResult:
        """Judge a single LLM response against a test case.

        Args:
            test_case: The input test case.
            response: The raw LLM response string.

        Returns:
            A ``TestResult`` capturing pass/fail and score.
        """

    def run(self, responses: Dict[str, str]) -> List[TestResult]:
        """Execute the benchmark against a set of LLM responses.

        Args:
            responses: Mapping of test-case ID to the LLM's response string.

        Returns:
            List of ``TestResult`` objects, one per test case.

        Raises:
            BenchmarkLoadError: If no test cases have been loaded.
        """
        if not self._test_cases:
            raise BenchmarkLoadError(
                "No test cases loaded. Call load_test_cases() first.",
                benchmark=self.name,
            )

        self._results = []
        for tc in self._test_cases:
            response = responses.get(tc.id, "")
            result = self.evaluate_response(tc, response)
            self._results.append(result)
        return list(self._results)

    def get_results(self) -> List[TestResult]:
        """Return the results from the most recent ``run()`` call.

        Returns:
            Copy of the results list (empty if ``run()`` has not been called).
        """
        return list(self._results)

    @property
    def test_cases(self) -> List[TestCase]:
        """Return loaded test cases."""
        return list(self._test_cases)

    @property
    def pass_count(self) -> int:
        """Number of passed test results."""
        return sum(1 for r in self._results if r.passed)

    @property
    def fail_count(self) -> int:
        """Number of failed test results."""
        return sum(1 for r in self._results if not r.passed)

    @property
    def average_score(self) -> float:
        """Mean score across all test results, or 0.0 if none."""
        if not self._results:
            return 0.0
        return sum(r.score for r in self._results) / len(self._results)
