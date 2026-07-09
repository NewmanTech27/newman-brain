# Index

Catalog of every wiki page. Maintained by the agents, not by hand.

## cfe-bill-parser
_(empty — awaiting first ingest)_

## cfe-ppa-bess
_(empty)_

## supabase-devops
- [[canonicity-prod-is-truth]] — decision: production DB is source of truth; reconcile git to it, unify the fork
- [[main-dev-fork]] — finding: main (cfe-collector) vs dev (CRM) is a two-way fork off frozen staging, not drift
- [[migration-git-prod-drift]] — finding: only 5/75 dev migration versions match the 117-migration prod ledger

## tuesday-inputs
- [[tuesday-newman-re-is-the-crm]] — descriptive: tuesday.newman.re is the Tuesday CRM (apps/crm-web) on its own droplet, not newman-vps
- [[whatsapp-intake-silent-drop]] — finding: WhatsApp edge fn is fire-and-forget, always-200, drops data with no retry/trace (CRITICAL)
- [[crm-rls-rbac-ordering-trap]] — finding: CRM RLS final state set by migration ordering; RBAC drops+recreates all crm.* policies to a staff gate

## concepts
_(empty)_

## Hubs
_(pages with 3+ inbound links)_

## Open questions
_(pages with `kind: question`)_
