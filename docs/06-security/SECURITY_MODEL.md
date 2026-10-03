# Security & Privacy Model

## Assets worth protecting

| Asset | Sensitivity | Where |
|---|---|---|
| Client portfolios: parcels, CAR codes, credit operations | Confidential (bank secrecy context) | `land_parcels`, future `dossiers` |
| Personal data: producers, partners, debtors (names, CPF, kinship), fiscal documents | **Personal data under LGPD**; some potentially sensitive | Shield-RJ data sources (future), seed/mock data (fictional) |
| Issued dossiers and petitions | Legal evidence; integrity is critical | Future `dossiers` + object storage |
| API keys (Registro Rural, ion, Umbra/Airbus, Supabase service role) | Secret, and billable | Hosting secret store |
| Proprietary models and thresholds (M1/M2/S_straw calibrations) | Trade secret | `src/lib`, `research/` |

## Current controls

| Control | State |
|---|---|
| AuthN | Supabase SSR session **or** a demo cookie when `NEXT_PUBLIC_DEMO_MODE=true` |
| Route gate | `middleware.ts` → `/dashboard/*` redirects to login, and `/api/*` returns 401 when unauthenticated. **Verified on 2026-10-03:** an anonymous POST to `/api/land/enrich` and `/api/dossier/generate` gets 401 |
| AuthZ | ❌ No role or tenant checks in the API (KI-05). RLS is defined in SQL but not exercised (KI-07, KI-26) |
| Input validation | Zod for commercial SAR only; manual checks elsewhere |
| Secrets | `.gitignore` blocks `.env*` except `.env.example`. No secrets were found in the repo during handover (pattern scan for common key formats) |
| Transport | HTTPS via the hosting provider |
| Integrity | SHA-256 over the dossier payload. The signature is a placeholder (KI-01) |
| Logging and audit | ❌ None |

## Threats and required mitigations before a pilot

| # | Threat | Mitigation |
|---|---|---|
| T1 | Anyone becomes `b2b_admin` by setting a cookie | `NEXT_PUBLIC_DEMO_MODE=false` in every non-demo deployment. Remove the demo-cookie path from production builds entirely (build-time flag) |
| T2 | Cross-tenant data access | Role and org checks in every route. Fix RLS with `SECURITY DEFINER` helpers. Add tests that user A cannot read org B |
| T3 | The middleware is bypassed via a path containing `.` | Narrow the exclusion to known static prefixes. Keep `checkApiAuth` in every handler (add it to `enrich`) |
| T4 | Fabricated output mistaken for evidence | KI-01 and KI-03. Label every field with its source and "live vs fixture" |
| T5 | Billing abuse of the Registro Rural key (paid per query) | Per-user rate limits, a server-side cache of demonstrativos (`max_age`), and a spend alert |
| T6 | Leakage of the ion token | Restrict it by domain in the ion dashboard (it is necessarily public) |
| T7 | PII in logs | Structured logging with redaction of CPF/CNPJ |
| T8 | Supply chain | Dependabot (configured), `npm ci` with lockfile, review postinstall scripts |

## LGPD checklist (for the DPO / counsel)

- [ ] Legal basis for each personal-data source (especially the fiscal and corporate data behind Shield-RJ)
- [ ] Records of processing (ROPA) and a DPIA (RIPD) for Shield-RJ, which profiles individuals
- [ ] Data residency: Supabase in `sa-east-1`
- [ ] Retention policy for dossiers and SAR evidence
- [ ] Data-subject request process
- [ ] Processor agreements with Supabase, Vercel and Registro Rural

## Repository hygiene

- **Keep this repository private.** The original monorepo is public.
- The Buritis farm data comes from a real client survey. Confirm consent for its use as the demo reference (CTO_HANDOVER §4).
- Never commit `.env.local`, service-account JSON, ion tokens or client files. Turn on GitHub secret scanning with push protection.
- Report vulnerabilities as described in [`SECURITY.md`](../../SECURITY.md).
