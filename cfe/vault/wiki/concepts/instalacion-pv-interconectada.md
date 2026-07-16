---
title: "Instalación PV Interconectada — NOM-001-SEDE-2012 Art. 690 & 705"
type: concept
tags: [pv, instalacion, interconexion, nom, art-690, art-705, inversor, anti-islanding]
created: 2026-06-05
updated: 2026-06-05
sources: [2026-06-05-nom-001-sede-2012]
---

# Instalación PV Interconectada — NOM-001-SEDE-2012 Art. 690 & 705

Technical installation requirements for grid-tied solar PV systems under Mexico's mandatory electrical code ([[2026-06-05-nom-001-sede-2012]]). Art. 690 governs the PV system itself; Art. 705 governs grid interconnection. Art. 690 explicitly cross-references Art. 705 (section 690-3): when a PV system operates in parallel with a primary source, sections 705-14, 705-16, 705-32, and 705-143 also apply.

> **Equipment:** the modules, inverters and protection this code governs are cataloged in [[pv-modules]], [[string-inverters]] / [[microinverters]] / [[hybrid-inverters]], and [[protection-bos]]. The on-roof labor-safety layer is [[2026-06-08-nom-009-stps-2011]]; the interconnection *process* is [[interconexion-cre]].

---

## Art. 690 — Sistemas Solares Fotovoltaicos

### Scope and key definitions (690-1, 690-2)

Applies to all PV electrical systems — circuits, inverters, controllers — whether standalone or grid-interactive, with or without battery storage.

Key defined terms:
- **Sistema interactivo:** PV system operating in parallel with the grid; battery storage within the PV system is NOT a separate generation source for this definition
- **Punto de acoplamiento común:** connection point with the grid — generally the load side of the utility meter
- **Circuito de salida del inversor:** conductors between inverter and the service equipment or other generation source

### Installation rules (690-4)

- PV system may supply a building in addition to any other power source
- DC source circuits and DC output circuits must be in **separate raceways** from AC feeders/branch circuits (unless separated by a physical partition)
- All conductors must be identified and grouped: by color code, tape, labeling, or other approved means
- Multiple-inverter systems (690-4(h)): allowed; each inverter must have a disconnecting directory at its disconnect, at each AC disconnect, and at the main service disconnect

### Maximum system voltage (690-7)

DC voltage = Σ open-circuit voltages of modules connected in series, corrected for lowest expected ambient temperature.

**Table 690-7 correction factors (crystalline silicon):**

| Temp (°C) | Factor |
|---|---|
| 4 to 0 | 1.10 |
| -1 to -5 | 1.12 |
| -6 to -10 | 1.14 |
| -11 to -15 | 1.18 |
| -16 to -20 | 1.20 |
| -21 to -25 | 1.21 |
| -26 to -30 | 1.23 |
| -31 to -35 | 1.25 |

For Mexico's central regions (SIN), temperatures rarely drop below 0°C, so the correction factor is typically 1.10 or less.

### Conductor sizing (690-8)

- **Max circuit current = Σ module short-circuit currents × 1.25** (for source circuits)
- **Conductor ampacity ≥ 125% of max circuit current** (before any derating)
- OCPD must carry ≥ 125% of max current; net result = conductors sized for 156% of Isc

### Ground-fault protection (690-5)

Grounded DC arrays must have ground-fault protection that detects, interrupts, and indicates a fault. Warning label required at the interactive inverter and on any associated battery bank.

### Disconnects (690-15)

Means must be provided to disconnect all equipment (inverters, batteries, charge controllers) from all phase conductors of all sources.

---

## Art. 705 — Fuentes de Generación Interconectadas

### Equipment approval (705-4)

Interactive inverters for grid-tied systems must be **approved and identified for interconnection service**. This effectively requires certified/listed equipment — field-assembled or uncertified inverters are not compliant.

### Qualified personnel (705-6)

Installation of sources operating in parallel with the primary source must be done **only by qualified persons.**

### Directory (705-10)

At each service equipment location and at each generation source, a permanent placard must list all energy sources on or in the building.

### Connection points (705-12)

Four permissible connection scenarios. The most common for commercial PV (interactive inverters):

**705-12(d) — Interactive inverter output, load side of service disconnect:**

The inverter output connects on the load side of the main service disconnect, into any distribution equipment. Requirements:

1. **Dedicated OCPD** for each generation source connection
2. **120% bus rule:** Σ(ratings of all OCPDs feeding the bus) ≤ 120% × bus ampacity
   - Example: 200A panel → max OCPD sum = 240A. If main breaker is 200A + PV breaker 40A = 240A ✓
   - Exception for storage systems: use 125% × inverter rated current instead of OCPD rating
3. **Ground-fault protection:** connection must be on the source side of GFP equipment
4. **Marking:** equipment must indicate presence of multiple sources
5. **Back-fed breakers** must be rated for back-feed and secured against re-movement (690-4(h))
6. **Inverter output connection** must be at the opposite (load) end of the busbar from the main feed, unless bus has capacity ≥ Σ all OCPD ratings

Warning label required at distribution equipment:  
*"PRECAUCIÓN — CONEXIÓN DE SALIDA DEL INVERSOR — NO REUBICAR ESTE DISPOSITIVO DE PROTECCIÓN CONTRA SOBRECORRIENTE"*

### Output characteristics (705-14)

Output of the generation source must be voltage, waveform, and frequency compatible with the grid. Certified interactive inverters automatically satisfy this via internal synchronization.

### Anti-islanding — loss of primary source (705-40)

**Critical rule:** Upon loss of the primary source (grid outage), ALL generation sources must **auto-disconnect** from all ungrounded conductors of the primary source and must NOT reconnect until the grid is restored.

**Exception:** A certified interactive inverter may instead **auto-cease output** (without physically disconnecting conductors) and may auto-reconnect once the grid is restored. This is how virtually all modern string and micro-inverters comply.

**Implication for BESS + PV:** If the system has off-grid capability (island mode), it must meet additional detection requirements to confirm grid loss vs. momentary dip before switching to island operation.

### Three-phase anti-islanding (705-42)

Three-phase generation sources must auto-disconnect if any one phase of the primary source opens. Does not apply to emergency or legally-required standby systems.

### Grounding (705-50)

Per Art. 250. Exception: DC systems connected via inverter directly to a grounded service may use alternative methods providing equivalent protection if equipment is approved for that use.

### Conductor sizing (705-60)

Same rule as Art. 690: **conductor ampacity ≥ 125% of max current**, OCPD ≥ 125% of max current.

---

## Key sizing constraint: the 120% rule

The **120% bus rule** is the single most important practical constraint from Art. 705 for PV sizing on existing commercial/industrial panels:

```
Σ(OCPD ratings on bus) ≤ 1.20 × bus ampacity

Alternatively expressed:
PV_OCPD ≤ (0.20 × bus_ampacity) + (bus_ampacity - load_OCPD_sum)
```

For most commercial buildings with a fully loaded 400A bus, the available capacity for PV without a panel upgrade is limited. This constraint may require upgrading the main panel, adding a dedicated subpanel, or connecting on the line side of the service disconnect instead (705-12(a)).

---

## Related concepts

- [[instalacion-bess]] — Art. 480 + 690 Part H: battery installation requirements
- [[pv-savings-model]] — billing savings model (the regulatory/tariff layer Art. 690/705 makes possible)
- [[bess-savings-model]] — BESS demand shaving model
- [[generacion-distribuida]] — the DG framework enabling permit-free grid-tied PV < 0.7 MW (2025; ≥0.7 MW → [[autoconsumo]])
- [[sae-cc]] — SAE-CC regulatory treatment; Art. 480 + 690-H govern how the battery itself is installed

## How sources treat this

- [[2026-06-05-nom-001-sede-2012]]: Art. 690 (pp. 587–606/780) and Art. 705 (pp. 627–631/780) — full technical requirements for PV installation and grid interconnection
