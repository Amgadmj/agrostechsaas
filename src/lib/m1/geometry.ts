/**
 * Model M1 Spatial Geometry & Hole-Punching Engine
 *
 * Implements GeoJSON boundary difference and hole-punching for Net Plantable Area.
 * In GeoJSON (RFC 7946), a Polygon is defined as [exteriorRing, innerRing1, innerRing2, ...],
 * where inner rings represent holes carved out of the exterior polygon (e.g. APP, RL, Embargoes).
 */

import { GeoJsonFeature } from "@/types/geospatial";

/**
 * Calculates spherical polygon ring area in hectares (ha)
 */
export function calculateRingAreaHa(ring: number[][]): number {
  if (!ring || ring.length < 3) return 0;

  const earthRadius = 6378137; // meters
  let area = 0;

  for (let i = 0; i < ring.length - 1; i++) {
    const p1 = ring[i];
    const p2 = ring[i + 1];

    const lat1 = (p1[1] * Math.PI) / 180;
    const lat2 = (p2[1] * Math.PI) / 180;
    const lonDiff = ((p2[0] - p1[0]) * Math.PI) / 180;

    area += lonDiff * (2 + Math.sin(lat1) + Math.sin(lat2));
  }

  area = (Math.abs(area) * earthRadius * earthRadius) / 4.0;
  return Number((area / 10000.0).toFixed(2));
}

/**
 * Ensures ring coordinates form a closed loop
 */
export function closeRing(ring: number[][]): number[][] {
  if (!ring || ring.length === 0) return [];
  const closed = [...ring];
  const first = closed[0];
  const last = closed[closed.length - 1];

  if (first[0] !== last[0] || first[1] !== last[1]) {
    closed.push([first[0], first[1]]);
  }
  return closed;
}

/**
 * Computes bounding box [minX, minY, maxX, maxY] for a ring
 */
export function getRingBbox(ring: number[][]): [number, number, number, number] {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const pt of ring) {
    if (pt[0] < minX) minX = pt[0];
    if (pt[1] < minY) minY = pt[1];
    if (pt[0] > maxX) maxX = pt[0];
    if (pt[1] > maxY) maxY = pt[1];
  }

  return [minX, minY, maxX, maxY];
}

/**
 * Ray-casting point-in-polygon test
 */
export function isPointInPolygon(
  point: [number, number],
  ring: number[][]
): boolean {
  const [x, y] = point;
  let inside = false;

  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0];
    const yi = ring[i][1];
    const xj = ring[j][0];
    const yj = ring[j][1];

    const intersect =
      yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }

  return inside;
}

/**
 * Determines whether a candidate hole ring intersects or is contained within the outer boundary
 */
function isRingInsideOrOverlapping(
  holeRing: number[][],
  outerRing: number[][],
  outerBbox: [number, number, number, number]
): boolean {
  const holeBbox = getRingBbox(holeRing);

  // Bbox disjoint check
  if (
    holeBbox[2] < outerBbox[0] ||
    holeBbox[0] > outerBbox[2] ||
    holeBbox[3] < outerBbox[1] ||
    holeBbox[1] > outerBbox[3]
  ) {
    return false;
  }

  // Check if at least one point of the hole is inside or near the outer ring
  for (const pt of holeRing) {
    if (isPointInPolygon(pt as [number, number], outerRing)) {
      return true;
    }
  }

  // Check centroid of the hole
  const centroidX = (holeBbox[0] + holeBbox[2]) / 2;
  const centroidY = (holeBbox[1] + holeBbox[3]) / 2;
  if (isPointInPolygon([centroidX, centroidY], outerRing)) {
    return true;
  }

  return true; // Overlapping bounding boxes
}

/**
 * Computes the Net Plantable Area GeoJSON Feature by punching exclusion holes
 * into the exterior gross boundary polygon.
 */
export function computeNetPlantablePolygon(
  grossBoundary: GeoJsonFeature,
  exclusionFeatures: GeoJsonFeature[]
): GeoJsonFeature {
  if (!grossBoundary || !grossBoundary.geometry) {
    throw new Error("Invalid grossBoundary: Feature geometry is required.");
  }

  // Extract exterior ring(s) from grossBoundary
  let exteriorRing: number[][] = [];
  const existingHoles: number[][][] = [];

  if (grossBoundary.geometry.type === "Polygon") {
    const coords = grossBoundary.geometry.coordinates as number[][][];
    if (coords && coords.length > 0) {
      exteriorRing = closeRing(coords[0]);
      for (let i = 1; i < coords.length; i++) {
        existingHoles.push(closeRing(coords[i]));
      }
    }
  } else if (grossBoundary.geometry.type === "MultiPolygon") {
    const coords = grossBoundary.geometry.coordinates as number[][][][];
    if (coords && coords.length > 0 && coords[0].length > 0) {
      exteriorRing = closeRing(coords[0][0]);
      for (let i = 1; i < coords[0].length; i++) {
        existingHoles.push(closeRing(coords[0][i]));
      }
    }
  }

  if (exteriorRing.length < 3) {
    return grossBoundary;
  }

  const outerBbox = getRingBbox(exteriorRing);
  const newHoles: number[][][] = [...existingHoles];

  // Process exclusion features (APP, Reserva Legal, Embargos)
  for (const feat of exclusionFeatures) {
    if (!feat || !feat.geometry) continue;

    if (feat.geometry.type === "Polygon") {
      const coords = feat.geometry.coordinates as number[][][];
      if (coords && coords.length > 0) {
        const ring = closeRing(coords[0]);
        if (ring.length >= 3 && isRingInsideOrOverlapping(ring, exteriorRing, outerBbox)) {
          newHoles.push(ring);
        }
      }
    } else if (feat.geometry.type === "MultiPolygon") {
      const coords = feat.geometry.coordinates as number[][][][];
      if (coords) {
        for (const poly of coords) {
          if (poly.length > 0) {
            const ring = closeRing(poly[0]);
            if (ring.length >= 3 && isRingInsideOrOverlapping(ring, exteriorRing, outerBbox)) {
              newHoles.push(ring);
            }
          }
        }
      }
    }
  }

  // Calculate gross area and deducted hole areas
  const grossAreaHa = calculateRingAreaHa(exteriorRing);
  let totalHoleAreaHa = 0;
  for (const hole of newHoles) {
    totalHoleAreaHa += calculateRingAreaHa(hole);
  }
  const calculatedNetHa = Math.max(0, Number((grossAreaHa - totalHoleAreaHa).toFixed(2)));

  const polygonCoordinates: number[][][] = [exteriorRing, ...newHoles];

  return {
    type: "Feature",
    properties: {
      ...grossBoundary.properties,
      name: "Área Útil Líquida (AUL - Modelo M1)",
      category: "parcel",
      nomenclature: "Área Útil Líquida (Gleba Descontada)",
      gross_area_ha: grossAreaHa,
      hole_count: newHoles.length,
      calculated_net_area_ha: calculatedNetHa,
    },
    geometry: {
      type: "Polygon",
      coordinates: polygonCoordinates,
    },
  };
}
