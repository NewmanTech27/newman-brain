# CENACE veteran review of PML WebForms scraping method (6/10)

**Summary**: A CENACE market-ops persona scored the ASP.NET WebForms PML scrape approach 6/10 — mechanics fine, market-selection and timezone discipline missing.
**Tags**: #newman #cenace #pml #scraper #eval
**Created**: 2026-07-03
**Source**: macbook session 39ed2f37-9da3-4632-8791-fdd2f52824c5.jsonl, user jesus

---

## Content
- Method reviewed: GET page for __VIEWSTATE/__VIEWSTATEGENERATOR/__EVENTVALIDATION; look for direct CSV/ZIP endpoints bypassing postback first; else POST full form with httpx + session cookies + Referer; save raw file stream, never parse HTML tables; chunk date loops (~31-day CENACE limit), throttle 1-2s, backoff on 5xx.
- Issue: no explicit MDA vs MTR market selection before submit.
- Issue: no node-ID validation against the CENACE NodosP catalog — typo yields silently wrong node.
- Issue: no handling of hora 1-25 DST edge; should cross-check row count per date.

## Related Notes
- [[newman-agents-review-committee]]
