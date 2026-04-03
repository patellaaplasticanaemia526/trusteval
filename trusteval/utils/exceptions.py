# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

"""Custom exception hierarchy for TrustEval.

All TrustEval exceptions inherit from ``TrustEvalError`` so callers can
catch a single base class while still differentiating specific failure
modes when needed.
"""

from __future__ import annotations


class TrustEvalError(Exception):
    """Base exception for all TrustEval errors.

    Attributes:
        message: Human-readable description of the error.
        details: Optional dict with structured context for logging/debugging.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        if self.details:
            return f"{cls}({self.message!r}, details={self.details!r})"
        return f"{cls}({self.message!r})"


class ProviderConnectionError(TrustEvalError):
    """Raised when a connection to an LLM provider fails.

    Common causes include invalid API keys, network timeouts, and
    provider-side rate limits.
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        status_code: int | None = None,
        details: dict | None = None,
    ) -> None:
        details = details or {}
        if provider:
            details["provider"] = provider
        if status_code is not None:
            details["status_code"] = status_code
        super().__init__(message, details)
        self.provider = provider
        self.status_code = status_code


class EvaluationConfigError(TrustEvalError):
    """Raised when evaluation configuration is invalid or incomplete.

    Examples: unknown pillar name, missing required fields, incompatible
    option combinations.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict | None = None,
    ) -> None:
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, details)
        self.field = field


class PIIDetectedError(TrustEvalError):
    """Raised when personally identifiable information is found in LLM output.

    Attributes:
        pii_types: List of PII categories detected (e.g. ``["email", "ssn"]``).
    """

    def __init__(
        self,
        message: str,
        pii_types: list[str] | None = None,
        details: dict | None = None,
    ) -> None:
        details = details or {}
        pii_types = pii_types or []
        details["pii_types"] = pii_types
        super().__init__(message, details)
        self.pii_types = pii_types


class BenchmarkLoadError(TrustEvalError):
    """Raised when a benchmark suite or test-case file cannot be loaded."""

    def __init__(
        self,
        message: str,
        benchmark: str | None = None,
        details: dict | None = None,
    ) -> None:
        details = details or {}
        if benchmark:
            details["benchmark"] = benchmark
        super().__init__(message, details)
        self.benchmark = benchmark


class ScoringError(TrustEvalError):
    """Raised when score computation or aggregation fails."""


class ValidationError(TrustEvalError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: object = None,
        details: dict | None = None,
    ) -> None:
        details = details or {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = repr(value)
        super().__init__(message, details)
        self.field = field
        self.value = value
