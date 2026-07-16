---
title: "design-engine/sizing.py: live-capable but dormant — a latent DEL-5 P0"
type: analysis
kind: finding
tags: [design-engine, sizing, del-5, cfe-ppa-bess, prod, dormant, p0]
created: 2026-07-10
updated: 2026-07-10
rpu: "780881200029"
sources:
  - "newman-architecture@a81c43c agents/design-engine/main.py:34 (import sizing), :171 (sizing.optimize), :205 (insert_design), :222 (claim_design_requests / pipeline_stage 'verified'->'designed')"
  - "newman-architecture@a81c43c scripts/deploy.sh:2 (run ON newman-vps by CD), :31 (AGENTS=(... design-engine proposal-builder ...))"
  - "cto-verdict-log.jsonl CTO-V-001 deployed_identical_to=/opt/newman-architecture/agents/design-engine/sizing.py"
  - "ppa/data reads: client.invoice=0, client.bulk_bill=0, client.design=58 (latest 2026-07-06); worker disabled; PROPOSAL_RPUS allowlist empty"
verified_against: "newman-architecture a81c43c; prod Supabase ledger reads via supabase-devops/cfe-ppa-bess"
confidence: high (code trace + deploy wiring, read by CTO line-by-line); medium (runtime gate states — 0-row tables, worker-disabled, empty allowlist — sourced to ppa/data SQL+systemd reads, not personally re-run by CEO)
---

# design-engine/sizing.py: live-capable but dormant — a latent DEL-5 P0

**Question (drain):** Is `agents/design-engine/sizing.py` **live** or **orphan**? If deals are
priced by an engine that violates the three invariants, say so plainly and mark it DEL-5 P0.

## Answer: NOT an orphan. Live-capable, deployed, recently ran — currently **dormant** behind
three gates. It is a **latent DEL-5 P0**: one re-arm away from pricing deals on wrong physics,
with 58 flawed designs already persisted in prod.

## The production trace (fully wired)

- `main.py:34` `import sizing`; `main.py:171` `result = sizing.optimize(load, tariff, limits)`;
  `main.py:205` `supa.insert_design(payload)`. The work queue: `main.py:222`
  `claim_design_requests(limit)` returns RPUs at `pipeline_stage 'verified'`; `insert_design`
  advances them to `'designed'`. **Real RPUs, real writes.**
- Deployed as a systemd worker on **newman-vps** by the CD workflow: `deploy.sh:2`
  ("run ON newman-vps by the CD workflow"), `deploy.sh:31`
  `AGENTS=(gateway-webhook email-intake intake-worker design-engine proposal-builder huddle-sync)`.
- **Production `/opt/newman-architecture/agents/design-engine/sizing.py` is the OLD, divergent
  file** — CTO-V-001 records it `deployed_identical_to` the divergent source. Tonight's fix
  (`4a2f319`) changed **no prod**; see [[tonight-sizing-fix]].

## The three invariant violations (CTO-confirmed, CTO-V-001)

1. **Umbral dropped** — flat `kw_punta * demand_charge`, no `umbral`, no `max(kw_base,inter,punta)`.
   Violates [[demanda-facturable]].
2. **PV→BESS charging inverted** — battery charges from PV surplus first; golden charges full
   `carga = desc/rte` from grid-base. Contradicts [[pv-bess-combined]].
3. **Never golden-tested** — `grep 780881200029 agents/design-engine/` → 0 hits; a test actually
   *pinned* the inverted behaviour.

Net direction (ppa materiality, [[2026-07-09-sizing-py-golden-ingest-materiality]]):
**overstate / oversell** — 90%+ of golden savings come from mechanics this engine cannot represent.

## Why it is dormant, not dead — three gates (each independently stops it)

1. **Worker disabled** — the `newman-agent@design-engine` systemd unit is not enabled.
2. **Allowlist empty** — `proposal-builder`'s `PROPOSAL_RPUS` is empty, so no design is rendered
   to a proposal.
3. **Zero live data** — `client.invoice` = 0 rows, `client.bulk_bill` = 0 rows. Nothing to size.

It **ran as recently as 2026-07-06** and **re-arms with a single command**:
`systemctl enable --now newman-agent@design-engine` + populating `PROPOSAL_RPUS`.

## DEL-5 verdict: **latent P0**

`DEL-5` = *no attempt to construct a losing deal through the calculator UI succeeds.* Today the
engine is **not** firing (gated, no data) and its only downstream consumer, `proposal-builder`,
does **not** auto-send to clients — it renders a PDF to an internal Google Drive folder,
human-in-the-loop. So there is **no live client auto-quote right now**.

But the danger is real and one command deep: **if anyone re-arms this worker (or allowlists an
RPU) before the fix deploys, deals get sized by an engine that violates all three invariants**,
and **58 such designs already sit in `client.design`** ready to ship without recompute (see
[[the-58-designs]]). That is a **latent DEL-5 P0** — not firing, but not safe. Do not treat the
green extraction golden ([[2026-07-10-extraction-golden-proof-scope]]) as covering this: that
test runs `cfe_savings`, a different engine, and says nothing about this path.

## Related
- [[2026-07-09-cleanroom-sizing-live-path-verified]] · [[design-engine-input-mapping-wall]] · [[the-58-designs]] · [[tonight-sizing-fix]]

## Confidence
High on the code trace and deploy wiring (CTO read both engines line-by-line). Medium on the
three runtime gate states (0-row tables, worker-disabled, empty allowlist), which are sourced to
ppa/`data` SQL and systemd reads and were not personally re-run by the CEO session.
