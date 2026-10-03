# AgrosTech Beta SaaS

**Rural-credit risk intelligence: net plantable area, MCR 2-9 compliance, SAR crop monitoring and a 3D digital twin of the land.**

AgrosTech gives banks, barter desks, FIAGRO funds and producers one view of the farm behind a loan:

- **Credit and finance.** A CAR code goes in. Out come Model M1 net plantable area, a regulatory ScoreCard, the *Passaporte de Crédito Rural* and an MCR 2-9 dossier.
- **Collateral monitoring.** Sentinel-1 radar detects harvest through cloud (Model M2). Commercial SAR is tasked on demand, and the Shield-RJ fraud war room tracks pre-planned judicial-recovery schemes.
- **3D digital twin.** A CesiumJS terrain globe with the extruded cadastral boundary and drone models, alongside 2D MapLibre/Deck.gl maps with MapBiomas layers.

> **Status (2026-10-03): beta / demo-grade.** The domain logic is implemented and tested. Much of the data is still fixtures, and the dossier's digital signature is a placeholder. Read [`docs/00-handover/CTO_HANDOVER.md`](docs/00-handover/CTO_HANDOVER.md) before showing this to a client.

---

## Quick start

Requires Node.js ≥ 20.11 (see `.nvmrc`).

```bash
npm ci
```

```bash
cp .env.example .env.local
```

```bash
npm run dev
```

Open http://localhost:3000 and choose the **B2B** or **B2C** portal. The defaults run fully offline in demo mode. For the 3D globe imagery, add `NEXT_PUBLIC_CESIUM_ION_TOKEN` to `.env.local`.

| Command | Purpose |
|---|---|
| `npm run dev` | Development server |
| `npm run typecheck` | TypeScript (`strict`) |
| `npm test` | 176-case tiered suite (`tests/e2e`) |
| `npm run test:adversarial` | Stress harnesses (currently report known defects) |
| `npm run build` / `npm start` | Production build / serve |

## Tech stack

Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS · MapLibre GL + Deck.gl · CesiumJS · Supabase (Postgres + PostGIS + Auth) · Zod

External data: Registro Rural (SICAR / R2C), INPE Brazil Data Cube STAC (Sentinel-1 RTC), MapBiomas, Cesium ion. Commercial SAR (Umbra, Airbus TerraSAR-X) is specified but not yet connected.

## Repository layout

```
├── src/
│   ├── app/              Pages (login, dashboard, onboard, shield-rj, land/[id]/3d) and /api route handlers
│   ├── components/       UI: layout, map (2D + Cesium 3D), wizard, shield-rj, theme, ui
│   ├── lib/              Framework-free domain logic: m1, sar, registrorural, dossier, supabase, format
│   ├── types/            Shared TypeScript types
│   └── middleware.ts     Auth gate for /dashboard and /api
├── supabase/             schema.sql (PostGIS + RLS), seed.sql
├── tests/
│   ├── e2e/              Tiered requirement suite (tiers 1–4) + fixtures
│   └── adversarial/      White-box stress harnesses
├── scripts/              copy-cesium-assets.mjs (postinstall)
├── research/             R&D whitepapers and Python benchmarks
├── docs/                 Handover, product, architecture, models, ops, quality, security, ADRs
├── AGENTS.md             Operating manual for AI coding agents (CLAUDE.md imports it)
└── .github/              CI, PR/issue templates, CODEOWNERS, Dependabot
```

## Documentation

| Start here | |
|---|---|
| [CTO handover](docs/00-handover/CTO_HANDOVER.md) | What is real vs demo, top risks, and a 30/60/90-day plan |
| [Known issues](docs/05-quality/KNOWN_ISSUES.md) | Every known defect with an ID, a file and a fix |
| [Architecture](docs/02-architecture/ARCHITECTURE.md) | System map and flows |
| [API reference](docs/02-architecture/API_REFERENCE.md) | All `/api/*` routes |
| [Domain models](docs/03-domain-models/) | M1, M2, Shield-RJ, MCR 2-9 dossier |
| [3D digital twin](docs/02-architecture/DIGITAL_TWIN_3D.md) | What exists and the target pipeline |
| [Full index](docs/README.md) | Everything else |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). AI agents: read [`AGENTS.md`](AGENTS.md) first.

## Security

See [`SECURITY.md`](SECURITY.md). **This repository must stay private.**

## License

Proprietary and confidential. © 2026 Agrostech Soluções em Aerolevantamento Ltda. All rights reserved. See [`LICENSE`](LICENSE).
