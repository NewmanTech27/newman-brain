# Legal & Privacy (PPA clauses + LFPDPPP)

**Summary**: The durable legal doctrine from the many PPA-clause and privacy reviews — bankability killers in PPA termination/escalation, the back-to-back broker risk, and the LFPDPPP obligations on the landing page and bill-upload pipeline.
**Tags**: #newman #legal #privacy #ppa #lfpdppp #topic
**Created**: 2026-07-15
**Source**: synthesis

---

## Content

### Standing state
- **No PPA contract draft exists** anywhere in the repos — CHARTER workstream #7 (PPA broker/developer ops) is queued. Reviews return a red/yellow/green clause checklist instead of a review. Every review carries a not-a-lawyer disclaimer; final clause language and Aviso text need a licensed Mexican attorney.

### PPA clause red flags
- **Back-to-back / assignment / step-in** (top priority): Newman signs as broker counterparty but the developer supplies power; without a back-to-back clause mirroring termination triggers/cure periods, Newman is stuck owing the developer after the offtaker walks.
- **One-way termination** (Cláusula 14 test): client can exit a 15-yr solar PPA on 30-day notice with no penalty = bankability killer (RED). Fix needs a real VPN/termination-fee formula with discount rate + cap — NOT a blank "Anexo X" — and must respect pena convencional excessive-penalty doctrine (CCF arts. 1843–1846).
- **Escalation index** must be a public reference (INPC or DOF-published CFE tariff) with a hard fallback if INPC is discontinued — not an internal number. Statute cites belong in memos/recitals, not operative price-mechanism text.
- **Change-in-law clause** required given the 2024–25 electricity reform (LIE → Ley del Sector Eléctrico); flag possible LIE statutory exit rights before pure contract drafting.
- **Marketing-ahead-of-legal**: the landing page already promises "blindado contra aumentos" / "salida sin penalización" with no contract behind it = PROFECO / pre-contractual-representation exposure. Draft the clauses or soften the copy; marketing copy making legal promises = same-turn escalation.

### LFPDPPP (privacy)
- Calculator form fields (tariff/kWh/kW) = not personal data, no persistence — fine. But **`mailto:` CTAs are a collection event** the moment the mail client sends name+email → LFPDPPP triggers regardless of no DB. Trigger attaches on COLLECTION, not storage mechanism. Zero Aviso de Privacidad currently exists site-wide (live gap).
- Aviso triggers: a real lead form, storing mailto contacts in a CRM, or the bill-upload pipeline going live (a CFE bill = personal + financial data → express consent). Then: aviso simplificado at point of collection + full /aviso-de-privacidad page.
- Required elements often missing: revocación/ARCO mechanism, explicit transferencias sí/no per Art. 16 Reglamento; PII over plain email violates Art. 19 transmission-security; RPU+consumption could enable a socioeconomic profile (sensitive-data boundary).
- **Citation discipline** (standing rule): every statute cite pairs with DOF publication + last-reform date. Bases: LIE DOF 11-ago-2014; LFPDPPP DOF 5-jul-2010 + Reglamento DOF 21-dic-2011 (amended 26-01-2017). **INAI dissolved** per DOF 20-12-2024 reform — functions moved to the Secretaría Anticorrupción; post-transfer enforcement mechanics unverified.
- RPU classified as dato patrimonial only by inference — needs an INAI criterio/precedent cite before asserting.

### Security posture (Mi Espacio pipeline)
Redact Playwright traces/screenshots of PII; encrypt + set retention TTL on data/raw CFDI; log LFPDPPP consent per pull before Path B; secrets manager for creds; serialize account access (TOCTOU race can blow the 10-receipt cap).

### Refusals (boundary log)
Declined IDOR/authz testing against a competitor's prod API (lisaenergy.com — live customers, real PII; box ownership ≠ consent to other tenants' data), and LinkedIn employee-dossier recon (people-targeting / spear-phishing shape).

## Related Notes
- [[2026-07-02-ppa-legal-review-dispatch]]
- [[2026-07-03-ppa-legal-privacy-review]]
- [[2026-07-03-legal-agent-ppa-privacy-review]]
- [[2026-07-02-legal-answer-rubric-grade]]
- [[2026-07-03-review-attorney-clause-redline]]
- [[2026-07-03-review-attorney-clause-redline-v2]]
- [[2026-07-03-review-attorney-legal-agent]]
- [[2026-07-03-review-negotiator-clause-redline]]
- [[2026-07-03-review-negotiator-legal-agent]]
- [[2026-07-03-review-negotiator-legal-agent-v2]]
- [[2026-07-03-review-privacy-officer-legal-agent]]
- [[2026-07-03-review-security-miespacio]]
- [[2026-07-03-deploy-newman-pages-lisa-api-refusal]]
