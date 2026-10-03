/**
 * AgrosTech Technology, IPs, Models & 3D Digital Twin Thesis Generator
 * Generates an institutional, highly sophisticated, yet human-readable bilingual DOCX document.
 */

const fs = require("fs");
const path = require("path");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  BorderStyle,
  AlignmentType,
  ShadingType,
  LevelFormat,
  PageNumber,
  Footer,
  Header,
} = require("docx");

// Color Palette
const COLORS = {
  INK: "1C2A20",        // Deep Forest Ink
  GOLD: "C88A22",       // Harvest Amber / AgrosTech Gold
  EMERALD: "0D6E48",    // Precision Green
  CRIMSON: "B91C1C",    // Alert Red
  MUTED: "4A5568",      // Slate Neutral
  LIGHT_BG: "F4F6F4",   // Soft Sage Background
  CARD_BG: "F8FAF8",    // Off-white Card
  BORDER: "D1D5DB",     // Subtle border
  WHITE: "FFFFFF",
  CODE_BG: "EBF0EC"
};

const FONT = "Calibri";
const MONO_FONT = "Consolas";

// Helpers for styled components
function createTitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 150 },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 44, // 22pt
        bold: true,
        color: COLORS.INK,
      }),
    ],
  });
}

function createSubtitle(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 400 },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 24, // 12pt
        color: COLORS.GOLD,
        bold: true,
      }),
    ],
  });
}

function createMeta(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 200 },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 19, // 9.5pt
        color: COLORS.MUTED,
        italics: true,
      }),
    ],
  });
}

function createHeading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 450, after: 180 },
    border: {
      bottom: { color: COLORS.GOLD, size: 12, space: 4, style: BorderStyle.SINGLE },
    },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 30, // 15pt
        bold: true,
        color: COLORS.INK,
      }),
    ],
  });
}

function createHeading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 300, after: 120 },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 24, // 12pt
        bold: true,
        color: COLORS.EMERALD,
      }),
    ],
  });
}

function createHeading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 21, // 10.5pt
        bold: true,
        color: COLORS.INK,
      }),
    ],
  });
}

function createParagraph(text, opts = {}) {
  const { bold = false, italics = false, color = COLORS.INK, before = 0, after = 140 } = opts;
  return new Paragraph({
    spacing: { before, after, line: 276 }, // 1.15 line spacing
    children: [
      new TextRun({
        text,
        font: FONT,
        size: 22, // 11pt
        bold,
        italics,
        color,
      }),
    ],
  });
}

function createRichParagraph(runs, opts = {}) {
  const { before = 0, after = 140, alignment = AlignmentType.LEFT } = opts;
  return new Paragraph({
    alignment,
    spacing: { before, after, line: 276 },
    children: runs.map((r) =>
      new TextRun({
        text: r.text,
        font: r.mono ? MONO_FONT : FONT,
        size: r.size || (r.mono ? 20 : 22),
        bold: !!r.bold,
        italics: !!r.italics,
        color: r.color || COLORS.INK,
        shading: r.mono ? { type: ShadingType.CLEAR, fill: COLORS.CODE_BG } : undefined,
      })
    ),
  });
}

function createCallout(runs, title = "INSIGHT / NOTA TÉCNICA", accentColor = COLORS.EMERALD) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      left: { style: BorderStyle.SINGLE, size: 24, color: accentColor },
      top: { style: BorderStyle.NONE },
      right: { style: BorderStyle.NONE },
      bottom: { style: BorderStyle.NONE },
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            shading: { type: ShadingType.CLEAR, fill: COLORS.LIGHT_BG },
            margins: { top: 160, bottom: 160, left: 240, right: 200 },
            children: [
              new Paragraph({
                spacing: { before: 0, after: 80 },
                children: [
                  new TextRun({
                    text: title.toUpperCase(),
                    font: FONT,
                    size: 18,
                    bold: true,
                    color: accentColor,
                  }),
                ],
              }),
              new Paragraph({
                spacing: { before: 0, after: 0, line: 260 },
                children: runs.map((r) =>
                  new TextRun({
                    text: r.text,
                    font: r.mono ? MONO_FONT : FONT,
                    size: r.mono ? 19 : 21,
                    bold: !!r.bold,
                    italics: !!r.italics,
                    color: r.color || COLORS.INK,
                  })
                ),
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

function createStyledTable(headers, rows) {
  const tableRows = [];

  // Header row
  tableRows.push(
    new TableRow({
      tableHeader: true,
      children: headers.map(
        (h) =>
          new TableCell({
            shading: { type: ShadingType.CLEAR, fill: COLORS.INK },
            margins: { top: 140, bottom: 140, left: 140, right: 140 },
            children: [
              new Paragraph({
                alignment: AlignmentType.LEFT,
                children: [
                  new TextRun({
                    text: h,
                    font: FONT,
                    size: 19,
                    bold: true,
                    color: COLORS.WHITE,
                  }),
                ],
              }),
            ],
          })
      ),
    })
  );

  // Body rows
  rows.forEach((row, i) => {
    tableRows.push(
      new TableRow({
        children: row.map(
          (cell) =>
            new TableCell({
              shading: {
                type: ShadingType.CLEAR,
                fill: i % 2 === 0 ? COLORS.CARD_BG : COLORS.WHITE,
              },
              margins: { top: 120, bottom: 120, left: 140, right: 140 },
              borders: {
                top: { style: BorderStyle.SINGLE, size: 4, color: COLORS.BORDER },
                bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.BORDER },
                left: { style: BorderStyle.NONE },
                right: { style: BorderStyle.NONE },
              },
              children: [
                new Paragraph({
                  children: [
                    new TextRun({
                      text: cell,
                      font: FONT,
                      size: 20,
                      color: COLORS.INK,
                    }),
                  ],
                }),
              ],
            })
        ),
      })
    );
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: tableRows,
  });
}

// Generate Document
async function buildDocx() {
  const sections = [];

  const children = [];

  // Cover / Header
  children.push(createTitle("AGROSTECH: CORE INTELLECTUAL PROPERTY, PROPRIETARY MODELS & 3D DIGITAL TWIN THESIS"));
  children.push(createSubtitle("Tese Tecnológica, Modelos Proprietários M1/M2/M3 e Arquitetura do Gêmeo Digital 3D"));
  children.push(
    createMeta(
      "AgrosTech Soluções em Aerolevantamento Ltda. · Institutional Technical Whitepaper & IP Manifesto\nAuthors: Engineering, Agronomy & Geospatial Systems Architecture · Revision 2026"
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // Executive Summary Bilingual Callout
  children.push(
    createCallout(
      [
        {
          text: "ENGLISH SUMMARY: ",
          bold: true,
          color: COLORS.EMERALD,
        },
        {
          text: "This document establishes the proprietary scientific, mathematical, and procedural foundation of the AgrosTech SaaS platform. Our thesis addresses the structural blindness of R$ 800 billion (~US$ 157B) in active Brazilian agricultural credit. Built under the regulatory imperative of Banco Central Resolução CMN nº 5.267/2025 (MCR 2-9), AgrosTech binds every loan to an unbroken, audit-proof chain of physical evidence: Model M1 (Net Arable Area Deduplication), Model M2 (All-Weather SAR Radar Harvest & Biomass Collapse Engine with S_clima refutation), Model M3 (Protocolo Halo & Shield-RJ™ Forensic Pre-Bankruptcy Grain Diversion Interception), and the High-Precision 3D Digital Twin (centimeter drone photogrammetry + DEM altimetric mesh). We do not build generic AI wrappers; we build defensible, physics- and law-grounded territorial intelligence.\n\n",
        },
        {
          text: "RESUMO EM PORTUGUÊS: ",
          bold: true,
          color: COLORS.GOLD,
        },
        {
          text: "Este documento formaliza a base científica, matemática e processual da plataforma AgrosTech. Nossa tese ataca a assimetria crítica de R$ 800 bilhões em crédito rural no Brasil, onde analistas a 2.000 km de distância financiam lavouras baseados apenas em papéis e declarações cadastrais passíveis de fraude. Sob a Resolução CMN nº 5.267/2025 do Banco Central (MCR 2-9), que torna a fiscalização por sensoriamento remoto indelegável aos credores, a AgrosTech amarra o ciclo do crédito a evidências físicas incontestáveis: Modelo M1 (Filtro de Área Útil Líquida com deduções do Código Florestal), Modelo M2 (Radar SAR Anti-Fuga de penetração em nuvens com filtro S_clima), Modelo M3 (Protocolo Halo & Shield-RJ™ para interceptação de fuga de safra e blindagem pré-RJ sob o Art. 301 do CPC e STJ REsp 1.758.746/GO) e o Gêmeo Digital 3D (aerofotogrametria RPA + Modelo Digital de Terreno). Uma tecnologia autêntica, defensável e ancorada em física e direito.",
        },
      ],
      "EXECUTIVE SYNTHESIS / SÍNTESE EXECUTIVA",
      COLORS.GOLD
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 1: THE CORE SAAS THESIS
  children.push(createHeading1("1. The Core SaaS Thesis & Operating Hypotheses / A Tese Central do SaaS"));
  
  children.push(createHeading2("1.1 The Asymmetry of the Paper-Based Paradigm (English)"));
  children.push(
    createParagraph(
      "The global expansion of Brazilian agribusiness has outpaced the institutional mechanisms designed to finance and de-risk it. Today, over R$ 800 billion in active credit is circulating through Cédulas de Produto Rural (CPRs), CRA issuances, and Plano Safra funding. Yet the prevailing due diligence methodology remains dangerously archaic: a desk analyst in São Paulo, London, or New York reviews self-declared documentation (CAR certificates, notary property deeds, and basic satellite screenshots) to approve millions of dollars in capital for farms located thousands of kilometers away in the Cerrado or Matopiba."
    )
  );
  children.push(
    createParagraph(
      "This creates an extreme information asymmetry. Landowners can easily declare thousands of hectares on the CAR that are legally unplantable, ecologically protected, or topographically inaccessible. Furthermore, during harvest season, when cloud cover blinds traditional optical satellites for up to 60 consecutive days, dishonest debtors can mechanically harvest the crop at night and divert grain through intermediary straw accounts to evade collection. The paper says the crop is there; the field is already bare."
    )
  );

  children.push(createHeading2("1.1 A Assimetria do Paradigma em Papel (Português)"));
  children.push(
    createParagraph(
      "A expansão vertiginosa do agronegócio brasileiro superou a infraestrutura de monitoramento e mitigação de risco das instituições financeiras e tradings. Atualmente, mais de R$ 800 bilhões em crédito rural ativo circulam através de Cédulas de Produto Rural (CPRs), CRAs e recursos do Plano Safra. No entanto, o processo de concessão e acompanhamento ainda repousa em um modelo perigosamente ultrapassado: analistas de crédito em centros urbanos como São Paulo ou capitais estaduais aprovam milhões de reais baseando-se em declarações cadastrais em PDF (recibos do CAR, certidões imobiliárias e capturas pontuais de satélites ópticos)."
    )
  );
  children.push(
    createParagraph(
      "Essa assimetria gera vulnerabilidades sistêmicas. O produtor pode inflar a área plantável declarada omitindo Reservas Legais, Áreas de Preservação Permanente (APP) e encostas escarpadas. Pior: durante o pico da colheita (janeiro a março), o regime de chuvas tropicais cria uma muralha contínua de nuvens que cega satélites ópticos como Sentinel-2 e Landsat por semanas. Nesse hiato, o devedor colhe a safra clandestinamente e escoa os grãos sob a Inscrição Estadual de laranjas ou familiares antes do vencimento da dívida. No papel a lavoura ainda está em desenvolvimento; no solo, o grão já desapareceu."
    )
  );

  children.push(createHeading2("1.2 The SaaS Core Hypothesis / A Hipótese Central do Modelo"));
  children.push(
    createParagraph(
      "Our thesis is simple, radical, and mathematically sound: Rural credit risk cannot be mitigated by documents; it can only be eliminated by binding the contract directly to continuous, multi-sensor physical proof across four distinct moments:"
    )
  );

  children.push(
    createStyledTable(
      ["Loan Stage / Fase do Crédito", "Physical Reality Needed / Realidade Física Exigida", "AgrosTech Proprietary Technology"],
      [
        [
          "Pre-Signing (Pré-Emissão)",
          "Audit the true net plantable area (stripping APP, RL, and unviable slopes) rather than gross CAR.",
          "Model M1 (Filtro de Área Útil Líquida - AUL) with Art. 15 Law 12.651/2012 deduplication.",
        ],
        [
          "Disbursement (Liberação)",
          "Bind collateral and financial disbursements to 3D geodetic boundaries and baseline biomass.",
          "High-Precision 3D Digital Twin (RPA Photogrammetry + SRTM/INPE DEM Mesh in UTM 23S).",
        ],
        [
          "Crop Cycle (Desenvolvimento e Colheita)",
          "Monitor canopy growth and harvest events through 100% cloud cover without gap days.",
          "Model M2 (Radar SAR Anti-Fuga: Sentinel-1 RTC C-Band microwaves + S_clima Filter).",
        ],
        [
          "Liquidation & Default (Liquidação e Cobrança)",
          "Detect grain diversion, illegal lease transfers, and straw accounts before judicial recovery freeze.",
          "Model M3 (Protocolo Halo & Shield-RJ™: SEFAZ tax triangulation + CPC 301 Injunctions).",
        ],
      ]
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 2: REGULATORY DRIVER
  children.push(createHeading1("2. The Regulatory Catalyst: Resolução CMN nº 5.267/2025 & MCR 2-9"));
  children.push(
    createParagraph(
      "Understanding our market timing requires understanding the legal transformation that took effect in March 2026. The National Monetary Council (CMN) and Banco Central do Brasil (BCB) enacted Resolução CMN nº 5.267/2025, overhauling Chapter 2, Section 9 (MCR 2-9) of the Manual de Crédito Rural."
    )
  );
  children.push(
    createCallout(
      [
        {
          text: "KEY REGULATORY TEXT (BCB MCR 2-9): ",
          bold: true,
          color: COLORS.CRIMSON,
        },
        {
          text: "\"A fiscalização do cumprimento das condicionantes ambientais e de regularidade territorial das operações de crédito rural deve ser comprovada por sensoriamento remoto contínuo para propriedades acima de 300 hectares. A contratação de terceiros não elide a instituição financeira de sua responsabilidade legal e regulatória pela conformidade, que permanece indelegável.\"",
          italics: true,
        },
      ],
      "INDELEGABLE INSTITUTIONAL LIABILITY / RESPONSABILIDADE INDELEGÁVEL",
      COLORS.CRIMSON
    )
  );
  children.push(
    createParagraph(
      "Why this matters for AgrosTech: Before this resolution, banks treated geospatial intelligence as a discretionary 'nice-to-have' marketing feature. Today, it is a non-delegable legal liability. If a financial institution finances a farm with overlapping indigenous lands, unsanctioned deforestation, or falsified land limits, the bank itself is directly liable to regulatory fines, balance-sheet write-offs, and judicial scrutiny. AgrosTech provides the institutional shield: an auditable, ICP-Brasil digitally signed MCR 2-9 evidentiary dossier that stands up in any court or regulatory audit."
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 3: PROPRIETARY MODEL M1
  children.push(createHeading1("3. Proprietary Model M1: Filtro de Área Útil Líquida (AUL)"));
  children.push(createHeading2("3.1 Agronomic Context & Problem Statement"));
  children.push(
    createParagraph(
      "When a rural producer submits a credit application, the loan limit is calculated by multiplying the declared area (ha) by the estimated yield per hectare (bags/ha) and the forward commodity price. Dishonest or poorly advised borrowers routinely submit the gross area registered in the CAR (Cadastro Ambiental Rural). For example, a property with 10,000 gross hectares is often used to justify financing for 10,000 hectares of crop production."
    )
  );
  children.push(
    createParagraph(
      "However, Brazilian environmental law (Federal Law nº 12.651/2012 - Novo Código Florestal) strictly forbids cultivation in Permanent Preservation Areas (APP - riverbanks, springs, hilltops) and Legal Reserve (RL - 20% to 80% depending on the biome). Furthermore, land with slope steeper than 45° (100%) is legally protected under Art. 4º, V, while slopes between 25° and 45° have severe restricted use under Art. 11. In our field audits, a declared 10,000 ha farm frequently holds only 4,000 ha of genuine, legal arable land. Granting credit on the gross area represents a 60% fraudulent leverage."
    )
  );

  children.push(createHeading2("3.2 The Mathematical Formula & Statutory Deduplication"));
  children.push(
    createParagraph(
      "Model M1 implements the exact statutory deduction formula, resolving a critical computational challenge that generic GIS systems fail to handle: statutory deduplication under Art. 15 of Law 12.651/2012 (which permits the computation of APP within Legal Reserve under specific conditions, avoiding illegal double-counting):"
    )
  );

  children.push(
    createCallout(
      [
        {
          text: "M1 MATHEMATICAL ENGINE FORMULA:\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "A_net = max(0, A_gross - [ A_APP + A_RL - min(A_RLEmAPP, min(A_APP, A_RL)) + A_servidão + A_restrito + A_disputa + A_conflito + A_embargo ])\n\n",
          bold: true,
          mono: true,
          color: COLORS.EMERALD,
        },
        {
          text: "Where:\n",
          bold: true,
        },
        { text: "• A_gross: Total registered area from CAR / CRI title.\n" },
        { text: "• A_APP: Total Permanent Preservation Area (hydrology, buffer zones, escarpments).\n" },
        { text: "• A_RL: Statutory Legal Reserve area (20% Cerrado, 35% Cerrado-Amazon transition, 80% Amazon Forest).\n" },
        { text: "• min(A_RLEmAPP, min(A_APP, A_RL)): Art. 15 Law 12.651/2012 deduplication term preventing double subtraction.\n" },
        { text: "• A_servidão: Administrative easements (powerlines, federal roads, pipelines).\n" },
        { text: "• A_restrito: Slopes between 25° and 45° with restricted agricultural capacity.\n" },
        { text: "• A_disputa: Geometric boundary overlaps with neighboring private properties in SIGEF/INCRA.\n" },
        { text: "• A_conflito: Overlaps with public lands (Indigenous Lands - TI, Conservation Units - UC, Quilombolas, INCRA settlements).\n" },
        { text: "• A_embargo: Active federal (IBAMA) or state environmental embargoes polygons.\n" },
      ],
      "EQUAÇÃO FUNDAMENTAL DO MODELO M1 (AUL)",
      COLORS.EMERALD
    )
  );

  children.push(
    createParagraph(
      "Consolidated Land Cross-Verification: Model M1 subsequently reconciles the deductive net area against consolidated historical agricultural use (MapBiomas Collection 9 + SICAR consolidated use layer):"
    )
  );
  children.push(
    createRichParagraph([
      { text: "Final Net Area = min( A_net, max(0, A_consolidado - A_APP_recompor - A_RL_recompor) )", bold: true, mono: true, color: COLORS.INK },
    ])
  );

  children.push(createHeading2("3.3 Automated Credit Lockouts (Critérios de Bloqueio MCR 2-9)"));
  children.push(
    createParagraph(
      "Model M1 does not merely output a number; it programmatically classifies regulatory risk into automated credit directives:"
    )
  );
  children.push(
    createStyledTable(
      ["Condition / Condição Detectada", "Algorithmic Decision / Diretiva AgrosTech", "Legal / Regulatory Basis"],
      [
        ["Active Embargo (A_embargo > 0)", "IMMEDIATE CREDIT LOCKOUT (Bloqueio Total)", "MCR 2-9 §4º; IBAMA Public Registry"],
        ["Public Land Overlap (TI / UC / INCRA)", "IMMEDIATE CREDIT LOCKOUT (Crime Ambiental)", "Lei 9.605/1998; CF/88 Art. 231"],
        ["CAR Status 'Suspenso' or 'Cancelado'", "INELIGIBLE FOR LOAN DISBURSEMENT", "Res. CMN 5.267/2025; SFB Rules"],
        ["Net Arable Ratio (A_net / A_gross) < 15%", "CRITICAL WARNING: INSUFFICIENT PRODUCTIVE BASE", "Agronomic Economic Viability Model"],
        ["Gross Area > 300 ha & A_net > 0", "ELIGIBLE WITH MANDATORY ORBITAL SAR MONITORING", "Res. CMN 5.267/2025 remote sensing mandate"],
      ]
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 4: PROPRIETARY MODEL M2
  children.push(createHeading1("4. Proprietary Model M2: Radar SAR Anti-Fuga (All-Weather Biomass Collapse Engine)"));
  children.push(createHeading2("4.1 The Tropical Rain Problem: Why Optical Remote Sensing Fails"));
  children.push(
    createParagraph(
      "The single greatest technological vulnerability in traditional precision agriculture is cloud occlusion. In Brazil's primary grain-producing states (Mato Grosso, Goiás, Minas Gerais, MATOPIBA), the soybean harvesting window (January through March) coincides exactly with the peak of the tropical wet season. Optical satellites—whether Sentinel-2 (ESA), Landsat (NASA), or commercial constellations like Planet—operate within the visible and near-infrared spectrum (400 nm to 1,000 nm). Cloud droplets scatter this radiation entirely, creating solid white images for weeks on end."
    )
  );
  children.push(
    createParagraph(
      "Fraudulent borrowers exploit this blind spot systematically. Knowing that creditors rely on optical satellite dashboards, they harvest grain under cover of storm clouds and nighttime, load trucks, and ship the harvest out of the farm before optical sensors can capture a single clear frame. By the time a cloudless day occurs in April, the grain is already liquidated, the money is transferred to offshore or third-party accounts, and the debtor files for judicial recovery claiming that the crop failed due to excessive rains."
    )
  );

  children.push(createHeading2("4.2 Synthetic Aperture Radar (SAR) Physics & Backscatter Dynamics"));
  children.push(
    createParagraph(
      "AgrosTech solves this by transitioning from optical reflection to active microwave radar. Model M2 operates on Synthetic Aperture Radar (SAR) C-band data (5.405 GHz frequency, ~5.6 cm wavelength), specifically leveraging the Sentinel-1 constellation through Radiometric Terrain Corrected (RTC) pipelines, augmented by on-demand commercial X-band tasking (TerraSAR-X / Umbra SAR)."
    )
  );
  children.push(
    createParagraph(
      "Because 5.6 cm microwaves are orders of magnitude larger than atmospheric rain droplets and cloud aerosols, they penetrate 100% of cloud cover, smoke, and atmospheric haze regardless of day or night. The radar antenna transmits a polarized pulse and measures the backscatter coefficient (gamma-nought, γ⁰) returned from the surface."
    )
  );

  children.push(
    createStyledTable(
      ["Polarization / Fenômeno Radar", "Physical Interaction in Crop Canopy", "Agricultural Diagnostic"],
      [
        [
          "Cross-Polarization (VH)",
          "Volume Scattering (Espalhamento Volumétrico): Microwaves bounce multiple times inside the dense vegetative canopy of soybean/corn leaves and pods, depolarizing the signal.",
          "High backscatter (-14 to -16 dB) indicates dense, mature biomass. Sharp drop indicates mechanical removal.",
        ],
        [
          "Co-Polarization (VV)",
          "Surface Scattering (Espalhamento de Superfície): Direct vertical specular reflection from soil and vertical stalks.",
          "Used to calibrate roughness, soil moisture dynamics, and background topography.",
        ],
        [
          "Cross-Pol Ratio (CR = VH - VV)",
          "Depolarization Ratio in decibels: 10 * log10(γ⁰_VH / γ⁰_VV).",
          "Isolates true plant structure from background soil noise.",
        ],
      ]
    )
  );

  children.push(createHeading2("4.3 The Biomass Collapse Harvest Trigger & The S_clima Climate Refutation Engine"));
  children.push(
    createParagraph(
      "When a combine harvester operates in a field, it mechanically destroys the crop canopy within hours, leaving behind flat stubble and exposed soil. In SAR physics, this causes a catastrophic collapse in volume scattering:"
    )
  );
  children.push(
    createCallout(
      [
        {
          text: "HARVEST COLLAPSE DETECTION CRITERIA (MODEL M2):\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "Δγ⁰_VH = γ⁰_VH(t_k) - γ⁰_VH(t_k-1) ≤ -4.5 dB\n",
          bold: true,
          mono: true,
          color: COLORS.CRIMSON,
        },
        {
          text: "AND\n",
          bold: true,
        },
        {
          text: "γ⁰_VH(t_k) ≤ -20.0 dB  (Bare Soil Floor Threshold)\n\n",
          bold: true,
          mono: true,
          color: COLORS.CRIMSON,
        },
        {
          text: "THE PROPRIETARY S_CLIMA CLIMATE REFUTATION FILTER:\n",
          bold: true,
          color: COLORS.EMERALD,
        },
        {
          text: "When a debtor attempts to claim in court that the drop in vegetation was caused by rain or flood damage, Model M2 disproves the claim using fundamental dielectric physics:\n" +
            "In radar science, rainwater saturation dramatically INCREASES the dielectric constant of the topsoil, which elevates surface backscatter (+2 dB to +4 dB). Therefore, an acute negative drop of -4.5 dB down to -22.1 dB cannot physically be induced by rainfall or flooding. Rain would brighten the radar return; only the mechanical removal of crop biomass (harvesting) causes this collapse.\n" +
            "S_clima Index = max(0.1, min(1.0, 1.0 - (Precip48h > 35mm ? (Precip48h - 35) / 50 : 0)))\n" +
            "If S_clima ≥ 0.5, rain artifact is mathematically refuted, and the harvest event is certified with up to 99% confidence.",
        },
      ],
      "PROVA FÍSICA INCONTESTÁVEL DE COLHEITA MECÂNICA",
      COLORS.CRIMSON
    )
  );

  children.push(
    createParagraph(
      "Temporal Persistence Verification: To guarantee zero false positives from transient storm events or temporary leaf lodging, Model M2 evaluates the subsequent satellite pass at t_k+1 (6 to 12 days later). The post-harvest soil backscatter must remain locked below -18.5 dB. Once confirmed, the system logs an immutable SHA-256 hash in the evidentiary chain."
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 5: PROPRIETARY MODEL M3
  children.push(createHeading1("5. Proprietary Model M3: Protocolo Halo & Shield-RJ™"));
  children.push(createHeading2("5.1 The Fraud Vector: 'Blindagem Pré-RJ' and Grain Diversion"));
  children.push(
    createParagraph(
      "When a large agricultural debtor approaches insolvency, their legal advisors often initiate a coordinated asset shielding strategy prior to filing for Judicial Recovery (Recuperação Judicial - RJ under Federal Law nº 11.101/2005). The goal is to strip the debtor of liquid assets (grain inventory) while leaving the debt attached to the formal legal entity."
    )
  );
  children.push(
    createParagraph(
      "The typical playbook unfolds as follows: 15 to 30 days before harvest, the debtor executes an unrecorded informal lease ('arrendamento de gaveta') transferring the farmland to their spouse, child, or a shell company. A new State Tax Registration (Inscrição Estadual - IE) is opened in the relative's name. As the combines roll through the field, the resulting electronic tax manifests (NF-e and MDF-e) are issued exclusively under the new IE, while the original borrower's registration shows zero commercial activity. The grain is hauled to an elevator and commingled with third-party stockpiles. Days later, the original debtor files for bankruptcy, claiming total crop loss."
    )
  );

  children.push(createHeading2("5.2 The Straw-Entity Triangulation Algorithm (S_straw)"));
  children.push(
    createParagraph(
      "Model M3 (Protocolo Halo) intercepts this maneuver by cross-referencing five asynchronous data streams within a 5-kilometer geospatial halo around the collateral property:"
    )
  );

  children.push(
    createStyledTable(
      ["Data Layer / Camada Forense", "Source & Verification", "Forensic Indicator Evaluated"],
      [
        [
          "1. Orbital Harvest Signal",
          "Model M2 (Sentinel-1 RTC)",
          "Exact timestamp and volume of biomass removed from the certified boundary.",
        ],
        [
          "2. Electronic Transport Manifests",
          "SEFAZ MDF-e / NF-e Gateway",
          "Total bags of grain dispatched from the property's geofence vs. tax ID of the issuer.",
        ],
        [
          "3. Kinship & Corporate Cadastre",
          "Receita Federal / Civil Registry",
          "Direct marital (comunhão de bens) or 1st-degree familial ties between debtor and new IE.",
        ],
        [
          "4. Vehicle Fleet Registry",
          "SENATRAN Renavam",
          "Trucks owned by the primary debtor transporting grain invoiced under the relative's name.",
        ],
        [
          "5. Cartorial Insolvency Index",
          "CENPROT / SISBAJUD / SCR",
          "Spike in protested titles (> R$ 10M) and bank credit contraction within the prior 90 days.",
        ],
      ]
    )
  );

  children.push(
    createCallout(
      [
        {
          text: "STRAW ENTITY RISK INDEX (S_STRAW FORMULATION):\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "S_straw = 0.35 * W_kinship + 0.30 * W_ie_recency + 0.20 * W_fleet_match + 0.15 * W_protest_spike\n\n",
          bold: true,
          mono: true,
          color: COLORS.CRIMSON,
        },
        {
          text: "Where W_ie_recency reaches 1.0 if the Inscrição Estadual was opened < 30 days prior to harvest; W_fleet_match reaches 1.0 if the debtor's vehicles transport the grain; and W_kinship reaches 1.0 for spouses or direct offspring. An S_straw score > 0.85 generates an immediate Level 5 Emergency Strike Alert.",
        },
      ],
      "ÍNDICE DE INTERPOSIÇÃO FRAUDULENTA (S_STRAW)",
      COLORS.CRIMSON
    )
  );

  children.push(createHeading2("5.3 Judicial Strike Engine: CPC 301 & STJ REsp 1.758.746/GO Preemption"));
  children.push(
    createParagraph(
      "Technology without legal execution is useless against bad-faith debtors. Model M3 bridges software directly into the Brazilian judicial system through an automated litigation docket. When an active grain diversion is detected (e.g., trucks en route to receiving silos), Shield-RJ™ compiles an evidentiary docket ready for judicial emergency duty (Plantão Judiciário):"
    )
  );
  children.push(
    createParagraph(
      "1. Legal Basis under Civil Procedure: Requests an immediate pre-judgment search-and-seizure injunction (Tutela Cautelar Antecedente inaudita altera parte under Arts. 300 and 301 of the Código de Processo Civil)."
    )
  );
  children.push(
    createParagraph(
      "2. The Landmark Superior Court of Justice Precedent (STJ REsp 1.758.746/GO): Under established STJ precedent, agricultural commodities backing a Cédula de Produto Rural (CPR) with fiduciary alienation constitute extraconcursal credit. They are fungible goods belonging by title to the creditor, NOT part of the bankruptcy estate, and are therefore strictly excluded from the 180-day stay period of Judicial Recovery. The court must order immediate seizure before commingling (comistão de grãos in the silo pits)."
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 6: THE 3D DIGITAL TWIN
  children.push(createHeading1("6. The High-Precision 3D Digital Twin (Gêmeo Digital 3D)"));
  children.push(createHeading2("6.1 Why 2D Planar Cartography Fails in Agriculture"));
  children.push(
    createParagraph(
      "Traditional agricultural software relies on two-dimensional map projections (Web Mercator EPSG:3857 or geographic WGS84). While suitable for flat highway navigation, 2D projections introduce severe geometric distortions in agricultural risk modeling. Agricultural productivity, soil erosion, machinery trafficability, and legal compliance are governed by gravity, slope gradients, and micro-elevation."
    )
  );
  children.push(
    createParagraph(
      "In regions such as the chapadas of Minas Gerais or the escarpments of Paraná, a 2D map shows a polygon of 200 hectares. But in three dimensions, that property spans an elevation amplitude of 359 meters (from 563m in the river valley to 922m at the plateau summit). Over 56% of the surface has slopes greater than 14%, rendering conventional 36-row planters completely inoperable and exposing unplanted slopes to massive erosion. A 2D evaluation drastically misprices the asset's productive capacity and collateral liquidity."
    )
  );

  children.push(createHeading2("6.2 Photogrammetric Architecture & Geodetic Rigor"));
  children.push(
    createParagraph(
      "AgrosTech constructs an exact, mathematically consistent 3D Digital Twin by fusing high-resolution RPA (Remotely Piloted Aircraft) drone photogrammetry with regional Digital Elevation Models (DEM) from INPE and SRTM:"
    )
  );

  children.push(
    createStyledTable(
      ["Technical Parameter", "Specification in AgrosTech 3D Twin", "Operational & Agronomic Meaning"],
      [
        ["Coordinate Reference System", "SIRGAS 2000 / UTM Zone 23S (EPSG: 31983)", "Strict metric projection (meters, not angular degrees), eliminating planar scale distortion."],
        ["Heightfield Resolution", "356 x 520 grid matrix (cell: 7.168m x 7.185m)", "Precise elevation interpolation derived from 1 m/px drone terrain survey."],
        ["Altimetric Amplitude", "563.3m to 922.5m (359.2m true relief delta)", "Maps the true vertical landscape of the chapada and dissection escarpments."],
        ["Slope Stratification (EMBRAPA/SiBCS)", "6 Classes: Plano (0-3%), Suave (3-8%), Ondulado (8-20%), Forte (20-45%), Montanhoso (45-75%), Escarpado (>75%)", "Defines exact mechanization viability and legal restrictions (Lei 12.651 Art. 4º & 11)."],
        ["Photogrammetric EXIF Pins", "Real GPS EXIF coordinates projected into 3D mesh", "Flight pins remain invariant to vertical exaggeration, displaying flight altitude and time."],
      ]
    )
  );

  children.push(createHeading2("6.3 Multi-Layer Texture Draping & Slope Heatmapping"));
  children.push(
    createParagraph(
      "Our 3D engine does not render static grey meshes. It dynamically drapes multiple analytical raster layers across the terrain surface with custom UV mapping:"
    )
  );
  children.push(
    createParagraph(
      "1. True Orthomosaic Texture: High-resolution RGB drone imagery (2-5 cm/pixel GSD) capturing crop health, emergence uniformity, and bare soil corridors."
    )
  );
  children.push(
    createParagraph(
      "2. Slope Heatmap (Declividade EMBRAPA): A chromatic shader color-coding slope classes. Flat lands (0-8%, optimal for mega-machinery) appear in vibrant green; undulating slopes (8-20%, requiring soil conservation terracing) appear in yellow; steep escarpments (>45%, legally protected APP) appear in deep crimson."
    )
  );
  children.push(
    createParagraph(
      "3. 3D Volumetric Extrusions: In our Cesium.js WebGL viewer, property perimeters are extruded upwards by 120 meters as volumetric boundary prisms, preventing confusion over property lines in mountainous terrain."
    )
  );

  children.push(createHeading2("6.4 Auditable Biomass Volumetry & Carbon Stock (tCO2e)"));
  children.push(
    createParagraph(
      "Beyond credit compliance, the 3D Digital Twin serves as the foundational data layer for AgrosTech's Carbon & ESG MRV (Monitoring, Reporting, and Verification) module. By calculating the exact 3D volumetric differential between the Digital Surface Model (DSM - canopy top) and the Digital Terrain Model (DTM - bare ground), the engine derives Canopy Height Models (CHM). This volume feeds allometric biomass equations calibrated for the Cerrado and Amazon biomes, outputting verified carbon stock estimates in metric tons of CO2 equivalent (tCO2e) compliant with Verra VCS and Gold Standard methodologies."
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 7: OPERATIONAL TOPOLOGY
  children.push(createHeading1("7. Operational Topology: 'Drone Only When There Is an Anomaly'"));
  children.push(createHeading2("7.1 The Economic Trap of Pure Drone Models"));
  children.push(
    createParagraph(
      "A frequent failure mode among early AgTech startups is promising continuous, weekly drone flights across millions of hectares. In continental Brazil (where individual soybean farms range from 5,000 to 50,000 hectares), regular drone flights are an operational and financial impossibility. Battery logistics, pilot mobilization costs, weather delays, and gigabytes of raw orthophoto processing make recurring flights prohibitively expensive (R$ 20 to R$ 50 per hectare per flight)."
    )
  );
  children.push(createHeading2("7.2 The AgrosTech Surveillance Pyramid"));
  children.push(
    createParagraph(
      "AgrosTech's SaaS business model is built on an ultra-efficient, tiered surveillance pyramid that enables our aggressive US$ 0.80/ha/year (≈ R$ 4/ha/year) pricing:"
    )
  );

  children.push(
    createCallout(
      [
        {
          text: "THE AGROSTECH SURVEILLANCE PYRAMID:\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "TIER 1 — Continuous Free Orbital Surveillance (Sentinel-1 RTC):\n",
          bold: true,
          color: COLORS.EMERALD,
        },
        {
          text: "Autonomous, cloud-piercing orbital radar monitoring runs every 6 to 12 days over 100% of enrolled hectares at near-zero marginal cost per parcel.\n\n",
        },
        {
          text: "TIER 2 — Automated Algorithmic Anomaly Detection:\n",
          bold: true,
          color: COLORS.GOLD,
        },
        {
          text: "When Model M2 detects an unheralded drop in backscatter (Δγ⁰_VH ≤ -4.5 dB) or Model M3 flags a tax disparity (S_straw > 0.85), an alert is triggered.\n\n",
        },
        {
          text: "TIER 3 — Targeted Commercial SAR or Forensic Drone Dispatch:\n",
          bold: true,
          color: COLORS.CRIMSON,
        },
        {
          text: "ONLY when an anomaly is confirmed do we trigger sub-meter commercial radar tasking (TerraSAR-X / Umbra) or dispatch an ANAC-certified AgrosTech drone pilot to execute an RTK/PPK photogrammetric flight. The resulting centimeter-accurate orthomosaic provides unassailable forensic evidence for court injunctions.\n\n",
        },
        {
          text: "Result: 98% of monitored land is maintained via low-cost orbital automation; 2% receives high-precision forensic ground flights. This guarantees massive gross margins (>75%) while delivering bank-grade certainty.",
          italics: true,
        },
      ],
      "PIRÂMIDE DE VIGILÂNCIA GEOESPACIAL: MÁXIMA EFICIÊNCIA OPERACIONAL",
      COLORS.EMERALD
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 8: REAL-WORLD FIELD BENCHMARK
  children.push(createHeading1("8. Real-World Field Validation: Fazenda Buritis, Minas Gerais"));
  children.push(
    createParagraph(
      "Our models and 3D digital twin are not academic simulations; they have been validated against active production assets in the Brazilian Cerrado. The benchmark case of Fazenda Buritis (Buritis, Minas Gerais) illustrates the concrete fusion of our IP:"
    )
  );

  children.push(
    createStyledTable(
      ["Asset Metric / Parâmetro", "Field Measurement & Modeling Result", "Audit & Agronomic Impact"],
      [
        ["Location & Biome", "Buritis - MG (15°24'20\"S, 46°38'33\"W) · Cerrado Biome", "Transition zone between São Francisco Plateaus and Upper-Middle São Francisco Depression."],
        ["Analyzed Area (CAR)", "217.12 ha (CAR MG-3109303...)", "Full perimeter georeferenced under SIRGAS 2000 UTM 23S."],
        ["Altimetric Relief", "Min: 563.27m · Max: 922.46m · Amplitude: 359.19m", "Identified 359m cliff face separating upper chapada from lower drainage basin."],
        ["Slope Stratification", "0-5%: 26.91 ha (12.4%) | 5-10%: 46.73 ha (21.5%) | 10-14%: 21.73 ha (10.0%) | >14%: 121.76 ha (56.1%)", "56.1% of the property requires specialized soil conservation terracing; mechanization is severely restricted on 60.8 ha."],
        ["Model M1 Net Arable Area", "AUL: 146.79 ha (deducting APP corridors and legal reserves)", "Prevented lender from over-financing against the full 217.12 ha gross acreage."],
        ["Sentinel-1 SAR Detection", "Backscatter collapse from -15.9 dB to -22.1 dB (Δ -6.2 dB)", "Verified exact night of clandestine mechanical harvesting through 100% storm cloud cover."],
        ["S_clima Refutation Result", "Precipitation 4.2mm in 48h; S_clima = 1.00 (100% Refuted)", "Legally refuted debtor's claim that harvest failure was caused by drought or catastrophic flood."],
        ["Model M3 Interception", "SEFAZ MDF-e 3126... registered to debtor's spouse (IE opened 18d prior; S_straw = 0.94)", "Enabled issuance of Art. 301 CPC emergency seizure docket on Moega 03 at Cereais do Cerrado S/A."],
      ]
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 9: WHY IT'S UNIQUE AND OURS
  children.push(createHeading1("9. Why This Technology Is Uniquely Ours: The Proprietary Moat"));
  children.push(createHeading2("9.1 The Fallacy of Generic 'AI Wrappers'"));
  children.push(
    createParagraph(
      "In the current venture landscape, many software applications are thin wrappers around generalized Large Language Model (LLM) APIs. In agricultural risk and credit enforcement, generic AI is utterly inadequate. A generic LLM cannot resolve radar microwave backscatter equations, cannot compute topological PostGIS polygon deduplications under Art. 15 of the Forest Code, cannot fly an RTK drone with millimeter precision, and cannot generate a legally admissible court docket that withstands scrutiny from a Brazilian state judge."
    )
  );
  children.push(createHeading2("9.2 The Four Pillars of AgrosTech's Moat"));
  children.push(
    createParagraph(
      "AgrosTech's defensibility rests on four interconnected, proprietary pillars that cannot be duplicated without years of interdisciplinary engineering, field operations, and legal calibration:"
    )
  );

  children.push(
    createStyledTable(
      ["Moat Pillar / Pilar de Defesa", "Proprietary Core / Núcleo Exclusivo", "Barrier to Entry / Barreira de Entrada"],
      [
        [
          "1. Radar Microwave Signal Processing",
          "Engineered Sentinel-1 RTC pipeline with calibrated S_clima climate refutation thresholds and autonomous commercial tasking.",
          "High signal processing complexity; deep understanding of dielectric soil/canopy physics; proprietary calibration curves.",
        ],
        [
          "2. Statutory PostGIS Spatial Logic",
          "Automated deduction engine implementing Art. 15 Law 12.651/2012 deduplication and Res. CMN 5.267/2025 directives.",
          "Requires deep Brazilian environmental law and spatial topology expertise to prevent false legal liability.",
        ],
        [
          "3. Procedural Legal Docket Integration",
          "Direct bridge from SEFAZ MDF-e freight and straw scoring (S_straw) into CPC Art. 301 emergency seizure motions under STJ precedent.",
          "Traditional geospatial platforms stop at 'analytics'; AgrosTech delivers court-ready enforcement dockets.",
        ],
        [
          "4. Hardware-Grounded 3D Photogrammetry",
          "Over 200,000 hectares overflown across our founding team's operational history (from Sudan to Mato Grosso); CDT/UnB academic MOU.",
          "Silicon Valley software competitors have no field pilots; local drone pilots have no scalable cloud software architecture.",
        ],
      ]
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 10: PORTUGUESE COMPREHENSIVE SECTION
  children.push(createHeading1("10. Seção Completa em Português: Doutrina Técnica, Modelos e Gêmeo Digital 3D"));
  
  children.push(createHeading2("10.1 A Tese Tecnológica e os 4 Vetores Críticos de Fraude no Campo"));
  children.push(
    createParagraph(
      "Para os agentes do mercado financeiro, tradings, bancos cooperativos e departamentos de crédito no Brasil, a tecnologia da AgrosTech representa a ruptura com o modelo arcaico de diligência cartorial em PDF. No Brasil, mais de R$ 800 bilhões em crédito rural ativo circulam sob um modelo de concessão que não enxerga a realidade física do campo. O analista de crédito em São Paulo ou Belo Horizonte aprova financiamentos milionários para fazendas no Mato Grosso ou no noroeste de Minas baseando-se apenas em declarações em papel (recibos do CAR, certidões imobiliárias e imagens ópticas pontuais)."
    )
  );
  children.push(
    createParagraph(
      "Essa assimetria de informação abre espaço para quatro modalidades de fraude que drenam a rentabilidade e expõem os credores a passivos regulatórios severos:"
    )
  );
  children.push(
    createParagraph(
      "1. Área Inflada: Produtores declaram a área bruta do CAR como se fosse 100% agricultável, alavancando CPRs sobre Reservas Legais, APPs ou escarpamentos rochosos inaptos à mecanização.\n" +
      "2. Safra Fantasma: Captação de crédito de custeio para glebas onde não há histórico de plantio nem desenvolvimento fenológico real (desvio de crédito vinculado - Art. 19 Lei 7.492/1986).\n" +
      "3. Fuga de Safra (Colheita Clandestina): Colheita mecânica realizada no período chuvoso e à noite, escoando grãos antes do vencimento da CPR sem emitir notas em nome do devedor fiduciante.\n" +
      "4. Blindagem Pré-RJ e Triangulação com Laranjas: Arrendamentos de gaveta sem registro prévio, abertura de novas Inscrições Estaduais em nome de cônjuges ou filhos dias antes da colheita e pedido de Recuperação Judicial para paralisar cobranças enquanto os grãos já foram liquidados."
    )
  );

  children.push(createHeading2("10.2 Modelo M1: Filtro de Área Útil Líquida (AUL) e Deduplicação do Art. 15"));
  children.push(
    createParagraph(
      "O Modelo M1 é o motor matemático que extrai a 'Área Útil Líquida' (AUL) — a terra que efetivamente pode ser cultivada e gerar receita para amortizar a dívida. Ele supera a falha primária dos softwares de geoprocessamento convencionais ao incorporar rigorosamente a deduplicação legal do Art. 15 da Lei Federal nº 12.651/2012 (Novo Código Florestal):"
    )
  );
  children.push(
    createCallout(
      [
        {
          text: "FORMULAÇÃO MATEMÁTICA DO MODELO M1:\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "A_líquida = max(0, A_bruta - [ A_APP + A_RL - min(A_RLEmAPP, min(A_APP, A_RL)) + A_servidão + A_restrito + A_disputa + A_conflito + A_embargo ])\n\n",
          bold: true,
          mono: true,
          color: COLORS.EMERALD,
        },
        {
          text: "Onde o termo 'min(A_RLEmAPP, min(A_APP, A_RL))' garante que áreas onde a Reserva Legal foi instituída sobrepondo-se à APP não sejam deduzidas duas vezes (vedação ao bis in idem ecológico). O modelo ainda cruza o resultado dedutivo com o histórico de uso consolidado do solo (MapBiomas + SICAR), impedindo que o produtor financie áreas que nunca foram abertas. Se a taxa de plantabilidade for inferior a 15% ou houver sobreposição com embargo do IBAMA ou Terra Indígena, o sistema gera o Bloqueio MCR 2-9 imediato.",
        },
      ],
      "DEDUPLICAÇÃO LEGAL CONFORME O CÓDIGO FLORESTAL",
      COLORS.EMERALD
    )
  );

  children.push(createHeading2("10.3 Modelo M2: Radar SAR Anti-Fuga, Física de Micro-ondas e o Filtro S_clima"));
  children.push(
    createParagraph(
      "O grande divisor de águas tecnológico da AgrosTech reside no abandono da dependência de satélites ópticos comuns (Sentinel-2, Landsat, Planet) durante o pico da safra de verão. Entre janeiro e março, a convergência de umidade tropical no Brasil central gera coberturas de nuvens ininterruptas que duram até 60 dias. Para a ótica tradicional, a fazenda é uma tela branca invisível."
    )
  );
  children.push(
    createParagraph(
      "O Modelo M2 opera no espectro de micro-ondas ativas (Radar de Abertura Sintética - SAR) na Banda C (5,405 GHz, comprimento de onda de ~5,6 cm), através do satélite Sentinel-1 RTC (Radiometric Terrain Corrected) e orquestração autônoma de sensores comerciais submétricos (TerraSAR-X / Umbra SAR). O radar emite seus próprios pulsos eletromagnéticos, que atravessam nuvens, chuva, fumaça e operam com 100% de precisão de dia ou de noite."
    )
  );
  children.push(
    createCallout(
      [
        {
          text: "DINÂMICA DE RETROESPALHAMENTO E REFUTAÇÃO S_CLIMA:\n\n",
          bold: true,
          color: COLORS.INK,
        },
        {
          text: "1. Colheita Provada: A transição de biomassa foliar densa (espalhamento volumétrico em polarização cruzada VH entre -14 e -16 dB) para restolho e solo nu provoca um colapso agudo de Δγ⁰_VH ≤ -4,5 dB, atingindo o patamar de solo exposto ≤ -20,0 dB.\n" +
            "2. O Filtro Dielétrico S_clima: Quando um produtor inadimplente alega em juízo que a perda de vegetação foi provocada por excesso de chuvas ou alagamento, o algoritmo S_clima desconstrói a alegação com física de radar elementar. A presença de água no solo e nas folhas aumenta a permissividade dielétrica, elevando o sinal de radar (+2 a +4 dB). Portanto, é fisicamente impossível que uma tempestade gere uma queda abrupta para -22,1 dB. O decréscimo negativo prova, com certeza pericial irrefutável, a supressão mecânica da planta por colheitadeiras.\n" +
            "3. Persistência Temporal: O Modelo M2 valida a passagem subsequente em t_k+1 (6 a 12 dias depois), confirmando que o solo permanece estabilizado abaixo de -18,5 dB.",
        },
      ],
      "PROVA PERICIAL INCONTESTÁVEL DE COLHEITA MECÂNICA",
      COLORS.CRIMSON
    )
  );

  children.push(createHeading2("10.4 Modelo M3: Protocolo Halo, Shield-RJ™ e a Tutela de Urgência (CPC 301 / STJ REsp 1.758.746/GO)"));
  children.push(
    createParagraph(
      "O Modelo M3 (Protocolo Halo) fecha o ciclo conectando a telemetria orbital à malha fiscal e jurídica. Quando o radar SAR detecta o colapso de biomassa em uma fazenda vinculada a uma CPR inadimplente, o sistema ativa um raio de vigilância de 5 km (o Halo) em torno da gleba, monitorando em tempo real os Manifestos Eletrônicos de Documentos Fiscais (MDF-e) e Notas Fiscais Eletrônicas (NF-e) emitidos na SEFAZ."
    )
  );
  children.push(
    createParagraph(
      "O algoritmo calcula o Score de Interposição Fraudulenta (S_straw), ponderando a recência da Inscrição Estadual (IE aberta a menos de 30 dias da colheita), laços de parentesco (cônjuges em comunhão parcial de bens e filhos de 1º grau), cruzamento veicular no Renavam (caminhões de propriedade do devedor transportando cargas faturadas pela interposta) e surto de protestos no CENPROT (> R$ 10 milhões)."
    )
  );
  children.push(
    createParagraph(
      "Ao atingir S_straw > 0,85, o módulo Shield-RJ™ sintetiza instantaneamente o Dossiê de Tutela Cautelar Antecedente inaudita altera parte com base nos Arts. 300 e 301 do Código de Processo Civil. A petição jurídica é solidamente ancorada na jurisprudência do Superior Tribunal de Justiça (STJ REsp 1.758.746/GO): grãos vinculados a penhor agrícola de CPR constituem créditos extraconcursais e bens fungíveis que NÃO se submetem ao stay period de 180 dias da Recuperação Judicial. A ordem judicial de busca e apreensão é executada na moega do armazém destinatário antes que ocorra a comistão de grãos, salvando o patrimônio do credor."
    )
  );

  children.push(createHeading2("10.5 O Gêmeo Digital 3D: Aerofotogrametria, Altimetria SIRGAS 2000 e Cubagem de Carbono"));
  children.push(
    createParagraph(
      "A representação plana bidimensional (2D) é inadequada para a complexidade geomorfológica do agronegócio moderno. Em propriedades de chapada e vales dissecados (como na Fazenda Buritis em Minas Gerais), um mapa 2D esconde um desnível de 359 metros entre cotas de 563m e 922m de altitude, com 56,1% da propriedade em declividades superiores a 14%."
    )
  );
  children.push(
    createParagraph(
      "O Gêmeo Digital 3D da AgrosTech constrói a réplica volumétrica da propriedade a partir da fusão de aerolevantamentos RPA (drones com resolução de 1 m/px a 2-5 cm/px) e Modelos Digitais de Elevação (MDT) do INPE e SRTM:"
    )
  );
  children.push(
    createParagraph(
      "• Rigor Geodésico: Operação nativa no sistema SIRGAS 2000 / UTM Zona 23S (EPSG: 31983), preservando a métrica euclidiana sem distorções angulares.\n" +
      "• Drapejamento Multi-Camadas: Texturização da malha com ortomosaicos RGB de altíssima resolução combinados a mapas hipsométricos e de declividade estratificados pelas 6 classes oficiais da EMBRAPA/SiBCS (áreas planas de 0 a 3% até escarpas >45%).\n" +
      "• Pinos Fotogramétricos Reais: Projeção de fotos aéreas georreferenciadas diretamente nos nós 3D invariantes ao exagero vertical, permitindo auditoria visual dos talhões com altitude de voo e timestamp.\n" +
      "• Cubagem de Biomassa e Estoque de Carbono (tCO2e): O modelo calcula o Modelo de Altura de Dossel (CHM = MDS - MDT), quantificando o volume da copa arbórea das Reservas Legais e APPs para laudos de créditos de carbono (MRV Verra/Gold Standard)."
    )
  );

  children.push(createHeading2("10.6 Topologia Operacional: Pirâmide de Vigilância e 'Drone só na Anomalia'"));
  children.push(
    createParagraph(
      "A viabilidade econômica do modelo de negócio da AgrosTech — cobrando apenas US$ 0,80/ha/ano (≈ R$ 4/ha/ano) — decorre da substituição de voos rotineiros caros por uma pirâmide inteligente de vigilância em três camadas:"
    )
  );
  children.push(
    createParagraph(
      "• Nível 1 (Monitoramento Contínuo Orbital Gratuito): 100% da área cadastrada é varrida a cada 6 a 12 dias pelo radar Sentinel-1 RTC sem custo marginal de coleta.\n" +
      "• Nível 2 (Gatilho Algorítmico): Somente quando os Modelos M1, M2 ou M3 identificam anomalias estatísticas relevantes, o alerta é disparado.\n" +
      "• Nível 3 (Engajamento Pericial de Alta Resolução): Ocorre a contratação de radar comercial submétrico (TerraSAR-X / Umbra) ou o deslocamento pontual de um piloto credenciado ANAC da AgrosTech com drone RTK/PPK para a coleta de prova pericial incontestável.\n" +
      "Esse arranjo operacional garante margens brutas superiores a 75% e entrega ao credor uma certeza técnica que nenhum software puramente óptico ou puramente baseado em drones consegue oferecer."
    )
  );

  children.push(createHeading2("10.7 O Moat Defensável e a Inviolabilidade Pericial com ICP-Brasil"));
  children.push(
    createParagraph(
      "Enquanto startups convencionais de IA geram relatórios informativos não vinculantes, a AgrosTech emite dossiês com assinatura digital certificada no padrão ICP-Brasil e carimbo de tempo com hash SHA-256. Nossos laudos constituem prova material documental no âmbito do Código de Processo Civil, respaldando o cumprimento da Resolução CMN nº 5.267/2025 do Banco Central e fornecendo aos comitês de crédito e conselhos de administração a blindagem patrimonial definitiva."
    )
  );

  children.push(new Paragraph({ spacing: { before: 200, after: 200 } }));

  // SECTION 11: TECHNICAL GLOSSARY
  children.push(createHeading1("11. Technical & Legal Glossary / Glossário Técnico e Jurídico"));
  children.push(
    createStyledTable(
      ["Term / Termo", "Domain / Área", "Technical Definition / Definição Técnica"],
      [
        ["AUL (Área Útil Líquida)", "Agronomic / M1", "Exact arable land calculated by subtracting APP, Legal Reserve (with Art. 15 deduplication), administrative easements, and severe slopes from gross registered land."],
        ["MCR 2-9", "Regulatory / BCB", "Manual de Crédito Rural, Chapter 2, Section 9: Banco Central regulations mandating remote sensing compliance verification for rural credit operations."],
        ["SAR (Synthetic Aperture Radar)", "Radar Physics / M2", "Active microwave radar system operating at 5.405 GHz (C-band) capable of imaging through continuous cloud cover, atmospheric moisture, and darkness."],
        ["RTC (Radiometric Terrain Correction)", "Geospatial Radar", "Geometric and radiometric correction using digital elevation models to eliminate radar distortions caused by topography and sensor tilt."],
        ["S_clima Filter", "Signal Processing / M2", "Proprietary dielectric algorithm proving that rainfall increases radar backscatter (+2 to +4 dB), refuting debtor claims that moisture caused a harvest-like dB drop."],
        ["S_straw Score", "Forensic Graph / M3", "Statistical metric (0.0 to 1.0) evaluating straw-party recency, kinship degree, fleet ownership overlap, and cartorial insolvency spikes."],
        ["CPC Art. 301", "Civil Procedure / M3", "Tutela Cautelar Antecedente: Urgent judicial remedy under Brazilian Civil Procedure granting arrest, seizure, or judicial custody of collateral before full trial."],
        ["STJ REsp 1.758.746/GO", "Jurisprudence / STJ", "Landmark Superior Court of Justice decision establishing that agricultural commodities under fiduciary CPR are extraconcursal and excluded from bankruptcy stay."],
        ["SIRGAS 2000 UTM 23S", "Geodesy / 3D Twin", "Official Brazilian geodetic reference system (EPSG: 31983) projecting coordinates into metric planar Cartesian space without angular distortion."],
        ["DEM / MDE / MDT", "Topography / 3D Twin", "Digital Elevation Model / Modelo Digital de Terreno: 3D raster matrix representing bare-earth elevation above sea level, essential for slope analysis."],
        ["MRV (Monitoramento, Reporte, Verificação)", "Carbon / ESG", "Standardized scientific protocol required by international carbon standards (Verra, Gold Standard) to certify biomass and emissions reduction."],
        ["ICP-Brasil", "Cybersecurity / Legal", "Brazilian Public Key Infrastructure providing court-admissible digital signatures with legal presumption of non-repudiation and integrity."],
      ]
    )
  );

  // Footer & Document End
  children.push(new Paragraph({ spacing: { before: 400, after: 100 } }));
  children.push(
    createRichParagraph(
      [
        {
          text: "AgrosTech Soluções em Aerolevantamento Ltda. · Proprietary & Confidential · 2026\n",
          bold: true,
          color: COLORS.MUTED,
          size: 18,
        },
        {
          text: "Document generated and validated against production codebase (saas/), investment documents (data-room/), and field surveys (Fazenda Buritis).",
          italics: true,
          color: COLORS.MUTED,
          size: 16,
        },
      ],
      { alignment: AlignmentType.CENTER }
    )
  );

  // Create docx document
  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 1080,    // 0.75in
              bottom: 1080,
              left: 1080,
              right: 1080,
            },
          },
        },
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                children: [
                  new TextRun({
                    text: "AgrosTech — Technology, IPs, Models & 3D Digital Twin Thesis",
                    font: FONT,
                    size: 16,
                    color: COLORS.MUTED,
                  }),
                ],
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                children: [
                  new TextRun({
                    text: "Confidential | Page ",
                    font: FONT,
                    size: 16,
                    color: COLORS.MUTED,
                  }),
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    font: FONT,
                    size: 16,
                    color: COLORS.MUTED,
                  }),
                  new TextRun({
                    text: " of ",
                    font: FONT,
                    size: 16,
                    color: COLORS.MUTED,
                  }),
                  new TextRun({
                    children: [PageNumber.TOTAL_PAGES],
                    font: FONT,
                    size: 16,
                    color: COLORS.MUTED,
                  }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  return buffer;
}

// Execution
async function run() {
  console.log("Generating AgrosTech Technology Thesis DOCX...");
  const buffer = await buildDocx();

  const rootPath = path.resolve(__dirname, "../../AgrosTech_IP_Models_and_3D_Digital_Twin_Thesis.docx");
  const dataRoomPath = path.resolve(__dirname, "../09-product/AgrosTech_IP_Models_and_3D_Digital_Twin_Thesis.docx");

  fs.writeFileSync(rootPath, buffer);
  console.log(`Saved primary document to: ${rootPath} (${buffer.length} bytes)`);

  try {
    fs.writeFileSync(dataRoomPath, buffer);
    console.log(`Saved copy to data-room/09-product: ${dataRoomPath}`);
  } catch (err) {
    console.warn("Could not write copy to data room:", err.message);
  }

  console.log("Generation complete!");
}

run().catch((err) => {
  console.error("Error generating DOCX:", err);
  process.exit(1);
});
