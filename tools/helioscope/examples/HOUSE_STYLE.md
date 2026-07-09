# House style — roof digitizing & sizing rules

Status: SEED (v0, 2026-07-09) — derived from CFE Brain wiki + first worked
site (016040800020). Every rule below should gain a citation to an
`examples/<slug>/` folder as the HelioScope library fills in; rules without an
example citation are provisional.

## Module & packing
- Module: **Tongwei TWMNF-66HD715** — 715 Wp, 2.384 × 1.303 m (3.106 m²),
  bifacial 80±5% (datasheet: CFE Brain `raw/pdfs/2025-06-30 - 720w TONGWEI.pdf`).
- Flat roof: 10° ballasted rows facing south; packing **0.75 on digitized
  clear planes** / **0.55 on gross roof** → 0.173 kWp/m² clear
  (matches CFE Brain intake heuristic 0.17 kWp/m²).

## Tracing rules (order matters)
1. **Verify the building first** — Places POI + OSM footprint (Overpass) +
   Solar API buildingInsights must agree before any tracing.
2. **Digitize in visual (roof-pixel) space, export in true space** — measure
   `lean_px` against the OSM footprint or the Solar API mask and set it in
   `<RPU>_polygons.json`; off-nadir lean runs 5–10 m on 4-6 story buildings.
3. **Run `--layers` before tracing** when Solar API covers the site: the red
   local-relief (≥0.8 m) marks equipment/cores to keep polygons OFF of, blue
   marks chronically shaded roof. Check `imageryDate` — layers may predate the
   Esri frame; the Esri image wins on current equipment, DSM wins on heights.
4. Keep a **buffer of ~2 px at z19 (0.5 m)** between a usable polygon edge and
   any parapet, equipment row, or mask edge. Provisional; replace with the
   setback used in real HelioScope projects once examples land.
5. Obstacles get their own polygons (never carved out of usable ones) so the
   KML shows the client what was avoided and why.
6. Iterate visually: export → crop the annotated PNG → look → nudge. Never
   ship a polygon that hasn't been rendered over the imagery at ≥3× zoom.

## Sizing doctrine (from CFE Brain — do not regress)
- Size PV+BESS to **maximize client NPV, not to stay under 0.7 MW**; the
  0.7 MW line is a regulatory step (exento vs autoconsumo), not a cap.
- Roof capacity from this tool is the **PV ceiling input** to
  `optimize_sizing.py`; the NPV sweep decides the build size.
- PV ⊥ punta in SIN divisions: the roof cuts energy, BESS cuts capacidad.
  Report coverage % of consumption, never imply demand savings from PV alone.

## Report style
- Client reports follow curvas.newman.re: Spanish, evidence-tiered
  (fuente-confirmado / derivado / supuesto), satellite hero with lettered
  strips keyed to a table, obstacles list, KML download.
