# Hallucination Detection

## Overview

Measures factual accuracy, source grounding, confidence calibration, and consistency of LLM outputs.

## Methodology

### Factual Recall Tests
Questions with known ground-truth answers scored on exact/partial match.

### Source Grounding
For RAG-style prompts, verifies model only references provided context.

### Confidence Calibration
Checks if model hedges appropriately when uncertain vs. giving confident wrong answers.

### Contradictory Prompt Testing
Same question asked differently to measure consistency.

## Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| `factual_accuracy` | 0-1 | Accuracy against ground truth |
| `hallucination_rate` | 0-1 | Inverse of accuracy |
| `confidence_calibration` | 0-1 | Appropriate uncertainty expression |
| `consistency_score` | 0-1 | Cross-question consistency |
