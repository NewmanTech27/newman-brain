# newman-rebuild — GitHub Issues Map

Mirror of all issues in NewmanTech27/newman-rebuild as of 2026-07-17. Full bodies+comments per issue in `issue-NNN.md`; raw dump in `issues-full.json`.

| # | State | Title | Closed |
|---|-------|-------|--------|
| [1](issue-001.md) | CLOSED | P0: provision clean Supabase project | 2026-07-10 |
| [2](issue-002.md) | CLOSED | P1: schema design — intake/cfe/design/crm | 2026-07-10 |
| [3](issue-003.md) | CLOSED | P1: old-data migration map | 2026-07-10 |
| [4](issue-004.md) | CLOSED | P2: OCR intake — invoice -> RPU + receptor name | 2026-07-10 |
| [5](issue-005.md) | CLOSED | P2: Consulta + MiEspacio harvester on the mini | 2026-07-10 |
| [6](issue-006.md) | OPEN | P2: harvest telemetry + business-error report |  |
| [7](issue-007.md) | CLOSED | P2: sizing + quotation — wrap newman-brain engine | 2026-07-10 |
| [8](issue-008.md) | OPEN | P2: DEALS front — HTML offer from design data |  |
| [9](issue-009.md) | CLOSED | P0: golden test in CI before any sizing code | 2026-07-10 |
| [10](issue-010.md) | OPEN | P0: token discipline baseline |  |
| [11](issue-011.md) | CLOSED | P0: capture ~/newman-sso auth scaffold into the repo (box-only, at-risk) | 2026-07-10 |
| [18](issue-018.md) | OPEN | P2: extract.py XML CONSUMO period-split MISLABELED per division (DW inverted) — CONFIRMED vault engine bug |  |
| [19](issue-019.md) | OPEN | CFE harvester: carry MiEspacio census + name-matching + lock/drain insights into the rebuild |  |
| [21](issue-021.md) | CLOSED | Invoice intake: WhatsApp/Twilio edge function on the new instance | 2026-07-10 |
| [22](issue-022.md) | CLOSED | Barcode decode for RPU + adeudo (intake reliability) | 2026-07-10 |
| [25](issue-025.md) | CLOSED | P2: wire the barcode decoder into the deployed intake pipeline (Python/Deno seam is unwired) | 2026-07-10 |
| [27](issue-027.md) | OPEN | Harden cto-verdict-log schema so ECO-3/ECO-4 are exact, not upper-bound |  |
| [29](issue-029.md) | OPEN | Verify CONSUMO period order for unverified CFE divisions (DX/Jalisco +) |  |
| [32](issue-032.md) | OPEN | Server-side Google hd-claim auth gate for internal *.newman.re pages (replace email-suffix) |  |
| [35](issue-035.md) | OPEN | OpenRouter name-variant fallback for MiEspacio AgregarServicio name-mismatch |  |
| [37](issue-037.md) | OPEN | Interactive web offer + live calculator powered by the design-engine (salesman-adjustable) |  |
| [38](issue-038.md) | CLOSED | Beat Imperva/WAF on the live MiEspacio harvest (census UNREADABLE blocks the drain) | 2026-07-10 |
| [40](issue-040.md) | CLOSED | Port the Consulta-first phase: derive total a pagar + nombre from Consulta BEFORE MiEspacio (the real harvest unblock) | 2026-07-10 |
| [43](issue-043.md) | CLOSED | Census false-positive: authed EMPTY account misread as 'login bounce' (blocked every live register) | 2026-07-10 |
| [44](issue-044.md) | CLOSED | eliminar confirm click threw → service LEFT REGISTERED (charter #7 incident) | 2026-07-10 |
| [45](issue-045.md) | CLOSED | F1 leak-gate false-positive: factura FOLIO read as grid RPU → aborted every drain | 2026-07-10 |
| [46](issue-046.md) | CLOSED | Dedup Consulta ∪ MiEspacio recibos (+ cross-run) by CFDI UUID | 2026-07-10 |
| [48](issue-048.md) | OPEN | Charter scrub: rule on pre-existing Chiapas client RPUs in already-merged harvest files |  |
| [49](issue-049.md) | OPEN | EPIC: Model B pipeline — Supabase-orchestrated Twilio-sync → extract → harvest |  |
| [50](issue-050.md) | CLOSED | Harvest endpoint crashes as a background daemon → service left REGISTERED (leak) | 2026-07-11 |
| [51](issue-051.md) | OPEN | CONSULTA_FAILED: add to business_error enum + route bad-name uploads to human review (no retry-loop) |  |
| [52](issue-052.md) | OPEN | Vision extraction grabs the service ADDRESS instead of the razón social on some invoice formats |  |
| [53](issue-053.md) | OPEN | Phase 4b: wire the 3 pg_cron jobs (twilio-sync / extract / harvest) + SQL stale-claim reaper |  |
| [54](issue-054.md) | OPEN | Extract edge OOMs (WORKER_RESOURCE_LIMIT) — base64 media in memory caps throughput |  |
| [55](issue-055.md) | OPEN | Extraction accuracy harness: labeled ground-truth + precision/recall metric |  |
| [56](issue-056.md) | OPEN | Deterministic barcode (CODE128) RPU cross-check in edge extract |  |
| [57](issue-057.md) | OPEN | Vision RPU confidence gate + DB-level human-review enforcement |  |
| [58](issue-058.md) | OPEN | Enforce ^[0-9]{12}$ on the OCR-path RPU + disambiguate multiple 12-digit runs |  |
| [59](issue-059.md) | OPEN | Fix XML CONSUMO1F/2F/3F division-code ordering (inverted for DW/Peninsular) |  |
| [60](issue-060.md) | OPEN | Extraction deployment/packaging + main-schema completeness |  |
| [61](issue-061.md) | OPEN | Extraction telemetry: RPU accuracy/drift SLA + regression gate |  |
| [62](issue-062.md) | OPEN | Extraction end-to-end integration test + browser-layer Finding port + merge #50 |  |
| [63](issue-063.md) | OPEN | Extraction contract: barcode-authoritative RPU+adeudo, OCR only for receptor_name |  |
| [64](issue-064.md) | CLOSED | Re-architect pipeline: pipeline.{twilio,consulta,mi_espacio} + raw_cfe.{consulta,mi_espacio} (pg_cron cascade) | 2026-07-12 |
| [65](issue-065.md) | CLOSED | pg_cron: claim ONE row per tick (endpoint/WAF throttle) | 2026-07-12 |
| [66](issue-066.md) | CLOSED | pg_cron: per-stage timing columns + pipeline.timing view (cadence optimization) | 2026-07-12 |
| [67](issue-067.md) | CLOSED | Surface the Twilio doc URL (media_url) on pipeline.twilio + pipeline.flow | 2026-07-12 |
| [68](issue-068.md) | CLOSED | Seed pipeline.twilio from the Twilio log (23 media records) | 2026-07-12 |
| [69](issue-069.md) | CLOSED | pipeline.twilio media_url: stable api.twilio.com is correct; CDN URL resolved at fetch (never stored) | 2026-07-12 |
| [70](issue-070.md) | CLOSED | pipeline/extract executor: LIVE on the mini — 23 twilio rows drained (21 barcode → consulta, 2 needs_review) | 2026-07-12 |
| [71](issue-071.md) | OPEN | extract: image (JPEG) support + pdfplumber-first name + sharper OCR prompt (board feedback) |  |
| [72](issue-072.md) | CLOSED | pipeline extract stage WIRED unattended (pg_cron → tunnel → mini) — Model B live | 2026-07-12 |
| [73](issue-073.md) | CLOSED | twilio-sync LIVE → pipeline.twilio: automatic WhatsApp ingestion wired (non-CFE) | 2026-07-12 |
| [74](issue-074.md) | CLOSED | consulta stage LIVE (read-only) — executor built, 3 blockers fixed, cron enabled | 2026-07-12 |
| [75](issue-075.md) | CLOSED | harvest stage executor built + proven live; raw_cfe deduped by (rpu, period) | 2026-07-11 |
| [76](issue-076.md) | CLOSED | pipeline: no auto-retry for failed rows — transient DRAIN_TIMEOUT/WAF sit failed forever | 2026-07-12 |
| [77](issue-077.md) | OPEN | extract/consulta: OCR razón social mismatches CFE registered name → CONSULTA_NAME_MISMATCH |  |
| [78](issue-078.md) | CLOSED | harvest failures mask the real error_class (hardcoded DRAIN_TIMEOUT) + drop detail — undebugable | 2026-07-12 |
| [79](issue-079.md) | OPEN | pipeline: endpoint restart/crash orphans in-flight rows as 'fetching'/'harvesting' zombies (no startup reaper) |  |
| [80](issue-080.md) | CLOSED | reaper recycles COMPLETED consulta rows — 'derived' in stale predicate + advance never clears claimed_at | 2026-07-12 |
| [81](issue-081.md) | OPEN | harvest drain may truncate deep histories — download_all_recibos does not paginate the OtrasFacturas grid |  |
| [82](issue-082.md) | CLOSED | harvest has no single-flight guard — concurrent harvests mutate the shared CFE account | 2026-07-12 |
| [83](issue-083.md) | OPEN | CRITICAL: harvest drain truncates deep grids — grid_rows=97 but bill_count=1 (got newest only) |  |
| [84](issue-084.md) | CLOSED | reaper interrupts live deep harvests (15-min stale < 25-min harvest runtime) → risk of double-harvest | 2026-07-12 |
| [85](issue-085.md) | OPEN | MiEspacio harvest depth: only ~8 recent months captured — pagination advance unverified |  |
| [86](issue-086.md) | OPEN | Deep-account harvest: WAF mass-rejects fetchDrain + eliminar selector timeout |  |
| [87](issue-087.md) | OPEN | Multi-invoice PDF bundles: fan out one consulta row per invoice |  |
| [90](issue-090.md) | CLOSED | Migration-ledger drift: repo migrations cannot reproduce prod (pipeline schema + live RPCs applied via direct psql, unrecorded) | 2026-07-12 |
| [91](issue-091.md) | OPEN | Committed rpc_advance_twilio is stale vs live: single-invoice path does not seed razon_social into pipeline.consulta |  |
| [92](issue-092.md) | CLOSED | pipeline.consulta: cross-upload duplicate RPUs — same invoice uploaded N times creates N consulta rows (observed live: 6× for one RPU) | 2026-07-13 |
| [93](issue-093.md) | OPEN | twilio-sync edge function is LIVE but its source is not in the repo |  |
| [94](issue-094.md) | OPEN | CI runs zero harvest tests: 15 pytest files (~3.4k lines) have no workflow; migrations also unvalidated in CI |  |
| [95](issue-095.md) | OPEN | Dev/staging Supabase branches clone real prod data: no PII scrub, retention, or access policy for lower environments |  |
| [96](issue-096.md) | OPEN | ocr_identify: payment-form layout dumps whole-page text as receptor_name → guaranteed CONSULTA_NAME_MISMATCH |  |
| [99](issue-099.md) | CLOSED | pipeline: RPC + schema drift across Supabase envs — rpc_advance_twilio_multi exists only in prod-URL project, missing in staging + oioya | 2026-07-13 |
| [101](issue-101.md) | CLOSED | Live system is a two-way fork: mini executor code and Supabase migrations live on divergent unmerged branches | 2026-07-12 |
| [102](issue-102.md) | OPEN | Mini executor launchd job runs from a disposable git worktree with no restart runbook — reboot recovery is one rm -rf from silent outage |  |
| [103](issue-103.md) | OPEN | No alerting when the pipeline stalls: pg_cron → pg_net is fire-and-forget, responses discarded, no watchdog |  |
| [104](issue-104.md) | OPEN | Harvest runtime depends on two unpinned external checkouts and an unlocked flake — environment not reproducible from this repo |  |
| [105](issue-105.md) | OPEN | Supabase anon key JWT committed in newman-sso login page while the sibling env template redacts the same value per charter §6 |  |
| [106](issue-106.md) | OPEN | pipeline.* and raw_cfe.* tables ship with zero RLS, breaking the 'RLS from day one' charter rule every earlier schema follows |  |
| [107](issue-107.md) | OPEN | No backup/DR strategy evidenced: raw CFE harvest corpus and pipeline state exist only in one Supabase project |  |
| [108](issue-108.md) | OPEN | .gitignore is one line; untracked .claude/ worktree with a full repo copy sits permanently dirty in the working tree |  |
| [112](issue-112.md) | OPEN | Pipeline dev branch can't run standalone — orchestration points at prod |  |
| [113](issue-113.md) | OPEN | Harvest stores non-invoice CFDIs (Complemento de Pago, TipoDeComprobante≠I) — filter to invoices only |  |
| [114](issue-114.md) | CLOSED | pipeline.consulta: enforce unique RPU (dedup + unique index + conflict-safe advance RPCs) | 2026-07-13 |
| [115](issue-115.md) | OPEN | Twilio media retention: sync can only pull the current window (36 inbound media msgs) |  |
| [117](issue-117.md) | OPEN | Extract stage reprocesses rows (re-claim loop) — needs attempt cap / dead-letter bound |  |
| [118](issue-118.md) | OPEN | Market data plane: CFE tariffs + CENACE PML (P3 backfill + live batch extraction via pg_cron) |  |
| [119](issue-119.md) | OPEN | Harvest: back-to-back sequential drives trip CFE WAF (deep-history drain rejected, 0 recibos) |  |
| [121](issue-121.md) | OPEN | Deep-drain capture gap: 92 grid rows → 81 XML (missing Feb-2026 invoice on 053200453456) |  |
| [122](issue-122.md) | OPEN | Benchmark CFE_DRAIN_PARALLEL: is the XML throttle per-session or per-IP? |  |
| [123](issue-123.md) | OPEN | Harvest: download only invoice rows at the grid (skip Complementos de Pago during drain) |  |
| [124](issue-124.md) | OPEN | Pipeline: full-history batch run (process all pipeline.twilio rows end-to-end) |  |
| [126](issue-126.md) | OPEN | 3 accounts have truncated invoice history in prod (old drain) — re-harvest with deep drain to backfill |  |
| [127](issue-127.md) | CLOSED | Mini executor crashes spawning harvest_one when Nix GC unlinks the devshell python mid-session | 2026-07-15 |
| [128](issue-128.md) | OPEN | CFE throwaway account WAF-degrades under sustained harvest load (deep drains stall) |  |
| [130](issue-130.md) | OPEN | Spike: 2captcha Browser API (cloud browser) vs mac-mini Chrome for CFE harvest WAF stability |  |
| [132](issue-132.md) | OPEN | Invoice = XML + PDF: only return/store recibos that have BOTH files |  |
| [134](issue-134.md) | OPEN | rpc_advance_twilio: unify conflict-safe insert (20260712110000) with dedup guard (20260712140100) |  |
| [135](issue-135.md) | OPEN | Consulta status regression: adeudo-refresh BridgeTimeout clobbers 'derived' rows |  |
| [136](issue-136.md) | OPEN | Bridge op=consulta goes silent past deadline on mini (:8791) |  |
| [137](issue-137.md) | OPEN | Leaked MiEspacio services: auto-requeue eliminar in later rounds |  |
| [141](issue-141.md) | CLOSED | Executor deploy drift: mini ran a 51-commits-behind CI branch | 2026-07-14 |
| [142](issue-142.md) | OPEN | Cross-env cron duplication: develop/staging clones drive the same mini as prod |  |
| [143](issue-143.md) | OPEN | Harvest executor observability: worker logs are HTTP access lines only |  |
| [147](issue-147.md) | OPEN | 2captcha Browser API can't speed the drain as-is: download-path + WAF-vs-throttle mismatch |  |
| [151](issue-151.md) | OPEN | Source-of-truth: SAT Descarga Masiva can't replace the CFE harvest (sizing data is in CFE's Addenda) |  |
| [156](issue-156.md) | CLOSED | Harvest executor loses partials on timeout → pipeline can never complete a deep account | 2026-07-15 |
| [157](issue-157.md) | OPEN | calculo P1: CFDI XML parser (parse_bill_xml port) + Python↔JS parity harness |  |
| [158](issue-158.md) | OPEN | calculo P2: migration — extend crm.bill + new calculo schema (oferta per RPU) |  |
| [159](issue-159.md) | OPEN | calculo P3: cfe-calculo edge function + pg_cron (raw XML → crm.bill → oferta per RPU) |  |
| [160](issue-160.md) | CLOSED | calculo P4: backfill + promote develop→staging→prod + docs | 2026-07-15 |
| [168](issue-168.md) | OPEN | calculo P5: real PV yield from bill CODIGO_POSTAL (kill the flat-1800 assumption) |  |
| [169](issue-169.md) | OPEN | calculo P6: DIVISION code → división map (SIN/BC/BCS) + BCS caveat flag |  |
| [170](issue-170.md) | OPEN | calculo P7: per-RPU config (giro, overrides) — graduate offers past prefeasibility |  |
| [171](issue-171.md) | OPEN | calculo P8: roof-cap the PV sweep via the Helioscope route (address → kWp cap) |  |
| [172](issue-172.md) | OPEN | rates P1: automate CFE published GDMTH cuotas (mini-side monthly scrape) — nobody has this today |  |
| [173](issue-173.md) | OPEN | calculo P9: offer consumer — expose design.current_offer (review UI / Monday / solucion-deck) |  |
| [174](issue-174.md) | OPEN | calculo P10: GDMTO/PDBT flat-tariff support — 8 of 12 prod RPUs have no offer |  |
| [175](issue-175.md) | OPEN | docs: sync stale golden numbers in CFE Brain cfe_savings/README (mario's vault) |  |
| [180](issue-180.md) | OPEN | rates P2: misbilling detector — bill-derived rates vs published cuotas |  |
| [181](issue-181.md) | OPEN | rates P3: operationalize cuotas — monthly scrape job + promotion + prod cp backfill |  |
| [193](issue-193.md) | OPEN | Migration drift: DBs run 20260715* migrations that exist on no git branch |  |
