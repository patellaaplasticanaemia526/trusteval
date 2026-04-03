# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Hallucination detection pillar.

Exports the ``HallucinationDetector`` class and key metric functions.
"""

from trusteval.pillars.hallucination.detector import HallucinationDetector
from trusteval.pillars.hallucination.metrics import (
    confidence_calibration,
    consistency_score,
    factual_accuracy,
    hallucination_rate,
)

__all__ = [
    "HallucinationDetector",
    "confidence_calibration",
    "consistency_score",
    "factual_accuracy",
    "hallucination_rate",
]
