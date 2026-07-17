---
name: solucion-deck
description: >-
  Build the Newman "Solución Energética" client-facing HTML presentation (deck) that
  integrates one or more proposal Excel workbooks (calculadoras / libros rev2) into a
  single interactive, printable HTML in the AFC/GEPP design system. Use whenever the
  user wants proposal xlsx files turned into "one single presentation html", a
  client-facing deck with illustrative graphs, an option selector (Autoconsumo vs GD
  Medición Neta / compra vs PPA), space-fit (superficie) verification, or an update to
  an existing "* - Solucion Energetica*.html" in Drive. Triggers: "presentación",
  "deck", "html client facing", "integra en una sola presentación", "como el de
  AFC/GEPP", "solución energética html".
---

# Newman "Solución Energética" HTML deck (AFC/GEPP style)

Turns proposal workbook(s) into ONE interactive client-facing HTML: portada →
manifiesto → trayectoria (proyectos en operación) → problemática → resumen portafolio →
esquemas → superficie → consumo → solución (cascada) → despacho → proyección 20 años →
supuestos → cierre. Reference implementation (GEPP v5, jul-2026) lives in `assets/`.

## Inputs & access
- Proposal xlsx books live in a **client Drive folder owned by `mario@newman.re`**.
  The claude.ai MCP Drive connector is a DIFFERENT account (`newman.jjzo@gmail.com`) —
  use the gcloud token instead: `TOKEN=$(gcloud auth print-access-token)` then the
  Drive REST API (`files?q='<folderId>'+in+parents`, `files/<id>?alt=media`,
  multipart upload; always `supportsAllDrives=true`).
- Client problemática (if referenced): original perfil/consumo workbook, usually in
  `~/CFE Brain/raw/` (e.g. hoja `RESUMEN_` = planta → descripción → problemática).
- Superficie disponible por sitio: ask the user or read from the workbook Supuestos.

## Steps
1. **Download** every relevant xlsx from the client folder to the scratchpad. If the
   folder already holds a delivered `* - Solucion Energetica*.html`, keep it — NEVER
   overwrite a delivered file; deliver `... v2.html`, `... v3.html`, etc.
2. **Extract → JSON** with an anchor-scan (don't hardcode row numbers). Adapt
   `assets/extract_gepp.py`: it locates sections by their `A`-column titles
   ("1. DATOS BASE", "2. SISTEMA PROPUESTO", "5. PROYECCIÓN 20 AÑOS — OPCIÓN 1",
   "8./9. DESPACHO DÍA TÍPICO", Resumen rows "Op1:/Op2:", PORTAFOLIO sums) and emits
   one JSON with `resumen`, and per-site: baseline 12m, sys (label→[op1,op2]),
   proj1/proj2 (20y), despacho invierno/verano + lectura.
3. **Verify space-fit** when superficies are known: `req = kWp × densidad (m²/kWp,
   from Supuestos, GEPP=4.0)` vs disponible. If it fits → report utilization % and
   holgura; if not → report % que cabe (`disp/req`), kWp que caben (`disp/densidad`)
   and m² faltantes. Flag >98.5 % utilization as "al límite del predio".
4. **Build the HTML** from `assets/template_gepp_v5.html` (THE template; v2 kept only
   as historical reference). Replace the inlined model with the JSON; adapt copy
   (client name, problemática cards quoting the client's own words + answer with
   proposal numbers, autoabasto/cliff story only if applicable), and the META/site keys.
   **v5 feature checklist (see `assets/v5_features_spec.md` for exact HTML/CSS):**
   - **Montaña cover-band** blending portada→manifiesto: `.cover-band` band at the
     bottom of `#portada` (`bottom:-22vh`, `#portada padding-bottom:34vh`), faded via
     `mask-image` linear-gradient + a `::after` `--canvas` gradient (the mask-image
     technique — no mix-blend, no SVG). Image = `assets/mountain_duo.webp` (brand art,
     client-agnostic) wired as photo slot `portada`.
   - **ZONA FOTOS editable photo system**: every swappable photo lives in a
     `<script type="text/plain" data-photo="KEY">data:…</script>` block after `<body>`,
     targeted by `<img data-photo-slot="KEY">` (no src), filled by the loader before
     `</body>`; preceded by the "CÓMO EDITAR" comment guide. Keeps data-driven
     helioscope/sembrado images in `IMAGES{}` (they switch with the selector); only
     static decoration photos become slots.
   - **Trayectoria photo mosaic** (section 03 `#trayectoria`): 5-figure `.ph-grid` /
     `figure.pframe` "Proyectos en operación" gallery (lead spans both rows).
   - **Cierre crew photo**: `<img class="crew" data-photo-slot="cierre">` leading `.cta`.
   - **v5 print-CSS**: `@media print` overrides for `.cover-band` (un-mask, static),
     `.ph-grid` (fixed rows), `#portada` padding, and despacho chart de-animation.
   **Manifiesto (Quiénes somos) is STANDARD copy — do not rewrite per client** (user-
   approved 2026-07-13, already in the template): opener «Es un tiempo nuevo, tiempo
   de cambios, tiempo de adaptarse e innovar, tiempo de atreverse a crear la nueva era
   del hombre.» → invitation «Newman Power Alliance te invita a ser parte de la nueva
   era…» → «Reunimos años de conocimiento y el trabajo de grandes instituciones
   internacionales… la red de empresas y organizaciones más grande del sector.» and
   the closing quote in ENGLISH: “What we do today becomes tomorrow's past, let's
   light it up.” (replaced the old «La energía más rentable…» quote).
   Keep the design system EXACTLY:
   - tokens: canvas `#F6F4F9`, ink `#221A33`, accent `#621558`; chart series
     `#8F3A81` (purple), `#B8741A` (amber), `#4356A5` (navy) — palette already
     validated with the dataviz skill validator against `#F6F4F9`.
   - full-viewport `section.page`, eyebrow/pagenum, KPI rails, Newman isotype SVG,
     print `@page letter landscape`.
   - interactivity: fixed bottom **option selector pill** (re-renders the whole deck
     via a RERENDER registry + `.opname` spans), site tabs per section, multi-meter
     sites expand via sub-chips (and an expandable row in the resumen table), hover
     tooltips (`data-tip` + `bindTips`), invierno/verano toggle in despacho.
   - charts (inline SVG, no libraries): stacked Base/Int/Punta consumption, cascada
     waterfall (gasto → −ahorros → +pagos → gasto final), despacho día típico — use
     the REVIEWED v5 design (see gepp_v5 renderDesp in ~/CFE Brain/work/gepp-deck/
     build_v5.py): monochrome violet PV area #8F3A81 (NO amber — user called it
     tacky), monotone Fritsch–Carlson interpolation for data series, neta line
     navy→plum hard-snapped to the punta band, single-layer punta band + unboxed
     PUNTA label, night-charge fill + «BESS cargando · horario base», direct-labeled
     «Carga del sitio», BESS lane with labeled CARGA/DESCARGA capsules, round kW
     ticks, «recorte a X kW» haloed in-band, 2-item legend, NO sun animation;
     for the non-simulated option scale the PV curve by kWp ratio and recompute
     `neta = carga − pv − chg − dis`, footnote it; 20-year projection (pleno dashed /
     real / con Newman, cliff year marked amber), portfolio cumulative op1 vs op2
     (selected emphasized).
5. **Quality gates** (all required before upload):
   - `node`: extract the `<script>` and `new Function(src)` for syntax;
   - DOM-stub runtime test (see the stub in this skill's provenance session or
     rebuild: fake `document.getElementById` returning innerHTML-capturing objects)
     running EVERY renderer × every site key × both options × both seasons +
     portfolio; then grep all captured HTML for `NaN|undefined` leaks;
   - **photo-slot check**: every `data-photo-slot` img resolves to a matching
     `<script data-photo>` block (and vice-versa) — no empty/broken slots;
   - **montaña band present**: the `.cover-band` exists on `#portada` with slot `portada`;
   - eyeball in a browser if one is available (usually not on this box — say so).
6. **Deliver**: multipart-upload the HTML to the same client Drive folder
   (`uploadType=multipart`, metadata JSON with `parents:[folderId]`). Report the
   webViewLink and remind the user Drive preview doesn't run JS (download → open).
7. **Memory**: update the client's auto-memory with file id + what changed.

## Variantes / portafolios (multi-proposal clients)
When a client has multiple proposal VARIANTS (site-selection / sizing, e.g. 1MW /
3.9MW / 4.4MW), the option selector switches VARIANTS (use `.vname` spans, not GEPP's
two-option `.opname`). Lessons:
- Map helioscope images **per variant** — a site's design can differ in size between
  variants; caption illustrative images honestly (say when a shot is illustrative).
- Show mounting-type chips per site (techo / suelo / pedestal / carport / mixto).
- **PV-only portfolios**: omit ALL BESS chart elements (no despacho charge/discharge,
  no punta-shave story) — use the Medición-Neta narrative.
- Derive gasto actual from **Σ recibos**, never a stale workbook indicator.

## Naming
`<Cliente> - Solucion Energetica[ vN].html` — matches the AFC/GEPP convention.

## Build-time inputs (`scripts/` — issue #3)
When building from `crm.bill` + `design.current_offer` (no rev2 workbook), generate the
MODEL gaps with `scripts/build_deck_inputs.py OFFER.json --target-irr X --punta-basis B`:
régimen dual-run Op1/Op2 (single-option fallback <700 kWp), PPA terms from the pricer,
20-yr projection, synthetic despacho 24 h (ALWAYS keep its "ilustrativo" footnote), and
the 12-mo baseline. `--target-irr` (0.14 vs 0.19) and `--punta-basis` (billing vs
calendar) are OPEN decisions — required flags, no default; both variants' GEPP numbers
live in `scripts/baselines.json`. Gate before use: `python3 scripts/golden_test.py`
(pins vs the delivered GEPP rev3/rev4 books + deck).

## Assets
- `assets/template_gepp_v5.html` — **canonical reference** (built GEPP v5: montaña
  cover-band, ZONA FOTOS system + all 7 data-photo blocks, Trayectoria mosaic, cierre
  crew, v5 print-CSS). Model is inlined here — swap it for the new client's JSON.
- `assets/v5_features_spec.md` — exact HTML/CSS for every v5 feature over v2.
- `assets/mountain_duo.webp` — the montaña (portada cover-band brand art, client-agnostic).
- `assets/template_gepp_v2.html` — historical reference (v2 layout, `__MODEL__` placeholder).
- `assets/extract_gepp.py` — anchor-scan extractor for the rev2 workbook layout.
