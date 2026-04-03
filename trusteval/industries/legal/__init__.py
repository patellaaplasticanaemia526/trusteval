# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Legal industry benchmark suite.

Covers contract analysis, legal advice appropriateness, confidentiality,
regulatory references, privilege detection, and jurisdictional awareness —
evaluated against attorney-client privilege and confidentiality standards.
"""

from trusteval.industries.legal.benchmarks import LegalBenchmark
from trusteval.industries.legal.compliance import (
    check_confidentiality_maintained,
    check_jurisdiction_awareness,
    check_legal_disclaimer,
    check_no_unauthorized_practice,
)

__all__ = [
    "LegalBenchmark",
    "check_confidentiality_maintained",
    "check_jurisdiction_awareness",
    "check_legal_disclaimer",
    "check_no_unauthorized_practice",
]
