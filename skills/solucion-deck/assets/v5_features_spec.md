# Solución Energética v5 — visual/structural feature spec

The v5 additions over the v2 template. **Canonical reference:** this skill's
`assets/template_gepp_v5.html` (built by `build_v5.py`; photo-slot machinery introduced
in `build_v4.py`). The montaña asset ships as `assets/mountain_duo.webp`.

Each entry below states what v5 adds and gives the exact HTML/CSS to port. The examples
were first written against a Pueblo-Bonito build, so some entries note "PB adaptation" —
read those as a worked example of adapting the v5 feature to a specific client, not as a
requirement of this skill.

---

## FEATURE LIST (severity-ordered — what v5 adds over v2)

1. **[HIGH] Montaña "cover-band" on the portada that blends into page 2** — v5 has an absolutely-positioned image band at the bottom of `#portada` with a CSS gradient mask that fades into the canvas of the following `#manifiesto` page. PB has none of this; PB's portada uses a faded full-bleed `.hero-bg` (`opacity:.10`) of a site photo instead — a different, weaker effect. (User complaint #1.)
2. **[HIGH] "ZONA FOTOS" editable photo system entirely absent** — v5 externalises every photo into `<script type="text/plain" data-photo="…">` blocks + `<img data-photo-slot="…">` targets + a small loader script, preceded by a "CÓMO EDITAR" HTML comment guide. PB instead bakes photos into a JS `IMAGES{}` object and assigns them programmatically — not hand-editable, no swap slots. (User complaint #2.)
3. **[MED-HIGH] "Trayectoria / Proyectos en operación" photo-grid section (03) missing** — v5 section `#trayectoria` is a 5-photo mosaic (`.ph-grid` + `figure.pframe` with captions). PB has no equivalent "projects in operation" gallery. (PB's `#sembrado` shows HelioScope layouts — a different purpose, not a substitute.)
4. **[MED] Cierre "crew" photo missing** — v5 cierre CTA card leads with `<img class="crew" data-photo-slot="cierre">` (a rooftop/skyline shot). PB cierre CTA is text-only.
5. **[MED] Supporting CSS missing** — `figure.pframe`, `.ph-grid` (+ `.lead`), `.cover-band`, `.cta .crew` are not in PB's `<style>`. Required for gaps 1/3/4.
6. **[LOW-MED] Print-CSS interactions missing** — v5 has dedicated `@media print` rules for `.cover-band` (un-mask, static, 34mm), `.ph-grid` (fixed 38mm rows), `#portada` padding, and de-animating the despacho chart. PB's print block is the generic one and doesn't handle these new elements.
7. **[LOW] "CÓMO EDITAR" editing-guide comment missing** — the top-of-body Spanish instructions block that documents text/photo editing. Ships with the ZONA FOTOS system (gap 2).

---

## SPEC ENTRIES

### 1. Montaña cover-band (portada → page 2 blend)

**What/where:** Last child of `#portada`, an absolutely-positioned band anchored to the bottom of the cover, extending *below* the section fold so its masked bottom edge dissolves into the `--canvas` background just as `#manifiesto` begins. `#portada` gets `border-bottom:none` and large `padding-bottom` so the band has room.

**v5 HTML (inside `#portada`, after the wordmark/eyebrow block):**
```html
  <div class="cover-band"><img data-photo-slot="portada" alt="Montaña Newman"></div>
</section>
```

**v5 CSS (exact):**
```css
#portada{padding-bottom:34vh;border-bottom:none}
.cover-band{position:absolute;left:0;right:0;bottom:-22vh;height:58vh;overflow:hidden;pointer-events:none;
  -webkit-mask-image:linear-gradient(180deg,#000 50%,rgba(0,0,0,0) 97%);
          mask-image:linear-gradient(180deg,#000 50%,rgba(0,0,0,0) 97%)}
.cover-band img{width:100%;height:100%;object-fit:cover;object-position:center top}
.cover-band::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,var(--canvas) 0%,rgba(246,244,249,0) 40%)}
```

**How the blend works (technique):** Two stacked gradients, no `mix-blend-mode`, no SVG.
- The **`mask-image`** (linear-gradient, opaque to 50% then to transparent at 97%) fades the *bottom* of the image out to nothing, so the band melts into the page below (this is what produces the "blends into the second page" effect).
- The **`::after`** overlay is a top-down gradient from solid `--canvas` (#F6F4F9) to transparent at 40%, feathering the *top* edge so the image emerges out of the cover text rather than starting with a hard line.
- `bottom:-22vh` pushes the band's masked tail past the section boundary; `#portada padding-bottom:34vh` reserves the space.

**PB adaptation:** Replace PB's `.hero-bg` treatment on the portada with this cover-band (v5 has no hero-bg at all). Use the montaña asset `v5assets/mountain_duo.webp` (see §ASSETS) as the portada slot image. If keeping PB's build style, either (a) wire it through the ZONA FOTOS system as slot `portada`, or (b) if not adopting ZONA FOTOS, set the `<img>` src via the existing `IMAGES` map (add `IMAGES["portada"]=datauri(...)`). The mountain is brand art, identical for every client — no PB-specific swap needed. `object-position:center top` and the `--canvas` (#F6F4F9) values are shared between decks, so the CSS ports verbatim.

---

### 2. ZONA FOTOS editable photo system

**What:** A hand-editability layer so a non-technical user can swap any photo by pasting a base64 string or URL into a labelled block, without touching JS.

**Three parts:**

**(a) Guide comment + photo blocks — injected right after `<body>`** (from `build_v4.py`; the block is plain HTML comments + `<script type="text/plain">` blobs):
```html
<!-- ✏️ ZONA FOTOS — cada bloque es una foto; vea instrucciones arriba -->
<!-- 📷 Portada · imagen inferior (montaña Newman) -->
<script type="text/plain" data-photo="portada">data:image/webp;base64,UklGR…</script>
<!-- 📷 Trayectoria · foto grande izquierda -->
<script type="text/plain" data-photo="tray1">data:image/jpeg;base64,/9j/…</script>
… tray2..tray5, cierre …
<!-- ✏️ FIN ZONA FOTOS -->
```
The full "CÓMO EDITAR" comment (gap 7) precedes it — copy verbatim from `build_v4.py` lines 46–74 (guide) / 82–89 (loader). It documents: edit text between tags only; don't touch `<script>` except ZONA FOTOS; convert images with `base64 -w0 foto.jpg` or paste a `https://` URL.

**(b) Slot targets** — every photo `<img>` carries `data-photo-slot="<key>"` and *no* `src`:
```html
<img data-photo-slot="portada" alt="Montaña Newman">
<img data-photo-slot="tray1" alt="…"> … <img class="crew" data-photo-slot="cierre" alt="…">
```

**(c) Loader (before `</body>`, "no editar"):**
```html
<script>
/* Cargador de fotos (ZONA FOTOS) — no editar */
document.querySelectorAll('script[data-photo]').forEach(function(s){
  var src = s.textContent.trim();
  document.querySelectorAll('img[data-photo-slot="' + s.dataset.photo + '"]').forEach(function(im){ im.src = src; });
});
</script>
```

**PB adaptation:** PB currently ships all photos in the JS `IMAGES{}` object (assigned in `deck.js`, e.g. `semb-main`, `hero-bg` via `.style.backgroundImage`). To match v5's editability, migrate the *static, non-data-driven* photos (portada montaña, any Trayectoria gallery, cierre crew) into ZONA FOTOS `data-photo` blocks with `data-photo-slot` targets + the loader. Keep the HelioScope/sembrado images data-driven in `IMAGES` since those switch with the variant selector (they are content, not decoration). Note: `deck.js` line 476 sets `#hero-bg` background via JS — if the montaña replaces hero-bg, drop that line. `build.py` would gain a small step to emit the ZONA FOTOS blocks (mirror `build_v4.py`'s `blocks` loop).

---

### 3. Trayectoria section (photo mosaic)

**What/where:** v5 section 03 `#trayectoria` ("Proyectos en operación"), between manifiesto and the portfolio summary — a 5-image mosaic proving execution track record.

**v5 HTML:**
```html
<section class="page" id="trayectoria">
  <div class="pagenum">03 · Trayectoria</div>
  <div class="eyebrow">Proyectos en operación</div>
  <h2>Azoteas solares de gran formato,<br>operando hoy.</h2>
  <p style="max-width:76ch">Una muestra de los sistemas comerciales e industriales … con los mismos bloques …</p>
  <div class="ph-grid">
    <figure class="pframe lead"><img data-photo-slot="tray1" alt="…"><figcaption>Retail de gran formato · integración urbana</figcaption></figure>
    <figure class="pframe"><img data-photo-slot="tray2" alt="…"><figcaption>Azotea completa · ≈1.5 MWp</figcaption></figure>
    <figure class="pframe"><img data-photo-slot="tray3" alt="…"><figcaption>Nave industrial · cubierta de lámina</figcaption></figure>
    <figure class="pframe"><img data-photo-slot="tray4" alt="…"><figcaption>Cubierta comercial · ≈0.8 MWp</figcaption></figure>
    <figure class="pframe"><img data-photo-slot="tray5" alt="…"><figcaption>Centro comercial regional · PV en cubierta</figcaption></figure>
  </div>
  <p class="footnote" style="margin-top:1rem">Fotografías de proyectos ejecutados y operados por el equipo Newman. …</p>
</section>
```

**v5 CSS:**
```css
figure.pframe{position:relative;margin:0;overflow:hidden;border-radius:14px;box-shadow:0 12px 32px rgba(34,26,51,.14);background:var(--ink)}
figure.pframe img{width:100%;height:100%;object-fit:cover;display:block}
figure.pframe figcaption{position:absolute;left:0;right:0;bottom:0;padding:1.4rem .95rem .6rem;font-size:.72rem;font-weight:600;letter-spacing:.05em;color:#fff;
  background:linear-gradient(transparent,rgba(34,26,51,.55) 35%,rgba(34,26,51,.92));text-shadow:0 1px 3px rgba(34,26,51,.65)}
.ph-grid{display:grid;grid-template-columns:1.35fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:1rem;height:56vh;margin-top:1.6rem}
.ph-grid .lead{grid-row:1/3}          /* first figure spans both rows on the left */
@media(max-width:820px){.ph-grid{grid-template-columns:1fr}}   /* note: v5 collapses columns responsively */
```

**PB adaptation:** PB has real site photos in `$PB/work/img/` (`campo_golf`, `lavanderia`, `taller_golf`, `ptar_sunset`, `sunset5`, `sunset123`, `monte_cristo_1/2`, `ptar_miramar`). Populate the 5 pframes with the strongest Pueblo Bonito shots (e.g. lead = a hero resort/rooftop, plus golf, lavandería, PTAR, monte cristo) and rewrite captions to the PB sites (e.g. "Campo de golf", "Lavandería central", "PTAR Miramar"). Reframe the copy from "azoteas retail/industrial" to "instalaciones de Pueblo Bonito / recurso solar en Los Cabos". Wire each `<img>` as a `data-photo-slot` (tray1..tray5) so it's swappable, or keep as editable ZONA FOTOS placeholders exactly like GEPP v4 if final photos aren't chosen yet. Renumber downstream pagenums (PB currently 01–12; adding Trayectoria shifts them).

---

### 4. Cierre crew photo

**v5 HTML (first child of `.cta` in `#cierre`):**
```html
<div class="cta">
  <img class="crew" data-photo-slot="cierre" alt="Sistema fotovoltaico Newman en azotea, con la ciudad al fondo">
  <h3>Siguiente paso</h3> …
```
**v5 CSS:**
```css
.cta .crew{width:100%;height:24vh;object-fit:cover;object-position:center 62%;border-radius:10px;margin-bottom:1rem;display:block}
```
**PB adaptation:** Add the same `<img class="crew" data-photo-slot="cierre">` at the top of PB's `.cta`. Use a Pueblo Bonito installation/resort photo (or keep the GEPP `v5_cierre.jpg` as a generic Newman-crew placeholder). CSS ports verbatim.

---

### 5. Print-CSS interactions

v5 adds these inside `@media print` (PB lacks them):
```css
@media print{
  #chart-desp .anim{animation:none;stroke-dasharray:none;stroke-dashoffset:0}
  #chart-desp .fadein{animation:none;opacity:1}
  #chart-desp .sunmove{display:none}
  .ph-grid{height:auto;grid-template-rows:38mm 38mm}
  .cover-band{position:static;height:34mm;margin-top:8mm;border-radius:8px;-webkit-mask-image:none;mask-image:none}
  #portada{padding-bottom:4vh}
  #opswitch,#tt{display:none!important}
  .tablewrap{max-height:none!important;overflow:visible!important}
  … (generic @page/section rules shared with PB) …
}
```
**PB adaptation:** Add the `.ph-grid`, `.cover-band`, `#portada` print overrides when gaps 1/3 are ported. The despacho de-animation rules are worth adopting regardless (PB has the same `#chart-desp` animations — its template already carries the `#despacho .footnote` rule but not the print de-animation). Keep PB's `#opswitch` (variant selector) hidden in print — PB already does this.

---

## GEPP-SPECIFIC — DO **NOT** PORT

- **`#problematica` "Sus necesidades" section (04)** — quotes GEPP's "Perfil de Consumo Eléctrico 2025-26" per-plant needs. PB has its own `#contexto` ("La oportunidad en Los Cabos") already — keep PB's.
- **`#esquemas` "Dos esquemas" (Autoconsumo vs GD Medición Neta) + the `#opswitch data-op` two-option toggle** — GEPP-specific dual-scheme story. PB is single-scheme (PPA GD Medición Neta) and instead uses a **three-variant size selector** (1MW / 3.9MW / 4.4MW). Do not import the Opción-1/Opción-2 model.
- **Autoabasto cliff story** — "Convive con su autoabasto (TALA/ENEL) hasta 2032", "Cobertura 2033", the vencimiento-de-autoabasto guarantees and cierre bullet. Entirely GEPP. PB has no legacy autoabasto.
- **BESS despacho narrative** — v5's despacho chart is a Solar+BESS punta-shave story (charge/discharge capsules, "recorte a X kW", ciruela-en-punta). PB is **solar-only, no BESS** and its `#despacho` is already adapted to a Medición-Neta narrative — do not reintroduce BESS dispatch elements.
- **`.opname` / two-option plumbing** — PB uses `.vname` (variant name) throughout; don't import GEPP's `opname` bindings.
- **Superficie framing tied to "Tongwei 715 Wp"** and per-option kWp — GEPP's exact module/CAPEX rates (0.65 USD/Wp PV, 0.28 USD/Wh BESS, TC 17.55) differ from PB's; PB already has its own sembrado/supuestos numbers.

Note: PB **already carries the v5 manifiesto copy** (institutional text + English quote) verbatim — no gap there.

---

## ASSETS  (`$PB/work/v5assets/`)

| file | bytes | format · dimensions | role / notes |
|---|---|---|---|
| `mountain_duo.webp` | 196,550 | WEBP (VP8X) · **2048×1132** | **The montaña.** Byte-identical to the `data-photo="portada"` blob embedded in gepp_v5.html and to `photos/mountain_duo_b64.txt`. This is the portada cover-band image. Use as-is (brand art, client-agnostic). |
| `v5_portada.webp` | 196,550 | WEBP (VP8X) · 2048×1132 | Same bytes as above, decoded straight from the v5 portada slot (kept for provenance). |
| `newman_mountains.png` | 848,397 | PNG · **2560×1415** | Higher-res PNG source of the mountains (from `photos/newman_mountains.png`). Use if you want a crisper/larger master before re-encoding to webp. |
| `v5_tray1.jpg` | 147,086 | JPEG · 1000×666 | GEPP trayectoria lead photo (retail rooftop). Placeholder only — replace with PB site photo. |
| `v5_tray3.jpg` | 117,863 | JPEG · 1000×562 | GEPP trayectoria (industrial). Placeholder. |
| `v5_tray4.jpg` | 137,212 | JPEG · 1000×562 | GEPP trayectoria (commercial). Placeholder. |
| `v5_tray5.jpg` | 139,441 | JPEG · 1024×767 | GEPP trayectoria (sunset mall). Placeholder. |
| `v5_cierre.jpg` | 166,721 | JPEG · 900×1200 | GEPP cierre crew/rooftop-skyline photo. Generic Newman placeholder for PB cierre. |

Notes:
- `v5_tray2.jpg` failed to decode (base64 padding artifact on extraction) — it is a GEPP retail photo and would be replaced by a PB photo anyway, so not re-extracted.
- **Logo / isotype:** the Newman isotype is an **inline SVG** in both decks (5-bar gradient, `linearGradient id="nwm-g1"` stops `#1E2A6E → #C81E82`), not a binary asset — PB already has it (2 occurrences: portada + cierre). No extraction needed; nothing missing.
- **Placeholder-slot artwork:** there is none beyond the photos above — v5 slots render the real embedded photos; empty slots would just show broken-img until filled. PB's real site photos in `$PB/work/img/` are the natural fill.
