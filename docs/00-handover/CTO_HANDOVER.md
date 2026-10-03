# CTO Handover: AgrosTech Beta SaaS

**Prepared:** 2026-10-03 · **For:** the incoming CTO and their AI agents · **Classification:** Confidential

This is the first document to read. It explains what the product is, how much of it is real, where the risk sits, and what to do first. Every claim here links to code or to a deeper document.

---

## 1. What this repository is

AgrosTech started as a drone and aerial-survey company (*aerolevantamento*). This repository is the **SaaS platform** it is pivoting to: a **rural-credit risk and collateral-monitoring console** for banks, barter desks, FIAGRO funds and trading companies. It combines three things:

1. **Credit and finance.** A farm's CAR code goes in. What comes out is the **net plantable area** (Model M1), a socio-environmental **MCR 2-9 eligibility** check, a **ScoreCard** and the **Passaporte de Crédito Rural**, plus an exportable **MCR 2-9 dossier** PDF.
2. **Collateral monitoring.** Sentinel-1 **SAR radar** time series detect harvest through cloud cover (Model M2 "Anti-Fuga"). **Shield-RJ** is the fraud-vector war room for pre-planned judicial-recovery schemes.
3. **3D digital twin of the land.** A CesiumJS globe with terrain, the extruded cadastral prism and drone GLB / 3D Tiles. A 2D MapLibre/Deck.gl map adds MapBiomas layers.

**Out of scope here:** the company's internal "AI operating system" (the CrewAI agents, Telegram bot, ClickUp/Geomart automations and Deal Desk). That stays in the original monorepo `Amgadmj/agrostech`.

## 2. Where it came from (provenance)

| Item | Value |
|---|---|
| Source monorepo | `Amgadmj/agrostech` (GitHub, **public** visibility) |
| Source path | `saas/` |
| Source branch / commit | `fix/ux-audit-2026-10` @ `c5feb92` (2026-10-03). **This branch only existed locally when this folder was prepared. It was not merged to `main` or pushed.** |
| Build history | Built 2026-09-26 → 2026-10-03 by an AI agent team: a spec, 4 milestones, an adversarial review, then a UX-audit remediation sprint. All records are in [`docs/history/`](../history/). |
| Related R&D | The IP-models / 3D-twin thesis (`docs/strategy/`) and the novel R&D benchmarks (`research/novel-rd/`), both from the same period. |

## 3. Honest status: what is real and what is demo

| Capability | Code status | Data status |
|---|---|---|
| **M1 net plantable area** (`src/lib/m1/`) | ✅ Implemented, unit-tested, Art. 15 dedup | Uses SICAR areas from the client, but fixtures in demo |
| **Registro Rural CAR client** (`src/lib/registrorural/`) | ✅ Implemented: polling, backoff, diagnostic errors | ⚠️ Never run against a live key; endpoint paths unverified (KI-36) |
| **Enrich pipeline** (`/api/land/enrich`) | ✅ Orchestrates the steps | ❌ Geometries and several fields are hardcoded or random (KI-03) |
| **BDC STAC search** (`src/lib/sar/bdcStacClient.ts`) | ✅ Live search works, with offline fallback | ✅ Real INPE endpoint |
| **SAR backscatter extraction** | ❌ No raster read; constants on live data (KI-02) | Fixtures only |
| **M2 harvest engine** (`src/lib/sar/harvestEngine.ts`) | ✅ Thresholds, alert levels, S_clima | ⚠️ 1 failing and 4 noted defects; precipitation defaults to 4.2 mm (KI-09, KI-11…15) |
| **Commercial SAR tasking** (Umbra, TerraSAR-X) | ✅ Zod schemas and a state machine | ❌ No provider calls; in-memory store (KI-08) |
| **MCR 2-9 dossier** (`src/lib/dossier/`) | ✅ Checks, SHA-256, PDF | ❌ The ICP-Brasil signature and RFC 3161 token are placeholders (KI-01) |
| **Shield-RJ** (`/dashboard/shield-rj`) | ✅ Rich UI: graph, timeline, evidence table, petition draft | ❌ 100% mock scenario (KI-07) |
| **3D digital twin** (`/dashboard/land/[id]/3d`) | ✅ Cesium, terrain, prism, GLB/3D Tiles | ⚠️ Twin assets come from mock parcels; ion token needed (KI-33/34) |
| **Auth / multi-tenancy** | ⚠️ Supabase SSR plus a demo cookie; RLS in the schema | ❌ App doesn't read the DB; no RBAC (KI-05/07) |
| **Persistence** (`/api/land/save`) | ⚠️ Insert code exists | ❌ Fails against a real DB (UUID bug, KI-06) |

**Verified on 2026-10-03:** `npm run typecheck` ✅ · `npm run test:e2e` 176/176 ✅ · `npm run build` ✅ · `npm run test:adversarial` reports 7 failing checks and 6 noted weaknesses (expected; all listed in KNOWN_ISSUES).

## 4. Top risks, in order

1. **Legal: presenting placeholders as real.** The dossier claims an ICP-Brasil signature it doesn't have (KI-01). Shield-RJ drafts a court petition (KI-38). Regulatory citations were never validated by counsel (KI-37). *Do not send any dossier or petition to a bank or court until these are resolved.*
2. **Model credibility.** M2 cannot fire on live data (KI-02), and the thesis §8 "validation" includes demo-scenario numbers (KI-10). Investors and banks will probe this first.
3. **Security.** Demo mode grants admin by cookie (KI-05). The source monorepo is **public**: keep this new repo **private**, and never set `NEXT_PUBLIC_DEMO_MODE=true` on a deployment that holds client data.
4. **Client data.** `tests/e2e/fixtures/buritis_real_polygon.json` and the Buritis figures throughout come from a real client survey (Fazenda Buritis, MG). They were already present in the public monorepo. Confirm with the founders that the client consents to their use as the reference demo.

## 5. Suggested first 30 / 60 / 90 days

**First week (orientation, no feature work)**
- [ ] Read this file, then [`ARCHITECTURE.md`](../02-architecture/ARCHITECTURE.md), then [`KNOWN_ISSUES.md`](../05-quality/KNOWN_ISSUES.md).
- [ ] Follow [`REPO_MIGRATION.md`](./REPO_MIGRATION.md) to create the private repo, CI and branch protection.
- [ ] Run it locally ([`LOCAL_DEVELOPMENT.md`](../04-operations/LOCAL_DEVELOPMENT.md)) and walk the demo script in [`USER_JOURNEYS.md`](../01-product/USER_JOURNEYS.md).
- [ ] Rotate any credentials that ever lived in the old monorepo (Supabase, Registro Rural, Cesium ion), and issue new ones for this repo.
- [ ] Decide on hosting (Vercel + Supabase is the path of least resistance; see [`DEPLOYMENT.md`](../04-operations/DEPLOYMENT.md)).

**Days 1–30: make the demo honest and safe**
- [ ] KI-01: relabel the dossier as an unsigned draft; remove "CONCEDIDO".
- [ ] KI-04/KI-05: production mode must never fall back to fixtures or accept the demo cookie.
- [ ] KI-11, KI-19: fix the two cheapest correctness bugs (float rounding; dossier reusing the M1 calculator).
- [ ] Add ESLint and Playwright smoke tests for the demo script (KI-30/31).

**Days 31–60: first real data path**
- [ ] Get a Registro Rural key and verify endpoints with a contract test (KI-36).
- [ ] Take enrich geometries from SICAR; persist parcels properly (KI-03/06).
- [ ] Read paths from Supabase for the dashboard (KI-07).

**Days 61–90: real radar**
- [ ] SAR zonal statistics from Sentinel-1 RTC COGs in the linear domain (KI-02/12).
- [ ] A precipitation source for S_clima (KI-09).
- [ ] Back-test M2 on one or more real harvested fields with known dates before any client-facing claim.

The longer view is in [`docs/ROADMAP.md`](../ROADMAP.md).

## 6. How to work in this repo with AI agents

- **[`AGENTS.md`](../../AGENTS.md)** at the repo root is the operating manual for coding agents: commands, conventions and guardrails. `CLAUDE.md` imports it.
- **Ground rules that came out of the audit** (keep enforcing them):
  - UI language is pt-BR, and numbers go through `src/lib/format.ts`.
  - **Never claim certainty the data can't support.** Write "indica", "compatível com" or "alerta", never "provado", "impossível" or "concedido".
  - Never name real companies as debtors or creditors in demo data.
  - Never publish turnaround times (*prazos*) in client-facing copy.
- **Decisions are recorded as ADRs** in [`docs/adr/`](../adr/). Add one whenever you reverse or make a structural decision.

## 7. People and open questions for the founders

| Question | Why it matters |
|---|---|
| Is the Buritis client OK with their farm as the public reference demo? | Client data and LGPD (risk 4) |
| Legal entity: "Agrostech Soluções em Aerolevantamento Ltda." (company profile) or "AgrosTech Inteligência Territorial e Perícias Digitais Ltda." (old SaaS README)? | Contracts, the dossier header, the ICP-Brasil certificate subject |
| Which bank or cooperative is the first pilot, and what output format do they accept? | Prioritizes KI-01 vs KI-02 |
| Is `assets.agrostech.xyz` controlled by the company, and where do drone twin assets live today? | 3D twin hosting (KI-34) |
| Where is the source of the external 3D twin app `dashboard-ui-liart-ten.vercel.app`, which the Sidebar still links to? | It is not in this repo (KI-41) |
| Are there any live API contracts (Registro Rural, BDC token, Umbra, Airbus)? | Integration order |
