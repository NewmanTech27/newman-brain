# #48: Charter scrub: rule on pre-existing Chiapas client RPUs in already-merged harvest files

- State: OPEN
- Created: 2026-07-10T22:04:50Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/48

## Body

CTO flagged during the #47 re-gate: real-looking Chiapas RPUs **679220758161** and **671140638635** appear across ~13 already-merged files (test_issue19, barcode_identify, recibo_parser, doc_taxonomy, test_drive_adapter, etc.), same charter-PII class as the #43 scrub. (The golden RPU **780881200029** is deliberately public per charter #3 and must be LEFT.)

Deliverable:
- [ ] Rule whether 679220758161 / 671140638635 are real client data (must scrub to synthetic) or sanctioned public test fixtures like the golden.
- [ ] If real: replace with synthetic across the merged files + scrub the #19 issue thread; do NOT touch 780881200029.
- [ ] Out of scope for / does not block #47 (those are pre-existing, not introduced by #47).
