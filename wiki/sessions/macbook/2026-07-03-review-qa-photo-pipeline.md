# QA-gate review of photo-to-consumption pipeline (7/10)

**Summary**: A QA-engineer persona flagged missing idempotency and tariff-staleness checks in the blurry-photo ingestion pipeline.
**Tags**: #newman #cfe #qa #eval #agents
**Created**: 2026-07-03
**Source**: macbook session 46a0d3d5-698b-4dbf-8671-565f11317910.jsonl, user jesus

---

## Content
- Same pipeline as the billing-specialist review: rpu-extractor (qwen2.5vl vision, automation/ocr/extract_bill.py, confidence score, needs_human on low confidence) then cfe-bill-scraper Path A/B.
- Issue: visible think-out-loud false starts ("wait—we don't have RPU yet") — output not sign-off clean.
- Issue: no dedupe/idempotency for re-submitted customers — re-runs risk double-counting history and re-triggering Path B add/delete against the 10-receipt cap.
- Issue: verification gate covers fabrication but not staleness — no check that fetched CFDI tariff_code/period aligns with the current DOF acuerdo before handoff to savings.

## Related Notes
- [[newman-agents-review-committee]]
