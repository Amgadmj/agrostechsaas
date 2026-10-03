# Regulatory & Legal Context

> ⚠️ **Engineering summary, not legal advice.** These references are cited by the product, the thesis and the code. **None has been validated by counsel for this product** (KI-37). Before any client-facing statement, have a lawyer confirm each item: its current wording, effective date and how it applies.

| Reference | What the product assumes | Where it shows up |
|---|---|---|
| **Resolução CMN nº 5.267/2025** (amending MCR chapter 2, section 9) | Tightens socio-environmental impediments for rural credit; continuous remote-sensing monitoring for financed properties **> 300 ha**, as a responsibility the lender cannot delegate | `m1/calculator.ts` and `dossier/generator.ts` (`continuousMonitoringMandatory`), ScoreCard, thesis §2 |
| **Manual de Crédito Rural (MCR) 2-9** | Impediments: CAR status, IBAMA embargo, indigenous lands, conservation units, slave-labour list, etc. | Dossier checks, onboarding MCR 2-9 matrix |
| **Lei 12.651/2012** (Código Florestal), art. 4, 12, 15 | APP and Reserva Legal are not cultivable; RL may be computed inside APP (art. 15), so de-duplicate | Model M1 |
| **Lei 8.929/1994** (CPR) | Cédula de Produto Rural as the financed instrument and collateral | Product framing, Shield-RJ |
| **Lei 11.101/2005**, art. 49 §3º | Fiduciary agricultural guarantees are excluded from the judicial-recovery stay | Shield-RJ narrative |
| **STJ REsp 1.758.746/GO** | Precedent cited for grain as a fungible good subject to precautionary seizure | Shield-RJ, petition template |
| **CPC arts. 300 / 301** | Urgent precautionary relief (*tutela cautelar antecedente*) | `StrikeModal` petition draft |
| **ICP-Brasil DOC-ICP-15**, ETSI EN 319 142 (PAdES), RFC 3161 | Requirements for a legally valid electronic signature and timestamp on the dossier | `dossier/*`. **Not implemented** (KI-01) |
| **LGPD** (Lei 13.709/2018) | Personal data of producers, CPFs, partners and debtors in the Shield-RJ data sources | See [`SECURITY_MODEL.md`](../06-security/SECURITY_MODEL.md) |
| **ANAC / DECEA (SARPAS)** | Drone operations that produce the twin and ground truth | Operations, outside this codebase |

## Data-source terms to review

| Source | Concern |
|---|---|
| Registro Rural (commercial SICAR gateway) | Contract, per-query billing, permitted reuse of the demonstrativo in client reports |
| INPE Brazil Data Cube | Open data; check the attribution requirements |
| MapBiomas | CC-BY-SA style licence; attribution; endpoint availability (KI-28) |
| Esri World Imagery / Carto basemaps | Commercial-use terms (KI-32) |
| Cesium ion | Plan limits, attribution |
| Umbra / Airbus | Tasking contracts and the licence for imagery used as court evidence |
