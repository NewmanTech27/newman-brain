# #85: MiEspacio harvest depth: only ~8 recent months captured — pagination advance unverified

- State: OPEN
- Created: 2026-07-11T22:13:59Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/85

## Body

## Symptom
First harvest of the fresh run finished with **grid_rows=61, bill_count=8, months_covered=8**. The raw periods for the account span only `202511 → 202606` (8 consecutive recent months). The board expects ~24–30 months of MiEspacio history.

Every harvest this run also resolves to **`partial`** (bills drained, inline eliminar verdict != CONFIRMED_REMOVED) — the endpoint's post-cleanup then confirms removal (`verdict=confirmed_removed`), so the account is **not stranded** (charter #7 OK) and data lands. Partial is a soft-fail, not a strand.

## Two candidate root causes for the depth
1. **Pagination breaks after page 1** — `download_all_recibos` paginates via `gotoNextGridPage` (finds the GridView pager `<span>` current-page + next `<a>`). If the OtrasFacturas grid's pager selector doesn't match, it returns `no-pager` and drains only page 1 (~8 recent months).
2. **Account genuinely has 8 months** — the grid may render all 61 rows on a single page with no pager, in which case 8 months is complete for this (possibly newer) service.

`grid_rows=61` is the page-1 row count only (`grid_row_count` reads the current DOM before draining), so it can't distinguish the two.

## Action taken
Added surgical stderr diagnostics to `cfe_bridge/bridge.mjs` `download_all_recibos` (bridge stderr → endpoint log, live next harvest, no manual CFE driving):
- `[drain] page N: X download controls` per page
- `[drain] pager: {advanced, why, span, links}` — reveals whether a pager exists and why advance stops (`no-pager` / `no-next` / advanced)
- `[drain] done: N page(s), X new files`

The next natural harvest will show whether a pager exists. If `why=no-pager` on an account we know has >8 months, the pager selector is wrong and needs correcting to the real CFE OtrasFacturas pager markup. If it genuinely shows one page, 8 months is complete and this is a non-issue.

## Follow-ups
- Consulta deep-history pagination (no-login path) — separate, still pending.
- Consider why inline eliminar never confirms (always `partial`) even though post-cleanup does — likely the drain leaves the grid on a later pager page; investigate once depth is resolved.

## Comment by NewmanTech27 (2026-07-11T23:10:53Z)

## ROOT CAUSE FOUND + FIXED

Not a pagination/selector bug. The OtrasFacturas grid has **no pager** — it renders the entire history on a single page. Diagnostic trace from the first fixed harvest:

```
[drain] page 0: fetchDrain 22 files, 11 rejected
[drain] pager: {"advanced":false,"why":"no-pager", gridHtmlTail:"...gvFacturasUsuario_ctl23_lnkDescargaXML..."}
[drain] done: 1 page(s), 22 new files
```

The real cause: `download_all_recibos` drained by **clicking** each ASP.NET download button (`await h.click()`). A click on a download postback can hang its promise indefinitely (no navigation ever resolves), stalling the whole drain loop until Python's subprocess timeout **SIGKILLed the bridge (~330s)** — after only the newest ~8 months had downloaded. Every account looked like an "8-month cap"; it was actually a mid-page truncation. The SIGKILL (no catch/finally) is why the drive also never confirmed eliminar → **every harvest was `partial`**.

## Fix
Replaced the click loop in `download_all_recibos` (cfe_bridge/bridge.mjs) with the frozen **`fetchDrain`** (fetch-POST replay of each `__doPostBack`, 15s/fetch timeout, chunked 3-wide + backoff, page-tagged files). This is the same robust path Consulta already uses.

## Result (first fixed harvest)
- status **`harvested`** (was always `partial`)
- **11 months** captured (`202410→202606`) vs the 8-month cap
- 246s (was ~480s)
- no hang, eliminar confirmed clean

Fixes BOTH the depth truncation and the always-`partial` symptom. Requeuing the 7 accounts drained on the old click code so they re-drain at full depth.
