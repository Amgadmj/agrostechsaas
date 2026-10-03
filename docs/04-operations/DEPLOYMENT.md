# Deployment

**Status: not deployed from this repository.** No deployment config (Vercel project, Dockerfile, IaC) was found in the source monorepo for `saas/`. The external app `dashboard-ui-liart-ten.vercel.app` is a separate project (KI-41). This document is the recommended path; record the final choice as an ADR.

## Recommended baseline: Vercel + Supabase

Why: Next.js App Router, route handlers and middleware run natively on Vercel with zero config. Supabase gives Postgres + PostGIS + Auth + storage in the São Paulo region.

1. **Supabase.** Create one project per environment (staging, production) in `sa-east-1`.
   - Apply the schema as the first migration (see [`DATA_MODEL.md`](../02-architecture/DATA_MODEL.md#migrations)) **after** fixing the RLS recursion (KI-26).
   - Enable point-in-time recovery on production.
2. **Vercel.** Import the GitHub repo. Framework preset: Next.js. The install command `npm ci` runs `postinstall`, which copies the Cesium assets. The build command is `npm run build`.
3. **Environment variables.** Set them per environment ([`ENVIRONMENT.md`](./ENVIRONMENT.md)). Production **must** have `NEXT_PUBLIC_DEMO_MODE=false` and `INTEGRITY_MODE=production`.
4. **Domains.** For example, `app.agrostech.xyz` (prod) and `staging.agrostech.xyz`. Note that `agrostech.xyz` (the marketing site) is hosted on Lovable behind Cloudflare. Add the app sub-domain as a CNAME to Vercel in Cloudflare DNS (proxy off, or "Full (strict)" TLS).
5. **Cesium ion.** Use a production token restricted to the production domain.
6. **Preview deployments.** Each PR gets a preview URL with demo mode on and a staging Supabase. Do not connect previews to production data.

## Runtime notes

- **Long work does not belong in route handlers.** Registro Rural polling can take up to 60 s by default, and SAR raster processing will take much longer. Vercel functions have execution limits, so move heavy or slow jobs to a queue or worker (e.g. Supabase Edge Functions + pg_cron, a small container service, or a managed queue) and poll for results.
- **In-memory state is per instance.** The commercial tasking store (KI-08) loses orders across serverless invocations. Persist it before any real use.
- **The middleware runs on every request.** It calls `supabase.auth.getUser()`, which adds a network round-trip. Keep the matcher narrow.

## Alternative: container

If data-residency or cost requires it, the app runs as a standard Node server:

```bash
npm ci && npm run build && npm start
```

Use `output: "standalone"` in `next.config.mjs` for a slim image. Serve `public/` (including the generated `public/cesium/`) from the same container or a CDN.

## Release checklist

- [ ] CI green (typecheck, tests, build)
- [ ] `NEXT_PUBLIC_DEMO_MODE=false`, `INTEGRITY_MODE=production`, `ALLOW_MOCK_FALLBACK=false` in prod
- [ ] No placeholder signature presented as real (KI-01)
- [ ] DB migrations applied to staging, then prod
- [ ] Smoke test: the demo script in [`USER_JOURNEYS.md`](../01-product/USER_JOURNEYS.md) on staging
- [ ] `CHANGELOG.md` updated, tag `vX.Y.Z`
