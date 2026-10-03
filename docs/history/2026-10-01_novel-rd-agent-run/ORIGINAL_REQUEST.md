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

## Follow-up — 2026-10-01T21:01:04Z

Conduct an in-depth R&D investigation and author an Executive & Technical Defensibility Whitepaper / Dossier for SP Ventures and rural credit partners on three novel, uncrowded agtech directions: (1) Área Contínua detection across property boundaries under CMN Res. 5.267, (2) Value-of-Information trigger-based drone dispatch (turning 'drone por gatilho' into an auditable decision model), and (3) Uncertainty-aware probabilistic runoff & erosion risk (SCS-CN Monte Carlo over DTM error). For each candidate, provide prior-art clearance (Google Scholar, INPI, patents), derive Agrostech's own original mathematical formulas to innovate in the unattacked gap, design benchmark experiments against standard industry baselines, and specify concrete pilot validation protocols.

Working directory: c:/Users/Razer/Desktop/Agrostech/novel_rd_directions
Integrity mode: benchmark

## Requirements

### R1. Prior-Art & Patent Landscape Clearance
Perform systematic prior-art searches across Google Scholar, INPI, and patent registries for all three candidates:
- Área contínua & cross-boundary management detection (identifying nearest farm management / field boundary literature and establishing the gap under Brazilian Resolution CMN 5.267).
- Value-of-Information (VoI) remote sensing / UAV trigger systems (contrasting ad-hoc scheduling with decision-theoretic dispatch).
- Drone DTM vertical error propagation in agricultural hydrology (contrasting deterministic Rational Method / standard SCS-CN with Monte Carlo spatial error models).
Confirm the exact boundary where commodity methods stop and Agrostech's patentable/defensible novelty begins.

### R2. Original Mathematical Formulations & Algorithmic Specifications
Develop Agrostech's own original mathematical formulas and step-by-step algorithms designed to solve the unattacked gaps:
- **Área Contínua Detection (3.1)**: Formulate a multi-feature fusion metric combining phenological time-series similarity, Sentinel-1/NISAR SAR coherence synchrony, and machinery pass/row orientation alignment across adjacent CAR polygons to compute a calibrated probability $P(\text{Continuous Operation} \mid \text{Polygons } A, B)$.
- **Value-of-Information Drone Trigger (6.1)**: Formulate a rigorous decision-theoretic dispatch equation $VoI = \mathbb{E}[\Delta \text{Loss}(\text{Action})] \cdot P(\text{Uncertainty}) - C_{\text{flight}}$, factoring satellite cloud cover probability, credit exposure at risk, crop phenological vulnerability window, and marginal flight cost.
- **Probabilistic Runoff & Erosion (1.3)**: Formulate a distributed Monte Carlo perturbation model over DTM vertical error $\mathcal{N}(0, \sigma^2(z, \text{cover}))$, propagating elevation variance through hydrological flow routing and SCS-CN equations to generate per-pixel exceedance probability maps $P(Q > Q_{\text{threshold}})$ and terrace overtopping probabilities.

### R3. Benchmark Protocol & Baseline Comparison Architecture
Design reproducible benchmark evaluation protocols comparing Agrostech's formulas against standard industry baselines:
- Baseline 1: Deterministic single-CAR clipping vs. Agrostech Área Contínua confidence surface.
- Baseline 2: Fixed calendar/ad-hoc drone scouting vs. VoI-optimized trigger dispatch.
- Baseline 3: Deterministic Rational Method ($Q = C I A$) vs. Probabilistic SCS-CN Monte Carlo.
Include executable Python proof-of-concept verification scripts or reproducible synthetic test cases demonstrating the mathematical mechanics and proving computational feasibility.

### R4. Executive & Technical Defensibility Dossier (SP Ventures & Lenders)
Synthesize the investigation into a publication-grade R&D whitepaper and executive dossier formatted for venture capital and banking technical due diligence:
- Executive summary highlighting commercial moats and IP defensibility.
- Regulatory alignment mapping (CMN Res. 5.267 fiscalização rules, ZarcNM management levels, and Forest Code APP 45° thresholds).
- Ground-truth pilot requirements (RTK paired points, rain gauge reference events, field rill surveys).
- 12-month R&D and field validation roadmap with milestone gates.

## Acceptance Criteria

### Prior-Art & Gap Definition
- [ ] For each of the 3 candidates, at least 3 closest prior-art publications or patents are cited with specific reasons why they fail to address the target operational gap.
- [ ] Freedom-to-operate and IP moat analysis explicitly articulated for the Brazilian market (INPI/CMN context).

### Mathematical Rigor
- [ ] Complete mathematical definitions provided for all 3 candidates with unambiguous variable definitions, units, dimensional consistency, and boundary constraints.
- [ ] All equations are translated into structured, step-by-step algorithmic pseudocode ready for engineering implementation.

### Executable Proof-of-Concept & Benchmarks
- [ ] Contains runnable Python demonstration script(s) in the working directory that simulate the mathematical logic on sample inputs and produce comparative benchmark metrics (e.g., error distributions, VoI payoff curves, continuous area confidence scores).
- [ ] Clear quantitative metrics defined for baseline comparison (e.g., Brier score, ROC-AUC, cost savings per hectare, false escalation rate).

### Dossier Completeness
- [ ] The final whitepaper is structured as an investor- and bank-grade technical dossier saved in `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/AGROSTECH_NOVEL_RD_DOSSIER.md`.
- [ ] Includes a 12-month execution roadmap with specific pilot validation gates and resource requirements.

