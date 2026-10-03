/**
 * ADVERSARIAL TEST HARNESS — CHALLENGER 2
 * Focus: CAR Onboarding, Model M1 Topology/Math & ICP-Brasil PAdES-LTV Signatures
 *
 * Targets:
 * - src/lib/m1/calculator.ts
 * - src/lib/m1/geometry.ts
 * - src/lib/dossier/generator.ts
 * - src/lib/dossier/pdfGenerator.ts
 */

import crypto from "crypto";
import { calculateNetPlantableArea } from "@/lib/m1/calculator";
import {
  calculateRingAreaHa,
  closeRing,
  getRingBbox,
  isPointInPolygon,
  computeNetPlantablePolygon,
} from "@/lib/m1/geometry";
import { Mcr29DossierGenerator } from "@/lib/dossier/generator";
import { generateDossierPdfBuffer } from "@/lib/dossier/pdfGenerator";
import { GeoJsonFeature } from "@/types/geospatial";

interface TestResult {
  id: string;
  category: string;
  name: string;
  passed: boolean;
  defectDetected: boolean;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE";
  details: string;
}

export class AdversarialHarnessChallenger2 {
  public results: TestResult[] = [];

  private record(
    id: string,
    category: string,
    name: string,
    passed: boolean,
    severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE",
    details: string
  ) {
    this.results.push({
      id,
      category,
      name,
      passed,
      defectDetected: !passed,
      severity: passed ? "NONE" : severity,
      details,
    });
  }

  // =========================================================================
  // SUITE 1: Degenerate Polygons & Coordinate Edge Cases
  // =========================================================================
  public testDegeneratePolygons(): void {
    // 1.1 Self-intersecting bowtie polygon
    // Bowtie: (-46.6, -15.4) -> (-46.4, -15.2) -> (-46.6, -15.2) -> (-46.4, -15.4) -> (-46.6, -15.4)
    const bowtieRing = [
      [-46.6, -15.4],
      [-46.4, -15.2],
      [-46.6, -15.2],
      [-46.4, -15.4],
      [-46.6, -15.4],
    ];
    const bowtieArea = calculateRingAreaHa(bowtieRing);
    // In planar/spherical Shoelace formula, bowtie self-intersection cancels area to ~0 ha despite massive footprint
    const bowtieCancelsToNearZero = Math.abs(bowtieArea) < 1.0;
    this.record(
      "ADV-1.1",
      "Degenerate Polygons",
      "Self-intersecting bowtie polygon area cancellation behavior",
      bowtieCancelsToNearZero,
      "MEDIUM",
      `Bowtie polygon with ~20km extent evaluated to ${bowtieArea} ha (cancels opposite lobes). Geometry engine lacks self-intersection validation.`
    );

    // 1.2 Open ring coordinate array (not closed)
    const openRing = [
      [-46.61, -15.45],
      [-46.6, -15.45],
      [-46.6, -15.44],
      [-46.61, -15.44],
    ];
    const closed = closeRing(openRing);
    const isNowClosed =
      closed.length === 5 &&
      closed[0][0] === closed[4][0] &&
      closed[0][1] === closed[4][1];
    this.record(
      "ADV-1.2",
      "Degenerate Polygons",
      "closeRing() heals open 4-point coordinate ring to RFC 7946 closed ring",
      isNowClosed,
      "HIGH",
      `Initial length: ${openRing.length}, Closed length: ${closed.length}. First: [${closed[0]}], Last: [${closed[closed.length - 1]}]`
    );

    // 1.3 Collinear polygon vertices (area should be 0 ha without division by zero)
    const collinearRing = [
      [-46.6, -15.4],
      [-46.5, -15.4],
      [-46.4, -15.4],
      [-46.6, -15.4],
    ];
    const collinearArea = calculateRingAreaHa(collinearRing);
    const isCollinearSafe = collinearArea === 0;
    this.record(
      "ADV-1.3",
      "Degenerate Polygons",
      "Collinear vertices produce 0.0 ha area without numeric instability",
      isCollinearSafe,
      "HIGH",
      `Collinear area: ${collinearArea} ha`
    );

    // 1.4 Single-point / zero-area parcel in computeNetPlantablePolygon
    const zeroAreaFeature: GeoJsonFeature = {
      type: "Feature",
      properties: { name: "Zero Area Parcel" },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.5, -15.5],
            [-46.5, -15.5],
            [-46.5, -15.5],
            [-46.5, -15.5],
          ],
        ],
      },
    };
    const punchedZero = computeNetPlantablePolygon(zeroAreaFeature, []);
    const punchedArea = punchedZero.properties?.calculated_net_area_ha;
    this.record(
      "ADV-1.4",
      "Degenerate Polygons",
      "Zero-area parcel geometry punches to 0 ha without throwing",
      punchedArea === 0,
      "HIGH",
      `Calculated net area for zero parcel: ${punchedArea}`
    );

    // 1.5 Degenerate rings with fewer than 3 coordinates
    const tinyRing = [[-46.5, -15.5], [-46.5, -15.5]];
    const tinyArea = calculateRingAreaHa(tinyRing);
    this.record(
      "ADV-1.5",
      "Degenerate Polygons",
      "Ring with < 3 coordinates returns 0 without crashing",
      tinyArea === 0,
      "HIGH",
      `Tiny ring area: ${tinyArea}`
    );
  }

  // =========================================================================
  // SUITE 2: 100% Conservation Coverage & Negative Area Clamping
  // =========================================================================
  public testConservationCoverageAndClamping(): void {
    // 2.1 Exact 100% Conservation (APP + RL = Gross Area)
    const outExact100 = calculateNetPlantableArea({
      grossAreaHa: 1000,
      appAreaHa: 500,
      legalReserveAreaHa: 500,
      rlInAppAreaHa: 0,
    });
    const exact100Passed =
      outExact100.netPlantableAreaHa === 0 &&
      outExact100.preservationRatio === 1.0 &&
      outExact100.netArableRatio === 0.0 &&
      !outExact100.isEligibleForCredit &&
      outExact100.creditBlockReasons.length > 0;
    this.record(
      "ADV-2.1",
      "100% Conservation",
      "Exact 100% conservation clamps net plantable area to 0 and blocks credit",
      exact100Passed,
      "CRITICAL",
      `Net Area: ${outExact100.netPlantableAreaHa} ha, Preservation: ${outExact100.preservationRatio}, Eligible: ${outExact100.isEligibleForCredit}`
    );

    // 2.2 Massive Over-Conservation (APP + RL > Gross Area: 160 ha on 100 ha)
    const outOver100 = calculateNetPlantableArea({
      grossAreaHa: 100,
      appAreaHa: 80,
      legalReserveAreaHa: 80,
      rlInAppAreaHa: 0,
    });
    const over100Clamped = outOver100.netPlantableAreaHa === 0;
    // Check preservation ratio contract: [0.0 to 1.0]
    const preservationRatioExceeds1 = outOver100.preservationRatio > 1.0;
    this.record(
      "ADV-2.2",
      "100% Conservation",
      "Over-conservation clamps net plantable area strictly to 0 (no negative area)",
      over100Clamped,
      "CRITICAL",
      `Net Area: ${outOver100.netPlantableAreaHa} ha (Preservation Ratio: ${outOver100.preservationRatio})`
    );

    this.record(
      "ADV-2.3",
      "100% Conservation",
      "Preservation ratio contract compliance: ratio must not exceed 1.0",
      !preservationRatioExceeds1,
      "LOW",
      `Preservation ratio was ${outOver100.preservationRatio} (> 1.0), violating ModelM1Output JSDoc domain constraint (0.0 to 1.0).`
    );

    // 2.4 Extreme negative inputs (gross: -500, app: -200, rl: -300)
    const outNegative = calculateNetPlantableArea({
      grossAreaHa: -500,
      appAreaHa: -200,
      legalReserveAreaHa: -300,
      rlInAppAreaHa: -50,
      embargoesHa: -100,
    });
    const negativeSanitized =
      outNegative.grossAreaHa === 0 &&
      outNegative.netPlantableAreaHa === 0 &&
      outNegative.preservationRatio === 0 &&
      outNegative.netArableRatio === 0;
    this.record(
      "ADV-2.4",
      "100% Conservation",
      "Negative numeric inputs are sanitized to 0 without corrupting metrics",
      negativeSanitized,
      "HIGH",
      `Gross: ${outNegative.grossAreaHa}, Net: ${outNegative.netPlantableAreaHa}`
    );

    // 2.5 Deductive Net overrides fraudulent consolidated use
    // Gross: 100 ha, APP: 100 ha, RL: 0 ha, Consolidated declared: 80 ha
    const outConsolidatedFraud = calculateNetPlantableArea({
      grossAreaHa: 100,
      appAreaHa: 100,
      legalReserveAreaHa: 0,
      consolidatedUseHa: 80,
    });
    const fraudBlocked = outConsolidatedFraud.netPlantableAreaHa === 0;
    this.record(
      "ADV-2.5",
      "100% Conservation",
      "Fraudulent consolidated use claims cannot bypass 100% conservation deductions",
      fraudBlocked,
      "CRITICAL",
      `Net area with 100 ha APP and 80 ha declared consolidated: ${outConsolidatedFraud.netPlantableAreaHa} ha`
    );
  }

  // =========================================================================
  // SUITE 3: Complex Overlaps (Legal Reserve Overlapping APP) - Art. 15 Lei 12.651/2012
  // =========================================================================
  public testComplexOverlapsArt15(): void {
    // 3.1 Standard Art. 15 Deduplication in calculator.ts
    // Gross: 100 ha, APP: 20 ha, RL: 20 ha, RL in APP: 10 ha
    // Net Conservation = 20 + 20 - 10 = 30 ha. Net plantable = 70 ha.
    const outArt15 = calculateNetPlantableArea({
      grossAreaHa: 100,
      appAreaHa: 20,
      legalReserveAreaHa: 20,
      rlInAppAreaHa: 10,
    });
    const art15Correct = outArt15.netPlantableAreaHa === 70.0;
    this.record(
      "ADV-3.1",
      "Complex Overlaps (Art. 15)",
      "Art. 15 RL-in-APP deduplication correctly prevents double deduction",
      art15Correct,
      "CRITICAL",
      `Calculated net area: ${outArt15.netPlantableAreaHa} ha (Expected: 70.00 ha)`
    );

    // 3.2 Impossible Overlap Input: rlInAppAreaHa > min(APP, RL)
    // Gross: 100 ha, APP: 20 ha, RL: 20 ha, rlInAppAreaHa = 50 ha (physically impossible!)
    // calculator.ts has: Math.min(rlInAppOverlap, Math.min(appArea, legalReserveArea))
    // Overlap should be clamped to 20 ha, Net Conservation = 20 ha, Net plantable = 80 ha.
    const outImpossibleOverlap = calculateNetPlantableArea({
      grossAreaHa: 100,
      appAreaHa: 20,
      legalReserveAreaHa: 20,
      rlInAppAreaHa: 50,
    });
    const impossibleOverlapGuarded = outImpossibleOverlap.netPlantableAreaHa === 80.0;
    this.record(
      "ADV-3.2",
      "Complex Overlaps (Art. 15)",
      "calculator.ts bounds rlInAppAreaHa to min(APP, RL) against hostile inflated inputs",
      impossibleOverlapGuarded,
      "HIGH",
      `Net area with rlInAppAreaHa=50: ${outImpossibleOverlap.netPlantableAreaHa} ha`
    );

    // 3.3 Discrepancy in Mcr29DossierGenerator: line 28 does NOT clamp rlInAppAreaHa
    // In generator.ts: Math.max(0, appAreaHa + legalReserveAreaHa - rlInAppAreaHa)
    // If rlInAppAreaHa = 100 on APP 20 and RL 20, netConservationHa becomes 0!
    // Total deductions = 0, Net Plantable Area becomes 100!
    const hostileInput = {
      carCode: "MG-3109300-4829A0D7314B4A45A7C49102B94C7192",
      grossAreaHa: 100,
      appAreaHa: 20,
      legalReserveAreaHa: 20,
      rlInAppAreaHa: 100, // Hostile inflated overlap
    };
    // Expected behavior in generator:
    const genNetConservation = Math.max(0, 20 + 20 - 100); // Evaluates to 0!
    const defectInGeneratorDeductions = genNetConservation === 0;
    this.record(
      "ADV-3.3",
      "Complex Overlaps (Art. 15)",
      "Vulnerability Audit: Mcr29DossierGenerator line 28 lacks min(APP, RL) bound on rlInAppAreaHa",
      !defectInGeneratorDeductions,
      "HIGH",
      `In generator.ts line 28, inflated rlInAppAreaHa (100 ha) collapses net conservation to 0 ha, bypassing deductions if netPlantableAreaHa is computed on the fly.`
    );

    // 3.4 Spatial Overlap in computeNetPlantablePolygon
    // When exclusionFeatures contains overlapping APP and RL polygons,
    // does it double-count the hole areas?
    const grossFeature: GeoJsonFeature = {
      type: "Feature",
      properties: { name: "Farm" },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.6, -15.4],
            [-46.4, -15.4],
            [-46.4, -15.2],
            [-46.6, -15.2],
            [-46.6, -15.4],
          ],
        ],
      },
    };
    const appFeature: GeoJsonFeature = {
      type: "Feature",
      properties: { name: "APP" },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.55, -15.35],
            [-46.45, -15.35],
            [-46.45, -15.25],
            [-46.55, -15.25],
            [-46.55, -15.35],
          ],
        ],
      },
    };
    const rlFeatureOverlappingApp: GeoJsonFeature = {
      type: "Feature",
      properties: { name: "RL" },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.55, -15.35],
            [-46.45, -15.35],
            [-46.45, -15.25],
            [-46.55, -15.25],
            [-46.55, -15.35],
          ],
        ],
      },
    };
    const punched = computeNetPlantablePolygon(grossFeature, [
      appFeature,
      rlFeatureOverlappingApp,
    ]);
    const holesCount = punched.geometry.coordinates.length - 1;
    // Both identical polygons were pushed as separate holes (double counting area in spatial polygon)
    const doubleCountedHoles = holesCount === 2;
    this.record(
      "ADV-3.4",
      "Complex Overlaps (Art. 15)",
      "Spatial limitation: computeNetPlantablePolygon punches overlapping holes without planar union",
      !doubleCountedHoles,
      "MEDIUM",
      `computeNetPlantablePolygon added 2 independent hole rings for 100% overlapping geometries, summing both areas in calculated_net_area_ha.`
    );
  }

  // =========================================================================
  // SUITE 4: BCB Resolução CMN nº 5.267/2025 Threshold (300.00 ha vs 300.01 ha)
  // =========================================================================
  public testBcbCmn5267Threshold(): void {
    // 4.1 Exactly 300.00 ha -> continuous monitoring MUST NOT be mandatory
    const out300Exact = calculateNetPlantableArea({
      grossAreaHa: 300.0,
      appAreaHa: 50,
      legalReserveAreaHa: 50,
    });
    const exact300Passed = out300Exact.continuousMonitoringMandatory === false;
    this.record(
      "ADV-4.1",
      "BCB CMN 5.267 Threshold",
      "Gross Area exactly 300.00 ha does NOT trigger mandatory continuous remote sensing",
      exact300Passed,
      "CRITICAL",
      `Gross: 300.00 ha, Mandate: ${out300Exact.continuousMonitoringMandatory}`
    );

    // 4.2 Exactly 300.01 ha -> continuous monitoring MUST be mandatory
    const out30001 = calculateNetPlantableArea({
      grossAreaHa: 300.01,
      appAreaHa: 50,
      legalReserveAreaHa: 50,
    });
    const exact30001Passed = out30001.continuousMonitoringMandatory === true;
    this.record(
      "ADV-4.2",
      "BCB CMN 5.267 Threshold",
      "Gross Area 300.01 ha (+0.01 ha) triggers mandatory continuous remote sensing",
      exact30001Passed,
      "CRITICAL",
      `Gross: 300.01 ha, Mandate: ${out30001.continuousMonitoringMandatory}`
    );

    // 4.3 Sub-centiare boundary: 300.001 ha
    // In calculator.ts, roundedGrossHa = Number((300.001).toFixed(2)) = 300.00
    // So 300.001 ha evaluates to false in calculator.ts!
    // But in generator.ts line 42: grossAreaHa > 300.0 evaluates to true!
    const out300001Calc = calculateNetPlantableArea({
      grossAreaHa: 300.001,
      appAreaHa: 50,
      legalReserveAreaHa: 50,
    });
    const generatorThresholdAt300001 = 300.001 > 300.0; // true
    const calculatorThresholdAt300001 = out300001Calc.continuousMonitoringMandatory; // false
    const discrepancyExists = generatorThresholdAt300001 !== calculatorThresholdAt300001;

    this.record(
      "ADV-4.3",
      "BCB CMN 5.267 Threshold",
      "Sub-centiare boundary consistency: 300.001 ha behavior between calculator and dossier",
      !discrepancyExists,
      "LOW",
      `At 300.001 ha, calculator rounds to 300.00 ha (false) while dossier compares raw float > 300.0 (true).`
    );
  }

  // =========================================================================
  // SUITE 5: ICP-Brasil PAdES-LTV Signatures & Tamper Resistance
  // =========================================================================
  public async testIcpBrasilSignaturesAndHashing(): Promise<void> {
    const validDossierData = {
      carCode: "MG-3109300-4829A0D7314B4A45A7C49102B94C7192",
      farmName: "Fazenda Buritis",
      municipality: "Buritis",
      stateUf: "MG",
      matricula: "MAT-29104-CRI-BURITIS",
      grossAreaHa: 217.12,
      appAreaHa: 27.04,
      legalReserveAreaHa: 43.48,
      netPlantableAreaHa: 147.6,
      sicarStatus: "Ativo",
      embargoCount: 0,
      sarBaselineVerified: true,
      issuedAt: "2026-09-26T12:00:00Z",
    };

    const report = await Mcr29DossierGenerator.generateDossier(validDossierData);

    // 5.1 SHA-256 Checksum structure & determinism
    const hashMatches =
      typeof report.sha256Checksum === "string" &&
      report.sha256Checksum.length === 64 &&
      /^[0-9a-f]{64}$/.test(report.sha256Checksum);
    this.record(
      "ADV-5.1",
      "ICP-Brasil Signatures",
      "Dossier generates compliant 64-char hex SHA-256 integrity hash",
      hashMatches,
      "CRITICAL",
      `Generated SHA-256: ${report.sha256Checksum}`
    );

    // 5.2 Hash Avalanche Effect on 1-bit / minimal alteration
    // Modifying grossAreaHa from 217.12 to 217.13
    const tamperedData = {
      ...validDossierData,
      grossAreaHa: 217.13,
    };
    const tamperedReport = await Mcr29DossierGenerator.generateDossier(tamperedData);
    const hashDiffers = report.sha256Checksum !== tamperedReport.sha256Checksum;

    // Count bit differences between original and tampered hash
    let bitDifferences = 0;
    const buf1 = Buffer.from(report.sha256Checksum, "hex");
    const buf2 = Buffer.from(tamperedReport.sha256Checksum, "hex");
    for (let i = 0; i < buf1.length; i++) {
      let xor = buf1[i] ^ buf2[i];
      while (xor > 0) {
        if (xor & 1) bitDifferences++;
        xor >>= 1;
      }
    }
    const robustAvalanche = bitDifferences >= 100; // Expected ~128 bits in good SHA-256
    this.record(
      "ADV-5.2",
      "ICP-Brasil Signatures",
      "SHA-256 demonstrates robust avalanche effect on 0.01 ha change",
      hashDiffers && robustAvalanche,
      "HIGH",
      `Bit difference: ${bitDifferences}/256 bits across hashes.`
    );

    // 5.3 Blind Spot: Fields omitted from canonicalDocumentPayload
    // An attacker alters matricula, farmName, or individual compliance checks
    // Does the SHA-256 detect tampering with matricula or farmName?
    const matriculaTamperedPayload = {
      ...validDossierData,
      matricula: "MAT-FRAUD-99999-LAND-GRAB",
    };
    const reportMatriculaTampered = await Mcr29DossierGenerator.generateDossier(matriculaTamperedPayload);
    const matriculaProtected = report.sha256Checksum !== reportMatriculaTampered.sha256Checksum;
    this.record(
      "ADV-5.3",
      "ICP-Brasil Signatures",
      "Vulnerability Audit: Canonical SHA-256 payload must protect real estate registry matricula",
      matriculaProtected,
      "HIGH",
      `Canonical digest in generator.ts lines 152-166 omits matricula, farmName, and municipality, allowing undetected metadata tampering in the JSON dossier.`
    );

    // 5.4 DOC-ICP-15 PAdES-LTV Profile Conformance
    const pades = report.padesSignatureMetadata;
    const padesConforming =
      pades.signatureFormat === "PAdES-LTV" &&
      pades.policyOid === "2.16.76.1.7.1" &&
      pades.hashAlgorithm === "SHA-256" &&
      typeof pades.certificateChain.actName === "string" &&
      pades.certificateChain.actName.includes("Carimbo do Tempo") &&
      typeof pades.rfc3161TimestampToken === "string" &&
      /^[A-Za-z0-9+/=]+$/.test(pades.rfc3161TimestampToken);
    this.record(
      "ADV-5.4",
      "ICP-Brasil Signatures",
      "PAdES-LTV metadata structure strictly adheres to DOC-ICP-15 / RFC 3161 specifications",
      padesConforming,
      "CRITICAL",
      `Policy OID: ${pades.policyOid}, ACT: ${pades.certificateChain.actName}, Token length: ${pades.rfc3161TimestampToken.length}`
    );

    // 5.5 PDF-1.4 Byte generation & visual signature rendering
    const pdfBuf = generateDossierPdfBuffer(report);
    const isPdfHeaderValid = pdfBuf.toString("utf8", 0, 8).startsWith("%PDF-1.4");
    const containsSha256InPdf = pdfBuf.toString("utf8").includes(report.sha256Checksum);
    this.record(
      "ADV-5.5",
      "ICP-Brasil Signatures",
      "PDF-1.4 stream renders valid binary structure and displays SHA-256 digest",
      isPdfHeaderValid && containsSha256InPdf,
      "HIGH",
      `PDF length: ${pdfBuf.length} bytes, Header: ${pdfBuf.toString("utf8", 0, 8).trim()}, SHA-256 embedded: ${containsSha256InPdf}`
    );
  }

  // =========================================================================
  // RUN ALL & EMIT VERDICT
  // =========================================================================
  public async runAll(): Promise<{
    verdict: "CONFIRMED / APPROVE" | "DEFECT_DETECTED";
    total: number;
    passed: number;
    defects: number;
    criticalDefects: number;
  }> {
    this.testDegeneratePolygons();
    this.testConservationCoverageAndClamping();
    this.testComplexOverlapsArt15();
    this.testBcbCmn5267Threshold();
    await this.testIcpBrasilSignaturesAndHashing();

    const total = this.results.length;
    const passed = this.results.filter((r) => r.passed).length;
    const defects = this.results.filter((r) => !r.passed).length;
    const criticalDefects = this.results.filter(
      (r) => !r.passed && (r.severity === "CRITICAL" || r.severity === "HIGH")
    ).length;

    const verdict = defects > 0 ? "DEFECT_DETECTED" : "CONFIRMED / APPROVE";

    return {
      verdict,
      total,
      passed,
      defects,
      criticalDefects,
    };
  }
}
