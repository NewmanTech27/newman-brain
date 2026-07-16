# Roof tool on Google Maps + Deals auto-cards + recibo panel

**Summary**: /roof migrated Leaflet→Google Maps (drawing rebuilt after Google removed DrawingManager in v3.65), recibo XML viewer added, service addresses backfilled from XML addendas, and the Deals board now auto-creates LLM-briefed cards per arriving invoice.
**Tags**: #newman #tuesday-crm #roof #google-maps #deals #openrouter #recibos
**Created**: 2026-07-16
**Source**: macbook session bf5241e4 (day 2), user jesus

---

## Content
- Google Maps in /roof: browser key `tuesday-browser-maps` (cfe-brain-geo, referrer-locked *.newman.re); mario's key stays server-side (GOOGLE_GEOCODING_KEY). GOTCHA: **Maps JS v3.65 removed DrawingManager** — custom click-to-draw built (two buttons: Dibujar permitida verde / prohibida roja); legacy Marker + places.Autocomplete deprecated-but-working, future migration = AdvancedMarkerElement + PlaceAutocompleteElement.
- Autocomplete must bind to the SIDEBAR input (externalSearchRef) — Enter handled in capture phase to not fight pac selection.
- Debug method that worked: Playwright headless against local dev served as https://local.newman.re:3000 (host-resolver-rules + self-signed cert) to satisfy key referrers — no key edits needed.
- Recibo panel: NO recibo PDFs exist anywhere (Drive = XML only); panel renders XML as summary with DIRECCIÓN DEL SERVICIO; bucket `recibos-roof/<rpu>.xml` (121/131), RLS-gated, no service key on droplet.
- Address backfill: service address ONLY in XML addenda (DIRECC/COLONIA/NOMPOB/NOMEST); FIS_CP is fiscal. 119/131 with address+coords after Google geocoding (rooftop precision); poison fallback coords scrubbed.
- Deals: kanban renamed Deals; trigger on client.bill INSERT extends crm.deal_from_intake(); dedupe = one open deal per account (name variants split accounts — normalization pass pending); briefs via OpenRouter gpt-4o-mini temp 0, DB-numbers-only, "[auto-generado]" suffix; retro-fill 131 RPUs → 36 deals, 36 briefs.
- Env gotcha: /etc/newman-crm.env perms must stay 640 root:deploy (configure-crm-env self-heals); nonprod droplet needs `deploy ALL=(ALL) NOPASSWD:ALL` sudoers one-liner (pending) for its env job.

## Related Notes
- [[2026-07-16-tuesday-roof-review-calculo-buildout]]
- [[2026-07-09-helioscope-roof-sizing-pipeline]]
