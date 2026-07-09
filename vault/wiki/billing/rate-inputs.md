---
title: "Rate Inputs — Time-Varying GDMTH Tariff Values"
type: concept
tags: [cfe, gdmth, tarifas, cuotas, rate-inputs]
created: 2026-06-04
updated: 2026-06-07
sources: [2026-06-04-acuerdo-a158-2024, 2026-06-07-cfe-bill-795150706028-mar26]
---

# Rate Inputs — Time-Varying GDMTH Tariff Values

> **Purpose:** Stores the current $/kWh and $/kW-mes values needed to compute a GDMTH bill. These are the **only inputs that change monthly**. All formulas, FC values, and period schedules are stable regulatory logic in the other billing pages. Update this file when CFE publishes new rates; do not touch the logic pages.

> **✓ Status:** **12 months of SIN rates now populated** (Abr 2025 – Mar 2026) from real bills — see the 12-month table below. Other divisions (BC, BCS, Norte…) still pending. The Acuerdo A/158/2024 defines the monthly update methodology (§3.4) but does not fix values; CFE SSB publishes final rates monthly within 5 business days before each month.

---

## How to find current rates

CFE publishes monthly GDMTH rates at:
- **CFE tariff page:** https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRENegocio/Tarifas/GranDemandaMTH.aspx (select month and region)
- **CRE Acuerdo:** Each month's rates are set via a CRE Órgano de Gobierno resolution notified to CFE SSB within 5 business days before the month starts (A/158/2024 art. OCTAVO)

---

## Rate structure

### Energy rates ($/kWh) — vary by period

These are the "cargo de generación energía" + transmisión components bundled into the published final rates per period.

| Rate | Description | Current value | Last updated |
|---|---|---|---|
| `r_punta` | Energy rate — punta period | **TBD** | — |
| `r_intermedio` | Energy rate — intermedio period | **TBD** | — |
| `r_base` | Energy rate — base period | **TBD** | — |

> **Note:** r_punta > r_intermedio > r_base always. The spread between punta and base is the key driver of energy savings from demand shifting and solar.

### Demand rates ($/kW-mes) — vary monthly

| Rate | Description | Current value | Last updated |
|---|---|---|---|
| `r_capacidad` | Cargo por Capacidad — punta-coincident demand | **TBD** | — |
| `r_distribucion` | Cargo por Distribución — monthly max demand | **TBD** | — |

> **Source:** These are the "Tarifas Reguladas para el Servicio Público de Distribución" (r_distribucion) and "cargo de generación capacidad" (r_capacidad) from A/158/2024.

### Flat per-kWh rates (stable)

| Rate | Description | Value | Source |
|---|---|---|---|
| `r_scnmem` | Servicios Conexos no MEM | **$0.0062/kWh** | A/158/2024 art. PRIMERO |
| `r_transmision` | Transmisión | TBD (set by A/154/2024) | Separate tariff resolution |
| `r_cenace` | Operación CENACE | TBD (set by A/157/2024) | Separate tariff resolution |

> **Note:** SCnMEM rate ($0.0062/kWh) is fixed for all of 2025 by art. PRIMERO of A/158/2024. Transmisión and CENACE rates are set by their own CRE resolutions (A/154/2024 and A/157/2024 respectively) and may change.

### Fixed monthly charge

| Rate | Description | Value | Source |
|---|---|---|---|
| `r_ssb` | Operación Suministrador Básico | TBD (per division/category) | A/156/2024 |

---

## How rates update

Under A/158/2024 §3.4, the generation cost components (which drive energy and capacity rates) are adjusted monthly using:

```
rate_month_t = rate_month_t-1 × (generation_cost_t / generation_cost_t-1)
```

The generation cost is itself computed from CLSB costs, MEM spot prices, SLP contract costs, and PSE costs. CRE verifies and approves monthly. This is why rates change every month and why this file exists separately from the logic pages.

---

## Rate relationship to savings calculations

These rates are used in:

| Page | Which rates needed |
|---|---|
| [[gdmth-bill-structure]] | All of the above |
| [[pv-savings-model]] | r_punta, r_intermedio, r_base (energy savings) |
| [[bess-savings-model]] | r_capacidad, r_distribucion (demand savings) |
| [[pv-bess-combined]] | All demand rates + energy rates |
| [[medicion-neta]] | r_punta, r_intermedio, r_base (credit values) |

---

## Actual rates — SIN division, March 2026

> **Source:** [[2026-06-07-cfe-bill-795150706028-mar26]] — derived by dividing MEM component totals by billed kW and kWh. Valid for SIN division (Campeche), billing period 28 Feb – 31 Mar 2026.

| Component | Value | Derived from |
|---|---|---|
| `r_punta` (Generación P) | **$2.128/kWh** | $1,904.47 / 895 kWh punta |
| `r_intermedio` (Generación I) | **$1.887/kWh** | $6,941.17 / 3,679 kWh inter |
| `r_base` (Generación B) | **$1.042/kWh** | $2,695.66 / 2,588 kWh base |
| `r_transmision` | **$0.180/kWh** | $1,289.88 / 7,162 kWh total |
| `r_cenace` | **$0.0076/kWh** | $54.43 / 7,162 kWh total |
| `r_scnmem` | $0.0069/kWh | $49.43 / 7,162 kWh (cf. regulated $0.0062 — minor discrepancy) |
| `r_capacidad` | **$392.66/kW-mes** | $4,711.92 / 12 kW |
| `r_distribucion` | **$91.87/kW-mes** | $1,102.44 / 12 kW |
| `r_ssb` (Cargo Fijo) | **$452.58/mes** | Direct from bill |

> **⚠ Caveats:** (1) Rates are SIN-division only. Other divisions (BC, BCS, Norte, etc.) have different values. (2) Rates change monthly — these are valid for March 2026 only. (3) Demand rates were derived from a 12 kW billed demand; verify against a higher-demand bill to confirm linearity.

---

## 12-month SIN rate history — derived from 12 CFE bills (780881200029)

> **Source:** [[2026-06-08-cfe-bills-780881200029-fy25-26]] — implied unit rates = MEM importe ÷ kWh (or ÷ billed kW), validated peso-exact against the PDFs. **SIN division.** Confirms rates move every month. Generation rates shown; add `r_transmision + r_cenace + r_scnmem` to get the bundled per-kWh energy rate.

| Mes | r_base (Gen B) | r_inter (Gen I) | r_punta (Gen P) | r_transmisión | r_cenace | r_scnmem | r_capacidad ($/kW) | r_distribución ($/kW) |
|---|---|---|---|---|---|---|---|---|
| ABR 25 | 1.3031 | 2.4642 | **3.6998** | 0.2211 | 0.0079 | 0.0076 | 426.27 | 93.30 |
| MAY 25 | 1.1202 | 2.0291 | 2.2885 | 0.1809 | 0.0065 | 0.0062 | 422.31 | 94.61 |
| JUN 25 | 1.1468 | 2.0773 | 2.3429 | 0.1809 | 0.0065 | 0.0062 | 432.34 | 94.61 |
| JUL 25 | 1.1640 | 2.1085 | 2.3780 | 0.1809 | 0.0065 | 0.0062 | 438.82 | 94.61 |
| AGO 25 | 1.1657 | 2.1114 | 2.3813 | 0.1809 | 0.0065 | 0.0062 | 439.43 | 94.61 |
| SEP 25 | 1.1550 | 2.0921 | 2.3595 | 0.1809 | 0.0106 | 0.0062 | 435.41 | 94.61 |
| OCT 25 | 1.1550 | 2.0921 | 2.3596 | 0.1809 | 0.0106 | 0.0062 | 451.81 | 106.01 |
| NOV 25 | 1.1203 | 2.0293 | 2.2887 | 0.1809 | 0.0106 | 0.0062 | 422.34 | 94.61 |
| DIC 25 | 1.0643 | 1.9279 | 2.1743 | 0.1809 | 0.0106 | 0.0062 | 401.23 | 94.61 |
| ENE 26 | 1.0404 | 1.8845 | 2.1254 | 0.1801 | 0.0076 | 0.0069 | 392.20 | 91.87 |
| FEB 26 | 1.0410 | 1.8856 | 2.1266 | 0.1801 | 0.0076 | 0.0069 | 392.43 | 91.87 |
| MAR 26 | 1.0416 | 1.8867 | 2.1279 | 0.1801 | 0.0076 | 0.0069 | 392.66 | 91.87 |

**Observations:**
- **Energy rates trend down** through the year (Gen P $3.70→$2.13; Gen B $1.30→$1.04) — summer 2025 was materially pricier than early 2026. The **ABR 25 punta rate ($3.70/kWh) is an outlier** ~55% above the rest; worth a second look against the bill.
- **Capacidad peaks in summer** ($439/kW Aug) and bottoms in winter ($392/kW Jan–Mar) — reinforces that summer peak-shaving is where BESS earns most.
- **OCT 25 distribución jumps to $106/kW** (vs ~$94 baseline) — a one-month spike worth verifying.
- These are the calculator-ready inputs for any SIN-division GDMTH bill in this window.

## Historical rate context (for sizing estimates — other divisions)

For non-SIN divisions without a real bill yet, use these order-of-magnitude estimates only:

| Component | Approximate range | Notes |
|---|---|---|
| r_punta | $2.00–$4.00/kWh | SIN March 2026: $2.13 |
| r_intermedio | $1.00–$2.00/kWh | SIN March 2026: $1.89 |
| r_base | $0.50–$1.50/kWh | SIN March 2026: $1.04 |
| r_capacidad | $200–$500/kW-mes | SIN March 2026: $392.66 |
| r_distribucion | $50–$150/kW-mes | SIN March 2026: $91.87 |
