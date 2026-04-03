# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Responsible AI evaluation pillars.

Exports all detector classes and provides a ``get_pillar_detector``
factory function for instantiating detectors by name.
"""

from __future__ import annotations

from typing import Union

from trusteval.pillars.bias.detector import BiasDetector
from trusteval.pillars.hallucination.detector import HallucinationDetector
from trusteval.pillars.pii.detector import PIIDetector
from trusteval.pillars.toxicity.detector import ToxicityDetector

__all__ = [
    "BiasDetector",
    "HallucinationDetector",
    "PIIDetector",
    "ToxicityDetector",
    "get_pillar_detector",
]

# Registry mapping canonical names to detector classes
_DETECTOR_REGISTRY = {
    "bias": BiasDetector,
    "fairness": BiasDetector,
    "hallucination": HallucinationDetector,
    "factuality": HallucinationDetector,
    "pii": PIIDetector,
    "data_leakage": PIIDetector,
    "privacy": PIIDetector,
    "toxicity": ToxicityDetector,
    "safety": ToxicityDetector,
}


def get_pillar_detector(
    name: str,
) -> Union[BiasDetector, HallucinationDetector, PIIDetector, ToxicityDetector]:
    """Factory function to instantiate a pillar detector by name.

    Supports canonical names and common aliases:
        - ``"bias"`` / ``"fairness"`` -> ``BiasDetector``
        - ``"hallucination"`` / ``"factuality"`` -> ``HallucinationDetector``
        - ``"pii"`` / ``"data_leakage"`` / ``"privacy"`` -> ``PIIDetector``
        - ``"toxicity"`` / ``"safety"`` -> ``ToxicityDetector``

    Args:
        name: The name of the pillar (case-insensitive).

    Returns:
        An instance of the corresponding detector class.

    Raises:
        ValueError: If the name does not match any known pillar.
    """
    key = name.lower().strip().replace(" ", "_").replace("-", "_")
    cls = _DETECTOR_REGISTRY.get(key)
    if cls is None:
        available = sorted(set(_DETECTOR_REGISTRY.keys()))
        raise ValueError(
            f"Unknown pillar '{name}'. Available pillars: {available}"
        )
    return cls()
