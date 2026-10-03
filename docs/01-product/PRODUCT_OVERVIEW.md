# Product Overview

## One sentence

AgrosTech Beta SaaS lets a rural lender **see the farm behind the loan**: its legal plantable area, its regulatory standing, its crop through the clouds and its terrain in 3D. It packages that into evidence a credit committee and a regulator can accept.

## Who it is for

| Segment | Buyer | Job to be done |
|---|---|---|
| Banks and cooperatives (crédito rural) | Credit risk / agro desk | Underwrite and monitor rural credit under MCR 2-9; avoid financing impeded properties; prove continuous monitoring |
| Barter desks and trading companies | Commercial / risk | Make sure the grain promised in a CPR is planted, harvested and delivered |
| FIAGRO / CRA funds | Portfolio risk | Portfolio-level collateral health and early warning |
| Rural producers (B2C) | Farm owner | A "Passaporte de Crédito Rural" that shortens credit approval |

The login screen offers the two portals: **B2B** (an institutional portfolio, demo org "Banco AgroInvest") and **B2C** (a single producer, Fazenda Buritis).

## The product's three pillars

### 1. Credit and finance
- **Onboarding wizard**: CAR code and/or KML/GeoJSON upload → enrichment (SICAR, situação, restrições, IBAMA) → ScoreCard.
- **Model M1**: the net plantable area ([details](../03-domain-models/M1_NET_PLANTABLE_AREA.md)).
- **ScoreCard and Passaporte**: ESG score, risk level (BAIXO / MÉDIO / ALTO / CRÍTICO), eligibility and recommendations.
- **MCR 2-9 dossier**: JSON or PDF with an integrity hash ([details](../03-domain-models/MCR29_DOSSIER.md)).

### 2. Collateral monitoring and fraud defence
- **Model M2**: Sentinel-1 SAR harvest detection through cloud ([details](../03-domain-models/M2_SAR_HARVEST_ENGINE.md)).
- **Commercial SAR tasking**: sub-metre radar on demand, for disputes.
- **Shield-RJ**: the fraud-vector war room for pre-planned judicial recovery schemes ([details](../03-domain-models/SHIELD_RJ.md)).

### 3. 3D digital twin of the land
- **Cesium 3D globe**: terrain, the extruded cadastral boundary and drone models ([details](../02-architecture/DIGITAL_TWIN_3D.md)).
- **2D map**: satellite basemap, MapBiomas Coleção 9 land-use themes, APP / Reserva Legal / embargo layers.

## Positioning (from the strategy documents)

- **Regulatory forcing function.** Per the thesis, Resolução CMN 5.267/2025 makes continuous remote monitoring of financed properties over 300 ha a non-delegable obligation of the lender. **Counsel must confirm this before it is used in sales** (KI-37).
- **Surveillance pyramid ("drone só na anomalia").** Free radar on 100 % of hectares → algorithmic anomaly detection → paid commercial SAR or a drone flight only on confirmed anomalies. This is what makes per-hectare SaaS pricing viable. See [thesis §7](../strategy/IP_MODELS_AND_3D_DIGITAL_TWIN_THESIS.md).
- **Moat claims.** The thesis names proprietary models (M1 / M2 / M3), the drone-operations ground truth, ICP-Brasil-grade evidence and the 3D twin. Engineering status for each claim is in [`CTO_HANDOVER.md`](../00-handover/CTO_HANDOVER.md#3-honest-status-what-is-real-and-what-is-demo).

## Product rules (non-negotiable)

1. **pt-BR UI**, with pt-BR number formatting (`src/lib/format.ts`).
2. **No certainty the data can't support.** "Indica", "compatível com" and "alerta", never "provado", "impossível" or "concedido".
3. **Demo data is always labelled** ("Dados de Demonstração" badge; `source: live | fixture`).
4. **No real companies** as debtors or creditors in demo data.
5. **No turnaround times (*prazos*)** in client-facing copy.

## Further reading

- [User journeys and demo script](./USER_JOURNEYS.md)
- [Regulatory context](./REGULATORY_CONTEXT.md)
- [Original investor-facing product docs (data room)](../strategy/data-room-product/). These predate the 2026-09-26 build and are partly outdated, so read them for intent, not status.
