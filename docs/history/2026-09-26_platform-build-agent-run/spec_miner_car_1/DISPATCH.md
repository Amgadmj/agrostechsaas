## 2026-09-26T14:39:30Z

<USER_REQUEST>
You are the CAR & SICAR Regulatory Spec Miner for the Agrostech SaaS MVP project.
Your Working Directory: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1
Project Directory: c:\Users\Razer\Desktop\Agrostech\saas
Authoritative User Request: c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md

You MUST read the authoritative request at c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\ORIGINAL_REQUEST.md before starting.

Your Mission:
1. Investigate and document all technical specifications for Requirement R1: Live Registro Rural CAR API Integration (Strict Production Mode).
2. Reference URL: https://docs.registrorural.com.br/reference/consultademonstrativodocar
   Endpoints: GET /v2/car/demonstrativo/{car}, /v2/r2c/situacao, /v2/r2c/restricoes.
3. Detail the authentication headers (REGISTRO_RURAL_API_KEY), request/response schemas, asynchronous polling logic (PENDING -> COMPLETE, retry delays, timeout handling), error states and diagnostic failure messages.
4. Detail the SICAR demonstrativo data model: property boundaries, conservation areas (APP, Reserva Legal), non-arable geometries, and the M1 Net Plantable Area (Área Útil Líquida) calculation formulas and boundary intersection logic.
5. Search docs / web / codebase for reference schemas and mock/live fixtures if available.
6. Write your detailed specification report to:
   c:\Users\Razer\Desktop\Agrostech\saas\.agents\teamwork\spec_miner_car_1\spec_report.md
   and write a self-contained handoff.md in your working directory.
7. Send a message to your parent with the summary and report path.
</USER_REQUEST>
