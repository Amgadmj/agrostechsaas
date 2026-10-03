# 0008. Separate the SaaS into its own repository

- **Status:** Accepted
- **Date:** 2026-10-03
- **Deciders:** CEO (request), engineering handover

## Context

The SaaS lived in `saas/` inside the company monorepo `Amgadmj/agrostech`. That monorepo also holds:

- the internal AI operating system (CrewAI agents, Telegram bot, CRM automations)
- marketing material
- the data room
- client folders

The monorepo is **public**. A new CTO and their AI agents are taking over the technical department.

## Decision

Move the SaaS, its R&D and its strategy documents into a dedicated **private** repository named "Agrostech Beta Saas". The company AI OS stays in the monorepo.

## Consequences

- The engineering team and its agents get a clean scope, with isolated CI, permissions and secrets.
- Commit history stays in the monorepo (branch `fix/ux-audit-2026-10`, commit `c5feb92`). The new repository starts from a single import commit.
- The `saas/` copy in the monorepo must be retired or replaced with a pointer, so the two copies don't drift.
