# PPA clause + LFPDPPP privacy review via legal-agent (first run)

**Summary**: Orchestrator dispatched the newman legal-agent to review PPA termination/escalation clauses and confirm the LFPDPPP obligation on the landing lead form; no PPA draft existed, so it returned a clause checklist plus a RED privacy gap.
**Tags**: #newman #ppa #legal #privacy #landing
**Created**: 2026-07-02
**Source**: macbook session b3f428a6-6911-4843-9263-ef6c324a01f8.jsonl (newman-agents project), user jesus

---

## Content
- Task: review a PPA's termination + price-escalation clauses and confirm the privacy obligation for the lead-capture form.
- Orchestrator dispatched legal-agent as a background task; report dated 2026-07-02.
- Key finding: no PPA contract file exists anywhere in the newman-agents repo — nothing to review; charter workstream #7 (legal/PPA broker ops) still queued.
- Checklist of RED risks delivered instead:
  - Broker↔developer back-to-back contracts must mirror termination triggers/cure periods, else Newman stuck owing the developer after the offtaker walks.
  - Marketing/contract gap: landing page already promises "salida sin penalización oculta" and "precio blindado" with no contract behind it.
  - Escalation clause needs a defined formula + cap/collar tied to a DOF-published baseline, not vague "market rate".
  - Change-in-law clause required given 2024-25 Mexican electricity reform volatility (LIE → Ley del Sector Eléctrico package; article numbers post-reform unverified, must be cross-checked via regulation-policy-analyst + licensed MX attorney).
- LFPDPPP verdict: RED. Calculator form has no persistence (no PII), but two `mailto:` CTAs in `landing/index.html` / `app.js` send name/email/consumption to Newman = tratamiento → Art. 16 Aviso de Privacidad duty. No Aviso exists anywhere in `landing/`.
- Fix proposed: short notice near CTAs + full Aviso page + footer link before real leads flow.
- Legal basis cited: LIE DOF 11-ago-2014; LFPDPPP DOF 5-jul-2010 + Reglamento DOF 21-dic-2011.

## Related Notes
- [[2026-07-03-legal-agent-ppa-privacy-review]]
- [[2026-07-03-review-committee-judges]]
