# 0007. CesiumJS for the 3D digital twin; MapLibre + Deck.gl for 2D

- **Status:** Accepted (retroactive)
- **Date:** 2026-10-03

## Context

The 3D twin needs a geodetically correct globe with real terrain, 3D Tiles streaming for drone photogrammetry, and extrusions. The 2D analysis needs fast vector and raster layers: MapBiomas WMS, APP/RL polygons and heatmaps.

## Decision

- **3D:** CesiumJS (WGS84 ellipsoid, quantized-mesh terrain, 3D Tiles, glTF), loaded client-side only.
- **2D:** MapLibre GL for the basemap and Deck.gl for the analytical layers.

## Consequences

- We maintain two map stacks, each chosen as the best fit for its job.
- Cesium is heavy, both in bundle size and in static assets (see [0004](0004-cesium-assets-copied-at-install.md)). Full terrain and imagery need a Cesium ion token or self-hosted tiles.
- Drone survey products come in SIRGAS 2000 / UTM 23S. A processing pipeline must reproject them to ECEF/WGS84 before streaming (see `docs/02-architecture/DIGITAL_TWIN_3D.md`).
