# Newman BESS Portfolio Master Document

**Summary**: Swept every source (Drive, Monday, CFE Brain, Gmail) to consolidate all BESS projects into one master HTML/PDF portfolio, then made it mobile-ready, re-sorted by kWh, and simplified the table.
**Tags**: #newman #bess #portfolio #monday #yazaki #report
**Created**: 2026-07-09
**Source**: newman-vps sessions 1df458d1, 1ae0f0c7, 5dc8f97e, user mario

---

## Content
- Task: single document listing every BESS project with battery size (kW/kWh) per RPU, Newman-branded.
- Sources swept: Drive proposals, all Monday boards (tuesday.newman.re), CFE Brain, Gmail. Yazaki + FibraHotel included.
- **5-tier organization** (later flattened per user request into one ungrouped list): (1) Engine-sized CFE Brain — 8 services, 38.3 MWh; (2) Proposal-sized Newman PPA/EPC — Grupo Aceites del Mayo 3,340 kWh/1,754 kW + 839 kWp PV (Navojoa), Bemis Packaging 4,300 kWh/2,160 kW (Tlaquepaque); (3) Yazaki study — 55 sites, 32.7 MWh; (4) Monday pipeline self-reported — 7 lines, unvalidated; (5) prospects TBD — 11 (Pueblo Bonito, GICSA/Arcos Bosques, Grupo Alhel/St. Regis, Kuehne & Nagel, Fibra Shop, Royal Pedregal…).
- **Data-quality find**: Monday "Proyecto" numbers on Inzentrum/Covestro/Molex (1,753.5 / 1,252.5 / 839.41) are copied straight from the Aceites del Mayo proposal template — placeholders, not real per-client sizes. Flagged.
- Final flattened list: **136 BESS projects, 129.9 MWh / 72.3 MW**, typical project ≈ 245 kWh (median; avg 955 kWh), range 10 kWh (smallest hotel meter) → 11,340 kWh (largest GEPP plant). Basis column removed; estimated prospects marked with amber `*`.
- Idempotency gotcha: the generator was parsing the 55 Yazaki rows out of the same HTML it overwrites, losing them on re-run — fixed by hardcoding the 55 rows.
- Deliverables (mario@newman.re): PDF `1sJ0frLxSxn8JWTcjqKTKP-lv7h0cEnwY` (updated in place), HTML `1pCcGvkdmogdvOdw7E6k7JGor-VfNRNGv`; local `/home/mario/bess-projects.{html,pdf}`. Made mobile-responsive (tables stack into labeled cards) and sorted largest→smallest by kWh.
- **Sharing limitation**: Drive tools authenticated as newman.jjzo@gmail.com can only *read* sharing (`get_file_permissions`) — no tool to toggle link-sharing or write into mario@newman.re's Drive. Workaround = user flips Restricted→"Anyone with the link" or a Gmail draft with attachment.

## Related Notes
- [[2026-07-12-fibrahotel-proposals]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[bess-agent-project]]
