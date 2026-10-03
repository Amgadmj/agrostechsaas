## 2026-09-26T14:53:26Z
You are Worker M1 for the Agrostech SaaS MVP platform project.
Your Working Directory: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\worker_m1_1
Project Directory: c:\Users\Razer\Desktop\Agrostech\saas
Authoritative User Request: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md
Authoritative Project Specification: c:\Users\Razer\Desktop\Agrostech\saas\PROJECT.md
Spec Miner Report: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1\spec_report.md

You MUST read the authoritative request at c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md and the specification report at c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1\spec_report.md before writing code.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Write Ownership (Files you exclusively own):
- src/lib/registrorural/**
- src/lib/m1/**
- src/app/api/land/enrich/route.ts

Your Mission — Milestone M1 Implementation:
1. Implement the Registro Rural API Client in src/lib/registrorural/:
   - Enforce strict process.env.REGISTRO_RURAL_API_KEY verification. If missing or invalid, throw/return explicit diagnostic errors (CONFIG_MISSING_API_KEY, AUTH_UNAUTHORIZED).
   - Query official SICAR demonstrativos (GET /v2/car/demonstrativo/{car} proxying upstream https://api-gateway-v2.registrorural.com.br/car/consulta/{numero_car}/demonstrativo with X-API-Key).
   - Asynchronous polling engine: handle HTTP 200/202 PENDING -> COMPLETE/COMPLETED with exponential backoff (2s initial, 3s interval, max 20 attempts, 60s timeout ceiling).
   - Implement compliance check methods: /v2/r2c/situacao (upstream /r2c/car/{numero_car}/situacao_car) and /v2/r2c/restricoes (upstream /r2c/car/{numero_car}/restricoes_sicar).
   - Support offline/demo fallback mode when no live API key is present OR key is invalid, returning real Fazenda Buritis/MG demonstrativo fixtures so the platform functions deterministically while logging explicit diagnostics.
2. Implement Model M1 Net Plantable Area (Área Útil Líquida) in src/lib/m1/:
   - Exact mathematical formula and deduplication:
     A_net = max(0, A_gross - (A_APP + A_RL - A_RLEmAPP + A_servidao + A_restrito + A_disputa + A_conflito + A_embargo))
   - Support geometry difference / hole-punching for GeoJSON polygons if geometries are present.
   - Calculate preservationRatio, netArableRatio, and credit eligibility under Law 12.651/2012 and BCB Resolução CMN 5.267/2025.
3. Integrate with src/app/api/land/enrich/route.ts:
   - Replace simulated setTimeout mock with real call through RegistroRuralClient and Model M1.
   - Return clean EnrichedLandData matching application frontend interfaces.
4. Verify your implementation:
   - Run type checks / tests.
   - Document commands run and verified results in your handoff.
5. Author a detailed handoff report in c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\worker_m1_1\handoff.md and send a completion message to your parent.
