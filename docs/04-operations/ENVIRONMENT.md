# Environment Variables

Template: [`.env.example`](../../.env.example). Copy it to `.env.local` for development, which is gitignored. In hosted environments, set the variables in the platform's secret store; never commit them.

`NEXT_PUBLIC_*` variables are **inlined into the browser bundle at build time**. Never put a secret in one, and rebuild after changing one.

| Variable | Read by code? | Scope | Required in prod | Purpose |
|---|---|---|---|---|
| `NEXT_PUBLIC_DEMO_MODE` | ✅ `middleware.ts`, `auth-guard.ts`, `login/page.tsx`, `DemoBadge.tsx` | client + server | **must be `false`** | `true` enables cookie login (no password) and the demo badge |
| `INTEGRITY_MODE` | ✅ `registrorural/client.ts` | server | `production` | `demo` allows offline SICAR fixtures |
| `ALLOW_MOCK_FALLBACK` | ✅ `registrorural/client.ts` | server | `false` | `true` also allows fixtures on upstream failure |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ `lib/supabase/*` | client + server | ✅ | Supabase project URL. If unset, the code uses a mock URL and save "succeeds" without persisting |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ `lib/supabase/*` | client + server | ✅ | Public anon key (safe for the browser; RLS protects the data) |
| `SUPABASE_SERVICE_ROLE_KEY` | ❌ reserved | **server only** | when needed | Admin key. Must never reach the client |
| `REGISTRO_RURAL_API_KEY` | ✅ | server | ✅ | Gateway key, sent as the `X-API-Key` header |
| `REGISTRO_RURAL_BASE_URL` | ✅ | server | optional | Defaults to `https://api-gateway-v2.registrorural.com.br` |
| `NEXT_PUBLIC_CESIUM_ION_TOKEN` | ✅ `CesiumViewer.tsx` | client | ✅ for 3D | World Terrain + imagery. Restrict it by URL in the ion dashboard |
| `NEXT_PUBLIC_MAP_STYLE` | ❌ reserved | client | n/a | Kept for the F15 test; basemaps are hardcoded |
| `BDC_STAC_URL`, `BDC_ACCESS_TOKEN` | ❌ reserved | server | n/a | The STAC URL is hardcoded in `bdcStacClient.ts` |
| `UMBRA_API_KEY`, `TERRASARX_API_KEY` | ❌ reserved | server | n/a | Provider clients are not implemented (KI-08) |

## Recommended environment matrix

| Env | DEMO_MODE | INTEGRITY_MODE | Supabase | Purpose |
|---|---|---|---|---|
| local | `true` | `demo` | none or a local Supabase (`supabase start`) | Development and demos |
| preview (per PR) | `true` | `demo` | shared staging project | Review apps |
| staging | `false` | `production` | staging project | Pilot rehearsal with test credentials |
| production | `false` | `production` | prod project (region: São Paulo, `sa-east-1`, for LGPD data locality) | Real clients |

## Adding a new variable

1. Read it in **one** module (a config helper) and validate it with Zod at startup.
2. Add it to `.env.example` with a `[READ]` comment.
3. Add a row to this table.
4. Add it to the hosting provider for every environment.
