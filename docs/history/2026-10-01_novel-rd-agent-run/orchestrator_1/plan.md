# Plan: Agrostech Novel R&D Directions Dossier & POC Benchmarks

## Goal
Conduct comprehensive R&D investigation, formalize mathematical models, build runnable Python PoC benchmark test suites, and write an institutional Executive & Technical Defensibility Whitepaper for SP Ventures and credit lenders across three novel directions:
1. Área Contínua detection across property boundaries under CMN Res. 5.267
2. Value-of-Information (VoI) trigger-based drone dispatch
3. Uncertainty-aware probabilistic runoff & erosion risk (SCS-CN Monte Carlo over DTM error)

## Phases

### Phase 0: Survey & Scoping (Current)
- Dispatch 3 Explorers / Spec Miners:
  - Explorer 1 (Legal, Prior-Art & Landscape): Focus on Brazilian rural credit regulations (CMN Res. 5.267, SICAR, CAR, ZARC, Forest Code), academic literature on field boundary detection, continuous operation, and patent/INPI search strategies.
  - Explorer 2 (Mathematical Formulation & Decision Theory): Focus on mathematical modeling of multi-feature fusion (phenology time series, Sentinel-1/NISAR coherence, machinery pass/row azimuths), VoI decision-theoretic dispatch equations under cloud cover/credit risk, and SCS-CN distributed Monte Carlo DTM vertical error equations.
  - Explorer 3 (Benchmark Architecture & Implementation Environment): Focus on working directory setup (`c:/Users/Razer/Desktop/Agrostech/novel_rd_directions`), Python environment, dependencies, synthetic dataset generation, and verification metrics (Brier score, ROC-AUC, cost savings/ha, false escalation rate).
- Synthesize findings into `PROJECT.md` with Feature Inventory, Milestones, and Interface Contracts.

### Phase 1: Milestone 1 — Prior-Art & Patent Landscape Clearance (R1)
- Systematic prior-art clearance for all 3 candidates (at least 3 closest prior-art publications or patents per candidate).
- Clear demarcation of commodity methods vs. Agrostech patentable novelty.
- Freedom-to-operate and IP moat analysis for Brazilian and international markets.

### Phase 2: Milestone 2 — Original Mathematical Formulations & Algorithmic Specifications (R2)
- Mathematical derivation for Candidate 1 (Área Contínua Multi-Feature Fusion).
- Mathematical derivation for Candidate 2 (VoI-Driven Drone Dispatch Decision Model).
- Mathematical derivation for Candidate 3 (Distributed SCS-CN Monte Carlo over DTM Error).
- Step-by-step algorithmic pseudocode with dimensional consistency, units, and boundary constraints.

### Phase 3: Milestone 3 — Benchmark Protocol & Executable Verification Scripts (R3)
- Reproducible Python proof-of-concept scripts in `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/`:
  - `benchmark_area_continua.py` (Single-CAR vs Multi-Feature Fusion Surface).
  - `benchmark_voi_drone.py` (Fixed calendar vs VoI trigger dispatch).
  - `benchmark_runoff_erosion.py` (Deterministic Rational Method vs Probabilistic SCS-CN Monte Carlo).
- Comparative benchmark metrics generation and automated validation.

### Phase 4: Milestone 4 — Executive & Technical Defensibility Dossier (R4)
- Author `c:/Users/Razer/Desktop/Agrostech/novel_rd_directions/AGROSTECH_NOVEL_RD_DOSSIER.md`.
- Executive summary, commercial moats, IP defensibility.
- Regulatory alignment mapping (CMN Res. 5.267 fiscalização, ZarcNM, Forest Code 45°).
- Ground-truth pilot requirements (RTK points, rain gauges, rill surveys).
- 12-month R&D and field validation roadmap with milestone gates.

### Phase 5: Verification & Gate Review
- Verification loop: Reviewers, Challengers, and Forensic Auditor verification.
- Final synthesis and reporting to parent.
