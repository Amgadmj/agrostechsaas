# Technical Specification Report: Dual-Track SAR Ingestion & Bank Risk Dossier (MCR 2-9)
**Document Version:** 1.0.0  
**Project:** Agrostech SaaS MVP (Institutional Grade)  
**Author:** SAR & Risk Dossier Spec Miner (`spec_miner_sar_risk_1`)  
**Date:** 2026-09-26  
**Status:** Authoritative Specification  

---

## Executive Summary
This document provides the definitive technical specification for **Requirement R2 (Dual-Track SAR Satellite Ingestion & M2 Anti-Fuga Engine)** and **Requirement R3 (Bank & Barter Enterprise Risk Console & MCR 2-9 Dossier)** for the Agrostech SaaS platform.

The platform bridges orbital radar telemetry, Brazilian regulatory compliance (Banco Central do Brasil Resolução CMN nº 5.267/2025 / MCR 2-9), and agricultural credit litigation defense (Shield-RJ forensic engine) to serve institutional agricultural lenders, barter desks, FIAGRO funds, and trading companies.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | SAR Baseline | INPE BDC STAC Collection Query | Query Sentinel-1 RTC Level-2 Analysis-Ready Data collection (`sentinel-1-rtc-1`) via INPE Brazil Data Cube STAC API v1.0.0. | `bbox` (WGS84 `[minX, minY, maxX, maxY]`), `datetime` (ISO-8601 interval `start/end`), `limit` | GeoJSON FeatureCollection of STAC Items with COG asset links | Returns HTTP 400 for malformed bbox/datetime; HTTP 404 if collection not found; HTTP 500/timeout with fallback to cached metadata. | Probed live endpoint `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1` |
| 2 | SAR Baseline | Dual-Polarization $\gamma^0$ Extraction | Ingestion of radiometrically terrain-corrected gamma-nought backscatter in VV (`Gamma0_VV`) and VH (`Gamma0_VH`) polarizations at 10m spatial resolution in IW mode (40m in EW). | STAC Asset URLs for `Gamma0_VH` and `Gamma0_VV` Cloud-Optimized GeoTIFFs (COG), parcel boundary polygon | Linear $\gamma^0$ pixel arrays, converted to decibels: $\gamma^0_{\text{dB}} = 10 \cdot \log_{10}(\gamma^0_{\text{linear}})$ | Returns NaN/NoData for pixels outside swath; mask out layover and radar shadow using `layover_shadow_mask`. | INPE STAC Item metadata asset schemas (`item_assets`) |
| 3 | SAR Baseline | Zonal Temporal Curve Construction | Extraction and time-series aggregation of parcel-level backscatter statistics (mean, median, standard deviation, 10th and 90th percentiles) across Sentinel-1 revisit dates (6-12 days). | Parcel boundary polygon GeoJSON, date range (e.g., 90–180 days), polarization channel (`VH` or `VV`) | Temporal series object: `[{ date: string, vh_mean_db: number, vv_mean_db: number, vh_vv_ratio: number, pixel_count: number }]` | Throws `EmptyIntersectionError` if parcel is completely outside valid swath or cloud storage asset is unreadable. | SAR agronomic phenology literature & Sentinel-1 RTC specs |
| 4 | SAR Baseline | M2 Anti-Fuga Harvest Event Detection | Algorithmic detection of abrupt biomass collapse caused by mechanical harvesting through rain and persistent cloud cover using calibrated $\gamma^0_{VH}$ threshold drops. | Temporal backscatter series, threshold $\Delta \gamma^0_{VH} \le -4.5 \text{ dB}$, minimum bare soil floor ($\le -20.0 \text{ dB}$), climate cross-check index ($S_{\text{clima}}$) | Harvest detection event object: `{ harvest_detected: boolean, confidence: number, estimated_date: string, delta_db: number, biomass_loss_pct: number, alert_level: 1..5 }` | Flags `FalsePositiveAnomaly` if precipitation spike causes transient dielectric drop without persistent vegetation loss. | Codebase inspection (`StrikeModal.tsx`, `RedFlagTimeline.tsx`) & SAR agronomic radar backscatter mechanics |
| 5 | SAR Commercial | High-Res Tasking Adapter Interface | Modular adapter specification for sub-meter commercial X-band SAR tasking (Umbra Space Canopy API and Airbus TerraSAR-X Tasking API) for forensic audits on defaulted or distressed loans. | AOI Polygon/BBox, satellite provider (`umbra` \| `terrasar_x`), imaging mode, target acquisition window, polarization | Tasking Order JSON: `{ order_id: string, provider: string, status: TaskingStatus, feasibility: FeasibilityReport, estimated_cost: number }` | Rejects with `InvalidTaskingParameterError` for oversized AOI, out-of-range incidence angles, or expired time windows. | Umbra Canopy STAC & Airbus TerraSAR-X mission specifications |
| 6 | SAR Commercial | Tasking Parameter Validation Schema | Strict validation of tasking parameters against satellite orbital capabilities and provider SLAs. | JSON payload with `geometry`, `resolution_mode`, `polarization`, `start_datetime`, `end_datetime`, `incidence_angle_min/max` | Validated `TaskingRequest` object or detailed validation error matrix | Throws `ValidationError` listing specific failing constraints (e.g. AOI exceeds max footprint of 25 km² for spotlight mode). | Umbra Canopy API & TerraSAR-X Tasking manual |
| 7 | Regulatory Risk | BCB CMN nº 5.267/2025 & MCR 2-9 Compliance Engine | Automated validation of agricultural credit operations against Brazilian National Monetary Council (CMN) Resolução nº 5.267/2025 and Manual de Crédito Rural (MCR) Seção 2-9 socioenvironmental constraints. | CAR code, parcel boundary GeoJSON, operation area (ha), credit modality | Compliance audit result: `{ is_compliant: boolean, mandatory_remote_sensing: boolean, impediments: Impediment[], mcr_2_9_status: "REGULAR" \| "IMPEDIDO" }` | Emits `CriticalImpedimentError` if parcel intersects IBAMA embargos, indigenous lands, or unallocated public forests (Gleba Pública Tipo B). | Banco Central do Brasil Resolução CMN nº 5.267/2025 & MCR 2-9 regulations |
| 8 | Regulatory Risk | Audit-Grade ICP-Brasil Signature & RFC 3161 Timestamp | Generation of an immutable compliance report PDF with PAdES-LTV (Long Term Validation) signature structure and RFC 3161 cryptographic timestamp (Carimbo do Tempo) for judicial presentation. | Audit report metadata, SHA-256 hash of document, digital certificate (A1/A3 ICP-Brasil), ACT timestamp token | Digitally signed PDF/A bundle with CMS signature dictionary, ACT certificate chain, and cryptographic proof | Returns signature validation error if cryptographic digest mismatches or certificate chain is revoked/untrusted. | ICP-Brasil DOC-ICP-15 and RFC 3161 specifications |
| 9 | Fraud Forensic | Shield-RJ Credit Fraud Vectors | Multi-vector fraud detection engine evaluating: (1) Inflated Area, (2) Unverified/Phantom Harvest, (3) Grain Diversion via straw persons (*laranjas*), (4) Insolvency/Pre-RJ legal restructuring. | CAR geometry, M1 Net Plantable Area, SAR backscatter timeline, SEFAZ NF-e/MDF-e tax manifests, CENPROT protest data | Risk score (0–100), alert level (1–5), detected fraud vectors array, straw person probability ($S_{\text{straw}}$) | Graceful degradation if external fiscal data is inaccessible (falls back to orbital SAR + CAR geometric verification). | Codebase inspection (`src/components/shield-rj/*`, `StrikeModal.tsx`, `GraphVisualizer.tsx`) |
| 10 | Fraud Forensic | Pre-RJ Cautelar Strike Petition Generator | Automated drafting of urgent precautionary search and seizure petitions (*Tutela Cautelar Antecedente de Busca e Apreensão Liminar*) under CPC Arts. 300/301, CPR Law 8.929/1994, and STJ REsp 1.758.746/GO. | Pledged CPR data, creditor identity, debtor identity, detected straw person, warehouse receiver CNPJ, SAR evidence hash | Pre-formatted legal petition ready for Judicial Emergency Plantão (`minuta_peticao_cautelar.pdf / .docx / text`) | Emits warning if required evidence items (e.g. proof of grain diversion in transit) lack cryptographic timestamping. | Codebase inspection (`StrikeModal.tsx`) & STJ binding precedent |
| 11 | Risk Console | Real-time Land ScoreCard Engine | Multi-dimensional scoring model computing ESG Rating (0–100), Rural Credit Risk Level (BAIXO, MÉDIO, ALTO, CRÍTICO), CPR Eligibility, and Passaporte de Crédito Rural AgrosTech. | Enriched land data: SICAR, SIGEF, IBAMA, Environmental Context, Slope, Net Plantable Area | ScoreCard summary: `{ overall_status, score_esg, risk_level, credit_passport_eligible, recommendations }` | Non-blocking scoring; defaulting to ALERTA status if any primary government registry is unreachable. | Codebase inspection (`src/components/wizard/ScoreCard.tsx`, `types/geospatial.ts`) |
| 12 | Visualizer | 2D Multi-Layer Map Engine (Deck.gl / MapLibre) | Synchronized 2D canvas displaying parcel boundaries (Gleba), environmental reserves (APP, Reserva Legal), MapBiomas 9.0 WMS rasters, and SAR backscatter heatmaps. | Parcel polygons GeoJSON, MapBiomas theme selections, SAR raster layer configuration | Hardware-accelerated WebGL viewport with hover tooltips, measurement tools, and GeoJSON export | WebGL fallback for older clients; graceful tile loading retries for external WMS sources. | Codebase inspection (`src/components/map/MapView2D.tsx`) |
| 13 | Visualizer | 3D Digital Twin Viewer (CesiumJS) | High-precision 3D globe rendering parcel boundaries over world terrain, drone photogrammetry DSM (3D Tiles / GLB), elevation profiles, and camera flight paths (drone, nadir, orbit). | Centroid coordinates, parcel polygon boundary, 3D model asset URL (`.glb` or `3dtiles`), terrain provider | Interactive 3D Cesium canvas with altitude readouts, lighting simulation, and boundary wireframe extrusion | Fallback to extruded polygon on standard ellipsoid if custom terrain or 3D model fails to load. | Codebase inspection (`src/components/map/CesiumViewer.tsx`) |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | INPE BDC STAC Query | Bounding box spanning outside Brazil territory or where Sentinel-1 RTC is not processed | API returns HTTP 200 with empty features collection: `{"context": {"matched": 0, "returned": 0, "limit": 1}, "features": []}`. System must inform the user that Sentinel-1 RTC Coverage from BDC is currently restricted to Brazilian national territory. |
| 2 | INPE BDC STAC Query | Date range where satellite was in orbital maintenance or pass was missed | STAC returns empty or sparse items. System must interpolate across closest available acquisitions and flag a confidence reduction warning in the temporal curve. |
| 3 | M2 Harvest Detection | Heavy convective storm right before acquisition date (temporary dielectric soil saturation) | Sudden increase in soil moisture can temporarily shift backscatter upward (+2 to +4 dB) or attenuate signals. M2 engine must verify that a negative drop is accompanied by persistent low backscatter in subsequent passes, cross-referencing meteorological reanalysis ($S_{\text{clima}}$). |
| 4 | M2 Harvest Detection | Crop lodging (*acamamento*) due to violent winds | Partial drop in VH backscatter (-2 to -3 dB) without complete biomass removal. The M2 engine uses a strict threshold ($\Delta \le -4.5 \text{ dB}$ reaching bare-soil floor $\le -20 \text{ dB}$) to distinguish lodging from true mechanical harvesting. |
| 5 | SAR Backscatter Extraction | Small parcel (< 2 ha) with few 10m pixels | Zonal statistics suffer from speckle noise due to low pixel count ($N < 200$). System must apply a 3x3 Lee or Frost speckle filter before computing spatial averages and display a spatial margin-of-error indicator. |
| 6 | Commercial SAR Tasking | AOI exceeds maximum spotlight scene size (e.g. 50 km² requested for Umbra 0.25m spotlight) | Validation schema rejects request immediately with error: `AOI_EXCEEDS_MODE_LIMIT (requested: 50 km², maximum: 25 km² for spotlight mode)`. User is prompted to switch to Stripmap mode or define multiple tasking tiles. |
| 7 | Commercial SAR Tasking | Target acquisition window shorter than satellite revisit orbit opportunity (< 24 hours) | Feasibility check returns `NO_ORBITAL_PASS_AVAILABLE`. System suggests the nearest available satellite pass windows within the subsequent 3–5 days. |
| 8 | BCB CMN 5.267/2025 Audit | Financed area is 299 ha (just under the 300 ha mandatory remote sensing threshold) | System flags that while remote sensing is not legally mandatory under CMN 5.267 for < 300 ha, the institutional lender's internal policy still enforces standard monitoring. The dossier explicitly notes: `REMOTE_SENSING_REGULATORY_EXEMPT_SIZE: false (< 300 ha), INTERNAL_RISK_APPLIED: true`. |
| 9 | MCR 2-9 Socioenvironmental | Partial embargo on a 1,000 ha farm where only 50 ha is embargada by IBAMA | MCR 2-9 prohibits credit for the entire property unless the credit is exclusively for an isolated gleba with distinct matricula and no economic use of the embargada area. System computes `intersection_area_ha` and flags: `BLOQUEIO_MCR_2_9: Gleba intersecta termo de embargo IBAMA nº TAD-991204-A (14.8 ha)`. |
| 10 | Shield-RJ Diversion Engine | Debtor creates new state tax registration (Inscrição Estadual) under spouse's name 10 days before harvest | Fraud engine detects temporal anomaly: `DELTA_T_IE_TO_HARVEST = 10 days (< 30 days critical threshold)` and assigns $S_{\text{straw}} \ge 0.90$, generating a Level 5 Alert (Fuga Iminente). |
| 11 | ICP-Brasil Signature | Offline or unreachable Time-Stamp Authority (ACT) server during PDF dossier generation | Generator halts with `ACT_TIMESTAMP_UNAVAILABLE_RETRY_QUEUE`. It does not issue an uncertified dossier as audit-grade; instead, it retries with secondary ACT endpoint (e.g., Certisign / Serpro / Imprensa Nacional). |
| 12 | 3D Cesium Visualizer | Client browser running in headless VM or device without WebGL 2.0 hardware acceleration | Cesium viewer fails to initialize 3D context. System catches `CesiumWidgetError` and cleanly toggles back to 2D MapLibre/Deck.gl mode with notification: "Aceleração 3D indisponível. Alternado para modo 2D". |

---

## Deep Dive 1: Requirement R2 — Dual-Track SAR Architecture

```
                                  AGROSTECH DUAL-TRACK SAR INGESTION ARCHITECTURE
                                  =================================================

       TRACK 1: BASELINE PORTFOLIO (10m)                            TRACK 2: COMMERCIAL TASKING (Sub-Meter)
       ---------------------------------                            ---------------------------------------
       INPE Brazil Data Cube (BDC) STAC API                         Commercial High-Resolution SAR Providers
       [https://data.inpe.br/bdc/stac/v1]                           [Umbra Space Canopy API / Airbus TerraSAR-X]
                     |                                                                  |
           +---------+---------+                                              +---------+---------+
           |                   |                                              |                   |
    GET /collections    POST /search                                     Umbra Canopy       Airbus TerraSAR-X
    sentinel-1-rtc-1   (bbox, datetime)                                  STAC /tasking      Tasking Order API
           |                   |                                              |                   |
           +---------+---------+                                              +---------+---------+
                     |                                                                  |
             STAC Item Metadata                                                Feasibility & Scheduling
       - Asset: Gamma0_VV (10m COG)                                            - 0.25m - 1.0m Spotlight
       - Asset: Gamma0_VH (10m COG)                                            - Single / Dual-Pol (HH/VV)
       - Asset: layover_shadow_mask                                            - Targeted Acquisition Window
       - Asset: local_incidence_angle                                                   |
                     |                                                                  v
                     v                                                     Targeted Forensic SAR Products
           SAR Radiometric Decibel Conversion                              (GEC / EEC / SICD Analysis-Ready)
           gamma0_dB = 10 * log10(gamma0_linear)                                       |
                     |                                                                  |
                     v                                                                  |
           Zonal Parcel Curve Construction                                              |
           [Mean, Median, Percentiles over Time]                                        |
                     |                                                                  |
                     +---------------------------------+--------------------------------+
                                                       |
                                                       v
                                         M2 ANTI-FUGA HARVEST ENGINE
                                         ---------------------------
                                         - Drop in gamma0_VH <= -4.5 dB
                                         - Bare soil baseline <= -20.0 dB
                                         - Precipitation / S_clima Filter
                                         - SEFAZ NF-e / MDF-e Triangulation
                                                       |
                                                       v
                                          HARVEST EVENT & DIVERSION ALERT
                                          (Shield-RJ Level 1 to 5 Alert)
```

### 1. Track 1: Baseline Portfolio SAR Ingestion (INPE Sentinel-1 RTC L2)

#### 1.1 Authoritative Endpoint Specifications
- **STAC API Root Catalog:** `https://data.inpe.br/bdc/stac/v1`
- **Collection Endpoint:** `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1`
- **Items Endpoint:** `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1/items`
- **Search Endpoint:** `https://data.inpe.br/bdc/stac/v1/search`
- **Specification Standard:** STAC 1.0.0 with extensions:
  - `sar` (v1.0.0)
  - `processing` (v1.0.0)
  - `item-assets` (v1.0.0)
  - `version` (v1.0.0)

#### 1.2 Query Schema
For parcel-level search, the client issues either a `GET` request to `/collections/sentinel-1-rtc-1/items` or a `POST` request to `/search`:

```typescript
// TypeScript Interface for STAC Search Query
export interface BDCStacSearchQuery {
  collections: ["sentinel-1-rtc-1"];
  bbox?: [number, number, number, number]; // [min_lon, min_lat, max_lon, max_lat] in EPSG:4326
  intersects?: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  datetime: string; // ISO-8601 formatted: "YYYY-MM-DDTHH:mm:ssZ/YYYY-MM-DDTHH:mm:ssZ"
  limit?: number;   // Default: 10, Max: 100
  query?: {
    "sar:instrument_mode"?: { eq: "IW" | "EW" };
    "orbit_direction"?: { eq: "ASCENDING" | "DESCENDING" };
    "relative_orbit"?: { eq: number };
  };
}
```

#### 1.3 Asset Catalog & Data Formats
Each STAC item in `sentinel-1-rtc-1` contains the following verified item assets:
- `Gamma0_VH`: Cloud-Optimized GeoTIFF (COG), 10m resolution in IW mode, radiometric terrain corrected, pixel values represented as linear power $\gamma^0$.
- `Gamma0_VV`: Cloud-Optimized GeoTIFF (COG), 10m resolution in IW mode, co-polarized channel.
- `layover_shadow_mask`: 8-bit integer mask flagging pixels obscured by radar layover (active radar foreshortening) and radar shadowing.
- `local_incidence_angle`: Floating point GeoTIFF indicating the incident beam angle relative to the local topographic normal surface (Copernicus 30m Global DEM).
- `thumbnail`: PNG overview preview.

#### 1.4 Mathematical Radiometric Conversion
INPE Sentinel-1 RTC assets store backscatter values in linear intensity scale ($\gamma^0_{\text{linear}}$). For agronomic analysis, crop phenology, and threshold drop detection, values must be converted to logarithmic decibels (dB):
$$\gamma^0_{\text{dB}} = 10 \cdot \log_{10}(\gamma^0_{\text{linear}})$$

When $\gamma^0_{\text{linear}} \le 0$ or represents NoData:
$$\gamma^0_{\text{dB}} = \text{NaN}$$

Cross-polarization ratio (depolarization indicator):
$$\text{CR}_{\text{dB}} = \gamma^0_{VH,\text{dB}} - \gamma^0_{VV,\text{dB}} = 10 \cdot \log_{10}\left(\frac{\gamma^0_{VH,\text{linear}}}{\gamma^0_{VV,\text{linear}}}\right)$$

#### 1.5 Temporal Curve Construction Algorithm
1. **Zonal Masking:** Project parcel polygon into the pixel coordinate space of the COG asset. Filter out pixels flagged by `layover_shadow_mask != 0`.
2. **Despeckling (Optional / Filtered):** Compute the spatial mean ($\mu_{\text{dB}}$) and median ($M_{\text{dB}}$) across all valid interior pixels of the parcel:
   $$\mu_{\text{dB}}(t) = \frac{1}{N} \sum_{i=1}^{N} \gamma^0_{VH,\text{dB}}(p_i, t)$$
   $$\sigma_{\text{dB}}(t) = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} \left(\gamma^0_{VH,\text{dB}}(p_i, t) - \mu_{\text{dB}}(t)\right)^2}$$
3. **Temporal Trajectory:** Build an array ordered by acquisition datetime $t_0, t_1, \dots, t_k$:
   $$\mathcal{T} = \Big\{ \big(t_k, \mu_{VH}(t_k), \mu_{VV}(t_k), \text{CR}(t_k), \sigma_{VH}(t_k)\big) \Big\}_{k=1}^K$$

#### 1.6 M2 Anti-Fuga Harvest Event Detection Algorithm
- **Agronomic Physics:**
  - *Vegetative / Reproductive Phase (Soybean/Corn):* High volume scattering inside the dense canopy produces high $\gamma^0_{VH}$ backscatter (typically between $-16.0 \text{ dB}$ and $-12.0 \text{ dB}$).
  - *Harvest Phase (Colheita):* Mechanical harvesters strip the vegetative canopy within hours, exposing bare soil with low surface scattering. $\gamma^0_{VH}$ plummets to $-20.0 \text{ dB}$ to $-25.0 \text{ dB}$.
- **Mathematical Decision Rule:**
  A harvest event at date $t_k$ is confirmed if:
  1. $\Delta \gamma^0_{VH}(t_k) = \mu_{VH}(t_k) - \mu_{VH}(t_{k-1}) \le \theta_{\text{harvest}}$ where calibrated $\theta_{\text{harvest}} = -4.5 \text{ dB}$.
  2. The post-event backscatter drops below the bare-soil threshold: $\mu_{VH}(t_k) \le -19.5 \text{ dB}$.
  3. The post-event condition persists at $t_{k+1}$: $\mu_{VH}(t_{k+1}) \le -18.5 \text{ dB}$.
  4. Climate Refutation Filter ($S_{\text{clima}}$): Precipitation in the preceding 48 hours is verified via meteorological reanalysis (e.g. INMET / ERA5). Rain causes dielectric increases (higher backscatter), so a sharp drop *cannot* be explained by rain.
- **Alert Levels:**
  - **Level 1 (Monitoring):** Normal vegetative development, stable $\gamma^0_{VH}$.
  - **Level 2 (Senescence):** Gradual decrease in moisture content, $-2.0 \text{ dB} \le \Delta \le -1.0 \text{ dB}$.
  - **Level 3 (Harvest Imminent):** Crop reaches full physiological maturity, field desiccated.
  - **Level 4 (Harvest Confirmed):** $\Delta \gamma^0_{VH} \le -4.5 \text{ dB}$, biomass collapse verified through clouds.
  - **Level 5 (Fuga Noturna / Active Diversion):** Harvest confirmed via SAR, but no corresponding NF-e / MDF-e issued under debtor's CNPJ, or transport manifest issued under third-party *laranja*.

---

### 2. Track 2: Commercial Sub-Meter SAR Tasking Adapter

For high-stakes judicial recovery disputes, debt restructurings, and court-ordered audits, 10m Sentinel-1 data lacks the resolution to count combine harvesters, identify grain trucks, or inspect storage silos. Agrostech specifies a modular Commercial Tasking Adapter.

#### 2.1 Multi-Provider Adapter Specification
The adapter abstracts two primary providers:
1. **Umbra Space (Canopy API):** Sub-meter X-band SAR (0.25m to 1.0m resolution).
2. **Airbus Defence and Space (TerraSAR-X / TanDEM-X):** Staring Spotlight (0.25m), High Resolution Spotlight (1.0m), and Stripmap (3.0m).

#### 2.2 Tasking Parameter Validation Schema (Zod / JSON Schema)

```typescript
import { z } from "zod";

export const GeoJsonPolygonSchema = z.object({
  type: z.literal("Polygon"),
  coordinates: z.array(z.array(z.tuple([z.number(), z.number()]))).refine(
    (rings) => {
      // Must have at least 4 coordinates (closed ring)
      return rings[0] && rings[0].length >= 4;
    },
    { message: "Polygon exterior ring must have at least 4 coordinates and be closed." }
  ),
});

export const CommercialTaskingRequestSchema = z.object({
  provider: z.enum(["umbra", "terrasar_x"]),
  farm_id: z.string().uuid(),
  car_code: z.string().min(10),
  geometry: GeoJsonPolygonSchema,
  resolution_mode: z.enum([
    "SPOTLIGHT_0_25M", // Umbra 25cm / TerraSAR-X Staring Spotlight
    "SPOTLIGHT_0_50M", // Umbra 50cm
    "SPOTLIGHT_1_00M", // Umbra 1m / TerraSAR-X High Resolution Spotlight
    "STRIPMAP_3_00M",  // TerraSAR-X Standard Stripmap
  ]),
  polarization: z.enum([
    "HH",
    "VV",
    "DUAL_HH_HV",
    "DUAL_VV_VH",
  ]),
  acquisition_window: z.object({
    start_datetime: z.string().datetime(),
    end_datetime: z.string().datetime(),
  }).refine(
    (data) => new Date(data.end_datetime) > new Date(data.start_datetime),
    { message: "end_datetime must be strictly after start_datetime." }
  ),
  geometric_constraints: z.object({
    min_grazing_angle_deg: z.number().min(15).max(75).default(40),
    max_grazing_angle_deg: z.number().min(20).max(85).default(70),
    pass_direction: z.enum(["ASCENDING", "DESCENDING", "ANY"]).default("ANY"),
  }),
  priority: z.enum(["STANDARD", "RUSH", "EMERGENCY_JUDICIAL"]).default("STANDARD"),
});

export type CommercialTaskingRequest = z.infer<typeof CommercialTaskingRequestSchema>;
```

#### 2.3 Tasking Order Lifecycle State Machine
```
[DRAFT]
   |  (submitTaskingRequest)
   v
[FEASIBILITY_REQUESTED] ---> [INFEASIBLE / REJECTED]
   |  (orbital pass matched)
   v
[SCHEDULED]
   |  (satellite execution)
   v
[ACQUIRING]
   |  (downlink & radiometric correction)
   v
[PROCESSING_L2_RTC]
   |  (delivery to Cloud Storage bucket)
   v
[COMPLETED] ---> [DELIVERED_TO_DOSSIER]
```

---

## Deep Dive 2: Requirement R3 — Risk Console & Regulatory Compliance

### 1. Central Bank BCB Resolução CMN nº 5.267/2025 & MCR 2-9

#### 1.1 Regulatory Mandate Analysis
- **Resolution:** Resolução CMN nº 5.267, issued November 28, 2025.
- **Effective Date:** March 1, 2026.
- **Regulatory Framework:** Alters the *Manual de Crédito Rural (MCR)* Chapter 2 (Condições Básicas), Section 7 (Monitoramento e Fiscalização), and enforces Section 9 (Impedimentos Sociais, Ambientais e Climáticos).
- **Core Mandates:**
  1. **Mandatory Remote Sensing for Large Operations:** Operations with total financed area $> 300 \text{ ha}$ (custeio and investimento) MUST be monitored via continuous remote sensing (satellite / radar).
  2. **Continuous Monitoring:** Shift from point-in-time sporadic inspections to full-cycle temporal tracking throughout the contract lifecycle.
  3. **Direct Bank Responsibility:** Financial institutions must maintain auditable, verifiable digital logs for BACEN inspection.
  4. **Key Verification Checklist:**
     - Correct application of funds inside the georeferenced polygon (SICOR compliance).
     - Crop type identification and phenological verification (preventing credit diverted to other crops).
     - Environmental compliance and zero-overlap with IBAMA embargos, Conservation Units (UC), Indigenous Lands (TI), and Unallocated Public Forests (Florestas Públicas Tipo B).
     - Prevention of double-financing (duplicidade de crédito) across distinct institutions.

#### 1.2 MCR 2-9 Automated Compliance Checks

```typescript
export interface Mcr29ComplianceResult {
  evaluation_timestamp: string;
  car_code: string;
  total_area_ha: number;
  mandatory_remote_sensing: boolean; // true if total_area_ha > 300
  checks: {
    sicar_status: {
      status: "Ativo" | "Pendente" | "Suspenso" | "Cancelado";
      passed: boolean; // only Ativo or Pendente allowed
      rule: "MCR 2-9-1 (Inscrição Válida no CAR)";
    };
    ibama_embargo: {
      has_overlap: boolean;
      embargo_count: number;
      overlap_area_ha: number;
      passed: boolean; // must be false
      rule: "MCR 2-9-2 (Vedação a Áreas Embargadas pelo IBAMA)";
      records: Array<{
        process_num: string;
        infraction_term: string;
        date: string;
      }>;
    };
    indigenous_land_overlap: {
      has_overlap: boolean;
      passed: boolean;
      rule: "MCR 2-9-3 (Sobreposição com Terras Indígenas)";
    };
    conservation_unit_overlap: {
      has_overlap: boolean;
      passed: boolean;
      rule: "MCR 2-9-4 (Unidades de Conservação de Proteção Integral)";
    };
    public_forest_type_b: {
      has_overlap: boolean;
      passed: boolean;
      rule: "MCR 2-9-5 (Vedação em Florestas Públicas Tipo B Não Destinadas)";
    };
    slave_labor_list: {
      listed: boolean;
      passed: boolean;
      rule: "MCR 2-9-6 (Cadastro de Empregadores - Trabalho Análogo à Escravidão)";
    };
  };
  final_verdict: "CONFORME" | "IMPEDIDO" | "PENDENTE_REGULARIZACAO";
  passaporte_credito_rural_eligible: boolean;
}
```

---

### 2. Audit-Grade ICP-Brasil Digital Signature Architecture

To serve as valid forensic evidence in Brazilian courts (Plantão Judiciário, Varas Empresariais e de Falência), credit dossiers must satisfy the technical requirements of the **ICP-Brasil (Infraestrutura de Chaves Públicas Brasileira)**.

#### 2.1 Cryptographic Profile & Standards
- **Standard:** PAdES-LTV (PDF Advanced Electronic Signature - Long Term Validation) conforming to DOC-ICP-15 and ETSI EN 319 142.
- **Hash Algorithm:** SHA-256 (Secure Hash Algorithm 256 bits).
- **Signature Algorithm:** RSA-2048 or RSA-4096 / ECDSA NIST P-256.
- **Time-Stamp Protocol:** RFC 3161 (Time-Stamp Protocol - TSP) via an authorized Time-Stamping Authority (Autoridade de Carimbo do Tempo - ACT) accredited by ITI.
- **Legal Force:** Medida Provisória nº 2.200-2/2001 and Lei nº 14.063/2020 (Assinatura Eletrônica Qualificada).

#### 2.2 Metadata Data Structure for PDF Dossier

```typescript
export interface IcpBrasilDossierSignatureMetadata {
  dossier_id: string; // UUID v4
  document_hash_sha256: string; // 64 hex characters
  signing_time_utc: string; // ISO-8601
  icp_brasil: {
    act_name: string; // e.g. "Autoridade de Carimbo do Tempo SERPRO"
    certificate_serial_number: string;
    certificate_cn: string; // e.g. "AGROSTECH PERICIAS DIGITAIS LTDA:12345678000199"
    certificate_issuer: string; // e.g. "AC SERPRO Brasil v5"
    policy_oid: "2.16.76.1.7.1" | "2.16.76.1.7.2"; // DOC-ICP-15 Signature Policy
    timestamp_token_der_b64: string; // RFC 3161 TimeStampResp in Base64
  };
  audited_entities: {
    farm_name: string;
    car_code: string;
    matricula: string;
    cpr_code?: string;
  };
  peritagem_summary: {
    sar_baseline_verified: boolean;
    sentinel1_orbit_reference: string;
    biomass_collapse_timestamp?: string;
    mcr_2_9_status: "CONFORME" | "IMPEDIDO";
  };
}
```

---

### 3. Shield-RJ Fraud Vectors & Forensics

The Shield-RJ module protects creditors and barter desks from pre-planned judicial recovery fraud (*golpe da recuperação judicial*).

#### 3.1 Four Primary Credit Fraud Vectors

```
+-----------------------------------------------------------------------------------+
|                            SHIELD-RJ FRAUD VECTORS                                |
+-----------------------------------------------------------------------------------+
| 1. ÁREA INFLADA (CAR vs M1)       | 2. SAFRA FANTASMA (Unverified Harvest)        |
| - CAR bruto declarado: 1.000 ha   | - Financiamento captado para 50.000 sacas     |
| - APP + Reserva Legal: 450 ha     | - SAR não detecta ciclo fenológico ou colapso |
| - Área Útil Líquida M1: 550 ha    | - Ausência de insumos / lavoura fantasma      |
| - Desvio: Alavancagem artificial  | - Desvio de recurso para outras atividades    |
+-----------------------------------+-----------------------------------------------+
| 3. FUGA DE SAFRA (Grain Diversion)| 4. BLINDAGEM PRÉ-RJ (Legal Restructuring)     |
| - Colheita noturna provada no SAR | - Arrendamento de gaveta para esposa/filho    |
| - Queda de VH: -22,1 dB (colheita)| - Abertura de nova Inscrição Estadual (IE)    |
| - Grão escoado por intermediário  | - Surto de protestos no CENPROT               |
| - Fraude ao Penhor Agrícola (CPR) | - Pedido iminente de Recuperação Judicial     |
+-----------------------------------+-----------------------------------------------+
```

#### 3.2 Straw Person (*Laranja*) Probability Model ($S_{\text{straw}}$)
The platform calculates a composite straw person score ($S_{\text{straw}} \in [0, 1]$):
$$S_{\text{straw}} = w_1 \cdot f_{\text{kinship}} + w_2 \cdot f_{\text{ie\_age}} + w_3 \cdot f_{\text{machinery}} + w_4 \cdot f_{\text{mdf\_triangulation}}$$

- $f_{\text{kinship}}$: 1.0 for spouse (comunhão parcial/universal) or 1st-degree descendant; 0.6 for 2nd-degree relative.
- $f_{\text{ie\_age}}$: 1.0 if IE opened $< 30$ days before harvest; 0.5 if $< 90$ days; 0.0 if $> 365$ days.
- $f_{\text{machinery}}$: 1.0 if zero agricultural equipment registered in Renavam/SIGEF; 0.0 if fleet commensurate with acreage.
- $f_{\text{mdf\_triangulation}}$: 1.0 if transport manifest (MDF-e) vehicles belong to the debtor while shipping invoices (NF-e) are issued by the relative.
- **Thresholds:**
  - $S_{\text{straw}} \ge 0.70$: High Risk (Orange Flag)
  - $S_{\text{straw}} \ge 0.85$: Critical Straw Fraud (Red Alert Level 5)

#### 3.3 Binding Judicial Precedent (STJ REsp 1.758.746/GO)
- **Legal Doctrine:** Harvested agricultural grains are fungible consumer/trade assets (*bens fungíveis de consumo e circulação*), NOT essential capital goods (*bens de capital essenciais à atividade*).
- **Consequence:** Fiduciary assignments of agricultural products (CPR Fiduciária / Penhor Agrícola) are **EXCLUDED from the stay period** of Judicial Recovery under Lei nº 11.101/2005 Art. 49 §3º.
- **Strike Action:** Creditor can immediately file an *inaudita altera parte* precautionary seizure (*Tutela Cautelar Antecedente de Busca e Apreensão*) under CPC Arts. 300 and 301 before grain commingling (*comistão*) in warehouse silos occurs.

---

### 4. Real-Time ScoreCard Indicators

The ScoreCard component renders six primary institutional indicators:
1. **Status Geral:** `VERIFICADO` (Green), `ALERTA` (Amber), `BLOQUEADO` (Red).
2. **Rating Socioambiental (ESG):** Calculated 0–100 score based on legal reserve preservation, water basin protection, and zero infractions.
3. **Nível de Risco de Crédito Rural:** `BAIXO` ($> 80$), `MÉDIO` ($50–80$), `ALTO` ($30–50$), `CRÍTICO` ($< 30$).
4. **Cadastro SICAR:** Status (`Ativo`, `Pendente`, `Cancelado`), overlap detection, and registration verification.
5. **Certificação SIGEF/INCRA:** Land tenure certainty, INCRA boundary certification code, technical responsibility (CREA/ART).
6. **Passaporte de Crédito Rural:** Binary qualification flag verifying zero environmental embargos, zero indigenous overlaps, and verified plantable area.

---

### 5. Geospatial Visualizer Specifications (2D & 3D)

#### 5.1 2D Visualizer (MapLibre GL + Deck.gl)
- **Base Map Toggle:**
  - `satellite`: Esri World Imagery high-resolution raster tiles (`https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`).
  - `mapbiomas`: CartoDB Dark Matter background with MapBiomas Brasil Coleção 9.0 WMS GetMap overlays (`https://geoserver.mapbiomas.org/geoserver/wms`).
- **Vector Overlays (Deck.gl Layers):**
  - `Polígono Cadastrado (Gleba)`: `GeoJsonLayer`, stroke `#00e676` (Radar Emerald, 3–4px), fill `rgba(0, 230, 118, 0.15)`.
  - `APP Hídrica (Rio Urucuia)`: `GeoJsonLayer` fill `rgba(0, 229, 255, 0.30)` + `PathLayer` dashed stroke `#00e5ff` (Water Cyan, `[8, 4]` dash array).
  - `Reserva Legal Cerrado`: `GeoJsonLayer` fill `rgba(21, 128, 61, 0.35)` + `PathLayer` dotted stroke `#15803d` (Deep Forest Green, `[2, 3]` dot array).
  - `Embargos IBAMA`: `GeoJsonLayer` stroke `#ef4444` (Hazard Red, 4px), fill `rgba(239, 68, 68, 0.40)`.
  - `SAR Backscatter Heatmap / TileLayer`: Raster overlay rendering $\gamma^0_{VH}$ backscatter grid with color ramp ($-25 \text{ dB}$ bare soil red to $-10 \text{ dB}$ dense canopy green).

#### 5.2 3D Visualizer (CesiumJS)
- **Engine:** CesiumJS 1.127+
- **Terrain Provider:** `Cesium.Terrain.fromWorldTerrain({ requestWaterMask: true, requestVertexNormals: true })`.
- **Polygon Extrusion:** Parcel boundary extruded 80m–150m above ground with glowing neon outline:
  - Material: `Cesium.Color.fromCssColorString("#c2ff00").withAlpha(0.25)`
  - Outline Color: `Cesium.Color.fromCssColorString("#c2ff00")`
  - Outline Width: 3px
- **Model Asset Pipeline:**
  - `model_type: "3dtiles"`: Streamed via `Cesium.Cesium3DTileset.fromUrl()`.
  - `model_type: "glb"`: Loaded via `viewer.entities.add({ model: { uri } })`.
- **Camera Modes:**
  - `drone`: Centered at parcel, altitude 350m–800m, pitch $-35^\circ$, tracking altitude changes in real time.
  - `nadir`: Perpendicular top-down inspection, pitch $-90^\circ$.
  - `orbit`: Continuous 360-degree rotation around parcel centroid at constant velocity.

---

## Implementation Blueprint

### 1. New TypeScript Types Required (`src/types/sar.ts`)
```typescript
export interface StacAssetLink {
  href: string;
  type: string;
  roles: string[];
}

export interface Sentinel1RtcItem {
  id: string;
  collection: "sentinel-1-rtc-1";
  bbox: [number, number, number, number];
  properties: {
    datetime: string;
    operational_mode: "IW" | "EW";
    polarisation_channels: "VV&VH" | "HH&HV";
    orbit_direction: "ASCENDING" | "DESCENDING";
    relative_orbit: number;
    rtc_radiometry: "gamma0";
  };
  assets: {
    Gamma0_VH: StacAssetLink;
    Gamma0_VV: StacAssetLink;
    layover_shadow_mask?: StacAssetLink;
    local_incidence_angle?: StacAssetLink;
    thumbnail?: StacAssetLink;
  };
}

export interface TemporalBackscatterPoint {
  date: string;
  vh_db: number;
  vv_db: number;
  vh_vv_ratio_db: number;
  is_harvest_event: boolean;
}

export interface HarvestDetectionAlert {
  farm_id: string;
  car_code: string;
  alert_level: 1 | 2 | 3 | 4 | 5;
  detected_at: string;
  pre_harvest_vh_db: number;
  post_harvest_vh_db: number;
  delta_db: number;
  straw_person_probability: number;
  recommended_action: string;
}
```

### 2. New Backend Services & APIs to Implement
1. `src/lib/sar/inpeStacClient.ts`: Client for querying `https://data.inpe.br/bdc/stac/v1`.
2. `src/lib/sar/harvestEngine.ts`: Algorithm calculating $\gamma^0_{VH}$ drops and issuing M2 alerts.
3. `src/lib/sar/commercialAdapter.ts`: Modular tasking validator for Umbra and TerraSAR-X.
4. `src/lib/compliance/mcr29Engine.ts`: BCB Resolução CMN 5.267 / MCR 2-9 validator.
5. `src/lib/compliance/icpBrasilDossier.ts`: PDF generator with PAdES-LTV metadata and RFC 3161 timestamping structure.
6. `src/app/api/sar/baseline/route.ts`: API route returning Sentinel-1 RTC temporal curves for a parcel.
7. `src/app/api/sar/tasking/route.ts`: API route for commercial SAR tasking feasibility and orders.
8. `src/app/api/compliance/mcr29/route.ts`: API route generating compliance dossiers.

---
*End of Specification Report.*
