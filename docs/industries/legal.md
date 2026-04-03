# Legal & Compliance Industry Module

## Overview

The Legal module evaluates LLMs for contract analysis accuracy, legal advice appropriateness, and confidentiality awareness.

## Benchmark Areas

- **Contract Analysis** — Clause identification accuracy
- **Legal Advice Appropriateness** — Must not give definitive legal advice
- **Confidentiality** — Attorney-client privilege awareness
- **Regulatory References** — GDPR, HIPAA, CCPA accuracy
- **Privilege Detection** — Privileged information handling
- **Jurisdictional Awareness** — Multi-jurisdiction considerations

## Usage

```python
from trusteval import TrustEvaluator

evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4",
    industry="legal"
)
result = evaluator.evaluate()
```
