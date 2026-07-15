# Review Committee Evaluation of the newman-agents Flock (17 Judge Sessions)

**Summary**: A batch of 17 one-shot LLM-judge subagent sessions, each scoring a newman-agents answer from a distinct professional persona (SRE, QA, CFE billing specialist, Mexican energy attorney, LFPDPPP privacy officer, SEO lead, Sutherland-school CMO, sales director, data engineer, browser-automation engineer, C&I energy consultant), returning strict-JSON verdicts with scores 5-8/10 and instruction-level improvement suggestions.

**Tags**: #newman #agents #eval #cfe #scraper #ppa #crm #legal #seo

**Created**: 2026-07-03

**Source**: macbook sessions in -Users-jesuslopez-newman-agents (17 files, ids 01a3ecce…, 01b4ac82…, 092c20be…, 0e5f323d…, 108a0777…, 109fdc82…, 12212419…, 12681874…, 1284b6a6…, 159d7ff6…, 174e5a74…, 1bd1e370…, 1cb3a032…, 1d9aab33…, 290dd6cf…, 29c0ddca…, 2acd7bcb….jsonl), user jesus

---

## Content
- Evaluation harness: each session spawns a persona judge ("You are on a professional review committee evaluating an AI agent that works for Newman Energy") that grades one agent answer and returns `{score, issues[], improvements[]}` — improvements phrased as edits to agent instructions/specs.
- Tasks judged (each by 2-3 personas): silent tariff-scrape failure (exit 0, green n8n, no DB rows); blurry-photo CFE recibo → verified consumption pipeline; CENACE ASP.NET WebForms PML scrape; Mi Espacio history pull safeguards; text-layer PDF field extraction; GDMTH PPA structuring (generic + real COVESTRO Ecatepec bill); stale Monday leads + price objection; GDMTH-volatility top-of-funnel play; PPA clause + LFPDPPP legal review.
- Scores ranged 5-8/10; no answer got sign-off-clean. Recurring cross-persona defects:
  - Unsourced magic numbers: 0.80 OCR confidence threshold, 6%/2% escalators, 19% solar CF, 65/35 energy/demand split, 1.65 MXN/kWh PPA price — all "pulled from air"; judges demand DOF/CRE/PRODESEN citations or calibration data.
  - Silent-empty-scrape blind spot: 200 OK + zero rows treated as success; require post-load row-count/schema gates as separate n8n nodes, baseline-deviation math (e.g. 3-sigma trailing avg), idempotent upsert on period key, checkpoint/resume for backfills.
  - Escalation vagueness: "flag" without alert channel/paging path for P0; objection leads should escalate immediately, not wait on MCP auth.
  - CFE identity-field confusion: RMU vs RPU vs No. de Servicio conflated; dual-print cross-read of RPU described but not wired; RPU length spec disputed (12 vs 18 digits).
  - Mi Espacio Path B is a scarce, risky resource: 10-receipt permaban, orphan-receipt reconciliation at startup, delete-after-download failure handling underspecified; judges want Path A (public Consulta) exhausted first.
  - Legal: PPA Cláusula 14 one-way exit = RED (needs VPN exit fee, anchored to Art 1840 CCF pena convencional caps); escalation clause needs hard fallback index if INPC discontinued; LFPDPPP cites must include Reglamento, INAI sanctions (Arts 63-64), and "aviso simplificado" (not "aviso corto") terminology.
  - Marketing: Alchemy reframing judged "name-dropped not applied" — require one concrete psychological device per asset and SERP/keyword-volume verification of the "post-reform whitespace" claim before building.
- COVESTRO Ecatepec verified bill (CFDI conf 1.0): GDMTH, Feb-26 period, 570,075 kWh (base 33,286 / intermedio 347,276 / punta 189,513), 1,138 kW demand, MXN 1,701,443.51; 12-mo history has one outlier month (101,636 kWh) whose exclusion the judge flagged as untested.
- Highest scores (8): Mi Espacio safeguard walkthrough and Monday drafts-only compliance answer; lowest (5): generic GDMTH PPA economics, CENACE scrape (no failure reporting), and the marketing play.
- Net purpose: harvest instruction-level fixes to feed back into the newman skill/agent specs (maintainer, cfe-bill-agent, deal-structuring, monday-lead-followup, growth-marketing-lead).

## Related Notes
- [[newman-agent-org]]
- [[newman-skill-stack]]
- [[newman-invoice-collector]]
- [[cfe-consulta-name-match]]
