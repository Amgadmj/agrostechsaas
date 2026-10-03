import { NextResponse } from "next/server";
import { harvestDetectionEngine } from "@/lib/sar/harvestEngine";
import { bdcStacClient } from "@/lib/sar/bdcStacClient";
import { sarTemporalEngine } from "@/lib/sar/temporalEngine";
import { REAL_BURITIS_PARCELS, EXACT_BURITIS_COORDINATES } from "@/lib/mockData";
import { TemporalBackscatterPoint } from "@/types/sar";
import { checkApiAuth, unauthorizedResponse } from "@/lib/supabase/auth-guard";

export async function POST(request: Request) {
  const auth = await checkApiAuth(request);
  if (!auth.authenticated) {
    return unauthorizedResponse();
  }
  try {
    const body = await request.json();
    const {
      temporalPoints,
      car_code,
      geojson,
      thresholdDb,
      bareSoilFloorDb,
      precipitationMm48h,
      unregisteredDiversionSuspected,
    } = body;

    let points: TemporalBackscatterPoint[] = temporalPoints;

    // If temporalPoints were not directly passed, derive them from parcel or CAR code
    if (!points || !Array.isArray(points) || points.length === 0) {
      if (!car_code && !geojson) {
        return NextResponse.json(
          {
            success: false,
            error:
              "Must provide either 'temporalPoints' array or 'car_code' / 'geojson' to evaluate harvest events.",
          },
          { status: 400 }
        );
      }

      // Resolve geometry
      let targetPolygon: any;
      let bbox: [number, number, number, number] = [
        -46.615, -15.452, -46.591, -15.418,
      ];

      if (geojson) {
        targetPolygon = geojson.type === "Feature" ? geojson.geometry : geojson;
      } else if (car_code) {
        const found = REAL_BURITIS_PARCELS.find(
          (p) => p.car_code.toLowerCase() === car_code.toLowerCase()
        );
        targetPolygon = found
          ? found.geojson_boundary.geometry
          : { type: "Polygon", coordinates: [EXACT_BURITIS_COORDINATES] };
      }

      // Query STAC & generate curve
      const stacItems = await bdcStacClient.searchSentinel1Rtc(bbox, {
        start: "2025-11-01T00:00:00Z",
        end: "2026-04-15T23:59:59Z",
      });

      points = await sarTemporalEngine.generateBackscatterCurve(
        targetPolygon,
        stacItems
      );
    }

    // Run M2 Anti-Fuga Harvest Engine
    const result = harvestDetectionEngine.detectHarvestEvents(
      points,
      thresholdDb,
      {
        bareSoilFloorDb,
        precipitationMm48h,
        unregisteredDiversionSuspected,
      }
    );

    return NextResponse.json({
      success: true,
      data: {
        ...result,
        evaluatedPointsCount: points.length,
        evaluatedPeriod: {
          start: points[0]?.date || null,
          end: points[points.length - 1]?.date || null,
        },
      },
    });
  } catch (error: any) {
    console.error("SAR Harvest Check API Error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || "Failed to execute M2 harvest detection engine.",
      },
      { status: 500 }
    );
  }
}
