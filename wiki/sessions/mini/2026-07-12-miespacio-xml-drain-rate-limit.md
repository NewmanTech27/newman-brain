# MiEspacio XML drain tuned past CFE's ~5-download rate limit (v2→v5 harvest iterations)

**Summary**: Iteratively tuned the MiEspacio full-history XML harvester against CFE's "No es posible obtener el archivo Xml" popup rate limit — pacing between downloads, dismiss-popup-and-retry logic, scroll-to-load-more — across v2–v5 runs on a 92-invoice RPU, then merged migration promotions and PR #184 at session end.

**Tags**: #newman #cfe #harvest #scraper #rebuild #rate-limit
**Created**: 2026-07-12
**Source**: mini session 84fb5676-af1f-40be-9f45-043130c60979.jsonl, user jesus

---

## Content
- Started by reviewing prior MiEspacio extraction work, then ran a live harvest on a stable RPU (053200453456) — hit CFE error popup "No es posible obtener el archivo Xml en este momento, intenta de nuevo más tarde".
- Jesus's observations drove the fixes: (1) invoice list lazy-loads — must scroll down to expose the rest (target RPU had **92 invoices**, v2 initially captured 0); (2) rate limit appears to be **~5 downloads** before the popup; (3) clicking the popup's dismiss button clears it immediately — no long wait needed afterward; (4) the XML that triggered the popup must be retried.
- Harvest versions: v2 (drain, stalled at 0), v3 (wait period between downloads — slow but climbing 1,2,3,4), v4 (fast-tuned: click popup + retry — reached 10+ quickly), v5 (full drain from scratch toward 92); manual click confirmed working, MiEspacio re-run from scratch requested.
- Requested XMLs copied to Desktop for manual inspection.
- Monitor-based background runs with push-notification-worthy event filtering used throughout to watch capture counts.
- Session end shifted to repo ops on newman-rebuild: migration promotion merged, `supabase-migrations` workflow green on main, all 3 migrations verified on prod; PR **#184** (twilio commit) rebased onto updated main and force-pushed for CI re-run.

## Related Notes
- [[newman-invoice-collector]]
- [[2026-07-10-chiapas-cfe-invoice-harvest]]
- [[newman-architecture-project]]
