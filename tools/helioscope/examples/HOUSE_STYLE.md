# HOUSE_STYLE — HelioScope design rules

Status: **v1 (2026-07-11)** — distilled from the 30-project training library
(Drive: `Helios Training` → curated folder, `INDEX.md` + `_design_specs.tsv`),
cross-checked against 12 layout renders (yaqui, grupo-frisa, alberta-calgary,
tmex, hotel-yori-inn, casino-solaz, africam, anahuac-queretaro, kotobukiya,
frutos, ocesa, pinnacle). Supersedes the v0 seed; §10 lists what v0 got wrong.
The library's `notes.md` rationale sections are still blank — rules marked
**(why?)** have an open question in §11.

Citations are library slugs (`examples/2026-<slug>/` on Drive).

## 1. Module & orientation

- **Every one of the 30 designs uses the Tongwei 715 W module** — including the
  ones with blank metadata (arithmetic check: grupo-frisa 7,001,280 W / 9,792
  mods = 715.0; same for casa-santiago, centro-joyero, yaqui, alberta-calgary,
  tmex). Default it; deviations need a reason.
- Orientation follows racking: **flush → landscape** ("horizontal"),
  **tilt rack & carport → portrait** ("vertical"). Holds across the whole TSV;
  the few flush-portrait segments are pitched roof sections
  (hotel-tesoro-manzanillo, casino-solaz-delicias, productores-pecuarios-petatlan).

## 2. DC:AC sizing

- Observed 1.07–1.30, mean 1.24, **median/target ≈ 1.25**.
- Mechanics: the roof/parcel sets DC; AC is then assembled from discrete
  inverter steps just under DC/1.25. The spread is mostly inverter granularity:
  - **High end 1.28–1.30** = low-tilt flush carpets where one more inverter
    would overshoot (up-fitness 1.30 = 103.7/80, casino-solaz 1.30,
    oreilly 1.29, molex 1.29, petatlan 1.29, both hotels 1.28).
  - **Large fleets converge to 1.21–1.25** because N×100 kW steps are fine
    enough (kuehne-nagel 1.24, leche-19-hermanos 1.25, ocesa 1.22,
    grupo-frisa 1.23, tmex 1.21).
  - **Low outliers** casa-santiago 1.07 and tiendas-3b-7664 1.14 are small
    Growatt sites (10/15 kW units — the step is huge at that scale);
    frutos-de-huerta-real 1.14 looks deliberate **(why?)**.

## 3. Racking & tilt by surface

- **Flat/low-slope commercial-industrial roof (20/30 designs): flush carpet.**
  Modules laid parallel to the deck at its native pitch — the 2–5° "tilt" in
  the specs *is the roof slope*, not added tilt (up-fitness 2°, tiendas-3b 3°,
  kotobukiya 3°, conservas 3°, leche 3°, kuehne 4°, equialum 4°,
  hotel-yori-inn 5°). Landscape, 0.025 m module gap, packed dense.
- **10° tilt racks** appear in two places:
  - on roofs when the designer wants them **(why? — ballast/yield trade
    unstated)**: anahuac-queretaro (whole campus, 0.6–1.6 m spacing),
    foro-sol (1.2 m), and single rack segments beside flush carpets
    (alfa-montes, oreilly, smart-plastics, molex).
  - on classic ground-mount: tmex-industrial-park (10 MW, 180° south, 1.6 m),
    alberta-calgary (1 MW, 180°, 2.2 m — cold/high-latitude site gets the
    widest spacing in the library).
  - frutos-de-huerta-real is the only 15° (ground rows at 2.2 m).
- **Ground-mount has a second, denser style**: low-tilt (3–4°) tables in
  opposing-azimuth pairs 180° apart — grupo-frisa (7 MW at 67°/247° on graded
  land), and the same signature at ocesa-hipodromo (134°/314°) and yaqui
  (90°/270°). Don't assume "ground-mount = south-facing racks"; at MW scale
  the house default is the dense E-W-style carpet.
- **Carport** when parking is the resource: long canopies at 3–4° portrait
  following the aisle azimuth, zero setback, zero keepouts
  (pinnacle-aerospace, africam-safari).

## 4. Azimuth

- Flush arrays **inherit the building's axis** — nothing is forced to south
  (hotel-yori-inn 89–359.5°, conservas 41–224°, casino-solaz 47–229°).
- Only tilt racks aim near-south (alberta 180°, tmex 180°, foro-sol 188°;
  anahuac-queretaro 215° follows its buildings).
- Opposing 180°-apart azimuth pairs are the standard way to carpet a
  duo-pitch roof or a big flat area (ocesa, grupo-frisa, yaqui).

## 5. Row spacing & walkways

- **Flush: 0.025 m** between rows (touching carpet) — universal.
- Maintenance access is drawn as explicit corridors, not row spacing: orange
  walkway strips every few module columns (kotobukiya), white gaps splitting
  banks every 2–3 rows (hotel-yori-inn), dashed walkway lines every ~4–5 rows
  (yaqui). Exact cadence/width unstated **(why?)**.
- **Roof tilt racks: 0.6–1.6 m** (anahuac-queretaro 0.6/1.2/1.6, foro-sol 1.2,
  molex 1.3, anahuac-veracruz 1.2–1.3).
- **Ground racks: 1.6–2.2 m** (tmex 1.6; alberta and frutos 2.2).

## 6. Setbacks

- **Default ≈ 0.5 m from parapet** (0.4–0.6 band: kotobukiya 0.4,
  conservas 0.4/0.5, smart-plastics 0.4, hotel-yori-inn 0.5,
  centro-joyero 0.5, equialum 0.6, up-fitness 0.6, oreilly 0.6, molex 0.6).
  This confirms the v0 "2 px at z19 ≈ 0.5 m" tracing buffer.
- Tight small roofs go down to 0.2–0.3 m (calimax 0.3, casa-santiago 0.2–0.5,
  casino-solaz 0.2–0.8).
- **≥ ~1 MW scales up to 1 m** (kuehne, ocesa, alberta, tmex, yaqui edges,
  anahuac-queretaro) **(why? — fire corridor / norm unstated)**.
- Carports: 0 m (pinnacle, africam).

## 7. Keepouts & shade objects

- **27/30 designs place zero keepout polygons** — the house method is to
  *shape the segment around* big obstructions, not to carve holes.
- Explicit keepouts only where equipment is scattered *inside* the field:
  casino-solaz-delicias 34 (heavy rooftop kit; also models neighboring trees
  as 3D spheres for shade), calimax-californias 8, casa-santiago 3.
  Kotobukiya's render shows the light version: small orange dots on roof
  penetrations plus walkway strips, but 0 formal keepouts.
- Model adjacent trees whenever they can shade the array (casino-solaz).

## 8. Inverter selection

Huawei SUN2000 string family, **480 V default**:

| AC need | Choice | Citations |
|---|---|---|
| ≤ ~15 kW | Growatt (MID 8/10KTL3-XL, 15000TL3-S) | alfa-montes, casa-santiago, tiendas-3b-7664 |
| ~30 kW | one SUN2000-30KTL-M3 | oreilly-autopartes |
| 40–180 kW | 1–4× SUN2000-40KTL-M3 | calimax, up-fitness, anahuac-veracruz, pinnacle |
| 140–900 kW | mix 100KTL-M2 + 40KTL-M3 to top up to target AC | casino-solaz, tiendas-3b-cedis, hotel-yori-inn, conservas, kotobukiya, molex, petatlan |
| ≥ ~400 kW round | pure 100KTL-M2 fleets | equialum 4×, alberta 8×, kuehne 17×, leche 20×, ocesa 41×, grupo-frisa 57×, tmex 83× |

- The 40KTL is the "make-up" unit that lands DC:AC on ~1.25.
- 380/400 V only when the site's LV dictates it (petatlan 100KTL-M1 380/400,
  casino-solaz 400 V). One 60KTL-M0 exists (hotel-tesoro) — legacy, not a
  pattern.

## 9. Segment placement

- **One field segment per roof plane / azimuth / tilt combination.** Segment
  count tracks roof complexity, not size: kuehne-nagel is 2.1 MW in 1 segment
  (one clean warehouse), hotel-tesoro-manzanillo is 0.49 MW in 33 (resort
  slabs and wings); universities/casinos run 9–11 across campus buildings.
- Fill the best (largest, cleanest) roof completely before spilling to
  secondary buildings (hotel-yori-inn covers three buildings in order of
  size; anahuac-queretaro takes two long halls then a third small roof).
- No usable roof → carport over the parking lot (pinnacle-aerospace,
  africam-safari).
- New-build sites are designed over the architect's CAD/blueprint underlay
  instead of satellite imagery (yaqui — plant drawing, PV placed on the
  planned roof).
- Inverters sit at array edges next to their segments (AC/DC markers in every
  render); big ground plants distribute them through the field
  (grupo-frisa, tmex).
- casa-santiago is **layout-only** (never simulated — no report/hourly);
  use it for geometry precedent only.

## 10. Corrections vs the v0 seed

- v0 said flat roofs get "10° ballasted rows facing south". **Wrong for the
  library**: the dominant pattern is a flush 2–5° carpet following the roof,
  azimuth inherited from the building (§3, §4). 10° south racks are the
  exception (2 roofs + classic ground-mounts).
- v0's 0.5 m edge buffer is **confirmed** (§6).
- v0's packing heuristic (0.75 clear-plane / 0.17 kWp/m²) not re-derivable
  from the TSV alone — needs roof areas; keep provisional.
- Still valid from v0 (wiki-scope, not layout-scope): verify building before
  tracing; digitize in roof-pixel space, export true; Solar-API `--layers`
  for equipment/shade; obstacles get their own polygons in the client KML;
  size PV+BESS by NPV sweep, 0.7 MW is a regulatory step not a cap; report
  style per curvas.newman.re.

## 11. Open rationale questions (for the expert — answers feed notes.md)

1. **DC:AC**: is 1.25 the explicit target? What drove frutos-de-huerta-real
   to 1.14 (interconnection limit? contracted demand?)?
2. **Flush vs 10° rack on a flat roof**: what tips the choice
   (anahuac-queretaro/foro-sol went rack; kotobukiya/kuehne went flush)?
   Ballast weight, wind, winter yield, cost?
3. **Ground-mount style**: when dense low-tilt opposing rows (grupo-frisa)
   vs spaced 10° south racks (tmex)? Land-constrained vs yield-per-module?
   Is alberta's 2.2 m a snow/latitude rule?
4. **Setbacks**: is 0.5 m the codified parapet setback? What triggers the
   1 m at MW scale — fire corridor, insurer, CFE norm?
5. **Walkways**: what's the rule — corridor every N rows, and how wide?
6. **Keepouts**: confirmed policy to shape segments around obstructions and
   reserve keepout polygons for scattered equipment? Always model neighbor
   trees?
7. **Inverters**: why Huawei as house standard, and the exact mixing rule
   (top-up with 40KTL)? When is 380/400 V chosen?
8. **Module**: is Tongwei 715 W locked in for everything going forward,
   including residential (casa-santiago used it at 11 kW)?
9. **Per-project sizing driver**: for each library entry — roof-limited,
   NPV-optimum, 0.7 MW step, or client budget? (This is the blank field in
   every notes.md.)
10. **Carports**: offered when roofs are structurally unusable, or as a
    client preference (pinnacle, africam)?
11. **New-build workflow**: for blueprint-underlay designs (yaqui), what
    inputs do you require from the architect (CAD scale, roof spec)?
