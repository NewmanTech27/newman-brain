# #121: Deep-drain capture gap: 92 grid rows → 81 XML (missing Feb-2026 invoice on 053200453456)

- State: OPEN
- Created: 2026-07-13T00:20:35Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/121

## Body

On RPU 053200453456 the OtrasFacturas grid reports `grid_rows=92` but the incognito session-cycle drain (PR #120) captured 81 XML. The 29 real invoices (`TipoDeComprobante=I`) cover Feb 2024 → Jul 2026 **except Feb 2026** (periods jump 2026-01 → 2026-03).

Need to determine whether the 11-row shortfall is:
- non-XML grid rows (some pago rows may lack a downloadable factura), or
- genuine per-row download misses inside a batch (e.g. a slow click that never landed and wasn't retried — the incognito drain intentionally does NOT retry in-session to avoid the 5th-request popup), or
- the Feb-2026 factura simply absent from CFE.

Proposed: log per-row (grid index → captured/absent) during the drain so the shortfall is attributable, and add a bounded cross-session retry for rows that produced no file.
