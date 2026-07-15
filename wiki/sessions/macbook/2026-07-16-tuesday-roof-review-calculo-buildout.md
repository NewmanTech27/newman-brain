# Tuesday CRM: reset, 4-feature buildout, roof→design→calculo chain live

**Summary**: Two-day session that decommissioned monday.com, reset Tuesday to SSO-only, shipped the 4 kept features (Pipeline, ToDos, Review, Roof), wired roof measurements into the calculo engine (helioscope module-fit, TIR-19% objective, solar-charge dispatch), and backfilled service addresses from recibo XML addendas.
**Tags**: #newman #tuesday-crm #roof #calculo #helioscope #review #security #infra
**Created**: 2026-07-16
**Source**: macbook session bf5241e4 (this wiki's mining session), user jesus

---

## Content
- monday.com decommissioned: full export in [[crm/monday-export]] (70 boards, 3,138 items); newman-rebuild issues mirrored; this wiki created (105 session notes + 12 topics).
- Tuesday reset: all 147 crm.* tables truncated (backup crm/tuesday-backup-2026-07-15/), login = Google SSO "Welcome to Tuesday", legacy modules stripped; navbar = Pipeline, ToDos, Revisión facturas, Techos.
- Services decommissioned per keep/kill list; droplet newman-crm-nonprod destroyed then REBUILT properly (137.184.19.31) as dev+staging envs: dev-tuesday/staging-tuesday.newman.re, branches develop/staging, per-env Supabase branch DBs. Promotion: feature → develop → staging → dev (prod git branch is called `dev`!). Manual pending: GCP OAuth redirect URIs for branch callbacks.
- /review: ported from newman-review (vps service retired, review.newman.re 301s); sha256 media dedupe on pipeline.twilio (18 dupes found, queue 4→0); env gotcha: app reads TWILIO_ACCOUNT_SID/AUTH_TOKEN.
- /roof: leaflet draw allowed/forbidden → Tongwei 715W per-plane module fit (packing 0.75, faithful helioscope port) → design.roof_fit (oioy) + crm.rpu_config.pv_kwp_override → hourly cfe-calculo re-queue via rpu_config.updated_at hash. Adversarial audit found 5 defects (registry mismatch 6/131, swallowed sync failure, zero-kWp poison, false queued, overlap double-count) — all fixed; RPUs auto-register.
- Address backfill: service address ONLY exists in recibo XML addenda (DIRECC/COLONIA/NOMPOB/NOMEST); FIS_CP is FISCAL, never service. 2,455 Drive XMLs parsed → 119/131 candidates with address, 99/131 with coords; poison fallback coords scrubbed.
- Engine economics: solar-charge dispatch ported golden-gated (18/18 bit-identical pre-flag; +$911k/yr on 10× variant); PPA objective = deal-solved bisection @ TIR 19% (pipeline.config ppa_target_irr); fleet recompute deliberately NOT triggered — pull calculo_generation bump to re-offer all RPUs.
- Generar propuesta: solucion-deck v5 deck from crm.bill + design.current_offer, /propuesta/<id>, Drive outbox → Dataroom_Newman/Leads/<Client>; demo shipped for PRODUCTOS CHACHITOS.
- Security: RLS fixes, 194 crm_web_* RPCs gated with crm.assert_newman(), auth hook function ready (dashboard toggle pending), search_path pinned, legacy plaintext Twilio env shredded.
- Golden RPU 780881200029 (GRUPO POSADAS) is in the roof picker — do not measure it casually; it re-prices the reference offer.

## Related Notes
- [[2026-07-15-monday-decommission-newman-brain]]
- [[roof-design-calculo-flow]] (docs/)
- [[2026-07-09-helioscope-roof-sizing-pipeline]]
- [[2026-07-14-gepp-solar-charge-bess-dispatch]]
