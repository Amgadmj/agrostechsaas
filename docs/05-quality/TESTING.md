# Testing

## What exists

| Suite | Command | Count | Runtime | Gate in CI |
|---|---|---|---|---|
| Tiered requirement suite (`tests/e2e/`) | `npm run test:e2e` | 176 (77 + 75 + 16 + 8) | ~3 s | ✅ blocking |
| Adversarial white-box harnesses (`tests/adversarial/`) | `npm run test:adversarial` | 39 checks | ~1 s | ⚠️ non-blocking (exits 1 on the known defects) |
| Type checking | `npm run typecheck` | n/a | ~20 s | ✅ blocking |
| Production build | `npm run build` | n/a | ~1–2 min | ✅ blocking |

### `tests/e2e/`: how it works

- A **custom harness**, not Jest or Vitest: `harness.ts` (registry + `assert*` helpers), `runner.ts` (runs all tiers, prints a table, exits 0/1) and `run-all.ts` (alias).
- Executed with `tsx`. The path alias `@/` resolves through `tsconfig.json`.
- **Tier 1** has 5 or more cases per feature F1–F15. **Tier 2** covers boundaries and corners. **Tier 3** has cross-feature flows. **Tier 4** has eight real-world scenarios (S1 Buritis underwriting … S8 full onboarding → PDF dossier).
- Fixtures: `tests/e2e/fixtures/reference_data.ts` and `buritis_real_polygon.json`.
- To add a test, write `registerXTests()` in a file, call `testTier1|2|3|4(id, name, fn)`, and register the function in `runner.ts`.

### Be honest about what it covers

- Despite the name, **this is not end-to-end**. No HTTP route, browser or database is exercised. It is a library-level integration suite over `src/lib/*`.
- **F11, F13 and F14 do not import production code** (KI-27). They re-implement the rule in the test, so they would pass even if the app were broken.
- **F15** asserts on the text of `.env.example` and `tailwind.config.ts`.
- Several Tier-4 expectations are the fixtures' own numbers, which is circular.

## Recommended target (in order)

1. **Vitest** for unit tests in `src/lib` (fast, watch mode, coverage). Migrate the existing cases gradually; the custom harness can stay as a scenario runner meanwhile.
2. **Route tests:** call the route handlers with a `Request` and assert on status and body, including 401 without auth (KI-05) and 500 on DB failure (KI-06).
3. **Playwright** smoke test of the demo script ([`USER_JOURNEYS.md`](../01-product/USER_JOURNEYS.md)) at 1440 px and 375 px, with an axe accessibility check (the audit target: score ≥ 90).
4. **Contract tests** for Registro Rural and BDC STAC: record real responses once (with a key), replay them in CI, and re-validate on a schedule.
5. **Model validation set** for M2: real fields with known harvest dates. This is a precision/recall report, not a unit test (see [`M2_SAR_HARVEST_ENGINE.md`](../03-domain-models/M2_SAR_HARVEST_ENGINE.md)).
6. **Make the adversarial suite blocking** once the P1 defects are fixed. Each fixed defect should become a regular regression test.

## Conventions

- Test the domain in `src/lib` without React or Next imports.
- Use the Buritis reference figures (217,12 / 26,91 / 43,42 / 146,79 ha) as the canonical fixture. Never invent a second "real" farm.
- Never call paid external APIs from tests.
