# Newman review-committee judge runs: 16 single-shot persona evaluations of agent answers

**Summary**: A batch of 16 one-message sessions where persona judges (attorney, CRO, project-finance director, OCR engineer, security reviewer, CFE billing specialist, data-quality engineer, contracts negotiator, C&I consultant) scored newman-agents answers 6-8/10 and produced concrete instruction improvements for the agent flock.
**Tags**: #newman #agents #evals #ppa #cfe #ocr #finance #legal
**Created**: 2026-07-03
**Source**: macbook sessions (newman-agents project), user jesus — 16 JSONLs: ed657337, ebbbb143, e7766533, e4659460, dff4bb37, de0930ab, dbe453c3, d417429e, d28f05d1, cf91b535, cd2b311f, ccac368d, c8d630e1, c05f0278, bc0daac2, b898d5d5, b63ed299

---

## Content
- Structure: each session = one user prompt ("You are a <persona>... judge the agent's ANSWER to the TASK") + one JSON verdict `{score, issues, improvements}`. Personas were run in duplicate/triplicate across 4-5 underlying tasks. Scores ranged 6-8.
- Tasks evaluated: (1) PPA termination/escalation + LFPDPPP review, (2) blurry-CFE-recibo-photo → verified consumption pipeline, (3) GDMTH fundable PPA structure + economics, (4) nightly tariff scrape "green but no rows" detection, (5) Mi Espacio history pull safeguards, (6) a real VERIFIED deal: COVESTRO, Ecatepec (Valle de México Norte), GDMTH, 570,075 kWh/mo (base 33,286 / intermedio 347,276 / punta 189,513), 1,138 kW demand, MXN 1,701,443.51 bill, one outlier month 101,636 kWh.
- Recurring judge findings across personas:
  - Finance (d417429e, ccac368d, c05f0278, bc0daac2): always state real-vs-nominal and IVA convention; no headline IRR without a year-by-year FCF/DSCR table; DSCR stress breaches must resolve to one re-sized fix; model offtaker credit default and FX hedge cost quantitatively, not as flags; source every CAPEX $/W and debt rate/tenor.
  - Tariff realism (c8d630e1, b63ed299): 22% solar CF too high for Central fixed-tilt (~19-20% real); tag every number [ASSUMED] vs [SOURCED: doc+date]; query the warehouse/tariff DB first before declaring inputs "not in hand"; CFE escalation needs DOF/CRE historical cite, not ad-hoc 5%.
  - OCR/CFDI pipeline (de0930ab, dbe453c3, b898d5d5, e4659460): add post-scrape reconciliation (scraped CFDI vs photo reads) so a misread no_servicio can't silently pull the wrong account; define numeric per-field confidence thresholds (XML 0.95+, text-PDF 0.85+, vision 0.6+); dedup by RPU+period before re-scraping; persist a durable cross-session Mi Espacio receipt counter (10-receipt permaban is cumulative, not per-run); embedded-XML pdfdetach step only applies to PDF-only acquisitions.
  - Security (ebbbb143, score 8): redact Playwright traces/screenshots of PII, encrypt + set retention TTL on data/raw CFDI files, log LFPDPPP consent per pull before Path B.
  - Data quality (d28f05d1, score 8): 200-but-empty trap handled well; add explicit staleness SLA (N days past expected DOF publish = escalate), idempotent gate checks, named P0/P1 escalation channel.
  - Legal (ed657337, cd2b311f, e7766533, dff4bb37, cf91b535): privacy verdicts must state files checked and confirm repo-wide before claiming site-wide compliance; re-verify 2024-25 LFPDPPP reform before citing article numbers; cite the Reglamento too; proposed numeric caps/collars must be labeled placeholders with sourcing rationale; flag LIE regulatory overlay (possible statutory exit rights) before pure contract drafting; marketing copy making legal promises = same-turn escalation.
- Purpose: the improvements were framed as instructions to bake into the newman-agents AGENTS.md / child-agent prompts — an eval harness for the flock.

## Related Notes
- [[2026-07-02-ppa-legal-review-dispatch]]
- [[2026-07-03-legal-agent-ppa-privacy-review]]
