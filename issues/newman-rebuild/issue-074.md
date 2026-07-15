# #74: consulta stage LIVE (read-only) — executor built, 3 blockers fixed, cron enabled

- State: CLOSED
- Created: 2026-07-11T15:16:04Z  Closed: 2026-07-12T12:28:17Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/74

## Body

## Done — consulta stage proven live + cron enabled (harvest still held)

Board: "enable the cron for consulta and harvest" → chose consulta-first.

### Built
- **`consulta_one.py`** — the /pipeline/consulta executor child (was missing entirely). Read-only CFE Consulta (`CfeDriver.consulta_latest`) on a throwaway context → authoritative razón + adeudo + latest period from the newest recibo + every captured recibo XML (sha256/period/serie_folio/uuid) for `raw_cfe.consulta`. Reduction unit-tested; injectable `run`.
- CFE creds (`TWOCAPTCHA_KEY`, `CFE_USER/PASS`) added to `~/.newman-pipeline.env`; endpoint restarted.

### 3 blockers found + fixed live
1. **`rpc_fail_stage` enum cast** — the status `CASE` resolved to `text`; every stage's failure path errored `42804`. Fixed with explicit `::pipeline.*_status` casts. (`20260711280000`)
2. **`rpc_advance_twilio` dropped the name** — it inserted the consulta row as `(status, twilio_id, rpu)`, never copying the OCR'd `receptor_name` → `razon_social`. Every consulta failed `CONSULTA_NAME_MISMATCH` ("no name candidates"). Fixed + backfilled the 21 existing rows. (`20260711290000`)
3. Consulta cron enabled (`20260711300000`); trimmed out of the phase-2 CFE hold.

### Verified live (consulta_id 2)
`fetching → derived` in ~77s: **adeudo 281439**, **period 202606**, razón matched, **8 recibos** stored in `raw_cfe.consulta` (sha256-deduped), **1 `pipeline.mi_espacio`** cascade row created.

### Live cron topology (5 stages, harvest held)
| job | schedule | CFE? |
|---|---|---|
| pipeline-twilio-sync | */5 :00 | no (edge pull) |
| pipeline-extract | :01 | no (barcode/OCR) |
| pipeline-consulta | :02 | **yes, read-only** |
| pipeline-reaper | :04 | no |
| ~~pipeline-harvest~~ | held | yes, register/eliminar (#50) |

The 20 remaining pending consulta rows will drain ~1/tick. Next: build/port `harvest_one` + careful live test before enabling harvest.

Commits: `pipeline/executors` (consulta_one), `pipeline/schema` (fixes + cron). Pushed.

## Comment by NewmanTech27 (2026-07-12T12:28:16Z)

Closing per INT-1. Artifacts: `bd4425d`, `034106f` — consulta executor built, 3 blockers fixed, cron enabled (live, read-only). Branch → main merge tracked in #101.
