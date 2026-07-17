# #193: Migration drift: DBs run 20260715* migrations that exist on no git branch

- State: OPEN
- Created: 2026-07-15T19:09:37Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/193

## Body

Found while shipping the review-confirm razon fix (#192): the prod and develop
databases have migrations applied that are absent from EVERY git branch.

- prod (oioyawhgvazebtarigpc) schema_migrations max: 20260715200000
- develop clone max: 20260715220000
- git: no branch has any migration file newer than 20260714090000
  (main tree tops out at 20260713120000, develop at 20260714090000)

So migrations 20260715140000 … 220000 (incl. 20260715120000_rpc_stored_periods,
and the three review RPCs rpc_review_confirm_twilio / rpc_review_reject_twilio /
rpc_confirm_review) were applied straight to the DBs, bypassing the git migration
pipeline. Consequences observed:
1. `db push --dry-run vs develop` fails for any new PR ("remote ahead / insert
   before last remote migration") — the migration CI is effectively broken.
2. Schema divergence between prod and the clones: prod has pipeline.twilio.duplicate_of;
   develop and staging do NOT. (prod is AHEAD of its own with_data clones.)

Impact: the git repo is no longer the source of truth for these schemas, and the
promotion pipeline (develop→staging→prod) can't be used until reconciled.

Fix: dump the applied-but-uncommitted migrations from the prod DB
(schema_migrations + pg_dump of the objects), commit them as the missing migration
files with their real versions, re-clone develop/staging from prod so the schemas
match, and lock down who can apply migrations out-of-band. Until then, changes are
going in by direct psql (as the review-confirm fix #192 had to).
