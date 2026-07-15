# #99: pipeline: RPC + schema drift across Supabase envs — rpc_advance_twilio_multi exists only in prod-URL project, missing in staging + oioya

- State: CLOSED
- Created: 2026-07-12T12:06:21Z  Closed: 2026-07-13T22:05:43Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/99

## Body

## Problem

The extract-stage RPCs and the `pipeline` schema have **drifted across the Supabase environments**. Discovered while investigating the duplicate-RPU issue (#92) on 2026-07-12.

### Environment map (Supabase project refs)
| ref | role | `pipeline` schema | `rpc_advance_twilio` | `rpc_advance_twilio_multi` |
|---|---|---|---|---|
| `ugjqqezqtnjkzxkcqujz` | (owner reviewing here) | ✅ 6 tables | ✅ | ✅ |
| `bvhonjmjxbliuqxhrhec` | **staging** | ✅ 6 tables | ✅ | ❌ **missing** |
| `oioyawhgvazebtarigpc` | newman-rebuild | ✅ 6 tables | ✅ | ❌ **missing** |
| `bwudgrwfwjdbvqhgbwty` | **legacy** | ❌ none | ❌ | ❌ |

(Owner to confirm which of `ugjqqezqtnjkzxkcqujz` / `oioyawhgvazebtarigpc` is prod vs dev — both carry identical 37/33/12 twilio/consulta/mi_espacio seed data, i.e. cloned.)

### Findings
1. **`rpc_advance_twilio_multi` exists only in `ugjqqezqtnjkzxkcqujz`.** Migration `supabase/migrations/20260712100000_pipeline_twilio_multi_invoice.sql` is applied there but **not** in staging or oioya. So the multi-invoice fan-out (#87) and the within-parent dedup only run in one env — a fix targeting `_multi` (see #92) will silently no-op in the others.
2. **`pipeline.consulta` has no `UNIQUE(rpu)` in any env** — only `mi_espacio_rpu_uk` dedups, at the mi_espacio layer. Consistent across all three pipeline projects, so the duplicate-RPU behavior of #92 reproduces everywhere.
3. Enums (`twilio_status`, `consulta_status`, `mi_espacio_status`, `error_class`) are identical across the three pipeline envs — so the enum change proposed in #92 must be applied to all three.

### Why it matters
- Any fix authored against live objects in one project won't reach the others (compounds #90 migration-ledger drift and #91 stale-committed-RPC).
- Testing on staging (`bvhonjmjxbliuqxhrhec`) does **not** exercise the multi-invoice path, because `_multi` isn't there.

### Ask
- [ ] Confirm the canonical env map (which ref = dev / staging / prod).
- [ ] Re-apply `20260712100000_pipeline_twilio_multi_invoice.sql` (and any later pipeline migrations) to staging + oioya so all pipeline envs converge before the #92 dedup fix ships.
- [ ] Add a CI/preflight check that diffs `pipeline` schema + `public.rpc_advance_twilio*` definitions across envs so drift is caught (ties into #94 CI gap).

Related: #92, #90, #91, #87, #95.


## Comment by NewmanTech27 (2026-07-13T22:05:42Z)

Converged 2026-07-13/14. All 3 envs (develop ugjqqe, staging bvhonj, prod oioya) now:

- migration history 40/40 == repo files (repair_migration_history.py --apply per env; weak function-probe false positives excluded by direct body verification — rpc_advance_twilio guard, rpc_requeue_transient_failures WAF split)
- rpc_advance_twilio_multi present everywhere (applied to prod 2026-07-13)
- dedup enums+guard, consulta_rpu_uidx (33→13 dedup, prod losers in pipeline._consulta_dedup_backup_20260713), pipeline.monitor, WAF-environmental requeue, orchestrator_phase1 view: verified identical
- 20260711250000_pipeline_cron_cfe recorded-as-applied but deliberately NOT run (monthly adeudo refresh stays operator-HELD)
- promotion workflow (#97) merged; PR dry-run gate ran green against converged develop

Residual RPC semantics gap tracked in #134.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
