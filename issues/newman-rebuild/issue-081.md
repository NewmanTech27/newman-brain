# #81: harvest drain may truncate deep histories — download_all_recibos does not paginate the OtrasFacturas grid

- State: OPEN
- Created: 2026-07-11T18:35:45Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/81

## Body

## Concern (raised checking extraction depth)
Both harvested RPUs returned **exactly 8** invoices — a bimonthly account (008241003311, 202504–202606) and a monthly account (008970211013, 202511–202606). Two accounts of different cadence landing on the same count looks like a **page-size**, not real history.

Reading `cfe_bridge/bridge.mjs`:
- `download_all_recibos` clicks download controls only in the **currently-rendered** grid (`gridSelector xmlBtn, gridSelector pdfBtn`) — **no pagination / next-page navigation**.
- `grid_row_count` counts only the current rows.

A bridge comment claims "deep ~30-month grids" get a longer budget, implying the grid may render all rows without a pager — in which case 8 is genuine. Ambiguous offline.

## Investigation (shipped)
Instrumented the harvest to record `grid_rows` (the count the drain sees) into `pipeline.mi_espacio`, alongside `bill_count`. Over the next ~9 harvests:
- `grid_rows` varies per account AND `grid_rows == bill_count` → full depth, no truncation. Close.
- `grid_rows` caps at ~8-10 (or `> bill_count`) → the grid paginates and the drain only gets page 1 → **fix: paginate the OtrasFacturas GridView** (drain page → click the pager next-page postback → repeat until no next page). Needs the live pager selector.

Blocking nothing today; determines whether we're capturing full billing history.
