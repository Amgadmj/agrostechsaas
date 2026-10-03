# User Journeys & Demo Script

Walked in a browser on 2026-10-03 (`npm run dev`, demo env, no API keys). Use this as the manual smoke test until the Playwright suite exists (KI-31).

## Routes

| Route | Who | What |
|---|---|---|
| `/` | any | Redirects to `/dashboard`; the middleware sends anonymous users to `/login?redirect=…` |
| `/login` | anonymous | Portal picker: **Produtor Rural (B2C)** or **Institucional & Bancário (B2B)**, plus an e-mail/password form |
| `/dashboard` | B2B / B2C | Portfolio sidebar (parcel list and parcel detail) + 2D map (satellite, MapBiomas, APP/RL vectors) |
| `/dashboard/onboard` | B2B / B2C | 3-step wizard: **1. Entrada** → **2. Radar Scanner** → **3. Dossiê & Mini-Map** |
| `/dashboard/shield-rj` | B2B | Fraud war room: KPIs, forensic pipeline / graph, evidence table, timeline, petition draft |
| `/dashboard/land/[id]/3d` | B2B / B2C | Cesium 3D twin. Demo id: `buritis-gleba-sede`. Unknown ids → 404 |

## Demo script (≈ 7 minutes)

**Setup.** Copy `.env.example` to `.env.local` and keep `NEXT_PUBLIC_DEMO_MODE=true`. Set `NEXT_PUBLIC_CESIUM_ION_TOKEN`, or the 3D globe has no imagery (KI-33). Run `npm run dev`.

1. **Login.** Open `/`. You land on `/login`. Click **Portal Institucional & Bancário (B2B)**. *(This sets the `agrostech_demo_role=b2b_admin` cookie.)*
2. **Portfolio (`/dashboard`).**
   - The header shows **ENTERPRISE B2B** and the amber **DADOS DE DEMONSTRAÇÃO** badge.
   - The sidebar lists 7 parcels. Select **Fazenda Buritis — Gleba Total (217,12 ha)** to see the area, APP (26,91 ha), Reserva Legal (43,42 ha) and the CAR code.
   - The map card **Auditoria Temática MapBiomas** breaks land use down to 146,79 ha soy, 43,42 ha RL and 26,91 ha APP.
   - *Known:* the MapBiomas WMS host is down, so you get a "Camada indisponível" chip (KI-28).
3. **Onboarding (`Novo Imóvel`).**
   - Click the preset **Fazenda Buritis**, then **Iniciar Varredura Geoespacial**.
   - The radar scanner runs through SICAR → SIGEF → IBGE/CPRM → IBAMA.
   - Step 3 shows **Origem: Base de Demonstração (Fixture Offline)**, the mini-map with the boundary, APP and RL, and the M1 card: **146,79 ha net, 67,6 % plantable, ESG 96, risk BAIXO**. It also shows the CMN 5.267 monitoring card (**dispensado**, ≤ 300 ha) and the **MCR 2-9 matrix**.
   - Try the **Fazenda Rio Preto (Alerta Embargo)** preset to see a blocked case.
4. **Shield-RJ.**
   - Walk the KPIs (SAR Δ −6,2 dB, S_clima, SEFAZ triangulation, STJ precedent).
   - Then the 5-column forensic pipeline (Ativo → Órbita → Societário → Escoamento → Destino) and the evidence table filtered by vector.
   - Say clearly that **this is a fictional demonstration case** (KI-07, KI-37).
5. **3D twin (`Gêmeo 3D`).**
   - Click **Voo Drone (35°)** to fly to the parcel. It does not fly automatically (KI-43).
   - Show the extruded 120 m cadastral prism over terrain, then switch to **Ortofoto Nadir** and **Órbita Baixa**.
6. **Dossier.** From Shield-RJ, open the petition/dossier modal and export the PDF. Point at the SHA-256 hash. **Do not call it digitally signed** (KI-01).

## Personas and their key questions

| Persona | Question the product must answer |
|---|---|
| Credit analyst (bank) | "How many hectares can really back this CPR, and is the operation impeded under MCR 2-9?" |
| Credit committee | "Show me the evidence, its sources and its date." |
| Barter / trading risk | "Was the crop planted and harvested, and where did the grain go?" |
| Legal / recovery desk | "Do we have grounds and evidence to act before the bankruptcy stay?" |
| Producer (B2C) | "Is my farm credit-ready, and what do I fix if not?" |
