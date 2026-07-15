# Legal-agent PPA/privacy review, second run: mailto CTAs are a collection event

**Summary**: Re-run of the PPA-clause + privacy drill; legal-agent reported the missing-PPA blocker as top finding, flagged PROFECO pre-contractual exposure from landing copy, and confirmed the mailto CTAs trigger LFPDPPP despite no database.
**Tags**: #newman #ppa #legal #privacy #landing
**Created**: 2026-07-03
**Source**: macbook session e66c6aee-84f9-4c51-ae1e-253354e6fc95.jsonl (newman-agents project), user jesus

---

## Content
- Same drill as 2026-07-02 run: review PPA termination + escalation clauses, confirm LFPDPPP obligation on lead capture.
- Task 1: no PPA draft anywhere (proposals/ empty, no contracts/ dir); blocker reported as the primary finding rather than buried.
- Live liability ranked above the missing draft: `landing/index.html` lines 130-135 and 337-340 make binding-sounding promises ("blindado contra los aumentos", "condiciones de salida explícitas... por escrito") with zero contract behind them → PROFECO / pre-contractual-representation exposure. Fix: draft clauses now or soften copy until they exist.
- Task 2 (LFPDPPP, verified 2026-07-03):
  - Calculator form fields (tariff/kWh/kW) = not personal data, no persistence — fine.
  - `mailto:hola@newman.energy` CTAs (app.js:178, 249) + footer link = a collection event once the user's mail client sends name/email; LFPDPPP triggers regardless of no DB.
  - Zero Aviso de Privacidad exists site-wide — live gap.
  - Citations: LFPDPPP Art. 15-16 (Aviso required pre-collection), Art. 8 (consent), Art. 16-III (minimum content: responsable, purpose, ARCO mechanism); DOF 5-jul-2010 base; 2024-25 reform impact flagged as unverified/pending.
- Draft Aviso placeholder produced (footer + CTA-adjacent links, ARCO text, entity TBD) — marked DRAFT, needs licensed Mexican attorney.
- Explicit needs-counsel list: final PPA clause language, final Aviso text, FAQ copy-softening decision.

## Related Notes
- [[2026-07-02-ppa-legal-review-dispatch]]
- [[2026-07-03-review-committee-judges]]
