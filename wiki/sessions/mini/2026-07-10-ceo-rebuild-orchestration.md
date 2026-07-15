# CEO seat orchestrates the newman-rebuild kickoff: seats migrate from droplet tmux to mini subagents

**Summary**: The CEO orchestrator session that launched newman-rebuild — booted seed issues on new prod Supabase oioyawhgvazebtarigpc, moved the 5-seat agent org from droplet tmux panes to mini subagents, killed the droplets, and drove seat deliverables (golden CI, schema PRs, recibo parser) plus a paced Yazaki 76-RPU harvest sweep.

**Tags**: #newman #rebuild #agents #supabase #cfe #harvest #ci
**Created**: 2026-07-10
**Source**: mini session d2ee23c8-7d52-4861-9a0b-d5dc41735d19.jsonl, user jesus

---

## Content
- Session ran the CEO seat via `~/prompts/ceo_boot.md` / `ceo_v2.md` / `ceo_drains_done.md` — org pivoted to a clean-room rebuild; the six legacy droplet agents were drained and retired, parting findings folded into seed-issue drafts.
- Blockers cleared to start: new Supabase project **oioyawhgvazebtarigpc** ACTIVE_HEALTHY (us-east-2), db password in HashiCorp Vault as `NEWMAN_REBUILD_DB_PASSWORD`; 10 seed issues live in **NewmanTech27/newman-rebuild**.
- Five seats initially on droplet tmux (cto=opus; data/harvest/engine/crm=sonnet); Jesus saw no issue comments landing → panes judged ineffective; CEO switched to running seats as subagents directly on the mini, then **killed the droplets**.
- Data seat: migration-0 applied to remote (`20260710120000`), PRs #12/#14/#15 opened (schema + migration map), held unmerged pending CTO ≥95 gate; secret audit of repo confirmed clean.
- CTO seat built the **golden-test CI** (PR #16, issue #9): drives deployed `newman-brain/.../cfe-ppa-bess/engine.js` via `compute()`, asserts baseline **$30,157,371**, ahorro **$7,083,252**, **23.5%** peso-exact (tol <1 peso); proven RED on one-peso drift.
- CTO verdicts: data #1 → 97/100 APPROVE; harvest #5 → 72 then 86/100 RETURN; SSO #11 → 96/100 APPROVE. Caught a real XML mislabel bug: `CONSUMO1F=104467` is punta but extract.py labeled it base; also flagged tautological ground-truth in #4 test harness (78/100 RETURN).
- Harvest seat (issue #5, "linchpin"): `harvest/recibo_parser.py` wraps the vault golden engine `cfe_savings.extract.parse_bill` (no math re-derivation), adds a foot check `(Σ MEM importes + bonif_FP) × (1+IVA)` vs printed Facturación del Periodo — unreconciling bills route to typed `PARSE_FAIL` rows; validated on 39 GDMTH Yazaki bills (PR #17).
- CRM seat: `apps/crm-web` frozen reference didn't exist in repo yet, #8 correctly HOLD; secret audit verdict CLEAN — hardcoded key in `login/index.html:79` is the Supabase anon/publishable key (role=anon), fine to embed.
- Harness governance note: coordinator-relayed merge approval carries no user authority — data seat correctly refused to merge to main without direct CEO/Jesus confirmation.
- Session tail: Yazaki multi-site sweep of 76 RPUs hit 58% UNKNOWN failures → hypothesis of transient throttling confirmed; **18s pacing between RPUs eliminated the failures** (~2.5h full sweep). Residual skips are genuine `NAME_MISMATCH` (CFE wants canonical name form: `SA DE CV` vs `S.A. DE C.V.`).

## Related Notes
- [[newman-rebuild-project]]
- [[newman-agent-org]]
- [[cfe-brain-vault]]
- [[2026-07-10-chiapas-cfe-invoice-harvest]]
