# HelioScope route — CFE address → verified roof → PV design

Turns every RPU in Supabase with a CFE bill on file into a HelioScope solar
project, with an explicit confidence score that the located roof is the real
service point.

## The route

```
Supabase (main, read-only)                 Google APIs                    HelioScope (Enterprise API)
─────────────────────────                  ───────────                    ────────────────────────────
raw_clients.cfdi ──extract_sites.sql──▶ sites.json
  CALLE1/CALLE2/COLONIA/CP                    │
  + client.rpu + ref.sepomex_cp               ▼
                                    geocode_verify.py
                                      Places Text Search (brand/landmark)
                                      Geocoding (literal address)
                                      Solar API buildingInsights (roof m², max panels)
                                              │  confidence 0-100 → HIGH / MEDIUM / LOW
                                              ▼
                                     run_pipeline.py ────────────▶ create_project(lat,lng)
                                              │                    create_design(field segments)
                                              ▼                    run_simulation()
                                     out/designs.json ──▶ client.helioscope_site (dev branch, schema.sql)
```

Why this shape: CFE addresses are "between streets" + landmark strings
("HOTEL FIESTA INN", "FTE A SUZUKI", "KM 16.5 ZONA HOTELERA"), so a literal
geocode alone is unreliable. This portfolio is mostly the Grupo Posadas hotel
trust (FIDEICOMISO F/1596), and branded hotels are first-class Google POIs —
the Places match is the primary signal, the literal geocode is the
cross-check, and the Solar API confirms an actual building with a usable roof
(and pre-sizes the array: `maxArrayPanelsCount`).

## Confidence rubric (per design, reported as evidence[])

| Signal                                         | Points |
|------------------------------------------------|--------|
| Branded/lodging POI matched in Places          | +40 (25 if unbranded) |
| Bill CP appears in the POI address             | +15 |
| Municipio matches POI address                  | +10 |
| Literal geocode ROOFTOP (interpolated: +10)    | +20 |
| POI and geocode agree within 800 m             | +15 |
| Solar API finds a building at the point        | +10 |

**HIGH ≥ 80** auto-design · **MEDIUM 50–79** design + flag for human roof
confirmation · **LOW < 50** no design, manual pinning queue.

## Run

```bash
export GOOGLE_MAPS_API_KEY=...   # Places API (New) + Geocoding + Solar API enabled
export HELIOSCOPE_API_KEY=...    # Enterprise plan key

python3 geocode_verify.py                 # all 57 sites → out/verified_sites.json
python3 run_pipeline.py                   # dry-run: shows what would be created
python3 run_pipeline.py --live            # creates HelioScope projects + designs
python3 run_pipeline.py --site 780881200029 --live   # single site
```

Refresh the dataset after new bills land: run `extract_sites.sql` via the
Supabase MCP / psql and rewrite `sites.json`.

## Persistence & deploy

- `schema.sql` creates `client.helioscope_site` — **apply on the dev branch only**.
- Keys belong in `vault.secrets` (`HELIOSCOPE_API_KEY`, `GOOGLE_MAPS_API_KEY`)
  alongside the existing `DIGITALOCEAN_TOKEN`/`GITHUB_TOKEN`.
- For recurring runs, deploy as a small DigitalOcean worker (or a Supabase
  scheduled edge function) that re-runs the route when a new RPU gains its
  first CFDI.

## Caveats

- `helioscope_config.json` endpoint paths follow HelioScope's documented
  Project → Design → Simulation model, but the exact spec ships with the
  Enterprise API key — validate before `--live`.
- The seed design is a 40 m square field segment on the verified roof point
  (or Solar API roof polygons when available); trim to the parapet in the
  HelioScope UI before quoting module counts to a client.
- Solar API coverage in Mexico is partial; a missing building response does
  not lower the score, it just withholds the +10.
