# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/) (pre-1.0 while in beta).

## [Unreleased]

## [0.1.0] - 2026-10-03

Initial import into a standalone repository from `Amgadmj/agrostech` (`saas/`, branch `fix/ux-audit-2026-10`, commit `c5feb92`).

### Included from the source

- Next.js 15 app with portfolio dashboard, onboarding wizard, Shield-RJ war room and Cesium 3D twin.
- Domain libraries: Model M1, the Registro Rural client with fixtures, the BDC STAC client, the SAR temporal and harvest engines (M2), commercial SAR tasking (Umbra, TerraSAR-X), and the MCR 2-9 dossier with a PDF writer.
- Supabase schema with PostGIS and RLS, plus seed data.
- 176-case tiered test suite.
- UX-audit remediation sprint (WS-A…WS-D): demo labelling, consistent Buritis figures, a single app shell, API auth guards, local Cesium assets and an accessibility pass.

### Added during handover

- `docs/`: CTO handover, product, architecture, API, data model, 3D twin, domain models, operations, testing, a known-issues register (KI-01…KI-45), a security model, ADRs 0001–0008, a roadmap and a glossary.
- `AGENTS.md` and `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md` and `LICENSE`.
- `.github/`: CI workflow, PR and issue templates, CODEOWNERS and Dependabot.
- `tests/adversarial/`: the challenger agents' stress harnesses, promoted from the build archive, with a runner (`npm run test:adversarial`).
- `research/`: novel R&D whitepapers and benchmarks, with `requirements.txt`. `docs/strategy/`: the IP / 3D-twin thesis (`.docx` + Markdown) and the data-room product docs.
- `scripts/copy-cesium-assets.mjs`, which generates `public/cesium/` on install, dev and build.

### Fixed

- A fresh clone missed `public/cesium/Workers/`, which broke the 3D twin. Assets are now generated from `node_modules` and gitignored.
- `zod` and `tsx` were used but not declared in `package.json`.
- `npm run test:e2e` was documented but did not exist. Added `test`, `test:e2e`, `test:adversarial` and `typecheck`.
- `.env.example` documented `REGISTRO_RURAL_API_URL`, but the code reads `REGISTRO_RURAL_BASE_URL`. Every variable is now marked READ or RESERVED.
- Tailwind and PostCSS now resolve their config relative to the project, not the process working directory.

### Moved

- `PROJECT.md`, `TEST_INFRA.md`, `TEST_READY.md` and the old `README.md` → `docs/history/2026-09-26_platform-build-agent-run/`.
- `audits/` → `docs/history/2026-10-03_ux-audit/`.
- `buritis_real_polygon.json` → `tests/e2e/fixtures/`.
