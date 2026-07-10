---
title: "public.claim_media boolean=integer bug — CTO verification (CONFIRMED; provenance corrected)"
type: analysis
tags: [cfe-bill-parser, cto-finding, whatsapp-intake, claim_media, silent-loss, prod-drift, verified]
created: 2026-07-09
updated: 2026-07-09
status: vigente
sources: [prod bwudgrwfwjdbvqhgbwty pg_get_functiondef public.claim_media, supabase_migrations 20260708215946 claim_media_atomic, newman-architecture origin/main supabase/functions/whatsapp-intake/index.ts]
---

# public.claim_media boolean=integer bug — CTO verification

cfe reported that `public.claim_media` silently loses WhatsApp bills via a boolean/integer
type bug. Verified read-only against prod `bwudgrwfwjdbvqhgbwty` on 2026-07-09.

## (1) Broken as described — CONFIRMED (and worse: 100% broken)
Live def: `v_inserted boolean`; `get diagnostics v_inserted = row_count`; then
`if v_inserted = 1 then`. `select true = 1;` on prod → `ERROR 42883: operator does not
exist: boolean = integer`. The `IF` condition must be evaluated on every call, so
`claim_media` **raises on every invocation — winner or loser — not intermittently.** It has
been unable to return since deploy.
(The `GET DIAGNOSTICS` line itself is fine: `1::boolean`→true, `0::boolean`→false via the
int→bool assignment cast; the fatal line is strictly `if v_inserted = 1`.)

## (2) Did migrations 014/015 introduce it? — REFUTED
`supabase_migrations.schema_migrations` shows the `v_inserted boolean` + `v_inserted = 1`
text first appears in **`20260708215946 claim_media_atomic`** (2026-07-08). The
RPU-confirmation gate is **`20260709065500 whatsapp_rpu_confirmation_gate`** (2026-07-09);
git `db/migrations/014_whatsapp_rpu_confirmation_gate.sql` / `015_bulk_pdf_confirm_phone.sql`
contain no `claim_media`, `v_inserted`, or `row_count`. **The bug came from the atomic-media-
claim rework a day earlier, not the RPU gate.** Reverting 014/015 would not fix it.
(`claim_media` is also defined in **no git migration** — it is prod-only ledger drift.)

## (3) "Silent loss + stuck redelivery re-fails identically" — CONFIRMED
`whatsapp-intake/index.ts` (origin/main): `rpc()` throws on any non-2xx (`:83`); a thrown
handler returns non-200 **by design** so Twilio redelivers (`:153`, `:235-237`); the
two-phase design needs `claim_media` to return `false` to proceed and only then
`mark_media_done` (`:353-356`). Since `claim_media` errors instead of returning, the
attachment is never processed, never dead-lettered, never marked done → Twilio redelivers →
identical 42883 → **infinite identical re-failure = silent loss.** Precision: `claim_media`'s
own `processed_media` INSERT rolls back with the error (no stuck row there); it is the
message-level claim that hangs — outcome unchanged.

## (4) One-line type fix, no side effects — CONFIRMED
Only caller is the whatsapp-intake edge fn (repo grep; `pg_proc` shows no other DB function
calls it). Fix is one line — `if v_inserted = 1` → `if v_inserted` (cast already gives
true/false), or `declare v_inserted integer`. Either preserves the boolean RETURN contract
(`true`=skip / `false`=proceed) the edge fn relies on (`index.ts:238`), so the caller is
unaffected. `claim_media` touches only `client.processed_media` (media dedup) — **zero
overlap with calc_core / ppa_pricer / proposal / finance.ts / the golden test.** The function
currently always errors, so there is no working behavior to regress.

## Blast radius
Since `claim_media_atomic` (2026-07-08 21:59), **all** WhatsApp media bill intake has failed.

## Process note
The fix migration must be captured in **git and prod** — `claim_media` is currently prod-only
drift (widens DEL-4). Review the fix migration when cfe's draft lands.

## Verdict
Bug + failure model + one-line fix: **CONFIRMED, safe to approve.** The 014/015 attribution:
**REFUTED** — introduced by `claim_media_atomic` (`20260708215946`).

## Related
- [[2026-07-09-gate0-fork-cto-verification]] — the prod-only-drift context (DEL-4 5/75)
