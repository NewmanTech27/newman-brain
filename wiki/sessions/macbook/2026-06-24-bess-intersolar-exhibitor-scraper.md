# BESS/Intersolar exhibitor scraper + enrichment on mac mini

**Summary**: Built an SSH agent on the mac mini that scraped and enriched the full Intersolar exhibitor directory (2,682 companies) into Postgres, targeting top BESS players.
**Tags**: #newman #bess #scraper #warehouse
**Created**: 2026-06-24
**Source**: macbook session 18642cb0-68b6-4b45-985b-8173bb8b827b.jsonl, user jesus

---

## Content
- Goal: automate procurement-datasheet harvest from top BESS brands; China dominates ~90% LFP cell supply.
- Biggest players named: CATL (#1, Tener/EnerOne/EnerC), BYD (#2, Blade / MC Cube), EVE Energy (314Ah), Hithium (314/587Ah), tier-2: REPT, Gotion, CALB, Sunwoda, Envision AESC.
- Agent on the mini (SSH-able) extracts datasheets and organizes into existing Postgres DB; roles: data engineer, warehouse expert, professional scraper.
- `/loop` scraped exhibitors by priority/importance; ran agentic CATL enrichment with a 14b Ollama model.
- Final directory: 2,682 rows × 15 columns — 2,497 sites done, 331 named reference persons, 1,565 LinkedIn (58%), 2,519 clean emails (94%), 2,272 E.164 phones (85%).
- Columns: priority, company, segment, product_groups, reference_person, person_role, contact_email, all_emails, phone, linkedin, website, country, booth, booth_m2, description.
- Output Sheet (jesus@lopac.mx Drive, anyone-with-link): docs.google.com/spreadsheets/d/1qzzzXFnfaMvUEbw4g3IV51Re4z5c-3L2
- Gotcha: openpyxl choked on control chars in descriptions — had to sanitize illegal chars before rebuild.
- Only authed rclone account was jesus@lopac.mx; newman.re move deferred.

## Related Notes
- [[2026-07-05-monday-intersolar-board-contacts]]
- [[2026-06-24-datasheet-scraper-agent-kickoff]]
