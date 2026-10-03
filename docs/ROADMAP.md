# Technical Roadmap

This roadmap is the engineering view. It is sequenced so that **credibility comes before features**. The business phases (pilots, raise milestones) are in [`strategy/data-room-product/ROADMAP.md`](strategy/data-room-product/ROADMAP.md), and the R&D gates are in [`research/novel-rd/`](../research/novel-rd/). Issue IDs (KI-xx) refer to [`05-quality/KNOWN_ISSUES.md`](05-quality/KNOWN_ISSUES.md).

## Phase 0: Handover hygiene (week 1)

- Create the private repo, CI, branch protection and CODEOWNERS ([REPO_MIGRATION](00-handover/REPO_MIGRATION.md)).
- Issue fresh credentials and decide on hosting ([DEPLOYMENT](04-operations/DEPLOYMENT.md)).
- Add ESLint and make lint part of CI (KI-30).

## Phase 1: Honest demo (weeks 1–4)

Goal: nothing on screen or in a PDF can be mistaken for something it is not.

- Relabel the dossier as an unsigned draft and remove "CONCEDIDO" (KI-01).
- Make production mode strict, with no fixture fallback or demo cookie (KI-04, KI-05).
- Remove fabricated fields from enrich (KI-03). Fix the copy and locale leftovers (KI-45).
- Fix the cheap correctness bugs: KI-11, KI-16, KI-17, KI-19, KI-21, KI-22.
- Fix the UX defects: 3D fly-in (KI-43), onboarding contrast (KI-44), Sidebar external link (KI-41). Pick a MapBiomas endpoint (KI-28) and set the ion token (KI-33).
- Add a Playwright smoke test for the demo script (KI-31).

## Phase 2: First real data path (months 2–3)

Goal: one real farm, end to end, with live sources and persistence.

- Registro Rural with a real key and contract tests (KI-36). Geometries from SICAR.
- Persistence: fix RLS (KI-26) and save (KI-06). Read the dashboard from Supabase (KI-07). Add an audit log.
- RBAC and tenant isolation in the API (KI-05).
- Persist commercial tasking orders (KI-08).

## Phase 3: Real radar (months 3–5)

Goal: M2 fires on real Sentinel-1 data, and its accuracy is measured.

- SAR processing worker: COG zonal statistics in the linear domain, orbit-consistent series, a `sar_observations` table (KI-02, KI-12).
- A precipitation source for S_clima (KI-09).
- Multi-temporal detection, plus tillage- and crop-aware floors (KI-13, KI-14, KI-15).
- A back-test report on fields with known harvest dates, before any client claim.

## Phase 4: Evidence-grade outputs (months 4–6)

- Real ICP-Brasil PAdES-LTV signature and RFC 3161 timestamp, plus a stored, immutable dossier archive (KI-01).
- Legal review of the regulatory claims and the petition template (KI-37, KI-38).
- An LGPD programme for the Shield-RJ data sources ([SECURITY_MODEL](06-security/SECURITY_MODEL.md)).

## Phase 5: The real 3D twin and Shield-RJ (months 6+)

- Photogrammetry → terrain, 3D Tiles and ortho pipeline. Add a `twin_assets` table, a slope-class overlay and a CHM-based carbon estimate ([DIGITAL_TWIN_3D](02-architecture/DIGITAL_TWIN_3D.md)).
- Shield-RJ vectors 1–2, which need only M1 and M2. Then vectors 3–4 once data access and LGPD bases are settled ([SHIELD_RJ](03-domain-models/SHIELD_RJ.md)).
- R&D candidates from [`research/novel-rd`](../research/novel-rd/), behind stage gates: Área Contínua detection, VoI-based drone dispatch, probabilistic runoff and erosion.
