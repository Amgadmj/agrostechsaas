# 0005. Dual-track SAR: free Sentinel-1 baseline, commercial tasking on anomaly

- **Status:** Accepted (retroactive)
- **Date:** 2026-10-03

## Context

Three constraints shape the satellite design:

- Monitoring every financed hectare must cost almost nothing, or per-hectare SaaS pricing fails.
- Disputes such as judicial recovery or suspected grain diversion need sub-metre evidence.
- Optical imagery fails under harvest-season cloud.

## Decision

1. **Baseline track:** Sentinel-1 RTC γ⁰ VV/VH at 10 m, from the INPE Brazil Data Cube STAC, covers 100 % of enrolled parcels and feeds Model M2.
2. **Forensic track:** commercial X-band SAR (Umbra, TerraSAR-X) is tasked only when an anomaly is confirmed. It sits behind a provider-agnostic adapter in `src/lib/sar/commercial`.
3. **Drone flight:** the last tier ("drone só na anomalia").

## Consequences

- We need a **raster processing service** for zonal statistics, which is not built yet (KI-02). It should live outside Next.js, as a worker or a Python service.
- We need persistent storage for the per-parcel time series and for tasking orders (KI-08).
- Cost scales with the number of anomalies, not with hectares.
