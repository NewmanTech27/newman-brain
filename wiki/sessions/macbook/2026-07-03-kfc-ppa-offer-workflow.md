# KFC front-to-back: CFE invoices → solar+BESS sizing → PPA offer on Pages

**Summary**: Proved the full pipeline on the KFC folder — invoice extraction, PV+BESS sizing, PPA financials, committee-reviewed HTML offer — culminating in the live kfc-report Propuesta v2 in Anáhuac format.
**Tags**: #newman #ppa #bess #cfe #proposal #workflow #supabase
**Created**: 2026-07-03
**Source**: macbook session da0103f0-fb0c-4965-98bb-1cafab135f34.jsonl, user jesus

---

## Content
- Task: from `~/Documents/kfc` invoices, extract CFE data and generate a solar+BESS PPA offer in HTML/CSS/vanilla JS, iterating until the logic works front to back; all client work saved to the Dataroom_Newman shared drive (Leads/KFC folder id `1LIbd84tYYo5k0DVei5m9XCJ-WDgnXqA2`).
- Dynamic workflow (14 agents) produced per-site results: KFC Plaza Bella (GDMTO, 19,120 kWh/mo, 106.14 kWp, 30 kWh BESS, $134,852 yr1), KFC Boulevard (125.28 kWp, $168,977), KFC Centro (GDMTH, 110.2 kWp + 86.4 kWh, $225,085, 27.9%), Pizza Hut Oriente (63.8 kWp, $103,724); portfolio yr1 savings $632,638 MXN.
- WhatsApp intake explored: contacts share PDFs in group "Newman Power alliance" (WhatsApp on Brave on the mini + Chrome extension).
- Connected the Supabase MCP (project bwudgrwfwjdbvqhgbwty); read CFE Brain on Drive to learn how equipment data is used.
- Rebuilt the offer to match the "Propuesta PPA Universidad Anáhuac" PDF format with Brain doctrine + committee review loop (12 agents, 2 rounds + final pass).
- Final live: https://newmantech27.github.io/kfc-report/ — portfolio 405.4 kWp + 186.4 kWh BESS, 82.2% coverage, PPA 28% discount over generation, 144 months with asset transfer end of year 12, yr1 savings $617,856 MXN, 20-yr $62.2M MXN, Newman reference investment $437,341 USD.
- Open business decision: with PPA-on-generation at 28% and 82% coverage, yr1 savings mathematically cap ~24% — the Anáhuac PDF's 35–55% band implies a different structure (>40% discount, oversized generation with net billing, or PPA on autoconsumo).
- Also drafted the full CFE bill-scraper agent spec (3 input modes: direct RPU/servicio/total, invoice file, photo OCR; Phase 1 = Consulta without login).

## Related Notes
- [[2026-07-04-cfe-invoice-harvest-supabase]]
- [[2026-07-04-solar-bess-sizing-agent]]
- [[2026-07-05-afch-ppa-offer-dataroom]]
