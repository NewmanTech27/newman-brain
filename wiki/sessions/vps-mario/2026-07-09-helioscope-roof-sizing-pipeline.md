# HelioScope Roof-Sizing Pipeline + HOUSE_STYLE Distillation

**Summary**: Built a geocode→roof-polygon→module-fit pipeline for Newman under `tools/helioscope/`, minted a Google Solar/Places/Geocoding API key, ran the 57-site portfolio, and distilled a HOUSE_STYLE from 30 reference HelioScope designs.
**Tags**: #newman #helioscope #solar-api #roof-sizing #tongwei #newman-brain
**Created**: 2026-07-09
**Source**: newman-vps sessions 4ba7132d, 4d53b6e5, 32fc120e, 12c9b6a4, 2d4efed1, user mario

---

## Content
- Goal: from CFE addresses in Supabase, find the real roof (addresses are imprecise), score confidence, and estimate PV module fit. No HelioScope API key yet — workaround uses satellite imagery + OSM footprints + packing formula.
- **Google API key** created end-to-end via gcloud as mario@newman.re: new GCP project **`cfe-brain-geo`**, enabled Places API (New) + Geocoding + Solar API, key restricted to those three, saved gitignored at `~/newman-brain/tools/helioscope/.env` (mode 600). Not written to `vault.secrets` (main branch DB — never touch).
- **57-site portfolio run**: HIGH ≥80% = 36 sites (roof confirmed), MEDIUM 50–79% = 20, LOW = 1 (`671140638635` "FTE A SUZUKI" Tuxtla, needs manual pin). Solar API covered 37/57 buildings = 71,374 m² roof, 21,393 max panels ≈ **12.3 MWp**.
- Scoring refinements now in code: **landmark beats brand** (CFE landmark text + POI bonus); +20 bonus for Posadas-brand POIs. Fixed cases where geocode matched FedEx / medical clinic / wrong hotel.
- **Module standard: Tongwei TWMNF-66HD715** (715 Wp, 2.384×1.303m = 3.106 m², 23.0% eff, bifacial 80±5%). Packing math `0.75 × 715 / 3.106 = 0.173 kWp/m²` lands on the CFE Brain 0.17 kWp/m² heuristic — both systems agree. Datasheet read visually from CFE Brain `raw/pdfs/2025-06-30 - 720w TONGWEI.pdf`.
- **roof_polygon.py** three-mode flow: `--fetch` (satellite imagery), `--layers` (Solar API dataLayers aid), `--export` (KML + GeoJSON + report inputs). Middle "tracing" step is where Claude visually traces the usable roof, verifies building against OSM, iterates. z20 unavailable in Mexicali/Tuxtla/Oaxaca — falls back to z19.
- **HOUSE_STYLE distillation**: 30 curated past HelioScope designs (10kW→10MW) exported to a Drive training library (`INDEX.md`, `_design_specs.tsv` from HelioScope API, `_manifest.csv`). Wrote `examples/HOUSE_STYLE.md` — the real design rules (DC:AC ratio, tilt, racking, azimuth, row spacing, setbacks, keepouts). Re-traced example RPU `016040800020` in house style (v1 overwrote v0, backup `_v0`).
- **KFC/Pizza Hut Chiapas (Alimentos y Franquicias de Chiapas)** roof-sizing: Solar API has NO coverage in Tuxtla/Oaxaca (404), Esri only z19. Fits: KFC 22 Pte `744931031693` ~64 mod/45.8 kWp; KFC Centro `671071116338` ~30 mod/21.4 kWp; Plaza Bella Oax `679220758161` ~64 mod/45.8 kWp; `671140638635` unresolved. Analog areas measured from franchisee's own OSM stores (366 m² KFC, 365 m² Pizza Hut).
- First report modeled on curvas.newman.re style. Repo commit `716ac62` (pipeline) + `8521de2`/`d5d6a7f` (v1 re-traces) on master.
- One dead-end session (2d4efed1): asked to read a Windows path `C:\Users\vidan\helioscope-automation\examples\_HANDOFF.md` — file does not exist on the Linux VPS.

## Related Notes
- [[newman-brain-repo]]
- [[cfe-brain-vault]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
