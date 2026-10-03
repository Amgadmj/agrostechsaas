## 2026-09-26T14:53:26Z
You are Worker M2 for the Agrostech SaaS MVP platform project.
Your Working Directory: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\worker_m2_1
Project Directory: c:\Users\Razer\Desktop\Agrostech\saas
Authoritative User Request: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md
Authoritative Project Specification: c:\Users\Razer\Desktop\Agrostech\saas\PROJECT.md
Spec Miner Report: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_sar_risk_1\spec_report.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Write Ownership (Files you exclusively own):
- src/lib/sar/**
- src/app/api/sar/**

Your Mission — Milestone M2 Implementation:
1. Implement INPE Brazil Data Cube STAC Client in src/lib/sar/bdcStacClient.ts:
   - Query https://data.inpe.br/bdc/stac/v1/collections/sentinel-1-rtc-1 by bounding box (bbox: [minX, minY, maxX, maxY]) and date range (datetime: start/end).
   - Parse STAC item assets: Gamma0_VV and Gamma0_VH (10m Cloud-Optimized GeoTIFFs, C-band SAR), layover_shadow_mask, and local_incidence_angle.
   - Provide offline/cached fallback data for Fazenda Buritis/MG parcel when INPE API is unreachable or rate-limited.
2. Implement Temporal Backscatter Engine in src/lib/sar/temporalEngine.ts:
   - Linear to decibel conversion: gamma0_dB = 10 * log10(gamma0_linear).
   - Generate parcel-level temporal backscatter curves over time (VV, VH, VH/VV ratio in dB).
3. Implement All-Weather Harvest Engine (Model M2 Anti-Fuga) in src/lib/sar/harvestEngine.ts:
   - Detect biomass loss (harvest events) through persistent cloud cover:
     Delta gamma0_VH = VH(t_k) - VH(t_k-1) <= -4.5 dB reaching bare soil baseline <= -20.0 dB.
   - Refutation filter (S_clima) to reject rain/moisture artifacts.
   - Return harvestDetected, harvestDate, dropMagnitudeDb, confidence score.
4. Implement Commercial SAR Tasking Adapter in src/lib/sar/commercial/:
   - Modular adapter for sub-meter commercial SAR (Umbra Space Canopy API 0.25m-1.0m X-band spotlight; Airbus TerraSAR-X Spotlight 0.25m/HighRes 1.0m/Stripmap 3.0m).
   - Parameter validation using Zod (bbox, resolutionMode, polarization, acquisitionWindow, priority).
   - Order lifecycle state machine (SUBMITTED -> SCHEDULED -> ACQUIRING -> COMPLETED).
5. Implement Next.js API route handlers in src/app/api/sar/:
   - POST /api/sar/temporal: queries backscatter curves for a given parcel GeoJSON or CAR code.
   - POST /api/sar/harvest-check: runs M2 harvest detection engine.
   - POST /api/sar/commercial/task: validates and creates commercial SAR tasking order.
6. Verify your implementation:
   - Run type checks / tests.
   - Document commands run and verified results in your handoff.
7. Author a detailed handoff report in c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\worker_m2_1\handoff.md and send a completion message to your parent.

## 2026-09-26T15:10:47Z
Sender: parent (25db47f9-1b22-4c1b-a2ff-46c16559e080)
**Context**: Milestone M2 Completion (SAR Telemetry & M2 Harvest Engine)
**Content**: Your terminal command `Check Node.js version` is waiting for input or terminal confirmation. The implementation in `src/lib/sar/` (bdcStacClient.ts, harvestEngine.ts, temporalEngine.ts, commercial adapters) and `src/app/api/sar/` is already in place.
**Action**: Please avoid blocking on terminal commands. Finalize any remaining code or type exports, write your handoff.md report in your working directory, and send your completion report.
