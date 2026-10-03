# Contributing

## Workflow

1. Branch from `main`: `feat/<short-name>`, `fix/<KI-xx-short-name>` or `docs/<topic>`.
2. Make the change, with tests for any logic in `src/lib`.
3. Run the local gate:
   ```bash
   npm run typecheck && npm test && npm run build
   ```
4. Open a PR using the template. CI (`.github/workflows/ci.yml`) must pass, and one review from a CODEOWNER is required.
5. Squash-merge. The PR title becomes the commit message, so use Conventional Commits.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`.

- **Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`.
- **Scopes:** `m1`, `sar`, `dossier`, `registrorural`, `shield-rj`, `twin3d`, `map`, `auth`, `db`, `ui`, `deps`.
- Reference known issues in the body, e.g. `Fixes KI-11`.

## Code standards

- **TypeScript strict.** No new `any` without a comment explaining why.
- **Domain logic stays framework-free** in `src/lib`; React and Next stay in `src/app` and `src/components`.
- **Validate input** at every API boundary (Zod), and return `{ success: false, error }` with a correct HTTP status.
- **UI copy** follows the product rules in [`AGENTS.md`](AGENTS.md) §4: pt-BR, no overclaiming, demo data labelled.
- **Accessibility:** text ≥ 12 px, visible focus states, `aria-label` on icon buttons, and `role="dialog"` + focus trap on modals.
- **No new dependencies** without a short justification in the PR (bundle size matters: deck.gl and Cesium are already heavy).

## Documentation

- If behaviour, an API or a status changes, update the matching doc in the same PR.
- When you fix a known issue, move its row to "Fixed" in `docs/05-quality/KNOWN_ISSUES.md`.
- Structural decisions get an ADR (`docs/adr/`).

## Reviews

Reviewers check:
- correctness
- tests
- the demo-vs-real impact (does this change what a client could mistake for real?)
- security (auth, tenant, PII)
- docs
