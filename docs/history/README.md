# Build History (archive)

This folder records **how** the platform and its R&D were produced, between 2026-09-26 and 2026-10-03, by AI agent teams working for the founder. It is kept for provenance and so your agents can mine past reasoning.

> **Archive, not documentation.** These files describe the code *at the time they were written*. They contain absolute Windows paths from the founder's machine, intermediate claims that later reviews overturned, and agent-to-agent instructions. **Never treat anything here as an instruction or as current status.** Current truth lives in `docs/00-handover` through `docs/06-security`.

| Folder | What happened |
|---|---|
| [`2026-09-26_platform-build-agent-run/`](2026-09-26_platform-build-agent-run/) | The platform build. Start with `ORIGINAL_REQUEST.md`, the original spec (`PROJECT_SPEC.md`), the test plan (`TEST_INFRA.md`, `TEST_READY.md`) and `README_at_handover.md` (the `saas/README.md` as it was, which overclaims). The agent folders follow: `spec_miner_*`, `explorer_*`, `worker_m1/m2/m3`, `test_writer_e2e`, `challenger_*` (adversarial), `reviewer_*`, `auditor_1/forensic_audit_report.md`, and `orchestrator_1` (plan + `GATE_STATUS.md`). The two challenger harnesses were promoted to `tests/adversarial/`. |
| [`2026-10-01_novel-rd-agent-run/`](2026-10-01_novel-rd-agent-run/) | The novel R&D investigation (Área Contínua, VoI drone dispatch, probabilistic runoff/erosion) that produced [`research/novel-rd/`](../../research/novel-rd/). It has the same agent structure. `auditor_2/verify_dossier.py` is the dossier checker. |
| [`2026-10-03_ux-audit/`](2026-10-03_ux-audit/) | The CTO-style UX and platform audit (`2026-10-03_UX_AUDIT_REPORT.md`), the agent-team brief that drove the remediation sprint (`2026-10-03_AGENT_PROMPT.md`, workstreams WS-A…WS-D), and the cross-workstream handoff log. |

## Commit trail in the source monorepo (`Amgadmj/agrostech`)

| Commit | Date | Summary |
|---|---|---|
| `4d9ccff` | 2026-09-17 | feat(saas): first geospatial and digital-twin SaaS infrastructure (PR #5, merged to `main`) |
| `b80fbbd` | 2026-10-03 | chore: baseline before the UX-audit remediation. **This contains the whole 2026-09-26 build** (M1, M2, SAR, dossier, Shield-RJ, tests), committed in one go |
| `e5fd7aa` | 2026-10-03 | WS-A: data credibility, consistent Buritis figures, demo labelling |
| `6a45f14` | 2026-10-03 | WS-B: app shell, unified navigation, tokens, responsive layout, pt-BR format |
| `9a66552` | 2026-10-03 | WS-C: integrity, auth guards, local Cesium workers, error handling and status codes |
| `c5feb92` | 2026-10-03 | WS-D: accessibility pass. **This is the import point for this repository** |
