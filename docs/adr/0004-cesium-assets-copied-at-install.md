# 0004. Copy Cesium static assets at install time instead of committing them

- **Status:** Accepted
- **Date:** 2026-10-03

## Context

CesiumJS has to serve its static runtime (Workers, Assets, Widgets, ThirdParty) from the app's own origin. `CesiumViewer` sets `CESIUM_BASE_URL = "/cesium/"` for this.

The source branch committed 272 files from `public/cesium/Assets` and `Widgets`, but **left out `Workers/`**. The 3D twin therefore only worked on the one machine where `Workers/` existed as untracked files. The committed copies also drift from whichever `cesium` version is installed.

## Decision

`scripts/copy-cesium-assets.mjs` generates `public/cesium/` from `node_modules/cesium/Build/Cesium`. It runs on `postinstall`, `predev` and `prebuild`. The folder is gitignored.

## Consequences

- A fresh clone works after `npm ci`, and the assets always match the installed Cesium version.
- Builds need `node_modules/cesium`, which every install provides.
- Verified on 2026-10-03: in the browser, the Workers load from `/cesium/Workers/*` with HTTP 200.
