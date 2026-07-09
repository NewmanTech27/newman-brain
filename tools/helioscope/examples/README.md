# examples/ — the HelioScope training library

Drop past HelioScope projects here, one folder per project. This is the
few-shot reference the digitizing agent reads BEFORE tracing polygons on a new
site, so new designs follow house style instead of generic guesses.

## Folder convention

```
examples/<year>-<client-or-site-slug>/
├── report.pdf          HelioScope production/shade report export (the key file)
├── layout.png|pdf      the field-segment layout view, if exported separately
├── segments.csv|dxf    HelioScope CSV/CAD export of field segments (optional)
├── site.kml            polygons if you traced them anywhere (optional)
└── notes.md            REQUIRED, 5-15 lines — see template below
```

`notes.md` template — the "why", which no export captures:

```markdown
# <Site name> — <kWp> kWp, <module model>
- Setback from parapet used: X m   · walkway width: X m
- Keepout margin around HVAC/equipment: X m
- Row pitch / GCR / tilt: ...
- Why segments were placed this way (shading, structure, interconnection):
- Sizing driver: (roof-limited | NPV-optimum | 0.7 MW step | client budget)
- Anything the satellite view got wrong vs reality:
```

## How the agent uses this

1. Before digitizing a new roof, it reads every `notes.md` (cheap) and skims
   1-2 `report.pdf` layouts closest in building type (hotel slab, warehouse,
   retail pad) to load the house rules: setbacks, walkway spacing, what counts
   as an obstacle, how aggressively to pack.
2. The distilled rules live in `HOUSE_STYLE.md` (this folder) — regenerate it
   whenever several new examples land: the agent re-reads the library and
   updates the numbers with citations to the example folders.
3. Corrections are training data: when a human fixes a traced polygon
   (edits `out/roof/<RPU>_polygons.json`), commit the fix — the diff is the
   lesson, and the site becomes a new example.

## Current house rules (seed — refine as examples land)

See `HOUSE_STYLE.md`. Seeded from CFE Brain wiki (module = Tongwei
TWMNF-66HD715, 0.17 kWp/m² intake heuristic, sizing by NPV sweep per
`optimize_sizing.py`, NOT auto-capped at 0.7 MW) pending real HelioScope
examples in this folder.
