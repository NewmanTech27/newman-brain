# #92: pipeline.consulta: cross-upload duplicate RPUs — same invoice uploaded N times creates N consulta rows (observed live: 6× for one RPU)

- State: CLOSED
- Created: 2026-07-12T10:12:59Z  Closed: 2026-07-13T22:05:45Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/92

## Body

## Problem

Observed live (2026-07-12): `pipeline.consulta` had 33 rows over only 13 distinct RPUs. One RPU (redacted) had **6 consulta rows from 6 different `pipeline.twilio` uploads** — the same invoice sent 6× over WhatsApp, each cascading to its own consulta row (all 6 then parked `needs_review` via the razón-social bug, see #77 and the payment-form issue).

Dedup exists only:
- **within** a twilio parent: `rpc_advance_twilio_multi` skips an RPU already fanned out under the same `twilio_id` (`supabase/migrations/20260712100000_pipeline_twilio_multi_invoice.sql:62-64` — `where twilio_id = p_id and rpu = v_rpu`);
- on raw XML content: `raw_cfe.*.sha256 unique`.

There is **no unique constraint or guard on `pipeline.consulta.rpu` across twilio rows** (`20260711210000_pipeline_schema.sql` — consulta table has no unique index on rpu).

## Consequence

- N redundant CFE Consulta drives per re-sent invoice → wasted ticks and unnecessary WAF exposure (each drive is a chance to get blocked, see #86).
- N redundant `needs_review` rows for a human to clear.
- Downstream, N `pipeline.mi_espacio` rows can be spawned for one RPU → duplicate full harvests against the shared CFE account (compounds #82 single-flight risk).

## Fix (policy decision needed)

Options, roughly in order of preference:
1. In `rpc_advance_twilio`/`_multi`: if a non-terminal consulta row already exists for the RPU, link the new twilio row to it (`consulta_id`) instead of inserting — upload N becomes an ack, not a new drive.
2. Partial unique index on `pipeline.consulta(rpu)` where status not in ('failed') + `on conflict` handling in the advance RPCs.
3. Time-window dedup (skip if a consulta row for this RPU derived within X days) — weaker, but allows deliberate refresh.

Whatever is chosen must also define the refresh path (`refreshing` status exists for re-querying adeudo on an existing row — reuse it rather than new rows).

## Comment by NewmanTech27 (2026-07-12T12:06:19Z)

## Decision locked: **Fix option 1 (guard at intake)** — with an added mi_espacio check

Owner reviewed live on 2026-07-12 and approved the guard-at-intake approach. Recording the concrete scope + fresh evidence so this is actionable.

### Live re-measurement (project `ugjqqezqtnjkzxkcqujz`, `pipeline.flow` editor view)
- `twilio`: 37 rows / **13** distinct RPU
- `consulta`: 33 rows / **13** distinct RPU — top offenders: `008970211013` ×9, `096240956737` ×6, `780020900569` ×6
- `mi_espacio`: 12 rows / 12 distinct RPU (already deduped — `mi_espacio_rpu_uk UNIQUE(rpu)`)
- **27 of 33 consulta rows are for RPUs already onboarded in `mi_espacio`** (12 RPUs) → 27 redundant CFE consulta drives.
- `pipeline.flow` (OID 18788) is a **view** joined at twilio grain (`twilio ⟕ consulta ⟕ mi_espacio`), so the "repeated RPU" the owner saw in the editor is the underlying consulta duplication surfacing — not a view bug.

### Guard to implement (both `rpc_advance_twilio` and `rpc_advance_twilio_multi`)
Before inserting a new `pipeline.consulta` row for an RPU, short-circuit if the service is **already onboarded or in flight**:

1. **Already onboarded** — `exists (select 1 from pipeline.mi_espacio where rpu = <rpu>)` → do **not** create a consulta; link the twilio row's `consulta_id` to the existing onboarded record's consulta and set the twilio row to a terminal ack state (see enum note). This is the case option 1 in the description didn't cover — mi_espacio is the authoritative onboarded layer and none of the current RPCs check it.
2. **In flight / already extracted** — a non-terminal consulta row already exists for the RPU (`status not in ('failed')`) → link `consulta_id` to it instead of inserting (original option 1).

`rpc_advance_twilio` (single path) has **no** cross-row guard at all today; `_multi` only guards within the same `twilio_id`. Both need the same helper.

### Enum gap (blocks a clean terminal state)
`pipeline.twilio_status` = `received, extracting, extracted, needs_review, failed` — there is **no** value for "duplicate / already-onboarded ack". Options: add enum value `duplicate` (schema change, cleanest), or reuse `extracted` + `error_class` — but `error_class` has no `ALREADY_ONBOARDED`/`DUPLICATE` member either (`NONE, NO_BARCODE, OCR_FAIL, WAF_BLOCK, CONSULTA_EMPTY, CONSULTA_NAME_MISMATCH, DRAIN_TIMEOUT, ELIMINAR_FAIL, RPC_FAIL, UNKNOWN`). Recommend adding `twilio_status.duplicate` + `error_class.ALREADY_ONBOARDED` so the reaper/flow view can distinguish a dedup ack from a real extraction.

### Refresh path (must not be broken by the guard)
Monthly adeudo refresh is currently HELD. When it lands it must reuse the existing consulta via `consulta_status.refreshing` (already in the enum) rather than a fresh row — the guard's "already onboarded" branch should route a legitimate re-bill into refresh, not silently drop it. Keep this period-aware for later; for now a resend of an already-onboarded RPU = ack/no-op.

### Rollout blocker
`rpc_advance_twilio_multi` currently exists **only** in `ugjqqezqtnjkzxkcqujz` — it is **missing** in staging (`bvhonjmjxbliuqxhrhec`) and in `oioyawhgvazebtarigpc`. Fixing `_multi` alone won't propagate. See the RPC-drift issue for the reconciliation needed before this ships to all envs.


## Comment by NewmanTech27 (2026-07-12T15:12:40Z)

Fix merged to main via #100 (`0c07ec7`): migrations `20260712140000_pipeline_dedup_enums` + `20260712140100_pipeline_dedup_guard` guard `rpc_advance_twilio(_multi)` — resend of an onboarded/in-flight RPU → `twilio_status.duplicate` / `error_class.ALREADY_ONBOARDED`, no new consulta row. Functionally verified on STAGING. Keep open until applied to the remaining envs (blocked on the #90/#99 migration-history repair — see PR #97 comment for the per-env `supabase migration repair` path).

## Comment by NewmanTech27 (2026-07-13T22:05:45Z)

Dedup guard live in ALL envs as of 2026-07-13 (was staging-only): enums + guard applied to develop and prod, verified prosrc contains duplicate/ALREADY_ONBOARDED path. consulta_rpu_uidx enforces at the index level. Follow-up on RPC unification: #134.
