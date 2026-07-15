# Newman Brain — Karpathy-style LLM Wiki

A plain-markdown personal knowledge base distilled from **all Newman Claude Code sessions** across the MacBook, mac mini, and the newman-vps/droplet (jesus + mario). It follows Andrej Karpathy's "LLM-wiki" idea: a durable, human-readable store that a future LLM can load and reason over instead of re-deriving everything from scratch.

## How to query it

Point Claude Code (or any agent) at this folder:

```
cd ~/Documents/newman-brain/wiki
# then ask, e.g. "how does the CFE MiEspacio harvest avoid the 10-recibo permaban?"
```

The agent reads the topic notes first (synthesis of durable facts), then follows `[[slug]]` links down into the session notes for provenance. Slug = filename without `.md`. Every note carries its source session id so a claim can be traced back to the raw transcript.

## Note template convention

Every note (session and topic) uses `_templates/note.md`:

```
# Title

**Summary**: one-liner
**Tags**: #space #separated
**Created**: YYYY-MM-DD
**Source**: <session id + host>  |  synthesis   (for topic notes)

---

## Content
- durable facts, numbers, gotchas, standing rules

## Related Notes
- [[slug]] links
```

- **Session notes** (`sessions/<host>/`) distill one Claude session each.
- **Topic notes** (`topics/`) are cross-cutting syntheses — the place to start; `Source: synthesis`, `Created 2026-07-15`.

## Topics index (`topics/`)

| Topic | What it covers |
|---|---|
| [[cfe-invoice-harvesting]] | Consulta/MiEspacio paths, pseudo-API postbacks, 10-recibo permaban, rate limits, RPU-vs-RMU rules |
| [[ppa-pricing-model]] | 28%-on-generation / 144-mo / yr-12 transfer structure; finance-rigor rules; verified deal economics |
| [[solar-bess-sizing]] | CFE Brain max-NPV optimizer, PV⊥punta / BESS-lever doctrine, PV-surplus bug, golden tests |
| [[market-data-pml-tariffs]] | CFE tariff scraping (DOF/CENACE), 18M/45M-row PML backfill, nodal-grain schema, throttling |
| [[crm-and-monday-decommission]] | Intersolar contacts, Monday MCP fragility, tuesday CRM, the Monday→newman-brain decommission |
| [[newman-agent-org]] | CEO/CTO org, 95-gate governance, the review-committee eval harness + recurring defects |
| [[newman-rebuild-pipeline]] | Clean-room v2 Supabase-orchestrated invoice→PPA pipeline, self-heal auto-deploy, repo governance |
| [[brand-ui-design-system]] | Newman v3 (+ Kamú, Swiss) design systems, committee /loop workflow, deploy conventions |
| [[sales-marketing-plays]] | Competitor intel, GDMTH-volatility SEO/TOFU whitespace, Sutherland doctrine, academy/pitch assets |
| [[clients-and-deals]] | KFC, AFCH, COVESTRO, FibraHotel, Anáhuac, PepsiCo, Yazaki, Chiapas — who/tariff/system/economics |
| [[infra-and-secrets]] | mini/droplet/Supabase/Cloudflare topology, Vault secrets doctrine, devops gotchas |
| [[legal-privacy]] | PPA clause red flags, LFPDPPP obligations, citation discipline, security posture, refusals |

## Session notes

### MacBook (`sessions/macbook/`)

| File | Date | Summary |
|---|---|---|
| 2026-06-20-pepsico-ppa-proposal | 06-20 | PepsiCo/GEPP PPA repo + executive proposal site on Pages |
| 2026-06-21-newman-agents-founding | 06-21 | Founded the newman-agents company; CFE scraper + CENACE PML backfill kickoff |
| 2026-06-23-clean-room-skill-newman-skill-stack | 06-23 | Built /clean-room + 6 /newman-* skills |
| 2026-06-23-newman-re-registrar-workspace-dns | 06-23 | newman.re registrar (101domain) + Workspace DNS records |
| 2026-06-24-bess-intersolar-exhibitor-scraper | 06-24 | Scraped 2,682 Intersolar exhibitors into Postgres |
| 2026-06-24-byd-bess-rfq-anahuac | 06-24 | BYD BESS RFQ for Anáhuac (1.25 MW / 2.5 MWh) |
| 2026-06-24-datasheet-scraper-agent-kickoff | 06-24 | Kickoff of the PV/BESS/hydro datasheet scraper agent |
| 2026-06-24-qwen36-mini-bakeoff | 06-24 | Qwen3.6 vs 3.5 bake-off on the mini (/api/chat gotcha) |
| 2026-06-26-cfe-warehouse-schema-supabase | 06-26 | Source-namespaced warehouse schema + Supabase + PML backfill |
| 2026-06-26-competitor-intel-research | 06-26 | Competitor intel on 4 MX rivals + SEO battle plan |
| 2026-06-26-newman-ui-brand-logo-committee | 06-26 | Newman v3 design system + /newman-ui + logo committee loop |
| 2026-06-27-energy-academy-eu-course | 06-27 | 7-track EU energy sales course on Pages |
| 2026-06-27-kamu-living-investor-site | 06-27 | Kamú Living investor site + /kamu-ui + council loop |
| 2026-06-27-newman-data-api-fastapi-mini | 06-27 | FastAPI over the warehouse live at api.kameloso.com |
| 2026-07-02-agent-org-restructure-fibrahotel | 07-02 | Fable orchestrator org restructure + FibraHotel report rebuild |
| 2026-07-02-gdmth-volatility-funnel-play | 07-02 | GDMTH-volatility TOFU lead-gen SEO play |
| 2026-07-02-legal-answer-rubric-grade | 07-02 | Rubric-graded legal-agent PPA/privacy answer (0.85) |
| 2026-07-02-monday-stale-leads-blocked | 07-02 | Stale-lead drill blocked on Monday OAuth (no fabrication) |
| 2026-07-02-ppa-legal-review-dispatch | 07-02 | First PPA-clause + LFPDPPP legal-agent review |
| 2026-07-02-tofu-lead-play-agent | 07-02 | GDMTH finding → TOFU lead play (agent dispatch) |
| 2026-07-03-agent-committee-reviews-ppa-cfe | 07-03 | CRO PPA + CFE billing committee reviews |
| 2026-07-03-agent-review-committee | 07-03 | 17-judge eval batch of the newman-agents flock |
| 2026-07-03-deploy-newman-pages-lisa-api-refusal | 07-03 | Deployed Pages; refused LISA prod IDOR + LinkedIn recon |
| 2026-07-03-gws-auth-intersolar-contacts | 07-03 | gws auth + 2,634 Intersolar contacts into the directory |
| 2026-07-03-kfc-ppa-offer-workflow | 07-03 | KFC front-to-back: invoices → sizing → PPA offer on Pages |
| 2026-07-03-legal-agent-ppa-privacy-review | 07-03 | Legal-agent 2nd run: mailto CTAs are a collection event |
| 2026-07-03-newman-agents-review-committee | 07-03 | 19-grader eval batch (finance/data/legal gaps) |
| 2026-07-03-newman-repos-committee-audit | 07-03 | 7-expert audit + fix loop across 11 NewmanTech27 repos |
| 2026-07-03-ppa-legal-privacy-review | 07-03 | Legal-agent clause checklist + no-Aviso-yet verdict |
| 2026-07-03-review-attorney-clause-redline | 07-03 | Attorney review of PPA clause redline (8/10) |
| 2026-07-03-review-attorney-clause-redline-v2 | 07-03 | Second attorney redline pass (7/10) |
| 2026-07-03-review-attorney-legal-agent | 07-03 | Attorney review of legal-agent (7/10) |
| 2026-07-03-review-billing-miespacio-invariant | 07-03 | Billing review of add-download-DELETE invariant (7/10) |
| 2026-07-03-review-billing-photo-pipeline | 07-03 | Billing review of photo→consumption pipeline (7/10) |
| 2026-07-03-review-cenace-webforms-scrape | 07-03 | CENACE review of PML WebForms scrape (6/10) |
| 2026-07-03-review-committee-judges | 07-03 | 16-judge persona eval batch |
| 2026-07-03-review-consultant-gdmth-method | 07-03 | C&I consultant review of GDMTH method (7/10) |
| 2026-07-03-review-finance-covestro-deal | 07-03 | Project-finance review of COVESTRO PPA (7/10) |
| 2026-07-03-review-finance-gdmth-walkthrough | 07-03 | Project-finance review of GDMTH walkthrough (6/10) |
| 2026-07-03-review-negotiator-clause-redline | 07-03 | Negotiator review of clause redline (7/10) |
| 2026-07-03-review-negotiator-legal-agent | 07-03 | Negotiator review of legal-agent (6/10) |
| 2026-07-03-review-negotiator-legal-agent-v2 | 07-03 | Second negotiator review (6/10) |
| 2026-07-03-review-ocr-text-layer | 07-03 | OCR review: RPU/RMU confusion caught (5/10) |
| 2026-07-03-review-pml-storage-schema | 07-03 | Data-specialist review of PML storage design (7/10) |
| 2026-07-03-review-privacy-officer-legal-agent | 07-03 | LFPDPPP officer review of legal-agent (7/10) |
| 2026-07-03-review-qa-photo-pipeline | 07-03 | QA review of photo pipeline (7/10) |
| 2026-07-03-review-security-miespacio | 07-03 | Security review of Mi Espacio workflow (6/10) |
| 2026-07-04-cfe-invoice-harvest-supabase | 07-04 | CFE portal harvest + client schema on Supabase |
| 2026-07-04-solar-bess-sizing-agent | 07-04 | PV+BESS sizing agent: optimizer, divisions, BESS bug |
| 2026-07-05-afch-ppa-offer-dataroom | 07-05 | AFCH PPA offer + data room + Cloudflare DNS |
| 2026-07-05-monday-intersolar-board-contacts | 07-05 | Intersolar contacts into a new Monday board |
| 2026-07-05-monday-intersolar-dedupe-blocked | 07-05 | Board insert done; dedupe blocked by Monday 403 |
| 2026-07-05-newman-academy-pages-deploy-check | 07-05 | Verified academy on GitHub (not GitLab) Pages |
| 2026-07-06-pml-supabase-migration | 07-06 | 18.1M zona + 45M node PML rows mini → Supabase |
| 2026-07-07-cfe-miespacio-harvest-pseudo-api | 07-07 | fetchDrain postback pseudo-API (newman-architecture PR #5) |
| 2026-07-07-daily-huddle-deliverables-vc-pitch | 07-07 | Huddle transcript → deliverables + VC pitch loop |
| 2026-07-07-droplet-setup-secrets | 07-07 | DO droplet setup, users, Vault secrets, clean-room kickoff |
| 2026-07-07-huddle-marketplace-pitch | 07-07 | Marketplace VC-committee pitch loop (→89/100) |
| 2026-07-07-newman-architecture-cleanroom-deploy | 07-07 | 7-agent clean-room into newman-architecture + droplet deploy |
| 2026-07-07-whatsapp-intake-cutover | 07-07 | Twilio intake test, cascade cutover, golden 18/18 |
| 2026-07-08-supabase-pipeline-pgcron | 07-08 | Supabase as orchestrator: pipeline table + pg_cron drain |
| 2026-07-09-agent-org-ceo-cto | 07-09 | iTerm 6-pane org, CEO/CTO, newman-rebuild v2 reboot |
| 2026-07-10-newman-ceo-session-branch-consolidation | 07-10 | CEO session: bug-fix + single-main-branch consolidation |
| 2026-07-14-newman-rebuild-miespacio-phases | 07-14 | Twilio→Consulta→MiEspacio harvest phases + auto-deploy |
| 2026-07-15-monday-decommission-newman-brain | 07-15 | Monday decommission → newman-brain export + wiki kickoff |

### mac mini (`sessions/mini/`)

| File | Date | Summary |
|---|---|---|
| 2026-07-10-ceo-rebuild-orchestration | 07-10 | CEO seat orchestrates newman-rebuild kickoff; seats → mini subagents |
| 2026-07-10-chiapas-cfe-invoice-harvest | 07-10 | Full-depth Chiapas MiEspacio harvests; harvest gotchas → issue #19 |
| 2026-07-11-invoice-review-ui-and-cosecha | 07-11 | review.newman.re invoice-review UI + /cosecha RPU-harvest page |
| 2026-07-11-tuesday-crm-redesign-board | 07-11 | 33-issue tuesday CRM redesign/migration board |
| 2026-07-12-graphify-codebase-graph | 07-12 | Graphify code graph traces the harvest write chain |
| 2026-07-12-market-data-migration-plan | 07-12 | CFE tariff + PML migration into newman-rebuild `market.*` |
| 2026-07-12-miespacio-xml-drain-rate-limit | 07-12 | MiEspacio XML drain tuned past the ~5-download rate limit |
| 2026-07-12-rebuild-repo-audit-readme-issues | 07-12 | newman-rebuild repo audit: README, infra issues, #109 merge |
| 2026-07-15-mario-engine-client-calculo | 07-15 | Mario's savings engine → pg_cron offers into client.calculo |

### newman-vps — jesus (`sessions/vps-jesus/`)

| File | Date | Summary |
|---|---|---|
| 2026-07-07-cfe-cicd-tests-pseudo-api | 07-07 | CFE CI/CD fix, unit tests, __doPostBack pseudo-API probe (blocked on mini SSH) |
| 2026-07-07-monday-mcp-seat-audit | 07-07 | Monday MCP reorg attempt; no API path to a paid CRM seat |
| 2026-07-07-vault-secrets-hardening | 07-07 | HashiCorp Vault auto-unseal + token rotations on newman-vps |
| 2026-07-08-curvas-consumption-curves | 07-08 | Load-curve tables + curvas.newman.re; Vault→Supabase secrets |
| 2026-07-08-excalidraw-sso-crm-prod | 07-08 | Excalidraw self-host, login.newman.re SSO gate, dev/main fork discovered |
| 2026-07-08-huddle-todos-agent | 07-08 | Huddle-minutes agent → Tuesday kanban + ToDos tab |
| 2026-07-08-mario-access-and-vps-onboarding | 07-08 | tmux seats, Supabase MCP, Mario SSH key on the droplet |
| 2026-07-08-newman-landing-deploy | 07-08 | Landing-page CI/CD to dev.newman.re (Actions + cloudflared) |
| 2026-07-08-tuesday-crm-committee-loop | 07-08 | /loop built Tuesday CRM under committee scoring (→88/100) |
| 2026-07-09-ceo-org-real-invoice-gate0 | 07-09 | CEO seat: real WhatsApp invoice test, GATE-0 preserve-both ruling |
| 2026-07-09-cfe-real-invoice-claim-media | 07-09 | claim_media (016) + bulk_pdf status (017) prod bugs traced/fixed |
| 2026-07-09-cto-verification-freeze | 07-09 | Verify-claims-against-artifacts rule; REVOKE client-facing freeze |
| 2026-07-09-phase1-assessments | 07-09 | Parser/ppa seat assessments; enrich.py reconciliation is a tautology |
| 2026-07-09-sizing-materiality | 07-09 | sizing.py divergence quantified: net oversell of savings |
| 2026-07-09-supabase-devops-gate0 | 07-09 | DEL-4 (prod 5/75 migrations), freeze execution, gate0 merge |
| 2026-07-09-token-audit-baseline | 07-09 | $2,475 token audit: median 147k carried context is the driver |
| 2026-07-09-tuesday-inputs-spec | 07-09 | Tuesday input-surface spec (56/100, WhatsApp silent drop) |
| 2026-07-09-vps-reboot-cleanup | 07-09 | Reboot recovery; vault-fetch boot race + NordVPN snap removed |
| 2026-07-10-flock-overnight-golden-proof | 07-10 | Golden extraction proof 18/18, sizing.py fix, org-wide drain |
| 2026-07-10-newman-rebuild-seat-org | 07-10 | Issue-driven rebuild seats: orchestration schema, golden CI, SSO capture |

### newman-vps — mario (`sessions/vps-mario/`)

| File | Date | Summary |
|---|---|---|
| 2026-07-08-cfe-ppa-bess-engine-to-edge-functions | 07-08 | PPA+BESS engine → edge function; newman-brain repo born; Yazaki runs |
| 2026-07-08-supabase-mcp-and-auth-setup | 07-08 | Supabase MCP/CLI + gcloud auth patterns and gotchas |
| 2026-07-09-bess-portfolio-master-document | 07-09 | 136-project BESS portfolio master doc (129.9 MWh / 72.3 MW) |
| 2026-07-09-helioscope-roof-sizing-pipeline | 07-09 | Helioscope roof pipeline + Tongwei packing + HOUSE_STYLE |
| 2026-07-10-camaron-dorado-financial-dd | 07-10 | El Camarón Dorado financial DD: 3.31/5 requiere mitigantes |
| 2026-07-11-gdmto-vs-gdmth-bess-value | 07-11 | BESS barely pays under GDMTO (no punta, umbral-bound capacidad) |
| 2026-07-12-afc-kfc-pizzahut-proposal | 07-12 | AFC live-motor Excel + deck; PV-only $617,636/yr (26.22%) |
| 2026-07-12-fable-opus-handoff-tooling | 07-12 | /handoff command; orchestrate-in-Fable, execute-in-Opus doctrine |
| 2026-07-12-fibrahotel-proposals | 07-12 | 5 Posadas hotels; BCS DIV/0 fix; deck mobile prerender fix |
| 2026-07-13-gepp-solucion-deck | 07-13 | GEPP deck v4–v7 + the /solucion-deck skill frozen |
| 2026-07-13-pueblo-bonito-desaladora | 07-13 | 6-yr/18% desaladora PPA; SIN-vs-BCS motor limitation found |
| 2026-07-14-gepp-solar-charge-bess-dispatch | 07-14 | Solar-charge BESS dispatch rev4 (+$954k/yr portfolio) |

**Totals: 64 MacBook + 9 mini + 20 vps-jesus + 12 vps-mario = 105 session notes; 12 topic syntheses.**

## Coverage

**All three hosts mined as of 2026-07-15** — MacBook, mac mini, and newman-vps (both jesus's and mario's sessions). Future sessions should be distilled into `sessions/<host>/` and folded into the topic notes as they land.
