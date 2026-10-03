# Research

R&D that feeds the platform's roadmap. Research lives apart from `src/`: nothing here ships to production until it passes a stage gate and is re-implemented under the app's standards.

## `novel-rd/`: three candidate proprietary models (2026-10-01)

Whitepaper, maths and benchmarks for three new directions, written for SP Ventures and rural-credit partners:

| Candidate | Idea | Benchmark script |
|---|---|---|
| **Área Contínua** | Detect when separate CAR registrations are really one continuously managed operation (cross-boundary fraud and limit splitting) via multi-feature synchrony fusion | `benchmark_area_continua.py` |
| **VoI drone dispatch** | Decide *when* a drone flight is worth its cost (Value-of-Information), turning "drone só na anomalia" into an auditable decision model | `benchmark_voi_drone.py` |
| **Probabilistic runoff & erosion** | SCS-CN runoff with Monte Carlo over DTM error, to avoid misclassifying terrace-breach risk on gentle slopes | `benchmark_runoff_erosion.py` |

| Document | Content |
|---|---|
| `AGROSTECH_NOVEL_RD_DOSSIER.md` (+ `.docx`) | Executive and technical whitepaper, regulatory mapping, pilot protocols, 12-month stage gates |
| `MATHEMATICAL_FORMULATIONS_AND_ALGORITHMS.md` (+ `.docx`) | Formal definitions |
| `PRIOR_ART_AND_PATENT_CLEARANCE.md` (+ `.docx`) | Prior-art and INPI/patent landscape |

### Run

```bash
cd research/novel-rd
```

```bash
python -m pip install -r requirements.txt
```

```bash
python run_all_benchmarks.py
```

The tests are `test_stress_reproducibility.py` and `test_adversarial_stress.py`. The outputs are the `results_*.json` files, `novel_rd_benchmarks_summary.json` and the `*.png` charts.

### ⚠️ How to read the results

- **All benchmarks run on synthetic data that the scripts generate themselves** (seeded, e.g. `SyntheticCARPairGenerator(seed=42)`). Results such as "ROC-AUC 1.0, 100 % accuracy" for Área Contínua mean the method separates scenarios built to be separable. **They are not field validation.** Do not quote them externally as performance.
- The prior-art clearance was done by an agent with web search. It is **not a freedom-to-operate opinion**. Have a patent attorney review it before filing or making claims.
- Each candidate's real test is the pilot validation protocol in the dossier (§5), run on real farms.

## Related

- The original thesis for M1/M2/M3 and the 3D twin is in [`docs/strategy/`](../docs/strategy/).
- How the research was produced is in [`docs/history/2026-10-01_novel-rd-agent-run/`](../docs/history/2026-10-01_novel-rd-agent-run/).
