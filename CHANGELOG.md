# Changelog

All notable changes to TrustEval will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-18

### Added
- Core evaluation engine with 4 Responsible AI pillars (Bias, Hallucination, PII, Toxicity)
- LLM provider connectors for OpenAI, Anthropic, Google Gemini, and HuggingFace
- Industry-specific benchmark modules for Healthcare, BFSI, Retail, and Legal
- CLI tool with rich terminal output (`trusteval evaluate`, `trusteval compare`, etc.)
- Web Dashboard with FastAPI backend and React + Tailwind frontend
- Report generation in PDF, JSON, CSV, and HTML formats
- Application security module (API key encryption, input sanitization, rate limiting, audit logging)
- Comprehensive unit and integration test suite
- CI/CD pipelines for testing, security scanning, and PyPI publishing
- Full documentation with quickstart guide, SDK reference, and industry guides
