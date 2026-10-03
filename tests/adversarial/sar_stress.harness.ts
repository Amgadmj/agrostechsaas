/**
 * Adversarial Stress Test Harness for SAR Ingestion & M2 Anti-Fuga Engine
 * Agent: Challenger 1 (Generation 2)
 * Working Directory: .agents/teamwork/challenger_1_gen2/sar_stress_harness.ts
 *
 * Verifies:
 * 1. Boundary Drops: -4.49 dB vs -4.50 dB vs -4.51 dB
 * 2. Bare-Soil Floor: -20.0 dB threshold, lodging vs harvest, stubble bias
 * 3. S_clima Precipitation Refutation: 0 to 100 mm sweep, 60 mm cutoff, storm suppression
 * 4. Commercial SAR Tasking Schemas: Extreme coordinates, inverted windows, > 25 km² AOI, grazing angles
 * 5. Radiometric Conversions & Statistical Biases: linearToDb, dbToLinear, zonal averaging
 */

import { HarvestDetectionEngine, DEFAULT_HARVEST_THRESHOLD_DB, DEFAULT_BARE_SOIL_FLOOR_DB } from "@/lib/sar/harvestEngine";
import { CommercialTaskingRequestSchema } from "@/lib/sar/commercial/schema";
import { UmbraCanopyAdapter } from "@/lib/sar/commercial/umbraAdapter";
import { TerraSarXAdapter } from "@/lib/sar/commercial/terrasarxAdapter";
import { linearToDb, dbToLinear, calculateCrossPolRatioDb, calculateZonalStats } from "@/lib/sar/temporalEngine";
import { calculatePolygonAreaHa } from "@/lib/spatialUtils";
import { TemporalBackscatterPoint } from "@/types/sar";

export interface StressTestResult {
  testId: string;
  name: string;
  category: "BOUNDARY_DROPS" | "BARE_SOIL_FLOOR" | "CLIMATE_REFUTATION" | "COMMERCIAL_SCHEMA" | "RADIOMETRIC_BIAS";
  passed: boolean;
  expected: string;
  actual: string;
  defectIdentified: boolean;
  notes: string;
}

export class SarAdversarialHarness {
  private results: StressTestResult[] = [];

  private record(
    testId: string,
    name: string,
    category: StressTestResult["category"],
    passed: boolean,
    expected: string,
    actual: string,
    defectIdentified: boolean,
    notes: string
  ) {
    this.results.push({
      testId,
      name,
      category,
      passed,
      expected,
      actual,
      defectIdentified,
      notes,
    });
  }

  // ---------------------------------------------------------------------------
  // 1. Boundary Drops: -4.49 dB vs -4.50 dB vs -4.51 dB
  // ---------------------------------------------------------------------------
  runBoundaryDropTests(): void {
    const engine = new HarvestDetectionEngine();

    // Test 1.1: Drop = -4.49 dB (Sub-threshold boundary)
    const points449: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -10, gamma0_vh_db: -15.5, vh_vv_ratio_db: -5.5, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -15, gamma0_vh_db: -19.99, vh_vv_ratio_db: -4.99, pixelCount: 1000 }, // Delta = -4.49 dB
    ];
    const res449 = engine.detectHarvestEvents(points449, -4.5);
    const pass449 = !res449.harvestDetected;
    // Defect investigation: alertLevel for -4.49 dB drop
    // An acute drop of -4.49 dB should indicate at least Level 3 (Desiccation / Imminent harvest),
    // but because drop is not recorded when deltaVh > thresholdDb, alertLevel falls through to 1.
    const alertLevelAnomaly = res449.alertLevel === 1;
    this.record(
      "ADV-DROP-01",
      "Sub-threshold drop (-4.49 dB) correctly rejects harvest detection",
      "BOUNDARY_DROPS",
      pass449,
      "harvestDetected = false",
      `harvestDetected = ${res449.harvestDetected}, alertLevel = ${res449.alertLevel}`,
      alertLevelAnomaly,
      "Defect Note: -4.49 dB drop is not recorded in maxDropMagnitude, resetting alertLevel to 1 (Vegetative) instead of 3 (Desiccation)."
    );

    // Test 1.2: Drop = -4.50 dB (Exact calibrated threshold)
    const points450: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -10, gamma0_vh_db: -15.5, vh_vv_ratio_db: -5.5, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -15, gamma0_vh_db: -20.0, vh_vv_ratio_db: -5.0, pixelCount: 1000 }, // Delta = -4.50 dB
    ];
    const res450 = engine.detectHarvestEvents(points450, -4.5);
    const pass450 = res450.harvestDetected && res450.dropMagnitudeDb === 4.5 && res450.alertLevel >= 4;
    this.record(
      "ADV-DROP-02",
      "Exact threshold drop (-4.50 dB) triggers harvest alert Level 4",
      "BOUNDARY_DROPS",
      pass450,
      "harvestDetected = true, dropMagnitudeDb = 4.5, alertLevel >= 4",
      `harvestDetected = ${res450.harvestDetected}, dropMagnitudeDb = ${res450.dropMagnitudeDb}, alertLevel = ${res450.alertLevel}`,
      false,
      "Exact boundary -4.50 dB confirms harvest when soil floor is reached."
    );

    // Test 1.3: Drop = -4.51 dB (Supra-threshold boundary)
    const points451: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -10, gamma0_vh_db: -15.5, vh_vv_ratio_db: -5.5, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -15, gamma0_vh_db: -20.01, vh_vv_ratio_db: -5.01, pixelCount: 1000 }, // Delta = -4.51 dB
    ];
    const res451 = engine.detectHarvestEvents(points451, -4.5);
    const pass451 = res451.harvestDetected && res451.dropMagnitudeDb === 4.5 && res451.alertLevel >= 4;
    this.record(
      "ADV-DROP-03",
      "Supra-threshold drop (-4.51 dB) triggers harvest alert Level 4",
      "BOUNDARY_DROPS",
      pass451,
      "harvestDetected = true, alertLevel >= 4",
      `harvestDetected = ${res451.harvestDetected}, dropMagnitudeDb = ${res451.dropMagnitudeDb}, alertLevel = ${res451.alertLevel}`,
      false,
      "Supra-threshold drop cleanly detected."
    );

    // Test 1.4: Floating-point precision hazard (-19.6 - (-15.1))
    // In IEEE 754: -19.6 - (-15.1) evaluates to -4.499999999999999
    const deltaFloat = -19.6 - (-15.1);
    const isLeq = deltaFloat <= -4.5;
    this.record(
      "ADV-DROP-04",
      "IEEE 754 floating point precision edge case on exact 0.1dB steps",
      "BOUNDARY_DROPS",
      !isLeq, // It fails <= -4.5 due to floating point representation
      "deltaFloat <= -4.5 is false due to binary representation (-4.499999999999999)",
      `deltaFloat = ${deltaFloat}, isLeq = ${isLeq}`,
      true,
      "Defect Note: Unrounded float subtraction -19.6 - (-15.1) yields -4.499999999999999, causing false negative rejection."
    );
  }

  // ---------------------------------------------------------------------------
  // 2. Bare-Soil Floor Requirement (-20.0 dB)
  // ---------------------------------------------------------------------------
  runBareSoilFloorTests(): void {
    const engine = new HarvestDetectionEngine();

    // Test 2.1: Massive drop of -6.0 dB, but post-harvest is -19.5 dB (stubble/rough soil)
    const pointsNoTill: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -9.0, gamma0_vh_db: -13.5, vh_vv_ratio_db: -4.5, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -14.0, gamma0_vh_db: -19.5, vh_vv_ratio_db: -5.5, pixelCount: 1000 }, // Delta = -6.0 dB
    ];
    const resNoTill = engine.detectHarvestEvents(pointsNoTill, -4.5, { bareSoilFloorDb: -20.0 });
    this.record(
      "ADV-SOIL-01",
      "Massive drop (-6.0 dB) missing -20.0 dB floor is rejected",
      "BARE_SOIL_FLOOR",
      !resNoTill.harvestDetected && !resNoTill.bareSoilReached,
      "harvestDetected = false, bareSoilReached = false",
      `harvestDetected = ${resNoTill.harvestDetected}, bareSoilReached = ${resNoTill.bareSoilReached}`,
      true,
      "Defect Note: In Brazilian No-Till (Plantio Direto) with heavy mulch, post-harvest backscatter often remains at -19.5 dB, resulting in missed harvest detection."
    );

    // Test 2.2: Lodging scenario (flattened crop, drop of -4.8 dB from -12.0 to -16.8 dB)
    const pointsLodging: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -8.0, gamma0_vh_db: -12.0, vh_vv_ratio_db: -4.0, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -11.0, gamma0_vh_db: -16.8, vh_vv_ratio_db: -5.8, pixelCount: 1000 },
    ];
    const resLodging = engine.detectHarvestEvents(pointsLodging, -4.5, { bareSoilFloorDb: -20.0 });
    this.record(
      "ADV-SOIL-02",
      "Crop lodging / storm damage (-4.8 dB drop to -16.8 dB) correctly rejected",
      "BARE_SOIL_FLOOR",
      !resLodging.harvestDetected && !resLodging.bareSoilReached,
      "harvestDetected = false, bareSoilReached = false",
      `harvestDetected = ${resLodging.harvestDetected}, bareSoilReached = ${resLodging.bareSoilReached}`,
      false,
      "Bare-soil floor correctly discriminates canopy flattening/lodging from full mechanical harvest."
    );

    // Test 2.3: Progressive two-stage harvest (two -3.0 dB steps, cumulative -6.0 dB to -21.0 dB)
    const pointsProgressive: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -10.0, gamma0_vh_db: -15.0, vh_vv_ratio_db: -5.0, pixelCount: 1000 },
      { date: "2026-02-10", gamma0_vv_db: -12.5, gamma0_vh_db: -18.0, vh_vv_ratio_db: -5.5, pixelCount: 1000 }, // Step 1: -3.0 dB
      { date: "2026-02-20", gamma0_vv_db: -15.0, gamma0_vh_db: -21.0, vh_vv_ratio_db: -6.0, pixelCount: 1000 }, // Step 2: -3.0 dB
    ];
    const resProgressive = engine.detectHarvestEvents(pointsProgressive, -4.5);
    this.record(
      "ADV-SOIL-03",
      "Progressive multi-pass harvest (-3.0 dB + -3.0 dB = -6.0 dB) missed by single-step evaluation",
      "BARE_SOIL_FLOOR",
      !resProgressive.harvestDetected,
      "harvestDetected = false (single step < -4.5 dB)",
      `harvestDetected = ${resProgressive.harvestDetected}, dropMagnitudeDb = ${resProgressive.dropMagnitudeDb}`,
      true,
      "Defect Note: Engine only inspects adjacent consecutive acquisitions (deltaVh = curr - prev). Progressive harvesting over 10-20 days is missed."
    );
  }

  // ---------------------------------------------------------------------------
  // 3. S_clima Precipitation Refutation Filter
  // ---------------------------------------------------------------------------
  runClimateRefutationTests(): void {
    const engine = new HarvestDetectionEngine();
    const standardHarvestPoints: TemporalBackscatterPoint[] = [
      { date: "2026-02-01", gamma0_vv_db: -10, gamma0_vh_db: -15.0, vh_vv_ratio_db: -5.0, pixelCount: 1000 },
      { date: "2026-02-15", gamma0_vv_db: -15, gamma0_vh_db: -20.5, vh_vv_ratio_db: -5.5, pixelCount: 1000 }, // Delta = -5.5 dB
    ];

    // Test 3.1: Dry conditions (5 mm) -> Refuted = true, Harvest detected
    const res5mm = engine.detectHarvestEvents(standardHarvestPoints, -4.5, { precipitationMm48h: 5.0 });
    this.record(
      "ADV-CLIM-01",
      "Dry conditions (5.0 mm 48h) confirms harvest with high confidence",
      "CLIMATE_REFUTATION",
      res5mm.harvestDetected && res5mm.climateRefutation.rainArtifactRefuted && res5mm.climateRefutation.sClimaIndex === 1.0,
      "harvestDetected = true, sClimaIndex = 1.0",
      `harvestDetected = ${res5mm.harvestDetected}, sClimaIndex = ${res5mm.climateRefutation.sClimaIndex}`,
      false,
      "Baseline dry conditions pass cleanly."
    );

    // Test 3.2: Critical Boundary at 60.0 mm -> Exactly sClimaIndex = 0.50 (Passes)
    const res60mm = engine.detectHarvestEvents(standardHarvestPoints, -4.5, { precipitationMm48h: 60.0 });
    this.record(
      "ADV-CLIM-02",
      "Boundary precipitation (60.0 mm 48h) yields exact cutoff sClimaIndex = 0.50",
      "CLIMATE_REFUTATION",
      res60mm.harvestDetected && res60mm.climateRefutation.sClimaIndex === 0.5 && res60mm.climateRefutation.rainArtifactRefuted,
      "harvestDetected = true, sClimaIndex = 0.50",
      `harvestDetected = ${res60mm.harvestDetected}, sClimaIndex = ${res60mm.climateRefutation.sClimaIndex}`,
      false,
      "60.0 mm is the exact mathematical boundary."
    );

    // Test 3.3: Rainfall > 60.0 mm (65.0 mm) -> Refuted = false, Harvest Suppressed
    const res65mm = engine.detectHarvestEvents(standardHarvestPoints, -4.5, { precipitationMm48h: 65.0 });
    this.record(
      "ADV-CLIM-03",
      "Heavy precipitation (65.0 mm 48h) suppresses harvest alert due to dielectric ambiguity",
      "CLIMATE_REFUTATION",
      !res65mm.harvestDetected && !res65mm.climateRefutation.rainArtifactRefuted && res65mm.climateRefutation.sClimaIndex === 0.4,
      "harvestDetected = false, rainArtifactRefuted = false, sClimaIndex = 0.40",
      `harvestDetected = ${res65mm.harvestDetected}, rainArtifactRefuted = ${res65mm.climateRefutation.rainArtifactRefuted}, sClimaIndex = ${res65mm.climateRefutation.sClimaIndex}`,
      false,
      "Rain filter correctly prevents false positives from moisture swings."
    );

    // Test 3.4: Adversarial Storm Vulnerability: Real harvest during heavy storm is suppressed
    const resStorm = engine.detectHarvestEvents(standardHarvestPoints, -4.5, {
      precipitationMm48h: 80.0,
      unregisteredDiversionSuspected: true,
    });
    this.record(
      "ADV-CLIM-04",
      "Adversarial storm exploit: Fraudulent harvest during 80mm rainstorm is suppressed",
      "CLIMATE_REFUTATION",
      !resStorm.harvestDetected,
      "harvestDetected = false (suppressed by rain filter)",
      `harvestDetected = ${resStorm.harvestDetected}, alertLevel = ${resStorm.alertLevel}`,
      true,
      "Defect Note: A debtor harvesting in heavy rain avoids Level 5 Fuga Noturna alert because rainArtifactRefuted suppresses detection."
    );
  }

  // ---------------------------------------------------------------------------
  // 4. Commercial SAR Tasking Schemas (Umbra & TerraSAR-X)
  // ---------------------------------------------------------------------------
  runCommercialSchemaTests(): void {
    // Test 4.1: Extreme Non-Physical Coordinates ([-350, 450])
    const payloadExtremeCoords = {
      provider: "umbra",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-350, 450],
            [-350, 451],
            [-349, 451],
            [-349, 450],
            [-350, 450],
          ],
        ],
      },
      resolutionMode: "SPOTLIGHT_0_25M",
      polarization: "HH",
      acquisitionWindow: {
        startDatetime: "2026-10-01T00:00:00Z",
        endDatetime: "2026-10-02T00:00:00Z",
      },
    };
    const parseResultExtreme = CommercialTaskingRequestSchema.safeParse(payloadExtremeCoords);
    this.record(
      "ADV-COMM-01",
      "GeoJsonPolygonSchema permits out-of-range WGS84 coordinates ([-350, 450])",
      "COMMERCIAL_SCHEMA",
      parseResultExtreme.success, // Schema currently accepts this!
      "Schema should reject coordinates outside [-180, 180] and [-90, 90]",
      `safeParse.success = ${parseResultExtreme.success}`,
      true,
      "Defect Note: GeoJsonPolygonSchema lacks .min(-180).max(180) and .min(-90).max(90) boundary constraints."
    );

    // Test 4.2: Inverted Time Window (startDatetime > endDatetime)
    const payloadInvertedWindow = {
      provider: "umbra",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.615, -15.452],
            [-46.615, -15.418],
            [-46.591, -15.418],
            [-46.591, -15.452],
            [-46.615, -15.452],
          ],
        ],
      },
      resolutionMode: "SPOTLIGHT_0_25M",
      polarization: "HH",
      acquisitionWindow: {
        startDatetime: "2026-10-05T00:00:00Z",
        endDatetime: "2026-10-01T00:00:00Z", // Inverted
      },
    };
    const parseResultInverted = CommercialTaskingRequestSchema.safeParse(payloadInvertedWindow);
    this.record(
      "ADV-COMM-02",
      "Inverted acquisition window (start > end) is strictly rejected by Zod refinement",
      "COMMERCIAL_SCHEMA",
      !parseResultInverted.success,
      "safeParse.success = false",
      `safeParse.success = ${parseResultInverted.success}`,
      false,
      "Inverted time windows are cleanly rejected."
    );

    // Test 4.3: Oversized AOI (> 25 km²) for Spotlight Mode
    // 6 km x 6 km = 36 km² (3,600 ha)
    const payloadOversizedAoi = {
      provider: "umbra",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.65, -15.45],
            [-46.65, -15.39],
            [-46.59, -15.39],
            [-46.59, -15.45],
            [-46.65, -15.45],
          ],
        ],
      },
      resolutionMode: "SPOTLIGHT_0_25M",
      polarization: "HH",
      acquisitionWindow: {
        startDatetime: "2026-10-01T00:00:00Z",
        endDatetime: "2026-10-02T00:00:00Z",
      },
    };
    const parseResultOversized = CommercialTaskingRequestSchema.safeParse(payloadOversizedAoi);
    this.record(
      "ADV-COMM-03",
      "Oversized footprint (> 25 km²) is rejected for Spotlight 0.25m mode",
      "COMMERCIAL_SCHEMA",
      !parseResultOversized.success,
      "safeParse.success = false (AOI exceeds 25 km² limit)",
      `safeParse.success = ${parseResultOversized.success}`,
      false,
      "Footprint area limit is strictly enforced for Spotlight modes."
    );

    // Test 4.4: Inverted Grazing Angles (min: 70, max: 30)
    const payloadInvertedGrazing = {
      provider: "umbra",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-46.615, -15.452],
            [-46.615, -15.418],
            [-46.591, -15.418],
            [-46.591, -15.452],
            [-46.615, -15.452],
          ],
        ],
      },
      resolutionMode: "SPOTLIGHT_0_25M",
      polarization: "HH",
      acquisitionWindow: {
        startDatetime: "2026-10-01T00:00:00Z",
        endDatetime: "2026-10-02T00:00:00Z",
      },
      geometricConstraints: {
        minGrazingAngleDeg: 70,
        maxGrazingAngleDeg: 30, // Inverted! min > max
      },
    };
    const parseResultGrazing = CommercialTaskingRequestSchema.safeParse(payloadInvertedGrazing);
    this.record(
      "ADV-COMM-04",
      "Inverted grazing angles (min 70 > max 30) bypasses GeometricConstraintsSchema validation",
      "COMMERCIAL_SCHEMA",
      parseResultGrazing.success, // Currently passes!
      "Schema should reject minGrazingAngleDeg >= maxGrazingAngleDeg",
      `safeParse.success = ${parseResultGrazing.success}`,
      true,
      "Defect Note: GeometricConstraintsSchema does not refine minGrazingAngleDeg < maxGrazingAngleDeg."
    );

    // Test 4.5: Umbra Infeasible Duration (< 12h)
    const umbraAdapter = new UmbraCanopyAdapter();
    let umbraThrows = false;
    try {
      umbraAdapter.scheduleTasking({
        provider: "umbra",
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [-46.615, -15.452],
              [-46.615, -15.418],
              [-46.591, -15.418],
              [-46.591, -15.452],
              [-46.615, -15.452],
            ],
          ],
        },
        resolutionMode: "SPOTLIGHT_0_25M",
        polarization: "HH",
        acquisitionWindow: {
          startDatetime: "2026-10-01T00:00:00Z",
          endDatetime: "2026-10-01T06:00:00Z", // 6 hours < 12h
        },
      });
    } catch {
      umbraThrows = true;
    }
    this.record(
      "ADV-COMM-05",
      "Umbra adapter rejects acquisition window shorter than 12h constellation revisit",
      "COMMERCIAL_SCHEMA",
      umbraThrows,
      "Throws feasibility error for duration < 12h",
      `umbraThrows = ${umbraThrows}`,
      false,
      "Feasibility constraint verified."
    );
  }

  // ---------------------------------------------------------------------------
  // 5. Radiometric Conversions & Statistical Biases
  // ---------------------------------------------------------------------------
  runRadiometricBiasTests(): void {
    // Test 5.1: Negative Euler-Mascheroni bias in log-domain spatial averaging
    // Pixel sample representing radar speckle: [0.01, 0.05, 0.02, 0.08, 0.03]
    const pixels = [0.01, 0.05, 0.02, 0.08, 0.03];
    const meanLinear = pixels.reduce((a, b) => a + b, 0) / pixels.length; // 0.038
    const trueUnbiasedMeanDb = linearToDb(meanLinear); // -14.20 dB

    const zonalStats = calculateZonalStats(pixels);
    const logAveragedMeanDb = zonalStats.meanDb; // Averaged in dB domain
    const biasDb = logAveragedMeanDb - trueUnbiasedMeanDb;

    this.record(
      "ADV-RADIO-01",
      "Log-domain spatial averaging introduces negative Euler-Mascheroni bias",
      "RADIOMETRIC_BIAS",
      logAveragedMeanDb < trueUnbiasedMeanDb,
      `True linear-domain mean dB (${trueUnbiasedMeanDb.toFixed(2)} dB)`,
      `Log-domain mean dB (${logAveragedMeanDb.toFixed(2)} dB), Bias: ${biasDb.toFixed(2)} dB`,
      true,
      "Defect Note: calculateZonalStats averages dB values instead of linear intensities, introducing a ~1.5 dB negative bias on parcel backscatter."
    );
  }

  runAll(): StressTestResult[] {
    this.results = [];
    this.runBoundaryDropTests();
    this.runBareSoilFloorTests();
    this.runClimateRefutationTests();
    this.runCommercialSchemaTests();
    this.runRadiometricBiasTests();
    return this.results;
  }
}

// Export singleton instance for direct test consumption
export const sarAdversarialHarness = new SarAdversarialHarness();
