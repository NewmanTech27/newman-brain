# Live intake test (Twilio RPU), cascade cutover to client.bill, golden 18/18

**Summary**: Tested the front-to-back CFE extraction live via Twilio/WhatsApp, cut the cascade read-path over to the new client.bill warehouse table (bit-exact), fixed the BESS PV-surplus charging in both engines with golden tests green, and wired an email intake gateway.
**Tags**: #newman #cfe #whatsapp #supabase #cfe-brain #intake
**Created**: 2026-07-07
**Source**: macbook session 632785b3-9c61-4f39-bacb-8ca5fc5c59f0.jsonl (Downloads dir), user jesus

---

## Content
- Verified the front-to-back CFE invoice extraction was live; test RPU 671140638635 sent to Twilio; requirement: intake must work for RPU text, PDF, or photo — contradictions between paths adapted.
- 4 parallel agent threads, all landed:
  - Cascade read-cutover: new `get_bills` public RPC (anon SECURITY DEFINER) + `run_design_v2` + `build_bills_from_bill_rows` reading `client.bill`, old invoice/invoice_field path as automatic fallback; bit-exact old-vs-new on both RPUs (86.4 kWp / 64% / irr 0.265 for 671140638635); commit `14663ad`.
  - Golden re-anchor: fixture (Grupo Posadas hotel, RPU 780881200029) recovered from Drive after being missing on disk; golden 18/18 PASS after the engine.py BESS-surplus change (safe no-op for that fixture since PV never exceeds intermedia).
  - Engine consistency: `cfe_savings/engine.py` now charges BESS from PV surplus like calc_core — both engines aligned.
  - Email gateway: launchd poller `energy.newman.email-intake` live with `cfe-intake` Gmail label → files PDF to Drive + fires intake_event driving the design→offer cascade; Gmail filter creation blocked on missing `gmail.settings.basic` scope (re-auth needed).
- Commits on `feat/offer-template`: `576557d` + `14663ad` (not pushed at session end).
- Remaining blockers: gws Gmail settings scope, sales@ production setup.

## Related Notes
- [[2026-07-04-solar-bess-sizing-agent]]
- [[2026-07-08-supabase-pipeline-pgcron]]
- [[2026-07-04-cfe-invoice-harvest-supabase]]
