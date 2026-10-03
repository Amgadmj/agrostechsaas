# Model M2: Radar SAR "Anti-Fuga" Harvest Engine

**Code:**
- `src/lib/sar/bdcStacClient.ts`: STAC search
- `src/lib/sar/temporalEngine.ts`: dB math and curves
- `src/lib/sar/harvestEngine.ts`: detection
- `src/lib/sar/commercial/*`: high-resolution tasking

**Types:** `src/types/sar.ts`
**Tests:** tier-1 F6–F9, tier 2–4, and `tests/adversarial/sar_stress.harness.ts`

## Why it exists

The soybean harvest in the main grain states (Jan–Mar) happens under persistent cloud, which blinds optical satellites. C-band SAR (Sentinel-1, ~5.6 cm wavelength) sees through cloud, day and night. A sharp fall in cross-polarised backscatter (γ⁰ VH) means the canopy volume scatterer is gone: the crop was harvested. M2 turns that physical signal into an auditable alert, so a lender learns the grain left the field before it learns of a default.

## Dual-track design ([ADR-0005](../adr/0005-dual-track-sar.md))

| Track | Source | Resolution | Cost | Status |
|---|---|---|---|---|
| **Baseline portfolio** | INPE Brazil Data Cube STAC, collection `sentinel-1-rtc-1` (Sentinel-1 RTC L2 ARD, γ⁰ VV/VH) | 10 m, 6–12 day revisit | Free | Search ✅, pixel extraction ❌ (KI-02) |
| **Forensic, on demand** | Umbra Canopy (0.25–1 m Spotlight), Airbus TerraSAR-X (0.25 m Staring Spotlight, 1 m HS, 3 m Stripmap) | Sub-metre | Paid per tasking | Validation + payload builder only (KI-08) |

## Signal processing

```
γ⁰_dB  = 10 · log10(γ⁰_linear)
CR_dB  = γ⁰_VH_dB − γ⁰_VV_dB        (cross-pol ratio)
```

Parcel statistics should average **linear** intensities and then convert to dB. Today `calculateZonalStats` averages in dB (KI-12, about −1.5 dB bias).

## Detection rule (`HarvestDetectionEngine.detectHarvestEvents`)

For consecutive acquisitions *(t₋₁, t)* sorted by date:

| Parameter | Default | Meaning |
|---|---|---|
| `thresholdDb` | **−4.5 dB** | ΔγVH = γVH(t) − γVH(t₋₁) must be ≤ this |
| `bareSoilFloorDb` | **−20.0 dB** | γVH(t) must reach bare soil |
| Persistence | −18.5 dB | The next acquisition must stay ≤ this (confidence weight) |
| `precipitationMm48h` | 4.2 mm (**default when unknown, KI-09**) | Feeds S_clima |

**Climate refutation (S_clima).** Rain raises backscatter, so a large negative drop is hard to explain by rain alone. Drying after heavy rain is the exception:

```
S_clima = clamp(1 − max(0, P48h − 35) / 50, 0.1, 1.0)
rainArtifactRefuted = S_clima ≥ 0.5          # i.e. P48h ≤ 60 mm
```

`harvestDetected = maxDrop ≥ |threshold| AND bareSoilReached AND rainArtifactRefuted`

**Confidence** (0–0.99) is a weighted sum: drop magnitude 0.35 + soil depth 0.30 + persistence 0.20 + climate 0.15.

**Alert levels:**

| Level | Rule |
|---|---|
| 1 | Normal vegetative |
| 2 | Max drop ≥ 1.2 dB (senescence) |
| 3 | Max drop ≥ 2.5 dB (desiccation, harvest imminent) |
| 4 | Harvest detected |
| 5 | Harvest detected **and** the caller flags `unregisteredDiversionSuspected` |

The UI calls level 5 "Fuga". Per the audit, copy must say *"compatível com"* or *"indica"*. SAR cannot prove the time of day or intent.

## Known weaknesses

From `npm run test:adversarial`; details in [`KNOWN_ISSUES.md`](../05-quality/KNOWN_ISSUES.md):

- **KI-11:** float rounding at exactly −4.5 dB.
- **KI-13:** no-till mulch stays near −19.5 dB and misses the floor.
- **KI-14:** progressive harvests spread over several passes are missed (only adjacent pairs are compared).
- **KI-15:** harvesting during heavy rain suppresses the alert (an evasion path).
- **KI-24:** sub-threshold drops reset the alert level.

## What it takes to make M2 real

1. **Zonal statistics from COGs.** Read the `Gamma0_VH` / `Gamma0_VV` assets for each STAC item, clip to the parcel (minus a buffer for edge pixels), and average in linear. Store one row per acquisition × parcel (`sar_observations`, see DATA_MODEL). This is CPU and IO heavy, so run it in a worker or service, not in a Next.js route handler.
2. **Orbit consistency.** Compare acquisitions from the same relative orbit and pass direction, or normalise for incidence angle. Mixing orbits creates false drops.
3. **Multi-temporal logic.** Use a rolling baseline or change-point detection instead of adjacent pairs (fixes KI-14). Make the bare-soil floor crop- and tillage-aware (KI-13).
4. **Weather.** Daily precipitation per parcel (INMET stations, CHIRPS or ERA5-Land). Unknown must mean "not refuted" (KI-09).
5. **Validation.** Back-test on fields with known harvest dates (the founders' drone and field operations can provide ground truth) and report precision and recall per crop and region before any client-facing claim.

## Commercial tasking (forensic track)

`commercialSarTaskingAdapter.validateAndScheduleTasking(params)` validates the request with `CommercialTaskingRequestSchema` (Zod), applies provider rules (`umbraAdapter.ts`, `terrasarxAdapter.ts`) and stores an order in `CommercialTaskingStateMachine`.

Statuses: `SUBMITTED → FEASIBILITY_REQUESTED → SCHEDULED → ACQUIRING → PROCESSING_L2_RTC → COMPLETED`, plus `REJECTED` / `CANCELLED`. The `EMERGENCY_JUDICIAL` priority exists for court-driven requests. **There are no provider API calls yet, and orders are in memory only.**
