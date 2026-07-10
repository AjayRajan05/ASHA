# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.2.x   | :x:                |
| < 0.2   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in ASHA, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email: **ajayrajan727@gmail.com**

Include:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to acknowledge reports within **48 hours** and provide a status update within **7 days**.

## Scope

This policy covers:

- PII detection and masking bypasses
- Prompt injection / jailbreak evasion in ASHA's security layer
- Fail-safe behavior failures (data leakage on error paths)
- Dependency vulnerabilities in core `asha` package dependencies

Out of scope:

- Vulnerabilities in third-party LLM providers (OpenAI, Anthropic, etc.)
- Applications that disable privacy features (`privacy=False`, `mode="off"`)
- ML model behavior when using optional `[ml]` extras

## Security Design Principles

ASHA follows these defaults:

- **Privacy-first**: PII masking enabled by default
- **Fail-safe**: Returns original or sanitized content on errors - never crashes the host app
- **No hidden downloads**: Rule-based mode requires no model downloads
- **Local processing**: Core security runs locally; no telemetry sent by default

## Best Practices for Users

- Keep `privacy=True` in production
- Use `mode="strict"` for sensitive workloads
- Run `pip audit` regularly on your environment
- Do not log raw prompts containing PII in production
- Validate ASHA on your own data before compliance use
