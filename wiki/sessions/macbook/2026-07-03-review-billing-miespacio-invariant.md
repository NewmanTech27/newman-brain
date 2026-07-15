# CFE billing-specialist review of add-download-DELETE invariant (7/10)

**Summary**: A CFE-billing persona scored the Mi Espacio path 7/10; strong on startup reconciliation and 10-receipt discipline, weak on post-add verification and partial-failure protocol.
**Tags**: #newman #cfe #scraper #eval
**Created**: 2026-07-03
**Source**: macbook session 34431f6d-0681-440f-a677-5a2d5065bfad.jsonl, user jesus

---

## Content
- Reviewed workflow adds: startup reconciliation deletes orphan receipts by identity (RPU/No.Servicio match, not count) if a prior run crashed between add and delete; stop after 2 failed logins; OTP/CAPTCHA mid-flow -> abort + needs_human (CAPTCHA bypass off-limits).
- Issue: no explicit post-add verification that the receipt appears before downloading — silent add failure yields stale history.
- Issue: no check that returned period count matches the requested 1-2yr range; partial data could be returned as success.
- Issue: partial-failure protocol undefined when download fails after add (delete must still run — the invariant is non-negotiable).

## Related Notes
- [[newman-agents-review-committee]]
