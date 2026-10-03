# Moving this folder into its own GitHub repository

The folder `Agrostech Beta Saas/` is self-contained. It has its own `package.json`, lockfile, CI, docs and `.gitignore`, so it can become a standalone repository as-is. Full commit history stays in the source monorepo (`Amgadmj/agrostech`, path `saas/`, branch `fix/ux-audit-2026-10`). Commit-level history is summarized in [`CHANGELOG.md`](../../CHANGELOG.md) and [`docs/history/`](../history/).

## 1. Create the repository (private)

> The source monorepo is **public**. This repository contains demo data drawn from a real client survey and internal strategy documents, so create it **private**.

From a terminal, copy the folder somewhere outside the monorepo first so the new repo has a clean root:

```bash
cp -r "Agrostech Beta Saas" ~/code/agrostech-beta-saas
```

```bash
cd ~/code/agrostech-beta-saas
```

```bash
git init -b main && git add -A && git commit -m "chore: initial import of AgrosTech Beta SaaS from Amgadmj/agrostech@c5feb92"
```

```bash
gh repo create <org>/agrostech-beta-saas --private --source=. --push
```

Before the first commit, confirm that `git status` does **not** list `node_modules/`, `.next/`, `public/cesium/` or any `.env*` file other than `.env.example`.

## 2. Configure the repository

| Setting | Recommended value |
|---|---|
| Default branch | `main` |
| Branch protection on `main` | Require a PR, require 1 approval, require status check **CI / verify**, dismiss stale approvals, no force-push |
| Merge strategy | Squash merge only; delete branch on merge |
| CODEOWNERS | Edit [`.github/CODEOWNERS`](../../.github/CODEOWNERS) to the CTO's GitHub handle |
| Dependabot | Enabled by [`.github/dependabot.yml`](../../.github/dependabot.yml) (weekly npm + GitHub Actions) |
| Secret scanning + push protection | On |
| Actions secrets | None needed for CI today. Add deploy secrets only when a deploy workflow is added. |

## 3. Credentials to issue fresh (do not copy from the old repo)

| Secret | Where it goes | Notes |
|---|---|---|
| Supabase URL + anon key | Hosting env (Vercel) | New project per environment (dev / staging / prod) |
| Supabase service-role key | Hosting env, server only | Not used by the code yet |
| `REGISTRO_RURAL_API_KEY` | Hosting env | Billed per query; set a spending limit |
| `NEXT_PUBLIC_CESIUM_ION_TOKEN` | Hosting env | Restrict the token to the production domain in the ion dashboard |

Every variable is described in [`docs/04-operations/ENVIRONMENT.md`](../04-operations/ENVIRONMENT.md).

## 4. After the move

- In the old monorepo, replace `saas/` with a short README pointing to the new repo, or delete it, so two copies don't drift. **This is the founders' decision.**
- Update the data-room links (`data-room/09-product/*.md`) that point at `saas/` paths.
- Transfer or re-create any Vercel project that was linked to the old path.
