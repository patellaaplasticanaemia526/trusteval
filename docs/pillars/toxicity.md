# Toxicity & Safety Scoring

## Overview

Evaluates LLM outputs for harmful content across multiple categories and tests jailbreak resistance.

## Categories

- Hate speech
- Profanity
- Violence incitement
- Self-harm content
- Sexual content
- Illegal activity facilitation
- Jailbreak susceptibility

## Methodology

### Category-Based Scoring
Each response scored across all toxicity categories using keyword detection and pattern matching.

### Jailbreak Resistance
Tests known jailbreak patterns (role-play, hypothetical framing, DAN-style) and measures refusal rate.

### NSFW Content Detection
Keyword lists and pattern-based classification for unsafe content.

## Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| `overall_safety_score` | 0-1 | Aggregate safety |
| `jailbreak_resistance` | 0-1 | % of jailbreaks refused |
| `category_scores` | dict | Per-category scores |
