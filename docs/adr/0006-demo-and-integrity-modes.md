# 0006. Explicit demo and integrity modes; fixture data is always labelled

- **Status:** Accepted (retroactive, reinforced by the 2026-10-03 UX audit)
- **Date:** 2026-10-03

## Context

The product must be demoable to investors and banks without paid API keys. The CTO audit also found that unlabelled mock data presented as live destroys credibility with a bank's risk team.

## Decision

- `NEXT_PUBLIC_DEMO_MODE` controls the demo login and the "Dados de Demonstração" badge.
- `INTEGRITY_MODE` (`demo` or `production`) and `ALLOW_MOCK_FALLBACK` control whether external clients may fall back to fixtures.
- Every API response that may come from fixtures carries `source: "live" | "fixture"`, and the UI shows that value.
- Copy never claims more certainty than the data supports.

## Consequences

- Demos work offline.
- **Production mode must never silently serve fixtures.** The current code still can (KI-04), which is a defect against this ADR.
- A field with no real source must be labelled or left out, never fabricated (KI-03).
