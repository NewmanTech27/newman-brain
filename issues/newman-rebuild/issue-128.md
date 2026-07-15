# #128: CFE throwaway account WAF-degrades under sustained harvest load (deep drains stall)

- State: OPEN
- Created: 2026-07-13T15:28:59Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/128

## Body

Observed: after ~12-15 register→drain→remove cycles in a day, the shared CFE MiEspacio account's XML downloads get WAF-throttled — deep drains (30+ invoices) stall mid-download (`No es posible obtener el Xml`, DRAIN_TIMEOUT), while login/census/scan still work. A single probe after ~1h rest recovered partially (1→18 downloads), but sustained driving re-degraded it within ~20 min.

Implications for the whole-history / batch run (#124): can't blast N deep accounts back-to-back. Need one or more of: aggressive F3 inter-account cool-down pacing, a hard cap on drives/hour, or multiple throwaway accounts to spread load. The removal path is safe throughout (leaked=0 with the re-login fix), so no leak risk — just throughput.

## Comment by NewmanTech27 (2026-07-13T16:52:42Z)

**Refined hypothesis — likely a per-account DAILY download quota, not just a rolling WAF throttle.** Evidence: `968` returned exactly 18 XML on two separate drains an hour apart (identical period set); after ~150+ XML downloaded across the account today, deep drains consistently stall past a similar count regardless of hourly cooldown. This looks like CFE bounding downloadable XML per account per day.

Implication: the remaining deep backfills (780/585, #126) won't complete today no matter the pacing — they need a **fresh day** (quota reset) or a **second throwaway account**. Confirm by re-running 780 tomorrow on an otherwise-idle account and checking whether it exceeds today's ceiling.

## Comment by NewmanTech27 (2026-07-14T22:29:02Z)

## Best-outcome characterization (instrumented drain runs, 2026-07-15)

Ran mini-direct instrumented drains on 780020900569 (grid 96, 32 invoices) with per-download timestamps. Findings:

**1. Harvest must be mini-direct** — login is IP-gated (project_cfe_login_ip_gated / #130). Browser-API/proxy can't authenticate; they only help no-login Consulta. Not codeable-around.

**2. The drain code is correct** — it scanned 32 invoices, filtered 64 pagos (OPC), removed cleanly (`confirmed_removed`, `leaked=0`). No logic problem.

**3. Throughput is a CFE per-IP WAF rate-limit that CUMULATIVELY DEGRADES:**
- Fresh account/IP (053200453456, 3 days ago): **~2.3 XML/min** → 30 invoices in ~13 min.
- Same drain today after ~20 sessions over 3 days: **~0.5 XML/min** (timeline: 1@30s, 2@170s, 3@309s).
- The per-session 5-limit (reset by incognito) is separate and handled; THIS is an IP/account-level rate cap that fresh sessions do NOT reset — only rest does.

**Operational best-outcome:**
- Drive mini-direct on a **rested** account/IP; pace inter-drive cool-down (#119) so it never degrades to the crawl state.
- Treat deep accounts as **resumable**: raw_cfe dedups by sha256+(rpu,period), so a timed-out run's partial persists and the next run continues. Fix shipped: `download_rows` bridge deadline now scales to batch size (was fixed 180s → aborted throttled batches as DRAIN_TIMEOUT).
- For a heavily-degraded account, consider a **second throwaway account** to spread load, or a multi-day rest.

**"Harvest all except manual-review":** the reachable invoices (recent window CFE serves XML for) drain fully on a rested account. The manual-review set = older grid rows CFE no longer serves XML for (the "30 grid rows → 18 downloadable" pattern) — those need manual retrieval, by design.
