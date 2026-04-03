# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Abstract base class for industry-specific benchmark suites.

Every industry module (healthcare, BFSI, retail, legal, …) must sub-class
:class:`BaseIndustry` and implement all abstract methods.  This guarantees a
uniform interface so the evaluation engine can treat every industry
identically.
"""

from __future__ import annotations

import abc
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseIndustry(abc.ABC):
    """Abstract base for all industry benchmark implementations.

    Concrete sub-classes define the benchmark areas, test prompts, and
    compliance checks that are relevant for a specific regulated industry.

    Example::

        suite = HealthcareBenchmark()
        prompts = suite.get_test_prompts(pillar="safety")
        for p in prompts:
            response = llm.generate(p["prompt"])
            result = suite.run_compliance_check(response, "disclaimer")
    """

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def get_name(self) -> str:
        """Return the canonical industry name.

        Returns:
            A short, human-readable name such as ``"Healthcare"`` or
            ``"BFSI"``.
        """

    @abc.abstractmethod
    def get_description(self) -> str:
        """Return a one-paragraph description of the industry suite.

        Returns:
            A description explaining what this benchmark covers and why
            it matters for responsible AI deployment.
        """

    @abc.abstractmethod
    def get_benchmark_areas(self) -> List[str]:
        """Return the list of benchmark area names.

        Each area corresponds to a distinct evaluation dimension — for
        example ``"Clinical QA"`` or ``"Credit Decision Fairness"``.

        Returns:
            Ordered list of area name strings.
        """

    @abc.abstractmethod
    def get_test_prompts(self, pillar: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return test prompts, optionally filtered by trust pillar.

        Each prompt dictionary contains at minimum:

        * ``prompt`` — the text to send to the LLM.
        * ``expected_behavior`` — a human-readable description of the
          correct / safe behaviour.
        * ``pillar`` — the TrustEval pillar (e.g. ``"safety"``,
          ``"fairness"``, ``"privacy"``).
        * ``category`` — the specific benchmark area.

        Args:
            pillar: If provided, only return prompts that belong to this
                trust pillar.  Pass ``None`` to get all prompts.

        Returns:
            List of prompt dictionaries.
        """

    @abc.abstractmethod
    def get_compliance_checks(self) -> List[Dict[str, Any]]:
        """Return metadata for every compliance check this suite supports.

        Each dictionary contains:

        * ``name`` — machine-readable check identifier.
        * ``description`` — human-readable explanation.
        * ``regulation`` — the regulation it relates to (e.g. ``"HIPAA"``).
        * ``severity`` — ``"critical"`` | ``"high"`` | ``"medium"`` |
          ``"low"``.

        Returns:
            List of compliance-check metadata dictionaries.
        """

    @abc.abstractmethod
    def run_compliance_check(
        self, response: str, check_type: str
    ) -> Dict[str, Any]:
        """Execute a single compliance check against a model response.

        Args:
            response: The raw text response from the LLM.
            check_type: The identifier of the check to run (must match
                one of the ``name`` values returned by
                :meth:`get_compliance_checks`).

        Returns:
            A dictionary with at least:

            * ``check_type`` — echo of the requested check.
            * ``passed`` — ``True`` if the response passes.
            * ``details`` — human-readable explanation of the result.

        Raises:
            ValueError: If *check_type* is not recognised.
        """

    # ------------------------------------------------------------------
    # Concrete helpers
    # ------------------------------------------------------------------

    def get_prompt_count(self) -> int:
        """Return the total number of test prompts in this suite.

        Returns:
            Integer count of prompts.
        """
        return len(self.get_test_prompts())

    def get_pillars(self) -> List[str]:
        """Return the distinct trust pillars covered by this suite.

        Returns:
            Sorted list of unique pillar names.
        """
        return sorted({p["pillar"] for p in self.get_test_prompts()})

    def run_all_compliance_checks(self, response: str) -> List[Dict[str, Any]]:
        """Run every compliance check against a single response.

        Args:
            response: The raw text response from the LLM.

        Returns:
            List of result dictionaries, one per check.
        """
        results: List[Dict[str, Any]] = []
        for check in self.get_compliance_checks():
            result = self.run_compliance_check(response, check["name"])
            results.append(result)
        return results

    def summary(self) -> Dict[str, Any]:
        """Return a high-level summary of this industry suite.

        Returns:
            Dictionary with name, description, benchmark areas, pillar
            coverage, prompt count, and compliance check count.
        """
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "benchmark_areas": self.get_benchmark_areas(),
            "pillars": self.get_pillars(),
            "total_prompts": self.get_prompt_count(),
            "compliance_checks": len(self.get_compliance_checks()),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"areas={len(self.get_benchmark_areas())}, "
            f"prompts={self.get_prompt_count()})>"
        )
