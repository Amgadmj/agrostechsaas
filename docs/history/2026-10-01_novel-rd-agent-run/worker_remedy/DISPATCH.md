# Dispatch: Forensic Integrity Remediation Worker (worker_remedy)

**Assigned Agent**: worker_remedy
**Role**: Forensic Integrity Remediation Worker
**Working Directory**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_remedy
**Original Request Path**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/ORIGINAL_REQUEST.md
**Project Plan Path**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/orchestrator_1/PROJECT.md
**Auditor Report Path**: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/auditor_1/handoff.md
**Explorer Handoffs**:
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_1/handoff.md` (Detailed volumetric math and code lines)
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_2/handoff.md` (Detailed dossier text replacements)
- `c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_3/handoff.md` (Step-by-step remediation plan and verification)

## Mandatory Tasks

### Task 1: Eliminate Hardcoded Literals in `benchmark_runoff_erosion.py`
Follow the exact instructions and code blocks from `explorer_remedy_1/handoff.md` and `explorer_remedy_3/handoff.md`:
1. In `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/benchmark_runoff_erosion.py`:
   - Set $q_{\text{crit}} = 0.010\text{ m}^3/\text{s}$ (line 401) and update the plot title (line 568) so that spatial exceedance activates active drainage swales.
   - Implement the dynamic volumetric terrace excavation calculation:
     * $d_{\text{water}, j} = \sqrt{\frac{2 S_0 V_{\text{design}, j}}{L_j}}$
     * $h_{\text{embankment}, j} = d_{\text{water}, j} + h_{\text{fb}}$ ($h_{\text{fb}} = 0.25\text{ m}$)
     * $w_{\text{base}, j} = 2 z_s h_{\text{embankment}, j}$ ($z_s = 2.0$)
     * $A_{\text{cross}, j} = 2 z_s h_{\text{embankment}, j}^2$
     * $V_{\text{excavation}} = \sum_j A_{\text{cross}, j} L_j$
   - Sizing policies:
     * Baseline (Single-Run Deterministic): sizes to single-run inflow with standard $FS_{\text{det}} = 1.35$ on noisy DTM ($0.0\%$ baseline savings).
     * Agrostech Probabilistic SCS-CN: sizes to Monte Carlo expected inflow $\mu_{\text{inflow}, j}$ across the GRF error field, eliminating redundant over-excavation while maintaining zero overtopping.
     * Deterministic Rational Method: sizes a uniform template based on critical downslope catchment, resulting in over-excavation penalty.
     * Compute volumetric savings: $\text{earthmoving\_savings\_pct} = \frac{V_{\text{base}} - V_{\text{model}}}{V_{\text{base}}} \times 100\%$.
   - Calculate dynamic spatial Brier scores across all 3 models using dynamic Rational exceedance surface.
   - Remove hardcoded constants `24.5`, `0.0`, `-15.0`, and `brier_rat = 0.44`.

### Task 2: Re-Execute Benchmark Suite
1. Run `python run_all_benchmarks.py` in `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/`.
2. Verify exit code 0 and refresh all 4 JSON files and 4 PNG plots.
3. Run `python test_stress_reproducibility.py` to ensure all tests pass.

### Task 3: Synchronize `AGROSTECH_NOVEL_RD_DOSSIER.md`
Follow the exact drop-in replacement blocks from `explorer_remedy_2/handoff.md`:
1. In `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/AGROSTECH_NOVEL_RD_DOSSIER.md`:
   - Replace lines 27–29 (Executive Summary At-A-Glance) with true empirical numbers.
   - Replace lines 349–359 (Table 4) with the exact empirical numbers from the refreshed JSON files:
     * Candidate 2: R$ 661.36/ha Net Economic Value (+50.1% vs R$ 440.66/ha Fixed), 4.24 days Latency (vs 6.00d Fixed, 8.67d Naive), 63.8% Early Capture (vs 47.0% Fixed, 28.0% Naive), 49.8% False Escalation Rate (vs 58.9% Fixed, 70.3% Naive), R$ 63.90/ha Flight Cost (vs R$ 89.60/ha Fixed).
     * Candidate 3: 0.0% OHMR (vs 100.0% Single-Run miss rate), dynamic spatial Brier scores, and the genuine computed volumetric earthmoving savings.
   - Replace lines 361–367 (Takeaways and footnote) to match the empirical data.

### Task 4: Verify Zero Hardcoded Literals
Ensure `grep` for static literals returns 0 matches.
Document all before-and-after diffs, execution logs, and verified values in your handoff report:

## 2026-10-01T21:57:27Z
You are worker_remedy (Forensic Integrity Remediation Worker) for Agrostech's Novel R&D directions.
Your working directory is: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_remedy
Read your dispatch instructions in: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_remedy/DISPATCH.md
Read the original request in: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/ORIGINAL_REQUEST.md
Read the auditor handoff in: c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/auditor_1/handoff.md
Read the three remediation explorer handoffs:
- c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_1/handoff.md
- c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_2/handoff.md
- c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/explorer_remedy_3/handoff.md

Execute all 4 tasks in DISPATCH.md:
1. Eliminate hardcoded literals in benchmark_runoff_erosion.py by implementing genuine volumetric earthmoving calculations (V = z * h^2 * L) and dynamic spatial Brier scoring.
2. Re-run `python run_all_benchmarks.py` and `python test_stress_reproducibility.py` to refresh all JSON outputs and PNG plots with exit code 0.
3. Synchronize AGROSTECH_NOVEL_RD_DOSSIER.md so that all table values and text claims 100% match the refreshed empirical JSON numbers.
4. Verify that zero hardcoded literals remain.

Document your work, verification runs, and exact metrics in:
c:/Users/Razer/Desktop/Agrostech/.agents/teamwork/worker_remedy/handoff.md
Send a message when complete.
