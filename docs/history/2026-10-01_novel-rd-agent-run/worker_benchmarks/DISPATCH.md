# Dispatch: Benchmark & PoC Implementation Worker

**Assigned Agent**: worker_benchmarks
**Role**: Benchmark & PoC Implementation Worker
**Working Directory**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_benchmarks
**Original Request Path**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/ORIGINAL_REQUEST.md
**Project Plan Path**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/orchestrator_1/PROJECT.md

## Exclusive File Ownership
You exclusively own and write to the following files in `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/`:
- `benchmark_area_continua.py`
- `benchmark_voi_drone.py`
- `benchmark_runoff_erosion.py`
- `run_all_benchmarks.py`
- Any generated benchmark output data files (`results_*.json`, `*.png`)

## Inputs & Specifications to Read
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/ORIGINAL_REQUEST.md` (Mandatory read)
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_survey_2/handoff.md` (Mathematical formulas, variables, and Algorithms 1, 2, and 3)
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_survey_3/handoff.md` (Detailed benchmark specifications, zero-dependency GIS design, classes, CLI flags, metrics)

## Tasks & Deliverables
1. **Implement `benchmark_area_continua.py`**:
   - Zero-dependency geospatial design (pure Python + NumPy + SciPy + Matplotlib + Shapely).
   - Generates 200 synthetic paired CAR boundaries across 4 realistic Cerrado operational scenarios.
   - Evaluates Naive Single-CAR clipping and Spatial Buffering baselines vs Agrostech Multi-Feature Fusion ($S_{\text{pheno}}, S_{\text{SAR}}, S_{\text{azimuth}}, S_{\text{perm}}$).
   - Computes ROC-AUC, Brier score, False Merge Rate (FMR), False Split Rate (FSR), and Jaccard IoU.
   - Saves `results_area_continua.json` and renders `benchmark_area_continua.png`.
2. **Implement `benchmark_voi_drone.py`**:
   - 120-day stochastic soybean cycle simulation with cloud cover Markov chain in Mato Grosso.
   - Compares Fixed Calendar and Naive NDVI threshold baselines vs Agrostech Decision-Theoretic VoI dispatch ($\text{NVoI} = \text{GVoI} - C_{\text{flight}}$).
   - Computes Net Economic Value (NEV), flight cost/ha, detection latency, and false escalation rate.
   - Saves `results_voi_drone.json` and renders `benchmark_voi_drone.png`.
3. **Implement `benchmark_runoff_erosion.py`**:
   - 50 ha rolling Cerrado micro-catchment with 4 contour terraces.
   - Generates spatially correlated 2D Gaussian Random Field DTM errors ($\sigma_z = 0.25\text{ m}, L_{\text{corr}} = 20\text{ m}$) via 2D FFT spectral convolution.
   - Compares Deterministic Rational Method ($Q=CIA$) and Single-Run SCS-CN vs Agrostech Probabilistic SCS-CN Monte Carlo (500 iterations).
   - Computes Terrace Overtopping Hazard Misclassification Rate (OHMR), runoff exceedance probabilities $P(Q > Q_{\text{crit}})$, and spatial risk variance surface.
   - Saves `results_runoff_erosion.json` and renders `benchmark_runoff_erosion.png`.
4. **Implement `run_all_benchmarks.py`**:
   - Master orchestrator running all 3 benchmarks sequentially, aggregating metrics into `novel_rd_benchmarks_summary.json` and producing a unified VC dashboard `benchmark_summary_dashboard.png`.
5. **Execute and Verify**:
   - Run `python run_all_benchmarks.py` in `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/`.
   - Ensure all scripts execute cleanly with returncode 0 and generate all JSON and PNG artifacts.
   - Include execution logs and exact metric outputs in your handoff report.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write your handoff report to: `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_benchmarks/handoff.md`.

## 2026-10-01T21:09:20Z
[Message] timestamp=2026-10-01T21:09:20Z sender=72ef1a57-61b6-4a7a-aa8d-c95a675f260d priority=MESSAGE_PRIORITY_HIGH content=You are worker_benchmarks (Benchmark & PoC Implementation Worker) for Agrostech's Novel R&D directions.
Your working directory is: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_benchmarks
Read your dispatch instructions in: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_benchmarks/DISPATCH.md
Read the original request in: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/ORIGINAL_REQUEST.md
Read the survey handoffs in:
- c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_survey_2/handoff.md
- c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_survey_3/handoff.md

You exclusively own and write code in c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/:
- benchmark_area_continua.py
- benchmark_voi_drone.py
- benchmark_runoff_erosion.py
- run_all_benchmarks.py

Implement all 4 scripts with genuine, rigorous algorithms. Follow the zero-dependency geospatial design (Python 3.12 + numpy + scipy + pandas + matplotlib + shapely).
Run `python run_all_benchmarks.py` using your tools to execute all benchmarks, generate the JSON metrics files and PNG plots, and verify that all benchmarks pass with returncode 0.
Document your implementation, execution commands, and exact quantitative results in:
c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_benchmarks/handoff.md
Send a message when complete.

