# Strategy & Thesis Documents

These documents explain **why** the platform exists and what it is meant to become. They were written for investors and partners, so read them for intent. For engineering status, use [`../00-handover/CTO_HANDOVER.md`](../00-handover/CTO_HANDOVER.md).

| File | What it is |
|---|---|
| [`IP_MODELS_AND_3D_DIGITAL_TWIN_THESIS.md`](IP_MODELS_AND_3D_DIGITAL_TWIN_THESIS.md) | The core thesis (EN and pt-BR): the credit-risk hypothesis, CMN 5.267/2025, models M1/M2/M3, the 3D digital twin, the surveillance pyramid, the Buritis case and the moat. Converted to Markdown from the `.docx` for agent readability |
| [`AgrosTech_IP_Models_and_3D_Digital_Twin_Thesis.docx`](AgrosTech_IP_Models_and_3D_Digital_Twin_Thesis.docx) | The original formatted document (source of truth for layout) |
| [`generate_technology_thesis_docx.js`](generate_technology_thesis_docx.js) | The docx-js script that generated the `.docx` (from `data-room/scripts/` in the monorepo). It needs the `docx` npm package to run |
| [`data-room-product/`](data-room-product/) | The investor data-room product section: Product Overview, Roadmap, Tech Stack, Security, Demo Video Brief. **These predate the 2026-09-26 build**. Some statements are outdated (e.g. "enrich uses `setTimeout`"), and several items are marked [CONFIRM] |

⚠️ Thesis §8 ("Real-World Field Validation") mixes real survey figures with demo-scenario numbers. See KI-10 in [`KNOWN_ISSUES.md`](../05-quality/KNOWN_ISSUES.md).
