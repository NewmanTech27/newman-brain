# CFE billing review of blurry-photo-to-verified-consumption pipeline (7/10)

**Summary**: A CFE-billing persona reviewed the rpu-extractor -> cfe-bill-scraper pipeline; main gap is no persistent cross-session receipt-count ledger for the 10-receipt permaban.
**Tags**: #newman #cfe #ocr #scraper #eval
**Created**: 2026-07-03
**Source**: macbook session 4c7fa3b2-6c5e-4563-a25c-a2a95ea79679.jsonl, user jesus

---

## Content
- Pipeline: Step 1 rpu-extractor (qwen2.5vl:7b vision on the mini) extracts no_servicio, rmu (cross-check both prints), folio, rfc, total_mxn — never guesses digits, RMU mismatch -> needs_human.
- Domain rule: no_servicio + rmu are the portal keys; the authoritative RPU comes from the acquired XML, not the print (usually unlabeled/partial on paper).
- Step 2 cfe-bill-scraper: Path A public Consulta first (no login); Path B Mi Espacio fallback.
- Issue: 10-receipt limit needs a persistent cross-customer/session counter ledger, not just per-run delete — permaban tracks cumulative account state.
- Issue: no explicit step reconciling print-guessed RPU with XML-authoritative RPU back into the identity block.
- Issue: Path A ">=12 periods available" branch condition unspecified.

## Related Notes
- [[newman-agents-review-committee]]
