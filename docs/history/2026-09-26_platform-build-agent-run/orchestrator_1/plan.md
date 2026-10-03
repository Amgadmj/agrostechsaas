# Plan — Agrostech SaaS MVP Platform

## 1. Survey & Scope Mapping (Current)
- Dispatch 3 parallel exploration agents:
  1. `teamwork_preview_explorer` (Codebase Explorer): Survey existing files, project configuration, dependencies (`package.json`), build scripts, and directory structure in `c:/Users/Razer/Desktop/Agrostech/saas`.
  2. `teamwork_preview_spec_miner` (CAR & Regulatory Spec Miner): Probe and document Registro Rural API (`https://docs.registrorural.com.br/reference/consultademonstrativodocar`), endpoints (`/v2/car/demonstrativo/{car}`, `/v2/r2c/situacao`, `/v2/r2c/restricoes`), asynchronous polling flow, M1 Net Plantable Area rules.
  3. `teamwork_preview_spec_miner` (SAR & Risk Spec Miner): Probe BDC STAC Sentinel-1 RTC L2 ARD endpoints, gamma0 backscatter calculations, harvest detection algorithm (M2 Anti-Fuga), commercial SAR tasking schemas, MCR 2-9 / Resolução CMN 5.267/2025 compliance dossier requirements, and Shield-RJ fraud vectors.

## 2. Synthesis & Architecture Definition
- Aggregate Explorer and Spec Miner reports.
- Author `PROJECT.md` at root of SaaS project:
  - Architecture & Code Layout
  - Feature Inventory (fully assigned to milestones)
  - Milestones 1..N with interface contracts and strict dependencies
- Author `TEST_INFRA.md` for Opaque-Box E2E Testing Track.

## 3. Dual-Track Execution
- Implementation Track: Dispatch sub-orchestrator per milestone following strict dependency order.
- E2E Testing Track: Dispatch E2E Testing Orchestrator to build multi-tier test runner and test cases (Tiers 1-4).

## 4. Final Milestone & Hardening
- Pass 100% of E2E tests (Tiers 1-4).
- Adversarial hardening (Tier 5) with Challengers and Reviewers.
- Independent Forensic Auditor verification (Zero Tolerance for mock/cheating).

## 5. Production Build Verification & Final Delivery
- Verify Next.js 15 production build (`npm run build`) and TypeScript check (`tsc --noEmit`).
- Prepare final report and notify parent agent.
