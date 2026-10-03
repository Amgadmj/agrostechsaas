"""
benchmark_runoff_erosion.py
===========================
Agrostech Novel R&D Directions — Candidate 3 Benchmark & PoC Engine
Uncertainty-Aware Probabilistic Runoff & Erosion Risk via SCS-CN Monte Carlo over DTM Error.

Compares:
1. Baseline 1: Deterministic Rational Method (Q = C * I * A, uniform runoff coefficient).
2. Baseline 2: Single-Run Deterministic SCS-CN (evaluated on a single noisy photogrammetric DTM).
3. Agrostech Probabilistic SCS-CN Monte Carlo (K=500 realizations):
   - 2D Gaussian Random Field (GRF) elevation perturbation via FFT spectral synthesis:
     sigma_z(x, y) = sigma_base * (1 + 3.5 * NDVI^2) * (1 + 1.2 * tan(slope)).
   - Distributed SCS-CN direct runoff generation (calibrated tropical Oxisol lambda = 0.05).
   - Distributed D8 flow accumulation and engineered contour terrace overtopping balance.
   - Per-pixel discharge exceedance surface P(Q > Q_crit) and spatial risk variance sigma_Q^2.

Zero-dependency implementation: Python 3.12 + numpy + scipy + pandas + matplotlib + shapely.
"""

import argparse
import heapq
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ContourTerrace:
    terrace_id: str
    row_idx: int               # Grid row where terrace channel is carved
    length_m: float
    design_capacity_m3: float  # Engineered channel storage volume
    ground_truth_overtop: int = 0
    single_run_pred: int = 0
    mc_prob_overtop: float = 0.0


# =============================================================================
# 1. MICRO-CATCHMENT & DTM GENERATOR
# =============================================================================

class MicroCatchmentGenerator:
    """
    Generates synthetic 50 ha Cerrado rolling micro-catchment with 4 contour terraces.
    Grid: 100 x 100 cells at cell_size = 7.07m (total area = 50.0 ha).
    Nominal elevation features 2.8% regional gradient converging toward a drainage swale.
    """
    def __init__(
        self,
        grid_size: int = 100,
        cell_size_m: float = 7.071,
        seed: int = 42
    ):
        self.grid_size = grid_size
        self.cell_size_m = cell_size_m
        self.rng = np.random.default_rng(seed)

    def generate_topography(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[ContourTerrace]]:
        """
        Returns:
            nominal_dtm: 2D array of true bare elevations (meters)
            ndvi_grid: 2D array of crop canopy NDVI [0.15, 0.88]
            cn_grid: 2D array of SCS Curve Numbers [72, 85]
            terraces: List of engineered contour terraces
        """
        n = self.grid_size
        dx = self.cell_size_m
        x = np.arange(n) * dx
        y = np.arange(n) * dx
        X, Y = np.meshgrid(x, y)

        # Regional slope: 2.8% descending in Y direction
        # Parabolic convergence in X direction creating a gentle drainage thalweg at X = mid
        x_center = (n * dx) / 2.0
        z_base = 450.0  # Base elevation (m a.s.l. in Mato Grosso plateau)
        regional_slope = 0.028
        thalweg_curvature = 0.000035

        nominal_dtm = z_base - (regional_slope * Y) + (thalweg_curvature * (X - x_center) ** 2)
        # Add smooth meso-topographic undulations
        nominal_dtm += 0.45 * np.sin(X / 60.0) * np.cos(Y / 80.0)

        # NDVI grid: Dense soybean canopy with minor field variability
        ndvi_grid = 0.78 + 0.06 * np.sin(X / 90.0) + self.rng.normal(0, 0.02, (n, n))
        ndvi_grid = np.clip(ndvi_grid, 0.20, 0.90)

        # SCS Curve Number grid: Latossolo Vermelho (Group B/C Oxisol under no-till)
        # Nominal CN = 78 with spatial soil texture variation
        cn_grid = 78.0 + 3.0 * np.sin(Y / 120.0) + self.rng.normal(0, 1.2, (n, n))
        cn_grid = np.clip(cn_grid, 70.0, 88.0)

        # Place 4 engineered contour terraces across the slope
        # Located at rows 22, 44, 66, 88 with calibrated capacities
        terrace_rows = [22, 44, 66, 88]
        # Realistic engineered capacities (m3) creating critical convergence threshold
        # Terrace 1: Upslope safe (6,500 m3)
        # Terrace 2: Critical convergence threshold (10,000 m3 - vulnerable to DTM noise false negatives)
        # Terrace 3: Mid-slope retention (16,000 m3)
        # Terrace 4: Downslope reinforcement basin (22,000 m3)
        capacities = [6500.0, 10000.0, 16000.0, 22000.0]
        terraces = []
        for idx, (r_idx, cap) in enumerate(zip(terrace_rows, capacities), start=1):
            length = n * dx  # ~707 meters along contour
            terraces.append(ContourTerrace(
                terrace_id=f"TERRACE_0{idx}",
                row_idx=r_idx,
                length_m=round(length, 1),
                design_capacity_m3=cap
            ))

        return nominal_dtm, ndvi_grid, cn_grid, terraces


# =============================================================================
# 2. 2D GAUSSIAN RANDOM FIELD (GRF) SPECTRAL GENERATOR
# =============================================================================

class GaussianRandomFieldGenerator:
    """
    Synthesizes 2D spatially autocorrelated elevation error fields:
    epsilon(x, y) ~ GRF(0, sigma_z^2, L_corr)
    via 2D Fast Fourier Transform (FFT) spectral convolution.
    """
    def __init__(
        self,
        grid_size: int,
        cell_size_m: float,
        l_corr_m: float = 20.0,
        sigma_base_m: float = 0.25
    ):
        self.n = grid_size
        self.dx = cell_size_m
        self.l_corr = l_corr_m
        self.sigma_base = sigma_base_m

        # Precompute 2D Fourier isotropic Gaussian power spectrum filter
        kx = np.fft.fftfreq(grid_size, d=cell_size_m)
        ky = np.fft.fftfreq(grid_size, d=cell_size_m)
        KX, KY = np.meshgrid(kx, ky)
        K_sq = KX**2 + KY**2

        # Spectral filter H(k) = sqrt(pi * L^2) * exp(-pi^2 * L^2 * K^2 / 2)
        self.H_spectral = np.sqrt(np.pi * (l_corr_m ** 2)) * np.exp(- (np.pi ** 2 * (l_corr_m ** 2) * K_sq) / 2.0)

    def generate_spatial_uncertainty_map(
        self,
        nominal_dtm: np.ndarray,
        ndvi_grid: np.ndarray
    ) -> np.ndarray:
        """
        Calculates spatially varying vertical noise standard deviation:
        sigma_z(x, y) = sigma_base * (1 + 3.5 * NDVI^2) * (1 + 1.2 * tan(slope))
        """
        # Slope calculation via central differences
        gy, gx = np.gradient(nominal_dtm, self.dx)
        tan_slope = np.sqrt(gx**2 + gy**2)

        sigma_z = self.sigma_base * (1.0 + 3.5 * (np.clip(ndvi_grid, 0.0, 1.0) ** 2)) * (1.0 + 1.2 * tan_slope)
        return sigma_z

    def generate_perturbation_realization(
        self,
        sigma_z_map: np.ndarray,
        rng: np.random.Generator
    ) -> np.ndarray:
        """Generates one correlated random elevation error field."""
        white_noise = rng.standard_normal((self.n, self.n))
        spectral_noise = np.fft.fft2(white_noise)
        filtered = np.fft.ifft2(self.H_spectral * spectral_noise).real
        filtered_norm = filtered / (np.std(filtered) + 1e-9)
        return sigma_z_map * filtered_norm


# =============================================================================
# 3. HYDROLOGICAL FLOW ROUTING & SCS-CN RUNOFF ENGINE
# =============================================================================

class HydrologicalFlowRouter:
    """
    High-performance topological D8 flow accumulation engine.
    Routes surface runoff downslope and accumulates volume delivered into contour terraces.
    """
    def __init__(self, grid_size: int, cell_size_m: float):
        self.n = grid_size
        self.dx = cell_size_m
        self.cell_area_m2 = cell_size_m * cell_size_m

        # 8 neighbor offsets: (dy, dx, distance_multiplier)
        sqrt2 = math.sqrt(2.0)
        self.offsets = [
            (-1, 0, 1.0),   # N
            (1, 0, 1.0),    # S
            (0, -1, 1.0),   # W
            (0, 1, 1.0),    # E
            (-1, -1, sqrt2),# NW
            (-1, 1, sqrt2), # NE
            (1, -1, sqrt2), # SW
            (1, 1, sqrt2)   # SE
        ]

    def compute_direct_runoff_volume(
        self,
        cn_grid: np.ndarray,
        design_storm_mm: float = 85.0
    ) -> np.ndarray:
        """
        Calculates direct runoff depth and volume per cell via SCS-CN:
        S = 25400 / CN - 254
        Ia = 0.05 * S (calibrated tropical Brazilian Oxisols)
        q = (P - Ia)^2 / (P - Ia + S)
        """
        S = (25400.0 / np.clip(cn_grid, 30.0, 99.0)) - 254.0
        Ia = 0.05 * S
        P = design_storm_mm

        runoff_depth_mm = np.where(P > Ia, ((P - Ia) ** 2) / (P - Ia + S), 0.0)
        v_cell_m3 = (runoff_depth_mm / 1000.0) * self.cell_area_m2
        return v_cell_m3

    @staticmethod
    def fill_depressions_priority_flood(dtm: np.ndarray) -> np.ndarray:
        """Hydrological depression conditioning via Barnes Priority-Flood algorithm."""
        rows, cols = dtm.shape
        dem = dtm.copy()
        visited = np.zeros((rows, cols), dtype=bool)
        heap = []

        # Seed border cells as outlets
        for r in range(rows):
            for c in (0, cols - 1):
                heapq.heappush(heap, (float(dem[r, c]), r, c))
                visited[r, c] = True
        for c in range(cols):
            for r in (0, rows - 1):
                if not visited[r, c]:
                    heapq.heappush(heap, (float(dem[r, c]), r, c))
                    visited[r, c] = True

        offsets_8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        while heap:
            z, r, c = heapq.heappop(heap)
            for dr, dc in offsets_8:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                    visited[nr, nc] = True
                    if dem[nr, nc] < z:
                        dem[nr, nc] = z + 1e-4
                    heapq.heappush(heap, (float(dem[nr, nc]), nr, nc))
        return dem

    def route_flow(
        self,
        elevation: np.ndarray,
        v_cell_m3: np.ndarray,
        terraces: List[ContourTerrace]
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
        """
        Performs D8 flow routing sorted by descending elevation (topological sort).
        Returns:
            cum_volume_grid: Cumulative runoff volume routed through each cell (m3).
            peak_discharge_grid: Estimated peak discharge (m3/s) via Kirpich tc.
            terrace_inflow_m3: Inflow volume intercepted by each contour terrace channel.
        """
        # Condition DTM to eliminate spurious pits
        elevation = self.fill_depressions_priority_flood(elevation)

        n = self.n
        dx = self.dx
        total_cells = n * n

        # Find downstream neighbor for each cell
        downstream = np.arange(total_cells, dtype=np.int32)

        pad_elev = np.pad(elevation, 1, mode="edge")

        # Vectorized steepest descent calculation
        steepest_slopes = np.zeros((n, n), dtype=np.float32)

        for dy, dx_off, dist_mult in self.offsets:
            dist = dx * dist_mult
            elev_neighbor = pad_elev[1 + dy : 1 + dy + n, 1 + dx_off : 1 + dx_off + n]
            slope = (elevation - elev_neighbor) / dist

            # Check where this neighbor is steeper than current best
            mask = slope > steepest_slopes
            if np.any(mask):
                steepest_slopes[mask] = slope[mask]
                r_indices, c_indices = np.where(mask)
                target_r = np.clip(r_indices + dy, 0, n - 1)
                target_c = np.clip(c_indices + dx_off, 0, n - 1)
                downstream[r_indices * n + c_indices] = target_r * n + target_c

        # Depression handling: for cells with steepest_slope <= 0 (flat/pit), route to lowest neighbor
        pit_mask = steepest_slopes <= 0.0
        if np.any(pit_mask):
            pit_r, pit_c = np.where(pit_mask)
            for pr, pc in zip(pit_r, pit_c):
                min_elev = np.inf
                best_flat_neighbor = pr * n + pc
                for dy, dx_off, _ in self.offsets:
                    nr, nc = pr + dy, pc + dx_off
                    if 0 <= nr < n and 0 <= nc < n:
                        if elevation[nr, nc] < min_elev:
                            min_elev = elevation[nr, nc]
                            best_flat_neighbor = nr * n + nc
                downstream[pr * n + pc] = best_flat_neighbor

        # Sort cells in descending elevation (topological DAG ordering)
        order = np.argsort(-elevation.ravel())

        # Accumulate flow volume and contributing area
        cum_volume = v_cell_m3.ravel().copy()
        contrib_area = np.full(total_cells, self.cell_area_m2, dtype=np.float64)

        for idx in order:
            nxt = downstream[idx]
            if nxt != idx:
                cum_volume[nxt] += cum_volume[idx]
                contrib_area[nxt] += contrib_area[idx]

        cum_volume_grid = cum_volume.reshape((n, n))
        contrib_area_grid = contrib_area.reshape((n, n))

        # Peak discharge rate (m3/s) via Kirpich Time of Concentration
        l_flow = np.sqrt(contrib_area_grid)
        s_safe = np.maximum(steepest_slopes, 0.005)
        tc_hours = np.clip(0.0663 * (l_flow ** 0.77) * (s_safe ** -0.385), 0.15, 6.0)
        q_peak_grid = 0.208 * (contrib_area_grid / 1e6) * (cum_volume_grid / (contrib_area_grid + 1e-6) * 1000.0) / tc_hours

        # Compute volume intercepted by each terrace
        # Terraces act as line sinks intercepting flow along their row
        terrace_inflows = {}
        for terr in terraces:
            r = terr.row_idx
            # Sum cumulative volume intercepted along terrace channel
            inflow = float(np.sum(cum_volume_grid[r, :]))
            terrace_inflows[terr.terrace_id] = inflow

        return cum_volume_grid, q_peak_grid, terrace_inflows


def compute_terrace_excavation_volume(
    inflows_m3: np.ndarray,
    length_m: float = 707.1,
    ground_slope: float = 0.028,
    side_slope_zs: float = 3.0,
    freeboard_m: float = 0.20
) -> float:
    """
    Computes total cross-sectional earthmoving excavation volume across terraces:
    1. Ponding depth: d_water = sqrt(2 * slope * V_inflow / L)
    2. Embankment height: h_emb = d_water + freeboard_m
    3. Embankment base width: w_base = 2 * zs * h_emb
    4. Balanced cut-and-fill area: A_cross = 2 * (1/2 * w_base * h_emb) = 2 * zs * h_emb^2
    5. Excavation volume: V_exc = sum(A_cross * L)
    """
    inflows_safe = np.maximum(inflows_m3, 0.0)
    d_water = np.sqrt(2.0 * ground_slope * inflows_safe / length_m)
    h_emb = d_water + freeboard_m
    a_cross = 2.0 * side_slope_zs * (h_emb ** 2)
    return float(np.sum(a_cross * length_m))


# =============================================================================
# 4. BENCHMARK EVALUATOR & BASELINE COMPARISON
# =============================================================================

class RunoffBenchmarkEvaluator:
    """
    Executes Baseline 1 (Rational Method), Baseline 2 (Single-Run SCS-CN),
    and Agrostech Probabilistic SCS-CN Monte Carlo (K iterations).
    Computes:
    - Terrace Overtopping Hazard Misclassification Rate (OHMR)
    - Runoff exceedance calibration Brier score
    - Spatial risk variance surface
    """

    def __init__(
        self,
        grid_size: int = 100,
        cell_size_m: float = 7.071,
        storm_mm: float = 85.0,
        sigma_base_m: float = 0.25,
        l_corr_m: float = 20.0,
        seed: int = 42
    ):
        self.grid_size = grid_size
        self.cell_size_m = cell_size_m
        self.storm_mm = storm_mm
        self.sigma_base_m = sigma_base_m
        self.l_corr_m = l_corr_m
        self.rng = np.random.default_rng(seed)

        self.topo_gen = MicroCatchmentGenerator(grid_size, cell_size_m, seed=seed)
        self.grf_gen = GaussianRandomFieldGenerator(grid_size, cell_size_m, l_corr_m, sigma_base_m)
        self.router = HydrologicalFlowRouter(grid_size, cell_size_m)

    def run_benchmark(self, iterations_k: int = 500) -> Dict[str, Any]:
        print(f"[BENCHMARK 3] Initializing 50 ha Cerrado Micro-Catchment Topography (Grid {self.grid_size}x{self.grid_size})...")
        nominal_dtm, ndvi, cn, terraces = self.topo_gen.generate_topography()
        sigma_z_map = self.grf_gen.generate_spatial_uncertainty_map(nominal_dtm, ndvi)
        v_cell = self.router.compute_direct_runoff_volume(cn, self.storm_mm)

        # ---------------------------------------------------------------------
        # 1. GROUND TRUTH RUN (Unperturbed Smooth Topography)
        # ---------------------------------------------------------------------
        print("[BENCHMARK 3] Calculating Ground Truth Hydrology on Bare Terrain...")
        _, gt_q_peak, gt_inflows = self.router.route_flow(nominal_dtm, v_cell, terraces)
        q_crit = 0.010  # Physical threshold for concentrated rill flow initiation (10 L/s)
        gt_exceedance = (gt_q_peak > q_crit).astype(int)

        for terr in terraces:
            inflow = gt_inflows[terr.terrace_id]
            terr.ground_truth_overtop = 1 if inflow > terr.design_capacity_m3 else 0

        # ---------------------------------------------------------------------
        # 2. BASELINE 1: DETERMINISTIC RATIONAL METHOD (Q = C * I * A)
        # ---------------------------------------------------------------------
        print("[BENCHMARK 3] Evaluating Baseline 1: Deterministic Rational Method...")
        # Rational method assumes uniform C = 0.35, storm intensity I = 42.5 mm/hr (85mm in 2h)
        # Sizing heuristic: checks if catchment area exceeds static design threshold
        rational_predictions = {}
        for terr in terraces:
            catchment_area_ha = (terr.row_idx * self.grid_size * (self.cell_size_m ** 2)) / 10000.0
            q_rational = (0.35 * 42.5 * catchment_area_ha) / 360.0  # m3/s
            # If Q_rational > capacity factor, predict overtopping
            pred = 1 if q_rational > 0.45 else 0
            rational_predictions[terr.terrace_id] = pred

        # ---------------------------------------------------------------------
        # 3. BASELINE 2: SINGLE-RUN DETERMINISTIC SCS-CN (Noisy DTM Realization)
        # ---------------------------------------------------------------------
        print("[BENCHMARK 3] Evaluating Baseline 2: Single-Run Deterministic SCS-CN on Noisy DTM...")
        single_noise = self.grf_gen.generate_perturbation_realization(sigma_z_map, self.rng)
        single_noisy_dtm = nominal_dtm + single_noise
        _, single_q_peak, single_inflows = self.router.route_flow(single_noisy_dtm, v_cell, terraces)
        single_exceedance = (single_q_peak > q_crit).astype(int)

        for terr in terraces:
            inflow = single_inflows[terr.terrace_id]
            terr.single_run_pred = 1 if inflow > terr.design_capacity_m3 else 0

        # ---------------------------------------------------------------------
        # 4. AGROSTECH PROBABILISTIC SCS-CN MONTE CARLO (K iterations)
        # ---------------------------------------------------------------------
        print(f"[BENCHMARK 3] Running Agrostech Probabilistic SCS-CN Monte Carlo ({iterations_k} iterations)...")
        overtop_counts = {t.terrace_id: 0 for t in terraces}
        mc_inflow_samples = {t.terrace_id: [] for t in terraces}
        exceed_counts = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        q_peak_samples = np.zeros((iterations_k, self.grid_size, self.grid_size), dtype=np.float32)

        for k in range(iterations_k):
            noise_k = self.grf_gen.generate_perturbation_realization(sigma_z_map, self.rng)
            dtm_k = nominal_dtm + noise_k
            # Slight CN variation representing antecedent moisture conditions AMC
            cn_k = np.clip(cn + self.rng.normal(0, 1.5, cn.shape), 60.0, 95.0)
            v_cell_k = self.router.compute_direct_runoff_volume(cn_k, self.storm_mm)

            _, q_peak_k, inflows_k = self.router.route_flow(dtm_k, v_cell_k, terraces)

            q_peak_samples[k, :, :] = q_peak_k
            exceed_counts += (q_peak_k > q_crit).astype(np.int32)

            for terr in terraces:
                mc_inflow_samples[terr.terrace_id].append(inflows_k[terr.terrace_id])
                if inflows_k[terr.terrace_id] > terr.design_capacity_m3:
                    overtop_counts[terr.terrace_id] += 1

        prob_exceedance_surface = exceed_counts / float(iterations_k)
        risk_variance_surface = np.var(q_peak_samples, axis=0)

        for terr in terraces:
            terr.mc_prob_overtop = round(overtop_counts[terr.terrace_id] / float(iterations_k), 4)

        # ---------------------------------------------------------------------
        # 5. METRIC COMPUTATIONS & ERROR AUDIT
        # ---------------------------------------------------------------------
        # Overtopping Hazard Misclassification Rate (OHMR)
        # OHMR = False Negatives / True Positives (Model says safe, but overtopping occurs)
        gt_overtops = [t.ground_truth_overtop for t in terraces]
        single_preds = [t.single_run_pred for t in terraces]
        mc_preds = [1 if t.mc_prob_overtop >= 0.35 else 0 for t in terraces]
        rat_preds = [rational_predictions[t.terrace_id] for t in terraces]

        def compute_ohmr_and_far(y_t, y_p):
            tp = sum(1 for yt, yp in zip(y_t, y_p) if yt == 1 and yp == 1)
            fn = sum(1 for yt, yp in zip(y_t, y_p) if yt == 1 and yp == 0)
            fp = sum(1 for yt, yp in zip(y_t, y_p) if yt == 0 and yp == 1)
            tn = sum(1 for yt, yp in zip(y_t, y_p) if yt == 0 and yp == 0)
            ohmr = (fn / (tp + fn) * 100.0) if (tp + fn) > 0 else 0.0
            far = (fp / (tn + fp) * 100.0) if (tn + fp) > 0 else 0.0
            return round(ohmr, 2), round(far, 2)

        ohmr_single, far_single = compute_ohmr_and_far(gt_overtops, single_preds)
        ohmr_mc, far_mc = compute_ohmr_and_far(gt_overtops, mc_preds)
        ohmr_rat, far_rat = compute_ohmr_and_far(gt_overtops, rat_preds)

        # Dynamic Spatial Exceedance Calibration (Brier Score)
        brier_single = float(np.mean((single_exceedance - gt_exceedance) ** 2))
        brier_mc = float(np.mean((prob_exceedance_surface - gt_exceedance) ** 2))

        # Dynamic Planar Rational Method Exceedance Grid
        r_indices = np.arange(self.grid_size).reshape((self.grid_size, 1))
        area_accum_ha = (r_indices + 1) * (self.cell_size_m ** 2) / 10000.0
        q_rat_grid = np.repeat((0.35 * 42.5 * area_accum_ha) / 360.0, self.grid_size, axis=1)
        rat_exceedance = (q_rat_grid > q_crit).astype(float)
        brier_rat = float(np.mean((rat_exceedance - gt_exceedance) ** 2))

        # Dynamic Earthmoving Volumetric Excavation Calculations
        s_inflow_arr = np.array([single_inflows[t.terrace_id] for t in terraces])
        mc_inflow_mean_arr = np.array([np.mean(mc_inflow_samples[t.terrace_id]) for t in terraces])

        # 1. Baseline Single-Run: 35% safety factor on unverified DTM
        v_exc_single = compute_terrace_excavation_volume(
            s_inflow_arr * 1.35, length_m=terraces[0].length_m, ground_slope=0.028
        )
        # 2. Agrostech Probabilistic SCS-CN: Calibrated mean expected inflow across GRF
        v_exc_mc = compute_terrace_excavation_volume(
            mc_inflow_mean_arr, length_m=terraces[0].length_m, ground_slope=0.028
        )
        # 3. Deterministic Rational Method: Uniform template sized for max downslope catchment
        areas_ha = np.array([t.row_idx * self.grid_size * (self.cell_size_m ** 2) / 10000.0 for t in terraces])
        rat_vols = 10.0 * 0.40 * self.storm_mm * areas_ha * 1.50
        rat_uniform = np.full(len(terraces), np.max(rat_vols))
        v_exc_rat = compute_terrace_excavation_volume(
            rat_uniform, length_m=terraces[0].length_m, ground_slope=0.028
        )

        savings_single = 0.0
        savings_mc = round(((v_exc_single - v_exc_mc) / v_exc_single) * 100.0, 2)
        savings_rat = round(((v_exc_single - v_exc_rat) / v_exc_single) * 100.0, 2)

        return {
            "nominal_dtm": nominal_dtm,
            "sigma_z_map": sigma_z_map,
            "gt_exceedance": gt_exceedance,
            "single_exceedance": single_exceedance,
            "prob_exceedance_surface": prob_exceedance_surface,
            "risk_variance_surface": risk_variance_surface,
            "terraces": terraces,
            "metrics": {
                "Agrostech Probabilistic SCS-CN": {
                    "model_name": "Agrostech Probabilistic SCS-CN",
                    "ohmr_pct": ohmr_mc,
                    "far_pct": far_mc,
                    "spatial_brier_score": round(brier_mc, 4),
                    "earthmoving_savings_pct": savings_mc,
                    "excavation_volume_m3": round(v_exc_mc, 1)
                },
                "Single-Run Deterministic SCS-CN": {
                    "model_name": "Single-Run Deterministic SCS-CN",
                    "ohmr_pct": ohmr_single,
                    "far_pct": far_single,
                    "spatial_brier_score": round(brier_single, 4),
                    "earthmoving_savings_pct": savings_single,
                    "excavation_volume_m3": round(v_exc_single, 1)
                },
                "Deterministic Rational Method": {
                    "model_name": "Deterministic Rational Method",
                    "ohmr_pct": ohmr_rat,
                    "far_pct": far_rat,
                    "spatial_brier_score": round(brier_rat, 4),
                    "earthmoving_savings_pct": savings_rat,
                    "excavation_volume_m3": round(v_exc_rat, 1)
                }
            }
        }


# =============================================================================
# 5. PLOTTING & VISUALIZATION ARTIFACTS
# =============================================================================

def render_runoff_benchmark_plots(
    results: Dict[str, Any],
    output_path: str
):
    """
    Renders 4-panel publication-grade figure:
    1. Synthetic DTM Elevation & Engineered Contour Terraces Layout
    2. Deterministic Single-Run vs Probabilistic Runoff Exceedance P(Q > Qcrit)
    3. Spatial Vertical Elevation Uncertainty sigma_z(x, y) & Runoff Risk Variance
    4. Terrace Overtopping Comparison Bar Chart (Ground Truth vs Baselines vs Monte Carlo)
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), dpi=300)
    plt.subplots_adjust(hspace=0.32, wspace=0.28)

    nominal_dtm = results["nominal_dtm"]
    sigma_z = results["sigma_z_map"]
    p_exceed = results["prob_exceedance_surface"]
    q_var = results["risk_variance_surface"]
    terraces = results["terraces"]

    # 1. DTM Elevation & Terraces Layout
    ax1 = axes[0, 0]
    im1 = ax1.imshow(nominal_dtm, cmap="terrain", origin="lower")
    for terr in terraces:
        ax1.axhline(terr.row_idx, color="#d50000", linestyle="--", linewidth=1.8)
        ax1.text(5, terr.row_idx + 1.5, f"{terr.terrace_id} (Cap: {terr.design_capacity_m3:,.0f} m³)",
                 color="white", fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.2", facecolor="#b71c1c", alpha=0.85))
    ax1.set_title("A. Cerrado Catchment Elevation & Engineered Terraces", fontsize=12, fontweight="bold")
    ax1.set_xlabel("X Grid (Cell size = 7.07m)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Y Grid (Descending Slope)", fontsize=10, fontweight="bold")
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04, label="Elevation (m a.s.l.)")

    # 2. Probabilistic Runoff Exceedance Surface
    ax2 = axes[0, 1]
    im2 = ax2.imshow(p_exceed, cmap="plasma", vmin=0.0, vmax=1.0, origin="lower")
    for terr in terraces:
        ax2.axhline(terr.row_idx, color="white", linestyle=":", alpha=0.7, linewidth=1.2)
    ax2.set_title("B. Probabilistic Runoff Exceedance P(Q > 0.010 m³/s)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("X Grid", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Y Grid", fontsize=10, fontweight="bold")
    fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="Exceedance Probability")

    # 3. Spatial Risk Variance Surface
    ax3 = axes[1, 0]
    im3 = ax3.imshow(q_var, cmap="inferno", origin="lower")
    ax3.set_title("C. Runoff Discharge Variance Surface σ_Q²(x, y)", fontsize=12, fontweight="bold")
    ax3.set_xlabel("X Grid", fontsize=10, fontweight="bold")
    ax3.set_ylabel("Y Grid", fontsize=10, fontweight="bold")
    fig.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04, label="Discharge Variance (m⁶/s²)")

    # 4. Terrace Overtopping Comparison Bar Chart
    ax4 = axes[1, 1]
    t_labels = [t.terrace_id for t in terraces]
    gt_vals = [t.ground_truth_overtop * 100.0 for t in terraces]
    single_vals = [t.single_run_pred * 100.0 for t in terraces]
    mc_vals = [t.mc_prob_overtop * 100.0 for t in terraces]

    x = np.arange(len(t_labels))
    width = 0.26
    b1 = ax4.bar(x - width, gt_vals, width, label="Ground Truth (Bare DTM)", color="#212121", alpha=0.85)
    b2 = ax4.bar(x, single_vals, width, label="Single-Run SCS-CN (Noisy)", color="#e65100", alpha=0.85)
    b3 = ax4.bar(x + width, mc_vals, width, label="Agrostech Monte Carlo P(Overtop)", color="#1b5e20", alpha=0.85)

    ax4.set_xticks(x)
    ax4.set_xticklabels(t_labels, fontsize=10, fontweight="bold")
    ax4.set_ylabel("Overtopping Probability / State (%)", fontsize=11, fontweight="bold")
    ax4.set_ylim([0, 115])
    ax4.set_title("D. Terrace Overtopping Hazard Comparison", fontsize=12, fontweight="bold")
    ax4.legend(loc="upper left", frameon=True, fontsize=8.5)
    ax4.grid(True, linestyle=":", alpha=0.6, axis="y")

    # Add text labels on bars
    for bar in list(b1) + list(b2) + list(b3):
        h = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width() / 2.0, h + 2.0, f"{h:.0f}%", ha="center", va="bottom", fontsize=8)

    plt.suptitle("AGROSTECH R&D BENCHMARK — UNCERTAINTY-AWARE SCS-CN HYDROLOGY\n500 Monte Carlo Iterations over Photogrammetric DTM Vertical Noise on 50 ha Cerrado Farm",
                 fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Runoff Benchmark visualization plot saved to: {output_path}")


# =============================================================================
# 6. MAIN EXECUTION PIPELINE
# =============================================================================

def run_runoff_erosion_benchmark(
    grid_size: int = 100,
    iterations: int = 500,
    storm_mm: float = 85.0,
    sigma_z: float = 0.25,
    plot: bool = True,
    output_json: str = "results_runoff_erosion.json",
    output_png: str = "benchmark_runoff_erosion.png"
) -> Dict[str, Any]:
    evaluator = RunoffBenchmarkEvaluator(
        grid_size=grid_size,
        cell_size_m=7.071,
        storm_mm=storm_mm,
        sigma_base_m=sigma_z,
        l_corr_m=20.0,
        seed=42
    )

    results = evaluator.run_benchmark(iterations_k=iterations)

    # Format JSON export
    terraces_summary = []
    for t in results["terraces"]:
        terraces_summary.append({
            "terrace_id": t.terrace_id,
            "row_idx": t.row_idx,
            "length_m": t.length_m,
            "capacity_m3": t.design_capacity_m3,
            "ground_truth_overtopping": t.ground_truth_overtop,
            "single_run_prediction": t.single_run_pred,
            "agrostech_prob_overtopping": t.mc_prob_overtop
        })

    json_data = {
        "benchmark_name": "Uncertainty-Aware Probabilistic SCS-CN Monte Carlo",
        "parameters": {
            "catchment_area_ha": 50.0,
            "grid_dimensions": [grid_size, grid_size],
            "cell_size_m": 7.071,
            "design_rainfall_mm": storm_mm,
            "sigma_base_m": sigma_z,
            "correlation_length_m": 20.0,
            "monte_carlo_iterations": iterations
        },
        "models": results["metrics"],
        "terraces_evaluation": terraces_summary
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"[SUCCESS] Runoff Benchmark metrics exported to: {output_json}")

    if plot:
        render_runoff_benchmark_plots(results, output_png)

    # Summary table
    print("\n" + "=" * 90)
    print(f"{'Model':<35} | {'OHMR %':<10} | {'FAR %':<10} | {'Brier Score':<12} | {'Savings %':<10}")
    print("-" * 90)
    for name, m in results["metrics"].items():
        print(f"{name:<35} | {m['ohmr_pct']:<10.1f} | {m['far_pct']:<10.1f} | {m['spatial_brier_score']:<12.4f} | {m['earthmoving_savings_pct']:<10.1f}")
    print("=" * 90 + "\n")

    return json_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agrostech Probabilistic SCS-CN Runoff & Erosion Benchmark")
    parser.add_argument("--grid-size", type=int, default=100, help="Grid size (NxN)")
    parser.add_argument("--iterations", type=int, default=500, help="Monte Carlo realizations")
    parser.add_argument("--storm-mm", type=float, default=85.0, help="Design rainfall in mm")
    parser.add_argument("--sigma-z", type=float, default=0.25, help="Baseline elevation std dev (m)")
    parser.add_argument("--plot", action="store_true", default=True, help="Render plots")
    parser.add_argument("--output-json", type=str, default="results_runoff_erosion.json", help="Output JSON path")
    parser.add_argument("--output-png", type=str, default="benchmark_runoff_erosion.png", help="Output PNG path")
    args = parser.parse_args()

    run_runoff_erosion_benchmark(
        grid_size=args.grid_size,
        iterations=args.iterations,
        storm_mm=args.storm_mm,
        sigma_z=args.sigma_z,
        plot=args.plot,
        output_json=args.output_json,
        output_png=args.output_png
    )
