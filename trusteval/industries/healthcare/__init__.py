# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Healthcare industry benchmark suite.

Covers clinical question-answering, medical triage, ICD/CPT coding accuracy,
patient communication quality, diagnostic reasoning, and PHI leakage
detection — all evaluated against HIPAA-relevant compliance checks.
"""

from trusteval.industries.healthcare.benchmarks import HealthcareBenchmark
from trusteval.industries.healthcare.compliance import (
    check_disclaimer_present,
    check_no_definitive_diagnosis,
    check_no_phi_disclosure,
    check_professional_referral,
)

__all__ = [
    "HealthcareBenchmark",
    "check_disclaimer_present",
    "check_no_definitive_diagnosis",
    "check_no_phi_disclosure",
    "check_professional_referral",
]
