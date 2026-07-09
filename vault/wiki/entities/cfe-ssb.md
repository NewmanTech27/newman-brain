---
title: "CFE SSB — Suministrador de Servicios Básicos"
type: entity
tags: [cfe, suministro-basico, ssb, gdmth, facturacion]
created: 2026-06-04
updated: 2026-06-04
sources: [2026-06-04-gdmth, 2026-06-04-dacg-sae-a113-2024, 2026-06-04-res142-2017-gen-dist]
---

# CFE SSB — CFE Suministrador de Servicios Básicos

**Type:** organization (CFE subsidiary / business unit)

The CFE subsidiary responsible for providing regulated retail electricity supply ("Suministro Básico") to end users. CFE SSB is the entity that contracts with commercial and industrial users, issues bills under tariffs like [[gdmth]], and is the counterparty for [[generador-exento|Generadores Exentos]] compensation contracts.

## Role in this wiki

CFE SSB is the direct commercial counterparty for all GDMTH users. It:
- Issues monthly bills applying [[gdmth]] billing rules
- Calculates energy by period (punta/intermedio/base) and demand charges
- Contracts the compensation model with Generadores Exentos under [[medicion-neta]] or other models
- Represents Generadores Exentos in the MEM (Mercado Eléctrico Mayorista) under the net metering / compensation contract
- Does not require a SAE-CC permit — no permit process goes through CFE SSB for behind-the-meter batteries

## Billing authority

CFE SSB applies the charges defined in Acuerdo A/158/2024 (currently a data gap — see [[2026-06-04-acuerdo-a158-2024]]). The billing components under [[gdmth]] include costs from multiple grid segments (transmission, distribution, CENACE operation, market services) but CFE SSB integrates them into a single invoice.

## Legal status under 2025 reform

Under the [[2026-06-04-ley-sector-electrico-2025|2025 Ley del Sector Eléctrico]], CFE is now restructured as an "empresa pública del Estado" with "empresas filiales." CFE SSB's continued structure and authority under the new law is a known open question — the first 20 pages of the new law cover CFE's governance but the Ley del Sector Eléctrico portions (which govern suministro básico) were not yet fully read.

## What sources say

- [[2026-06-04-gdmth]]: CFE SSB is named as the suministrador; charges include "Operación del Suministrador Básico"
- [[2026-06-04-dacg-sae-a113-2024]]: SAE-CC under SSB requires no permit; SSB handles all commercial acts for these users
- [[2026-06-04-res142-2017-gen-dist]]: CFE SSB is the counterparty for compensation contracts; calculates and pays net metering credits; 30-day payment terms for facturación neta
