# Known Issues & Technical Debt Register

**Last verified:** 2026-10-03, against source commit `c5feb92` (branch `fix/ux-audit-2026-10`).
**How this list was built:** reading the source, running `npm run test:e2e` (176/176 pass) and `npm run test:adversarial` (7 failing checks, 6 noted weaknesses), and the CTO UX audit in [`docs/history/2026-10-03_ux-audit/`](../history/2026-10-03_ux-audit/).

Every item names the file to start from. Severity:

| Level | Meaning |
|---|---|
| **P0** | Blocks use with a real client or bank. The output could be mistaken for a real, legally binding or physically measured result. |
| **P1** | A correctness defect in a model or API. Wrong answers on some inputs. |
| **P2** | Engineering hygiene. Slows the team down or adds operational risk. |

> **The one-line summary for a new CTO:** the domain logic (M1 math, M2 thresholds, MCR 2-9 checks) is real and tested. Most of the *data* entering it is still fixtures or constants, and the *signature* on the dossier is a placeholder. The platform is an investor and pilot demo, not yet a production underwriting system.

---

## P0: Demo vs. real (fix before any real client data)

### KI-01 · The dossier's "ICP-Brasil PAdES-LTV signature" is a placeholder
- **Where:** `src/lib/dossier/generator.ts` (section 6), `src/lib/dossier/pdfGenerator.ts`
- **What:** The SHA-256 hash of the canonical payload is real. Everything else in the signature is not:
  - The certificate chain is hardcoded, with subject `AGROSTECH PERICIAS DIGITAIS LTDA:12345678000199` (a placeholder CNPJ).
  - The "RFC 3161 timestamp token" is the Base64 of a plain string, not an ASN.1 token from a Time-Stamp Authority.
  - No cryptographic signature is applied to the PDF.
  - The PDF prints `Passaporte Credito Rural: CONCEDIDO (REGULAR)`. That is the kind of certainty language the UX audit banned.
- **Risk:** If a bank or court receives this PDF as "digitally signed", that is a legal and reputational problem.
- **Fix:** Integrate a real ICP-Brasil A1/A3 certificate and an accredited TSA (ACT), for example through a signing provider. Until then, label the PDF "minuta não assinada" and remove "CONCEDIDO".

### KI-02 · SAR backscatter is not computed from satellite imagery
- **Where:** `src/lib/sar/temporalEngine.ts` → `generateBackscatterCurve`
- **What:** For each STAC item the engine reads `properties.mean_vh_linear` / `mean_vv_linear`, which only the **fixtures** carry. Live INPE BDC items do not have these fields, so the engine falls back to constants (`-14.5 dB` VH, `-9.5 dB` VV) for every date. No COG raster is ever downloaded or clipped to the parcel.
- **Consequence:** On live data the backscatter curve is flat, so **Model M2 can never detect a harvest**. The live STAC *search* (`bdcStacClient.ts`) does work; only the pixel-extraction step is missing.
- **Fix:** Build a zonal-statistics pipeline that reads the `Gamma0_VH` / `Gamma0_VV` COGs, masks them to the parcel and averages in the **linear** domain (see KI-12). Options: `geotiff.js` in a worker, a small Python service (rasterio), or a managed engine. See [ADR-0005](../adr/0005-dual-track-sar.md).

### KI-03 · `/api/land/enrich` fabricates part of its response
- **Where:** `src/app/api/land/enrich/route.ts`
- **What:**
  - **Fixed geometry:** the APP, Reserva Legal and embargo polygons are always the **Buritis** coordinates, whatever CAR is queried. The parcel boundary also falls back to Buritis (or a Mato Grosso polygon for `MT-` codes) when no GeoJSON is uploaded.
  - **Random identifiers:** `matricula_code` and the IBAMA `process_num` are generated with `Math.random()`.
  - **Hardcoded facts:** SIGEF is always `certified: true`, with a hardcoded "Eng. Agrônomo CREA-MG 48192". Slope, elevation, watershed and soil type are constants.
  - **Derived guess:** `carbon_stock_tco2e = area × 65.7`.
- **Fix:** Take geometries from the SICAR demonstrativo (or the uploaded KML). Remove every generated identifier. Return `null` plus a "not available" flag for anything without a source.

### KI-04 · Fixture fallback can leak into production mode
- **Where:** `src/lib/registrorural/client.ts` (`checkAuth`, `consultarDemonstrativo`), `src/lib/registrorural/fixtures.ts` (`getFixtureForCar`), and the enrich route
- **What:** The route always passes `allowDemoFallback: true`. With no `REGISTRO_RURAL_API_KEY`, the client therefore serves fixtures **even when `INTEGRITY_MODE=production`**. `getFixtureForCar` maps *any* unknown CAR to the Buritis fixture (or the MT/PA fixture by prefix). The response is labelled `source: "fixture"` and the UI shows it, but the request still "succeeds".
- **Fix:** When `INTEGRITY_MODE=production`, the route must call the client with `strict: true`, and unknown CARs must error.

### KI-05 · Authentication and authorization are demo-grade
- **Where:** `src/middleware.ts`, `src/lib/supabase/auth-guard.ts`, `src/app/login/page.tsx`
- **What:**
  - **Cookie login.** With `NEXT_PUBLIC_DEMO_MODE=true`, anyone can set `agrostech_demo_role=b2b_admin` and is fully authenticated. The login page sets that cookie with no password.
  - **No role checks.** Real Supabase sessions are supported, but no route checks the role (`b2c` / `b2b_admin` / `b2b_viewer`), so there is no RBAC.
  - **No tenant isolation in the app.** RLS policies exist in `supabase/schema.sql`, but the pages read `mockData.ts`, not the database.
  - **Middleware bypass.** The middleware skips any path containing `.`, so a route like `/api/x.json` would skip it.
  - **One unguarded route.** `/api/land/enrich` has no `checkApiAuth` of its own (the other five routes do) and relies only on the middleware.
- **Fix:** Production must run with `NEXT_PUBLIC_DEMO_MODE=false`. Then add RBAC to the API, call `checkApiAuth` in enrich, and narrow the middleware's static-file exclusion. See [`docs/06-security/SECURITY_MODEL.md`](../06-security/SECURITY_MODEL.md).

### KI-06 · `/api/land/save` cannot persist to a real database
- **Where:** `src/app/api/land/save/route.ts`
- **What:**
  - **Bad primary key.** It inserts `id: "parcel-<timestamp>"` into a `UUID` primary key, with a hardcoded fallback `owner_id`. Against a real Supabase project the insert fails and the route correctly returns 500.
  - **Silent success on mock URLs.** When the Supabase URL is a mock or empty, it returns success without persisting anything. That is intended for the demo.
- **Fix:** Let Postgres generate the UUID. Take `owner_id` / `org_id` from the session, not the body. Populate `geom` (PostGIS) from the GeoJSON.

### KI-07 · All dashboard screens read static mock data
- **Where:** `src/lib/mockData.ts`, used by `/dashboard`, `/dashboard/shield-rj` and `/dashboard/land/[id]/3d`
- **What:** No page reads from Supabase. The Shield-RJ case (straw entities, CPFs, MDF-e, warehouse) is a fictional scenario built around the Buritis figures.
- **Fix:** Build read APIs and repositories over `land_parcels` and new tables for cases, SAR series and dossiers (see [`DATA_MODEL.md`](../02-architecture/DATA_MODEL.md)).

### KI-08 · Commercial SAR tasking is a specification only
- **Where:** `src/lib/sar/commercial/*`, `src/app/api/sar/commercial/task/route.ts`
- **What:**
  - **Payloads only.** The Umbra and TerraSAR-X adapters validate requests and build payloads, but never call the provider APIs.
  - **In-memory orders.** Orders live in a static in-memory `Map` (`stateMachine.ts`). They are lost on every restart and are not shared between serverless instances.
- **Fix:** Persist orders in Postgres and implement the provider clients behind the existing adapter interface.

### KI-09 · Weather data for the S_clima climate filter is not integrated
- **Where:** `src/lib/sar/harvestEngine.ts`
- **What:** `precipitationMm48h` defaults to **4.2 mm** when the caller does not supply it, so the "climate refutation" passes by default. No weather source (INMET, ERA5, etc.) is connected.
- **Fix:** Integrate a precipitation source per parcel and date. Treat "unknown" as "not refuted".

### KI-10 · The thesis document mixes measured results with the demo scenario
- **Where:** [`docs/strategy/IP_MODELS_AND_3D_DIGITAL_TWIN_THESIS.md`](../strategy/IP_MODELS_AND_3D_DIGITAL_TWIN_THESIS.md), §8 "Real-World Field Validation"
- **What:** The Buritis survey figures (217,12 ha, relief, slope classes, 146,79 ha AUL) come from the real drone survey. Three rows do not. The "−6.2 dB backscatter collapse", the "S_clima = 1.00" result and the "MDF-e to debtor's spouse / S_straw = 0.94" row match the **Shield-RJ demo scenario** in `mockData.ts`, and nothing in the repo shows they come from a real case.
- **Fix:** Confirm with the founders. Until then, do not reuse those rows as validation evidence.

---

## P1: Model and API correctness (from `npm run test:adversarial`)

Each ID is a check in `tests/adversarial/`. "FAIL" means the harness check fails today. "Noted" means the harness passes but records a known weakness.

| ID | Status | Module | Defect |
|---|---|---|---|
| KI-11 · ADV-DROP-04 | FAIL | `sar/harvestEngine.ts` | Float subtraction: `-19.6 - (-15.1) = -4.4999…`, so an exact −4.5 dB drop is missed. Round deltas (e.g. to 0.01 dB) before comparing. |
| KI-12 · ADV-RADIO-01 | Noted | `sar/temporalEngine.ts` `calculateZonalStats` | Averages in dB instead of linear intensity, which biases the parcel mean by about −1.5 dB. |
| KI-13 · ADV-SOIL-01 | Noted | `sar/harvestEngine.ts` | The −20 dB bare-soil floor misses no-till (plantio direto) fields with mulch (~−19.5 dB). |
| KI-14 · ADV-SOIL-03 | Noted | `sar/harvestEngine.ts` | Only compares consecutive acquisitions, so a progressive harvest (−3 dB + −3 dB) is missed. |
| KI-15 · ADV-CLIM-04 | Noted | `sar/harvestEngine.ts` | Harvesting during heavy rain suppresses the alert. This is an exploitable evasion path. |
| KI-16 · ADV-COMM-01 | FAIL | `sar/commercial/schema.ts` | `GeoJsonPolygonSchema` accepts out-of-range WGS84 coordinates. |
| KI-17 · ADV-COMM-03 | FAIL | `sar/commercial/schema.ts` | Footprints over 25 km² are not rejected for 0.25 m Spotlight mode. |
| KI-18 · ADV-COMM-04 | Noted | `sar/commercial/schema.ts` | Inverted grazing-angle bounds (min > max) are accepted. |
| KI-19 · ADV-3.3 | FAIL (HIGH) | `dossier/generator.ts` | `rlInAppAreaHa` is not bounded by `min(APP, RL)`, unlike `m1/calculator.ts`, so a hostile input inflates the net area. Reuse `calculateNetPlantableArea` instead of duplicating the formula. |
| KI-20 · ADV-3.4 | FAIL (MED) | `m1/geometry.ts` `computeNetPlantablePolygon` | Overlapping exclusion polygons are punched as separate holes, with no planar union. Use a robust geometry library (e.g. Turf/JSTS) or PostGIS. |
| KI-21 · ADV-2.3 | FAIL (LOW) | `m1/calculator.ts` | `preservationRatio` can exceed 1.0. |
| KI-22 · ADV-4.3 | FAIL (LOW) | calculator vs. dossier | The 300 ha threshold is evaluated on rounded area in one module and raw area in the other. |
| KI-23 | n/a | `dossier/generator.ts` | Magic default: any embargo count > 0 with no area becomes `14.8 ha`. |
| KI-24 · ADV-DROP-01 | Noted | `sar/harvestEngine.ts` | A −4.49 dB drop is not recorded in `maxDropMagnitude`, so the alert level resets to 1 (vegetative) instead of 3 (desiccation). |
| KI-25 | n/a | `api/sar/harvest-check`, `api/sar/temporal` | `harvest-check` always searches the **Buritis bbox** and a fixed 2025-11-01 → 2026-04-15 window, whatever geometry is sent. `temporal` maps unknown CARs to the Buritis polygon. |
| KI-26 | n/a | `supabase/schema.sql` | The RLS policies on `users` and `land_parcels` subquery `public.users` from within a policy on `users`, which Postgres usually rejects with "infinite recursion detected in policy". `check_ibama_intersection` is `SECURITY DEFINER` with no `search_path`. See [`DATA_MODEL.md`](../02-architecture/DATA_MODEL.md#️-review-before-first-real-deployment). |
| KI-27 | n/a | `tests/e2e/tier1/f11_*`, `f13_*`, `f14_*` | These three files never import `src/`. They re-implement the rule inline (e.g. the four Shield-RJ vectors, the S_straw formula, a SHA-256 over a fixture) and test that copy. **The Shield-RJ fraud vectors have no implementation in `src/lib` at all.** They exist only as static UI and mock data. Coverage for F11/F13/F14 is therefore overstated. |

---

## P2: Engineering hygiene

| ID | Issue | Where | Suggested fix |
|---|---|---|---|
| KI-28 | **MapBiomas WMS host is gone.** `geoserver.mapbiomas.org` does not resolve in DNS (checked 2026-10-03, including against 8.8.8.8), so every MapBiomas layer on the 2D map shows "Camada indisponível". `plataforma.alerta.mapbiomas.org` still resolves. | `src/lib/mapbiomas.ts`, `MapView2D.tsx` | Find MapBiomas' current tile/WMS service (or use Google Earth Engine assets) and make the endpoint configurable. |
| KI-30 | No ESLint config. `npm run lint` (`next lint`) prompts interactively and is deprecated in Next 15.5+. | repo root | Add `eslint.config.mjs` with `eslint-config-next`, then add lint to CI. |
| KI-31 | The test suite is called "E2E", but it imports library modules directly. Nothing exercises HTTP routes or the UI. | `tests/e2e/` | Add Playwright for the demo script in [`USER_JOURNEYS.md`](../01-product/USER_JOURNEYS.md) and route-level tests. Several assertions also check fixture values (circular). |
| KI-32 | Basemap licensing: Esri World Imagery and Carto tiles are called directly without an account or key. Check their terms before commercial use. | `MapView2D.tsx`, `MiniMap.tsx` | Move to a licensed provider or self-hosted tiles. |
| KI-33 | **Verified in the browser on 2026-10-03:** without `NEXT_PUBLIC_CESIUM_ION_TOKEN`, Cesium ion answers `401 INVALID_TOKEN`, no imagery or terrain loads, and the globe renders black (only the lime cadastral prism is visible). | `CesiumViewer.tsx` | Make the token mandatory outside demo, or set an explicit non-ion imagery provider. |
| KI-34 | The parcel `model_3d_url` points at `https://assets.agrostech.xyz/models/fazenda-buritis.glb`. Its availability was not verified. | enrich route, `mockData.ts` | Host twin assets in object storage you control, and record them in the DB. |
| KI-35 | Version drift: `cesium: ^1.127` resolves to 1.145 and `next: ^15.1.7` to 15.5. Old docs cite the old versions. | `package.json` | Pin with Renovate/Dependabot and upgrade deliberately. |
| KI-36 | The Registro Rural endpoint paths in the code (`/car/consulta/{car}/demonstrativo`, `/r2c/car/{car}/situacao_car`, `/r2c/car/{car}/restricoes_sicar`) differ from the paths in the original spec (`/v2/car/demonstrativo/{car}`). Neither was verified against a live key. | `registrorural/client.ts` | Verify against https://docs.registrorural.com.br with a real key. Add a contract test. |
| KI-37 | Regulatory statements were never validated by counsel: CMN 5.267/2025, the ">300 ha continuous monitoring" rule, MCR 2-9 citations, STJ REsp 1.758.746/GO and the CPC 300/301 petition template. | UI copy, dossier, thesis | Legal review before any client-facing use. |
| KI-38 | `StrikeModal` generates a legal petition draft (*minuta*) from demo data. | `shield-rj/StrikeModal.tsx` | Keep it behind demo mode until reviewed by a lawyer. |
| KI-39 | The `/dashboard/onboard` first-load JS is 666 kB (deck.gl + maplibre). | build output | Code-split the map and wizard steps. |
| KI-40 | No observability: no error tracking, structured logs or request IDs. | n/a | Add Sentry or OpenTelemetry once deployed. |
| KI-41 | The Sidebar's "Gêmeo 3D" button still opens an **external** app, `https://dashboard-ui-liart-ten.vercel.app/`, and `supabase/seed.sql` stores that URL as `model_3d_url`. Its source code is **not** in this repository. The Header correctly uses the internal `/dashboard/land/[id]/3d`. | `src/components/layout/Sidebar.tsx` (~line 189), `supabase/seed.sql` | Point the Sidebar at the internal route. Ask the founders where the `dashboard-ui` source lives and whether anything in it should be ported. |
| KI-42 | Duplicate ScoreCard: `src/components/dashboard/ScoreCard.tsx` is not imported anywhere; onboarding uses `src/components/wizard/ScoreCard.tsx`. | `src/components/` | Keep one ScoreCard and delete the other. |
| KI-43 | **3D twin does not fly to the parcel on load.** The camera stays at the default ~20,000 km globe view until the user clicks a camera preset ("Voo Drone"). After that, the prism renders correctly. | `CesiumViewer.tsx` (init `flyTo`) | Call `flyTo` after the first render tick, or use `camera.setView` for the initial pose. |
| KI-44 | **Onboarding light-theme contrast.** In light theme the page title and the form inputs on `/dashboard/onboard` step 1 are nearly invisible (light text on a light background). | `src/app/dashboard/onboard/page.tsx` | Replace the remaining static dark-only colours with theme tokens. |
| KI-45 | **Overclaiming and locale leftovers seen in the UI.** "Selo Verde: 100% Conforme EUDR & CMN 5.267" (2D map card), "Fazenda Buritis (100% Regular)" (onboarding preset), "VERIFICADO" badges on fixture data, "Emitir Mandado Cautelar (CPC 301)" (Shield-RJ button; the audit asked for "Gerar minuta"). Numbers still mix `217.12 ha` and `217,12 ha`. | `MapBiomasThematicAuditCard.tsx`, onboarding, `Sidebar.tsx`, Shield-RJ page | Apply the copy rules in `AGENTS.md`; route every number through `src/lib/format.ts`. |

---

## Already fixed in the UX remediation sprint (2026-10-03, commits `e5fd7aa`…`c5feb92`)

These come from [`docs/history/2026-10-03_ux-audit/2026-10-03_UX_AUDIT_REPORT.md`](../history/2026-10-03_ux-audit/2026-10-03_UX_AUDIT_REPORT.md), and the commit messages state they were addressed. All four routes and a clean `npm run build` were re-checked during this handover. The audit's own acceptance criteria (Lighthouse ≥ 90, keyboard-only onboarding) were **not** re-measured.

- **Data credibility:** Shield-RJ figures now match Buritis (217,12 ha / 146,79 ha), real company names were removed, and overclaiming copy was rewritten. A persistent "Dados de Demonstração" badge was added, and enrich returns `source: live | fixture`.
- **One app shell:** a single `AppShell`, with portal context read from a cookie. The Header's "Gêmeo 3D" now points at the internal `/dashboard/land/[id]/3d` (the Sidebar still does not; see KI-41). The layout is responsive.
- **Auth and errors:** the demo cookie is gated behind `NEXT_PUBLIC_DEMO_MODE`. Guards were added to five of the six API routes, false-success states were removed and `alert()` calls were replaced. Cesium assets are now served locally.
- **Accessibility:** 12 px minimum text, focus rings, aria-labels, and dialog roles with focus traps.

## Fixed during this handover (2026-10-03)

- **Missing Cesium Workers on a fresh clone.** `public/cesium` was committed without `Workers/` (it existed only untracked on the founder's machine). It is now generated from `node_modules/cesium` by `scripts/copy-cesium-assets.mjs` on `postinstall`/`predev`/`prebuild`, and gitignored. See [ADR-0004](../adr/0004-cesium-assets-copied-at-install.md).
- **Undeclared dependencies.** `zod` was imported but not declared (it only worked through a transitive install), and `tsx` was used by the test runner but not declared. Both are now in `package.json`.
- **Missing scripts.** `npm run test:e2e`, cited by the old README, did not exist. It is now defined, together with `typecheck` and `test:adversarial`.
- **Wrong env var name.** `.env.example` documented `REGISTRO_RURAL_API_URL`, but the code reads `REGISTRO_RURAL_BASE_URL`. Every variable is now marked READ or RESERVED.
