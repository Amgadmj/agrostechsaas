"""
test_adversarial_stress.py
==========================
Agrostech Novel R&D Directions — Adversarial Mathematical & Edge-Case Verification Suite
Executed by Agent: challenger_1 (Empirical Challenger)

Stress-tests Candidate 1, Candidate 2, and Candidate 3 under extreme, degenerate, and hostile edge cases:
- Candidate 1: Orthogonal passes (90 deg), extreme phenological shifts (>30d), disconnected/non-adjacent polygons, dense hedgerows.
- Candidate 2: Zero credit exposure (E=0), 100% clear skies (P_cloud=0, dt=0), prohibitive flight costs (C_flight >> Loss).
- Candidate 3: Zero rainfall (P=0), extreme downpour (P=250mm), flat plain (0.1%) vs steep slope (8.0%) monotonicity.
"""

import json
import math
import os
import sys
import unittest
from typing import Dict, List, Any

import numpy as np

# Ensure novel_rd_directions is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from benchmark_area_continua import (
    CARParcelPair,
    SyntheticCARPairGenerator,
    AgrostechMultiFeatureFusionClassifier,
    BaselineSingleCARClassifier,
    BaselineSpatialBufferClassifier,
)
from benchmark_voi_drone import (
    DroneFlightCostModel,
    AgrostechVoIPolicy,
    CerradoWeatherSimulator,
    CropCycleRiskSimulator,
)
from benchmark_runoff_erosion import (
    ContourTerrace,
    MicroCatchmentGenerator,
    GaussianRandomFieldGenerator,
    HydrologicalFlowRouter,
)


class TestCandidate1AreaContinuaAdversarial(unittest.TestCase):
    """Adversarial stress-testing of Candidate 1 (Área Contínua Multi-Feature Synchrony Fusion)."""

    def setUp(self):
        self.generator = SyntheticCARPairGenerator(seed=1337)
        self.classifier = AgrostechMultiFeatureFusionClassifier()
        # Baseline true continuous pair for reference
        self.base_pair = self.generator.generate_pair(1, "true_continuous")

    def test_orthogonal_tractor_passes(self):
        """Stress Test 1.1: Orthogonal crop row / tractor passes (delta_theta = 90 deg)."""
        pair = self.generator.generate_pair(2, "true_continuous")
        pair.row_azimuth_a_deg = 0.0
        pair.row_azimuth_b_deg = 90.0
        pair.row_concentration_a = 0.95
        pair.row_concentration_b = 0.95

        feats = self.classifier.extract_features(pair)
        s_azimuth = feats["S_azimuth"]

        # Exact mathematical expectation: cos^2(90 deg) == 0.0
        self.assertAlmostEqual(s_azimuth, 0.0, places=6,
                               msg=f"S_azimuth must be identically 0 for orthogonal passes, got {s_azimuth}")

        prob_ortho = self.classifier.predict_proba(pair)
        prob_aligned = self.classifier.predict_proba(self.base_pair)

        # Logit drop should equal w_azimuth * S_azimuth_aligned = 2.0 * ~0.95 = ~1.90
        logit_drop = math.log(prob_aligned / (1.0 - prob_aligned + 1e-9)) - math.log(prob_ortho / (1.0 - prob_ortho + 1e-9))
        self.assertGreater(logit_drop, 1.5,
                           msg=f"Logit drop under orthogonal passes should exceed 1.5, got {logit_drop:.3f}")

        # When evaluated on independent fields with orthogonal passes, prob drops sharply
        p_indep_ortho = self.generator.generate_pair(11, "independent_same_crop")
        p_indep_ortho.row_azimuth_a_deg = 0.0
        p_indep_ortho.row_azimuth_b_deg = 90.0
        prob_indep_ortho = self.classifier.predict_proba(p_indep_ortho)
        self.assertLess(prob_indep_ortho, 0.30,
                        f"Independent parcels with orthogonal passes must have P < 0.30, got {prob_indep_ortho:.4f}")

        print(f"[PASS 1.1] Orthogonal Passes: S_azimuth={s_azimuth:.6f}, P(Aligned)={prob_aligned:.4f} -> P(Ortho)={prob_ortho:.4f} (Logit Drop={logit_drop:.3f}), P(Indep+Ortho)={prob_indep_ortho:.4f}")

    def test_extreme_phenological_shift(self):
        """Stress Test 1.2: Extreme phenological shift (delta_t > 30 days)."""
        pair = self.generator.generate_pair(3, "true_continuous")
        t = pair.timestamps_days

        # Shift parcel B planting by 35 days (e.g. November vs late December)
        t_plant_a = 20.0
        t_plant_b = t_plant_a + 35.0
        dur = 110.0

        pair.ndvi_a = self.generator._generate_phenology_curve(t, t_plant_a, dur, ndvi_max=0.86)
        pair.ndvi_b = self.generator._generate_phenology_curve(t, t_plant_b, dur, ndvi_max=0.86)

        feats = self.classifier.extract_features(pair)
        s_event = feats["S_event"]
        s_pheno = feats["S_pheno"]

        # S_event = exp(-(35^2 + 35^2) / (2 * 5^2)) = exp(-2450 / 50) = exp(-49) ~ 5e-22
        self.assertLess(s_event, 1e-15,
                        msg=f"S_event must strictly collapse under 35-day shift, got {s_event}")

        # When evaluated on independent fields with 35d shift, P drops to ~0.12
        p_indep_35d = self.generator.generate_pair(12, "independent_same_crop")
        p_indep_35d.ndvi_b = self.generator._generate_phenology_curve(t, 55.0, 110.0)
        prob_indep_35d = self.classifier.predict_proba(p_indep_35d)
        self.assertLess(prob_indep_35d, 0.25,
                        f"Independent parcels with 35d shift must have P < 0.25, got {prob_indep_35d:.4f}")

        print(f"[PASS 1.2] Phenological Shift (35 days): S_event={s_event:.3e}, S_pheno={s_pheno:.4f}, P(Indep+35d)={prob_indep_35d:.4f}")

    def test_dense_impenetrable_hedgerow(self):
        """Stress Test 1.3: Dense impenetrable hedgerow / physical barrier (Delta_barrier >> 5, barrier_frac = 1.0)."""
        pair = self.generator.generate_pair(4, "true_continuous")
        pair.barrier_fraction = 1.0  # 100% of border is fenced / treed
        pair.barrier_contrast = 8.5  # Contrast ratio Delta_barrier = 8.5 >> 5.0

        feats = self.classifier.extract_features(pair)
        s_perm = feats["S_perm"]

        # Contrast delta = 8.5 - 1.0 = 7.5. exp(-7.5^2 / (2 * 0.5^2)) = exp(-112.5) ~ 0
        # s_perm_geom = 1 - 1.0 = 0.
        # s_perm = 0.5 * (0 + 0) = 0.0
        self.assertAlmostEqual(s_perm, 0.0, places=6,
                               msg=f"S_perm must collapse to 0 under dense barrier, got {s_perm}")

        p_indep_hedge = self.generator.generate_pair(13, "independent_same_crop")
        p_indep_hedge.barrier_fraction = 1.0
        p_indep_hedge.barrier_contrast = 10.0
        prob_indep_hedge = self.classifier.predict_proba(p_indep_hedge)
        self.assertLess(prob_indep_hedge, 0.22,
                        f"Independent parcels with dense barrier must have P < 0.22, got {prob_indep_hedge:.4f}")

        print(f"[PASS 1.3] Dense Impenetrable Barrier: barrier_contrast=8.5, barrier_frac=1.0 -> S_perm={s_perm:.6e}, P(Indep+Hedge)={prob_indep_hedge:.4f}")

    def test_disconnected_nonadjacent_polygons_architectural_check(self):
        """Stress Test 1.4: Disconnected non-adjacent polygons with zero shared boundary."""
        pair = self.generator.generate_pair(5, "true_continuous")
        pair.shared_boundary_length_m = 0.0  # Topologically disjoint!

        # Check specification vs implementation:
        # In MATHEMATICAL_FORMULATIONS_AND_ALGORITHMS.md (Algorithm 1):
        # if shared_boundary_length_m < min_boundary_length_m: P = 0.0.
        # In benchmark_area_continua.py BaselineSpatialBufferClassifier:
        buffer_clf = BaselineSpatialBufferClassifier()
        p_buffer = buffer_clf.predict_proba(pair)
        self.assertEqual(p_buffer, 0.0, "Spatial buffer baseline correctly rejects disjoint parcels")

        # Mathematical specification strict gating check:
        gated_prob = 0.0 if pair.shared_boundary_length_m < 10.0 else self.classifier.predict_proba(pair)
        self.assertEqual(gated_prob, 0.0, "Gated probability must strictly collapse to 0.0 per Algorithm 1")

        # Record empirical finding for handoff:
        raw_fusion_prob = self.classifier.predict_proba(pair)
        self.assertGreater(raw_fusion_prob, 0.50,
                           "Empirical confirmation: raw classifier omits boundary gate, highlighting need for Algorithm 1 pre-filter")
        print(f"[AUDIT 1.4] Disconnected Polygons (L_shared=0m): BufferBaseline P={p_buffer:.2f}, MathSpec Gated P={gated_prob:.2f}, Raw Un-gated Fusion P={raw_fusion_prob:.4f}")

    def test_compound_adversarial_collapse(self):
        """Stress Test 1.5: Compound hostile edge case (All divergence vectors combined)."""
        pair = self.generator.generate_pair(6, "true_continuous")
        t = pair.timestamps_days

        # 1. 35-day phenological delay
        pair.ndvi_a = self.generator._generate_phenology_curve(t, 20.0, 110.0)
        pair.ndvi_b = self.generator._generate_phenology_curve(t, 55.0, 110.0)
        # 2. Desynchronized SAR
        pair.sar_vh_a = -16.0 + 7.0 * pair.ndvi_a
        pair.sar_vh_b = -12.0 + np.random.normal(0, 1.0, len(t))
        pair.sar_vv_a = -10.0 + 4.0 * pair.ndvi_a
        pair.sar_vv_b = -8.0 + np.random.normal(0, 1.0, len(t))
        pair.insar_coherence = np.full(len(t), 0.15)
        # 3. Orthogonal passes
        pair.row_azimuth_a_deg = 0.0
        pair.row_azimuth_b_deg = 90.0
        # 4. Impenetrable barrier
        pair.barrier_fraction = 1.0
        pair.barrier_contrast = 9.0

        feats = self.classifier.extract_features(pair)
        prob = self.classifier.predict_proba(pair)

        # Key orthogonal synchrony features must collapse:
        self.assertLess(feats["S_event"], 1e-15, "S_event failed to collapse")
        self.assertLess(feats["S_sar"], 0.15, "S_sar failed to collapse")
        self.assertLess(feats["S_azimuth"], 1e-6, "S_azimuth failed to collapse")
        self.assertLess(feats["S_perm"], 1e-15, "S_perm failed to collapse")

        # Probability must decisively collapse (< 0.05 / 5%)
        self.assertLess(prob, 0.05, msg=f"Compound probability must collapse below 0.05, got {prob}")
        self.assertEqual(self.classifier.predict(pair), 0, "Compound hostile pair must be classified as 0 (Independent)")
        print(f"[PASS 1.5] Compound Hostile Case: Feats={feats} -> P(Continuous)={prob:.5f} (Collapsed to < 0.05)")


class TestCandidate2VoIDroneTriggerAdversarial(unittest.TestCase):
    """Adversarial stress-testing of Candidate 2 (Value-of-Information UAV Dispatch Engine)."""

    def setUp(self):
        self.cost_model = DroneFlightCostModel(mobilization_base=1200.0, variable_cost_per_ha=4.50)
        self.area_ha = 1000.0
        self.credit_exposure = 3500000.0  # R$ 3.5M

    def test_zero_credit_exposure(self):
        """Stress Test 2.1: Zero credit exposure (E_credit = 0.0 BRL)."""
        policy = AgrostechVoIPolicy(
            cost_model=self.cost_model,
            area_ha=self.area_ha,
            credit_exposure=0.0,  # Zero debt exposure
            threshold_brl=0.0
        )

        c_flight = self.cost_model.compute_cost(self.area_ha)  # R$ 5,700

        # Simulate across a variety of DAP and vulnerability stages under maximum uncertainty
        for dap in [15, 45, 65, 85, 105]:
            v_t = CropCycleRiskSimulator.get_phenological_vulnerability(dap)
            policy.update_daily_belief(dap, days_since_clear=15, optical_observed=False, ndvi_apparent=0.45, v_t=v_t)
            should_dispatch, nvoi, gvoi, cost = policy.evaluate_voi(dap, v_t, cloud_prob_forecast=0.90)

            # When debt exposure is 0, financial loss is 0 for all actions, so GVoI == 0, NVoI == -C_flight
            self.assertAlmostEqual(gvoi, 0.0, places=4,
                                   msg=f"GVoI must be identically 0 under E_credit=0, got {gvoi}")
            self.assertAlmostEqual(nvoi, -c_flight, places=2,
                                   msg=f"NVoI must equal -C_flight under E_credit=0, got {nvoi}")
            self.assertFalse(should_dispatch,
                             f"UAV must NEVER be dispatched when credit exposure is 0 (dap={dap})")

        print(f"[PASS 2.1] Zero Credit Exposure (E=0): GVoI=0.00, NVoI=-{c_flight:.2f} BRL, Dispatched=False across all DAP")

    def test_100_percent_clear_skies(self):
        """Stress Test 2.2: 100% clear skies (P_cloud = 0.0, days_since_clear = 0)."""
        policy = AgrostechVoIPolicy(
            cost_model=self.cost_model,
            area_ha=self.area_ha,
            credit_exposure=self.credit_exposure,
            threshold_brl=0.0
        )

        dispatched_count = 0
        nvoi_history = []

        # Simulate 120 days of uninterrupted cloud-free optical satellite passes
        for d in range(1, 121):
            v_t = CropCycleRiskSimulator.get_phenological_vulnerability(d)
            # High apparent NDVI from healthy crop
            policy.update_daily_belief(d, days_since_clear=0, optical_observed=True, ndvi_apparent=0.82, v_t=v_t)
            should_dispatch, nvoi, gvoi, _ = policy.evaluate_voi(d, v_t, cloud_prob_forecast=0.0)
            if should_dispatch:
                dispatched_count += 1
            nvoi_history.append(nvoi)

        self.assertEqual(dispatched_count, 0,
                         f"Zero flights should be dispatched under 100% clear skies, got {dispatched_count}")
        max_nvoi = max(nvoi_history)
        self.assertLess(max_nvoi, 0.0,
                        f"NVoI must remain strictly negative under clear skies, max was {max_nvoi}")
        print(f"[PASS 2.2] 100% Clear Skies: 0 flights dispatched over 120 days, Max NVoI={max_nvoi:.2f} BRL")

    def test_prohibitive_drone_flight_cost(self):
        """Stress Test 2.3: Prohibitive drone flight logistics cost (C_flight >> Max Loss)."""
        prohibitive_cost_model = DroneFlightCostModel(mobilization_base=50000000.0, variable_cost_per_ha=100.0)
        policy = AgrostechVoIPolicy(
            cost_model=prohibitive_cost_model,
            area_ha=self.area_ha,
            credit_exposure=self.credit_exposure,
            threshold_brl=0.0
        )

        v_t = CropCycleRiskSimulator.get_phenological_vulnerability(65)
        policy.update_daily_belief(65, days_since_clear=10, optical_observed=False, ndvi_apparent=0.40, v_t=v_t)
        should_dispatch, nvoi, gvoi, flight_cost = policy.evaluate_voi(65, v_t, cloud_prob_forecast=0.95)

        self.assertFalse(should_dispatch, "Drone must NOT be dispatched when flight cost is prohibitive")
        self.assertLess(nvoi, -10000000.0, f"NVoI must be deeply negative, got {nvoi}")
        print(f"[PASS 2.3] Prohibitive Flight Cost: C_flight={flight_cost:.2f} BRL, GVoI={gvoi:.2f} BRL, NVoI={nvoi:.2f} BRL -> Dispatch=False")

    def test_voi_monotonicity_with_credit_exposure(self):
        """Stress Test 2.4: Monotonic scaling of GVoI with respect to credit exposure."""
        exposures = [0.0, 500000.0, 1500000.0, 3500000.0, 7000000.0, 12000000.0]
        gvoi_results = []

        v_t = CropCycleRiskSimulator.get_phenological_vulnerability(65)
        for exp in exposures:
            pol = AgrostechVoIPolicy(self.cost_model, self.area_ha, exp, threshold_brl=0.0)
            pol.update_daily_belief(65, days_since_clear=8, optical_observed=False, ndvi_apparent=0.50, v_t=v_t)
            _, nvoi, gvoi, _ = pol.evaluate_voi(65, v_t, cloud_prob_forecast=0.85)
            gvoi_results.append(gvoi)

        # Verify strict monotonicity: GVoI(E_k+1) >= GVoI(E_k)
        for i in range(len(gvoi_results) - 1):
            self.assertGreaterEqual(gvoi_results[i + 1], gvoi_results[i] - 1e-4,
                                    f"GVoI violated monotonicity: {gvoi_results[i+1]} < {gvoi_results[i]}")

        print(f"[PASS 2.4] VoI Monotonicity with Credit Exposure: Exposures={exposures} -> GVoI={gvoi_results}")


class TestCandidate3SCSCNHydrologyAdversarial(unittest.TestCase):
    """Adversarial stress-testing of Candidate 3 (Uncertainty-Aware Hydrology & SCS-CN Monte Carlo)."""

    def setUp(self):
        self.grid_size = 100  # Full 100x100 micro-catchment (50 ha)
        self.cell_size = 7.071  # 50 m2 per cell
        self.topo_gen = MicroCatchmentGenerator(self.grid_size, self.cell_size, seed=42)
        self.router = HydrologicalFlowRouter(self.grid_size, self.cell_size)
        self.nominal_dtm, self.ndvi_grid, self.cn_grid, self.terraces = self.topo_gen.generate_topography()

    def test_zero_rainfall_storm(self):
        """Stress Test 3.1: Zero rainfall storm event (P = 0.0 mm)."""
        v_cell = self.router.compute_direct_runoff_volume(self.cn_grid, design_storm_mm=0.0)

        # Runoff must be identically zero everywhere
        self.assertTrue(np.all(v_cell == 0.0), "Runoff volume must be identically 0.0 m3 for P=0mm")

        cum_vol, q_peak, inflows = self.router.route_flow(self.nominal_dtm, v_cell, self.terraces)

        self.assertTrue(np.all(cum_vol == 0.0), "Cumulative volume must be identically 0.0 m3 for P=0mm")
        self.assertTrue(np.all(q_peak == 0.0), "Peak discharge must be identically 0.0 m3/s for P=0mm")
        for terr_id, inflow in inflows.items():
            self.assertEqual(inflow, 0.0, f"Terrace {terr_id} inflow must be 0.0 m3, got {inflow}")

        print(f"[PASS 3.1] Zero Rainfall Storm (P=0mm): v_cell_max={np.max(v_cell):.4f}, q_peak_max={np.max(q_peak):.4f}, All Terrace Inflows=0.0 m3")

    def test_extreme_tropical_downpour(self):
        """Stress Test 3.2: Extreme tropical downpour (P = 250.0 mm, 100-year Cerrado storm)."""
        v_cell = self.router.compute_direct_runoff_volume(self.cn_grid, design_storm_mm=250.0)
        cum_vol, q_peak, inflows = self.router.route_flow(self.nominal_dtm, v_cell, self.terraces)

        # Mean CN ~ 78 -> S ~ 71.7 mm, Ia ~ 3.58 mm -> q ~ 191 mm
        mean_runoff_depth_mm = (np.mean(v_cell) / (self.cell_size ** 2)) * 1000.0
        self.assertGreater(mean_runoff_depth_mm, 180.0,
                           f"Mean runoff depth under 250mm storm should exceed 180mm, got {mean_runoff_depth_mm:.2f}")

        # All 4 terraces must experience catastrophic overtopping
        for terr in self.terraces:
            inflow = inflows[terr.terrace_id]
            self.assertGreater(inflow, terr.design_capacity_m3,
                               f"Terrace {terr.terrace_id} should have overtopped (inflow={inflow:.1f} > cap={terr.design_capacity_m3})")

        print(f"[PASS 3.2] Extreme Downpour (P=250mm): Mean Runoff Depth={mean_runoff_depth_mm:.1f}mm, Inflows={inflows} (100% Terraces Overtopped)")

    def test_rainfall_response_monotonicity(self):
        """Stress Test 3.3: Strict monotonicity of runoff volume and peak discharge across rainfall depths."""
        storm_depths = [0.0, 10.0, 25.0, 50.0, 85.0, 120.0, 180.0, 250.0]
        total_volumes = []
        mean_q_peaks = []
        t2_inflows = []

        for p in storm_depths:
            v_cell = self.router.compute_direct_runoff_volume(self.cn_grid, design_storm_mm=p)
            cum_vol, q_peak, inflows = self.router.route_flow(self.nominal_dtm, v_cell, self.terraces)
            total_volumes.append(float(np.sum(v_cell)))
            mean_q_peaks.append(float(np.mean(q_peak)))
            t2_inflows.append(inflows["TERRACE_02"])

        # Check strict monotonicity
        for i in range(len(storm_depths) - 1):
            self.assertGreaterEqual(total_volumes[i + 1], total_volumes[i],
                                    f"Runoff volume not monotonic at P={storm_depths[i+1]}")
            self.assertGreaterEqual(mean_q_peaks[i + 1], mean_q_peaks[i],
                                    f"Peak discharge not monotonic at P={storm_depths[i+1]}")
            self.assertGreaterEqual(t2_inflows[i + 1], t2_inflows[i],
                                    f"Terrace 2 inflow not monotonic at P={storm_depths[i+1]}")

        print(f"[PASS 3.3] Rainfall Monotonicity (0-250mm): Volumes={[round(v, 1) for v in total_volumes]}, Mean Q_peak={[round(q, 4) for q in mean_q_peaks]}")

    def test_topographic_slope_sensitivity(self):
        """Stress Test 3.4: Slope gradient impact on Kirpich Time of Concentration and DTM noise scale."""
        n = self.grid_size
        dx = self.cell_size
        X, Y = np.meshgrid(np.arange(n)*dx, np.arange(n)*dx)

        # Planar test surfaces with uniform slope descending in Y
        dtm_flat = 450.0 - 0.005 * Y    # 0.5% slope
        dtm_steep = 450.0 - 0.080 * Y   # 8.0% slope

        v_cell = self.router.compute_direct_runoff_volume(self.cn_grid, design_storm_mm=85.0)

        _, q_flat, _ = self.router.route_flow(dtm_flat, v_cell, self.terraces)
        _, q_steep, _ = self.router.route_flow(dtm_steep, v_cell, self.terraces)

        # Mean discharge across entire domain should be strictly higher on steep slope (Kirpich tc is smaller)
        mean_q_flat = float(np.mean(q_flat))
        mean_q_steep = float(np.mean(q_steep))
        self.assertGreater(mean_q_steep, mean_q_flat,
                           f"Steep slope mean discharge ({mean_q_steep:.4f}) should exceed flat plain ({mean_q_flat:.4f})")

        # Check spatial uncertainty scaling
        grf = GaussianRandomFieldGenerator(self.grid_size, self.cell_size)
        sigma_flat = grf.generate_spatial_uncertainty_map(dtm_flat, self.ndvi_grid)
        sigma_steep = grf.generate_spatial_uncertainty_map(dtm_steep, self.ndvi_grid)

        mean_sigma_flat = float(np.mean(sigma_flat))
        mean_sigma_steep = float(np.mean(sigma_steep))
        self.assertGreater(mean_sigma_steep, mean_sigma_flat,
                           f"Steep slope DTM uncertainty ({mean_sigma_steep:.3f}m) must exceed flat ({mean_sigma_flat:.3f}m)")

        print(f"[PASS 3.4] Slope Sensitivity: Flat (0.5%) Mean Q={mean_q_flat:.4f}m3/s, sigma_z={mean_sigma_flat:.3f}m vs Steep (8.0%) Mean Q={mean_q_steep:.4f}m3/s, sigma_z={mean_sigma_steep:.3f}m")


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING ADVERSARIAL STRESS TEST SUITE: AGROSTECH NOVEL R&D DIRECTIONS")
    print("=" * 80)
    unittest.main(verbosity=2)
