---
title: "Instalación BESS — NOM-001-SEDE-2012 Art. 480 & 690 Part H"
type: concept
tags: [bess, bateria, instalacion, nom, art-480, art-690, sae-cc, ventilacion]
created: 2026-06-05
updated: 2026-06-05
sources: [2026-06-05-nom-001-sede-2012]
---

# Instalación BESS — NOM-001-SEDE-2012 Art. 480 & 690 Part H

Technical installation requirements for stationary battery energy storage systems under Mexico's mandatory electrical code ([[2026-06-05-nom-001-sede-2012]]). Two articles apply:

- **Art. 480** — Baterías de Acumuladores: governs all stationary battery installations
- **Art. 690 Part H** (sections 690-71 through 690-74): additional rules when batteries are part of a solar PV system

These rules form the technical installation layer for [[sae-cc]], which is the CRE-defined regulatory modality for load-center battery storage. The battery products these rules govern are cataloged in [[bess]] (BYD MC Cube, Huawei LUNA2000, SigenStack), driven by [[hybrid-inverters]] or standalone PCS.

---

## Art. 480 — Baterías de Acumuladores

### Scope and definitions (480-1, 480-2)

Applies to **all stationary battery installations.** Key definitions:

- **Sistema de batería:** interconnected battery system including batteries, chargers, and may include inverters and converters
- **Tensión nominal de la batería:** based on number and type of cells
  - Lead-acid: 2V/cell → 48V = 24 cells
  - Alkaline (NiCd): 1.2V/cell
  - **Li-ion: 4V/cell** (explicitly listed)

### Conductor and equipment ratings (480-3)

All wiring and equipment connected to a battery system must comply with the same NOM requirements as for AC wiring at the equivalent voltage level.

### OCPD exceptions for low-voltage batteries (480-4)

No overcurrent protection required for conductors from a battery rated **<50V** when used for engine starting, ignition, or control of primary energy sources. Art. 300-3 (raceway fill rules) also does not apply to these conductors.

### Disconnect requirement (480-5)

**For stationary systems >50V:** a disconnect means must be provided for all ungrounded conductors. Must be:
- **Easily accessible**
- **Within sight** of the battery system

### Insulation by voltage tier

**480-6 — Systems ≤250V:**
- Ventilated lead-acid in non-conductive heat-resistant containers: no additional insulation support required
- Ventilated alkaline in non-conductive containers: max 20 cells (24V) in series on any single tray
- Rubber/composite containers: no insulation support if total series voltage ≤150V; groups of ≤150V required above that
- Sealed cells in non-conductive containers: no additional support required

**480-7 — Systems >250V:**
- Must split into groups ≤250V
- Insulation between groups (may be air): **minimum 5 cm clearance** between live parts of opposite polarity for systems ≤600V

### Enclosure and rack requirements (480-8)

- **Racks:** rigid frames of treated metal with non-conductive cell support, or non-conductive material (e.g., fiberglass)
- **Trays:** constructed/treated to resist electrolyte damage (wood or non-conductive material)

### Location (480-9)

- **Ventilation (480-9(a)):** sufficient ventilation and gas diffusion to prevent accumulation of explosive gas mixture — mandatory for all vented cell chemistries
- **Live parts (480-9(b)):** protected per Art. 110-27 (guarded or enclosed)
- **Workspace (480-9(c)):** work clearances per Art. 110-26, measured from battery rack edge

### Venting (480-10)

- **Vented cells:** must have pressure-relief vent, or be designed to prevent cell debris dispersal if a cell explodes from internal gas ignition
- **Sealed cells (VRLA, Li-ion):** must have pressure-relief valve preventing excess gas pressure buildup

**Note on room classification:** Battery rooms are explicitly excluded from several wiring methods throughout the NOM: FMC (348), LFMC (350), LFNC (356), FMT (360), ENT (362), and non-metallic surface raceways. This means battery rooms require rigid conduit systems.

---

## Art. 690 Part H — Batteries in PV Systems (690-71 to 690-74)

### General installation (690-71(a))

Batteries in PV systems must comply with **Art. 480** (above). Battery cells are considered grounded when the PV source circuit is installed per 690-41.

### Residential units (690-71(b))

For residential applications:
- Battery voltage must be **<50V nominal** (max 24 × 2V lead-acid cells = 48V)
- Exception: when live parts are not accessible during routine maintenance, the voltage may follow 690-7 limits
- Live parts must be guarded against accidental contact regardless of voltage or chemistry

### Current limiting (690-71(c))

If the battery bank's short-circuit current exceeds the interrupting rating of other circuit components, a **current-limiting device** (e.g., current-limiting fuses) must be installed adjacent to the batteries.

### Housing for lead-acid banks >48V (690-71(d))

Lead-acid vented banks with >24 cells in series (>48V) must **not** be installed in or with conductive enclosures. Conductive racks are permitted only if no rack material is within 15 cm of the top of non-conductive battery containers.

Exception: VRLA and other sealed battery types may use steel enclosures when required for proper function.

### Series disconnect for maintenance (690-71(e) and (f))

For banks >24 cells (>48V):
- Must have means to disconnect groups of ≤24 cells for maintenance
- No plug-type or no-load disconnects allowed
- A separate maintenance disconnect (accessible only to qualified persons) must allow disconnecting the grounded conductor within the PV battery circuit without affecting the rest of the PV system

### Batteries >48V: ungrounded operation conditions (690-71(g))

Systems with >24 cells in series may operate with ungrounded conductors if:
1. PV source/output circuits comply with 690-41
2. AC and DC load circuits are solidly grounded
3. All main battery input/output ungrounded conductors have disconnect + OCPD
4. Ground-fault detector/indicator installed to monitor the battery bank

### Charge control (690-72)

- **Charge control equipment required** (unless the PV circuit is designed so that charging current × 1 hour < 3% of battery Ah capacity, or manufacturer specifies otherwise)
- Diversion charge controllers must have a **second independent means** to prevent overcharge
- Grid-tied systems using the interactive inverter for charge control (by exporting excess to the grid) must have a second backup charge control means for grid-outage conditions

### Battery interconnections (690-74)

Flexible cables (per Art. 400) of **≥2/0 AWG** are permitted from battery terminals to nearby junction boxes within battery rooms. Fine-strand flexible cable must be terminated with compression terminals or listed connectors.

---

## Practical implications for SAE-CC design

| Requirement | Practical impact |
|---|---|
| Ventilation mandatory (480-9(a)) | Forced ventilation required for vented chemistries; Li-ion sealed BESS still needs pressure-relief per 480-10(b) |
| Disconnect >50V (480-5) | All commercial BESS (>50V) must have a dedicated accessible disconnect within sight |
| Rigid conduit in battery room (derived from exclusion list) | No FMC/LFNC/FMT allowed; add cost of conduit runs vs. flexible |
| 120V min clearance for >250V groups (480-7) | High-voltage BESS cabinets must maintain 5cm isolation between polarity groups |
| Battery room not accessible to unqualified persons (implied by 480-9(b)) | Commercial BESS requires restricted access — relevant to permit/insurance requirements |
| Certified equipment (705-4 cross-ref) | Inverters must be approved for interconnection; battery management systems not explicitly required to be listed but must meet voltage/wiring requirements |

---

## Related concepts

- [[instalacion-pv-interconectada]] — Art. 690 + 705: PV and grid interconnection installation rules
- [[sae-cc]] — CRE regulatory treatment of BESS at load centers; this page covers the NOM installation layer
- [[bess-savings-model]] — billing savings model; this page provides the physical installation constraints
- [[generacion-distribuida]] — solar DG regulatory framework

## How sources treat this

- [[2026-06-05-nom-001-sede-2012]]: Art. 480 (pp. 346/780) and Art. 690 Part H — 690-71 through 690-74 (pp. 600–602/780)
