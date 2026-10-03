# API Reference

All routes are Next.js Route Handlers under `src/app/api/`. They accept and return JSON (UTF-8) unless noted. There is no versioning yet: add a `/api/v1` prefix before the first external integration.

## Authentication

Every `/api/*` request passes through `src/middleware.ts`, which returns **401** unless one of these is true:

- there is a valid Supabase session cookie (`supabase.auth.getUser()` succeeds), or
- `NEXT_PUBLIC_DEMO_MODE=true` **and** the `agrostech_demo_role` cookie is present.

Five of the six handlers call `checkApiAuth()` again (defence in depth). `/api/land/enrich` does not (KI-05). No route checks the user's **role** yet.

Common error envelope:

```json
{ "success": false, "error": "human-readable message (pt-BR or en)", "code": "OPTIONAL_DIAGNOSTIC_CODE" }
```

---

## `POST /api/land/enrich`

Turns a CAR code (and an optional uploaded boundary) into an enriched parcel with M1 metrics and a ScoreCard.

**Request**

```json
{
  "car_code": "MG-3109300-4829A0D7314B4A45A7C49102B94C7192",
  "matricula_code": "optional",
  "name": "optional display name",
  "geojson": { "type": "Feature", "geometry": { "type": "Polygon", "coordinates": [[[lon, lat], ...]] } }
}
```

- `car_code` must match the federal format `UF-0000000-<32 hex>`. When it is omitted, the route uses the Buritis demo CAR.
- `geojson` may be a `Feature` or a `FeatureCollection` (the first feature is used).

**Response 200**

```json
{
  "success": true,
  "source": "live | fixture",
  "data": { "...EnrichedLandData (src/types/geospatial.ts)": "", "source": "live | fixture" },
  "steps": [ { "id": "sicar-layer", "layer": "SICAR", "status": "success", "detail": "…", "duration_ms": 12 } ],
  "elapsed_ms": 140
}
```

`data` includes:
- `metrics`: `total_area_ha`, `app_area_ha`, `legal_reserve_area_ha`, and `consolidated_area_ha` (= M1 net plantable area)
- `compliance_sicar`, `compliance_sigef`, `compliance_ibama`, `environmental_context`
- `scorecard`: `overall_status`, `score_esg`, `risk_level`, `credit_passport_eligible`, `recommendations`
- `layers`: GeoJSON for APP, Reserva Legal and embargoes

⚠️ Several fields are hardcoded or random today (KI-03).

**Errors.** `RegistroRuralError` is mapped to its HTTP status:

| `code` | HTTP | Meaning |
|---|---|---|
| `INVALID_CAR_FORMAT` | 400 | Malformed CAR |
| `CONFIG_MISSING_API_KEY` | 500 | No key in strict mode |
| `AUTH_UNAUTHORIZED` | 401 | Gateway rejected the key |
| `BILLING_INSUFFICIENT_CREDITS` | 402 | Gateway wallet empty |
| `CAR_NOT_FOUND` | 404 | Unknown CAR |
| `RATE_LIMITED` | 429 | Gateway throttling |
| `SICAR_POLLING_TIMEOUT` | 504 | Demonstrativo never reached `COMPLETE` |
| `NETWORK_ERROR` | upstream status | Any other non-2xx from the gateway |

Any other error returns 500. The source of truth is the factory methods in `src/lib/registrorural/errors.ts`.

---

## `POST /api/land/save`

Persists an enriched parcel to `land_parcels`.

**Request:** `{ "enriched": EnrichedLandData, "owner_id"?: uuid, "org_id"?: uuid }`

**Response 200:** `{ "success": true, "parcel": {…}, "message": "…" }`

**Errors:**
- 400 when `enriched` is missing.
- 500 when the database rejects the insert (with a real database it always does today, KI-06).

---

## `POST /api/sar/temporal`

Searches Sentinel-1 RTC acquisitions for a parcel and returns a backscatter time series.

**Request**

```json
{
  "car_code": "optional; unknown codes fall back to the Buritis polygon",
  "geojson": "optional Feature | Polygon | FeatureCollection",
  "dateRange": { "start": "2025-11-01T00:00:00Z", "end": "2026-04-15T23:59:59Z" }
}
```

At least one of `car_code` / `geojson` is required (otherwise 400). `dateRange` defaults to the 2025/26 soybean season shown above.

**Response 200**

```json
{
  "success": true,
  "data": {
    "car_code": "…", "bbox": [minLon, minLat, maxLon, maxLat],
    "dateRange": { "start": "…", "end": "…" },
    "acquisitionsCount": 12, "itemsCount": 12,
    "curve": [ { "date": "2026-01-10", "gamma0_vv_db": -9.5, "gamma0_vh_db": -14.5, "vh_vv_ratio_db": -5.0, "pixelCount": 21712 } ],
    "summary": { "latestDate": "…", "latestVhDb": -21.0, "latestVvDb": -12.0, "latestRatioDb": -9.0,
                 "trend": "HARVEST_COLLAPSE | BARE_SOIL | SENESCENCE | PEAK_BIOMASS | VEGETATIVE_GROWTH | STABLE" }
  }
}
```

⚠️ On live STAC items the curve values are constants (KI-02).

---

## `POST /api/sar/harvest-check`

Runs the M2 Anti-Fuga engine.

**Request**

```json
{
  "temporalPoints": [ { "date": "…", "gamma0_vv_db": -9.1, "gamma0_vh_db": -15.9, "vh_vv_ratio_db": -6.8, "pixelCount": 1000 } ],
  "car_code": "alternative to temporalPoints",
  "geojson": "alternative to temporalPoints",
  "thresholdDb": -4.5,
  "bareSoilFloorDb": -20.0,
  "precipitationMm48h": 4.2,
  "unregisteredDiversionSuspected": false
}
```

If `temporalPoints` is missing, the route builds them itself from STAC. It uses a **fixed Buritis bbox** and the **2025-11-01 → 2026-04-15** window, whatever geometry is sent (KI-25).

**Response 200:** `{ "success": true, "data": { "harvestDetected", "harvestDate", "dropMagnitudeDb", "confidence", "bareSoilReached", "alertLevel" (1–5), "climateRefutation": { "rainArtifactRefuted", "sClimaIndex", "precipitationMm48h", "explanation" }, "recommendations", "evaluatedPointsCount", "evaluatedPeriod" } }`

| `alertLevel` | Meaning |
|---|---|
| 1 | Normal vegetative monitoring |
| 2 | Senescence (max drop ≥ 1.2 dB) |
| 3 | Desiccation / harvest imminent (max drop ≥ 2.5 dB) |
| 4 | Harvest detected (ΔγVH ≤ threshold **and** γVH ≤ bare-soil floor, not refuted by rain) |
| 5 | Harvest detected **and** `unregisteredDiversionSuspected=true` (UI label "Fuga") |

---

## `POST /api/sar/commercial/task` · `GET /api/sar/commercial/task`

Commercial sub-metre SAR tasking (Umbra Canopy, Airbus TerraSAR-X). **Specification only:** orders are validated and kept in memory, and nothing is sent to the providers (KI-08).

**Create (POST, 201).** The body is validated by `CommercialTaskingRequestSchema` (`src/lib/sar/commercial/schema.ts`), which accepts camelCase or snake_case:

```json
{
  "provider": "umbra | terrasar_x",
  "carCode": "MG-…", "farmId": "optional",
  "geometry": { "type": "Polygon", "coordinates": [[[lon, lat], …, [lon, lat]]] },
  "resolutionMode": "SPOTLIGHT_0_25M | SPOTLIGHT_0_50M | SPOTLIGHT_1_00M | STRIPMAP_3_00M",
  "polarization": "HH | VV | DUAL_HH_HV | DUAL_VV_VH",
  "acquisitionWindow": { "startDatetime": "ISO-8601", "endDatetime": "ISO-8601" },
  "priority": "STANDARD | RUSH | EMERGENCY_JUDICIAL",
  "geometricConstraints": { "…": "optional" },
  "notes": "optional, ≤ 1000 chars"
}
```

The schema also enforces provider rules:
- Umbra has no Stripmap mode.
- TerraSAR-X has no 0.50 m mode.
- The Spotlight footprint must be ≤ 25 km² (this check currently fails: KI-17).
- The window must be valid, and the Umbra adapter rejects windows shorter than 12 h.

A validation failure returns 400 with `validationErrors: [{ field, message, code }]`.

**Transition (POST):** `{ "action": "transition", "orderId": "…", "targetStatus": "FEASIBILITY_REQUESTED | SCHEDULED | ACQUIRING | PROCESSING_L2_RTC | COMPLETED | REJECTED | CANCELLED", "comment": "optional" }` → `{ success, order }`. Unknown order → 404.

**Read (GET):** `?orderId=…` → one order. Or `?provider=…&status=…` → `{ ordersCount, orders }`.

---

## `POST /api/dossier/generate[?format=pdf]`

Generates the MCR 2-9 compliance dossier.

**Request** (camelCase or snake_case):

```json
{
  "carCode": "required",
  "grossAreaHa": 217.12,
  "appAreaHa": 26.91, "legalReserveAreaHa": 43.42, "rlInAppAreaHa": 0,
  "easementsHa": 0, "restrictedUseHa": 0, "netPlantableAreaHa": 146.79,
  "farmName": "…", "municipality": "…", "stateUf": "MG", "matricula": "…",
  "cprCode": "…", "creditorName": "…", "debtorName": "…",
  "sicarStatus": "Ativo", "embargoCount": 0, "embargoesHa": 0,
  "hasIndigenousOverlap": false, "hasConservationUnitOverlap": false, "hasSlaveLabor": false,
  "sarSeriesPoints": 6, "sarHarvestDetected": false, "sarHarvestDate": "…", "sarBaselineVerified": true,
  "caAuthority": "SERPRO | CAIXA_JUS",
  "format": "json | pdf"
}
```

Missing optional fields default to **Buritis demo values** (`farmName`, `municipality`, `matricula`, `grossAreaHa`). In production you must send every field explicitly.

**Response.**
- JSON: `{ success, data: Mcr29DossierReport }` (`src/lib/dossier/types.ts`).
- PDF: `application/pdf` attachment `dossie_mcr29_<car>.pdf`, with headers `X-Dossier-SHA256` and `X-MCR29-Status`.

⚠️ The signature metadata is a placeholder (KI-01).

**Errors:**
- 400 for a missing `carCode`, a non-positive `grossAreaHa` or invalid JSON.
- 500 otherwise.
