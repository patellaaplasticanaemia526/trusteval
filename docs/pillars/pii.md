# PII / Data Leakage Detection

## Overview

Identifies personal data leakage risks in LLM outputs using comprehensive regex patterns and behavioral testing.

## Detection Capabilities

- Social Security Numbers (SSN)
- Credit card numbers (with Luhn validation)
- IBAN / Bank account numbers
- Email addresses
- US phone numbers
- Medical Record Numbers (MRN)
- IP addresses
- Passport numbers
- Driver's license numbers

## Methodology

### PII Pattern Scanning
Comprehensive regex library scans all model outputs for PII patterns.

### PII Echo Testing
Includes PII in prompts and checks if model unnecessarily echoes it back.

### Prompt Injection Leakage
Tests if model can be tricked into revealing training data or generating fake PII.

## Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| `pii_leakage_rate` | 0-1 | 0 = no PII leaked |
| `pii_echo_rate` | 0-1 | Echo frequency |
| `pii_types_found` | list | Categories of PII detected |
