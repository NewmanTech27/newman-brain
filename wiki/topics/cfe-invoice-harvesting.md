# CFE Invoice Harvesting (Consulta + MiEspacio)

**Summary**: Everything durable about pulling CFDI XML/PDF invoices out of CFE's portals — the Consulta/MiEspacio two-path architecture, the pseudo-API postback trick, the 10-recibo permaban, rate limits, name-matching, and the identity-field domain rules (RPU vs RMU).
**Tags**: #newman #cfe #harvest #scraper #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### The two paths
- **Path A — Consulta** (`app.cfe.mx/Aplicaciones/CCFE/ReciboDeLuzGMX/Consulta`): login-free, zero-risk, gives the latest recibo (importe, no. de servicio, RPU) but caps at ~6 months of history. Requires the **EXACT account name** — blank → "campos obligatorios", wrong → "no coincide". Titular matching uses the raw `<NOMBRE>` from the CFDI (not razón social), and CFE wants the canonical form (`SA DE CV`, not `S.A. DE C.V.`). RPU-only intake therefore cannot drive the portal — OCR must read the exact name off the bill.
- **Path B — MiEspacio** (`Login.aspx`): the Consulta "total a pagar" is the credential to register a service; "Administrar recibos → Consulta tu recibo → Otras facturas" yields full history (~30 months, up to 92 invoices seen on one RPU). Captchas solved via 2captcha.

### Hard limits and invariants
- **10-recibo permaban**: CFE permanently blocks accounts with >10 registered recibos. Non-negotiable invariant: register → drain → **eliminar servicio** (delete must run even on partial failure); startup reconciliation deletes orphan receipts by identity (RPU/No.Servicio match, not count); the counter is cumulative across sessions — keep a persistent ledger.
- **XML download rate limit**: ~5 downloads before the popup "No es posible obtener el archivo Xml en este momento". Fix (v4/v5 harvester): click the popup dismiss (clears immediately), retry the failed XML, no long wait needed. Invoice list lazy-loads — must scroll to expose all rows.
- **Consulta sweep pacing**: 18s between RPUs eliminated the 58% UNKNOWN failure rate on the 76-RPU Yazaki sweep (~2.5h total). Residual skips are genuine NAME_MISMATCH.
- **WAF**: Imperva at app.cfe.mx needs headless Chrome with automation flags hidden + a Mexican **residential IP** (the mac mini) — datacenter IPs always dropped, so GitHub-hosted CI can't run it (self-hosted mini runner instead).

### Pseudo-API
- CFE has no REST API (legacy ASP.NET WebForms), but `__doPostBack` is replayable as raw HTTP POSTs (cookies + `__VIEWSTATE` + `__EVENTTARGET`). One `fetchDrain` in `harvest.js` unifies Consulta + MiEspacio drains (newman-architecture PR #5). If ≤12 invoices result, drain BOTH paths.

### Identity fields (load-bearing domain rules)
- **RMU** is the printed-twice field on the paper bill (cross-check both prints); **RPU** is authoritative only from the acquired XML (usually unlabeled/partial on print, clean RPU ~12 digits). Confusing them was the lowest committee score (5/10). Portal keys = no_servicio + RMU.
- OCR discipline: never guess digits; RMU-print mismatch → needs_human; check for embedded XML in the PDF before burning vision OCR; per-field confidence thresholds (XML 0.95+, text-PDF 0.85+, vision 0.6+).
- SAT descarga masiva **cannot** replace the harvest — the needed data lives in CFE's CFDI Addenda, not SAT.

### Operational gotchas (newman-rebuild issue #19)
Empty-account census blocker; Consulta 6-cap vs MiEspacio full history; raw `<NOMBRE>` titular matching; `cfe_lock` leak on external kill; drain-budget scaling; KC/K9/KX document taxonomy. Standing instruction: keep appending harvest findings to issue #19.

## Related Notes
- [[2026-07-04-cfe-invoice-harvest-supabase]]
- [[2026-07-07-cfe-miespacio-harvest-pseudo-api]]
- [[2026-07-14-newman-rebuild-miespacio-phases]]
- [[2026-07-10-chiapas-cfe-invoice-harvest]]
- [[2026-07-12-miespacio-xml-drain-rate-limit]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-03-review-billing-miespacio-invariant]]
- [[2026-07-03-review-billing-photo-pipeline]]
- [[2026-07-03-review-security-miespacio]]
- [[2026-07-03-review-ocr-text-layer]]
- [[2026-07-03-review-qa-photo-pipeline]]
- [[2026-07-03-agent-committee-reviews-ppa-cfe]]
- [[2026-07-07-newman-architecture-cleanroom-deploy]]
