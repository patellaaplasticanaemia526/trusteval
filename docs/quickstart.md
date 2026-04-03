# Quickstart Guide

## Installation

```bash
pip install trusteval
```

## SDK Quick Start

```python
from trusteval import TrustEvaluator

# Create evaluator
evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4",
    industry="healthcare",
    pillars=["bias", "hallucination", "pii", "toxicity"]
)

# Run evaluation
result = evaluator.evaluate()

# View results
print(result.summary())
print(f"Overall Score: {result.overall_score:.2f}")
print(f"Trust Level: {result.trust_level}")

# Export report
result.export("healthcare_gpt4_report.pdf")
```

## CLI Quick Start

```bash
# Run a full evaluation
trusteval evaluate \
  --provider openai \
  --model gpt-4 \
  --industry healthcare \
  --output report.pdf

# Quick single-prompt evaluation
trusteval evaluate \
  --provider openai \
  --model gpt-4 \
  --prompt "What is the safe dose of acetaminophen?"
```

## Dashboard Quick Start

```bash
# Launch the web dashboard
trusteval dashboard start
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Set your API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Next Steps

- Read the [SDK Reference](sdk-reference.md) for the full API
- Explore [Industry Modules](industries/healthcare.md) for domain-specific evaluations
- Learn about [Evaluation Pillars](pillars/bias.md) for responsible AI metrics
