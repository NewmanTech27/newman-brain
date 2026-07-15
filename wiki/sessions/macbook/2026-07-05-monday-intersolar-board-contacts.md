# Migrate Intersolar contacts into a new monday.com board

**Summary**: Created a dedicated Intersolar board in monday.com (CRM workspace) and bulk-inserted all 2,629 expo exhibitor contacts, keeping the legacy Contacts board untouched.
**Tags**: #newman #crm #agents
**Created**: 2026-07-05
**Source**: macbook session debfaa17-fba0-4251-8e05-117a155b5b55.jsonl, user jesus

---

## Content
- Re-authed monday MCP (logged in under newman-re) after an OAuth failure (ref ofid_e77ffc39cbeb1443).
- Decision: don't dilute the old Contacts board — spin up a separate **Intersolar** board (id 5099737762) in the CRM workspace.
- Columns: Name, Email, Phone, Website, Country, Sector, Description.
- Reverted the 4 columns accidentally added to Contacts board (0 expo items had been inserted).
- Relaunched bulk-insert agent to fill Intersolar with all 2,629 exhibitors (from Google Contacts).

## Related Notes
- [[2026-06-24-bess-intersolar-exhibitor-scraper]]
- [[2026-07-05-monday-intersolar-dedupe-blocked]]
