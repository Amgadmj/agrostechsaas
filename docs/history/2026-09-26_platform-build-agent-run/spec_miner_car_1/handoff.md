# Handoff Report: CAR & SICAR Regulatory Specification Mining (Requirement R1)

**Agent ID:** `teamwork_preview_spec_miner` (spec_miner_car_1)  
**Parent Agent:** `orchestrator_1` (`25db47f9-1b22-4c1b-a2ff-46c16559e080`)  
**Workspace:** `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1`  
**Date:** 2026-09-26  
**Type:** Hard Handoff (Task Complete)  

---

## 1. Observation

1. **User Request & Requirement R1:**
   In `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md` (lines 13–15):
   > "R1. Live Registro Rural CAR API Integration (Strict Production Mode)
   > Integrate the land onboarding pipeline with the live Registro Rural API (`https://docs.registrorural.com.br/reference/consultademonstrativodocar`). The client must require `REGISTRO_RURAL_API_KEY` in environment configuration, query official SICAR demonstrativos (`GET /v2/car/demonstrativo/{car}`), handle asynchronous `PENDING` to `COMPLETE` states, parse property and conservation boundaries (APP, Reserva Legal), execute compliance checks (`/v2/r2c/situacao` and `/v2/r2c/restricoes`), and compute the Net Plantable Area (*Área Útil Líquida* — Model M1). If credentials are missing or invalid, halt with explicit diagnostic errors."

2. **Authoritative Documentation Probed:**
   - Evaluated `https://docs.registrorural.com.br/llms.txt`, discovering the complete OpenAPI specifications for all endpoints.
   - Probed `https://docs.registrorural.com.br/reference/consultademonstrativodocar.md`:
     - Server base URL: `https://api-gateway-v2.registrorural.com.br`
     - Upstream OpenAPI path: `/car/consulta/{numero_car}/demonstrativo`
     - Authentication: `components.securitySchemes.apiKey` defined as header `X-API-Key`.
     - Polling States: HTTP 200 with `status: "PENDING", data: null` transitioning to `status: "COMPLETE", data: { car_id, dados: { cabecalho, areas, restricoes } }`.
     - Query parameter: `max_age` (in days, e.g. `0` for live same-day sync).
   - Probed `https://docs.registrorural.com.br/reference/situaocar.md`:
     - Upstream path: `/r2c/car/{numero_car}/situacao_car`
     - States: HTTP 202 `status: "PENDING"`, HTTP 200 `status: "COMPLETED", result: "PASSED" | "FAILED"`.
     - Evaluates whether CAR status is in `approved_statuses` (default `["Ativo", "Pendente"]`).
   - Probed `https://docs.registrorural.com.br/reference/restriessicar.md`:
     - Upstream path: `/r2c/car/{numero_car}/restricoes_sicar`
     - States: HTTP 202 `status: "PENDING"`, HTTP 200 `status: "COMPLETED", result: "PASSED" | "FAILED"`.
     - Infractions list: `data.restricoes` containing `area_conflito`, `descricao`, `origem`, `data_registro`.
   - Probed complementary endpoints: `consultadadosdocar.md` (`/car/consulta/{numero_car}/dados`) and `buscaporcoordenada.md` (`/car/busca/coordenada`).

3. **Current Codebase State:**
   - In `c:\Users\Razer\Desktop\Agrostech\saas\.env.example`: `REGISTRO_RURAL_API_KEY` is not yet registered (only Supabase and Cesium tokens exist).
   - In `src/app/api/land/enrich/route.ts`: Currently relies on simulated `setTimeout` delays and hardcoded Buritis/MG coordinates.
   - In `src/lib/mockData.ts`: Real polygon coordinates for Fazenda Buritis (`MG-3109300-4829A0D7314B4A45A7C49102B94C7192`), APP Hídrica Rio Urucuia, and Reserva Legal Cerrado already exist and provide perfect fixtures for testing.

---

## 2. Logic Chain

1. **Mapping Upstream Gateway to Application Routes:**
   - The user request specifies SaaS routes:
     - `GET /v2/car/demonstrativo/{car}`
     - `GET /v2/r2c/situacao`
     - `GET /v2/r2c/restricoes`
   - From upstream OpenAPI definitions, the real backend paths are:
     - `/car/consulta/{numero_car}/demonstrativo`
     - `/r2c/car/{numero_car}/situacao_car`
     - `/r2c/car/{numero_car}/restricoes_sicar`
   - Therefore, the Next.js SaaS backend must implement route handlers or an SDK client (`src/lib/registroRuralClient.ts`) that proxies requests to `https://api-gateway-v2.registrorural.com.br` injecting the `X-API-Key: process.env.REGISTRO_RURAL_API_KEY` header.

2. **Strict Production Mode Enforcement:**
   - The specification requires halting with explicit diagnostics if credentials are missing or invalid.
   - If `process.env.REGISTRO_RURAL_API_KEY` is missing, the client must throw `ConfigError: Missing REGISTRO_RURAL_API_KEY in environment configuration`.
   - If HTTP 401/403 is received, it must immediately return an unauthorized failure without retrying or silently returning fake data.

3. **Asynchronous Polling Engine Design:**
   - Because upstream SICAR queries can take 2 to 30 seconds, the client cannot assume immediate data.
   - Demonstrativo queries return HTTP 200 with `status: "PENDING"`, while R2C queries return HTTP 202 with `status: "PENDING"`.
   - The client polling engine must handle both HTTP 200 and 202, polling every 3,000 ms with an exponential backoff factor (1.2x) up to a 60,000 ms safety timeout (max 20 attempts).

4. **Model M1 Net Plantable Area (*Área Útil Líquida*) Formulation:**
   - Rural credit under BCB Resolução CMN 5.267/2025 (MCR 2-9) prohibits financing non-arable or preserved lands.
   - In SICAR, `areaRLEmAPP` represents Legal Reserve overlapping APP. Simply subtracting `areaAPP + areaRLP` would double-deduct the overlapping area.
   - Deduplication formula: $A_{\text{conservacao}} = A_{\text{APP}} + A_{\text{RL}} - A_{\text{RLEmAPP}}$.
   - Mandatory exclusions: Administrative easements ($A_{\text{servidaoAdministrativa}}$), restricted use ($A_{\text{usoRestrito}}$), title overlaps ($A_{\text{sobreposicaoOutrosImoveis}}$), public overlaps (Indigenous lands, Conservation Units), and active IBAMA embargoes.
   - Cross-check against consolidated land ($A_{\text{usoConsolidado}} - A_{\text{APPRecompor}} - A_{\text{RLRecompor}}$) ensures credit is restricted to legally and agronomically active crop fields.

---

## 3. Caveats

1. **Network Connectivity & Mock Server:**
   The upstream API `https://api-gateway-v2.registrorural.com.br` requires live paid credits and a valid `REGISTRO_RURAL_API_KEY`. While offline or in test environments lacking a funded key, tests must utilize high-fidelity wiremock / MSW (Mock Service Worker) handlers replicating the exact OpenAPI schemas documented in `spec_report.md`.
2. **PostGIS vs. Client-side Turf.js:**
   While simple vector differences can be computed in Node.js/browser via `@turf/difference`, large multi-polygon CAR perimeters with hundreds of vertices require topological cleaning (`turf.cleanCoords` or PostGIS `ST_MakeValid`) to prevent geometric topology exceptions.

---

## 4. Conclusion

Requirement R1 is completely specified and documented in `spec_report.md`. The report contains:
- Complete authentication and header contracts.
- Exact request and response JSON schemas for all 3 primary endpoints and 2 complementary endpoints.
- Detailed asynchronous polling state machine and retry logic.
- 32-attribute SICAR demonstrativo data dictionary.
- Mathematical and vector GIS specifications for Model M1 Net Plantable Area (*Área Útil Líquida*).
- 10 discovered features and 12 edge cases with mitigation strategies.
- 3 end-to-end reference fixtures.

---

## 5. Verification Method

To independently verify the specification findings:
1. **Inspect Report:**
   Read `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1\spec_report.md`.
2. **Verify Remote OpenAPI Schemas:**
   Fetch `https://docs.registrorural.com.br/reference/consultademonstrativodocar.md` and verify that the OpenAPI 3.0.3 paths and schemas match those in Section 4.1.
3. **Verify Compliance Endpoint Schemas:**
   Fetch `https://docs.registrorural.com.br/reference/situaocar.md` and `https://docs.registrorural.com.br/reference/restriessicar.md` and verify the `202 PENDING` and `200 COMPLETED` schemas in Sections 4.2 and 4.3.
4. **Verify Model M1 Math:**
   Validate the deduction equation against Federal Law 12.651/2012 Art. 15 and BCB Resolução CMN 5.267/2025.
