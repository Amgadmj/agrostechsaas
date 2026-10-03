import { NextResponse } from "next/server";
import { EnrichedLandData } from "@/types/geospatial";
import { createClient } from "@/lib/supabase/server";
import { checkApiAuth, unauthorizedResponse } from "@/lib/supabase/auth-guard";

export async function POST(request: Request) {
  // Auth guard
  const auth = await checkApiAuth(request);
  if (!auth.authenticated) {
    return unauthorizedResponse();
  }

  try {
    const body: { enriched: EnrichedLandData; owner_id?: string; org_id?: string } =
      await request.json();
    const { enriched, owner_id, org_id } = body;

    if (!enriched) {
      return NextResponse.json(
        { success: false, error: "Dados do imóvel ausentes na requisição." },
        { status: 400 }
      );
    }

    const parcelRecord = {
      id: `parcel-${Date.now()}`,
      name: enriched.name,
      owner_id: owner_id || "33333333-3333-3333-3333-333333333333",
      org_id: org_id || null,
      car_code: enriched.car_code,
      matricula_code: enriched.matricula_code,
      municipality: enriched.municipality,
      state_uf: enriched.state_uf,
      geojson_boundary: enriched.geojson_boundary,
      metrics_json: enriched.metrics,
      compliance_sicar: enriched.compliance_sicar,
      compliance_sigef: enriched.compliance_sigef,
      compliance_ibama: enriched.compliance_ibama,
      environmental_context: enriched.environmental_context,
      model_3d_url: enriched.model_3d_url,
      model_type: enriched.model_type,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
    const isMock = supabaseUrl.includes("mock") || !supabaseUrl;

    try {
      const supabase = await createClient();
      const { error } = await supabase.from("land_parcels").insert(parcelRecord as any);

      if (error) {
        console.error("Supabase insert error:", error);
        if (!isMock) {
          return NextResponse.json(
            {
              success: false,
              error: `Erro de persistência no Supabase: ${error.message}`,
            },
            { status: 500 }
          );
        }
      }
    } catch (e: any) {
      if (!isMock) {
        return NextResponse.json(
          {
            success: false,
            error: `Erro ao conectar com banco de dados: ${e.message}`,
          },
          { status: 500 }
        );
      }
    }

    return NextResponse.json({
      success: true,
      parcel: parcelRecord,
      message: "Passaporte de Crédito emitido e imóvel cadastrado com sucesso!",
    });
  } catch (err: any) {
    console.error("Save land error:", err);
    return NextResponse.json(
      { success: false, error: err.message || "Failed to save land parcel" },
      { status: 500 }
    );
  }
}
