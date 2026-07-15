# Agent committee reviews: PPA risk officer + CFE billing specialist

**Summary**: Two newman-agents committee-judge runs scoring a Newman AI agent's answers — a chief-risk-officer review of a COVESTRO PPA and a CFE-billing-specialist review of the photo→verified-consumption flow.
**Tags**: #newman #ppa #cfe #agents
**Created**: 2026-07-03
**Source**: macbook sessions (newman-agents) f13d5503 + eea9cb93, user jesus

---

## Content
- **Chief risk officer** judging a PPA structured for COVESTRO, Ecatepec (Valle de México Norte), GDMTH — scored 4/10. Issues: combined stress test too soft (DSCR 1.05 "near-breach" still passes, no true default scenario); punta timing (19:00–22:00 Central) stated as fact without DOF/CENACE cite though it drives the hybrid recommendation; PPA price 1.65 MXN/kWh built from stacked unverified benchmarks (solar clearing + porteo guess + FX) then used as headline instead of kept in a TODO bucket.
- **CFE billing specialist** judging the blurry-photo → verified-consumption walkthrough — scored 5/10. Key gotcha: **RPU vs RMU swap** — the printed-bill field is RMU (not RPU); RPU is authoritative and comes only from the XML, so handing the scraper "RPU" as input is circular/wrong. Also should check embedded-XML-in-PDF first before falling back to OCR.
- Both are structured JSON committee verdicts (score/issues/improvements) used to harden the Newman agent flock.

## Related Notes
- [[2026-07-07-cfe-miespacio-harvest-pseudo-api]]
- [[2026-07-14-newman-rebuild-miespacio-phases]]
