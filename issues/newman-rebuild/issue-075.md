# #75: harvest stage executor built + proven live; raw_cfe deduped by (rpu, period)

- State: CLOSED
- Created: 2026-07-11T16:09:42Z  Closed: 2026-07-11T16:24:20Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/75

## Body

## Done — harvest executor built, #50 fixed, raw_cfe dedup tightened

Board: "fix 50 then build test" (harvest) + "assign the raw_cfe unique id when created so [dup months] don't happen".

### Built
- **`harvest_one`** — the /pipeline/harvest child: full CONSULTA→login→census→add→drain→remove for one RPU, reduced to the executor contract (recibos w/ xml+sha256+meta, xml/pdf/bill counts, months, leaked, timings, state harvested|partial|failed).
- **`safe_cleanup`** — ported; fresh-session eliminar. Wired into the executor: any non-clean harvest triggers it (the #50 belt).

### Fixed
- **#50** (closed): bridge read deadline + safe_cleanup → a wedged/killed harvest can't strand a service.
- **raw_cfe dedup by (rpu, period)** (`20260711310000`): unique (rpu, period) on raw_cfe.{consulta,mi_espacio}; store RPCs conflict on it → a re-issued recibo (same month, new sha256) reuses the first row's id instead of double-storing. Verified: 2nd store of same (rpu,period) w/ different bytes → same id 89.

### Live harvest result (mi_espacio_id 1, RPU …013)
Drained **8 months** (202511–202606) into `raw_cfe.mi_espacio`; in-drive eliminar VERIFY_FAILED → state=partial; safe_cleanup **confirmed_removed** → no strand.

### Not enabled yet
`pipeline-harvest` cron still HELD. Harvest proved out, but it mutates the live CFE account (register/eliminar) — enabling unattended awaits explicit CEO go. Note: the harvest queue still has multiple rows per RPU (5× for one RPU); with the raw_cfe (rpu,period) dedup those redundant harvests now produce no duplicate data, but they still do redundant CFE work — a per-RPU queue dedup is a possible follow-up.

## Comment by NewmanTech27 (2026-07-11T16:24:19Z)

## Harvest cron ENABLED — full pipeline live end-to-end

Per-RPU queue dedup + harvest cron done (board: "a").

- **Per-RPU dedup** (`20260711320000`): MiEspacio drains an RPU's full history in one drive, so multiple invoices for the same RPU no longer queue redundant register/eliminar cycles. Collapsed the existing dups (11 rows → 3, one per RPU: kept the harvested survivor, re-pointed 4 consulta links), added `UNIQUE(rpu)`, and `rpc_advance_consulta` now `ON CONFLICT(rpu) DO NOTHING` (links the existing harvest row).
- **Harvest cron enabled** (`20260711330000`): `pipeline-harvest` at :03, live but strand-safe after #50 (BridgeTimeout + safe_cleanup).

### All 5 stages active
| job | :mm | stage |
|---|---|---|
| twilio-sync | :00 | Twilio pull → pipeline.twilio |
| extract | :01 | barcode RPU + OCR razón → pipeline.consulta |
| consulta | :02 | authoritative razón + adeudo → pipeline.mi_espacio |
| harvest | :03 | MiEspacio full history → raw_cfe.mi_espacio |
| reaper | :04 | release stale claims |

Only the monthly adeudo-refresh remains held (`20260711250000`). Closing.
