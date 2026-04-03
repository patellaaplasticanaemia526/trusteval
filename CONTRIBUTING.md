# Contributing to TrustEval

Thank you for your interest in contributing to TrustEval! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/trusteval.git`
3. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
4. Install in dev mode: `pip install -e ".[dev]"`
5. Create a branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Code Style
- Follow PEP 8 conventions
- Use Google-style docstrings for all public classes and methods
- Run `ruff check trusteval/` before committing
- Run `mypy trusteval/` for type checking

### Testing
- Write unit tests for all new functionality
- Run tests: `pytest tests/unit -v --cov=trusteval`
- Maintain 80%+ code coverage
- Never make real API calls in tests — always use mocks

### Security
- Never hardcode API keys or secrets
- Run `bandit -r trusteval/` to check for security issues
- Follow the security guidelines in SECURITY.md

## Pull Request Process

1. Update tests for your changes
2. Update documentation if needed
3. Update CHANGELOG.md
4. Ensure all CI checks pass
5. Request review from maintainers

## Areas for Contribution

- New industry modules (Manufacturing, Education, etc.)
- Additional LLM provider connectors
- Improved bias/toxicity detection algorithms
- Dashboard UI improvements
- Documentation and examples
- Bug fixes and performance improvements

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open an issue or reach out to [Antrixsh Gupta](https://www.linkedin.com/in/antrixshgupta).
