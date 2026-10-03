# 0002. Next.js App Router monolith for UI and API

- **Status:** Accepted (retroactive)
- **Date:** 2026-10-03 (decision taken during the 2026-09-26 build)

## Context

A small team needs to ship a demo-grade but credible product fast. It has a map-heavy UI, a few JSON APIs and auth. Separate frontend and backend services would double the deployment and auth surface.

## Decision

Build one Next.js 15 application (App Router, React 19, TypeScript strict) with three parts:

- pages in `src/app/**`
- route handlers in `src/app/api/**`
- framework-free domain logic in `src/lib/**`

## Consequences

- There is one deployable on Vercel, and the UI and API share types.
- **Long-running or CPU-heavy work does not fit in route handlers.** This covers SAR raster processing, Registro Rural polling and PDF signing. That work must move to workers or services as it becomes real (see [0005](0005-dual-track-sar.md)). Keeping `src/lib` free of Next and React imports keeps that extraction cheap.
- There is no versioned public API yet. Add `/api/v1` before any external integration.
