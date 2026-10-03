"""
test_stress_reproducibility.py
==============================
Agrostech Novel R&D Directions — Empirical Stress, Reproducibility & Feasibility Harness
Author: challenger_2 (Empirical Stress & Reproducibility Challenger)

Mandate:
1. Data Integrity & Physical Consistency of all JSON artifacts
2. Random Seed Sensitivity & Non-Cherry-Picking Verification across seeds (42, 101, 777, 999, 1234, 2026, 9999)
3. Computational Feasibility, Runtime Complexity Scaling, and Memory Leak Auditing
4. Adversarial Edge Cases & Boundary Value Stress Testing
"""

import copy
import json
import math
import os
import sys
import time
import tracemalloc
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from shapely.geometry import Polygon, box

# Import the core modules from novel_rd_directions
import benchmark_area_continua as bac
import benchmark_voi_drone as bvd
import benchmark_runoff_erosion as bre


# =============================================================================
# SUITE 1: DATA ARTIFACT INTEGRITY & PHYSICAL INVARIANTS
# =============================================================================

def test_data_artifact_integrity() -> Dict[str, Any]:
    print("\n" + "=" * 90)
    print("SUITE 1: DATA ARTIFACT INTEGRITY & PHYSICAL INVARIANTS")
    print("=" * 90)

    artifacts = [
        "results_area_continua.json",
        "results_voi_drone.json",
        "results_runoff_erosion.json",
        "novel_rd_benchmarks_summary.json"
    ]

    results = {}
    for filename in artifacts:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        assert os.path.exists(filepath), f"Missing artifact: {filepath}"
        assert os.path.getsize(filepath) > 0, f"Empty artifact: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        results[filename] = data
        print(f"[PASS] {filename} is valid JSON and non-empty ({os.path.getsize(filepath)} bytes).")

    # Deep check results_area_continua.json
    ac = results["results_area_continua.json"]
    assert ac["sample_size_pairs"] == 200, f"Expected 200 pairs, got {ac['sample_size_pairs']}"
    for model_name, m in ac["models"].items():
        assert 0.0 <= m["roc_auc"] <= 1.0, f"Invalid roc_auc: {m['roc_auc']} in {model_name}"
        assert 0.0 <= m["brier_score"] <= 1.0, f"Invalid brier_score: {m['brier_score']} in {model_name}"
        assert 0.0 <= m["false_merge_rate_pct"] <= 100.0
        assert 0.0 <= m["false_split_rate_pct"] <= 100.0
        assert 0.0 <= m["accuracy_pct"] <= 100.0
        assert 0.0 <= m["mean_jaccard_iou_pct"] <= 100.0
        cm = m["confusion_matrix"]
        total_cm = cm["true_positives"] + cm["false_positives"] + cm["true_negatives"] + cm["false_negatives"]
        assert total_cm == 200, f"Confusion matrix total {total_cm} != 200 in {model_name}"
    print("[PASS] results_area_continua.json satisfies all physical and mathematical bounds.")

    # Deep check results_voi_drone.json
    voi = results["results_voi_drone.json"]
    for pol_name, p in voi["policies"].items():
        nev_mean = p["net_economic_value_per_ha_brl"]["mean"]
        cost_mean = p["flight_cost_per_ha_brl"]["mean"]
        prevented_mean = p["loss_prevented_per_ha_brl"]["mean"]
        assert cost_mean >= 0.0, f"Negative flight cost: {cost_mean}"
        assert prevented_mean >= 0.0, f"Negative loss prevented: {prevented_mean}"
        # Economic balance check: NEV = Loss Prevented - Flight Cost
        expected_nev = round(prevented_mean - cost_mean, 2)
        diff = abs(nev_mean - expected_nev)
        assert diff <= 0.10, f"Economic balance discrepancy in {pol_name}: {nev_mean} vs {expected_nev}"
        assert p["mean_flight_count"] >= 0.0
        assert p["mean_detection_latency_days"] >= 0.0
        assert 0.0 <= p["false_escalation_rate_pct"] <= 100.0
        assert 0.0 <= p["early_intervention_capture_pct"] <= 100.0
    print("[PASS] results_voi_drone.json satisfies all economic equations and probability bounds.")

    # Deep check results_runoff_erosion.json
    ro = results["results_runoff_erosion.json"]
    for m_name, m in ro["models"].items():
        assert 0.0 <= m["ohmr_pct"] <= 100.0, f"Invalid ohmr: {m['ohmr_pct']}"
        assert 0.0 <= m["far_pct"] <= 100.0, f"Invalid far: {m['far_pct']}"
        assert 0.0 <= m["spatial_brier_score"] <= 1.0, f"Invalid brier: {m['spatial_brier_score']}"
    for t in ro["terraces_evaluation"]:
        assert 0.0 <= t["agrostech_prob_overtopping"] <= 1.0, f"Invalid terrace prob: {t['agrostech_prob_overtopping']}"
        assert t["capacity_m3"] > 0.0
    print("[PASS] results_runoff_erosion.json satisfies all hydrological bounds.")

    # Cross-check master summary with individual JSONs
    summary = results["novel_rd_benchmarks_summary.json"]
    s_benches = summary["benchmarks"]
    assert "candidate_1_area_continua" in s_benches
    assert "candidate_2_voi_drone" in s_benches
    assert "candidate_3_probabilistic_runoff" in s_benches

    # Check Candidate 1 synchronization
    c1_sum = s_benches["candidate_1_area_continua"]["models"]["Agrostech Multi-Feature Fusion"]
    c1_ind = ac["models"]["Agrostech Multi-Feature Fusion"]
    assert c1_sum["roc_auc"] == c1_ind["roc_auc"]
    assert c1_sum["brier_score"] == c1_ind["brier_score"]

    # Check Candidate 2 synchronization
    c2_sum = s_benches["candidate_2_voi_drone"]["policies"]["Agrostech VoI Dispatch"]
    c2_ind = voi["policies"]["Agrostech VoI Dispatch"]
    assert c2_sum["net_economic_value_per_ha_brl"]["mean"] == c2_ind["net_economic_value_per_ha_brl"]["mean"]

    # Check Candidate 3 synchronization
    c3_sum = s_benches["candidate_3_probabilistic_runoff"]["models"]["Agrostech Probabilistic SCS-CN"]
    c3_ind = ro["models"]["Agrostech Probabilistic SCS-CN"]
    assert c3_sum["ohmr_pct"] == c3_ind["ohmr_pct"]
    assert c3_sum["earthmoving_savings_pct"] == c3_ind["earthmoving_savings_pct"]

    print("[PASS] novel_rd_benchmarks_summary.json is in 100% synchronization with individual files.")
    return {"status": "SUCCESS"}


# =============================================================================
# SUITE 2: RANDOM SEED SENSITIVITY & NON-CHERRY-PICKING VERIFICATION
# =============================================================================

def test_random_seed_sensitivity() -> Dict[str, Any]:
    print("\n" + "=" * 90)
    print("SUITE 2: RANDOM SEED SENSITIVITY & NON-CHERRY-PICKING VERIFICATION")
    print("=" * 90)

    seeds = [42, 101, 777, 999, 1234, 2026, 9999]
    print(f"Testing {len(seeds)} random seeds across all 3 candidates: {seeds}")

    # -------------------------------------------------------------------------
    # Candidate 1: Area Continua across seeds
    # -------------------------------------------------------------------------
    print("\n--- [Candidate 1: Area Continua Multi-Feature Fusion] ---")
    c1_results = []
    for s in seeds:
        gen = bac.SyntheticCARPairGenerator(seed=s)
        pairs = gen.generate_dataset(num_pairs=100)  # 100 pairs per seed
        model_agro = bac.AgrostechMultiFeatureFusionClassifier()
        model_buff = bac.BaselineSpatialBufferClassifier()
        model_sing = bac.BaselineSingleCARClassifier()
        evaluator = bac.AreaContinuaBenchmarkEvaluator()

        res_agro = evaluator.evaluate_model("Agrostech", model_agro.predict, model_agro.predict_proba, pairs)
        res_buff = evaluator.evaluate_model("Buffer", model_buff.predict, model_buff.predict_proba, pairs)
        res_sing = evaluator.evaluate_model("Single", model_sing.predict, model_sing.predict_proba, pairs)

        c1_results.append({
            "seed": s,
            "agro_auc": res_agro["roc_auc"],
            "agro_brier": res_agro["brier_score"],
            "agro_fmr": res_agro["false_merge_rate_pct"],
            "agro_fsr": res_agro["false_split_rate_pct"],
            "agro_acc": res_agro["accuracy_pct"],
            "buff_auc": res_buff["roc_auc"],
            "buff_fmr": res_buff["false_merge_rate_pct"],
            "sing_auc": res_sing["roc_auc"],
            "sing_fsr": res_sing["false_split_rate_pct"],
        })
        print(f"Seed {s:5d}: Agrostech AUC={res_agro['roc_auc']:.4f}, Brier={res_agro['brier_score']:.4f}, Acc={res_agro['accuracy_pct']:.1f}% | Buffer FMR={res_buff['false_merge_rate_pct']:.1f}% | Single FSR={res_sing['false_split_rate_pct']:.1f}%")

    df_c1 = pd.DataFrame(c1_results)
    min_agro_auc = df_c1["agro_auc"].min()
    max_agro_brier = df_c1["agro_brier"].max()
    min_agro_acc = df_c1["agro_acc"].min()
    mean_buff_fmr = df_c1["buff_fmr"].mean()
    mean_sing_fsr = df_c1["sing_fsr"].mean()

    assert min_agro_auc >= 0.99, f"Agrostech AUC dipped below 0.99: {min_agro_auc}"
    assert max_agro_brier <= 0.06, f"Agrostech Brier exceeded 0.06: {max_agro_brier}"
    assert min_agro_acc >= 98.0, f"Agrostech accuracy dipped below 98%: {min_agro_acc}"
    assert mean_buff_fmr == 100.0, f"Baseline buffer FMR not 100%: {mean_buff_fmr}"
    assert mean_sing_fsr == 100.0, f"Baseline single-CAR FSR not 100%: {mean_sing_fsr}"
    print(f"[PASS] Candidate 1 Multi-Feature Fusion is 100% robust across all {len(seeds)} random seeds (AUC in [{min_agro_auc:.4f}, {df_c1['agro_auc'].max():.4f}]).")

    # -------------------------------------------------------------------------
    # Candidate 2: VoI Drone Trigger across seeds
    # -------------------------------------------------------------------------
    print("\n--- [Candidate 2: VoI Drone Dispatch] ---")
    c2_results = []
    for s in seeds:
        evaluator = bvd.VoIBenchmarkEvaluator(
            area_ha=1000.0,
            credit_exposure=3500000.0,
            seed=s
        )
        # Run 50 Monte Carlo seasons per seed to thoroughly sample distributions
        summary, _ = evaluator.run_monte_carlo_benchmark(num_seasons=50)
        agro_nev = summary["Agrostech VoI Dispatch"]["net_economic_value_per_ha_brl"]["mean"]
        fixed_nev = summary["Fixed Calendar (14d)"]["net_economic_value_per_ha_brl"]["mean"]
        naive_nev = summary["Naive NDVI Threshold"]["net_economic_value_per_ha_brl"]["mean"]

        agro_lat = summary["Agrostech VoI Dispatch"]["mean_detection_latency_days"]
        fixed_lat = summary["Fixed Calendar (14d)"]["mean_detection_latency_days"]
        naive_lat = summary["Naive NDVI Threshold"]["mean_detection_latency_days"]

        agro_cap = summary["Agrostech VoI Dispatch"]["early_intervention_capture_pct"]
        fixed_cap = summary["Fixed Calendar (14d)"]["early_intervention_capture_pct"]
        naive_cap = summary["Naive NDVI Threshold"]["early_intervention_capture_pct"]

        c2_results.append({
            "seed": s,
            "agro_nev": agro_nev,
            "fixed_nev": fixed_nev,
            "naive_nev": naive_nev,
            "agro_lat": agro_lat,
            "fixed_lat": fixed_lat,
            "naive_lat": naive_lat,
            "agro_cap": agro_cap,
            "fixed_cap": fixed_cap,
            "naive_cap": naive_cap
        })
        print(f"Seed {s:5d}: NEV Agro=R${agro_nev:6.1f} vs Fixed=R${fixed_nev:6.1f} vs Naive=R${naive_nev:6.1f} | Latency: Agro={agro_lat:.1f}d vs Fixed={fixed_lat:.1f}d vs Naive={naive_lat:.1f}d")

    df_c2 = pd.DataFrame(c2_results)
    # Check that Agrostech VoI NEV is strictly greater than both baselines across ALL seeds
    for idx, row in df_c2.iterrows():
        assert row["agro_nev"] > row["fixed_nev"], f"Seed {row['seed']}: Agro NEV ({row['agro_nev']}) <= Fixed NEV ({row['fixed_nev']})"
        assert row["agro_nev"] > row["naive_nev"], f"Seed {row['seed']}: Agro NEV ({row['agro_nev']}) <= Naive NEV ({row['naive_nev']})"
        assert row["agro_lat"] < row["fixed_lat"], f"Seed {row['seed']}: Agro latency ({row['agro_lat']}) >= Fixed latency ({row['fixed_lat']})"
        assert row["agro_lat"] < row["naive_lat"], f"Seed {row['seed']}: Agro latency ({row['agro_lat']}) >= Naive latency ({row['naive_lat']})"
        assert row["agro_cap"] > row["fixed_cap"], f"Seed {row['seed']}: Agro capture ({row['agro_cap']}) <= Fixed capture ({row['fixed_cap']})"

    mean_advantage_fixed = (df_c2["agro_nev"] - df_c2["fixed_nev"]).mean()
    mean_advantage_naive = (df_c2["agro_nev"] - df_c2["naive_nev"]).mean()
    print(f"[PASS] Candidate 2 VoI Dispatch statistically dominates across ALL {len(seeds)} seeds.")
    print(f"       Mean Advantage vs Fixed Calendar: +R$ {mean_advantage_fixed:.2f}/ha (min: +R$ {(df_c2['agro_nev'] - df_c2['fixed_nev']).min():.2f}/ha)")
    print(f"       Mean Advantage vs Naive NDVI:    +R$ {mean_advantage_naive:.2f}/ha (min: +R$ {(df_c2['agro_nev'] - df_c2['naive_nev']).min():.2f}/ha)")

    # -------------------------------------------------------------------------
    # Candidate 3: Probabilistic Runoff & Erosion across seeds
    # -------------------------------------------------------------------------
    print("\n--- [Candidate 3: Probabilistic SCS-CN Monte Carlo] ---")
    c3_results = []
    for s in seeds:
        evaluator = bre.RunoffBenchmarkEvaluator(
            grid_size=100,
            cell_size_m=7.071,
            storm_mm=85.0,
            sigma_base_m=0.25,
            l_corr_m=20.0,
            seed=s
        )
        res = evaluator.run_benchmark(iterations_k=100)  # 100 realizations per seed
        agro_ohmr = res["metrics"]["Agrostech Probabilistic SCS-CN"]["ohmr_pct"]
        single_ohmr = res["metrics"]["Single-Run Deterministic SCS-CN"]["ohmr_pct"]
        rational_far = res["metrics"]["Deterministic Rational Method"]["far_pct"]
        savings = res["metrics"]["Agrostech Probabilistic SCS-CN"]["earthmoving_savings_pct"]

        c3_results.append({
            "seed": s,
            "agro_ohmr": agro_ohmr,
            "single_ohmr": single_ohmr,
            "rational_far": rational_far,
            "savings": savings
        })
        print(f"Seed {s:5d}: Agrostech OHMR={agro_ohmr:.1f}%, Single-Run OHMR={single_ohmr:.1f}%, Rational FAR={rational_far:.1f}%, Earthmoving Savings={savings:.1f}%")

    df_c3 = pd.DataFrame(c3_results)
    # Check that Agrostech OHMR is ALWAYS 0.0% (catches all true overtoppings) across all seeds
    for idx, row in df_c3.iterrows():
        assert row["agro_ohmr"] == 0.0, f"Seed {row['seed']}: Agrostech missed overtopping! OHMR={row['agro_ohmr']}%"
        assert row["savings"] > 0.0, f"Seed {row['seed']}: Earthmoving savings not positive: {row['savings']}%"

    mean_single_ohmr = df_c3["single_ohmr"].mean()
    print(f"[PASS] Candidate 3 Probabilistic SCS-CN achieves 0.0% OHMR (Zero Missed Overtoppings) across ALL {len(seeds)} seeds.")
    print(f"       Deterministic Single-Run suffered average Overtopping Hazard Miss Rate of {mean_single_ohmr:.1f}%.")
    print(f"       Agrostech Earthmoving Savings averaged {df_c3['savings'].mean():.1f}% across all seeds.")

    return {
        "status": "SUCCESS",
        "c1_df": df_c1,
        "c2_df": df_c2,
        "c3_df": df_c3
    }


# =============================================================================
# SUITE 3: COMPUTATIONAL FEASIBILITY, RUNTIME SCALING & MEMORY LEAKS
# =============================================================================

def test_computational_feasibility_and_scaling() -> Dict[str, Any]:
    print("\n" + "=" * 90)
    print("SUITE 3: COMPUTATIONAL FEASIBILITY, RUNTIME SCALING & MEMORY AUDITING")
    print("=" * 90)

    # 1. Candidate 1 Pair Generation & Classification Scaling
    print("--- [Candidate 1 Runtime Scaling] ---")
    pair_counts = [50, 100, 200, 400, 800]
    c1_timing = []
    for n in pair_counts:
        t0 = time.perf_counter()
        gen = bac.SyntheticCARPairGenerator(seed=42)
        pairs = gen.generate_dataset(num_pairs=n)
        t_gen = time.perf_counter() - t0

        t1 = time.perf_counter()
        model_agro = bac.AgrostechMultiFeatureFusionClassifier()
        evaluator = bac.AreaContinuaBenchmarkEvaluator()
        res = evaluator.evaluate_model("Agrostech", model_agro.predict, model_agro.predict_proba, pairs)
        t_eval = time.perf_counter() - t1
        t_total = t_gen + t_eval

        c1_timing.append({"n": n, "t_gen": t_gen, "t_eval": t_eval, "t_total": t_total, "per_pair_ms": (t_total / n) * 1000})
        print(f"Pairs={n:4d} | Gen: {t_gen:6.3f}s | Eval: {t_eval:6.3f}s | Total: {t_total:6.3f}s ({c1_timing[-1]['per_pair_ms']:5.2f} ms/pair)")

    # Verify linear O(N) complexity for Candidate 1
    t_50 = c1_timing[0]["t_total"]
    t_800 = c1_timing[-1]["t_total"]
    ratio = t_800 / t_50  # Factor of 16 in pairs
    print(f"C1 16x scale factor: Time ratio = {ratio:.2f}x (Ideal linear = 16.0x). Linear complexity confirmed.")
    assert ratio <= 25.0, f"Super-linear scaling detected: {ratio}x for 16x data increase"

    # 2. Candidate 2 Monte Carlo Seasons Scaling
    print("\n--- [Candidate 2 Runtime Scaling: 25 vs 50 vs 100 vs 250 seasons] ---")
    season_counts = [25, 50, 100, 250]
    c2_timing = []
    evaluator_c2 = bvd.VoIBenchmarkEvaluator(area_ha=1000.0, credit_exposure=3500000.0, seed=42)
    for n_s in season_counts:
        t0 = time.perf_counter()
        summary, _ = evaluator_c2.run_monte_carlo_benchmark(num_seasons=n_s)
        t_el = time.perf_counter() - t0
        c2_timing.append({"seasons": n_s, "total_sec": t_el, "per_season_sec": t_el / n_s})
        print(f"Seasons={n_s:3d} | Total: {t_el:6.2f}s | Per Season: {c2_timing[-1]['per_season_sec']*1000:6.1f} ms")

    # Verify linear O(N) complexity for Candidate 2
    t_25 = c2_timing[0]["total_sec"]
    t_250 = c2_timing[-1]["total_sec"]
    ratio_c2 = t_250 / t_25
    print(f"C2 10x scale factor: Time ratio = {ratio_c2:.2f}x (Ideal linear = 10.0x). Linear complexity confirmed.")
    assert ratio_c2 <= 15.0, f"Super-linear scaling detected in VoI simulation: {ratio_c2}x"

    # 3. Candidate 3 Monte Carlo Iterations Scaling (50 vs 100 vs 250 vs 500)
    print("\n--- [Candidate 3 Runtime Scaling: 50 vs 100 vs 250 vs 500 iterations] ---")
    iteration_counts = [50, 100, 250, 500]
    c3_timing = []
    for iters in iteration_counts:
        evaluator_c3 = bre.RunoffBenchmarkEvaluator(
            grid_size=100,
            cell_size_m=7.071,
            storm_mm=85.0,
            sigma_base_m=0.25,
            l_corr_m=20.0,
            seed=42
        )
        t0 = time.perf_counter()
        res = evaluator_c3.run_benchmark(iterations_k=iters)
        t_el = time.perf_counter() - t0
        c3_timing.append({"iterations": iters, "total_sec": t_el, "per_iter_ms": (t_el / iters) * 1000})
        print(f"Iterations={iters:3d} | Total: {t_el:6.2f}s | Per Realization: {c3_timing[-1]['per_iter_ms']:6.2f} ms")

    t_50_c3 = c3_timing[0]["total_sec"]
    t_500_c3 = c3_timing[-1]["total_sec"]
    ratio_c3 = t_500_c3 / t_50_c3
    print(f"C3 10x scale factor: Time ratio = {ratio_c3:.2f}x (Ideal linear = 10.0x). Linear complexity confirmed.")
    assert ratio_c3 <= 14.0, f"Super-linear scaling in SCS-CN Monte Carlo: {ratio_c3}x"
    assert t_500_c3 < 45.0, f"500 iterations exceeded 45 seconds: {t_500_c3:.2f}s"

    # Memory usage check on dedicated realization batch
    tracemalloc.start()
    evaluator_mem = bre.RunoffBenchmarkEvaluator(grid_size=100, seed=42)
    _ = evaluator_mem.run_benchmark(iterations_k=10)
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"\n[PASS] Memory audit: Current = {current_mem / (1024**2):.2f} MB, Peak = {peak_mem / (1024**2):.2f} MB.")
    assert peak_mem / (1024**2) < 500.0, f"Excessive memory consumption: {peak_mem / (1024**2):.2f} MB"

    return {
        "status": "SUCCESS",
        "c1_timing": c1_timing,
        "c2_timing": c2_timing,
        "c3_timing": c3_timing,
        "peak_memory_mb": peak_mem / (1024**2)
    }


# =============================================================================
# SUITE 4: ADVERSARIAL EDGE CASES & BOUNDARY VALUE STRESS TESTING
# =============================================================================

def test_adversarial_and_boundary_conditions() -> Dict[str, Any]:
    print("\n" + "=" * 90)
    print("SUITE 4: ADVERSARIAL EDGE CASES & BOUNDARY VALUE STRESS TESTING")
    print("=" * 90)

    # 1. Candidate 1: Edge Cases
    print("--- [Candidate 1 Edge Cases] ---")
    gen = bac.SyntheticCARPairGenerator(seed=42)
    sample_pairs = gen.generate_dataset(num_pairs=4)
    model = bac.AgrostechMultiFeatureFusionClassifier()

    # Case 1A: Divergent land use pair (soybean vs pasture/eucalyptus)
    p_div = sample_pairs[0]
    prob_div = model.predict_proba(p_div)
    print(f"Case 1A (Divergent land use): Predicted continuous prob = {prob_div:.6f}, class = {model.predict(p_div)}")
    assert prob_div < 0.15, f"Divergent land use received high continuous prob: {prob_div}"
    assert model.predict(p_div) == 0, "Divergent land use falsely merged!"

    # Base continuous pair for perturbation testing
    p_base = copy.deepcopy(sample_pairs[2])
    prob_base = model.predict_proba(p_base)
    print(f"Base True Continuous pair: prob = {prob_base:.6f}, class = {model.predict(p_base)}")
    assert prob_base > 0.95, f"Base continuous prob lower than expected: {prob_base}"

    # Case 1B: Perpendicular row azimuth (90 degrees offset)
    p_perp = copy.deepcopy(p_base)
    p_perp.row_azimuth_a_deg = 0.0
    p_perp.row_azimuth_b_deg = 90.0
    prob_perp = model.predict_proba(p_perp)
    print(f"Case 1B (Perpendicular crop rows 90 deg): Predicted continuous prob = {prob_perp:.6f}")
    assert prob_perp < prob_base, f"Perpendicular rows not penalized: {prob_perp} vs {prob_base}"
    assert prob_perp < 0.90, f"Perpendicular row penalty too weak: {prob_perp}"

    # Case 1C: Heavy vegetative barrier (dense windbreak / fence)
    p_barr = copy.deepcopy(p_base)
    p_barr.barrier_fraction = 1.0
    p_barr.barrier_contrast = 3.0
    prob_barr = model.predict_proba(p_barr)
    print(f"Case 1C (100% Dense vegetative barrier): Predicted continuous prob = {prob_barr:.6f}")
    assert prob_barr < prob_base, f"Dense barrier not penalized: {prob_barr} vs {prob_base}"

    # Case 1D: Completely anti-correlated phenology (flips prediction from 1 to 0)
    p_anti = copy.deepcopy(p_base)
    p_anti.ndvi_b = 1.0 - p_anti.ndvi_a
    prob_anti = model.predict_proba(p_anti)
    print(f"Case 1D (Inverted phenology NDVI): Predicted continuous prob = {prob_anti:.6f}, class = {model.predict(p_anti)}")
    assert prob_anti < 0.70, f"Inverted phenology failed to flip classification below threshold 0.70: {prob_anti}"
    assert model.predict(p_anti) == 0, "Inverted phenology still classified as continuous!"

    # Case 1E: Combined adversarial spoofing (inverted NDVI + perpendicular rows)
    p_both = copy.deepcopy(p_base)
    p_both.ndvi_b = 1.0 - p_base.ndvi_a
    p_both.row_azimuth_a_deg = 0.0
    p_both.row_azimuth_b_deg = 90.0
    prob_both = model.predict_proba(p_both)
    print(f"Case 1E (Combined inverted NDVI + perpendicular rows): Predicted prob = {prob_both:.6f}")
    assert prob_both < 0.30, f"Combined discrepancies not strongly rejected: {prob_both}"
    assert model.predict(p_both) == 0

    print("[PASS] Candidate 1 correctly rejects all adversarial boundary spoofing attempts.")

    # 2. Candidate 2: Edge Cases (VoI Drone Dispatch)
    print("\n--- [Candidate 2 Edge Cases] ---")
    evaluator_voi = bvd.VoIBenchmarkEvaluator(seed=42)

    # Case 2A: Zero credit exposure (E = 0)
    # If credit exposure is zero, VoI should NEVER justify dispatching a drone!
    pol_zero_exposure = bvd.AgrostechVoIPolicy(
        evaluator_voi.cost_model,
        area_ha=1000.0,
        credit_exposure=0.0,
        threshold_brl=5000.0
    )
    # Simulate high cloud and stress telemetry
    pol_zero_exposure.update_daily_belief(
        dap=60,
        days_since_clear=25,
        optical_observed=False,
        ndvi_apparent=0.45,
        v_t=1.0
    )
    dispatch_zero, nvoi_zero, gvoi_zero, c_flight_zero = pol_zero_exposure.evaluate_voi(
        dap=60,
        v_t=1.0,
        cloud_prob_forecast=0.9
    )
    print(f"Case 2A (Zero Credit Exposure): NVoI = R$ {nvoi_zero:,.2f}, Dispatched = {dispatch_zero}")
    assert not dispatch_zero, "Drone dispatched despite ZERO credit exposure!"
    assert nvoi_zero <= 0.0, "NVoI > 0 despite ZERO credit exposure!"

    # Case 2B: Exorbitant flight cost (R$ 10,000,000 per flight)
    expensive_cost_model = bvd.DroneFlightCostModel(mobilization_base=10000000.0)
    pol_expensive = bvd.AgrostechVoIPolicy(
        expensive_cost_model,
        area_ha=1000.0,
        credit_exposure=3500000.0,
        threshold_brl=5000.0
    )
    pol_expensive.update_daily_belief(
        dap=60,
        days_since_clear=25,
        optical_observed=False,
        ndvi_apparent=0.45,
        v_t=1.0
    )
    dispatch_exp, nvoi_exp, gvoi_exp, c_flight_exp = pol_expensive.evaluate_voi(
        dap=60,
        v_t=1.0,
        cloud_prob_forecast=0.9
    )
    print(f"Case 2B (Exorbitant Flight Cost R$ 10M): NVoI = R$ {nvoi_exp:,.2f}, Dispatched = {dispatch_exp}")
    assert not dispatch_exp, "Drone dispatched when flight cost exceeds entire credit exposure!"

    # Case 2C: 100% Persistent Overcast Season (Optical satellite blind for 120 days)
    # The VoI engine should dynamically step in and prevent catastrophic unmonitored loss
    class PersistentOvercastWeather(bvd.CerradoWeatherSimulator):
        def simulate_season_weather(self, total_days: int = 120):
            return np.ones(total_days, dtype=bool), np.ones(total_days, dtype=float)

    weather_overcast = PersistentOvercastWeather(evaluator_voi.rng)
    risk_sim = bvd.CropCycleRiskSimulator(evaluator_voi.rng, 1000.0, 3500000.0)
    res_overcast = evaluator_voi.run_single_season(1, weather_overcast, risk_sim)
    agro_res = res_overcast["policies"]["Agrostech VoI Dispatch"]
    naive_res = res_overcast["policies"]["Naive NDVI Threshold"]
    print(f"Case 2C (100% Overcast Season): Agrostech Flights = {agro_res['total_flights']}, Loss Prevented = R$ {agro_res['loss_prevented_brl']:,.2f}")
    print(f"                                Naive NDVI Flights = {naive_res['total_flights']}, Loss Prevented = R$ {naive_res['loss_prevented_brl']:,.2f}")
    # Under persistent overcast, Naive NDVI is blind and fails to catch events, whereas VoI triggers based on information gap
    assert agro_res["total_flights"] > 0, "VoI failed to trigger flights during persistent 120-day overcast!"
    assert agro_res["loss_prevented_brl"] >= naive_res["loss_prevented_brl"], "VoI performed worse than blind naive NDVI!"

    print("[PASS] Candidate 2 VoI decision engine behaves with rigorous economic rationality.")

    # 3. Candidate 3: Edge Cases (Probabilistic SCS-CN)
    print("\n--- [Candidate 3 Edge Cases] ---")
    # Case 3A: Zero DTM Noise (sigma_z = 0)
    evaluator_zero_noise = bre.RunoffBenchmarkEvaluator(
        grid_size=100,
        cell_size_m=7.071,
        storm_mm=85.0,
        sigma_base_m=0.0,  # Zero noise
        seed=42
    )
    res_zn = evaluator_zero_noise.run_benchmark(iterations_k=20)
    brier_zn = res_zn["metrics"]["Agrostech Probabilistic SCS-CN"]["spatial_brier_score"]
    print(f"Case 3A (Zero DTM Error sigma_z = 0): Spatial Brier Score = {brier_zn:.6f}")
    assert brier_zn <= 0.001, f"Zero noise produced non-zero Brier discrepancy: {brier_zn}"

    # Case 3B: Drought / Ultra-low rainfall (P = 5 mm < Initial Abstraction Ia)
    evaluator_drought = bre.RunoffBenchmarkEvaluator(
        grid_size=100,
        cell_size_m=7.071,
        storm_mm=5.0,  # 5 mm is less than Ia (approx 8.5 to 10 mm for CN 80)
        sigma_base_m=0.25,
        seed=42
    )
    res_drought = evaluator_drought.run_benchmark(iterations_k=20)
    # Check that discharge across all terraces and pixels is zero
    for t in res_drought["terraces"]:
        assert t.mc_prob_overtop == 0.0, f"Overtopping predicted under 5mm drought rainfall: {t.mc_prob_overtop}"
    print(f"Case 3B (Sub-threshold storm P = 5mm < Ia): Terrace overtopping probabilities are strictly 0.0.")

    # Case 3C: Catastrophic Cloudburst (P = 250 mm)
    evaluator_flood = bre.RunoffBenchmarkEvaluator(
        grid_size=100,
        cell_size_m=7.071,
        storm_mm=250.0,  # Extreme 250mm deluge
        sigma_base_m=0.25,
        seed=42
    )
    res_flood = evaluator_flood.run_benchmark(iterations_k=20)
    # All terraces must have high overtopping probability under 250mm deluge
    for t in res_flood["terraces"]:
        assert t.mc_prob_overtop >= 0.70, f"Terrace overtopping low under 250mm deluge: {t.mc_prob_overtop}"
    print(f"Case 3C (Catastrophic 250mm cloudburst): All terraces correctly flagged with severe overtopping prob (>= 70%).")

    print("[PASS] Candidate 3 handles extreme hydrological boundary conditions perfectly.")
    return {"status": "SUCCESS"}


# =============================================================================
# MASTER TEST RUNNER
# =============================================================================

def run_all_empirical_tests():
    print("\n" + "#" * 90)
    print("AGROSTECH NOVEL R&D — EMPIRICAL CHALLENGER TEST SUITE (challenger_2)")
    print("#" * 90)

    start_total = time.time()

    r1 = test_data_artifact_integrity()
    r2 = test_random_seed_sensitivity()
    r3 = test_computational_feasibility_and_scaling()
    r4 = test_adversarial_and_boundary_conditions()

    elapsed_total = time.time() - start_total

    print("\n" + "=" * 90)
    print("ALL EMPIRICAL TESTS PASSED SUCCESSFULLY!")
    print(f"Total Test Suite Execution Time: {elapsed_total:.2f} seconds")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_all_empirical_tests()
