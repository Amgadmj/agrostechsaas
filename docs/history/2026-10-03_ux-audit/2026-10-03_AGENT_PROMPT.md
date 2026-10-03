# Agent Team Brief: AgrosTech SaaS Remediation Sprint

> Paste everything below the line into the orchestrator agent (Antigravity Manager view). Each workstream is sized for one agent. Agents must load only the files listed for their workstream.

---

## Role & mission
You are the engineering team for the AgrosTech SaaS (`saas/`, Next.js 15 App Router, React 19, Tailwind, MapLibre/Deck.gl, Cesium). A CTO audit on 2026-10-03 found the app looks premium but **is not credible in front of a bank risk team**. Your mission is to make the demo **trustworthy, consistent and robust**. Do not add features.

**Single source of truth for findings:** `saas/audits/2026-10-03_UX_AUDIT_REPORT.md`. Read it once, then work only on your workstream's rows. Do not re-audit.

## Ground rules (context and cost discipline)
1. **Baseline first.** The working tree has about 40 uncommitted changes. The orchestrator creates the branch `fix/ux-audit-2026-10` and commits the baseline before any agent starts.
2. **File ownership is exclusive.** Only touch files listed in your workstream. If you need a change in another workstream's file, write a one-line request in `saas/audits/HANDOFFS.md` and do not edit it.
3. **Read narrowly.** Never read `node_modules`, `.next`, lockfiles or `public/` binaries. Use grep or symbol search before opening a file, and open line ranges rather than whole files when a file is over 300 lines.
4. **No new dependencies** without orchestrator approval. Reuse the existing `components/ui/*`.
5. **UI language is pt-BR.** Use pt-BR number formatting via one shared `formatHa()` / `formatNumber()` helper in `src/lib/format.ts` (owned by WS-B).
6. **Never claim certainty the data can't support.** Use "indica", "compatível com" and "alerta"; never "provado", "impossível" or "concedido". Never name real companies as debtors or creditors in demo data. Never publish turnaround times (prazos).
7. **Definition of done, for every workstream:**
   - `npx tsc --noEmit` passes.
   - `npm run build` passes.
   - The touched route is checked at 1440 px and 375 px in a browser, with zero new console errors.
   - Before/after screenshots go in your PR description.
8. **Report back in at most 15 lines:** files changed, acceptance criteria met (✅/❌), open handoffs. Do not paste diffs.

## Workstreams (run in parallel; WS-A merges first)

### WS-A: Data credibility & demo labelling (P0 #1–4)
**Owns:** `src/lib/mockData.ts`, `src/components/shield-rj/EvidenceAuditTable.tsx`, `src/components/shield-rj/GraphVisualizer.tsx`, `src/app/dashboard/shield-rj/page.tsx`, `src/components/layout/Sidebar.tsx` (data bindings only), `src/app/api/land/enrich/route.ts`, `src/components/dashboard/DemoBadge.tsx` (new).
**Tasks:**
- Make every Shield-RJ figure consistent with Fazenda Buritis: 217,12 ha gross, 146,79 ha M1 net, 26,91 ha APP, 43,42 ha RL. The CPR value, sacas, truckloads and the area-inflation vector must all be derivable from those numbers, with plausible soy yields (~60–70 sc/ha).
- Replace Bayer, Syngenta and Corteva with fictional names.
- Rewrite the overclaiming copy (see ground rule 6).
- Remove the hardcoded "Hoje · 02:18".
- Derive Sidebar "Conformidade" and the per-parcel status badges from `compliance_*` fields instead of literals.
- Add a persistent "DADOS DE DEMONSTRAÇÃO" badge. It renders whenever the data comes from mocks or fixtures, driven by a single `isDemo` flag or env var.
- Have `/api/land/enrich` return `source: "live" | "fixture"`. The UI shows it, and the "Base Homologada" label must never appear on fixtures.

**Accept when:** no number on any screen contradicts another, and a reviewer can always tell demo data from live data.

### WS-B: App shell, navigation & theme (P1 shell/nav, P2 tokens)
**Owns:** `src/components/layout/Header.tsx`, `src/app/layout.tsx`, `src/app/globals.css`, `tailwind.config.ts`, `src/components/theme/*`, `src/lib/format.ts` (new), `src/app/dashboard/land/[id]/3d/page.tsx` (shell only), `src/app/dashboard/onboard/page.tsx` (shell and tokens only).
**Tasks:**
- Build one shared `<AppShell>` (Header + `<main>`) used by all four dashboard routes. Shield-RJ and 3D must stop rendering their own headers.
- Read the portal from the cookie, not `?portal=`.
- Point "Gêmeo 3D" at the internal `/dashboard/land/[selectedId]/3d` and remove the external Vercel URL. Unknown ids call `notFound()`.
- At 1024 px the header must not wrap: use short labels and icons, with tooltips.
- Mobile: add a hamburger or drawer nav below `md`. The dashboard uses a bottom-sheet sidebar over a full-height map.
- Merge the two token systems: point Tailwind colors at CSS vars (rgb channels) so every page honors light and dark. Fix the undefined `text-brand-lime` and `shadow-neon-lg` classes and the font mismatch (config says Space Grotesk, the layout loads Bricolage).
- Remove `select-none` from data containers.
- Hide the Next dev indicator (`devIndicators: false`).

**Accept when:** every route shares one header, theme and portal context; there is no horizontal scroll at 375 px; and nav is reachable on mobile.

### WS-C: Integrity, auth & error states (P0 #5–7, P1 states)
**Owns:** `src/middleware.ts`, `src/lib/supabase/*`, `src/app/login/page.tsx` (logic only), `src/app/api/**` (except enrich, which WS-A owns), `src/components/shield-rj/StrikeModal.tsx`, `src/components/map/MapView2D.tsx` (error states only), `src/components/map/CesiumViewer.tsx`, `.env.example`.
**Tasks:**
- Gate the demo cookie behind `NEXT_PUBLIC_DEMO_MODE=true`. Otherwise use real `supabase.auth.getUser()` in the middleware, and remove the `sb-*` substring shortcut.
- Add an auth guard to every `/api/*` handler.
- Logout calls `signOut()`.
- `/api/land/save` returns a non-2xx status when persistence fails. The UI shows an inline error.
- StrikeModal: rename the action to "Gerar minuta". Show a loading state and success only on `res.ok`, with an inline error otherwise.
- Replace every `alert()` with an inline banner component.
- Show a "Camada indisponível" chip when a WMS or tile fetch fails.
- Set `Cesium.Ion.defaultAccessToken` from env and serve Cesium workers locally (fixes the CORS error). Show a "Modelo 3D indisponível" notice on GLB failure.
- Configure or replace the basemap source that renders the "API KEY REQUIRED" watermark on the onboarding mini-map.
- Document every key in `.env.example`.

**Accept when:** no screen reports success for a failed operation; the console is clean on all routes (no CORS, no ion warning, no watermark tiles); and an unauthenticated `curl` to `/api/*` returns 401.

### WS-D: Accessibility pass (P1 a11y)
Runs **after** WS-A, WS-B and WS-C merge, so it touches every component without conflicts.
**Tasks:**
- Raise the minimum text size to 12 px. Replace `text-[8-11px]` with `text-xs` or larger; there are about 240 occurrences.
- Add `focus-visible:ring-2` globally.
- Add an `aria-label` to every icon-only button (grep for `<button` without text or label).
- Convert clickable divs to `<button>` ("Iniciar Varredura", Sidebar parcel cards).
- Link login and onboard labels to their inputs with `htmlFor`/`id`.
- Give modals `role="dialog"`, `aria-modal`, a focus trap and Esc to close.
- Contrast: use gray-300 or lighter on dark surfaces and slate-600 or darker on light ones.
- Shield-RJ: the "Ficha do Alvo" popover is closed by default.

**Accept when:** axe or Lighthouse accessibility scores ≥ 90 on all four routes, and the full onboarding flow can be completed by keyboard alone.

## Orchestrator checklist
1. Create the branch, commit the baseline, and create `HANDOFFS.md`.
2. Spawn WS-A, WS-B and WS-C in parallel, each with only its section plus the ground rules.
3. Merge WS-A, then WS-B, then WS-C, resolving handoffs between merges.
4. Spawn WS-D on the merged branch.
5. Final gate: run `tsc`, `build` and the E2E suite in `saas/tests/`. Walk the demo script at 1440 px and 375 px: login (B2B) → map → onboarding (Buritis) → Shield-RJ → 3D. Post one before/after screenshot set.
