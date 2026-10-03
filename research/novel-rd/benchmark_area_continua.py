"""
benchmark_area_continua.py
==========================
Agrostech Novel R&D Directions — Candidate 1 Benchmark & PoC Engine
Área Contínua Detection Across Property Boundaries under BCB Resolução CMN nº 5.267/2025.

Compares:
1. Baseline 1: Naive Single-CAR Clipping (Assumes cadastral borders are hard physical fences).
2. Baseline 2: Simple Spatial Buffering (Merges any adjacent touching CAR polygons).
3. Agrostech Multi-Feature Fusion Classifier:
   - S_pheno: Sentinel-2 NDVI Dynamic Time Warping (DTW) & Pearson cross-correlation.
   - S_event: Phenological milestone synchrony (planting & harvest inflections).
   - S_SAR: Sentinel-1 RTC dual-pol backscatter (VV, VH, CR) & InSAR coherence synchrony.
   - S_azimuth: Directional circular statistics of crop row orientations / RTK auto-steer passes.
   - S_perm: Boundary permeability & vegetative barrier contrast ratio.

Zero-dependency implementation: Python 3.12 + numpy + scipy + pandas + matplotlib + shapely.
"""

import argparse
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, box


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CARParcelPair:
    pair_id: str
    scenario: str
    ground_truth_continuous: int  # 1 = continuous, 0 = independent
    poly_a: Polygon
    poly_b: Polygon
    area_a_ha: float
    area_b_ha: float
    shared_boundary_length_m: float
    # Time-series data (T steps)
    timestamps_days: np.ndarray
    ndvi_a: np.ndarray
    ndvi_b: np.ndarray
    sar_vh_a: np.ndarray
    sar_vh_b: np.ndarray
    sar_vv_a: np.ndarray
    sar_vv_b: np.ndarray
    insar_coherence: np.ndarray  # Coherence delta across boundary
    # Directional kinematics
    row_azimuth_a_deg: float
    row_azimuth_b_deg: float
    row_concentration_a: float  # Circular order parameter R in [0, 1]
    row_concentration_b: float
    # Boundary structure
    barrier_fraction: float  # Fraction of boundary occupied by fence/trees [0, 1]
    barrier_contrast: float  # High-resolution gradient contrast ratio


# =============================================================================
# 1. SYNTHETIC CAR PAIR GENERATOR (Cerrado Operational Matrix)
# =============================================================================

class SyntheticCARPairGenerator:
    """
    Generates realistic paired CAR boundaries and remote sensing telemetry
    across four Cerrado grain production scenarios:
    1. True Continuous Operation (single lease/family, unified management) [y=1]
    2. Independent Neighboring Farms (same crop, staggered planting/azimuth) [y=0]
    3. Divergent Land Use (soybean vs pasture/eucalyptus) [y=0]
    4. Collusive/Fraudulent Split (PRONAF/PRONAMP credit ceiling evasion) [y=1]
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def _generate_phenology_curve(
        self,
        t: np.ndarray,
        t_plant: float,
        duration: float,
        ndvi_max: float = 0.85,
        ndvi_base: float = 0.18,
        noise_std: float = 0.02
    ) -> np.ndarray:
        """Double logistic vegetation index simulation."""
        k1 = 0.12  # Green-up slope
        k2 = 0.10  # Senescence slope
        t_peak = t_plant + duration * 0.55
        curve = ndvi_base + (ndvi_max - ndvi_base) * (
            (1.0 / (1.0 + np.exp(-k1 * (t - (t_plant + 15))))) -
            (1.0 / (1.0 + np.exp(-k2 * (t - (t_peak + 25)))))
        )
        noise = self.rng.normal(0.0, noise_std, size=len(t))
        return np.clip(curve + noise, 0.05, 0.95)

    def generate_pair(self, pair_idx: int, scenario: str) -> CARParcelPair:
        # 140-day observation window, sampled every 5 days (28 steps)
        t = np.arange(0, 140, 5, dtype=float)
        T = len(t)

        # Spatial geometry: Adjacent parcels along UTM-like coordinates
        w_a = self.rng.uniform(600.0, 1200.0)
        h_a = self.rng.uniform(800.0, 1500.0)
        w_b = self.rng.uniform(600.0, 1200.0)
        h_b = h_a  # Shared height creates realistic common boundary
        shared_length = h_a

        poly_a = box(0.0, 0.0, w_a, h_a)
        poly_b = box(w_a, 0.0, w_a + w_b, h_b)
        area_a = (w_a * h_a) / 10000.0
        area_b = (w_b * h_b) / 10000.0

        if scenario == "true_continuous":
            # Scenario 1: Same operator, same cultivar, planted within 24h
            gt = 1
            t_plant_a = self.rng.uniform(15.0, 30.0)
            t_plant_b = t_plant_a + self.rng.uniform(-1.0, 1.0)
            dur = self.rng.uniform(105.0, 115.0)

            ndvi_a = self._generate_phenology_curve(t, t_plant_a, dur, ndvi_max=0.86)
            ndvi_b = self._generate_phenology_curve(t, t_plant_b, dur, ndvi_max=0.85)

            # High SAR synchrony
            sar_vh_a = -16.0 + 7.0 * ndvi_a + self.rng.normal(0, 0.4, T)
            sar_vh_b = -16.0 + 7.0 * ndvi_b + self.rng.normal(0, 0.4, T)
            sar_vv_a = -10.0 + 4.0 * ndvi_a + self.rng.normal(0, 0.4, T)
            sar_vv_b = -10.0 + 4.0 * ndvi_b + self.rng.normal(0, 0.4, T)
            # Synchronous harvest decoherence
            insar_coh = np.full(T, 0.75) + self.rng.normal(0, 0.05, T)
            harvest_idx = np.where(t > (t_plant_a + dur - 10))[0]
            insar_coh[harvest_idx] = 0.20 + self.rng.normal(0, 0.03, len(harvest_idx))

            # Continuous tractor AB lines
            base_azimuth = self.rng.uniform(-80.0, 80.0)
            azimuth_a = base_azimuth
            azimuth_b = base_azimuth + self.rng.normal(0.0, 1.5)  # Near 0 deg delta
            R_a = self.rng.uniform(0.88, 0.96)
            R_b = self.rng.uniform(0.88, 0.96)

            barrier_frac = self.rng.uniform(0.0, 0.05)  # Open field
            barrier_contrast = self.rng.uniform(1.0, 1.15)

        elif scenario == "independent_same_crop":
            # Scenario 2: Different farmers, same crop, staggered by 15-25 days
            gt = 0
            t_plant_a = self.rng.uniform(15.0, 25.0)
            t_plant_b = t_plant_a + self.rng.uniform(15.0, 26.0)  # Significant lag
            dur_a = self.rng.uniform(105.0, 115.0)
            dur_b = self.rng.uniform(105.0, 115.0)

            ndvi_a = self._generate_phenology_curve(t, t_plant_a, dur_a, ndvi_max=0.84)
            ndvi_b = self._generate_phenology_curve(t, t_plant_b, dur_b, ndvi_max=0.81)

            sar_vh_a = -16.0 + 7.0 * ndvi_a + self.rng.normal(0, 0.5, T)
            sar_vh_b = -16.0 + 7.0 * ndvi_b + self.rng.normal(0, 0.5, T)
            sar_vv_a = -10.0 + 4.0 * ndvi_a + self.rng.normal(0, 0.5, T)
            sar_vv_b = -10.0 + 4.0 * ndvi_b + self.rng.normal(0, 0.5, T)
            insar_coh = self.rng.uniform(0.35, 0.65, T)

            # Different row directions
            azimuth_a = self.rng.uniform(-80.0, 80.0)
            azimuth_b = azimuth_a + self.rng.choice([-1, 1]) * self.rng.uniform(35.0, 85.0)
            if azimuth_b > 90.0:
                azimuth_b -= 180.0
            elif azimuth_b < -90.0:
                azimuth_b += 180.0
            R_a = self.rng.uniform(0.82, 0.94)
            R_b = self.rng.uniform(0.82, 0.94)

            barrier_frac = self.rng.uniform(0.65, 0.95)  # Fence + hedgerow
            barrier_contrast = self.rng.uniform(2.2, 4.0)

        elif scenario == "divergent_land_use":
            # Scenario 3: Soybean vs Pasture or Eucalyptus
            gt = 0
            t_plant_a = self.rng.uniform(15.0, 30.0)
            ndvi_a = self._generate_phenology_curve(t, t_plant_a, 110.0, ndvi_max=0.86)
            # Pasture: flat, noisy low/moderate NDVI (0.35 - 0.50)
            ndvi_b = 0.42 + 0.08 * np.sin(t / 25.0) + self.rng.normal(0, 0.03, T)
            ndvi_b = np.clip(ndvi_b, 0.20, 0.60)

            sar_vh_a = -16.0 + 7.0 * ndvi_a + self.rng.normal(0, 0.5, T)
            sar_vh_b = -14.5 + self.rng.normal(0, 0.8, T)  # Rough pasture backscatter
            sar_vv_a = -10.0 + 4.0 * ndvi_a + self.rng.normal(0, 0.5, T)
            sar_vv_b = -9.0 + self.rng.normal(0, 0.7, T)
            insar_coh = self.rng.uniform(0.20, 0.45, T)

            azimuth_a = self.rng.uniform(-80.0, 80.0)
            azimuth_b = self.rng.uniform(-90.0, 90.0)
            R_a = self.rng.uniform(0.85, 0.95)
            R_b = self.rng.uniform(0.15, 0.35)  # Unstructured grazing pasture

            barrier_frac = self.rng.uniform(0.80, 1.0)
            barrier_contrast = self.rng.uniform(2.8, 5.5)

        elif scenario == "collusive_fraudulent_split":
            # Scenario 4: Single farm split for credit ceiling bypass (subsidized credit evasion)
            gt = 1
            t_plant_a = self.rng.uniform(20.0, 30.0)
            t_plant_b = t_plant_a + self.rng.uniform(-0.5, 0.5)  # Identical timing
            dur = self.rng.uniform(108.0, 114.0)

            ndvi_a = self._generate_phenology_curve(t, t_plant_a, dur, ndvi_max=0.87)
            ndvi_b = self._generate_phenology_curve(t, t_plant_b, dur, ndvi_max=0.87)

            sar_vh_a = -16.0 + 7.0 * ndvi_a + self.rng.normal(0, 0.3, T)
            sar_vh_b = -16.0 + 7.0 * ndvi_b + self.rng.normal(0, 0.3, T)
            sar_vv_a = -10.0 + 4.0 * ndvi_a + self.rng.normal(0, 0.3, T)
            sar_vv_b = -10.0 + 4.0 * ndvi_b + self.rng.normal(0, 0.3, T)
            insar_coh = np.full(T, 0.78) + self.rng.normal(0, 0.04, T)
            harvest_idx = np.where(t > (t_plant_a + dur - 10))[0]
            insar_coh[harvest_idx] = 0.18 + self.rng.normal(0, 0.03, len(harvest_idx))

            base_azimuth = self.rng.uniform(-75.0, 75.0)
            azimuth_a = base_azimuth
            azimuth_b = base_azimuth + self.rng.normal(0.0, 0.8)
            R_a = self.rng.uniform(0.92, 0.98)
            R_b = self.rng.uniform(0.92, 0.98)

            barrier_frac = 0.0  # Zero physical fence; fictional cadastral line
            barrier_contrast = 1.0 + abs(self.rng.normal(0, 0.05))

        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        return CARParcelPair(
            pair_id=f"PAIR_{pair_idx:04d}",
            scenario=scenario,
            ground_truth_continuous=gt,
            poly_a=poly_a,
            poly_b=poly_b,
            area_a_ha=round(area_a, 2),
            area_b_ha=round(area_b, 2),
            shared_boundary_length_m=round(shared_length, 1),
            timestamps_days=t,
            ndvi_a=ndvi_a,
            ndvi_b=ndvi_b,
            sar_vh_a=sar_vh_a,
            sar_vh_b=sar_vh_b,
            sar_vv_a=sar_vv_a,
            sar_vv_b=sar_vv_b,
            insar_coherence=insar_coh,
            row_azimuth_a_deg=round(azimuth_a, 2),
            row_azimuth_b_deg=round(azimuth_b, 2),
            row_concentration_a=round(R_a, 3),
            row_concentration_b=round(R_b, 3),
            barrier_fraction=round(barrier_frac, 3),
            barrier_contrast=round(barrier_contrast, 3)
        )

    def generate_dataset(self, num_pairs: int = 200) -> List[CARParcelPair]:
        # Scenario distribution matching Cerrado reality:
        # 40% True Continuous, 30% Independent Same Crop, 20% Divergent, 10% Fraudulent Split
        n1 = int(round(num_pairs * 0.40))
        n2 = int(round(num_pairs * 0.30))
        n3 = int(round(num_pairs * 0.20))
        n4 = num_pairs - (n1 + n2 + n3)

        scenarios = (
            ["true_continuous"] * n1 +
            ["independent_same_crop"] * n2 +
            ["divergent_land_use"] * n3 +
            ["collusive_fraudulent_split"] * n4
        )
        self.rng.shuffle(scenarios)

        pairs = []
        for idx, sc in enumerate(scenarios, start=1):
            pairs.append(self.generate_pair(idx, sc))
        return pairs


# =============================================================================
# 2. CLASSIFIER IMPLEMENTATIONS
# =============================================================================

class BaselineSingleCARClassifier:
    """
    Baseline 1: Naive Single-CAR Clipping.
    Standard cadastral assumption: every CAR is an independent operational silo.
    Always predicts P(Continuous) = 0.0.
    """
    def predict_proba(self, pair: CARParcelPair) -> float:
        return 0.0

    def predict(self, pair: CARParcelPair, threshold: float = 0.5) -> int:
        return 0


class BaselineSpatialBufferClassifier:
    """
    Baseline 2: Spatial Buffering / Touching Neighbor Rule.
    Merges any adjacent parcels if they share a boundary > 10m.
    Because all candidate adjacent pairs share a boundary, it naively predicts P = 1.0.
    """
    def predict_proba(self, pair: CARParcelPair) -> float:
        if pair.shared_boundary_length_m >= 10.0:
            return 1.0
        return 0.0

    def predict(self, pair: CARParcelPair, threshold: float = 0.5) -> int:
        return 1 if self.predict_proba(pair) >= threshold else 0


class AgrostechMultiFeatureFusionClassifier:
    """
    Agrostech Patentable Engine: Multi-Feature Fusion under CMN Res. 5.267.
    Extracts 5 physical, spectral, and kinematic features:
    1. S_pheno: DTW distance and Pearson correlation on Sentinel-2 NDVI.
    2. S_event: Inflection-based milestone synchrony (planting and harvest).
    3. S_SAR: Sentinel-1 dual-pol correlation & InSAR coherence synchrony.
    4. S_azimuth: Circular statistics crop row axial alignment.
    5. S_perm: Boundary permeability and gradient contrast.
    """

    def __init__(
        self,
        weights: Tuple[float, float, float, float, float] = (2.2, 1.8, 2.5, 2.0, 1.5),
        bias: float = -4.5,
        threshold: float = 0.70
    ):
        self.weights = np.array(weights, dtype=float)
        self.bias = float(bias)
        self.threshold = float(threshold)

    @staticmethod
    def _compute_dtw_distance(v1: np.ndarray, v2: np.ndarray, max_window: int = 4) -> float:
        """Dynamic Time Warping with Sakoe-Chiba band."""
        n, m = len(v1), len(v2)
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0.0

        for i in range(1, n + 1):
            j_start = max(1, i - max_window)
            j_end = min(m + 1, i + max_window + 1)
            for j in range(j_start, j_end):
                cost = (v1[i - 1] - v2[j - 1]) ** 2
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i - 1, j],      # Insertion
                    dtw_matrix[i, j - 1],      # Deletion
                    dtw_matrix[i - 1, j - 1]   # Match
                )
        return float(np.sqrt(dtw_matrix[n, m]) / np.sqrt(n))

    @staticmethod
    def _extract_milestones(v: np.ndarray, t: np.ndarray) -> Tuple[float, float]:
        """Detects green-up date and harvest date via maximum derivative."""
        dv = np.gradient(v, t)
        t_green = float(t[np.argmax(dv)])
        t_harvest = float(t[np.argmin(dv)])
        return t_green, t_harvest

    def extract_features(self, pair: CARParcelPair) -> Dict[str, float]:
        # 1. Phenological Similarity (S_pheno)
        std_a = np.std(pair.ndvi_a)
        std_b = np.std(pair.ndvi_b)
        if std_a > 1e-4 and std_b > 1e-4:
            rho_pheno = float(np.corrcoef(pair.ndvi_a, pair.ndvi_b)[0, 1])
        else:
            rho_pheno = 0.0
        rho_pheno = max(-1.0, min(1.0, rho_pheno))

        d_dtw = self._compute_dtw_distance(pair.ndvi_a, pair.ndvi_b, max_window=4)
        s_pheno = 0.5 * (1.0 + rho_pheno) * math.exp(- (d_dtw ** 2) / 0.18)
        s_pheno = max(0.0, min(1.0, s_pheno))

        # 2. Milestone Synchrony (S_event)
        t_green_a, t_harvest_a = self._extract_milestones(pair.ndvi_a, pair.timestamps_days)
        t_green_b, t_harvest_b = self._extract_milestones(pair.ndvi_b, pair.timestamps_days)
        dt_plant = abs(t_green_a - t_green_b)
        dt_harvest = abs(t_harvest_a - t_harvest_b)
        tau_sync = 5.0  # days
        s_event = math.exp(- (dt_plant**2 + dt_harvest**2) / (2.0 * (tau_sync ** 2)))
        s_event = max(0.0, min(1.0, s_event))

        # 3. SAR Backscatter & InSAR Coherence (S_SAR)
        if np.std(pair.sar_vh_a) > 1e-4 and np.std(pair.sar_vh_b) > 1e-4:
            rho_vh = float(np.corrcoef(pair.sar_vh_a, pair.sar_vh_b)[0, 1])
        else:
            rho_vh = 0.0

        cr_a = pair.sar_vh_a - pair.sar_vv_a
        cr_b = pair.sar_vh_b - pair.sar_vv_b
        if np.std(cr_a) > 1e-4 and np.std(cr_b) > 1e-4:
            rho_cr = float(np.corrcoef(cr_a, cr_b)[0, 1])
        else:
            rho_cr = 0.0

        rho_sar = 0.5 * (max(0.0, rho_vh) + max(0.0, rho_cr))
        # Mean InSAR coherence across boundary
        mean_coh = float(np.mean(pair.insar_coherence))
        s_sar = 0.5 * (rho_sar + mean_coh)
        s_sar = max(0.0, min(1.0, s_sar))

        # 4. Crop Row Azimuth Alignment (S_azimuth)
        # Circular axial difference (period pi radians / 180 degrees)
        theta_a_rad = math.radians(pair.row_azimuth_a_deg)
        theta_b_rad = math.radians(pair.row_azimuth_b_deg)
        d_theta = min(abs(theta_a_rad - theta_b_rad), math.pi - abs(theta_a_rad - theta_b_rad))
        s_azimuth = (math.cos(d_theta) ** 2) * math.sqrt(max(0.0, pair.row_concentration_a * pair.row_concentration_b))
        s_azimuth = max(0.0, min(1.0, s_azimuth))

        # 5. Boundary Permeability (S_perm)
        delta_contrast = max(0.0, pair.barrier_contrast - 1.0)
        s_perm_contrast = math.exp(- (delta_contrast ** 2) / (2.0 * (0.5 ** 2)))
        s_perm_geom = 1.0 - pair.barrier_fraction
        s_perm = 0.5 * (s_perm_contrast + s_perm_geom)
        s_perm = max(0.0, min(1.0, s_perm))

        return {
            "S_pheno": s_pheno,
            "S_event": s_event,
            "S_sar": s_sar,
            "S_azimuth": s_azimuth,
            "S_perm": s_perm
        }

    def predict_proba(self, pair: CARParcelPair) -> float:
        feats = self.extract_features(pair)
        x = np.array([
            feats["S_pheno"],
            feats["S_event"],
            feats["S_sar"],
            feats["S_azimuth"],
            feats["S_perm"]
        ], dtype=float)
        z = float(np.dot(self.weights, x) + self.bias)
        # Numerically stable sigmoid
        p = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))
        return p

    def predict(self, pair: CARParcelPair) -> int:
        return 1 if self.predict_proba(pair) >= self.threshold else 0


# =============================================================================
# 3. BENCHMARK EVALUATOR & METRICS ENGINE
# =============================================================================

class AreaContinuaBenchmarkEvaluator:
    """
    Evaluates Agrostech Fusion vs Baselines across standard statistical & GIS metrics:
    - ROC-AUC
    - Brier Score (Probabilistic Calibration)
    - False Merge Rate (FMR / Type I error)
    - False Split Rate (FSR / Type II error)
    - Area Detection Accuracy (Jaccard IoU)
    - Scenario-stratified breakdown
    """

    @staticmethod
    def compute_roc_curve(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Calculates FPR, TPR points and Area Under the ROC Curve (AUC)."""
        thresholds = np.linspace(0.0, 1.0, 201)
        fpr_list, tpr_list = [], []

        pos_count = np.sum(y_true == 1)
        neg_count = np.sum(y_true == 0)

        for th in thresholds:
            y_pred = (y_score >= th).astype(int)
            tp = np.sum((y_pred == 1) & (y_true == 1))
            fp = np.sum((y_pred == 1) & (y_true == 0))
            tpr = tp / pos_count if pos_count > 0 else 0.0
            fpr = fp / neg_count if neg_count > 0 else 0.0
            fpr_list.append(fpr)
            tpr_list.append(tpr)

        fpr_list.append(0.0)
        tpr_list.append(0.0)
        fpr_list.append(1.0)
        tpr_list.append(1.0)

        fpr_arr = np.array(fpr_list)
        tpr_arr = np.array(tpr_list)

        # Sort by FPR ascending for trapezoidal integration
        order = np.lexsort((tpr_arr, fpr_arr))
        fpr_sorted = fpr_arr[order]
        tpr_sorted = tpr_arr[order]
        # Remove duplicate FPR points keeping max TPR for standard step ROC
        unique_fpr, unique_idx = np.unique(fpr_sorted, return_index=True)
        # Trapezoidal rule compatible with NumPy 2.0+ and legacy NumPy
        auc = float(np.sum(0.5 * (tpr_sorted[1:] + tpr_sorted[:-1]) * np.diff(fpr_sorted)))
        auc = max(0.5, min(1.0, auc)) if np.all(y_score == y_score[0]) else auc
        return fpr_sorted, tpr_sorted, abs(auc)

    @staticmethod
    def compute_brier_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
        return float(np.mean((y_score - y_true) ** 2))

    @staticmethod
    def compute_iou(pair: CARParcelPair, predicted_merge: int) -> float:
        """
        Calculates Jaccard Index of Detected Continuous Management Area.
        If ground truth is continuous (y=1):
          - If correctly merged, IoU = 1.0 (Union matches true continuous unit).
          - If falsely split, detected unit is only parcel A, IoU = Area(A)/Area(A U B) ~ 0.50.
        If ground truth is independent (y=0):
          - If correctly kept separate, IoU = 1.0.
          - If falsely merged, IoU = Area(A)/Area(A U B) ~ 0.50.
        """
        gt = pair.ground_truth_continuous
        area_a = pair.area_a_ha
        area_b = pair.area_b_ha
        area_union = area_a + area_b
        ratio = area_a / area_union

        if gt == 1:
            return 1.0 if predicted_merge == 1 else ratio
        else:
            return 1.0 if predicted_merge == 0 else ratio

    def evaluate_model(
        self,
        name: str,
        predict_fn,
        predict_proba_fn,
        pairs: List[CARParcelPair]
    ) -> Dict[str, Any]:
        y_true = np.array([p.ground_truth_continuous for p in pairs], dtype=int)
        y_score = np.array([predict_proba_fn(p) for p in pairs], dtype=float)
        y_pred = np.array([predict_fn(p) for p in pairs], dtype=int)

        tp = int(np.sum((y_pred == 1) & (y_true == 1)))
        fp = int(np.sum((y_pred == 1) & (y_true == 0)))
        tn = int(np.sum((y_pred == 0) & (y_true == 0)))
        fn = int(np.sum((y_pred == 0) & (y_true == 1)))

        pos = tp + fn
        neg = tn + fp

        fmr = (fp / neg) * 100.0 if neg > 0 else 0.0  # False Merge Rate / FPR (%)
        fsr = (fn / pos) * 100.0 if pos > 0 else 0.0  # False Split Rate / FNR (%)
        accuracy = ((tp + tn) / len(pairs)) * 100.0
        brier = self.compute_brier_score(y_true, y_score)
        fpr_curve, tpr_curve, roc_auc = self.compute_roc_curve(y_true, y_score)

        ious = [self.compute_iou(p, y_pred[i]) for i, p in enumerate(pairs)]
        mean_iou = float(np.mean(ious)) * 100.0

        # Scenario breakdown
        scenario_acc = {}
        for sc in ["true_continuous", "independent_same_crop", "divergent_land_use", "collusive_fraudulent_split"]:
            sc_idx = [i for i, p in enumerate(pairs) if p.scenario == sc]
            if sc_idx:
                sc_correct = np.sum(y_pred[sc_idx] == y_true[sc_idx])
                scenario_acc[sc] = round(float(sc_correct / len(sc_idx)) * 100.0, 1)

        return {
            "model_name": name,
            "roc_auc": round(roc_auc, 4),
            "brier_score": round(brier, 4),
            "false_merge_rate_pct": round(fmr, 2),
            "false_split_rate_pct": round(fsr, 2),
            "accuracy_pct": round(accuracy, 2),
            "mean_jaccard_iou_pct": round(mean_iou, 2),
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn
            },
            "scenario_accuracy_pct": scenario_acc,
            "_fpr_curve": fpr_curve,
            "_tpr_curve": tpr_curve,
            "_y_score": y_score,
            "_y_true": y_true
        }


# =============================================================================
# 4. PLOTTING & VISUALIZATION ARTIFACTS
# =============================================================================

def render_benchmark_plots(
    eval_results: Dict[str, Dict[str, Any]],
    fusion_features_df: pd.DataFrame,
    output_path: str
):
    """
    Renders 4-panel publication-grade figure:
    1. ROC Curves (Agrostech vs Baselines)
    2. Probability Calibration (Reliability Diagram)
    3. Multi-Feature Correlation Matrix
    4. Model Metrics & Confusion Matrix Comparison
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    plt.subplots_adjust(hspace=0.32, wspace=0.28)

    # 1. ROC Curves
    ax1 = axes[0, 0]
    colors = {"Agrostech Multi-Feature Fusion": "#1b5e20", "Naive Spatial Buffer": "#e65100", "Naive Single-CAR": "#b71c1c"}
    styles = {"Agrostech Multi-Feature Fusion": "-", "Naive Spatial Buffer": "--", "Naive Single-CAR": ":"}

    for name, res in eval_results.items():
        fpr = res["_fpr_curve"]
        tpr = res["_tpr_curve"]
        auc = res["roc_auc"]
        ax1.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=colors.get(name, "blue"),
                 linestyle=styles.get(name, "-"), linewidth=2.4)

    ax1.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Chance Level (AUC = 0.500)")
    ax1.set_xlim([-0.02, 1.02])
    ax1.set_ylim([-0.02, 1.05])
    ax1.set_xlabel("False Positive Rate (False Merge Rate)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("True Positive Rate (Sensitivity)", fontsize=11, fontweight="bold")
    ax1.set_title("A. ROC Curve Comparison (CMN 5.267 / Área Contínua)", fontsize=12, fontweight="bold")
    ax1.legend(loc="lower right", frameon=True, fontsize=9)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # 2. Probability Calibration (Reliability Diagram)
    ax2 = axes[0, 1]
    y_true = eval_results["Agrostech Multi-Feature Fusion"]["_y_true"]
    y_score = eval_results["Agrostech Multi-Feature Fusion"]["_y_score"]

    bins = np.linspace(0.0, 1.0, 11)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0
    bin_empirical = []
    bin_counts = []

    for i in range(len(bins) - 1):
        idx = np.where((y_score >= bins[i]) & (y_score < bins[i+1]))[0]
        if len(idx) > 0:
            bin_empirical.append(np.mean(y_true[idx]))
            bin_counts.append(len(idx))
        else:
            bin_empirical.append(np.nan)
            bin_counts.append(0)

    ax2.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect Calibration")
    ax2.plot(bin_centers, bin_empirical, "s-", color="#1b5e20", linewidth=2.2, markersize=7,
             label=f"Agrostech Fusion (Brier = {eval_results['Agrostech Multi-Feature Fusion']['brier_score']:.4f})")
    ax2.bar(bin_centers, np.array(bin_counts) / len(y_score), width=0.07, alpha=0.25, color="#2e7d32", label="Sample Density")
    ax2.set_xlabel("Predicted Probability P(Continuous Operation)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Empirical Frequency of True Continuous", fontsize=11, fontweight="bold")
    ax2.set_title("B. Probabilistic Reliability & Brier Calibration", fontsize=12, fontweight="bold")
    ax2.legend(loc="upper left", frameon=True, fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    # 3. Multi-Feature Correlation Matrix
    ax3 = axes[1, 0]
    corr_matrix = fusion_features_df.corr().values
    feature_names = ["S_pheno", "S_event", "S_SAR", "S_azimuth", "S_perm", "GroundTruth"]
    im = ax3.imshow(corr_matrix, cmap="RdYlGn", vmin=-0.2, vmax=1.0)
    ax3.set_xticks(range(len(feature_names)))
    ax3.set_yticks(range(len(feature_names)))
    ax3.set_xticklabels(feature_names, rotation=35, ha="right", fontsize=9, fontweight="bold")
    ax3.set_yticklabels(feature_names, fontsize=9, fontweight="bold")
    ax3.set_title("C. Multi-Feature Correlation with Ground Truth", fontsize=12, fontweight="bold")

    for i in range(len(feature_names)):
        for j in range(len(feature_names)):
            val = corr_matrix[i, j]
            text_color = "white" if abs(val) > 0.65 else "black"
            ax3.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8.5, fontweight="bold")
    fig.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)

    # 4. Error Rates & IoU Performance Summary
    ax4 = axes[1, 1]
    models = ["Agrostech Fusion", "Naive Spatial Buffer", "Naive Single-CAR"]
    fmr_vals = [
        eval_results["Agrostech Multi-Feature Fusion"]["false_merge_rate_pct"],
        eval_results["Naive Spatial Buffer"]["false_merge_rate_pct"],
        eval_results["Naive Single-CAR"]["false_merge_rate_pct"]
    ]
    fsr_vals = [
        eval_results["Agrostech Multi-Feature Fusion"]["false_split_rate_pct"],
        eval_results["Naive Spatial Buffer"]["false_split_rate_pct"],
        eval_results["Naive Single-CAR"]["false_split_rate_pct"]
    ]
    iou_vals = [
        eval_results["Agrostech Multi-Feature Fusion"]["mean_jaccard_iou_pct"],
        eval_results["Naive Spatial Buffer"]["mean_jaccard_iou_pct"],
        eval_results["Naive Single-CAR"]["mean_jaccard_iou_pct"]
    ]

    x = np.arange(len(models))
    width = 0.26
    b1 = ax4.bar(x - width, fmr_vals, width, label="False Merge Rate (Type I) %", color="#d32f2f", alpha=0.85)
    b2 = ax4.bar(x, fsr_vals, width, label="False Split Rate (Type II) %", color="#f57c00", alpha=0.85)
    b3 = ax4.bar(x + width, iou_vals, width, label="Mean Jaccard IoU %", color="#388e3c", alpha=0.85)

    ax4.set_xticks(x)
    ax4.set_xticklabels(models, fontsize=9.5, fontweight="bold")
    ax4.set_ylabel("Metric Percentage (%)", fontsize=11, fontweight="bold")
    ax4.set_title("D. Error Rates (FMR/FSR) & Area IoU Accuracy", fontsize=12, fontweight="bold")
    ax4.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True, fontsize=8.5)
    ax4.grid(True, linestyle=":", alpha=0.6, axis="y")

    # Value labels
    for bar in list(b1) + list(b2) + list(b3):
        h = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=7.5)

    plt.suptitle("AGROSTECH R&D BENCHMARK — ÁREA CONTÍNUA MULTI-FEATURE FUSION\nEvaluated on N=200 Cerrado CAR Boundary Pairs under BCB Res. CMN nº 5.267/2025",
                 fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Benchmark visualization plot saved to: {output_path}")


# =============================================================================
# 5. MAIN EXECUTION PIPELINE
# =============================================================================

def run_area_continua_benchmark(
    num_pairs: int = 200,
    seed: int = 42,
    plot: bool = True,
    output_json: str = "results_area_continua.json",
    output_png: str = "benchmark_area_continua.png"
) -> Dict[str, Any]:
    print(f"[BENCHMARK 1] Generating {num_pairs} synthetic Cerrado CAR boundary pairs (seed={seed})...")
    generator = SyntheticCARPairGenerator(seed=seed)
    pairs = generator.generate_dataset(num_pairs=num_pairs)

    print("[BENCHMARK 1] Initializing classifiers...")
    model_single = BaselineSingleCARClassifier()
    model_buffer = BaselineSpatialBufferClassifier()
    model_agrostech = AgrostechMultiFeatureFusionClassifier()

    evaluator = AreaContinuaBenchmarkEvaluator()

    print("[BENCHMARK 1] Evaluating Baseline 1: Naive Single-CAR Clipping...")
    res_single = evaluator.evaluate_model(
        "Naive Single-CAR",
        model_single.predict,
        model_single.predict_proba,
        pairs
    )

    print("[BENCHMARK 1] Evaluating Baseline 2: Naive Spatial Buffering...")
    res_buffer = evaluator.evaluate_model(
        "Naive Spatial Buffer",
        model_buffer.predict,
        model_buffer.predict_proba,
        pairs
    )

    print("[BENCHMARK 1] Evaluating Agrostech Multi-Feature Fusion...")
    res_agrostech = evaluator.evaluate_model(
        "Agrostech Multi-Feature Fusion",
        model_agrostech.predict,
        model_agrostech.predict_proba,
        pairs
    )

    # Feature correlation DataFrame for plotting & analytics
    feature_records = []
    for p in pairs:
        f = model_agrostech.extract_features(p)
        f["GroundTruth"] = float(p.ground_truth_continuous)
        feature_records.append(f)
    features_df = pd.DataFrame(feature_records)

    eval_results = {
        "Agrostech Multi-Feature Fusion": res_agrostech,
        "Naive Spatial Buffer": res_buffer,
        "Naive Single-CAR": res_single
    }

    # Clean non-serializable arrays for JSON output
    clean_results = {
        "benchmark_name": "Area Continua Multi-Feature Fusion",
        "sample_size_pairs": num_pairs,
        "random_seed": seed,
        "models": {}
    }
    for name, res in eval_results.items():
        clean_res = {k: v for k, v in res.items() if not k.startswith("_")}
        clean_results["models"][name] = clean_res

    # Save JSON results
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(clean_results, f, indent=2)
    print(f"[SUCCESS] Benchmark metrics exported to: {output_json}")

    # Render plots
    if plot:
        render_benchmark_plots(eval_results, features_df, output_png)

    # Print summary console table
    print("\n" + "=" * 90)
    print(f"{'Model':<32} | {'ROC-AUC':<8} | {'Brier':<8} | {'FMR %':<8} | {'FSR %':<8} | {'IoU %':<8} | {'Acc %':<8}")
    print("-" * 90)
    for name, m in clean_results["models"].items():
        print(f"{name:<32} | {m['roc_auc']:<8.4f} | {m['brier_score']:<8.4f} | {m['false_merge_rate_pct']:<8.2f} | {m['false_split_rate_pct']:<8.2f} | {m['mean_jaccard_iou_pct']:<8.2f} | {m['accuracy_pct']:<8.2f}")
    print("=" * 90 + "\n")

    return clean_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agrostech Área Contínua Multi-Feature Fusion Benchmark")
    parser.add_argument("--num-pairs", type=int, default=200, help="Number of synthetic CAR pairs to evaluate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--plot", action="store_true", default=True, help="Render publication figures")
    parser.add_argument("--output-json", type=str, default="results_area_continua.json", help="Output JSON path")
    parser.add_argument("--output-png", type=str, default="benchmark_area_continua.png", help="Output PNG path")
    args = parser.parse_args()

    run_area_continua_benchmark(
        num_pairs=args.num_pairs,
        seed=args.seed,
        plot=args.plot,
        output_json=args.output_json,
        output_png=args.output_png
    )
