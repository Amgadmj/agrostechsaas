# Comprehensive Codebase & Environment Exploration Report
**Project:** Agrostech SaaS MVP (Institutional-Grade Land Intelligence & Risk Console)  
**Location:** `c:\Users\Razer\Desktop\Agrostech\saas`  
**Date/Timestamp:** 2026-09-26T14:47:00Z  
**Author:** Codebase & Environment Explorer (`explorer_codebase_1`)  
**Status:** Completed Exploration & Synthesis

---

## 1. Executive Summary

A comprehensive, read-only architectural investigation was conducted across the `agrostech-saas` project repository at `c:\Users\Razer\Desktop\Agrostech\saas`. 

The repository contains an institutional-grade Next.js 15 App Router platform with React 19, Deck.gl v9, MapLibre GL v4, CesiumJS v1.127, Supabase PostGIS schemas, and Tailwind CSS. The visual identity, layout, thematic MapBiomas WMS layers, and high-fidelity mock data (centered on the real benchmark parcel **Fazenda Buritis - 217.12 ha, MG**) provide a robust starting point.

However, a strict gap analysis against the authoritative specification (`ORIGINAL_REQUEST.md`) reveals that the three core domain pillars are either simulated or unmounted:
1. **R1 (Live Registro Rural CAR API & M1 Model):** Currently simulated via `setTimeout` delays and hardcoded JSON responses in `/api/land/enrich/route.ts`. The real API client (`GET /v2/car/demonstrativo/{car}`, `/v2/r2c/situacao`, `/v2/r2c/restricoes`), asynchronous `PENDING` polling, strict `REGISTRO_RURAL_API_KEY` credential verification, and M1 Net Plantable Area (*Área Útil Líquida*) calculation are missing.
2. **R2 (Dual-Track SAR Ingestion & M2 Harvest Engine):** Mentioned only in static text copy within the Shield-RJ UI. The INPE Sentinel-1 RTC L2 ARD client via Brazil Data Cube (BDC) STAC API (`https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1`), $\gamma^0_{VV}$ and $\gamma^0_{VH}$ temporal curve computation, threshold-based harvest drop detection, and commercial SAR tasking adapter (TerraSAR-X / Umbra) do not yet exist.
3. **R3 (Enterprise Risk Console & MCR 2-9 Dossier):** The 2D map lacks SAR backscatter raster/temporal overlays; `CesiumViewer.tsx` is implemented but orphaned (not imported by `src/app/dashboard/land/[id]/3d/page.tsx`, which embeds an external iframe); the ScoreCard does not display Net Plantable Area ratios or MCR 2-9 compliance flags; and the audit-grade MCR 2-9 compliance report generator with ICP-Brasil digital signature structure under BCB Resolução CMN nº 5.267/2025 is not yet built.

---

## 2. Environment, Build Tooling & Dependency Audit

### 2.1 Package Manifest (`package.json`)
- **Framework:** Next.js `^15.1.7` (App Router)
- **Runtime / View Library:** React `^19.0.0`, React-DOM `^19.0.0`
- **Mapping & Visualization Engines:**
  - `@deck.gl/core`, `@deck.gl/extensions`, `@deck.gl/geo-layers`, `@deck.gl/layers`, `@deck.gl/react`: `^9.1.4`
  - `maplibre-gl`: `^4.7.1`
  - `cesium`: `^1.127.0`
- **Database & Backend:**
  - `@supabase/ssr`: `^0.5.2`
  - `@supabase/supabase-js`: `^2.49.1`
- **Geospatial Utilities & UI:**
  - `@tmcw/togeojson`: `^6.0.0` (KML to GeoJSON conversion)
  - `lucide-react`: `^0.475.0` (Icons)
  - `clsx`: `^2.1.1`, `tailwind-merge`: `^3.0.1`
- **TypeScript & Build Tooling:**
  - `typescript`: `^5.7.3`
  - `tailwindcss`: `^3.4.17`
  - `postcss`: `^8.5.2`, `autoprefixer`: `^10.4.20`
  - `@types/node`: `^22.13.4`, `@types/react`: `^19.0.10`, `@types/react-dom`: `^19.0.4`

### 2.2 TypeScript Configuration (`tsconfig.json`)
- Target: `ES2022`, moduleResolution: `bundler`, module: `esnext`.
- Strict mode: `true`.
- Path aliases: `"@/*": ["./src/*"]`.
- Inclusions: `next-env.d.ts`, `**/*.ts`, `**/*.tsx`, `.next/types/**/*.ts`.

### 2.3 Next.js Configuration (`next.config.mjs`)
- `reactStrictMode: true`
- `transpilePackages`: `@deck.gl/core`, `@deck.gl/layers`, `@deck.gl/geo-layers`, `@deck.gl/react`, `@deck.gl/extensions`.
- Webpack fallback: `{ fs: false, path: false }` for client bundle isolation.

### 2.4 Styling & Design Tokens (`tailwind.config.ts` & `globals.css`)
- **Theme Palette:**
  - Dark Void (`#050505`), Dark Panel (`#0a0d10`), Card Border (`#1f242b`)
  - Radar Emerald (`#00e676`), Telemetry Mint (`#00ff85`), Orbital Cyan (`#00e5ff`)
  - Alert Amber (`#f59e0b`), Hazard Red (`#ef4444`)
- **Observed Config Inconsistency:**
  - Components (`Card.tsx`, `onboard/page.tsx`, `layout.tsx`) use classes `brand-neon` (e.g. `text-brand-neon`, `border-brand-neon`, `selection:bg-brand-neon`) and `shadow-neon`.
  - However, in `tailwind.config.ts`, `brand` has keys `{ emerald, mint, cyan, dark, glow }` (missing `neon`) and `boxShadow` has keys `{ emerald, emerald-lg, cyan, embargo }` (missing `neon`).
  - **Resolution:** Add `neon: "#00e676"` to `theme.extend.colors.brand` and `"neon": "0 0 15px rgba(0, 230, 118, 0.35)"` to `theme.extend.boxShadow`.

### 2.5 Environment Variables (`.env.example` vs `.env.local`)
- Existing variables:
  ```env
  NEXT_PUBLIC_SUPABASE_URL=...
  NEXT_PUBLIC_SUPABASE_ANON_KEY=...
  SUPABASE_SERVICE_ROLE_KEY=...
  NEXT_PUBLIC_CESIUM_ION_TOKEN=...
  NEXT_PUBLIC_MAP_STYLE=https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json
  ```
- **Missing Required Variables:**
  - `REGISTRO_RURAL_API_KEY`: Mandatory for R1 live mode.
  - `REGISTRO_RURAL_API_URL`: Optional configurable base URL (defaulting to official endpoint).
  - `BDC_STAC_URL`: Brazil Data Cube STAC endpoint (`https://data.inpe.br/bdc/stac/v1`).
  - `BDC_ACCESS_TOKEN`: BDC authorization token if required for rate limits.
  - `COMMERCIAL_SAR_API_KEY` / `UMBRA_API_KEY` / `TERRASAR_API_KEY`: Commercial tasking credentials.

---

## 3. Comprehensive File Structure & Architecture Inventory

```
c:\Users\Razer\Desktop\Agrostech\saas\
├── .agents/
│   └── teamwork/
│       ├── ORIGINAL_REQUEST.md             # Authoritative user requirements
│       ├── explorer_codebase_1/            # Working directory of this explorer
│       │   ├── BRIEFING.md
│       │   ├── DISPATCH.md
│       │   ├── progress.md
│       │   ├── exploration_report.md       # THIS REPORT
│       │   └── handoff.md
├── buritis_real_polygon.json               # Real GeoJSON polygon of Fazenda Buritis (196.89 ha / 217.12 ha)
├── next.config.mjs                         # Next.js 15 config with Deck.gl transpilation
├── package.json                            # Next.js 15, Deck.gl 9, MapLibre 4, Cesium 1.127, Supabase SSR
├── tailwind.config.ts                      # Custom tactical dark HUD theme
├── tsconfig.json                           # Strict TS config with @/ path alias
├── .env.example                            # Env template (needs expansion)
├── .env.local                              # Local dev overrides
├── supabase/
│   ├── schema.sql                          # PostGIS database schema, RLS policies, spatial tables
│   └── seed.sql                            # Seed data for Buritis, Sorriso embargo, and B2B orgs
├── public/
│   ├── logo.png                            # AgrosTech brand emblem
│   └── logo.svg                            # AgrosTech vector emblem
└── src/
    ├── app/
    │   ├── globals.css                     # Tactical HUD styling, radar animations, scrollbars
    │   ├── layout.tsx                      # Root layout with fonts (Inter, IBM Plex Mono, Bricolage)
    │   ├── page.tsx                        # Redirects to /dashboard
    │   ├── login/
    │   │   └── page.tsx                    # Dual-portal login (B2B Enterprise vs B2C Rural Producer)
    │   ├── dashboard/
    │   │   ├── page.tsx                    # Main 2D workspace with Sidebar & MapView2D
    │   │   ├── onboard/
    │   │   │   └── page.tsx                # Land Onboarding Wizard (Inputs -> Radar Scanner -> ScoreCard)
    │   │   ├── shield-rj/
    │   │   │   └── page.tsx                # War Room Forense Anti-Golpe (Graph, Timeline, Strike Modal)
    │   │   └── land/[id]/3d/
    │   │       └── page.tsx                # 3D Digital Twin page (currently embedding external iframe)
    │   └── api/
    │       └── land/
    │           ├── enrich/route.ts         # Currently SIMULATED land enrichment endpoint
    │           └── save/route.ts           # Land parcel persistence to Supabase
    ├── components/
    │   ├── layout/
    │   │   ├── Header.tsx                  # Top HUD navbar, portal role badges, view switcher
    │   │   └── Sidebar.tsx                 # Searchable nationwide parcel drawer & metric cards
    │   ├── map/
    │   │   ├── MapView2D.tsx               # 925-line Deck.gl + MapLibre viewer with MapBiomas 9-theme WMS
    │   │   ├── CesiumViewer.tsx            # Standalone CesiumJS 3D viewer (currently orphaned)
    │   │   └── MiniMap.tsx                 # Compact Deck.gl preview used in Onboarding Step 3
    │   ├── wizard/
    │   │   ├── KmlUploader.tsx             # Drag-and-drop KML / GeoJSON parser
    │   │   ├── RadarScanner.tsx            # Animated radar sweep HUD with telemetry feed
    │   │   └── ScoreCard.tsx               # ESG & regulatory checklist (SICAR, SIGEF, IBAMA)
    │   ├── shield-rj/
    │   │   ├── GraphVisualizer.tsx         # SVG debtor/laranja/grain flow network graph
    │   │   ├── RedFlagTimeline.tsx         # Chronological fraud vector timeline
    │   │   └── StrikeModal.tsx             # CPC 301 precautionary seizure modal
    │   └── ui/
    │       ├── Badge.tsx                   # Tactical status badges (regular, warning, embargo, app)
    │       ├── Button.tsx                  # Tactical buttons with glowing states
    │       ├── Card.tsx                    # HUD glass cards
    │       └── Logo.tsx                    # AgrosTech brand component
    ├── lib/
    │   ├── kmlParser.ts                    # KML to GeoJSON parser using @tmcw/togeojson
    │   ├── mapbiomas.ts                    # Official MapBiomas GeoServer WMS & Alerta GraphQL catalog
    │   ├── mockData.ts                     # Benchmark Fazenda Buritis coordinates + nationwide parcels
    │   ├── spatialUtils.ts                 # Spherical polygon area (ha), bbox, and centroid calculations
    │   └── supabase/
    │       ├── client.ts                   # Browser Supabase client
    │       ├── server.ts                   # Next.js Server Components Supabase client
    │       └── middleware.ts               # Session refreshing middleware
    └── types/
        ├── database.ts                     # UserProfile, Organization, LandParcel, Compliance types
        └── geospatial.ts                   # GeoJson types, EnrichmentRequest, EnrichedLandData
```

---

## 4. Deep Module Audit & Technical State

### 4.1 Data Ingestion & API Layer
- **`/api/land/enrich/route.ts`:**
  - Implements simulated latency with `setTimeout(r, 600)`, `setTimeout(r, 500)`, etc.
  - Simulates checks for SICAR, SIGEF, IBGE, and IBAMA.
  - Infers embargo strictly if the string contains `"MT-"` or `"EMBARGO"`.
  - Calculates mock areas by multiplying gross area by fixed percentages (12.4% APP, 20% Legal Reserve).
  - **Verdict:** Fully simulated placeholder. Needs replacement or upgrade with the real Registro Rural client and M1 calculation engine.
- **`/api/land/save/route.ts`:**
  - Accepts `EnrichedLandData` and persists to Supabase `land_parcels` table if credentials are set, otherwise logs and gracefully returns the created parcel record.

### 4.2 Map & Visualization Engines
- **`MapView2D.tsx` (Deck.gl v9 + MapLibre GL v4):**
  - Robust implementation supporting Esri World Imagery satellite basemap.
  - Complete MapBiomas 9-theme WMS layer manager with year selection (1985-2024), opacity sliders, and legend inspector.
  - Vector layers for parcel boundary, APP river buffer, and Legal Reserve.
  - **Missing:** SAR temporal backscatter raster overlay or heatmap; Slope / terrain elevation heatmap.
- **`CesiumViewer.tsx` (CesiumJS v1.127):**
  - Dynamically loads CesiumJS in the browser via CDN script injection to avoid Next.js server-side Webpack bundling crashes.
  - Configures dark atmosphere, WorldTerrain (`Cesium.Terrain.fromWorldTerrain()`), camera angles (drone, nadir, orbit), and boundary wireframes.
  - **Critical Flaw:** It is completely **orphaned**. `src/app/dashboard/land/[id]/3d/page.tsx` ignores this component and embeds an external URL (`https://dashboard-ui-liart-ten.vercel.app/`) in an iframe!
- **`MiniMap.tsx`:**
  - Lightweight Deck.gl canvas used in the Onboarding Wizard to preview enriched geometries.

### 4.3 Shield-RJ Anti-Fraud War Room
- **`src/app/dashboard/shield-rj/page.tsx`:**
  - Highly polished tactical UI designed for debt restructuring and judicial recovery cases.
  - Includes `GraphVisualizer.tsx` displaying the fraudulent triangulations between Debtor, Spouse (Laranja), Son, Silo Receptivo, and Transportadora.
  - Includes `RedFlagTimeline.tsx` highlighting SAR biomass collapse, fake leases, protest surges, and bank credit contraction.
  - Includes `StrikeModal.tsx` for generating court-ready precautionary seizure orders (CPC art. 301).
  - **Missing:** Real SAR Sentinel-1 backscatter charts and commercial SAR tasking triggers.

### 4.4 Geospatial Algorithms (`spatialUtils.ts`)
- Computes approximate spherical polygon area in hectares using the trapezoidal spherical excess method.
- Calculates 2D bounding boxes and centroids.
- Does not currently implement polygon subtraction (clipping non-arable geometries from gross CAR area).

---

## 5. Detailed Gap Analysis Against Authoritative Requirements

| Requirement | Requirement Details | Current Codebase Status | Gap Severity | Concrete Action Needed |
| :--- | :--- | :--- | :--- | :--- |
| **R1.1: Registro Rural CAR API** | Query official SICAR demonstrativos: `GET /v2/car/demonstrativo/{car}` with polling on `PENDING` -> `COMPLETE` | Simulated in `/api/land/enrich/route.ts` with `setTimeout` | **CRITICAL** | Build `src/lib/registrorural/client.ts` with authentication, polling, and geometry extraction. |
| **R1.2: R2C Compliance Calls** | Execute compliance checks (`/v2/r2c/situacao` and `/v2/r2c/restricoes`) | Hardcoded mock steps in API | **CRITICAL** | Implement live calls to R2C endpoints or rigorous fallback with diagnostic error reporting. |
| **R1.3: Credential Handling** | Halt with explicit diagnostic errors if `REGISTRO_RURAL_API_KEY` is missing or invalid | Fallback to mock state without error | **HIGH** | Enforce environment validation in strict production mode. |
| **R1.4: Model M1 (Net Plantable Area)** | Deduct verified APP, Reserva Legal, and non-arable geometries from gross CAR area | Uses static multiplication `0.124` and `0.20` | **HIGH** | Implement Model M1 algorithm computing exact Área Útil Líquida and plantable ratio. |
| **R2.1: INPE Sentinel-1 RTC Ingestion** | Ingest Sentinel-1 RTC L2 ARD from BDC STAC API (`https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1`) | Zero code exists | **CRITICAL** | Build `src/lib/sar/bdcStacClient.ts` to query STAC items and extract $\gamma^0_{VV}$ and $\gamma^0_{VH}$ assets. |
| **R2.2: M2 Anti-Fuga Harvest Engine** | Temporal backscatter curve analysis at 10m resolution; drop detection below calibrated threshold | Only static string copy in Shield-RJ | **CRITICAL** | Implement `src/lib/sar/harvestEngine.ts` to compute temporal trends and trigger harvest alerts. |
| **R2.3: Commercial SAR Tasking Adapter** | Modular adapter for TerraSAR-X / Umbra validating schemas (bbox, resolution, polarization) | Zero code exists | **HIGH** | Implement `src/lib/sar/commercialTasking.ts` with schema validation and tasking simulation. |
| **R2.4: SAR API Endpoints** | Expose SAR telemetry and tasking to frontend | None exist | **HIGH** | Create `/api/sar/sentinel1` and `/api/sar/tasking`. |
| **R3.1: Land Onboarding Wizard** | Input CAR code, show real enrichment stages, render parsed boundary | UI exists, but connected to mock API | **MEDIUM** | Wire onboarding form and RadarScanner to live enrichment API. |
| **R3.2: ScoreCard Enhancements** | Display ESG rating, Net Plantable Area ratio, active embargoes, CPR eligibility | Partial display (lacks Net Plantable ratio and MCR 2-9 status) | **MEDIUM** | Update `ScoreCard.tsx` with M1 metrics and MCR 2-9 indicators. |
| **R3.3: 2D & 3D Map Visualizers** | 2D vector boundaries + SAR overlay; 3D Cesium elevation integration | 2D lacks SAR overlay; CesiumViewer is orphaned | **HIGH** | Integrate SAR layer into `MapView2D.tsx`; Mount `CesiumViewer.tsx` inside `src/app/dashboard/land/[id]/3d/page.tsx` with fallback option. |
| **R3.4: Shield-RJ Timeline** | Credit fraud vectors visualization | UI exists and is very rich | **LOW** | Connect timeline to SAR harvest engine alerts. |
| **R3.5: Audit-grade MCR 2-9 Dossier** | Compliance report generator with ICP-Brasil digital signature structure under BCB Resolução CMN nº 5.267/2025 | Zero code exists | **CRITICAL** | Implement `src/lib/compliance/mcr29Dossier.ts` and UI export modal/button. |
| **Acceptance: Build & Types** | `npm run build` and `tsc --noEmit` pass with zero errors | Not verified via CLI due to timed-out permission prompt | **HIGH** | Resolve Tailwind config tokens (`brand-neon`, `shadow-neon`) to ensure flawless compilation. |

---

## 6. Detailed Architectural Recommendations for Implementation

### 6.1 Architectural Layout
```
src/
├── lib/
│   ├── registrorural/
│   │   ├── client.ts             # Live Registro Rural API client with polling & error handling
│   │   └── types.ts              # Demonstrativo and R2C payload interfaces
│   ├── sar/
│   │   ├── bdcStacClient.ts      # BDC STAC client for INPE Sentinel-1 RTC L2 ARD
│   │   ├── harvestEngine.ts      # Model M2 Anti-Fuga: temporal backscatter & drop detection
│   │   └── commercialTasking.ts  # TerraSAR-X / Umbra modular tasking adapter & schema validator
│   ├── compliance/
│   │   ├── modelM1.ts            # Net Plantable Area (Área Útil Líquida) calculation
│   │   └── mcr29Dossier.ts       # MCR 2-9 report generator with ICP-Brasil signature structure
│   ├── mapbiomas.ts              # Existing WMS catalog (keep intact)
│   ├── spatialUtils.ts           # Existing & extended geometry helpers
│   └── mockData.ts               # Keep Fazenda Buritis benchmark data
├── app/
│   ├── api/
│   │   ├── land/
│   │   │   ├── enrich/route.ts   # Upgraded with Registro Rural & M1 logic
│   │   │   └── save/route.ts
│   │   ├── sar/
│   │   │   ├── sentinel1/route.ts # Serves Sentinel-1 RTC temporal curve & tiles
│   │   │   └── tasking/route.ts   # Commercial SAR tasking endpoint
│   │   └── compliance/
│   │       └── mcr29/route.ts    # Generates or downloads MCR 2-9 dossier
│   └── dashboard/
│       ├── onboard/page.tsx      # Integrated with live enrichment & M1 results
│       ├── land/[id]/3d/page.tsx # Mounted with native CesiumViewer component
│       └── shield-rj/page.tsx    # Connected to SAR M2 alerts
└── components/
    ├── map/
    │   ├── MapView2D.tsx         # Add SAR layer toggle (backscatter heatmap)
    │   └── CesiumViewer.tsx      # Refined and wired into 3D page
    ├── wizard/
    │   └── ScoreCard.tsx         # Displays Net Plantable Area ratio & MCR 2-9 badge
    └── compliance/
        └── Mcr29DossierModal.tsx # One-click export modal with ICP-Brasil signature preview
```

### 6.2 Key Algorithmic Formulations
1. **Model M1 (*Área Útil Líquida*):**
   $$A_{\text{líquida}} = A_{\text{total}} - (A_{\text{APP}} + A_{\text{RL}} + A_{\text{embargada}} + A_{\text{inapta}})$$
   $$\text{Ratio} = \frac{A_{\text{líquida}}}{A_{\text{total}}} \times 100$$
2. **Model M2 (*Anti-Fuga Harvest Detection*):**
   $$\Delta \gamma^0_{VH} = \gamma^0_{VH}(t) - \overline{\gamma^0_{VH}(t_{-30d})}$$
   $$\text{If } \gamma^0_{VH}(t) < -18.5\text{ dB and } \Delta \gamma^0_{VH} < -4.0\text{ dB} \implies \text{ALERTA: COLHEITA DETECTADA}$$
3. **ICP-Brasil Digital Signature Structure:**
   - X.509 v3 Digital Certificate envelope
   - SHA-256 Digest of the Land Parcel GeoJSON + CAR Demonstrativo + SICAR Protocol + Sentinel-1 Verification Hash
   - Timestamp Token (Padrão ICP-Brasil / Carimbo do Tempo)
   - Formatted for banking regulatory audit (BCB Resolução CMN nº 5.267/2025).

---

## 7. Conclusion

The repository has strong foundations: clean Next.js 15 structure, rich GIS capabilities (Deck.gl, MapLibre, Cesium), and high-resolution data for Fazenda Buritis. 

Executing the requirements of `ORIGINAL_REQUEST.md` requires transitioning the platform from a simulated frontend prototype into an active, production-grade land intelligence system by implementing the live Registro Rural client (R1), the dual-track SAR telemetry engine (R2), and the audit-grade MCR 2-9 compliance console with native Cesium 3D and ICP-Brasil signatures (R3).
