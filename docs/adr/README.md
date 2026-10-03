# Architecture Decision Records

We record significant technical decisions as short ADRs, in [Michael Nygard's format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions). ADRs 0001–0008 were written **retroactively** at handover (2026-10-03). They capture decisions already built into the code, so the new team can see what was decided and why, and reverse it deliberately.

| # | Title | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-nextjs-app-router-monolith.md) | Next.js App Router monolith for UI and API | Accepted (retroactive) |
| [0003](0003-supabase-postgis-system-of-record.md) | Supabase (Postgres + PostGIS + Auth + RLS) as system of record | Accepted (retroactive) |
| [0004](0004-cesium-assets-copied-at-install.md) | Copy Cesium static assets at install time instead of committing them | Accepted |
| [0005](0005-dual-track-sar.md) | Dual-track SAR: free Sentinel-1 baseline, commercial tasking on anomaly | Accepted (retroactive) |
| [0006](0006-demo-and-integrity-modes.md) | Explicit demo and integrity modes; fixture data is always labelled | Accepted (retroactive) |
| [0007](0007-cesiumjs-for-3d-twin.md) | CesiumJS for the 3D digital twin, MapLibre + Deck.gl for 2D | Accepted (retroactive) |
| [0008](0008-separate-saas-repository.md) | Separate the SaaS into its own repository | Accepted |

## Writing a new ADR

1. Copy [`template.md`](template.md) to `NNNN-short-title.md`, using the next number.
2. Fill it in and open it in the same PR as the change it describes.
3. Never edit the decision in an accepted ADR. To change it, write a new ADR that supersedes it.
