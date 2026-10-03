# Security Policy

## Reporting a vulnerability

Do **not** open a public issue. Report privately to the CTO, or use GitHub's private vulnerability reporting (Security → Report a vulnerability) on this repository. Include the affected route or module, the steps to reproduce and the impact. We aim to acknowledge reports promptly and agree on a fix timeline with the reporter.

## Scope and current posture

The platform is **beta**. Known security gaps are tracked openly, so read these before deploying anywhere that holds real client data:

- [`docs/06-security/SECURITY_MODEL.md`](docs/06-security/SECURITY_MODEL.md): threats, controls and the LGPD checklist.
- [`docs/05-quality/KNOWN_ISSUES.md`](docs/05-quality/KNOWN_ISSUES.md): KI-01 (placeholder signature), KI-04 (fixture fallback), KI-05 (demo auth / no RBAC), KI-26 (RLS).

**Hard rule:** never deploy with `NEXT_PUBLIC_DEMO_MODE=true` where real client data is present.

## Secrets

- Never commit secrets. Only `.env.example` is tracked.
- GitHub secret scanning with push protection must be enabled.
- If a secret leaks, rotate it immediately, then clean up history.
