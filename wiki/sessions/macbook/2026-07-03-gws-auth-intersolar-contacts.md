# Google Workspace auth + 2,634 Intersolar contacts into the newman.re directory

**Summary**: Authenticated the gws CLI for jesus@newman.re (GCP project newmanproject-501314) and cleaned/uploaded 2,634 Intersolar exhibitor contacts with sector labels, descriptions, and Trustpilot scores into the domain directory.
**Tags**: #newman #gws #contacts #crm
**Created**: 2026-07-03
**Source**: macbook session 25b84f6a-9035-497f-8b78-7ee215110262.jsonl, user jesus

---

## Content
- Set up gws OAuth for jesus@newman.re; user created GCP project "NewmanProject" (number 300495138622, ID `newmanproject-501314`) and dropped the credentials JSON in Downloads.
- Cleaned the Intersolar exhibitors CSV on the mac mini and uploaded 2,634 contacts to Google Contacts, tagged with 12 sector labels.
- Enrichment jobs on the mini: company descriptions filled (~83%) and 131 Trustpilot scores stamped into notes.
- Pushed the full set to the newman.re Domain Shared Contacts directory — visible to mario@ and jonathan@ via contacts.google.com Directory tab, Gmail autocomplete, mobile app; up to 24h propagation; requires admin "Enable contact sharing" setting.
- Alternative sharing options documented: label-sharing of "Intersolar 2026" (recommended) vs API push via domain-wide delegation (creates unsynced copies).
- Loose ends: delete unused GCP project `newman-gws-cli`; richer review scores via Google Places (~$90, needs billing) or free LinkedIn proxy.

## Related Notes
- [[2026-07-03-kfc-ppa-offer-workflow]]
