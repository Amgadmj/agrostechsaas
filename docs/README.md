# Documentation Index

**Start here:** [`00-handover/CTO_HANDOVER.md`](00-handover/CTO_HANDOVER.md)

| Folder | Read it when you need to… |
|---|---|
| [`00-handover/`](00-handover/) | Get oriented: what is real vs demo, top risks, the 30/60/90 plan, and how to create the new repo |
| [`01-product/`](01-product/) | Understand the product, users, demo script and regulatory context |
| [`02-architecture/`](02-architecture/) | Change code: the system map, APIs, data model and 3D digital twin |
| [`03-domain-models/`](03-domain-models/) | Touch the models: M1 net area, M2 SAR harvest engine, Shield-RJ, MCR 2-9 dossier |
| [`04-operations/`](04-operations/) | Run it locally, configure environments, deploy |
| [`05-quality/`](05-quality/) | Test it, or check the **known-issues register** before starting work |
| [`06-security/`](06-security/) | Handle auth, tenants, secrets or personal data (LGPD) |
| [`adr/`](adr/) | Understand or change a structural decision |
| [`strategy/`](strategy/) | Read the IP / 3D-twin thesis and the investor-facing product docs |
| [`history/`](history/) | Trace how the code was built: agent-run records, the original spec, the UX audit |
| [`ROADMAP.md`](ROADMAP.md) · [`GLOSSARY.md`](GLOSSARY.md) | Sequencing and vocabulary |

Related: [`../research/`](../research/) holds the R&D whitepapers and Python benchmarks.

## Documentation conventions

- Docs are in English for the engineering team. Product and UI terms stay in pt-BR, with the [glossary](GLOSSARY.md) for translations.
- Status statements carry a date. When code and docs disagree, **the code wins**: fix the doc in the same PR.
- Every known defect has a `KI-xx` id in [`KNOWN_ISSUES.md`](05-quality/KNOWN_ISSUES.md). Reference the id in PRs and commit messages.
