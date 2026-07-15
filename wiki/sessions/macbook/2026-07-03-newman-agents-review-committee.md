# Review-committee eval run grading newman-agents answers (19 grader sessions)

**Summary**: A batch of 19 single-shot subagent sessions (Jul 2-3, 2026) where professional-persona graders (CRO, project-finance director, CFE billing specialist, LFPDPPP officer, QA, DB engineer, browser-automation engineer, RevOps, CRO/conversion analyst) scored newman-agents answers 4-8/10 and surfaced recurring quality gaps.
**Tags**: #newman #agents #eval #ppa #cfe #privacy #warehouse #scraper
**Created**: 2026-07-03
**Source**: macbook sessions in -Users-jesuslopez-newman-agents (aa971d20, a0b84d0c, 94fbcc77, 931e9302, 92c014f6, 8c098abb, 8bfc6af4, 898d95e2, 8237f134, 803844e5, 7d6a5832, 7c0c6be4, 789232e3, 740c883b, 6fccb26e, 6d9aaa2c, 6d759751, 681b44d2, 67e678b2), user jesus

---

## Content
- Each session is one prompt: a persona reviewer on a "professional review committee evaluating an AI agent that works for Newman Energy" judges an agent answer and returns JSON {score, issues}. This is an eval harness run over the newman-agents flock, not interactive work.
- Tasks graded: CENACE PML storage design, fundable GDMTH PPA structure + headline economics, CFE bill OCR extraction discipline, CFE invoice harvest flow (Consulta vs Mi Espacio, add-download-DELETE), lead-conversion funnel play, Monday.com CRM handling, the legal/privacy answer, landing-page privacy check.
- Scores clustered 6-7/10; lowest 4 (CFE billing specialist on the add-download-DELETE flow), highest 8 (PML schema, bill-OCR never-guess rule). One rubric grader gave 0.85/1 on the PPA-structure walkthrough.
- Recurring finance gaps: DSCR asked for but never actually computed (only 1.25x/1.35x covenant targets quoted); sensitivities named without magnitudes (no MXN/USD or CFE-escalation swing ranges); PPA price 1.15 vs displaced 1.50 MXN/kWh ungrounded ("no comp cited"); false precision — DSCR/IRR decimals (0.81x, 1.10x) stacked on ~10 unsourced assumptions; demand-charge (capacidad/distribución, 1,138 kW) ignored in savings economics; debt currency (USD CAPEX vs MXN debt) unstated; CELs treatment vague.
- Recurring data gaps: every hard number TODO/illustrative — no real GDMTH tariff pulled from the warehouse despite the CHARTER mandate for sourced figures.
- CFE-harvest gaps: add→delete confirmation relies on count diff not receipt identity; no orphan-reconcile step if the process crashes between add and delete; throttling "random delays" with no concrete pacing vs Imperva; no session-expiry/CAPTCHA-mid-flow handling; no fallback when a blurry photo yields unreadable no_servicio/RMU.
- LFPDPPP gaps: aviso corto template missing required elements (revocación mechanism, explicit transferencias sí/no per Art. 16 Reglamento); PII over plain email violates the Art. 19 transmission-security obligation; RPU+consumption could enable a socioeconomic profile (sensitive-data boundary).
- PML schema review (score 8): recommends storing at nodal grain (~2,400 PNodo points) and rolling up to zona de carga (~50) via MV; flagged clave_nodo dual-purpose column ambiguity and missing FK to a nodo catalog.
- CRM/funnel reviews: no Monday-MCP-down fallback, no lead-routing SLA, "qualified lead" defined by intent not BANT data.
- Useful as a punch list of what the newman-agents flock must fix before customer-facing output: computed DSCR tables, sourced tariffs, identity-matched receipt deletion, aviso templates, concrete throttling numbers.

## Related Notes
- [[2026-07-03-ppa-legal-privacy-review]]
