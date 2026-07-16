# CRM cutover runbook — monday.com → Newman CRM (`tuesday.newman.re`)

Epic 5. Take the team off monday.com and cancel the seats, once the Newman CRM is
live. Everything up to this point is reversible; the point of no return is **cancelling
the monday subscription** (last step). Keep the monday export as the backstop.

**Owner:** Scrum Master / Ops. **Duration:** ~1–2 hours. **Prereq:** Epics 0–4 done
(schema live, data migrated + reconciled, MCP + app + assistant shipped).

---

## 0. Pre-cutover gates (all must be green)

- [ ] **App is live** at `tuesday.newman.re` and loads (see `deploy/crm-web/README.md`).
- [ ] **Users provisioned** — the 4 team members invited in Supabase Auth (Auth → Users)
      and each can sign in.
- [ ] **Reconciliation confirmed** — `crm.deal_summary` counts per stage match monday,
      and the financial view matches monday to the cent on a sample (Epic 1 already
      proved this; re-check after the delta migration in step 1).
- [ ] **Backups on** — the `crm.*` schema is in the Supabase project's normal backup
      window; note the retention.

> Optional but recommended: leave monday **read-only** for one week after cutover as a
> safety net before cancelling seats.

---

## 1. Delta re-migration (catch anything changed since the initial load)

The initial load was a point-in-time snapshot. Re-run the migration to pick up any
monday edits made since. It is **idempotent on `monday_item_id`**, so re-running only
updates/inserts — it never duplicates.

```bash
# on newman-vps (MONDAY_API_TOKEN + service_role in Vault)
vault-env python agents/crm-migrate/main.py --dry-run   # preview
vault-env python agents/crm-migrate/main.py             # apply
```

Then verify parity (service_role, via the MCP or psql):

```sql
select stage, count(*) from crm.deal_summary group by stage order by count(*) desc;
select count(*) as deals, count(*) filter (where total_vpn > 0) as with_vpn
from crm.deal_summary;
```

Compare against monday's current pipeline. Investigate any stage whose count differs
by more than the known null-stage default.

---

## 2. Announce + freeze monday

- [ ] Post the switch to the team: *"From today we work in **tuesday.newman.re**. monday
      is read-only and will be cancelled on <date>."*
- [ ] In monday, set boards to view-only for members (or revoke edit) so no new writes
      diverge from Supabase after the delta migration.

---

## 3. Flip the team

- [ ] Everyone signs in to `tuesday.newman.re`, confirms they can see the pipeline,
      open a deal, and read the financials.
- [ ] Sanity-check the assistant ("Ask Claude" → "which open deals are most stale?").
- [ ] Assign deal owners in `crm.deal.owner_id` (map monday owners → `crm.app_user`).
- [ ] Establish the weekly hygiene habit the old board lacked: use `crm_stale_deals`
      (MCP) or the pipeline's oldest-open list to chase deals untouched 30+ days.

---

## 4. Archive monday (the backstop)

- [ ] Export each monday board (Board menu → Export to Excel) — Deals, Deals NPA,
      Contacts, Quotes & Invoices, and the Ops boards.
- [ ] Drop the exports in the Drive backup location alongside the other Newman archives.
- [ ] Record the export date in this doc's history.

---

## 5. Decommission (point of no return)

- [ ] Confirm 1 week of the team working only in `tuesday.newman.re` with no issues.
- [ ] In monday.com billing, **cancel the CRM Pro subscription / remove the seats.**
- [ ] Remove the monday MCP from any Claude configs that no longer need it (the
      `crm-mcp` agent replaces it for CRM work).

**Savings realized:** ~$1.3–1.6k/yr in monday CRM Pro seats.

---

## Rollback

Before step 5 everything is reversible:

- **App issue:** `sudo systemctl stop newman-crm-web` and point the team back at monday
  (still read-only, not yet cancelled). Fix forward, redeploy.
- **Data issue:** the migration is idempotent — fix `crm-migrate` mapping and re-run;
  or `drop schema crm cascade` and re-apply the migrations + reload (prod is low-stakes
  until the team depends on it).
- After step 5, the monday export is the recovery source.

---

## Post-cutover hardening (follow-ups, not blockers)

- [ ] **Tighten RLS** — the `crm.*` policies are org-wide (`using(true)` for
      `authenticated`) for the 4-person launch. Scope writes by `owner_id`/role when
      ready (`supabase/migrations/…_crm_schema.sql` TODO).
- [ ] **Branch environments** — finish the dev/staging baseline (`supabase db pull` on
      newman-vps) so the failed branches replay cleanly; then promote via dev→staging→main.
- [ ] **Backup drill** — restore `crm.*` from a Supabase backup once to prove RTO.
- [ ] **Broaden the app** — contacts/accounts/quotes/ops screens (schema already exists).

---

## History

- _(fill in)_ initial load — 167 deals + 214 line items via the Supabase MCP.
- _(fill in)_ delta re-migration date.
- _(fill in)_ monday export date.
- _(fill in)_ monday cancellation date.
