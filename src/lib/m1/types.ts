/**
 * Model M1 Net Plantable Area (Área Útil Líquida - AUL) Types
 * Compliant with Law 12.651/2012 (Código Florestal) and BCB Resolução CMN nº 5.267/2025 (MCR 2-9).
 */

export interface ModelM1Input {
  grossAreaHa: number;
  appAreaHa: number;
  legalReserveAreaHa: number;
  rlInAppAreaHa?: number;
  easementsHa?: number;
  restrictedUseHa?: number;
  disputedAreaHa?: number;
  publicOverlapsHa?: number;
  embargoesHa?: number;
  consolidatedUseHa?: number;
  appRestorationHa?: number;
  rlRestorationHa?: number;
  carStatus?: string;
  hasIndigenousOverlap?: boolean;
  hasConservationUnitOverlap?: boolean;
}

export interface DeductionsBreakdown {
  appHa: number;
  legalReserveHa: number;
  rlInAppOverlapHa: number;
  netConservationHa: number;
  easementsHa: number;
  restrictedUseHa: number;
  disputedAreaHa: number;
  publicConflictsHa: number;
  embargoesHa: number;
  totalDeductionsHa: number;
  [key: string]: number;
}

export interface ModelM1Output {
  grossAreaHa: number;
  netPlantableAreaHa: number;
  preservationRatio: number; // Ratio of total conservation to gross area (0.0 to 1.0)
  netArableRatio: number; // Ratio of plantable area to gross area (0.0 to 1.0)
  deductionsBreakdown: DeductionsBreakdown;
  isEligibleForCredit: boolean;
  continuousMonitoringMandatory: boolean; // True if > 300 ha under CMN 5.267/2025
  creditBlockReasons: string[];
  recommendations: string[];
}
