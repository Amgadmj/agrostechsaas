# AgrosTech SaaS: UX/UI & Platform Audit (CTO Review)

**Date:** 2026-10-03 · **Build:** localhost:3000 (Next 15 dev, uncommitted working tree on `main`)
**Method:** I tested the app live in a browser at 1024, 1440 and 375 px, through the B2B demo portal across every route. In parallel, an agent did a static code audit of `saas/src`.

## Verdict

The product looks premium and the domain depth is real: the MCR 2-9 matrix, M1 net area and Shield-RJ narrative are differentiated. **It is not yet credible in front of a bank's risk team**, for three reasons:

1. **Trust.** Fictional data is presented as live, and the numbers contradict each other.
2. **Shell.** Each page has its own header, theme and navigation, and mobile is broken.
3. **Integrity.** Auth is a client cookie, the APIs are open, and success messages appear when operations fail.

Fixing the P0s is roughly one focused sprint, and it changes how the demo lands more than any new feature would.

## Scorecard (0–10)

| Area | Score | One-line reason |
|---|---|---|
| Visual polish | 7 | Strong look, but undermined by theme switching between pages |
| Information architecture | 4 | Four routes, three different headers, and the 3D link leaves the app |
| Data credibility | 3 | Unlabeled mocks, contradictory figures, overclaiming copy |
| Accessibility | 3 | About 240 sub-12px labels, no focus styles, 25 unlabeled icon buttons, div-buttons |
| Responsive | 2 | At 375 px there is no nav, the sidebar overflows and the map is unreachable |
| Robustness / states | 4 | Silent failures, `alert()` errors, false success toasts |
| Security (pre-pilot) | 2 | Spoofable cookie auth; `/api/*` is unauthenticated |

## P0: Fix before any external demo

| # | Finding | Evidence |
|---|---|---|
| 1 | **Shield-RJ figures contradict the farm.** Vetor 1 says "10.000 ha declared vs 4.000 ha M1", but Buritis is 217,12 ha gross and 146,79 ha net. An "R$ 10,6M CPR / 85.400 sacas" claim on 146 ha of soy is roughly 10× the plausible output. A bank analyst will catch this in seconds. | `/dashboard/shield-rj`, EvidenceAuditTable, mockData |
| 2 | **Real companies named as creditors in a fraud scenario:** "Bayer, Syngenta, Corteva" in the CENPROT event. This is a legal and reputational risk. | Shield-RJ table, Vetor 4 |
| 3 | **Overclaiming copy:** "Colheita Noturna Clandestina **Provada**", "Frustração por Seca **Impossível**", "Passaporte… **Concedido**". SAR does not prove night-time or intent. | Shield-RJ KPIs, onboarding result |
| 4 | **No demo labelling anywhere.** The dashboard renders 100% from `mockData.ts`. Sidebar shows a hardcoded "Conformidade 100%" and "Regular" on every parcel. Enrich silently falls back to fixtures labelled "Base Homologada". | `dashboard/page.tsx:25`, `Sidebar.tsx`, `api/land/enrich/route.ts:38-84` |
| 5 | **False success states.** `/api/land/save` returns success when the Supabase insert fails. "Protocolar no Plantão" alerts "preparado" even when the fetch fails. | `api/land/save/route.ts:33-44`, `StrikeModal.tsx:224-251` |
| 6 | **Auth is cosmetic.** The client-set `agrostech_demo_role` cookie, or any `sb-*` cookie, unlocks `/dashboard`. The password is never checked. All 6 API routes are unauthenticated. Changing `?portal=b2b` in the URL switches tenant view. | `middleware.ts:19-32`, `login/page.tsx`, `app/api/*` |
| 7 | **Visible broken assets.** The onboarding mini-map tiles render an "API KEY REQUIRED" watermark. Cesium shows the default-ion-token banner and a CORS error loading workers from cesium.com. There are 16+ `ERR_NAME_NOT_RESOLVED` on every page. | `/dashboard/onboard` step 3, `/dashboard/land/1/3d` console |

## P1: Next sprint

- **One app shell.** Header, theme and portal context are inconsistent:
  - The dashboard is light, onboard is dark-only (tokens are static hex values), and Shield-RJ and 3D have their own headers.
  - The Shield-RJ link drops `?portal`.
  - Onboard renders `<Header/>` without `portalRole`, so B2C users see "Banco AgroInvest".
- **3D navigation.** Header/Sidebar "Gêmeo 3D" goes to an external `dashboard-ui-liart-ten.vercel.app`, while the internal `/dashboard/land/[id]/3d` is orphaned. Shield-RJ links to `/land/1/3d`, but id `1` matches no parcel and silently falls back.
- **Header at 1024 px.** Nav labels wrap to 2–3 lines and the user block is clipped. On the map, the Auditoria card and coordinate bar overlap the Real/Cobertura toggle and the polygon.
- **Mobile.** Nav is `hidden md:flex` with no menu. The sidebar has a fixed width (380 px scroll width at 375 px) and the map never appears. Either build a bottom-sheet layout or show an explicit "use desktop" state for the map and graph views.
- **Accessibility.** Fixes needed:
  - Raise the minimum text size to 12 px (about 240 `text-[8–11px]` occurrences).
  - Add global `focus-visible` rings.
  - Add `aria-label` to the ~25 icon buttons.
  - Use `<button>` for clickable divs ("Iniciar Varredura" is a div, and so are the Sidebar parcel cards).
  - Link labels to inputs on login and onboard.
  - Give modals `role="dialog"`, a focus trap and Esc handling.
  - Fix contrast on gray-500/dark and slate-400/light.
- **Error and empty states.** Replace `alert()` with inline banners. Show a "camada indisponível" notice for failed WMS tiles and a "modelo 3D indisponível" notice for GLB failures. Add an empty portfolio state. Shield-RJ opens the "Ficha do Alvo" popover by default, covering the graph.
- **Locale.** Use pt-BR number formatting consistently: today the app mixes "217.12 ha" with "217,12 ha", and "Δ -6.2 dB" with "-6,2 dB". Remove English in the UI, such as "(Save)" and "Benchmark". Drop `select-none` on data containers so users can copy CAR codes and case numbers.

## P2: Hygiene

- Collapse the two token systems (globals.css vars vs static `tailwind.config.ts` hex values) into CSS-var-backed tokens. There are about 380 hardcoded hex values.
- Fix undefined classes: `text-brand-lime`, `shadow-neon-lg`.
- Fix the font mismatch: config says Space Grotesk, the layout loads Bricolage.
- Delete the duplicate `wizard/ScoreCard.tsx`.
- Label the RadarScanner random blips as "simulação".
- Hide the Next dev indicator, which overlaps the bottom-left content in demos.

## What's working (keep it)

- The login "portal" choice is a smart demo device.
- The onboarding 3-step pipeline (Entrada → Radar → Dossiê) tells the story well.
- The MCR 2-9 matrix and the "Como usar estes dados no crédito rural?" affordance are exactly the right framing for a bank.
- Shield-RJ's 5-column forensic pipeline (Ativo → Órbita → Societário → Escoamento → Destino) is a genuinely strong visualization once the data is coherent.
