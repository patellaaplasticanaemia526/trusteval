# Security Guide

## API Key Management

TrustEval encrypts API keys at rest using Fernet symmetric encryption.

### Using Environment Variables (Recommended)
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...
export HUGGINGFACE_API_KEY=hf_...
```

### Using KeyManager
```python
from trusteval.security import KeyManager

km = KeyManager()
km.store_key("openai", "sk-...")  # Encrypted at rest
key = km.get_key("openai")       # Returns decrypted
km.rotate_key("openai", "sk-new-key...")
```

Keys are stored encrypted in `~/.trusteval/keys.enc`.

## Dashboard Authentication

Set the dashboard API key:
```bash
export TRUSTEVAL_DASHBOARD_KEY=your-secret-key
```

All dashboard requests require the `X-TrustEval-Key` header.

## Rate Limiting

- SDK: 60 requests/minute per provider (configurable)
- Dashboard POST: 10 requests/minute per IP
- Dashboard GET: 100 requests/minute per IP

## Audit Logging

All evaluation runs and key access events are logged to `~/.trusteval/audit.log` with tamper-evident SHA256 hash chains.

## Input Sanitization

- Maximum prompt length: 8000 characters
- Control character and null byte stripping
- Prompt injection pattern detection
- UTF-8 validation

## Data Privacy

- Prompts are NOT stored by default (`store_prompts: false`)
- When enabled, prompts are encrypted at rest
- Daily log rotation with 30-day retention
