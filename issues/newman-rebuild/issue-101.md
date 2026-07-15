# #101: Live system is a two-way fork: mini executor code and Supabase migrations live on divergent unmerged branches

- State: CLOSED
- Created: 2026-07-12T12:19:33Z  Closed: 2026-07-12T14:52:35Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/101

## Body

**Severity: p1**

The deployed pipeline is the union of two branches that have forked two ways (`pipeline/schema..pipeline/executors` = 13 commits, reverse = 14). The mini runs `pipeline_endpoint.py` from `pipeline/executors` (via the `newman-rebuild-wt-drive` worktree) while the pg_cron/RPC migrations it depends on exist only on `pipeline/schema`. `harvest/pipeline_endpoint.py`, `harvest/deploy/com.newman.pipeline-endpoint.plist`, `harvest/flake.nix` exist ONLY on `pipeline/executors`; the 15 live cron/dedup/reaper migrations (`supabase/migrations/20260711230000+`) ONLY on `pipeline/schema`. `main` is ~50 commits behind and contains neither.

No single ref in the repo reproduces the running system, and `main` — the branch the golden gate protects — has none of it. This is exactly the "two-way fork (dev +102 / main +55)" failure mode CHARTER.md:19-20 says this clean-room was created to escape.

**Fix:** reconcile the two branches into one integration branch and merge to main behind the golden gate. Distinct from #90 (prod-applied SQL the repo never saw) — this is repo-internal divergence. Merging also unblocks closing ~25-30 open issues whose artifact commits are currently unmerged (INT-1).

## Comment by NewmanTech27 (2026-07-12T12:25:20Z)

## Merge plan (draft for data-lead + CTO sign-off per charter §9)

**Verified topology (2026-07-12):** `origin/main` @ `e80c98f`+PRs. `pipeline/schema` +15 (all pipeline migrations + cron), `pipeline/executors` +14 (`pipeline_endpoint.py`, launchd deploy, flake), two-way fork 13/14 between them. `pipeline/orchestrator` +5 — checked with `git cherry`: **NOT patch-equivalent** to schema/executors; its `rpc_enqueue_twilio` (dedup on media SID) is the live twilio-sync enqueue path (#73 artifact `b144171`). All three ARE pushed. `origin/develop` tip == `pipeline/executors` tip (`5d68bf3`) — decide: make it the integration branch or delete it to kill a second long-lived fork.

### Order

1. **Integration branch** `pipeline/integration` off `origin/main`.
2. Merge `pipeline/schema` (fast-forwardable alone vs main).
3. Merge `pipeline/executors` — resolve the 13/14 fork (overlap is in `harvest/`).
4. Merge `pipeline/orchestrator` — keep `rpc_enqueue_twilio` + monitoring-view commits; drop anything the #64 re-architecture superseded during conflict resolution.
5. **Ledger reconciliation on the branch** (ties #90/#91/#93/#99): renumber/order migration timestamps so a fresh `supabase db push` reproduces prod; capture the live-only `rpc_advance_twilio` razón-social seed (#91) and the twilio-sync edge function source (#93); diff resulting schema against each env (#99).
6. Verify: `harvest` pytest suite, `node --test engine/test`, golden selftest locally → PR to `main`, selftest + golden required checks green, CTO review, data-lead merge. **No force-push, no shared-branch rewrite.**
7. Rebase open PRs onto new main: #98 (drain depth), #88 (multi-invoice fanout), #100 (dedup guard — authored forward-only off remote main, should apply clean), #97 (migration-promotion CI). #89 (root README) needs reconciliation with the fuller root README now staged locally.
8. Post-merge: close the ~15 verified-done issues' merge-pending caveats resolve automatically; re-verify #90/#99 by replaying migrations onto a scratch Supabase branch.
9. Ops: repoint the mini's launchd deploy off the `newman-rebuild-wt-drive` worktree onto the merged ref (fixes half of #102 in the same motion).

Highest risk: step 5 — repo migrations vs prod-applied SQL. Everything else is mechanical.
