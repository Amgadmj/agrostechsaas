# 0003. Supabase (Postgres + PostGIS + Auth + RLS) as system of record

- **Status:** Accepted (retroactive)
- **Date:** 2026-10-03

## Context

The product's data is spatial: parcels, embargoes and SAR footprints. It is multi-tenant, serving banks with their analysts as well as producers. It is also regulated, under LGPD and banking secrecy.

## Decision

Use Supabase for persistence and identity:

- **Postgres with PostGIS** stores the spatial data.
- **Supabase Auth** handles identity.
- **Row-Level Security** isolates tenants (`supabase/schema.sql`).
- Production runs in the São Paulo region.

## Consequences

- Spatial predicates (`ST_Intersects`, `ST_Difference`) can move from hand-written JS into SQL.
- RLS adds defence in depth, but the current policies need rework because they recurse (KI-26), and the app does not read from the database yet (KI-07).
- Vendor coupling is moderate. This is standard Postgres, so moving to RDS or Cloud SQL stays feasible.
