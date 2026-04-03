# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Industry benchmark suite registry and factory.

Use :func:`get_industry_suite` to obtain a configured benchmark instance
for a specific regulated industry.  Use :func:`list_industries` to discover
which industries are available.

Example::

    from trusteval.industries import get_industry_suite, list_industries

    print(list_industries())          # ['bfsi', 'healthcare', 'legal', 'retail']
    suite = get_industry_suite("healthcare")
    prompts = suite.get_test_prompts(pillar="safety")
"""

from __future__ import annotations

import logging
from typing import Dict, List, Type

from trusteval.industries.base_industry import BaseIndustry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy registry — populated on first access to avoid import-time side-effects.
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, Type[BaseIndustry]] | None = None


def _build_registry() -> Dict[str, Type[BaseIndustry]]:
    """Import every industry module and map canonical names to classes.

    Returns:
        Mapping from lower-case industry name to its benchmark class.
    """
    from trusteval.industries.bfsi.benchmarks import BFSIBenchmark
    from trusteval.industries.healthcare.benchmarks import HealthcareBenchmark
    from trusteval.industries.legal.benchmarks import LegalBenchmark
    from trusteval.industries.retail.benchmarks import RetailBenchmark

    return {
        "healthcare": HealthcareBenchmark,
        "bfsi": BFSIBenchmark,
        "retail": RetailBenchmark,
        "legal": LegalBenchmark,
    }


def _ensure_registry() -> Dict[str, Type[BaseIndustry]]:
    """Return the registry, building it on first call."""
    global _REGISTRY  # noqa: PLW0603
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def list_industries() -> List[str]:
    """Return sorted list of available industry suite names.

    Returns:
        List of lower-case industry identifiers that can be passed to
        :func:`get_industry_suite`.
    """
    return sorted(_ensure_registry().keys())


def get_industry_suite(name: str) -> BaseIndustry:
    """Instantiate and return the benchmark suite for *name*.

    Args:
        name: Case-insensitive industry identifier (e.g. ``"healthcare"``).

    Returns:
        A fully initialised :class:`BaseIndustry` sub-class instance.

    Raises:
        ValueError: If *name* does not match any registered industry.
    """
    registry = _ensure_registry()
    key = name.strip().lower()
    if key not in registry:
        available = ", ".join(sorted(registry.keys()))
        raise ValueError(
            f"Unknown industry '{name}'. Available industries: {available}"
        )
    logger.info("Loading industry suite: %s", key)
    return registry[key]()


__all__ = [
    "BaseIndustry",
    "get_industry_suite",
    "list_industries",
]
