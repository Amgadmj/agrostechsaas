# Local Development

## Prerequisites

- **Node.js ≥ 20.11**. `.nvmrc` pins 22 LTS. The handover was verified on Node 26.2 and npm 11.13.
- npm (lockfile v3 is committed; use `npm ci` for clean installs)
- Optional: the **Supabase CLI** and Docker, for a local Postgres + PostGIS
- Optional: Python ≥ 3.11, only for `research/`

## First run

```bash
npm ci
```

`postinstall` copies the Cesium runtime assets into `public/cesium/`. That folder is generated and gitignored.

```bash
cp .env.example .env.local
```

The defaults run the full demo with **no external keys**: fixtures for SICAR, a live STAC search with fixture fallback, and the demo-cookie login.

```bash
npm run dev
```

Open http://localhost:3000 and pick a portal. If port 3000 is busy, Next picks the next free port; check the terminal.

## Everyday commands

| Command | What it does |
|---|---|
| `npm run dev` | Dev server, with hot reload |
| `npm run typecheck` | `tsc --noEmit` over `src/` and `tests/` |
| `npm run test` / `npm run test:e2e` | 176-case tiered suite (`tests/e2e/runner.ts`), about 3 s |
| `npm run test:adversarial` | White-box stress harnesses. **Exits 1 today** because of known defects (KNOWN_ISSUES P1) |
| `npm run build` | Production build (also re-copies the Cesium assets) |
| `npm start` | Serve the production build |

## Running against a local Supabase (optional)

```bash
supabase init
```

```bash
supabase start
```

Then apply `supabase/schema.sql` and `supabase/seed.sql` via Studio (http://localhost:54323) or `psql`. Put the printed API URL and anon key into `.env.local`. Expect the RLS recursion issue described in [`DATA_MODEL.md`](../02-architecture/DATA_MODEL.md) (KI-26) and the save-route UUID bug (KI-06).

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| 3D page: black globe, `401 INVALID_TOKEN` in the console | No `NEXT_PUBLIC_CESIUM_ION_TOKEN`. Set it and restart (KI-33) |
| 3D page: errors loading `/cesium/Workers/*.js` | `public/cesium` is missing. Run `npm install` or `node scripts/copy-cesium-assets.mjs` |
| 2D map: "Camada indisponível" on MapBiomas layers | `geoserver.mapbiomas.org` no longer resolves (KI-28) |
| Unstyled pages when running Next from another directory | Fixed: `postcss.config.mjs` passes the absolute Tailwind config path |
| `npm run lint` asks interactive questions | No ESLint config yet (KI-30) |
| Next warns "inferred your workspace root" | A `package-lock.json` exists in a parent folder (e.g. your home directory). Harmless; remove the stray lockfile or set `outputFileTracingRoot` |
| Login loops back to `/login` | `NEXT_PUBLIC_DEMO_MODE` is not `true` and there is no Supabase session |

## Editor setup

TypeScript `strict` is on, and the path alias `@/*` maps to `src/*`. `.editorconfig` sets 2-space, LF and UTF-8.
