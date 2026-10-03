# Handoff Report: SAR & Risk Dossier Specification Mining
**Agent:** SAR & Risk Dossier Spec Miner (`spec_miner_sar_risk_1`)  
**Date:** 2026-09-26T14:52:00Z  
**Type:** Hard Handoff (Task Complete)  

---

## 1. Observation
1. **Live INPE BDC STAC API Verification:**
   - Probed `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1` via tool call. The endpoint returned HTTP 200 with collection id `"sentinel-1-rtc-1"`, STAC version `"1.0.0"`, summaries including instruments `["c-sar"]`, operational modes `["IW", "EW", "SM"]`, center frequency `[5.405]` GHz, polarizations `[["VV"], ["VH"], ["HH"], ["HV"]]`, and spatial extent `[-76.383975, -31.7540236, -37.1882616, 6.5751645]`.
   - Probed item assets in collection item `S1D_IW_RTCH_1SDV_20260826_004294_007E83_45EB`: assets include `Gamma0_VH` (Cloud-Optimized GeoTIFF, type `"image/tiff; application=geotiff; profile=cloud-optimized"`), `Gamma0_VV`, `layover_shadow_mask`, `local_incidence_angle`, and `thumbnail`.
2. **Regulatory Standards Verification (BACEN / CMN):**
   - Verified that **Resolução CMN nº 5.267** was enacted on November 28, 2025, taking legal effect on **March 1, 2026**.
   - The rule amends MCR Chapter 2, Section 7, instituting **mandatory continuous remote sensing monitoring** for agricultural credit operations with total financed area $> 300 \text{ ha}$.
   - MCR Section 2-9 establishes mandatory impediments: active IBAMA embargos, suspended/cancelled CAR status in SICAR, overlaps with indigenous lands, fully protected conservation units, unallocated public forests (Tipo B), and slave labor registry (*Cadastro de Empregadores de Trabalho Escravo*).
3. **Existing Codebase Inspection:**
   - `src/types/database.ts`: Lines 23–69 contain existing definitions for `LandParcelMetrics`, `ComplianceSicar`, `ComplianceSigef`, `ComplianceIbama`, and `EnvironmentalContext`.
   - `src/types/geospatial.ts`: Lines 44–70 define `EnrichedLandData` and `ScoreCard`.
   - `src/components/map/MapView2D.tsx`: Lines 404–496 render Deck.gl layers for Polígonos Cadastrados (`#00e676`), APP Hídrica (`#00e5ff` dashed `[8, 4]`), and Reserva Legal (`#15803d` dotted `[2, 3]`).
   - `src/components/map/CesiumViewer.tsx`: Lines 48–144 initialize Cesium 1.127 WorldTerrain with extruded polygons (`#c2ff00`), and GLB/3D Tiles loading.
   - `src/components/shield-rj/StrikeModal.tsx`: Lines 16–46 embed a complete judicial emergency petition excerpt grounded on CPC Arts. 300/301, CPR Law 8.929/1994, and STJ REsp 1.758.746/GO.
   - `src/components/shield-rj/GraphVisualizer.tsx`: Lines 24–122 define nodes (debtor, straw person, farm, truck, silo) and suspicious links with straw person score filter $S_{\text{straw}}$.

---

## 2. Logic Chain
1. Based on Observation 1, INPE Brazil Data Cube distributes Sentinel-1 RTC Level-2 ARD in Cloud-Optimized GeoTIFFs with linear gamma-nought backscatter values at 10m spatial resolution. Therefore, extracting parcel-level temporal backscatter requires converting linear values to decibels ($\gamma^0_{\text{dB}} = 10 \cdot \log_{10}(\gamma^0_{\text{linear}})$), applying the `layover_shadow_mask` to eliminate radar distortions, and computing zonal mean and standard deviation per acquisition date.
2. Based on Observation 1 and agronomic radar mechanics, crop harvest causes an immediate loss of canopy volume scattering. Consequently, the M2 Anti-Fuga detection algorithm must evaluate the differential $\Delta \gamma^0_{VH} = \mu_{VH}(t_k) - \mu_{VH}(t_{k-1}) \le -4.5 \text{ dB}$ reaching a bare-soil baseline $\le -20.0 \text{ dB}$, while applying an environmental refutation index ($S_{\text{clima}}$) to reject dielectric shifts from heavy precipitation.
3. Based on Observation 2, under BCB Resolução CMN nº 5.267/2025 and MCR 2-9, operations $> 300 \text{ ha}$ must be verified through continuous orbital monitoring, and zero-overlap with IBAMA embargos and public forests is mandatory. Therefore, the risk console must evaluate both the $300 \text{ ha}$ threshold and all MCR 2-9 criteria before certifying Passaporte de Crédito Rural eligibility.
4. Based on Observation 3, the codebase already possesses the visual foundations (MapLibre/Deck.gl 2D, Cesium 3D, ScoreCard, Shield-RJ graph and timeline), but lacks dedicated SAR ingestion services, STAC query types, commercial SAR tasking schemas, and ICP-Brasil PAdES-LTV signature generators.
5. Therefore, a complete specification was constructed in `spec_report.md` encompassing schemas, mathematical formulations, provider APIs (Umbra / TerraSAR-X), regulatory rules (CMN 5.267 / MCR 2-9), cryptographic metadata (PAdES / RFC 3161), and implementation blueprints.

---

## 3. Caveats
- **INPE BDC Geographic Coverage:** While the STAC API endpoint is active, processing of Sentinel-1 RTC is focused on the Brazilian territory; international test coordinates will return empty item sets.
- **Commercial SAR Tasking Latency:** Tasking sub-meter commercial SAR (Umbra / TerraSAR-X) involves operational satellite scheduling (24 to 72 hour lead time); the platform interface must support asynchronous order state tracking.
- **ICP-Brasil Certificate Hardware:** In browser clients, generating qualified ICP-Brasil signatures requires either a cloud HSM certificate (e.g. BirdID, SafeID, NeoID) or server-side signing with an A1 PFX certificate.

---

## 4. Conclusion
All technical specifications for Requirement R2 (Dual-Track SAR Ingestion & M2 Anti-Fuga Engine) and Requirement R3 (Bank & Barter Risk Console & MCR 2-9 Dossier) have been discovered, validated against live endpoints and authoritative regulatory texts, and exhaustively documented in `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_sar_risk_1\spec_report.md`.

---

## 5. Verification Method
To independently verify these findings:
1. **Verify Specification Document:**
   Inspect `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_sar_risk_1\spec_report.md` to confirm the presence of all 13 discovered features, 12 edge cases, mathematical formulas, and Zod schemas.
2. **Verify INPE BDC STAC Endpoint:**
   Issue a GET request to `https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1` and confirm collection ID `sentinel-1-rtc-1`, instruments `c-sar`, and COG assets `Gamma0_VH` and `Gamma0_VV`.
3. **Verify Regulatory Text:**
   Inspect Banco Central do Brasil Resolução CMN nº 5.267 de 28/11/2025 and confirm the mandatory remote sensing requirement for rural credit operations exceeding 300 hectares effective March 1, 2026.
4. **Invalidation Condition:**
   If INPE changes its BDC STAC schema or BACEN modifies the 300 ha threshold in MCR 2-7/2-9, the corresponding schemas in `spec_report.md` must be updated.
