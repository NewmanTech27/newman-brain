# Invoice review UI shipped at review.newman.re + Cosecha RPU harvest table added to tuesday CRM

**Summary**: Built and deployed a human-review web UI for `pipeline.twilio` invoices (image/PDF left, extracted data right, confirm/correct CRUD) at review.newman.re, restyled it with the tuesday design, and added a /cosecha RPU-harvest monitoring page to tuesday.newman.re.

**Tags**: #newman #crm #supabase #cfe #pipeline #ui
**Created**: 2026-07-11
**Source**: mini session 09168bb8-88ff-4add-a07d-47bb07a9f2dc.jsonl, user jesus

---

## Content
- Ask: "create a UI to review the invoices that need review... left side rendering of the jpeg or pdf, right side prefilled extracted data, button data-is-correct or correction-needed and crud it manually"; deploy on the droplet under **review.newman.re**.
- Design decisions chosen by Jesus: auth gating reuses **newman-sso**; on confirm the pipeline continues (creates the downstream `pipeline.consulta` row). Twilio API token available for media fetch.
- Result live and verified end-to-end at https://review.newman.re, reading `pipeline.twilio` in Supabase; Supabase access obtained via ssh droplet-jesus when local CLI/MCP wasn't wired.
- Session continued after a context compaction (summary line embedded in transcript).
- Restyled the review app with the tuesday.newman.re design (frontend-design skill invoked); added a zoom button to the image/PDF viewer.
- Bug fixed along the way: `/api/confirm` returned 500 because `psql -c` does not interpolate `:'var'` — the confirm/reject path had never actually worked.
- New feature: **Cosecha RPU** page in the CRM (tuesday.newman.re/cosecha) — 4 stat cards (distinct RPUs, facturas, adeudo total, por revisar) + sortable/searchable table per RPU (invoice count, latest adeudo/periodo, consulta status, review flags, origin number).
- Backed by `public.crm_web_rpu_harvest()` SECURITY DEFINER function, live in prod DB; returned 13 RPUs at ship time (e.g. ETG Resorts — 8 invoices, $281,439 adeudo).
- Shipped to `dev` as a single surgical cherry-picked commit `3d254bc` (avoided 57 unrelated backend commits); deployed via GitHub Actions `redeploy-crm.sh` to the newman-crm droplet in 2m17s; `/cosecha` responds 307 → login.newman.re (SSO-gated, route compiles).

## Related Notes
- [[newman-architecture-project]]
- [[2026-07-11-tuesday-crm-redesign-board]]
- [[2026-07-12-miespacio-xml-drain-rate-limit]]
