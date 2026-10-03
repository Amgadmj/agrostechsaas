import { NextRequest, NextResponse } from "next/server";
import { createClient } from "./server";

export interface AuthResult {
  authenticated: boolean;
  user?: any;
  role?: string;
  error?: string;
}

/**
 * Validates authentication for API routes.
 * In production, requires a valid Supabase session.
 * In demo mode (NEXT_PUBLIC_DEMO_MODE === "true"), accepts valid agrostech_demo_role cookies.
 */
export async function checkApiAuth(request: Request | NextRequest): Promise<AuthResult> {
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

  // 1. Check demo cookie only when NEXT_PUBLIC_DEMO_MODE is true
  if (isDemoMode) {
    const cookieHeader = request.headers.get("cookie") || "";
    const match = cookieHeader.match(/agrostech_demo_role=([^;]+)/);
    if (match && (match[1] === "b2b_admin" || match[1] === "b2c" || match[1] === "b2b")) {
      return {
        authenticated: true,
        role: match[1],
        user: { id: "demo-user", role: match[1] },
      };
    }
  }

  // 2. Real Supabase auth check
  try {
    const supabase = await createClient();
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser();

    if (user && !error) {
      return {
        authenticated: true,
        user,
      };
    }
  } catch {
    // Auth validation failed
  }

  return {
    authenticated: false,
    error: "Acesso não autorizado. Autenticação obrigatória.",
  };
}

export function unauthorizedResponse(
  message: string = "Acesso não autorizado. Autenticação obrigatória."
) {
  return NextResponse.json(
    { success: false, error: message },
    { status: 401 }
  );
}
