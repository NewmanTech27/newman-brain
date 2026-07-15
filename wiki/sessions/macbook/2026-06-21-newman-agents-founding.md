# Founding the newman-agents AI company and CFE/CENACE data backfill

**Summary**: Kicked off the Newman Energy agent company (compete vs Enlight/Quartux), built the CFE tariff scraper + OCR pipeline plan, and started the decade-long CENACE PML backfill on the mac mini.
**Tags**: #newman #agents #scraper #cfe #cenace #warehouse #ocr
**Created**: 2026-06-21
**Source**: macbook session d8818f45-bac6-4eb3-910e-5cdb6ed1751e.jsonl, user jesus

---

## Content
- Founding prompt: create an agent company to compete against Enlight, Quartux etc.; scrape all historic CFE prices, build an Enlight-like landing with webapps, use Rory Sutherland persuasion doctrine, and automate bill intake (rclone Drive watch → n8n → ollama llava OCR → qwen sanity-check → PPA savings report).
- Repo `~/newman-agents` with `docs/CHARTER.md` as the COO-loop source of truth; autonomous build loop via ScheduleWakeup, commits on `sprint-0-foundation`.
- CFE tariff pipeline: manifest of DOF/CENACE monthly acuerdo PDFs back to 2018; 98 PDFs downloaded and parsed/loaded on the mini into Postgres `newman` at 127.0.0.1:5433 (1,810 rows for 2025-09 at one checkpoint). ≤2023 PDFs have a different layout (parser variant pending; browser-use suggested).
- n8n stood up via nix-darwin (`darwin-rebuild switch --flake ~/ai-station#ch-lopac`, port 5678, Docker) after several Nix errors.
- OCR pipeline built + verified: `automation/ocr/extract_bill.py` with qwen2.5vl; blocked on a real CFE bill sample for accuracy validation.
- CENACE PML ingest: MDA zonal data, then a decade backfill launched — 1.2M+ MDA rows spanning 2016-02→present at checkpoint (2016 = complete year; MEM launched Feb 2016), MTR after MDA.
- Ambition set: clean-room clone of https://euenergy.live/ for the Mexican market across all tarifas (mxenergy frontend agent attempted, stalled).
- Also asked for: solar/wind resource data by lat/lon mapped to postal code, and household (domestic) tariffs.

## Related Notes
- [[2026-07-06-pml-supabase-migration]]
- [[2026-06-24-qwen36-mini-bakeoff]]
