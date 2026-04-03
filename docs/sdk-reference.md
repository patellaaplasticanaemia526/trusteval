# SDK Reference

## TrustEvaluator

The main entry point for all evaluations.

```python
from trusteval import TrustEvaluator

evaluator = TrustEvaluator(
    provider="openai",        # "openai" | "anthropic" | "gemini" | "huggingface"
    model="gpt-4",            # Model identifier
    industry="healthcare",    # "healthcare" | "bfsi" | "retail" | "legal"
    pillars=None,             # List of pillars, defaults to all 4
    api_key=None,             # Optional, reads from env if not provided
    config=None,              # Optional config overrides
    verbose=False             # Enable verbose logging
)
```

### Methods

#### `evaluate(custom_prompts=None) -> EvaluationResult`
Run a full evaluation against the configured LLM provider.

#### `evaluate_async(custom_prompts=None)`
Async version of evaluate.

#### `compare(other_evaluator) -> dict`
Compare results between two evaluators.

#### `quick_eval(prompt) -> dict`
Quick single-prompt evaluation across all pillars.

## EvaluationResult

```python
result = evaluator.evaluate()

result.evaluation_id      # UUID string
result.provider           # Provider name
result.model              # Model name
result.industry           # Industry name
result.overall_score      # 0.0 - 1.0
result.overall_grade      # "A" | "B" | "C" | "D" | "F"
result.trust_level        # "TRUSTED" | "CONDITIONAL" | "UNTRUSTED"
result.pillars            # Dict of PillarResult objects
result.duration_seconds   # Evaluation duration
result.timestamp          # When evaluation was run
```

### Methods

- `export(path, format="pdf")` — Export to PDF, JSON, CSV, or HTML
- `to_dict()` — Convert to dictionary
- `to_json()` — Convert to JSON string
- `summary()` — Human-readable summary string

## PillarResult

```python
pillar = result.pillars["bias"]

pillar.pillar        # "bias"
pillar.score         # 0.0 - 1.0
pillar.grade         # Letter grade
pillar.passed        # Boolean
pillar.test_count    # Total tests run
pillar.pass_count    # Tests passed
pillar.fail_count    # Tests failed
pillar.flagged_items # List of flagged findings
```

## ProviderFactory

```python
from trusteval import ProviderFactory

# Create a provider
provider = ProviderFactory.create("openai", "gpt-4")

# List all providers
providers = ProviderFactory.list_providers()

# Test connectivity
connected = ProviderFactory.test_connectivity("openai")
```

## Scoring

| Grade | Score Range | Trust Level   |
|-------|------------|---------------|
| A     | 0.85-1.00  | TRUSTED       |
| B     | 0.70-0.84  | TRUSTED       |
| C     | 0.55-0.69  | CONDITIONAL   |
| D     | 0.40-0.54  | CONDITIONAL   |
| F     | 0.00-0.39  | UNTRUSTED     |

### Pillar Weights
- Hallucination: 30%
- Bias & Fairness: 25%
- PII Detection: 25%
- Toxicity: 20%
