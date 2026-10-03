# Original User Request

## Initial Request — 2026-09-26T14:37:26Z

<USER_REQUEST>
Build the institutional-grade Agrostech SaaS MVP platform for investor fundraising (US$ 600K SAFE @ US$ 4M cap) and enterprise bank/barter pilots, connecting real Registro Rural CAR demonstrativos, dual-track SAR orbital telemetry (INPE Sentinel-1 RTC baseline + commercial high-res tasking hooks), and automated MCR 2-9 compliance dossiers under BCB Resolução CMN nº 5.267/2025.

Working directory: c:/Users/Razer/Desktop/Agrostech/saas
Integrity mode: demo

## Requirements

### R1. Live Registro Rural CAR API Integration (Strict Production Mode)
Integrate the land onboarding pipeline with the live Registro Rural API (`https://docs.registrorural.com.br/reference/consultademonstrativodocar`). The client must require `REGISTRO_RURAL_API_KEY` in environment configuration, query official SICAR demonstrativos (`GET /v2/car/demonstrativo/{car}`), handle asynchronous `PENDING` to `COMPLETE` states, parse property and conservation boundaries (APP, Reserva Legal), execute compliance checks (`/v2/r2c/situacao` and `/v2/r2c/restricoes`), and compute the Net Plantable Area (*Área Útil Líquida* — Model M1). If credentials are missing or invalid, halt with explicit diagnostic errors.

### R2. Dual-Track SAR Satellite Ingestion & All-Weather Harvest Engine (M2 Anti-Fuga)
Implement a dual-track radar architecture:
1. **Baseline Portfolio Track:** Ingest INPE Sentinel-1 RTC L2 Analysis-Ready Data via Brazil Data Cube STAC API (`https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1`). Calculate parcel-level $\gamma^0_{VV}$ and $\gamma^0_{VH}$ temporal backscatter curves at 10m resolution to detect crop phenology, soil moisture shifts, and biomass loss (harvest events) through persistent cloud cover during the rainy season.
2. **Commercial High-Resolution Track:** Implement a modular tasking adapter specification for sub-meter commercial SAR (TerraSAR-X / Umbra) to support on-demand forensic audits on high-value debt restructurings and judicial recovery cases.

### R3. Bank & Barter Enterprise Risk Console & MCR 2-9 Dossier
Deliver a high-polish web console for institutional credit analysts and barter trading desks:
1. Land Onboarding Wizard supporting CAR code query and KML/GeoJSON boundary upload.
2. Real-time ScoreCard displaying ESG ratings, Net Plantable Area ratio, active embargoes, and Passaporte de Crédito Rural eligibility.
3. Interactive 2D (MapLibre/Deck.gl) and 3D (Cesium) parcel visualizers with multi-layer overlays (CAR boundary, APP/RL, SAR backscatter, slope).
4. Shield-RJ timeline visualizing credit fraud vectors (inflated area, unverified harvest, grain diversion alerts, legal restructuring flags).
5. Audit-grade MCR 2-9 compliance report generator with ICP-Brasil digital signature structure complying with Central Bank regulations.

## Acceptance Criteria

### API & Data Pipeline Verification
- [ ] Registro Rural client successfully performs live authenticated requests to `/v2/car/demonstrativo/{car}` with polling on `PENDING` status.
- [ ] M1 Net Plantable Area calculation deducts all verified APP, Reserva Legal, and non-arable geometries from the gross CAR area.
- [ ] BDC STAC client retrieves Sentinel-1 RTC items and extracts $\gamma^0$ assets for specified bounding boxes.
- [ ] Harvest detection algorithm flags an alert when temporal cross-polarization ($\gamma^0_{VH}$) backscatter drops below calibrated threshold.
- [ ] Commercial SAR adapter validates tasking parameter schemas (bbox, resolution mode, polarization).

### User Interface & Risk Console Verification
- [ ] Onboarding wizard successfully inputs a CAR code, displays enrichment progress stages, and renders the parsed geometry.
- [ ] ScoreCard renders all regulatory check results (SICAR status, IBAMA embargos, Biome context, CPR eligibility) with appropriate visual indicators.
- [ ] Map interface renders 2D vector boundaries and 3D terrain elevation seamlessly.
- [ ] One-click export produces a formatted MCR 2-9 compliance dossier summary.

### Build & Environment Standards
- [ ] Next.js 15 production build (`npm run build`) and TypeScript validation (`tsc --noEmit`) pass with zero errors.
- [ ] All configuration keys and documentation are cleanly registered in `.env.example` and `README.md`.
</USER_REQUEST>
