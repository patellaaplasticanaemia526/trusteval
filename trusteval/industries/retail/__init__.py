# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Retail industry benchmark suite.

Covers recommendation fairness, customer service quality, return/refund
accuracy, price discrimination detection, review sentiment analysis, and
consumer PII protection — evaluated against consumer protection standards.
"""

from trusteval.industries.retail.benchmarks import RetailBenchmark
from trusteval.industries.retail.compliance import (
    check_consumer_pii_protection,
    check_no_deceptive_practices,
    check_no_price_discrimination,
    check_return_policy_accuracy,
)

__all__ = [
    "RetailBenchmark",
    "check_consumer_pii_protection",
    "check_no_deceptive_practices",
    "check_no_price_discrimination",
    "check_return_policy_accuracy",
]
