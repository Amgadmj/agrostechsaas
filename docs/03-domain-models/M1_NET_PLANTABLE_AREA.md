# Model M1: Net Plantable Area (Área Útil Líquida, AUL)

**Code:** `src/lib/m1/calculator.ts` (math), `src/lib/m1/geometry.ts` (polygon area and hole-punching), `src/lib/m1/types.ts`
**Tests:** `tests/e2e/tier1/f5_model_m1.test.ts`, tier 2/3/4, and `tests/adversarial/m1_dossier_stress.harness.ts`

## Why it exists

A credit limit is roughly *area × yield × price*. Borrowers tend to declare the **gross** CAR area, but the Forest Code (Lei 12.651/2012) forbids cultivation in APP (permanent preservation areas) and Reserva Legal, and other areas are embargoed, disputed or restricted. M1 computes the area that can legally and physically back a loan.

## Formula (as implemented)

```
netConservation = max(0, APP + RL − min(RL_in_APP, min(APP, RL)))     # Art. 15 de-duplication
totalDeductions = netConservation + easements + restrictedUse + disputed + publicOverlaps + embargoes
deductiveNet    = max(0, gross − totalDeductions)

if consolidatedUseHa > 0:
    consolidatedNet = max(0, consolidatedUseHa − appRestorationHa − rlRestorationHa)
    finalNet = min(deductiveNet, consolidatedNet)
else:
    finalNet = deductiveNet

netArableRatio    = finalNet / gross
preservationRatio = netConservation / gross     # can exceed 1.0 today (KI-21)
```

Every input is clamped to ≥ 0. Areas are rounded to 0.01 ha and ratios to 4 decimals.

## Credit decision rules

| Condition | Effect |
|---|---|
| `finalNet ≤ 0` | Blocked: no plantable area |
| `embargoes > 0` | Blocked (MCR 2-9) |
| `publicOverlaps > 0` or indigenous land (TI) or conservation unit (UC) overlap | Blocked |
| CAR status `Suspenso` / `Cancelado` | Blocked |
| `0 < netArableRatio < 0.15` | Blocked: "taxa de plantabilidade crítica" |
| `gross > 300 ha` | `continuousMonitoringMandatory = true` (interpretation of CMN 5.267/2025; **to be validated by counsel**, KI-37) |

`isEligibleForCredit` is true only when there are no block reasons and `finalNet > 0`. The output also carries `creditBlockReasons[]` and `recommendations[]` (pt-BR).

## Reference case: Fazenda Buritis (MG)

| Quantity | Value |
|---|---|
| Gross (CAR) | 217,12 ha |
| APP | 26,91 ha |
| Reserva Legal | 43,42 ha |
| **Net plantable (M1)** | **146,79 ha** (67,6 %) |

These numbers anchor the demo and the tests. Every screen must stay consistent with them (rule from the UX audit).

## Geometry side

`computeNetPlantablePolygon(boundary, exclusions)` builds the net polygon by adding each exclusion as an interior ring (hole). Known limitation: overlapping exclusions become overlapping holes, with no union step (KI-20). For production, move spatial operations to PostGIS (`ST_Difference`, `ST_Union`) or a robust JS library.

## Known issues

KI-19 (the dossier re-implements this formula without the `min` bound), KI-20, KI-21 and KI-22. See [`KNOWN_ISSUES.md`](../05-quality/KNOWN_ISSUES.md).
