# AFCH PPA offer + data room, Steve Jobs design, committee loops, Cloudflare DNS

**Summary**: Built the password-gated AFCH (Alimentos y Franquicias de Chiapas) PPA offer + data room + calculator on GitHub Pages under one repo, iterated with role committees, and wired Cloudflare for the afch.newman.re subdomain.
**Tags**: #newman #ppa #proposal #ui #dataroom #cloudflare
**Created**: 2026-07-05
**Source**: macbook session 61b2faa1-7835-4fbc-a947-93aa3062bede.jsonl, user jesus

---

## Content
- Brief: from the newman-branding-guidelines repo, create a PPA offer following the "Contado BESS - Anahuac" structure, in HTML/CSS/JS "as if Steve Jobs had designed it".
- 4-role committee workflow (sales-closer / engineer / designer / consultant) iterated 6 rounds twice, peaking ~86 (target 95); blocker findings included placeholder contact data — real phone set to +52 1 56 6758 3630.
- Deployment: client-named placeholder subdomain under newman.re via GitHub Pages, password emailed to agents@newman.re; email should come from jesus@ (agents@ is a group).
- Cloudflare adopted for DNS automation instead of Hostinger — added the remote Cloudflare MCP (`https://mcp.cloudflare.com/mcp`).
- Data room expanded: historic price development per zone, forward modeling, YoY/MoM simulation Excel, equipment datasheets; committee flagged kW/capacidad/distribución data missing (only kWh shown) and a 12x understated BESS demand-upside band.
- Final consolidation into one repo `NewmanTech27/afch`: `/afch/` propuesta (password `verde-maya-rio-sierra-35`), `/afch/dataroom/`, `/afch/calculadora/` + `/afch/flujo/` (internal password `nodo-nucleo-forja-flujo-31`); old afch-ppa URL 404s; local source `~/Documents/kfc/`; leftover: DNS for afch.newman.re and deleting archived newman-cascade (needs delete_repo scope).

## Related Notes
- [[2026-07-03-kfc-ppa-offer-workflow]]
- [[2026-07-04-solar-bess-sizing-agent]]
