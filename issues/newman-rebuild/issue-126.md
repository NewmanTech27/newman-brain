# #126: 3 accounts have truncated invoice history in prod (old drain) — re-harvest with deep drain to backfill

- State: OPEN
- Created: 2026-07-13T15:28:55Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/126

## Body

Audit of prod (oioya) `raw_cfe.invoices` shows 3 accounts were captured with the pre-#83 truncating drain and are missing most of their history. The new deep incognito drain (PR #120) scans the full grid but couldn't finish these live due to CFE WAF throttling from heavy same-day use:

| RPU | prod invoices now | full (grid scan) |
|---|---|---|
| `780020900569` (UNIV ANAHUAC) | 1 | 32 |
| `585880702961` (PRODUCTOS CHACHITOS) | 13 | 30 |
| `968221200700` (FIDEICOMISO F/1596) | 18 | 30 |

(The MYRMEX accounts are NOT truncated — their grids genuinely contain 10-14 invoice rows; non-monthly billing.)

Action: after PR #120 merges + deploys, re-harvest these 3 RPUs with the deep drain on a **cooled** CFE account (raw_cfe dedups by sha256+(rpu,period), so re-harvest only adds the missing periods). Depends on #119 (WAF pacing).

## Comment by NewmanTech27 (2026-07-13T16:52:40Z)

**Correction after direct verification:** `968221200700` is NOT truncated — a fresh probe pulled exactly 18 periods (2025-01 → 2026-06) that are **identical** to prod's 18. The grid's "30 invoice rows" include 12 older ones for which CFE no longer serves downloadable XML. So prod is **complete** for 968 (18/18 reachable).

Revised scope: the genuinely-truncated accounts are:
- `780020900569` — prod has **1**, grid scan shows 32 invoice rows → real truncation (old drain).
- `585880702961` — prod has **13**; needs verification (may be complete-at-13 if CFE only serves 13 months for it, or truncated).

Net: re-harvest **780** (and verify **585**) with the deep drain; 968 is done.

## Comment by NewmanTech27 (2026-07-13T16:53:48Z)

**Verified via period analysis — scope narrows to ONE account.**
- `585880702961`: 13 invoices = 2025-06→2026-06, **13 consecutive recent months → COMPLETE** (windowed, like 968). Not truncated.
- `780020900569`: **1** invoice (2026-06 only) — genuinely truncated; grid shows 32 downloadable rows.

**So `780` is the sole real data gap in the whole 12-account corpus.** Everything else is at its reachable ceiling. Action: after PR #120 merges + deploys, re-harvest **780** on a fresh-quota account (see #128 daily-quota finding) to backfill its ~31 missing periods. Close this once 780 is backfilled.

## Comment by NewmanTech27 (2026-07-15T00:10:01Z)

**780 backfilled 1 → 30 via the patient drain (PR #155 fix) — and it corrects the earlier scope.**

The drain downloads newest-first, so every throttle-cut probe stops at the same recent-N — that N is NOT the account's true history, just where the WAF bit. 780 proved it: quick probes got 1; the patient drain (no per-batch abort) got the full **30** (2024-01→2026-06, monthly, complete).

So my earlier "968/585 complete at window" was wrong — they're **truncated too** (both grids scan 30 invoice rows; prod has 18 / 13 = missing the older months). Re-running them patiently now. Any account whose `[drain]` scan shows more invoice rows than prod holds is a backfill target.
