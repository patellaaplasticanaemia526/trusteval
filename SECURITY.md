# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of TrustEval seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email your findings to **antrixsh@gmail.com**
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Initial Assessment**: Within 5 business days
- **Fix & Release**: Depending on severity, typically within 14 days for critical issues

### What to Expect

- We will acknowledge receipt of your report
- We will investigate and validate the issue
- We will work on a fix and coordinate disclosure
- We will credit you in the security advisory (unless you prefer anonymity)

## Security Best Practices for Users

### API Key Management
- Never commit API keys to version control
- Use environment variables or TrustEval's encrypted KeyManager
- Rotate API keys regularly
- Use the `mask_key()` function when logging

### Dashboard Security
- Always set `TRUSTEVAL_DASHBOARD_KEY` in production
- Never expose the dashboard on public networks without authentication
- Configure `TRUSTEVAL_ALLOWED_ORIGINS` for CORS

### Data Privacy
- Set `TRUSTEVAL_STORE_PROMPTS=false` (default) unless you need prompt storage
- Review audit logs regularly at `~/.trusteval/audit.log`
- Encrypted data is stored using Fernet symmetric encryption

## Dependencies

We regularly scan dependencies for known vulnerabilities using:
- `bandit` for Python code security analysis
- `safety` for dependency vulnerability checking
- GitHub Dependabot for automated dependency updates
