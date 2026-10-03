# Technical Specification Report: Requirement R1 — Live Registro Rural CAR API Integration (Strict Production Mode)

**Author:** CAR & SICAR Regulatory Spec Miner  
**Project:** Agrostech SaaS MVP Platform  
**Target Delivery Path:** `c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1\spec_report.md`  
**Date:** 2026-09-26  
**Status:** Authoritative Specification Complete  

---

## 1. Executive Summary & Regulatory Context

Under Central Bank of Brazil (BCB) regulations (**Resolução CMN nº 5.267/2025**, which updates **MCR 2-9 — Disposições Especiais Socioambientais do Crédito Rural**), financial institutions, agro-fintechs, and barter trading desks are strictly prohibited from granting rural credit, issuing Cedula de Produto Rural (CPR), or financing agricultural inputs on rural properties with:
1. Irregular or cancelled Cadastro Ambiental Rural (CAR/SICAR) registrations.
2. Spatial intersections with active environmental embargoes (IBAMA, ICMBio, or state agencies).
3. Overlaps with Indigenous Lands (Terras Indígenas), Integral Protection Conservation Units (Unidades de Conservação de Proteção Integral), or Agrarian Settlements.
4. Discrepancies between total declared area and actual **Net Plantable Area (*Área Útil Líquida* — Model M1)**, which represents the core fraud vector in agricultural debt restructurings and CPR over-pledging.

To power institutional-grade underwriting for an upcoming US$ 600K SAFE funding round and enterprise barter pilots, Requirement **R1** specifies the live production integration with the **Registro Rural API** (`https://api-gateway-v2.registrorural.com.br`). This service interfaces directly with the Brazilian Federal Forest Service (SFB - Serviço Florestal Brasileiro) SICAR repository.

This document establishes the definitive engineering specification for:
- Authentication & Strict Production Mode diagnostics.
- Upstream and SaaS route contracts for `/v2/car/demonstrativo/{car}`, `/v2/r2c/situacao`, and `/v2/r2c/restricoes`.
- Asynchronous polling lifecycle (`PENDING` $\to$ `COMPLETE`).
- Exhaustive SICAR Demonstrativo data dictionary (30+ spatial and cadastral metrics).
- Model M1 Net Plantable Area (*Área Útil Líquida*) mathematical formulation and vector boundary clipping logic.
- Reference fixtures and edge-case handling.

---

## 2. Authoritative Specification Sources

| Source Identifier | Type | Host / URL / Location | Description |
|---|---|---|---|
| **Registro Rural Docs** | Official API Portal | `https://docs.registrorural.com.br/reference/consultademonstrativodocar` | Primary documentation for Demonstrativo do CAR |
| **Registro Rural Index** | OpenAPI / Markdown Hub | `https://docs.registrorural.com.br/llms.txt` | Machine-readable index of all endpoints and OpenAPI specs |
| **API Gateway V2** | Production Endpoint | `https://api-gateway-v2.registrorural.com.br` | Upstream REST API Gateway for all live CAR/R2C queries |
| **SFB / SICAR** | Federal Government Standard | Federal Forest Service (Lei 12.651/2012) | National Rural Environmental Cadastre Data Standard |
| **BCB Res. CMN 5.267/2025** | Regulatory Compliance | Central Bank of Brazil / MCR 2-9 | Environmental and Territorial Credit Rules |
| **Existing Codebase** | Local Repository | `c:/Users/Razer/Desktop/Agrostech/saas` | Next.js 15 App Router, TypeScript types, Supabase models |

---

## 3. Authentication & Strict Production Mode

### 3.1 Credentials & Environment Variables
- **Environment Variable:** `REGISTRO_RURAL_API_KEY`
- **Configuration File:** `.env.local` (local development), runtime environment secret (production).
- **HTTP Header Name:** `X-API-Key`
- **Value:** 64-character alphanumeric string generated via the Registro Rural Dashboard Empresas (`https://dashboard.registrorural.com.br/`).

```http
GET /car/consulta/{numero_car}/demonstrativo HTTP/1.1
Host: api-gateway-v2.registrorural.com.br
X-API-Key: YOUR_REGISTRO_RURAL_API_KEY
Accept: application/json
```

### 3.2 Strict Production Mode vs. Demo Fallback Rules
Per Requirement R1, the application must run in **Strict Production Mode** by default.
- If `REGISTRO_RURAL_API_KEY` is not present, is empty, or fails authentication:
  - The client **MUST NOT** silently fall back to synthetic mock data.
  - The client **MUST halt immediately** with explicit diagnostic failure messages and standard error codes.
  - Demo fallback is ONLY permitted if an explicit environment flag `INTEGRITY_MODE=demo` or `ALLOW_MOCK_FALLBACK=true` is enabled in non-production environments.

### 3.3 Diagnostic Failure States & Error Catalogue

| Condition | HTTP Status | Internal Code | Diagnostic Message / System Behavior |
|---|---|---|---|
| Missing Key | 500 / 400 | `CONFIG_MISSING_API_KEY` | `HALT: Missing REGISTRO_RURAL_API_KEY in environment configuration. Required for Strict Production Mode.` |
| Invalid / Expired Key | 401 / 403 | `AUTH_UNAUTHORIZED` | `HALT: Unauthorized: Invalid, expired, or deactivated REGISTRO_RURAL_API_KEY.` |
| Insufficient Credits | 402 | `BILLING_INSUFFICIENT_CREDITS` | `HALT: Registro Rural account credit balance exhausted. Add credits via dashboard.registrorural.com.br.` |
| Invalid CAR Code Format | 400 | `INVALID_CAR_FORMAT` | `CAR code does not match federal format (e.g. UF-0000000-HEX32). Received: '{car}'` |
| CAR Not Found | 404 | `CAR_NOT_FOUND` | `CAR não encontrado: Imóvel inexistente na base do SICAR/Registro Rural.` |
| Upstream Rate Limit | 429 | `RATE_LIMITED` | `Registro Rural rate limit exceeded. Retry after backoff interval.` |
| SICAR Upstream Timeout | 504 | `SICAR_POLLING_TIMEOUT` | `SICAR upstream synchronization timed out after {timeout_seconds}s for CAR {car}.` |

---

## 4. Endpoints & Interface Contracts

The platform exposes standardized SaaS proxy routes that map onto the upstream Registro Rural REST API.

```
+------------------------------------+          +-------------------------------------------------+
|       AgrosTech SaaS Platform      |          |               Registro Rural Gateway            |
| (Client / Onboarding Wizard)       |          |      api-gateway-v2.registrorural.com.br        |
+------------------------------------+          +-------------------------------------------------+
                 |                                                       |
                 | --- GET /v2/car/demonstrativo/{car} ----------------> | GET /car/consulta/{car}/demonstrativo
                 | <--- 200 PENDING (wait 3s) -------------------------- |
                 | --- GET /v2/car/demonstrativo/{car} (Poll 2) -------> | GET /car/consulta/{car}/demonstrativo
                 | <--- 200 COMPLETE (full payload) -------------------- |
                 |                                                       |
                 | --- GET /v2/r2c/situacao ---------------------------> | GET /r2c/car/{car}/situacao_car
                 | <--- 200 COMPLETED (result: PASSED) ----------------- |
                 |                                                       |
                 | --- GET /v2/r2c/restricoes -------------------------> | GET /r2c/car/{car}/restricoes_sicar
                 | <--- 200 COMPLETED (result: PASSED, restricoes: [])-- |
```

---

### 4.1 Endpoint 1: Demonstrativo do CAR
- **SaaS Proxy Path:** `GET /v2/car/demonstrativo/{car}`
- **Upstream Path:** `GET https://api-gateway-v2.registrorural.com.br/car/consulta/{numero_car}/demonstrativo`
- **Method:** `GET`
- **Purpose:** Fetches the full official SICAR cadastral demonstrativo in JSON format.

#### Parameters:
- `numero_car` (path, string, required): Federal CAR identifier (pattern: `^[A-Z]{2}-\d{7}-[A-F0-9]{32}$`).
- `max_age` (query, string/integer, optional): Maximum age in days acceptable for cached demonstrativo. Default: `7`. If `0`, forces real-time query against the federal SICAR base.

#### Request Headers:
```http
X-API-Key: {REGISTRO_RURAL_API_KEY}
Accept: application/json
```

#### Response Schemas:

##### 1. HTTP 200 — In-Progress (State: `PENDING`)
When the demonstrativo is being pulled from SICAR, the API returns HTTP 200 with `status: "PENDING"` and a null/empty `data` payload:
```json
{
  "status": "PENDING",
  "data": null
}
```

##### 2. HTTP 200 — Completed (State: `COMPLETE`)
When processing finishes, the full structured payload is available in `data`:
```json
{
  "status": "COMPLETE",
  "data": {
    "car_id": "PA-1507300-FC136733C09E4DEE9BFDBE8C016B2FE7",
    "status": "s",
    "mensagem": "Operação realizada com sucesso.",
    "dados": {
      "cabecalho": {
        "codigo": "PA-1507300-FC136733C09E4DEE9BFDBE8C016B2FE7",
        "statusImovel": "Ativo",
        "condicaoAnalise": "Aguardando análise",
        "dataRegistro": "20/05/2016",
        "dataRetificacao": "13/03/2024",
        "dataDemonstrativo": "20/11/24 20:28",
        "houveRetificacao": true,
        "municipio": "São Félix do Xingu",
        "estado": "PA",
        "area": 19993.2104,
        "modulosFiscais": 266.5761,
        "centroideX": -52.8228110927235,
        "centroideY": -6.56798240702913,
        "latitude": "06°34'04,74\" S",
        "longitude": "52°49'22,12\" O",
        "aderiuPRA": null,
        "condicaoPRA": null,
        "dataAnalise": null,
        "sucessoConexaoReceptorPRA": false,
        "sobrepostoTiNaoHomologada": null,
        "malhaMunDestinoAntigoCAR": null,
        "malhaMunOrigemCondicaoAnterior": null,
        "malhaMunOrigemNovoCAR": null
      },
      "areas": {
        "areaLiquida": 19898.746,
        "areaAPP": 1544.9133277578092,
        "areaAPPEmAC": 671.4462,
        "areaAPPEmAA": 6.0449,
        "areaAPPRecompor": 516.6,
        "areaAPPSobrepostaRVN": 867.4189,
        "areaRLMinimaExigidaLei": 15918.9968,
        "areaRLDeclarada": 0,
        "areaRLP": 9070.7686,
        "areaRLA": 0,
        "areaRLANA": 0,
        "areaRLEmAPP": 895.5817,
        "areaRLRecompor": 284.4632077823479,
        "areaRLRecomporAA": 231.8408,
        "areaRLRecomporAC": 52.691,
        "areaRLVetorizadaSobrepostaRVN": 8786.2259,
        "areaRLExcedentePassivo": -6850.036,
        "situacaoRL": "Não Analisada",
        "areaRLCompensadaDoIREmTerceiros": 0,
        "areaRLCompensadaDeTerceirosNoIR": 0,
        "areaRVN": 8802.53594331401,
        "areaUsoConsolidado": 10657.209570486517,
        "areaAA": 238.16461777272252,
        "areaAP": 0,
        "areaUsoRestrito": 0,
        "areaUREmAC": 0,
        "areaUREmAA": 0,
        "areaUsoRestritoRecompor": 0,
        "areaUsoRestritoSobrepostaRVN": 0,
        "areaServidaoAdministrativa": 94.36431725051943,
        "areaSobreposicaoOutrosImoveis": 65.6519,
        "areaSobreposicaoUC": 19993.2104,
        "areaSobreposicaoTI": 0,
        "areaSobreposicaoAssentamento": 0
      },
      "restricoes": [
        {
          "id": 5,
          "descricao": "Área de Proteção Ambiental-ÁREA DE PROTEÇÃO AMBIENTAL TRIUNFO DO XINGU",
          "origem": "Unidade de Conservação",
          "dataRegistro": "13/03/2024",
          "areaConflito": 19993.2104,
          "percentualConflito": 100,
          "fase": null
        }
      ],
      "temTI": false
    }
  }
}
```

##### 3. HTTP 404 — Not Found
```json
{
  "error": "CAR não encontrado"
}
```

---

### 4.2 Endpoint 2: Situação CAR (R2C Due Diligence)
- **SaaS Proxy Path:** `GET /v2/r2c/situacao`
- **Upstream Path:** `GET https://api-gateway-v2.registrorural.com.br/r2c/car/{numero_car}/situacao_car`
- **Method:** `GET`
- **Purpose:** Validates the administrative and legal standing of the CAR. If status is `Ativo` or `Pendente`, result is `PASSED`. If `Suspenso` or `Cancelado`, result is `FAILED`.

#### Parameters:
- `numero_car` (path, string, required)
- `data_max_age` (query, string/integer, optional, default: `7`)
- `approved_statuses` (query, string, optional, default: `["Ativo", "Pendente"]`)

#### Response Schemas:

##### 1. HTTP 200 — Completed (`PASSED`)
```json
{
  "status": "COMPLETED",
  "result": "PASSED",
  "data": {
    "numero_car": "RS-4300406-AD3BD4B621624DE4B3073DE8675E08A1",
    "situacao_car": "Ativo",
    "data_demonstrativo": "2025-01-21"
  },
  "_metadata": {
    "numero_car": "RS-4300406-AD3BD4B621624DE4B3073DE8675E08A1",
    "data_max_age": 7,
    "approved_statuses": ["Ativo", "Pendente"]
  }
}
```

##### 2. HTTP 200 — Completed (`FAILED`)
```json
{
  "status": "COMPLETED",
  "result": "FAILED",
  "data": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "situacao_car": "Suspenso",
    "data_demonstrativo": "2025-02-12"
  },
  "_metadata": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "data_max_age": 7,
    "approved_statuses": ["Ativo", "Pendente"]
  }
}
```

##### 3. HTTP 202 — Pending
```json
{
  "status": "PENDING",
  "result": null,
  "data": {},
  "_metadata": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "data_max_age": 7,
    "approved_statuses": ["Ativo", "Pendente"]
  }
}
```

---

### 4.3 Endpoint 3: Restrições SICAR (R2C Due Diligence)
- **SaaS Proxy Path:** `GET /v2/r2c/restricoes`
- **Upstream Path:** `GET https://api-gateway-v2.registrorural.com.br/r2c/car/{numero_car}/restricoes_sicar`
- **Method:** `GET`
- **Purpose:** Verifies whether the Brazilian Forest Service (SFB) or environmental databases have registered active embargoes, conservation unit overlaps, or infractions on the property. If any active restriction exists, result is `FAILED`. Otherwise, `PASSED`.

#### Parameters:
- `numero_car` (path, string, required)
- `data_max_age` (query, string/integer, optional, default: `7`)

#### Response Schemas:

##### 1. HTTP 200 — Completed (`PASSED` — Clean)
```json
{
  "status": "COMPLETED",
  "result": "PASSED",
  "data": {
    "numero_car": "RS-4300406-AD3BD4B621624DE4B3073DE8675E08A1",
    "data_demonstrativo": "2025-01-21",
    "restricoes": []
  },
  "_metadata": {
    "numero_car": "RS-4300406-AD3BD4B621624DE4B3073DE8675E08A1",
    "data_max_age": 7
  }
}
```

##### 2. HTTP 200 — Completed (`FAILED` — Restrictions Detected)
```json
{
  "status": "COMPLETED",
  "result": "FAILED",
  "data": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "data_demonstrativo": "2025-02-12",
    "restricoes": [
      {
        "id": 1,
        "origem": "Áreas Embargadas Sobreposição",
        "data_registro": "28/12/2022",
        "area_conflito": 0.7836,
        "percentual_conflito": 0,
        "descricao": "Infração: Destruir, desmatar, danificar florestas ou qualquer tipo de vegetação nativa ou de espécies nativas plantadas, objeto de especial preservação, em área de reserva legal..."
      },
      {
        "id": 2,
        "origem": "Áreas Embargadas Sobreposição",
        "data_registro": "28/12/2022",
        "area_conflito": 0.7841,
        "percentual_conflito": 0,
        "descricao": "Infração: Infração da Flora (Não Classificada-Móvel)"
      }
    ]
  },
  "_metadata": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "data_max_age": 7
  }
}
```

##### 3. HTTP 202 — Pending
```json
{
  "status": "PENDING",
  "result": null,
  "data": {},
  "_metadata": {
    "numero_car": "AM-1304104-CFC3C82E13654D0C8F6F71B025E1FBBA",
    "data_max_age": 7
  }
}
```

---

### 4.4 Related Discovered Endpoints
During probing of the authoritative documentation at `docs.registrorural.com.br`, four related complementary endpoints were identified:

1. **`GET /car/consulta/{numero_car}/dados`**:  
   Returns land registry contact details (`dados_contato`), property title records (`matriculas` with cartório book/sheet), legal owners (`titulares`), and cadastral applicant (`cadastrante` CPF and name).
2. **`GET /car/busca/coordenada?lat={lat}&lng={lng}&radius={meters}`**:  
   Spatial lookup that identifies CAR perimeters encompassing or intersecting a GPS coordinate point. Essential when farmers input coordinates or drop a pin on the 2D map.
3. **`GET /car/busca/municipio`**:  
   Queries properties by municipality IBGE code or UF.
4. **`GET /car/busca/cpf_cnpj`**:  
   Cross-references all properties registered under a producer's CPF or corporate CNPJ.

---

## 5. Asynchronous Polling Lifecycle & Engine

Because federal SICAR queries frequently involve synchronous bottlenecks on government databases, the Registro Rural API acts as an asynchronous proxy.

```
       [Client Initiates Request]
                    |
                    v
         [HTTP GET /demonstrativo]
                    |
          +---------+---------+
          |                   |
    [HTTP 404/401/403]   [HTTP 200/202]
          |                   |
    HALT IMMEDIATELY     Check status
          v                   |
     Emit Error               +-------------------+
                              |                   |
                       status == PENDING   status == COMPLETE
                              |                   |
                       Wait interval (3s)    Return Data
                              |
                       Increment Attempt
                              |
                        [Attempts > 20?]
                         /          \
                       YES           NO
                       /              \
                Timeout Error      Poll Again
```

### 5.1 Polling Engine Parameters

| Parameter | Value | Rationale |
|---|---|---|
| **Initial Delay** | `2,000 ms` | Allows fast-cache lookups without unnecessary immediate delay |
| **Polling Interval** | `3,000 ms` | Balance between prompt responsiveness and rate-limiting avoidance |
| **Backoff Multiplier** | `1.2x` | Gradually spaces out requests for long-running SICAR fetches |
| **Max Interval Cap** | `6,000 ms` | Caps maximum delay between polling rounds |
| **Maximum Timeout** | `60,000 ms` (60 seconds) | Fail-safe ceiling for SaaS interactive onboarding UX |
| **Maximum Attempts** | `20 attempts` | Prevents infinite loops on stuck upstream jobs |

### 5.2 Status Code & Field Discrepancies
- **Demonstrativo API (`/car/consulta/...`)**: Returns **HTTP 200** for both `PENDING` and `COMPLETE`. The client must check `response.status === "COMPLETE" && response.data !== null`.
- **R2C Compliance API (`/r2c/...`)**: Returns **HTTP 202 Accepted** when `PENDING` (`status: "PENDING"`), and **HTTP 200 OK** when finished (`status: "COMPLETED"`).
- The client implementation must normalize both status flags:
  - Pending: `status.toUpperCase() === "PENDING"`
  - Complete: `status.toUpperCase().startsWith("COMPLET")`

---

## 6. Complete SICAR Demonstrativo Data Dictionary

The `dados` object in the demonstrativo contains two primary nodes: `cabecalho` and `areas`.

### 6.1 Header Metadata (`dados.cabecalho`)

| Field | Type | Description | Unit / Example |
|---|---|---|---|
| `codigo` | `string` | Unique Federal CAR alphanumeric code | `PA-1507300-FC136733...` |
| `statusImovel` | `string` | Current legal administrative status: `Ativo`, `Pendente`, `Suspenso`, `Cancelado` | `"Ativo"` |
| `condicaoAnalise` | `string` | SFB state analysis stage (`Aguardando análise`, `Em análise`, `Analisado`) | `"Aguardando análise"` |
| `municipio` | `string` | Name of municipality | `"São Félix do Xingu"` |
| `estado` | `string` | Brazilian state federation code (UF) | `"PA"` |
| `area` | `number` | Gross declared property area ($A_{\text{total}}$) | Hectares (ha) |
| `modulosFiscais` | `number` | Fiscal modules calculated per regional INCRA coefficient | Numeric value |
| `centroideX` | `number` | Longitude of property centroid (WGS84) | Decimal degrees (e.g. `-52.8228`) |
| `centroideY` | `number` | Latitude of property centroid (WGS84) | Decimal degrees (e.g. `-6.5679`) |
| `latitude` | `string` | Formatted DMS latitude string | `06°34'04,74" S` |
| `longitude` | `string` | Formatted DMS longitude string | `52°49'22,12" O` |
| `dataRegistro` | `string` | Initial registration date in SICAR | DD/MM/YYYY |
| `dataRetificacao` | `string` | Most recent amendment/rectification date | DD/MM/YYYY |
| `dataDemonstrativo` | `string` | Timestamp when this demonstrativo was issued | DD/MM/YY HH:mm |
| `houveRetificacao`| `boolean` | Flag indicating if registration was modified | `true` / `false` |
| `aderiuPRA` | `boolean?`| Environmental Regularization Program (PRA) opt-in | `true`, `false`, `null` |
| `condicaoPRA` | `string?` | Status within PRA program | `null` or stage |

### 6.2 Spatial & Environmental Metrics (`dados.areas`)

| Key | Type | Category | Definition & Legal Basis |
|---|---|---|---|
| `areaLiquida` | `number` | Base | Net property area registered after cartographic adjustments ($A_{\text{total}} - \text{easements}$) |
| `areaAPP` | `number` | Conservation | Total Permanent Preservation Area (Área de Preservação Permanente) |
| `areaAPPEmAC` | `number` | Overlap | APP established over Consolidated Use Area (Área de Uso Consolidado) |
| `areaAPPEmAA` | `number` | Overlap | APP over Anthropized Area (Área Antropizada) |
| `areaAPPRecompor` | `number` | Liability | APP required by law to be reforested / restored |
| `areaAPPSobrepostaRVN` | `number` | Overlap | APP overlapping native vegetation remnants |
| `areaRLMinimaExigidaLei`| `number` | Legal Quota | Minimum Legal Reserve mandated by Forest Code (80% Amazon, 35% Cerrado Legal Amazon, 20% others) |
| `areaRLDeclarada` | `number` | Conservation | Officially declared Legal Reserve in initial filing |
| `areaRLP` | `number` | Conservation | Proposed Legal Reserve area ($A_{\text{RL,proposta}}$) |
| `areaRLA` | `number` | Conservation | Approved Legal Reserve area ($A_{\text{RL,aprovada}}$) |
| `areaRLANA` | `number` | Conservation | Unapproved Legal Reserve area |
| `areaRLEmAPP` | `number` | Overlap | Legal Reserve computed inside APP boundaries (Art. 15 Lei 12.651/2012) |
| `areaRLRecompor` | `number` | Liability | Legal Reserve required to be restored (environmental deficit) |
| `areaRLRecomporAA` | `number` | Liability | RL restoration required within Anthropized Area |
| `areaRLRecomporAC` | `number` | Liability | RL restoration required within Consolidated Use Area |
| `areaRLVetorizadaSobrepostaRVN` | `number` | Overlap | Vectorized RL overlapping Remnants of Native Vegetation |
| `areaRLExcedentePassivo` | `number` | Balance | Net RL deficit/surplus (negative = passivo/deficit; positive = surplus/CRA) |
| `situacaoRL` | `string` | Status | Status of Legal Reserve analysis (`"Não Analisada"`, `"Regular"`, etc.) |
| `areaRVN` | `number` | Native Veg | Remanescente de Vegetação Nativa (total native vegetation remnants) |
| `areaUsoConsolidado` | `number` | Agronomic | Consolidated agricultural or pastoral land in use prior to July 22, 2008 |
| `areaAA` | `number` | Agronomic | Área Antropizada (altered land post-2008) |
| `areaAP` | `number` | Agronomic | Área de Pousio (agricultural fallow land) |
| `areaUsoRestrito` | `number` | Exclusion | Restricted use area (pantanais, slopes 25°–45°) |
| `areaUREmAC` | `number` | Overlap | Restricted use area over Consolidated Use |
| `areaUREmAA` | `number` | Overlap | Restricted use area over Anthropized Area |
| `areaUsoRestritoRecompor` | `number` | Liability | Restricted use area requiring restoration |
| `areaServidaoAdministrativa` | `number` | Infrastructure| Administrative easements (high-voltage transmission lines, pipelines, roads) |
| `areaSobreposicaoOutrosImoveis` | `number` | Dispute | Overlap area with neighboring private CAR registrations (titular dispute) |
| `areaSobreposicaoUC` | `number` | Conflict | Overlap area with Conservation Units (Unidades de Conservação) |
| `areaSobreposicaoTI` | `number` | Conflict | Overlap area with Indigenous Lands (Terras Indígenas) |
| `areaSobreposicaoAssentamento` | `number` | Conflict | Overlap area with INCRA Agrarian Reform Settlements |

---

## 7. Model M1 Net Plantable Area (*Área Útil Líquida*) & Boundary Logic

### 7.1 The Agronomic & Credit Problem
Unscrupulous borrowers frequently pledge the entire gross area ($A_{\text{total}}$) of a property to collateralize agricultural credit (CPR) across multiple lenders. If a 10,000 ha property contains 8,000 ha of Legal Reserve and APP, only 2,000 ha can legally produce grain. Underwriting based on $A_{\text{total}}$ creates uncollateralized loan defaults.

Model M1 calculates the exact **Net Plantable Area ($A_{\text{AUL}}$)** and its spatial polygon.

### 7.2 Mathematical Formulation (Model M1)

Let:
- $A_{\text{total}} = \text{dados.cabecalho.area}$ (Gross declared area)
- $A_{\text{APP}} = \text{dados.areas.areaAPP}$
- $A_{\text{RL}} = \max(\text{dados.areas.areaRLP}, \text{dados.areas.areaRLA})$
- $A_{\text{RLEmAPP}} = \text{dados.areas.areaRLEmAPP}$ (Art. 15 overlap deduction)
- $A_{\text{servidao}} = \text{dados.areas.areaServidaoAdministrativa}$
- $A_{\text{restrito}} = \text{dados.areas.areaUsoRestrito}$
- $A_{\text{disputa}} = \text{dados.areas.areaSobreposicaoOutrosImoveis}$
- $A_{\text{conflito\_publico}} = \text{dados.areas.areaSobreposicaoTI} + \text{dados.areas.areaSobreposicaoUC} + \text{dados.areas.areaSobreposicaoAssentamento}$
- $A_{\text{embargos}} = \sum \text{areaConflito}_{\text{IBAMA/ICMBio}}$ (active embargoes)

#### Step 1: Conservation Area Deduplication
Under Art. 15 of Federal Law 12.651/2012, APP can be computed within the Legal Reserve percentage. To avoid double-deducting the overlap, the union of conservation areas is:
$$A_{\text{conservacao}} = A_{\text{APP}} + A_{\text{RL}} - A_{\text{RLEmAPP}}$$

#### Step 2: Total Statutory Deductions
Total area legally excluded from agricultural planting:
$$D_{\text{total}} = A_{\text{conservacao}} + A_{\text{servidao}} + A_{\text{restrito}} + A_{\text{disputa}} + A_{\text{conflito\_publico}} + A_{\text{embargos}}$$

#### Step 3: Deductive Net Plantable Area ($A_{\text{AUL,dedutivo}}$)
$$A_{\text{AUL,dedutivo}} = \max\left(0, A_{\text{total}} - D_{\text{total}}\right)$$

#### Step 4: Consolidated Land Cross-Verification ($A_{\text{AUL,consolidada}}$)
Agricultural credit under MCR 2-9 is strictly restricted to consolidated production zones. The agronomic effective plantable area is cross-checked against consolidated use minus mandatory restoration liabilities:
$$A_{\text{AUL,consolidada}} = \max\left(0, \text{dados.areas.areaUsoConsolidado} - \text{dados.areas.areaAPPRecompor} - \text{dados.areas.areaRLRecompor}\right)$$

#### Step 5: Final Certified Net Plantable Area
$$A_{\text{AUL}} = \min(A_{\text{AUL,dedutivo}}, A_{\text{AUL,consolidada}})$$
$$\text{Plantability Ratio } (\Phi_{\text{AUL}}) = \frac{A_{\text{AUL}}}{A_{\text{total}}}$$

*Note:* If $\Phi_{\text{AUL}} < 0.15$ or $A_{\text{AUL}} \le 0$, the property is flagged as **Agronomically Ineligible for Crop Financing**.

---

### 7.3 Vector Boundary Intersection Logic (Spatial GIS)

When vector geometries are provided (via KML upload, GeoJSON, or SICAR layer vectors):

```
                        +---------------------------+
                        |   CAR Property Boundary   |
                        |   (Polygon / MultiPoly)   |
                        +---------------------------+
                                      |
                     [Boolean Difference: ST_Difference]
                                      |
             +------------------------+------------------------+
             |                        |                        |
             v                        v                        v
   [Union: APP Polygons]   [Union: RL Polygons]   [Union: Embargo Polygons]
             |                        |                        |
             +------------------------+------------------------+
                                      |
                                      v
                        +---------------------------+
                        |    Net Plantable Area     |
                        |     (Vector Polygons)     |
                        +---------------------------+
```

1. **Topological Cleaning:** Ensure the boundary geometry is valid according to OGC standards (`ST_IsValid` or `turf.cleanCoords`). If self-intersecting, apply `ST_Buffer(geom, 0)` or `turf.unkinkPolygon`.
2. **Conservation Dissolve:** Compute the spatial geometric union:
   $$\mathbf{G}_{\text{conservacao}} = \mathbf{G}_{\text{APP}} \cup \mathbf{G}_{\text{ReservaLegal}}$$
3. **Exclusion Dissolve:** Compute the union of all exclusion vectors:
   $$\mathbf{G}_{\text{exclusoes}} = \mathbf{G}_{\text{conservacao}} \cup \mathbf{G}_{\text{Servidao}} \cup \mathbf{G}_{\text{Embargos}} \cup \mathbf{G}_{\text{SobreposicaoPublica}}$$
4. **Boolean Difference (Hole Punching):**
   $$\mathbf{G}_{\text{AUL}} = \mathbf{G}_{\text{Property}} \setminus \mathbf{G}_{\text{exclusoes}}$$
5. **Coordinate Reference System (CRS) & Projection Rules:**
   - Storage / Ingestion: **EPSG:4326 (WGS 84)**.
   - Geodesic Area Calculation: Must be reprojected to the appropriate local UTM projection (e.g. **EPSG:31983 / SIRGAS 2000 UTM 23S** for Buritis/MG) or calculated using ellipsoidal algorithms (`geodesicArea` / WGS84 ellipsoid $a=6378137.0, f=1/298.257223563$).

---

## 8. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| **1** | CAR Demonstrativo | `GET /v2/car/demonstrativo/{car}` | Queries full official SICAR demonstrativo from Registro Rural Gateway | `numero_car` (path), `max_age` (query: default `7`) | `status`: `"COMPLETE"`, `data`: `{ car_id, dados: { cabecalho, areas, restricoes } }` | HTTP 404 (`"CAR não encontrado"`), HTTP 401 (`"Unauthorized"`), HTTP 429 (`"Rate limit"`) | `consultademonstrativodocar.md` |
| **2** | Asynchronous Polling | Demonstrativo Polling Lifecycle | Handles asynchronous SICAR fetch when job is queued upstream | Initial delay 2s, retry interval 3s, max attempts 20 | `status`: `"PENDING"` $\to$ `status`: `"COMPLETE"` with hydrated payload | Timeout after 60s raises `SICAR_POLLING_TIMEOUT` error | `consultademonstrativodocar.md` |
| **3** | R2C Due Diligence | `GET /v2/r2c/situacao` | Validates active legal situation of CAR (`Ativo` or `Pendente`) | `numero_car` (path), `approved_statuses` (query), `data_max_age` (query) | `status`: `"COMPLETED"`, `result`: `"PASSED"` or `"FAILED"`, `data`: `{ situacao_car }` | HTTP 202 (`PENDING`), HTTP 404 (`Not Found`) | `situaocar.md` |
| **4** | R2C Due Diligence | `GET /v2/r2c/restricoes` | Validates absence of environmental restrictions, embargoes, and overlaps | `numero_car` (path), `data_max_age` (query) | `status`: `"COMPLETED"`, `result`: `"PASSED"` or `"FAILED"`, `data`: `{ restricoes: [] }` | HTTP 202 (`PENDING`), HTTP 404 (`Not Found`) | `restriessicar.md` |
| **5** | Cadastral Enrichment | `GET /car/consulta/{numero_car}/dados` | Fetches contact info, cartório matriculas, cadastrante, and titulares | `numero_car` (path), `allow_incomplete_data` (query) | `status`: `"COMPLETE"`, `data`: `{ cadastrante, matriculas, dados_basicos, titulares }` | HTTP 404 (`CAR não encontrado`) | `consultadadosdocar.md` |
| **6** | Spatial Discovery | `GET /car/busca/coordenada` | Discovers CAR registration code from latitude/longitude and radius | `lat` (query), `lng` (query), `radius` (query) | `data`: `[ "UF-0000000-..." ]`, `total`: `number` | HTTP 400 (`Bad Request`) | `buscaporcoordenada.md` |
| **7** | Model M1 | Net Plantable Area (*Área Útil Líquida*) Calculation | Computes net arable area by deducting APP, RL, easements, overlaps, and embargoes | `dados.cabecalho.area`, `dados.areas.*` | Net area in ha ($A_{\text{AUL}}$), plantability ratio ($\Phi_{\text{AUL}}$) | Halts with `Ineligible` flag if $A_{\text{AUL}} \le 0$ | SFB / MCR 2-9 / ORIGINAL_REQUEST.md |
| **8** | Model M1 | Vector Boundary Hole Punching | Computes polygon geometric difference: $\text{Gleba} \setminus (\text{APP} \cup \text{RL} \cup \text{Embargos})$ | GeoJSON coordinates (EPSG:4326) | Clipped GeoJSON Polygon / MultiPolygon | Catches self-intersections and repairs with `turf.unkinkPolygon` | GIS spatial specifications / `spatialUtils.ts` |
| **9** | Security & Auth | Strict Mode Credential Guard | Halts pipeline immediately if `REGISTRO_RURAL_API_KEY` is absent or unauthorized | `REGISTRO_RURAL_API_KEY` in environment | Valid API key forwarded in `X-API-Key` header | Explicit diagnostic exception thrown; no silent mock fallback | ORIGINAL_REQUEST.md (Requirement R1) |
| **10** | Risk Scoring | ScoreCard Enrichment Matrix | Synthesizes CAR status, SIGEF tenure, IBAMA embargoes, and M1 plantable ratio | Combined enrichment payload | ESG Score (0–100), Risk Level (`BAIXO` to `CRÍTICO`), Credit Passport Eligibility | Visual indicators and blockades on critical failure | `ScoreCard.tsx` / `route.ts` |

---

## 9. Edge Cases & Failure Modes

| # | Feature | Input Condition | Observed / Documented Behavior | Required Mitigation & System Response |
|---|---|---|---|---|
| **E1** | Strict Production Mode | Missing `REGISTRO_RURAL_API_KEY` in `.env.local` | Application crashes or API fails silently | Throw explicit error `CONFIG_MISSING_API_KEY: REGISTRO_RURAL_API_KEY is not defined`. Display configuration modal to admin. |
| **E2** | Strict Production Mode | Invalid or expired API Key | Upstream returns HTTP 401/403 with `{"message": "Forbidden"}` | Halt onboarding pipeline immediately with `AUTH_UNAUTHORIZED`. Do not poll. |
| **E3** | Demonstrativo API | Unregistered or malformed CAR code | Upstream returns HTTP 404 with `{"error": "CAR não encontrado"}` | Display input validation error on Onboarding Wizard: `"CAR não encontrado no SICAR nacional"`. |
| **E4** | Asynchronous Polling | High SICAR queue load (poll count > 20) | Successive `status: "PENDING"` responses | Terminate after 60s with `SICAR_POLLING_TIMEOUT`. Offer user "Try again" or background notification hook. |
| **E5** | Asynchronous Polling | Fast cached result | Upstream immediately returns HTTP 200 with `status: "COMPLETE"` | Skip delay loop, process data immediately in single round-trip. |
| **E6** | Model M1 Calculation | Property with 100% Conservation / Legal Reserve | $A_{\text{conservacao}} \ge A_{\text{total}}$ | $A_{\text{AUL}}$ evaluates to `0.00 ha`. Display alert: `"Imóvel sem área útil plantável (100% Preservação)"`. |
| **E7** | Model M1 Calculation | Legal Reserve overlapping APP ($A_{\text{RLEmAPP}} > 0$) | $A_{\text{APP}} + A_{\text{RL}} > A_{\text{total}}$, but legal overlap is permitted | Apply deduplication formula: $A_{\text{conservacao}} = A_{\text{APP}} + A_{\text{RL}} - A_{\text{RLEmAPP}}$ to prevent double deduction. |
| **E8** | Model M1 Vector GIS | APP geometry extends slightly outside CAR perimeter | Vector polygon boundary sliver errors | Clip $\mathbf{G}_{\text{APP}}$ with $\mathbf{G}_{\text{CAR}}$ via `turf.intersect` before performing Boolean difference. |
| **E9** | R2C Due Diligence | Suspended CAR status (`Suspenso`) | Upstream `/v2/r2c/situacao` returns `result: "FAILED"` | Set ScoreCard to `BLOQUEADO`, Risk Level to `CRÍTICO`, disqualify from Passaporte de Crédito Rural. |
| **E10** | R2C Due Diligence | Active IBAMA embargo intersecting parcel | Upstream `/v2/r2c/restricoes` returns `restricoes: [{origem: "Áreas Embargadas..."}]` | Render embargo polygons in red, subtract embargo area from $A_{\text{AUL}}$, trigger MCR 2-9 non-compliance alert. |
| **E11** | Registro Rural Billing | Account credit balance reaches zero | Upstream returns HTTP 402 with `{"message": "Insufficient credits"}` | Halt immediately with `BILLING_INSUFFICIENT_CREDITS`. Send administrative webhook. |
| **E12** | Geometry Projection | Multi-coordinate WGS84 polygon area calculation | Distortions in spherical area calculation at non-equatorial latitudes | Use ellipsoidal geodesic integration (WGS84) or UTM 23S projection to calculate precise hectares. |

---

## 10. Test & Validation Fixtures

### Fixture 1: Real Compliant Parcel (Fazenda Buritis, MG)
- **CAR Code:** `MG-3109300-4829A0D7314B4A45A7C49102B94C7192`
- **Location:** Buritis, Minas Gerais (Cerrado Biome)
- **Gross Area:** `217.12 ha`
- **APP Area:** `26.91 ha` (12.4%)
- **Reserva Legal Area:** `43.42 ha` (20.0%)
- **M1 Net Plantable Area:** `146.79 ha`
- **Expected Compliance:**
  - Status SICAR: `Ativo / Regular`
  - Restrições: `0` (Clean)
  - Result: `PASSED`
  - Score ESG: `96 / 100` (BAIXO RISCO)
  - Credit Passport: `Elegível`

### Fixture 2: Embargoed Parcel (Fazenda Rio Preto, Sorriso/MT)
- **CAR Code:** `MT-5107909-6C8E91A0B2C3D4E5F67890123456789A`
- **Location:** Sorriso, Mato Grosso (Amazon Biome)
- **Gross Area:** `1,250.00 ha`
- **Embargo Intersection:** `14.80 ha` (IBAMA TAD-991204-A)
- **Expected Compliance:**
  - Status SICAR: `Ativo`
  - Restrições: `1` (Active Embargo)
  - Result: `FAILED`
  - Score ESG: `38 / 100` (RISCO CRÍTICO)
  - Credit Passport: `Bloqueado`

### Fixture 3: Amazon Biome Heavy Forest / High Conservation (Upstream OpenAPI Reference)
- **CAR Code:** `PA-1507300-FC136733C09E4DEE9BFDBE8C016B2FE7`
- **Location:** São Félix do Xingu, Pará
- **Gross Area:** `19,993.21 ha`
- **APP Area:** `1,544.91 ha`
- **Reserva Legal Minima (80% Amazon Forest):** `15,918.99 ha`
- **Reserva Legal Passivo:** `-6,850.03 ha` (Severe Deficit)
- **Overlap APA Triunfo do Xingu:** `19,993.21 ha` (100% Conflict)
- **Expected Compliance:**
  - Result: `FAILED` (Active Environmental Restriction)
  - M1 Net Plantable Area: Confined to consolidated degraded zone (`10,657.21 ha`) minus restoration requirements (`284.46 ha` RL + `516.60 ha` APP).

---

## 11. Implementation Action Items for Milestones

1. **Environment & Gateway Setup:**
   - Register `REGISTRO_RURAL_API_KEY` in `.env.example` and documentation.
   - Create typed API client in `src/lib/registroRuralClient.ts`.
2. **API Routes Implementation:**
   - Implement route handlers `src/app/api/v2/car/demonstrativo/[car]/route.ts`, `src/app/api/v2/r2c/situacao/route.ts`, and `src/app/api/v2/r2c/restricoes/route.ts`.
   - Implement asynchronous polling engine with exponential backoff.
3. **Core Model M1 Engine:**
   - Implement `calculateModelM1NetPlantableArea(areas: SicarAreas, cabecalho: SicarCabecalho)` in `src/lib/spatialUtils.ts`.
   - Implement vector difference clipping with Turf.js for GeoJSON boundary layers.
4. **Integration with Land Onboarding Wizard:**
   - Connect `src/app/api/land/enrich/route.ts` to execute live calls via `registroRuralClient.ts` when `REGISTRO_RURAL_API_KEY` is present.
   - Wire ScoreCard to reflect real R2C `PASSED` / `FAILED` status.

---
*Report authored by CAR & SICAR Regulatory Spec Miner for Agrostech SaaS MVP.*
