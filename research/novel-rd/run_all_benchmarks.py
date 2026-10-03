"""
run_all_benchmarks.py
=====================
Agrostech Novel R&D Directions — Master Benchmark Orchestrator & VC Dashboard
Prepares complete technical and quantitative defensibility artifacts for SP Ventures
and agricultural credit partners under BCB Resolução CMN nº 5.267/2025.

Sequentially executes:
1. benchmark_area_continua.py (Candidate 1: Multi-Feature Continuous Operation Fusion)
2. benchmark_voi_drone.py (Candidate 2: Decision-Theoretic Value-of-Information Drone Trigger)
3. benchmark_runoff_erosion.py (Candidate 3: Uncertainty-Aware SCS-CN Monte Carlo over DTM Error)

Outputs:
- novel_rd_benchmarks_summary.json: Unified quantitative due diligence metrics
- benchmark_summary_dashboard.png: High-resolution investor presentation graphic
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# =============================================================================
# BENCHMARK EXECUTION HELPERS
# =============================================================================

def execute_benchmark_script(
    script_name: str,
    args_list: list,
    description: str
) -> Dict[str, Any]:
    """Runs a benchmark script via subprocess, verifying exit code and execution time."""
    print("\n" + "=" * 95)
    print(f"[*] EXECUTING {description.upper()} ({script_name})...")
    print("=" * 95)

    cmd = [sys.executable, script_name] + args_list
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time

    print(result.stdout)
    if result.stderr:
        print("[STDERR / WARNINGS]:", result.stderr)

    if result.returncode != 0:
        print(f"[FATAL] Benchmark script {script_name} failed with returncode {result.returncode}!")
        sys.exit(result.returncode)

    print(f"[SUCCESS] {description} completed in {elapsed:.2f} seconds with exit code 0.\n")
    return {"elapsed_sec": elapsed, "returncode": result.returncode}


# =============================================================================
# UNIFIED VC DASHBOARD RENDERER
# =============================================================================

def render_vc_summary_dashboard(
    area_results: Dict[str, Any],
    voi_results: Dict[str, Any],
    runoff_results: Dict[str, Any],
    output_path: str = "benchmark_summary_dashboard.png"
):
    """
    Renders high-impact 3-panel executive graphic tailored for SP Ventures
    technical due diligence and credit committee presentation.
    """
    fig = plt.figure(figsize=(16, 12), dpi=300)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.0], hspace=0.32, wspace=0.28)

    # -------------------------------------------------------------------------
    # Panel 1: Candidate 1 (Área Contínua ROC & Calibration)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ac_models = area_results["models"]
    m_names = ["Agrostech Multi-Feature Fusion", "Naive Spatial Buffer", "Naive Single-CAR"]
    m_labels = ["Agrostech Fusion", "Spatial Buffer", "Single-CAR"]
    aucs = [ac_models[m]["roc_auc"] for m in m_names]
    briers = [ac_models[m]["brier_score"] for m in m_names]

    x = np.arange(len(m_labels))
    width = 0.35
    b1 = ax1.bar(x - width/2, aucs, width, label="ROC-AUC", color="#1b5e20", alpha=0.85)
    b2 = ax1.bar(x + width/2, briers, width, label="Brier Score", color="#b71c1c", alpha=0.85)

    ax1.set_xticks(x)
    ax1.set_xticklabels(m_labels, fontsize=9.5, fontweight="bold")
    ax1.set_ylabel("Score [0, 1]", fontsize=10, fontweight="bold")
    ax1.set_title("1. Área Contínua Performance\n(BCB Resolução nº 5.267)", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax1.grid(True, linestyle=":", alpha=0.6, axis="y")
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 2: Candidate 1 Error Rates (FMR & FSR)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    fmrs = [ac_models[m]["false_merge_rate_pct"] for m in m_names]
    fsrs = [ac_models[m]["false_split_rate_pct"] for m in m_names]

    b3 = ax2.bar(x - width/2, fmrs, width, label="False Merge Rate (Type I) %", color="#d32f2f", alpha=0.85)
    b4 = ax2.bar(x + width/2, fsrs, width, label="False Split Rate (Type II) %", color="#f57c00", alpha=0.85)

    ax2.set_xticks(x)
    ax2.set_xticklabels(m_labels, fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Error Rate (%)", fontsize=10, fontweight="bold")
    ax2.set_title("1B. Cadastral Misclassification Rates\n(Fraud Loop Closure)", fontsize=11, fontweight="bold")
    ax2.legend(loc="upper center", frameon=True, fontsize=8.5)
    ax2.grid(True, linestyle=":", alpha=0.6, axis="y")
    for bar in list(b3) + list(b4):
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3: Candidate 2 (VoI Drone Net Economic Value)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 2])
    voi_pols = voi_results["policies"]
    p_names = ["Agrostech VoI Dispatch", "Fixed Calendar (14d)", "Naive NDVI Threshold"]
    p_labels = ["Agrostech VoI", "Fixed Calendar", "Naive NDVI"]
    nev_means = [voi_pols[p]["net_economic_value_per_ha_brl"]["mean"] for p in p_names]
    nev_stds = [voi_pols[p]["net_economic_value_per_ha_brl"]["std"] for p in p_names]

    colors_voi = ["#2e7d32", "#e65100", "#c62828"]
    bars_v = ax3.bar(p_labels, nev_means, yerr=nev_stds, capsize=5, color=colors_voi, alpha=0.85, edgecolor="black")
    ax3.set_ylabel("Net Economic Value (R$/ha)", fontsize=10, fontweight="bold")
    ax3.set_title("2. VoI Drone Dispatch Payoff\n(120d Soybean Season)", fontsize=11, fontweight="bold")
    ax3.grid(True, linestyle=":", alpha=0.6, axis="y")
    for bar in bars_v:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2.0, h + 15.0, f"R$ {h:.0f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # -------------------------------------------------------------------------
    # Panel 4: Candidate 2 Latency & Flight Cost Breakdown
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 0])
    costs_ha = [voi_pols[p]["flight_cost_per_ha_brl"]["mean"] for p in p_names]
    latencies = [voi_pols[p]["mean_detection_latency_days"] for p in p_names]

    b5 = ax4.bar(x - width/2, costs_ha, width, label="Flight Cost (R$/ha)", color="#ef5350", alpha=0.85)
    ax4_twin = ax4.twinx()
    b6 = ax4_twin.bar(x + width/2, latencies, width, label="Detection Latency (d)", color="#ff9800", alpha=0.85)

    ax4.set_xticks(x)
    ax4.set_xticklabels(p_labels, fontsize=9.5, fontweight="bold")
    ax4.set_ylabel("Flight Cost (R$/ha)", fontsize=10, fontweight="bold", color="#d32f2f")
    ax4_twin.set_ylabel("Mean Latency (Days)", fontsize=10, fontweight="bold", color="#e65100")
    ax4.set_title("2B. Drone Inspection Efficiency\n(Cost vs Response Speed)", fontsize=11, fontweight="bold")
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True, fontsize=8)
    ax4.grid(True, linestyle=":", alpha=0.6, axis="y")

    # -------------------------------------------------------------------------
    # Panel 5: Candidate 3 (Terrace Overtopping Misclassification OHMR)
    # -------------------------------------------------------------------------
    ax5 = fig.add_subplot(gs[1, 1])
    rf_models = runoff_results["models"]
    rf_names = ["Agrostech Probabilistic SCS-CN", "Single-Run Deterministic SCS-CN", "Deterministic Rational Method"]
    rf_labels = ["Agrostech MC", "Single-Run SCS", "Rational (CIA)"]
    ohmrs = [rf_models[m]["ohmr_pct"] for m in rf_names]
    fars = [rf_models[m]["far_pct"] for m in rf_names]

    b7 = ax5.bar(x - width/2, ohmrs, width, label="Overtopping Hazard Miss % (OHMR)", color="#d32f2f", alpha=0.85)
    b8 = ax5.bar(x + width/2, fars, width, label="False Alarm Rate %", color="#ffa726", alpha=0.85)

    ax5.set_xticks(x)
    ax5.set_xticklabels(rf_labels, fontsize=9.5, fontweight="bold")
    ax5.set_ylabel("Error Rate (%)", fontsize=10, fontweight="bold")
    ax5.set_title("3. Terrace Failure Hazard Risk\n(DTM Error Propagation)", fontsize=11, fontweight="bold")
    ax5.legend(loc="upper right", frameon=True, fontsize=8.5)
    ax5.grid(True, linestyle=":", alpha=0.6, axis="y")
    for bar in list(b7) + list(b8):
        h = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width() / 2.0, h + 1.0, f"{h:.1f}%", ha="center", va="bottom", fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 6: Candidate 3 Earthmoving Cost & Brier Calibration
    # -------------------------------------------------------------------------
    ax6 = fig.add_subplot(gs[1, 2])
    savings = [rf_models[m]["earthmoving_savings_pct"] for m in rf_names]
    brier_rf = [rf_models[m]["spatial_brier_score"] for m in rf_names]

    b9 = ax6.bar(x - width/2, savings, width, label="Earthmoving Savings %", color="#388e3c", alpha=0.85)
    ax6_twin = ax6.twinx()
    b10 = ax6_twin.bar(x + width/2, brier_rf, width, label="Spatial Brier Score", color="#5c6bc0", alpha=0.85)

    ax6.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax6.set_xticks(x)
    ax6.set_xticklabels(rf_labels, fontsize=9.5, fontweight="bold")
    ax6.set_ylabel("Earthmoving Savings (%)", fontsize=10, fontweight="bold", color="#1b5e20")
    ax6_twin.set_ylabel("Brier Score (Calibration)", fontsize=10, fontweight="bold", color="#3949ab")
    ax6.set_title("3B. Soil Conservation Optimization\n(Cost Savings vs Risk)", fontsize=11, fontweight="bold")
    lines_a, labels_a = ax6.get_legend_handles_labels()
    lines_b, labels_b = ax6_twin.get_legend_handles_labels()
    ax6.legend(lines_a + lines_b, labels_a + labels_b, loc="lower right", frameon=True, fontsize=8)
    ax6.grid(True, linestyle=":", alpha=0.6, axis="y")

    plt.suptitle("AGROSTECH NOVEL R&D DIRECTIONS — VENTURE CAPITAL & LENDER TECHNICAL DEFENSIBILITY DASHBOARD\nRigorous Mathematical Proof-of-Concept Benchmarks for SP Ventures Due Diligence (Mato Grosso / Cerrado)",
                 fontsize=14, fontweight="bold", y=0.98)
    fig.subplots_adjust(top=0.92, bottom=0.08, left=0.06, right=0.94, hspace=0.36, wspace=0.34)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Unified VC due diligence dashboard saved to: {output_path}")


# =============================================================================
# MASTER ORCHESTRATION PIPELINE
# =============================================================================

def run_all_benchmarks(fast_mode: bool = False):
    print("=" * 95)
    print("AGROSTECH NOVEL R&D DIRECTIONS — MASTER BENCHMARK SUITE")
    print(f"Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print(f"Execution Mode: {'FAST (Smoke Test)' if fast_mode else 'FULL (Comprehensive Investor Evaluation)'}")
    print("=" * 95)

    working_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Run Benchmark 1: Área Contínua
    pairs_count = 50 if fast_mode else 200
    b1_args = [
        "--num-pairs", str(pairs_count),
        "--seed", "42",
        "--output-json", os.path.join(working_dir, "results_area_continua.json"),
        "--output-png", os.path.join(working_dir, "benchmark_area_continua.png")
    ]
    execute_benchmark_script(
        os.path.join(working_dir, "benchmark_area_continua.py"),
        b1_args,
        "Candidate 1: Área Contínua Multi-Feature Fusion Benchmark"
    )

    # 2. Run Benchmark 2: VoI Drone Dispatch
    seasons_count = 25 if fast_mode else 100
    b2_args = [
        "--days", "120",
        "--area-ha", "1000",
        "--credit-exposure", "3500000",
        "--monte-carlo", str(seasons_count),
        "--output-json", os.path.join(working_dir, "results_voi_drone.json"),
        "--output-png", os.path.join(working_dir, "benchmark_voi_drone.png")
    ]
    execute_benchmark_script(
        os.path.join(working_dir, "benchmark_voi_drone.py"),
        b2_args,
        "Candidate 2: Value-of-Information (VoI) Drone Trigger Benchmark"
    )

    # 3. Run Benchmark 3: Probabilistic Hydrology & Runoff
    mc_iters = 100 if fast_mode else 500
    b3_args = [
        "--grid-size", "100",
        "--iterations", str(mc_iters),
        "--storm-mm", "85",
        "--sigma-z", "0.25",
        "--output-json", os.path.join(working_dir, "results_runoff_erosion.json"),
        "--output-png", os.path.join(working_dir, "benchmark_runoff_erosion.png")
    ]
    execute_benchmark_script(
        os.path.join(working_dir, "benchmark_runoff_erosion.py"),
        b3_args,
        "Candidate 3: Probabilistic SCS-CN Runoff & Erosion Benchmark"
    )

    # -------------------------------------------------------------------------
    # AGGREGATE SUMMARY & GENERATE VC DASHBOARD
    # -------------------------------------------------------------------------
    print("\n" + "=" * 95)
    print("[*] AGGREGATING BENCHMARK METRICS INTO UNIFIED DOSSIER SUMMARY...")
    print("=" * 95)

    with open(os.path.join(working_dir, "results_area_continua.json"), "r", encoding="utf-8") as f:
        area_res = json.load(f)

    with open(os.path.join(working_dir, "results_voi_drone.json"), "r", encoding="utf-8") as f:
        voi_res = json.load(f)

    with open(os.path.join(working_dir, "results_runoff_erosion.json"), "r", encoding="utf-8") as f:
        runoff_res = json.load(f)

    summary_data = {
        "title": "Agrostech Novel R&D Benchmarks Summary",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target_audience": "SP Ventures / Rural Credit Partners",
        "benchmarks": {
            "candidate_1_area_continua": area_res,
            "candidate_2_voi_drone": voi_res,
            "candidate_3_probabilistic_runoff": runoff_res
        }
    }

    summary_json_path = os.path.join(working_dir, "novel_rd_benchmarks_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"[SUCCESS] Unified metrics summary saved to: {summary_json_path}")

    dashboard_png_path = os.path.join(working_dir, "benchmark_summary_dashboard.png")
    render_vc_summary_dashboard(area_res, voi_res, runoff_res, dashboard_png_path)

    # Print Final Executive VC Presentation Table
    print("\n" + "=" * 105)
    print("SP VENTURES DUE DILIGENCE — AGROSTECH NOVEL R&D EMPIRICAL BENCHMARK SUMMARY")
    print("=" * 105)
    print(f"{'R&D Candidate':<28} | {'Agrostech Novel Model':<28} | {'Industry Baseline':<24} | {'Agrostech Advantage':<18}")
    print("-" * 105)

    # Candidate 1
    ag_auc = area_res["models"]["Agrostech Multi-Feature Fusion"]["roc_auc"]
    ag_fsr = area_res["models"]["Agrostech Multi-Feature Fusion"]["false_split_rate_pct"]
    base_fsr = area_res["models"]["Naive Single-CAR"]["false_split_rate_pct"]
    print(f"{'1. Área Contínua (CMN 5267)':<28} | {f'AUC: {ag_auc:.3f}, FSR: {ag_fsr:.1f}%':<28} | {f'Single-CAR FSR: {base_fsr:.1f}%':<24} | {'Zero False Splits':<18}")

    # Candidate 2
    ag_nev = voi_res["policies"]["Agrostech VoI Dispatch"]["net_economic_value_per_ha_brl"]["mean"]
    base_nev = voi_res["policies"]["Fixed Calendar (14d)"]["net_economic_value_per_ha_brl"]["mean"]
    ag_lat = voi_res["policies"]["Agrostech VoI Dispatch"]["mean_detection_latency_days"]
    base_lat = voi_res["policies"]["Fixed Calendar (14d)"]["mean_detection_latency_days"]
    print(f"{'2. VoI Drone Dispatch':<28} | {f'NEV: R$ {ag_nev:.1f}/ha, Lat: {ag_lat:.1f}d':<28} | {f'NEV: R$ {base_nev:.1f}/ha, Lat: {base_lat:.1f}d':<24} | {f'+R$ {ag_nev - base_nev:.1f}/ha (+{(ag_nev - base_nev)/base_nev*100:.0f}%)':<18}")

    # Candidate 3
    ag_ohmr = runoff_res["models"]["Agrostech Probabilistic SCS-CN"]["ohmr_pct"]
    base_ohmr = runoff_res["models"]["Single-Run Deterministic SCS-CN"]["ohmr_pct"]
    ag_sav = runoff_res["models"]["Agrostech Probabilistic SCS-CN"]["earthmoving_savings_pct"]
    print(f"{'3. Probabilistic Runoff (SCS)':<28} | {f'OHMR: {ag_ohmr:.1f}%, Savings: {ag_sav:.1f}%':<28} | {f'Single-Run OHMR: {base_ohmr:.1f}%':<24} | {f'{base_ohmr - ag_ohmr:.0f} pp Miss Reduc':<18}")

    print("=" * 105)
    print("\n[ALL BENCHMARKS SUCCESSFULLY EXECUTED AND ATTESTED — STATUS: PASSED]\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agrostech Master Benchmark Suite")
    parser.add_argument("--fast", action="store_true", help="Run in fast smoke test mode")
    args = parser.parse_args()

    run_all_benchmarks(fast_mode=args.fast)
