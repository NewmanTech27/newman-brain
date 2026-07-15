# Legal-agent review: PPA termination/escalation clauses + landing-page LFPDPPP obligation

**Summary**: Dispatched the legal-agent to review PPA termination/price-escalation clauses and confirm the privacy obligation for the lead-capture form; found no PPA draft exists (delivered a clause checklist instead) and no Aviso de Privacidad is required yet since the landing page only uses mailto links.
**Tags**: #newman #ppa #legal #privacy #lfpdppp #landing
**Created**: 2026-07-03
**Source**: macbook session 8a6ed9de-ad27-41bd-9a45-4df079b227f7.jsonl (newman-agents project), user jesus

---

## Content
- Task: review a PPA's termination + price-escalation clauses and confirm the privacy (LFPDPPP) obligation for the lead-capture form; routed to the legal-agent as a background task.
- **No PPA contract draft exists anywhere in the repo** — CHARTER.md workstream #7 (PPA broker/developer ops: legal, CRE/CNE, supply, financing) is still queued. Agent delivered a red/yellow/green clause checklist for a standard Mexican C&I shared-savings/fixed-price PPA instead of a review.
- Top red flags from the checklist:
  - **Assignment/step-in**: Newman signs as broker counterparty but the developer supplies power; without a back-to-back clause Newman holds risk it cannot pass upstream. Named top priority.
  - **Marketing-ahead-of-legal gap**: landing page already promises "no penalty exit" (index.html:65, 257-258, 337-340) with no contract backing it — either draft the contract to match or pull the copy.
  - **Force-majeure / termination interaction**: undefined who eats cost during a CFE-fallback gap.
  - Escalation index must be a public reference (INPC or DOF CFE tariff), not an internal number — yellow pending draft.
- Privacy verdict: landing form collects no name/email/phone, uses mailto: only (hola@newman.energy), no server-side capture — **no Aviso de Privacidad required today** (LFPDPPP DOF 05-07-2010, amended 26-01-2017).
- Aviso triggers listed: adding a real lead form, storing mailto inbox contacts in a CRM, or the bill-upload pipeline going live (a CFE bill = personal + financial data, needs express consent). Then: simplified notice at point of collection + full /aviso-de-privacidad page (Reglamento Art. 27-28).
- Regulatory note: INAI dissolved per DOF 20-12-2024 reform; functions moved to the Secretaría Anticorrupción — post-transfer enforcement mechanics unverified, check with counsel.
- Explicitly flagged as needing a licensed Mexican attorney: actual PPA clause drafting and the Aviso text once written.
- Next action recommended: start the PPA draft (assignment clause first) before shipping more landing-page promises.

## Related Notes
- [[2026-07-03-newman-agents-review-committee]]
