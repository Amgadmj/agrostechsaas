## 2026-09-26T14:53:26Z

You are the E2E Test Writer for the Agrostech SaaS MVP platform project.
Your Working Directory: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\test_writer_e2e_1
Project Directory: c:\Users\Razer\Desktop\Agrostech\saas
Authoritative User Request: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md
Authoritative Project Specification: c:\Users\Razer\Desktop\Agrostech\saas\PROJECT.md
Test Infrastructure Specification: c:\Users\Razer\Desktop\Agrostech\saas\TEST_INFRA.md

You MUST read the authoritative request at c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md and the test infrastructure specification at c:\Users\Razer\Desktop\Agrostech\saas\TEST_INFRA.md before writing tests.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All tests must be genuine, deterministic, and verifiable. DO NOT create trivial tautology tests. A teamwork_preview_auditor will independently inspect your test suite.

Your Write Ownership:
- tests/e2e/**
- TEST_READY.md (publish at project root when test suite is complete)

Your Mission — Opaque-Box E2E Test Suite Creation:
1. Build the automated test runner in tests/e2e/runner.ts (executable via npx tsx tests/e2e/runner.ts or Node test runner) that executes all test tiers, tabulates results, and exits with code 0 on all pass, or code 1 on failure.
2. Implement Tier 1 — Feature Coverage (>=5 test cases per feature across 15 features = >=75 tests) in tests/e2e/tier1/:
   - F1: API key authentication & diagnostic error codes.
   - F2: SICAR demonstrativo polling transitions (PENDING -> COMPLETE, timeouts).
   - F3: Property, APP, and Reserva Legal boundary parsing and structure.
   - F4: R2C situacao and restricoes compliance checking.
   - F5: Model M1 Net Plantable Area deduction math and formulas.
   - F6: INPE BDC STAC client Sentinel-1 RTC query schemas.
   - F7: Temporal backscatter decibel conversions and curve points.
   - F8: M2 Anti-Fuga harvest detection algorithm and thresholds.
   - F9: Commercial SAR tasking schemas and Zod parameter validation.
   - F10: Onboarding wizard stages and geometry ingestion.
   - F11: ScoreCard ESG, Net Area ratio, and CMN 5.267 (>300 ha) eligibility logic.
   - F12: 2D layers and 3D Cesium elevation component integration.
   - F13: Shield-RJ fraud vectors and CPC 300/301 cautelar strike petition.
   - F14: MCR 2-9 dossier generation and ICP-Brasil PAdES-LTV signature structures.
   - F15: Tailwind tokens & configuration integrity.
3. Implement Tier 2 — Boundary & Corner Cases (>=5 test cases per feature = >=75 tests) in tests/e2e/tier2/:
   - Zero/negative areas, 100% APP overlap, missing geometries, extreme coordinates, malformed CAR strings, network timeouts, invalid polarizations, extreme radar backscatter values.
4. Implement Tier 3 — Cross-Feature Interactions (>=15 tests) in tests/e2e/tier3/:
   - CAR Onboarding + M1 Net Area + ScoreCard integration.
   - SAR Backscatter + M2 Harvest Alert + Shield-RJ Timeline integration.
   - CMN 5.267 Area Threshold (>300 ha) + Continuous SAR Mandate + MCR 2-9 Dossier.
5. Implement Tier 4 — Real-World Application Scenarios (>=8 scenarios) in tests/e2e/tier4/:
   - Scenarios S1 through S8 as defined in TEST_INFRA.md.
6. Publish TEST_READY.md at project root c:\Users\Razer\Desktop\Agrostech\saas\TEST_READY.md summarizing total test counts, tier breakdown, and execution command.
7. Verify that the test runner executes cleanly.
8. Write a detailed handoff report in c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\test_writer_e2e_1\handoff.md and send a completion message to your parent.
