# Adversarial Stress Testing Report — Challenger 2
**Focus:** CAR Onboarding, Model M1 Topology/Geometry, BCB CMN 5.267 Threshold & ICP-Brasil PAdES-LTV Signatures  
**Author:** Challenger 2 (Empirical Challenger: Critic & Specialist)  
**Target Repository:** `c:\Users\Razer\Desktop\Agrostech\saas`  
**Targets Evaluated:** `src/lib/m1/`, `src/lib/dossier/`, `src/lib/spatialUtils.ts`  
**Date:** 2026-09-26  
**Formal Verdict:** **DEFECT_DETECTED**

---

## 1. Executive Summary

As Challenger 2, an independent adversarial verification was conducted against the Agrostech SaaS MVP core algorithmic engines:
1. **Model M1 Net Plantable Area (*Área Útil Líquida*) Math & Conservation Deduplication** (`src/lib/m1/calculator.ts`)
2. **Model M1 Geospatial Hole-Punching & Topology Engine** (`src/lib/m1/geometry.ts`)
3. **MCR 2-9 Compliance Dossier Generator & Continuous Monitoring Thresholds** (`src/lib/dossier/generator.ts`)
4. **ICP-Brasil PAdES-LTV Signature Structures & SHA-256 Tamper Resistance** (`src/lib/dossier/generator.ts`, `src/lib/dossier/pdfGenerator.ts`)

While the core math in `src/lib/m1/calculator.ts` demonstrates strong adherence to Law 12.651/2012 (Código Florestal) and BCB Resolução CMN nº 5.267/2025, adversarial probing revealed **2 HIGH-severity defects**, **1 MEDIUM-severity defect**, and **1 LOW-severity inconsistency** across the geometric hole-punching, dossier deduplication, and cryptographic digest boundaries.

The formal verdict is **DEFECT_DETECTED**.

---

## 2. Adversarial Challenge Matrix & Test Results

| ID | Category | Target | Stress Scenario | Expected Result | Observed Result | Severity | Status |
|---|---|---|---|---|---|---|---|
| **ADV-1.1** | Degenerate Geometry | `geometry.ts` | Bowtie self-intersecting polygon (figure-8) | Validate / reject self-intersection | Area cancels to ~0 ha; no topology validation | MEDIUM | DEFECT |
| **ADV-1.2** | Degenerate Geometry | `geometry.ts` | 4-point open coordinate ring (unclosed) | Close ring per RFC 7946 | `closeRing()` successfully closes ring | NONE | PASS |
| **ADV-1.3** | Degenerate Geometry | `geometry.ts` | Collinear vertices (zero width) | Zero area without divide-by-zero | Area is 0.0 ha; ray-casting skips division | NONE | PASS |
| **ADV-1.4** | Degenerate Geometry | `geometry.ts` | Zero-area parcel polygon | Compute net area = 0 ha | Net area = 0 ha; no crash | NONE | PASS |
| **ADV-1.5** | Degenerate Geometry | `geometry.ts` | Degenerate ring (< 3 coordinates) | Safe 0 ha return | Returns 0 ha without crash | NONE | PASS |
| **ADV-2.1** | 100% Conservation | `calculator.ts` | Exact 100% conservation (APP + RL = Gross) | Net Area = 0, Credit blocked | Net Area = 0.00 ha, Credit blocked | NONE | PASS |
| **ADV-2.2** | 100% Conservation | `calculator.ts` | Over-conservation (APP + RL > Gross: 160 ha on 100 ha) | Net Area clamped to 0 | Net Area clamped to 0.00 ha (never negative) | NONE | PASS |
| **ADV-2.3** | 100% Conservation | `calculator.ts` | Preservation ratio domain upper bound | Preservation ratio $\le 1.0$ | Preservation ratio evaluates to 1.6000 | LOW | DEFECT |
| **ADV-2.4** | 100% Conservation | `calculator.ts` | Negative numeric inputs (-500 ha) | Clamped to 0 | All negative values clamped to 0 | NONE | PASS |
| **ADV-2.5** | 100% Conservation | `calculator.ts` | Declared consolidated use on 100% conservation | Net Area forced to 0 | Net Area forced to 0 via `Math.min(deductiveNet, ...)` | NONE | PASS |
| **ADV-3.1** | Art. 15 Overlap | `calculator.ts` | Normal RL-in-APP overlap (10 ha on 20 ha APP & 20 ha RL) | Net Area = 70 ha | Net Area = 70.00 ha (deduplication sound) | NONE | PASS |
| **ADV-3.2** | Art. 15 Overlap | `calculator.ts` | Hostile inflated overlap: `rlInAppAreaHa: 50` | Bound overlap to $\min(\text{APP}, \text{RL})$ | Overlap bounded to 20 ha, Net Area = 80 ha | NONE | PASS |
| **ADV-3.3** | Art. 15 Overlap | `generator.ts` | Inflated overlap in dossier: `rlInAppAreaHa: 100` | Bound overlap to $\min(\text{APP}, \text{RL})$ | Deductions collapse to 0, Net Area jumps to 100% | HIGH | DEFECT |
| **ADV-3.4** | Art. 15 Overlap | `geometry.ts` | Spatial hole-punching with overlapping APP and RL | Planar union before hole-punch | Punches overlapping rings, double-counting holes | MEDIUM | DEFECT |
| **ADV-4.1** | BCB CMN 5.267 | `calculator.ts` | Exactly 300.00 ha gross area | `continuousMonitoringMandatory = false` | `false` | NONE | PASS |
| **ADV-4.2** | BCB CMN 5.267 | `calculator.ts` | Exactly 300.01 ha gross area | `continuousMonitoringMandatory = true` | `true` | NONE | PASS |
| **ADV-4.3** | BCB CMN 5.267 | `calculator.ts` vs `generator.ts` | Sub-centiare boundary: 300.001 ha | Consistent mandate decision | `calculator.ts` = `false`, `generator.ts` = `true` | LOW | DEFECT |
| **ADV-5.1** | ICP-Brasil / Hash | `generator.ts` | Deterministic SHA-256 generation | 64-char lowercase hex digest | Valid 64-char hex digest generated | NONE | PASS |
| **ADV-5.2** | ICP-Brasil / Hash | `generator.ts` | SHA-256 Avalanche on 0.01 ha area alteration | Extensive Hamming bit flip ($\ge 100$ bits) | Bit difference: >100 bits flipped | NONE | PASS |
| **ADV-5.3** | ICP-Brasil / Hash | `generator.ts` | Tamper resistance on `matricula` / land deed | Hash changes on `matricula` modification | Hash remains identical; `matricula` omitted from canonical digest | HIGH | DEFECT |
| **ADV-5.4** | ICP-Brasil / Hash | `generator.ts` | PAdES-LTV metadata structure | Complies with DOC-ICP-15 & RFC 3161 | Conforms to OID 2.16.76.1.7.1, ACT Serpro/Caixa | NONE | PASS |
| **ADV-5.5** | ICP-Brasil / Hash | `pdfGenerator.ts` | PDF-1.4 generation with visible hash | Valid PDF stream containing hash | Valid PDF-1.4 with embedded hash | NONE | PASS |

---

## 3. Deep-Dive Defect Analysis

### DEFECT-01 (HIGH): Unbounded RL-in-APP Deduction in `src/lib/dossier/generator.ts`
- **Location:** `src/lib/dossier/generator.ts`, Line 28:
  ```ts
  const netConservationHa = Math.max(0, appAreaHa + legalReserveAreaHa - rlInAppAreaHa);
  ```
- **Vulnerability Mechanism:**
  In `src/lib/m1/calculator.ts`, the overlap is strictly bounded to physical reality:
  ```ts
  appArea + legalReserveArea - Math.min(rlInAppOverlap, Math.min(appArea, legalReserveArea))
  ```
  However, in `src/lib/dossier/generator.ts`, line 28 does NOT bound `rlInAppAreaHa`. If a credit applicant submits an inflated `rlInAppAreaHa` (for example, 100 ha on a property with 20 ha APP and 20 ha RL), `generator.ts` computes:
  $$\text{netConservationHa} = \max(0, 20 + 20 - 100) = 0 \text{ ha}$$
  Consequently, all conservation deductions are eliminated! When `data.netPlantableAreaHa` is omitted, the dossier generates a Net Plantable Area equal to 100% of the gross property, and marks the dossier as `CONFORME` / `ELIGIBLE`.
- **Blast Radius:**
  High-risk borrowers can bypass environmental credit restrictions by deliberately reporting inflated overlap values in the dossier generation API.
- **Recommended Remediation:**
  In `src/lib/dossier/generator.ts`:
  ```ts
  const validRlInApp = Math.min(rlInAppAreaHa, Math.min(appAreaHa, legalReserveAreaHa));
  const netConservationHa = Math.max(0, appAreaHa + legalReserveAreaHa - validRlInApp);
  ```
  Or better, delegate net plantable area calculation directly to `calculateNetPlantableArea(input)` from `src/lib/m1/calculator.ts`.

---

### DEFECT-02 (HIGH): Real Estate Deed (`matricula`) and Compliance Checks Omitted from Canonical Cryptographic Hash
- **Location:** `src/lib/dossier/generator.ts`, Lines 152–166:
  ```ts
  const canonicalDocumentPayload = JSON.stringify({
    dossierId: reportId,
    carCode: data.carCode,
    grossAreaHa,
    netPlantableAreaHa,
    netArableRatio,
    preservationRatio,
    sicarStatus,
    embargoCount: data.embargoCount ?? (hasActiveEmbargo ? 1 : 0),
    mcr29Status,
    eligibilityStatus,
    regulation: "BCB Resolução CMN nº 5.267/2025 - MCR 2-9",
    issuedAt: nowUtc,
    sarBaselineVerified: !!data.sarBaselineVerified,
  });
  ```
- **Vulnerability Mechanism:**
  The canonical SHA-256 digest omits key legal anchors:
  1. `matricula` (Real Estate Registry identification number)
  2. `farmName`, `municipality`, `stateUf`
  3. Detailed `checks` (individual IBAMA, Indigenous, Slave Labor check records)
  4. The generated PDF file itself (`pdfSummaryBase64`)
  An adversary receiving an institutional signed JSON compliance dossier can alter `matricula` to associate the clean audit with an entirely different, disputed or non-owned land parcel (`MAT-99999-CRI-FRAUD`), and the SHA-256 integrity hash verification will still succeed with 100% match!
- **Blast Radius:**
  Enables collateral substitution fraud (*fraude fiduciária por troca de matrícula*) without invalidating the cryptographic checksum.
- **Recommended Remediation:**
  Include `matricula`, `farmName`, `municipality`, `stateUf`, and the PDF stream digest in `canonicalDocumentPayload`.

---

### DEFECT-03 (MEDIUM): Spatial Hole-Punching Lacks Planar Union for Overlapping Exclusions
- **Location:** `src/lib/m1/geometry.ts`, Lines 172–204:
  ```ts
  for (const feat of exclusionFeatures) {
    ...
    if (ring.length >= 3 && isRingInsideOrOverlapping(ring, exteriorRing, outerBbox)) {
      newHoles.push(ring);
    }
  }
  for (const hole of newHoles) {
    totalHoleAreaHa += calculateRingAreaHa(hole);
  }
  ```
- **Vulnerability Mechanism:**
  In GeoJSON (RFC 7946 §3.1.6), inner rings representing holes within a polygon MUST NOT intersect or overlap each other.
  When `exclusionFeatures` contains both an APP polygon and a Reserva Legal polygon that share overlapping spatial territory, `computeNetPlantablePolygon`:
  1. Appends both rings as separate holes into `coordinates: [exterior, appHole, rlHole]`, producing an invalid RFC 7946 polygon with intersecting inner rings.
  2. Sums both hole areas linearly (`totalHoleAreaHa += calculateRingAreaHa(hole)`), effectively double-deducting the shared spatial area and artificially deflating the visual geometry's net arable area.
- **Blast Radius:**
  Map visualizer rendering glitches and area discrepancy between algebraic Model M1 area and geometric hole-punched area.
- **Recommended Remediation:**
  Merge overlapping exclusion features via planar polygon union (e.g. `@turf/union` or boolean clipping) before punching inner rings.

---

### DEFECT-04 (LOW): Inconsistency at 300.001 ha & Preservation Ratio Upper Bound
- **Location 1:** `src/lib/m1/calculator.ts` line 130 vs `src/lib/dossier/generator.ts` line 42.
  - In `calculator.ts`, `grossArea` is rounded to 2 decimal places (`300.001` becomes `300.00`). Consequently, `continuousMonitoringMandatory` is `false`.
  - In `generator.ts`, `grossAreaHa > 300.0` is evaluated directly on unrounded float, resulting in `true`.
  - Furthermore, Tier 2 boundary test `B11-02` tests `300.001 ha -> true`.
- **Location 2:** `src/lib/m1/calculator.ts` line 69 vs `src/lib/m1/types.ts` line 41.
  - When conservation area exceeds gross area (e.g., 160 ha on a 100 ha parcel), `preservationRatio` evaluates to 1.6000.
  - The type definition states: `preservationRatio: number; // Ratio of total conservation to gross area (0.0 to 1.0)`.
  - Downstream components expecting a normalized ratio between 0.0 and 1.0 may experience layout or calculation errors unless clamped to `Math.min(1.0, ...)`.
- **Recommended Remediation:**
  Harmonize rounding rules across `calculator.ts` and `generator.ts`, and clamp `preservationRatio = Math.min(1.0, netConservationArea / roundedGrossHa)`.

---

## 4. Overall Verdict

**VERDICT: DEFECT_DETECTED**

The core calculation logic in `calculator.ts` is robust against negative values and standard Art. 15 deduplication. However, the discrepancies identified in `generator.ts` (unbounded overlap deduction and omission of `matricula` from SHA-256 payload) and `geometry.ts` (lack of planar union for overlapping holes) represent genuine defect vectors that must be remediated prior to institutional credit deployment.
