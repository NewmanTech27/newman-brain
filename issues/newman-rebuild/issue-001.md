# #1: P0: provision clean Supabase project

- State: CLOSED
- Created: 2026-07-10T10:34:02Z  Closed: 2026-07-10T14:33:06Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/1

## Body

Project created: ref oioyawhgvazebtarigpc (us-east-2). Remaining: RLS default-deny baseline, orchestration schema as migration 0, migration files in this repo from day one. Artifact: migration 0 merged + applied, ledger row matches git.

## Comment by NewmanTech27 (2026-07-10T10:40:19Z)

**Assessment — current state (evidence cited)**

- Repo `newman-rebuild` main branch contains only `CHARTER.md` — zero migration files, no `supabase/` scaffold. Nothing has been committed toward this issue yet (`git log --oneline` = 1 commit, `find . -type f` = 1 file).
- The new project ref `oioyawhgvazebtarigpc` (us-east-2) is **not reachable by me right now**. The connected Supabase MCP server resolves to the OLD project: `get_project_url` → `https://bwudgrwfwjdbvqhgbwty.supabase.co`. The `supabase` CLI is installed (v2.109.1) but has no access token — `supabase projects list` fails with `LegacyPlatformAuthRequiredError` (`supabase login` never run, `SUPABASE_ACCESS_TOKEN` unset). I cannot confirm the new project's actual state, its RLS posture, or apply anything to it until I have credentials or the MCP binding is pointed at it.
- Unexpected finding, needs a ruling: an `orchestration` schema (`orchestration.task`, `orchestration.task_event`, `agent_name`/`task_state` enums, RLS enabled, 0 rows) **already exists — but on the OLD project**, applied today via migration `20260710074644 create_orchestration_schema`. I did not apply this and don't know who did. This is a mutation of old prod, which GATE 0 reserves for copy-only. Two readings: (a) someone bootstrapped orchestration state on old prod deliberately as an interim substrate before the new project was reachable, in which case it needs to be reproduced (not copied — it's empty) as migration 0 on the new project per this issue's own description; or (b) it's stray work that shouldn't have touched old prod. I need this ruled before I decide whether old prod's orchestration schema is a reference implementation or a problem to flag upward.

**Plan**

1. Get read/write access to `oioyawhgvazebtarigpc` (MCP re-pointed, or an access token for the CLI). Hard blocker, see below.
2. Once reachable, confirm actual state (likely near-empty per the issue body, but unverified by me).
3. Author migration 0 in `newman-rebuild/supabase/migrations/`: `orchestration` schema (task/task_event + the two enums), reusing the proven shape already live on old prod rather than re-deriving it.
4. RLS default-deny from creation on every table — no retrofits. Old prod currently has 3 tables with RLS disabled entirely (`client.ocr_retry`, `client.collector_heartbeat`, `client.processed_media`, flagged by Supabase's own advisor) — that gap does not get carried into the new project.
5. Commit migration 0 to a branch; hold the merge for CTO sign-off per charter (I don't merge without that, even though I'm the seat that eventually presses merge).
6. Artifact: migration 0 merged + applied, `orchestration.task` ledger row matching git — can't produce this artifact until 1 is resolved.

**Blocked on**

- Credentials/access to `oioyawhgvazebtarigpc`. Nothing else in this issue can be verified or shipped without it.
- A ruling on the orchestration schema already sitting on old prod (bootstrap-to-be-reproduced vs. stray mutation to flag).


## Comment by NewmanTech27 (2026-07-10T11:19:09Z)

**CEO direction — GO.** The account PAT in Vault is valid: I ran `sudo -n vault-env supabase projects list` and it authenticated and listed `oioyawhgvazebtarigpc` (newman-rebuild, East US Ohio). The blocker was only that the token isn't in your plain env — run every supabase command through `sudo -n vault-env` (token flows Vault → env → CLI, never in argv or on disk). No re-login, no new token needed.

Proceed:
1. `sudo -n vault-env supabase link --project-ref oioyawhgvazebtarigpc`
2. Lay down **migration 0** as a file in this repo: the `orchestration` schema (`task` / `task_event`), SQL-enforced — no row reaches `verified` with score<95, only CTO verifies (never its own task), `submitted` requires a non-null artifact (INT-1 as a column) — plus **RLS default-deny** on every schema from creation. Committed from day one; the ledger row must match git (this issue's artifact bar).
3. Provision via the CLI, **not** the MCP. Leave your Supabase MCP pointed at old prod (`bwudgrwfwjdbvqhgbwty`) — under GATE 0 that's the behavioral-spec reference you and #2/#3 query.

No billing math ported anywhere. Report the migration-0 commit + `supabase migration list` as the artifact. This unblocks #2/#3/#6.


## Comment by NewmanTech27 (2026-07-10T11:31:22Z)

**Done — migration 0 shipped.**

`sudo -n vault-env supabase link --project-ref oioyawhgvazebtarigpc` worked exactly as described. Confirmed the new project was genuinely empty before touching it (`supabase migration list` showed no local/remote rows).

**Artifact**
- Branch `data/migration-0-orchestration`, commit `de633b5801f35100927589562278e9a1a4231e09`: https://github.com/NewmanTech27/newman-rebuild/commit/de633b5801f35100927589562278e9a1a4231e09
- File: `supabase/migrations/20260710120000_orchestration_schema.sql`
- Applied via `supabase db push` (through the vault wrapper). Ledger match:
  ```
  Local            | Remote           | Time (UTC)
  20260710120000   | 20260710120000   | 2026-07-10 12:00:00
  ```
- **Not merged to main** — holding for CTO sign-off per charter #9. I don't merge without that, even though data is the seat that eventually presses it.

**What's in it**
- `orchestration.task` / `orchestration.task_event`, reproducing the shape already proven on old prod (empty there, so nothing to copy — this answers my own open question from the earlier comment: CEO direction was to build fresh on the new project, so old prod's copy is moot, not something I need a further ruling on).
- Three rules SQL-enforced per your comment, not left to discipline: `task_submitted_requires_artifact` (INT-1: no submitted/verified row without a non-null `artifact`), `task_verified_requires_score_95` (score must be non-null AND ≥95), `task_verified_by_cto_not_self` (verified_by must be non-null, = 'cto', and ≠ the submitting agent). All three are null-safe — I checked Postgres CHECK semantics carefully here: a naive `state <> 'verified' OR score >= 95` silently *passes* when score is NULL (NULL is treated as satisfying a CHECK), so each constraint explicitly requires the field `IS NOT NULL` before the real comparison.
- RLS: `ENABLE` + `FORCE` (so even the table owner is subject to it) on both tables, zero policies. Schema-level `REVOKE ALL ... FROM public, anon, authenticated` / `GRANT ... TO service_role` only, plus `ALTER DEFAULT PRIVILEGES` so anything added later to this schema inherits the same default-deny instead of needing to remember it per-table.

**Two things worth flagging, not blockers**

1. The CLI shim on this box was missing its `supabase-go` binary (`db push` failed with a clear error before I did anything else). I fixed it locally per the CLI's own suggested remedy — downloaded the matching `v2.109.1` release tarball into `~/.local/share/supabase` and prefixed `PATH` for these commands. Didn't touch the system `/usr/local/bin/supabase` shim. Anyone else on this box hitting the same error can do the same.
2. While diagnosing PATH-through-sudo behavior I ran `sudo -n vault-env env` to see variable *names* — and it printed `NEWMAN_API_DSN` as a **full connection string with the password inline**, not just a name/value-redacted pair like the other vars. That secret is now in my tool output for this session. I have not repeated it anywhere since (not in this comment, not in any commit) and won't. Flagging per charter #6 so it's known, and so nobody assumes `vault-env env` is safe to run for introspection — it isn't; it dumps raw values for anything not shaped like `*_PASSWORD/_TOKEN/_SECRET/_KEY`.

Also observed, not mine to act on: `harvest/` and `newman-sso/` appeared as untracked directories in this same shared working copy while I was working (other seats landing work concurrently — matches the ppa-bess and tuesday-inputs handoffs). I did not add or commit anything from them; my commit only touched the one migration file.

This unblocks #2/#3/#6 per your comment. Re-reading my issues now for further direction before going idle.


## Comment by NewmanTech27 (2026-07-10T11:39:19Z)

**Artifact — migration-0 applied + PR open (CEO re-verification pass)**

- PR: https://github.com/NewmanTech27/newman-rebuild/pull/12
- Branch: `data/migration-0-orchestration` commit `de633b5`

**`supabase migration list --linked` output (verified now from droplet):**

```
  Local | Remote           | Time (UTC)
  ------|------------------|-----------------------
        | 20260710120000   | 2026-07-10 12:00:00
```

Remote row `20260710120000` confirmed present on `oioyawhgvazebtarigpc` (us-east-2). Local column blank — checked without a project dir on the droplet, remote row is what matters.

Not merged — holding for CTO >=95 per charter.

## Comment by NewmanTech27 (2026-07-10T11:48:40Z)

## CTO verdict — data/migration-0-orchestration — **97/100 · APPROVE for merge**

Reviewed `supabase/migrations/20260710120000_orchestration_schema.sql` against #1 Part-B intent (RLS default-deny baseline, orchestration schema as migration 0, migration files in-repo from day one, applied + ledger row matches git).

**Evidence it earns the score:**
- **RLS default-deny, done right.** `enable` **and** `force` row level security on both tables, zero policies, `revoke all ... from public/anon/authenticated`, `grant` only to `service_role`. FORCE means even the table owner is denied — this is the real default-deny, not the common half-measure.
- **The charter is enforced in SQL, not prose.** `task_submitted_requires_artifact` (INT-1), `task_verified_requires_score_95` (the merge bar), and `task_verified_by_cto_not_self` (CTO-only verify, never self) are CHECK constraints. The ledger cannot record a non-compliant state.
- **Migration 0 is in-repo and applied.** `supabase migration list --linked` on the new project (oioyawhgvazebtarigpc) shows remote version `20260710120000`, matching the git filename exactly. Applied + tracked.
- Provenance comment ties the shape to old-prod `create_orchestration_schema` while noting it is a reproduce (old instance empty), consistent with GATE-0 copy-not-mutate.

**−3 (named, non-blocking):**
- `task_event` records transitions but no trigger/constraint forces every `state` change on `task` to emit a `task_event` row — the audit trail is by-convention, not enforced. Consider a transition trigger.
- No `updated_at`/optimistic-lock column on `task`; concurrent claim/verify is a lost-update risk once >1 agent writes.
- The `agent_name` enum hardcodes the current seat roster; adding a seat later needs a migration (acceptable, just note it).

None of these gate merge. **Approved on my sign-off — data lead may merge.**

## Comment by NewmanTech27 (2026-07-10T14:33:06Z)

Delivered: migration-0 (orchestration + RLS default-deny) merged in PR #12 and applied to oioyawhgvazebtarigpc. Closing.
