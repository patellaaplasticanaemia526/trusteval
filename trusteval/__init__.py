# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""TrustEval — Enterprise LLM Evaluation Framework.

Evaluate large language models across trust pillars including
hallucination, bias, PII leakage, and toxicity with industry-specific
benchmarks and compliance checks.

Quick start::

    from trusteval import TrustEvaluator

    evaluator = TrustEvaluator(
        provider="openai",
        model="gpt-4",
        industry="healthcare",
        api_key="sk-...",
    )
    result = evaluator.evaluate()
    print(result.summary())
"""

from trusteval.version import __version__
from trusteval.core.evaluator import TrustEvaluator, get_industry_suite
from trusteval.providers.provider_factory import ProviderFactory
from trusteval.core.result import EvaluationResult, PillarResult
from trusteval.core.benchmark import BenchmarkSuite

__all__ = [
    "__version__",
    "TrustEvaluator",
    "EvaluationResult",
    "PillarResult",
    "BenchmarkSuite",
    "ProviderFactory",
    "get_industry_suite",
]
