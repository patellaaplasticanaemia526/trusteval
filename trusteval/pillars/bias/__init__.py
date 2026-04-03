# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Bias and fairness detection pillar.

Exports the ``BiasDetector`` class and key metric functions.
"""

from trusteval.pillars.bias.detector import BiasDetector
from trusteval.pillars.bias.metrics import (
    counterfactual_consistency,
    demographic_parity_score,
    get_stereotype_matches,
    stereotype_density,
)

__all__ = [
    "BiasDetector",
    "counterfactual_consistency",
    "demographic_parity_score",
    "get_stereotype_matches",
    "stereotype_density",
]
