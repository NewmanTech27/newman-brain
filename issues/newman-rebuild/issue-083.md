# #83: CRITICAL: harvest drain truncates deep grids — grid_rows=97 but bill_count=1 (got newest only)

- State: OPEN
- Created: 2026-07-11T18:56:12Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/83

## Body

## Finding (depth probe #81)
RPU 780020900569: **grid_rows=97, bill_count=1, xml_count=1** — the OtrasFacturas grid had **97 invoices**, the drain captured **1** (only the newest, 202606). 97 rows in one grid means it's NOT pagination — `download_all_recibos` is dropping 96 of 97 downloads on a deep grid.

Earlier RPUs got 8/8 (shallow grids drained fully), so the bug only bites deep histories. The board's "~30 invoices" expectation was an underestimate — real depth is ~97.

## Caveat
id 14 was one of two CONCURRENT harvests (before the #82 single-flight fix), so concurrency may have disrupted its grid mid-drain. Requeued 780020900569 for a CLEAN single-flight re-harvest to isolate:
- clean harvest gets ~97 → the 1/97 was concurrency (fixed by #82).
- clean harvest still gets ~1 → genuine deep-drain bug in `download_all_recibos` (likely: clicks 97 buttons with 1200ms sleeps = ~116s, then a single drain-budget wait; rows may need scroll-into-view, or CFE rate-limits rapid downloads, or only the visible/newest row's button is live).

## Likely fix (if genuine)
Rework `download_all_recibos` for deep grids: click → wait-per-file (not fire-all-then-wait), scroll each row into view, verify each file landed before the next, and scale the budget to grid_rows. The grid_rows probe (#81) now measures completeness (grid_rows vs bill_count) to verify a fix.

## Comment by NewmanTech27 (2026-07-11T20:19:49Z)

## RESOLVED — grid_rows counts DOCUMENTS, not billing periods; captures are complete

Fresh-run verification on 008970211013: the drain downloaded **413 files**, `raw_cfe.mi_espacio` stored **8** — one per billing month (202511–202606, 8 consecutive months, 1 recibo each).

So CFE's OtrasFacturas grid lists ~7-8 documents per billing period (recibo XML + PDF + aviso + detalle …). `grid_rows` counts those raw document rows, so `grid_rows=61` = ~8 months × ~7 docs. **`bill_count` (unique rpu+period) = 8 billing months = the complete history.** NOT truncation.

The original "1 of 97" was the concurrency bug (#82) collapsing captured *documents* to 1 → 1 period. With #82 (single-flight) + #83 (deep-drain, self-bounding bridge) fixed, the drain captures all documents → all billing months.

**Takeaway:** `bill_count` (billing months) is the real completeness metric, not `grid_rows` (documents). Accounts have ~8 months of history, fully captured. #83 fix stands; the depth concern is resolved. The concurrent-download optimization is still worthwhile for the deep document grids (413 files) but is a speed, not completeness, item.

## Comment by NewmanTech27 (2026-07-11T21:17:35Z)

## REOPENED — the real truncation is PAGINATION (I was wrong that 8=complete)

Board pushed back: MiEspacio has way more invoices. Verified: 424 downloaded XMLs for 008970211013 all span the SAME 8 recent months (202511–202606). The OtrasFacturas GridView **paginates** the history (frozen cfe.js: "the depth: up to ~30 months"; frozen harvest.js has `gotoNextGridPage`/`hasNextGridPage` clicking through pager pages). The rebuild's `download_all_recibos` only drains page 1 → the recent ~8 months.

**Fix (coded, pending deploy):** ported pagination into the bridge — drain each page, click the GridView pager next (tr.pager/[id*=Pager], next numeric page or "siguiente"/"..."), repeat until no next page, bounded by drainBudgetS + a page cap.

Verify on 008970211013 after deploy: bill_count should climb from 8 toward ~24-30 distinct billing months.
