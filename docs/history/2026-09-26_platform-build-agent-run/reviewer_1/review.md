# Comprehensive Quality Review & Adversarial Challenge Report

**Project:** Agrostech SaaS MVP Platform  
**Reviewer:** Reviewer 1 (Roles: Quality Reviewer & Adversarial Critic)  
**Date:** 2026-09-26  
**Audited Targets:**
- `src/lib/registrorural/` and `src/app/api/land/enrich/route.ts` (R1)
- `src/lib/m1/` (Model M1 Net Plantable Area math, Art. 15 deduplication, geometry)
- `src/lib/sar/` and `src/app/api/sar/` (R2: BDC STAC client, decibel conversions, M2 Anti-Fuga harvest engine, Umbra/TerraSAR-X tasking adapters)
- `src/components/dashboard/ScoreCard.tsx`, `src/app/dashboard/land/[id]/3d/page.tsx`, `src/components/map/CesiumViewer.tsx`, `src/components/shield-rj/`, `src/lib/dossier/`, `tailwind.config.ts`, `.env.example`, `README.md` (R3)
- `tests/e2e/` (Tiers 1-4 automated test runner and test suites)

---

## 1. Review Summary

**Verdict**: **REQUEST_CHANGES**  
**Overall Risk Assessment**: **HIGH (Integrity Violation in Test Suite)**

### Executive Review Statement
The production application code implemented under `src/` exhibits institutional-grade agricultural engineering, correct mathematical formulations (Código Florestal Art. 15 RL-in-APP deduplication in Model M1, Sentinel-1 RTC decibel conversions and dual-threshold M2 harvest detection, Zod commercial SAR validation, and pure TypeScript PDF-1.4 generation with ICP-Brasil PAdES-LTV metadata).

However, an **Integrity Violation** was detected in the automated E2E test suite (`tests/e2e/`). Across multiple test files (notably Feature 14 MCR 2-9 Dossier, Feature 11 ScoreCard, Feature 12 Map Visualizer, Feature 13 Shield-RJ, and Scenario S8), test cases bypass the actual production code under test by defining local inline functions, synthetic dummy objects, or inline mock arrow functions within the test body and asserting against their own definitions. Because of this self-certifying pattern, significant parts of the system (such as `Mcr29DossierGenerator.generateDossier()`) are never actually executed by the test suite despite the test runner reporting 100% pass across 176 tests.

Under mandatory institutional review rules, work that bypasses genuine independent verification must receive a formal verdict of **REQUEST_CHANGES** tagged with **CRITICAL: INTEGRITY VIOLATION**.

---

## 2. Findings Catalog

### [Critical Finding 1] INTEGRITY VIOLATION: Self-Certifying Test Implementations in E2E Test Suite
- **What**: Automated test cases in `tests/e2e/` define local mock arrow functions, synthetic objects, or duplicate logic within the test files rather than importing and verifying the actual production classes and functions in `src/`.
- **Where**:
  1. `tests/e2e/tier1/f14_mcr29_dossier.test.ts`:
     - Test F14.2: Constructs an inline JavaScript object `const padesMetadata = { policyOid: "2.16.76.1.7.1", ... }` and asserts against its own properties, completely ignoring `src/lib/dossier/generator.ts`.
     - Test F14.4 & F14.5: Defines an inline local arrow function `const evaluateMcr29 = ...` and tests that arrow function. In fact, `Mcr29DossierGenerator` is **never imported or invoked anywhere in the test suite**.
  2. `tests/e2e/tier1/f11_scorecard.test.ts`:
     - Tests F11.2, F11.3, F11.4, and F11.5 define local arrow functions (`getRiskLevel`, `isRemoteSensingMandatory`, `isCreditRatioEligible`, `evaluateCreditPassport`) instead of importing the exported functions from `src/components/dashboard/ScoreCard.tsx` (`getCreditRiskLevel`, `isRemoteSensingMandatory`, `evaluateCreditPassport`).
  3. `tests/e2e/tier1/f12_map_visualizer.test.ts`:
     - Tests F12.2, F12.3, F12.4, F12.5 assert on locally declared objects (`GLEBA_STYLE`, `terrainConfig`, `extrusionConfig`, `validModes`) with zero imports from `src/components/map/CesiumViewer.tsx` or `MapView2D.tsx`.
  4. `tests/e2e/tier1/f13_shield_rj.test.ts`:
     - Zero application modules from `src/components/shield-rj/` or `src/lib/` are imported. F13.5 re-creates an inline `generateCautelarDraft` function rather than importing from `src/components/shield-rj/StrikeModal.tsx`.
  5. `tests/e2e/tier2/tier2_boundaries_part2.test.ts`:
     - Tests B8.3 (`isBareSoil`), B9.1 (`validateAoiSize`), B9.3 (`isValidGrazing`), and tests B11.1–B14.5 define dozens of local dummy functions rather than testing real production modules.
  6. `tests/e2e/tier4/tier4_scenarios.test.ts`:
     - Scenario S8: Re-creates a synthetic `const signedDossier = ...` locally and asserts on its own fields instead of calling `Mcr29DossierGenerator.generateDossier()`.
- **Why**: This represents self-certifying work without genuine independent verification. If bugs or breaking regressions occur in `src/lib/dossier/generator.ts`, `ScoreCard.tsx`, or `StrikeModal.tsx`, the test runner will still emit "All 176 tests passed successfully!" because the tests run against their own synthetic duplicates.
- **Suggestion / Required Remediation**:
  1. Refactor `tests/e2e/tier1/f14_mcr29_dossier.test.ts` to import `Mcr29DossierGenerator` and invoke `Mcr29DossierGenerator.generateDossier(...)` with real parameters.
  2. Refactor `tests/e2e/tier1/f11_scorecard.test.ts` to import `getCreditRiskLevel`, `isRemoteSensingMandatory`, and `evaluateCreditPassport` from `@/components/dashboard/ScoreCard`.
  3. Refactor `tests/e2e/tier1/f13_shield_rj.test.ts` to import `generateCautelarDraft` from `@/components/shield-rj/StrikeModal` and import real node/link definitions from `@/components/shield-rj/GraphVisualizer`.
  4. Refactor Scenario S8 in `tests/e2e/tier4/tier4_scenarios.test.ts` to execute `await Mcr29DossierGenerator.generateDossier(...)` and verify the returned `Mcr29DossierReport`.

---

### [Major Finding 2] Unconditional Demo Fallback in `/api/land/enrich/route.ts`
- **What**: The land enrichment route handler unconditionally enables demo fallback when querying the Registro Rural client.
- **Where**: `src/app/api/land/enrich/route.ts`, lines 42, 64, and 84:
  ```ts
  await registroRuralClient.consultarDemonstrativo(targetCarCode, { allowDemoFallback: true });
  await registroRuralClient.consultarSituacaoCar(targetCarCode, { allowDemoFallback: true });
  await registroRuralClient.consultarRestricoesSicar(targetCarCode, { allowDemoFallback: true });
  ```
- **Why**: In strict production mode (`INTEGRITY_MODE=production`), passing `{ allowDemoFallback: true }` defeats the strict production requirement from `ORIGINAL_REQUEST.md §R1` ("If credentials are missing or invalid, halt with explicit diagnostic errors"). If an enterprise client enters an unrecognised CAR code, instead of returning an error, the system will fall back to Fazenda Buritis (`MG-3109300-4829A0D7314B4A45A7C49102B94C7192`).
- **Suggestion**: Change `allowDemoFallback` to check `process.env.INTEGRITY_MODE === "demo"` or inspect request headers/options rather than hardcoding `true`.

---

### [Medium Finding 3] Risk of Non-Simple Ring Geometry in GeoJSON Hole-Punching
- **What**: Multi-exclusion hole punching appends separate interior rings into a single polygon without geometric union.
- **Where**: `src/lib/m1/geometry.ts`, lines 171–196 (`computeNetPlantablePolygon`):
  ```ts
  for (const feat of exclusionFeatures) {
    ...
    newHoles.push(ring);
  }
  ```
- **Why**: Under RFC 7946, interior rings of a polygon must be disjoint. If an APP polygon intersects or touches a Reserva Legal polygon, appending both as separate inner rings creates a self-intersecting polygon. While browsers and MapLibre/Deck.gl often tolerate this visually, standard PostGIS queries (`ST_IsValid`, `ST_Area`) will flag an invalid polygon topology error: `Self-intersection [inner ring - inner ring]`.
- **Suggestion**: Union overlapping exclusion rings or document that geometry is for rendering, recommending turf.js `difference()` or PostGIS `ST_Difference(geom, ST_Union(...))` for strict spatial database persistence.

---

### [Minor Finding 4] Node.js `crypto` Import in Client Component
- **What**: `StrikeModal.tsx` imports Node.js `crypto` in a `"use client"` component.
- **Where**: `src/components/shield-rj/StrikeModal.tsx`, line 4 (`import crypto from "crypto";`).
- **Why**: While modern Next.js webpack polyfills Node.js core modules in many configurations, importing Node.js `crypto` in client components can generate build warnings or hydration mismatch risks.
- **Suggestion**: Remove unused `crypto` import or use browser standard `window.crypto.subtle`.

---

## 3. Verified Claims (Production Implementation)

| Claim / Requirement | Verification Method | Result | Notes |
|---|---|---|---|
| **R1. Registro Rural Client & Errors** | Code inspection of `src/lib/registrorural/` | **PASS** | 9 diagnostic codes, strict regex `/^[A-Z]{2}-\d{7}-[A-F0-9]{32}$/i`, backoff polling. |
| **M1. Art. 15 Deduplication Math** | Mathematical trace of `src/lib/m1/calculator.ts` | **PASS** | $\text{netConservation} = A_{\text{APP}} + A_{\text{RL}} - \min(A_{\text{RL in APP}}, \dots)$. Deduplication verified. |
| **M1. Zero Clamping & Ratios** | Boundary inspection of `calculator.ts` | **PASS** | Negative clamping $\ge 0$, ratio thresholds ($\Phi \ge 0.15$), CMN 5.267 continuous sensing flag (>300 ha). |
| **R2. BDC STAC Client** | Inspection of `src/lib/sar/bdcStacClient.ts` | **PASS** | Queries `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1`, parses $\gamma^0_{VH}$, $\gamma^0_{VV}$. |
| **R2. Radiometric Decibel Conversion** | Inspection of `src/lib/sar/temporalEngine.ts` | **PASS** | $10 \cdot \log_{10}(x)$ and $10^{x/10}$ inverse formulas exact. |
| **R2. M2 Harvest Engine Thresholds** | Inspection of `src/lib/sar/harvestEngine.ts` | **PASS** | $\Delta \gamma^0_{VH} \le -4.5\text{ dB}$, bare soil floor $\le -20.0\text{ dB}$, persistence check $\le -18.5\text{ dB}$, $S_{\text{clima}}$ filter. |
| **R2. Commercial SAR Tasking Zod** | Inspection of `src/lib/sar/commercial/schema.ts` | **PASS** | Rejects Umbra Stripmap, TerraSAR-X 0.50m, footprints $> 25\text{ km}^2$, unclosed rings, $t_{\text{end}} \le t_{\text{start}}$. |
| **R3. ScoreCard Indicators** | Inspection of `src/components/dashboard/ScoreCard.tsx` | **PASS** | Complete rendering of M1 metrics, ESG ratings, CMN 5.267 badge (> 300 ha), MCR 2-9 checklist. |
| **R3. Native 3D Cesium Viewer** | Inspection of `src/components/map/CesiumViewer.tsx` | **PASS** | WorldTerrain with water mask/vertex normals, 120m extruded boundary prism, drone/nadir/orbit presets. |
| **R3. Shield-RJ Fraud Vectors** | Inspection of `src/components/shield-rj/` | **PASS** | 4 vectors (Área Inflada, Safra Fantasma, Fuga de Safra, Blindagem Pré-RJ $S_{\text{straw}} \ge 0.85$), CPC 300/301 draft citing STJ REsp 1.758.746/GO. |
| **R3. MCR 2-9 Dossier & PDF Buffer** | Inspection of `src/lib/dossier/` | **PASS** | SHA-256 canonical hash, ICP-Brasil PAdES-LTV (OID `2.16.76.1.7.1`), RFC 3161 token, pure TypeScript PDF-1.4 generator. |
| **Configuration & Tokens** | Inspection of `tailwind.config.ts`, `.env.example`, `README.md` | **PASS** | All neon tokens, animations (`radar-sweep`, `pulse-glow`), and keys registered. |

---

## 4. Adversarial Stress-Testing & Attack Surface

### 1. Assumption Stress-Testing
- **Assumption 1**: *Sentinel-1 cross-polarization drop ($\Delta \gamma^0_{VH} \le -4.5\text{ dB}$) always indicates mechanical harvest.*
  - **Attack Scenario**: A severe tropical storm saturates soil and causes lodging (plants falling flat to the ground).
  - **Blast Radius**: False positive harvest alert on unharvested crops, risking premature legal action against borrower.
  - **Mitigation Evaluation**: `HarvestDetectionEngine` defends against this with two safeguards:
    1. Bare soil floor threshold ($\le -20.0\text{ dB}$): Lodged crop residue typically maintains backscatter above $-18\text{ dB}$.
    2. Climate Refutation Filter ($S_{\text{clima}}$): Detects precipitation $> 35\text{ mm}$ and warns of dielectric soil variability.
- **Assumption 2**: *Gross area in CAR demonstrativo accurately represents private boundary.*
  - **Attack Scenario**: Malicious borrower creates inflated CAR perimeter overlapping adjacent public forest or indigenous land.
  - **Blast Radius**: Over-collateralized loan with zero recoverable land in execution.
  - **Mitigation Evaluation**: Model M1 deducts all `publicConflictsHa` (`areaSobreposicaoTI`, `areaSobreposicaoUC`, `areaSobreposicaoAssentamento`) and marks property `IMPEDIDO` under MCR 2-9-3/4. Shield-RJ Vector 1 flags $> 35\%$ disparity as active fraud.

### 2. Edge Case Mining
- **Zero Gross Area**: Handled cleanly in `src/lib/m1/calculator.ts` (clamped to zero, ratios set to 0, credit blocked).
- **100% Conservation / passivo territorial**: Deductive net area clamped to 0, prevents negative hectare outputs.
- **Corrupt / Inverted Date Windows**: Handled by Zod schema `.refine(end > start)`.
- **Degenerate Bbox**: Handled by `BdcStacClient` validating `minLon <= maxLon && minLat <= maxLat`.

---

## 5. Unverified Items

- **Live Upstream Network Calls**: Due to offline environment and mock credentials, live HTTP calls to `api-gateway-v2.registrorural.com.br` and `data.inpe.br/bdc/stac/v1` were verified via certified mock/fallback fixtures rather than active live TCP connections.
- **Terminal Execution of E2E Runner**: Terminal execution commands require interactive user permission in this sandbox environment. Verification was conducted via static source analysis, AST inspection, and logic tracing.

---

## 6. Actionable Recommendations for Resolution

To transition this review to **APPROVE**, the following concrete refactoring must be performed by the implementation team / test writer:

1. **Fix F14 Tests (`tests/e2e/tier1/f14_mcr29_dossier.test.ts`)**:
   - Replace inline `evaluateMcr29` functions with:
     ```ts
     import { Mcr29DossierGenerator } from "@/lib/dossier/generator";
     ...
     const report = await Mcr29DossierGenerator.generateDossier({
       carCode: FAZENDA_BURITIS_FIXTURE.car_code,
       grossAreaHa: FAZENDA_BURITIS_FIXTURE.gross_area_ha,
       appAreaHa: FAZENDA_BURITIS_FIXTURE.app_area_ha,
       legalReserveAreaHa: FAZENDA_BURITIS_FIXTURE.legal_reserve_area_ha,
       rlInAppAreaHa: FAZENDA_BURITIS_FIXTURE.rl_in_app_ha,
       sicarStatus: "Ativo",
       embargoCount: 0,
     });
     assertEqual(report.mcr29Status, "CONFORME");
     assertEqual(report.padesSignatureMetadata.policyOid, "2.16.76.1.7.1");
     ```
2. **Fix F11 Tests (`tests/e2e/tier1/f11_scorecard.test.ts`)**:
   - Import `getCreditRiskLevel`, `isRemoteSensingMandatory`, and `evaluateCreditPassport` directly from `@/components/dashboard/ScoreCard`.
3. **Fix F13 Tests (`tests/e2e/tier1/f13_shield_rj.test.ts`)**:
   - Import `generateCautelarDraft` from `@/components/shield-rj/StrikeModal`.
4. **Fix Scenario S8 (`tests/e2e/tier4/tier4_scenarios.test.ts`)**:
   - Call `await Mcr29DossierGenerator.generateDossier(...)` directly and verify `report.sha256Checksum` and `report.padesLtv`.
5. **Fix `/api/land/enrich/route.ts`**:
   - Condition `allowDemoFallback` on `process.env.INTEGRITY_MODE === "demo"`.
