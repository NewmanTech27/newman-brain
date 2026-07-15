# Chiapas CFE invoice harvest: full-depth MiEspacio drains, gws auth, harvest gotchas filed as issue #19

**Summary**: Authenticated gcloud/gws for jesus@newman.re, then harvested all historical CFE invoices (not just 12 months) for the Chiapas lead RPUs via MiEspacio, debugging census/eliminar fixes and filing the harvest gotchas as newman-rebuild issue #19.

**Tags**: #newman #cfe #harvest #scraper #gws #rebuild
**Created**: 2026-07-10
**Source**: mini session 9c476cd3-1fb7-4fd9-8008-e4f9c749983a.jsonl, user jesus

---

## Content
- Confirmed gh auth as tech@newman.re (NewmanTech27), then authenticated Google Cloud + gws CLI tools for jesus@newman.re via OAuth loopback flows; decided GAM was not needed ("with the first one we have enough").
- Located Chiapas lead invoices under `00_Leads` on the Dataroom shared drive; counted XMLs; pulled counts from legacy Supabase via ssh droplet-jesus (told not to waste time hunting for the MCP token).
- Harvested RPU **679220758161** first for 12 months, then re-ran full-depth per Jesus: "we should harvest all the invoices, not only the last 12" — MiEspacio gives full history; Consulta caps at ~6.
- Multiple relaunches needed: census fix for empty-account blocker, then an "eliminar" (service removal) fix validated on fresh-login harvests of 671071116338, 671140638635, 744931031693; remaining 3 Chiapas RPUs harvested sequentially with the fix.
- Filed **NewmanTech27/newman-rebuild issue #19** with 6 harvesting insights: empty-account census blocker (root cause), Consulta 6-cap vs MiEspacio full history, titular name-matching uses raw `<NOMBRE>` not razón social, `cfe_lock` leak on external kill, drain-budget scaling, and the KC/K9/KX document taxonomy; patched `gridState()` from `agents/cfe-collector` added as a comment; standing instruction to keep appending findings to #19.
- Session tail moved to front-end↔CLI integration: reconciled the "Generar PDF" JSON schema — front-end changed to emit the CLI's exact param schema (`ppa_tariff`, `term`, `esc_ppa`, `commercial_model`, `kwp_override:{rpu:kwp}`) instead of building an adapter.

## Related Notes
- [[newman-invoice-collector]]
- [[cfe-consulta-name-match]]
- [[gws-cli-project]]
- [[2026-07-10-ceo-rebuild-orchestration]]
- [[2026-07-12-miespacio-xml-drain-rate-limit]]
