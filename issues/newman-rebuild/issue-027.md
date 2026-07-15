# #27: Harden cto-verdict-log schema so ECO-3/ECO-4 are exact, not upper-bound

- State: OPEN
- Created: 2026-07-10T14:40:58Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/27

## Body

## Deliverable
Give every `~/cfe-brain/vault/wiki/cto-verdict-log.jsonl` entry a canonical schema so the token-economics KPIs are computable exactly: `{date, agent, issue/PR, ref_commit, score:int, decision:"merge"|"reject", named_gaps:[]}`. Retrofit the existing entries (CTO-V-001 carries no numeric score, field names are inconsistent). Owner: CTO — it owns the verdict log and appends one row per merge decision.

## Spec source
Surfaced by the #10 token baseline: with the freeform log, `eco34_join.py` under-counts the ECO-3 denominator, so ECO-3 (tokens/merged-point) is only an upper bound and ECO-4 (rework rate) rests on 3 loosely-typed rows.

## Artifact (required to close)
- [ ] Canonical schema documented + all existing rows retrofitted
- [ ] `eco34_join.py` runs clean against it (ECO-3/ECO-4 exact)

## Hazards
- [ ] No secret/PII values in the log (scores, refs, agent names only)
