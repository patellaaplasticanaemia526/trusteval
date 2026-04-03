# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Banking, Financial Services, and Insurance (BFSI) benchmark suite.

Covers credit decision fairness, fraud detection, KYC/AML compliance,
financial advice appropriateness, regulatory accuracy, and financial PII
leakage — evaluated against GDPR, PCI-DSS, and fair-lending standards.
"""

from trusteval.industries.bfsi.benchmarks import BFSIBenchmark
from trusteval.industries.bfsi.compliance import (
    check_fair_lending_language,
    check_no_discriminatory_factors,
    check_no_financial_pii,
    check_regulatory_disclaimer,
)

__all__ = [
    "BFSIBenchmark",
    "check_fair_lending_language",
    "check_no_discriminatory_factors",
    "check_no_financial_pii",
    "check_regulatory_disclaimer",
]
