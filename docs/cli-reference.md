# CLI Reference

## Installation

```bash
pip install trusteval
```

## Commands

### `trusteval evaluate`

Run an LLM evaluation.

```bash
trusteval evaluate \
  --provider openai \
  --model gpt-4 \
  --industry healthcare \
  --pillars bias,hallucination,pii,toxicity \
  --output report.pdf \
  --verbose
```

Options:
- `--provider` — LLM provider (openai, anthropic, gemini, huggingface)
- `--model` — Model name
- `--industry` — Industry module (healthcare, bfsi, retail, legal)
- `--pillars` — Comma-separated pillar list (default: all)
- `--output` — Output report path
- `--prompt` — Single prompt for quick evaluation
- `--verbose` — Enable verbose output

### `trusteval compare`

Compare two models side-by-side.

```bash
trusteval compare \
  --provider-a openai --model-a gpt-4 \
  --provider-b anthropic --model-b claude-3-opus \
  --industry healthcare
```

### `trusteval providers`

```bash
trusteval providers list          # List all supported providers
trusteval providers test --provider openai    # Test connectivity
trusteval providers configure --provider openai  # Configure API key
```

### `trusteval report`

```bash
trusteval report generate \
  --input results.json \
  --format pdf \
  --output audit-report.pdf
```

### `trusteval dashboard`

```bash
trusteval dashboard start            # Launch with browser
trusteval dashboard start --port 8080 --no-browser
```

### `trusteval config`

```bash
trusteval config set industry healthcare
trusteval config show
trusteval config reset
```
