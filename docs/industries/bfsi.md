# BFSI Industry Module

## Overview

The BFSI (Banking, Financial Services & Insurance) module evaluates LLMs for fair lending practices, regulatory compliance, and financial data protection.

## Benchmark Areas

- **Credit Decision Fairness** — Demographic bias in credit scoring
- **Fraud Detection Reasoning** — Accuracy in fraud analysis
- **KYC/AML Compliance** — Know Your Customer and Anti-Money Laundering
- **Financial Advice** — Appropriateness and disclaimer usage
- **Regulatory Accuracy** — Basel, GDPR, PCI-DSS references
- **Financial PII** — IBAN, account numbers, SSN protection

## Usage

```python
from trusteval import TrustEvaluator

evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4",
    industry="bfsi"
)
result = evaluator.evaluate()
```

## Compliance Checks

- Fair lending language verification
- Non-discriminatory factor usage
- Regulatory disclaimer presence
- Financial PII non-disclosure
