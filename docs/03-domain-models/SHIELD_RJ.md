# Shield-RJ: Anti-Fraud War Room (Model M3 / Protocolo Halo)

**UI:**
- `src/app/dashboard/shield-rj/page.tsx`
- `src/components/shield-rj/GraphVisualizer.tsx`: entity graph across 5 columns (Ativo → Órbita → Societário → Escoamento → Destino)
- `RedFlagTimeline.tsx`, `EvidenceAuditTable.tsx`
- `StrikeModal.tsx`: drafts a petition (*minuta*)

**Data:** static scenario in the components and in `src/lib/mockData.ts`.
**Logic in `src/lib`:** none yet (KI-27).

> **Status: a demonstration of the product concept.** Every entity, CPF, CNPJ, invoice and event on this page is fictional, and the page computes nothing. This is the feature most likely to impress in a demo and the one most likely to cause legal trouble if mistaken for a real case. Keep it behind `NEXT_PUBLIC_DEMO_MODE` until the logic below exists and counsel has reviewed it (KI-37, KI-38).

## The problem it targets

A "golpe da recuperação judicial" is a pre-planned judicial-recovery fraud. A borrower financed against the crop prepares to file for judicial recovery (RJ). Before filing, they harvest and divert the grain to a third party (often a straw entity, or *laranja*) so it is out of reach when the bankruptcy stay freezes collection. The thesis argues that grain is a fungible good, so pledged grain may be seized pre-emptively (citing STJ REsp 1.758.746/GO and Lei 11.101/2005 art. 49 §3º). **That legal theory must be validated by counsel.**

## The four fraud vectors (as specified)

These rules come from the thesis and the tier-1 tests (`f13_shield_rj.test.ts`, where they are written inline). They are **not implemented** in `src/` yet.

| # | Vector | Rule (spec) | Inputs needed |
|---|---|---|---|
| 1 | **Área Inflada**: over-pledged area | `(gross − M1 net) / gross > 0.35` | M1 output, CPR/credit declared area |
| 2 | **Safra Fantasma**: phantom crop | Season peak γVH < −16 dB (no vegetative cycle) | M2 SAR series |
| 3 | **Fuga de Safra**: grain diversion | M2 harvest detected **and** zero NF-e / MDF-e issued by the debtor | M2 + fiscal documents (SEFAZ) |
| 4 | **Blindagem Pré-RJ**: straw-entity shielding | `S_straw ≥ 0.85`, a weighted score of kinship, age of a new state tax registration (IE) (< 30 days before harvest), lack of machinery, MDF-e routing, protest spikes (CENPROT) | Corporate registry, SEFAZ, CENPROT, rural lease registry (RTD) |

`S_straw = w₁·f_kinship + w₂·f_ie_age + w₃·f_machinery + w₄·f_mdf`. The weights are in the test file and the thesis §5.2. They are not calibrated on real cases.

## What it takes to build it

1. **Data access.** Vectors 3 and 4 need fiscal and corporate data (NF-e/MDF-e, IE registrations, QSA, CENPROT). Each source has its own legal basis and access route, so map the LGPD basis for each before any engineering.
2. **A case model.** Add `shield_cases`, `case_entities` and `case_events` tables, with an evidence chain (source, retrieval time, hash).
3. **Scoring service.** Implement vectors 1–2 first. They need only M1 and M2, which already exist.
4. **Human in the loop.** Shield-RJ should **raise alerts for an analyst**, never auto-generate a filing. The petition generator (`StrikeModal`) should stay a lawyer-reviewed template.
5. **Language.** Use "indica", "compatível com" and "alerta". Never name real companies in demo data.
