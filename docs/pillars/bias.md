# Bias & Fairness Detection

## Overview

Detects demographic disparities and stereotypes in LLM outputs using counterfactual testing, stereotype detection, and demographic parity analysis.

## Methodology

### Counterfactual Testing
Runs the same prompt with different demographic identifiers (race, gender, age, nationality) and compares output consistency.

### Stereotype Detection
Uses keyword/phrase matching and pattern detection to identify stereotyped language in responses.

### Demographic Parity
For decision-support prompts, measures if outcome recommendations differ by demographic group.

## Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| `demographic_parity_score` | 0-1 | 1 = perfectly fair |
| `counterfactual_consistency` | 0-1 | 1 = identical outputs across demographics |
| `stereotype_density` | 0-1 | 0 = no stereotypes detected |

## Usage

```python
from trusteval.pillars.bias import BiasDetector

detector = BiasDetector()
result = detector.detect(prompt, response)
print(f"Bias Score: {result['score']}")
```
