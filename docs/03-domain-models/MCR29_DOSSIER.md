# MCR 2-9 Compliance Dossier & Passaporte de Crédito Rural

**Code:**
- `src/lib/dossier/generator.ts`: checks, hash, metadata
- `src/lib/dossier/pdfGenerator.ts`: dependency-free PDF-1.4 writer
- `src/lib/dossier/types.ts`

**API:** `POST /api/dossier/generate[?format=pdf]` (see [API_REFERENCE](../02-architecture/API_REFERENCE.md#post-apidossiergenerateformatpdf))
**Callers:** Shield-RJ `StrikeModal` (PDF export)

## Purpose

This is the deliverable a bank files. It states, for one property and one point in time, whether the operation passes the socio-environmental impediments of the Manual de Crédito Rural, section 2-9, as amended by Resolução CMN nº 5.267/2025 (interpretation to be validated by counsel, KI-37). It also states whether continuous remote-sensing monitoring is required.

## Checks performed

| Check | Pass condition |
|---|---|
| SICAR status | Status contains "Ativo" or is "Pendente" |
| IBAMA embargo | No embargo count and no embargo area |
| Indigenous land (TI) | No overlap |
| Conservation unit (UC) | No overlap |
| Slave-labour list | `hasSlaveLabor = false` (input flag only; no list lookup is integrated) |
| Net arable ratio | ≥ 15 % |
| Continuous monitoring | `gross > 300 ha` → mandatory |

The result is `mcr29Status`, `eligibilityStatus` (`ELIGIBLE` / `IMPEDED`) and `passaporteAgrostechIssued`.

## Integrity and signature

| Element | Real? | Notes |
|---|---|---|
| Canonical JSON payload | ✅ | Deterministic field order |
| SHA-256 checksum | ✅ | Also returned in the `X-Dossier-SHA256` header and printed in the PDF |
| `reportId` | ✅ | `crypto.randomUUID()` |
| PAdES-LTV signature | ❌ **placeholder** | Hardcoded certificate chain and placeholder CNPJ (KI-01) |
| RFC 3161 timestamp | ❌ **placeholder** | Base64 of a plain string, not a TSA token |
| PDF | ✅ valid PDF-1.4 | Text only, no signature dictionary, no fonts beyond the base set |

### Path to a legally valid signature

1. The company obtains an **ICP-Brasil e-CNPJ certificate** (A1 file or A3 token/HSM). Confirm the legal entity name first (open question in CTO_HANDOVER §7).
2. Generate the PDF with a real library (e.g. `pdf-lib`), then sign with **PAdES** (PKCS#7/CMS detached signature in a `/Sig` dictionary). Use a signing provider or a server-side signer with the key in an HSM or KMS; never in the web process.
3. Request an **RFC 3161 timestamp** from an ICP-Brasil-accredited ACT and embed it (PAdES-T). Add the validation material, OCSP/CRL (PAdES-LTV).
4. Verify the output with the ITI validator (verificador.iti.gov.br) as part of CI for a sample document.
5. Store issued dossiers (`dossiers` table + object storage), immutable, with their hash.

## Copy rules

- Do not print "CONCEDIDO". Use neutral outcomes such as "Elegível segundo os critérios verificados" or "Impedimento identificado".
- Every dossier must state its data sources and their timestamps, and whether each source was live or a fixture.

## Known issues

KI-01, KI-19 (the area formula is duplicated without a bound; reuse `calculateNetPlantableArea`), KI-22, KI-23 (the 14.8 ha default embargo area).
