# Healthcare Industry Module

## Overview

The Healthcare module evaluates LLMs against clinical AI safety standards, focusing on patient safety, diagnostic accuracy, and HIPAA compliance.

## Benchmark Areas

- **Clinical Question Answering** — Drug interactions, dosage, diagnosis accuracy
- **Medical Triage** — Emergency decision support accuracy
- **ICD/CPT Coding** — Medical coding generation accuracy
- **Patient Communication** — Appropriateness of patient-facing responses
- **Diagnostic Reasoning** — Hallucination rate in clinical reasoning
- **PHI Leakage** — Protected Health Information exposure risk

## Usage

```python
from trusteval import TrustEvaluator

evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4",
    industry="healthcare"
)
result = evaluator.evaluate()
```

## Compliance Checks

- Disclaimer presence in medical responses
- Professional consultation recommendations
- Avoidance of definitive diagnoses
- PHI non-disclosure verification

## Test Coverage

25+ test prompts per benchmark area, covering edge cases for clinical safety.
