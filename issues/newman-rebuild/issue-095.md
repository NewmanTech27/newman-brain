# #95: Dev/staging Supabase branches clone real prod data: no PII scrub, retention, or access policy for lower environments

- State: OPEN
- Created: 2026-07-12T10:13:52Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/95

## Body

## Problem

The new dev/staging persistent Supabase branches were provisioned with the "clone real prod data" policy (operator decision, 2026-07-12). That replicates real client PII — 12-digit RPUs, receptor names in `pipeline.*`, `crm.client`/`crm.rpu`, raw recibo XML in `raw_cfe.*` (which embeds names, addresses, and consumption history) — into environments that exist precisely to be experimented on with weaker discipline. PR preview branches, if enabled in the Supabase GitHub integration, would multiply the copies further.

Charter §6 enforces secrets discipline ("names, lengths, hashes. Never values") and #48 already flags pre-existing client RPUs in merged files — but there is no written rule at all for the DB copies.

## What's missing (decide + document, then enforce)

1. **Scrub or don't-scrub, in writing.** Either accept full-fidelity clones (and say so), or add a post-clone scrub script (pseudonymize RPUs keeping check-digit shape, replace names, keep volumes) that runs on every branch reset. Synthetic-seed-only was the charter-aligned option; if fidelity is required, an anonymized clone is the middle ground.
2. **Retention:** branches are periodically reset/rebased from prod — define when stale clones are refreshed or deleted (a deleted feature branch's data should not outlive the branch).
3. **Access parity:** lower environments must keep prod's RLS/default-deny posture and restricted service keys — a leaked dev service key must not be a leak of real client data.
4. **Preview branches:** decide whether PR preview branches get data at all (schema-only is the safe default).

One page in the repo (e.g. `docs/environments.md` or a README section) + a scrub/seed script is enough; the point is that today the policy is implicit and the PII copies already exist.
