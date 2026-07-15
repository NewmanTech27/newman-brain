# #29: Verify CONSUMO period order for unverified CFE divisions (DX/Jalisco +)

- State: OPEN
- Created: 2026-07-10T14:45:44Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/29

## Body

## Deliverable
Byte-verify the CFDI CONSUMO1F/2F/3F -> base/inter/punta order for divisions still on the DEFAULT in extract.py's _CONSUMO_ORDER_BY_DIVISION, starting with DX (Jalisco), as real bills for each division become available. Confirm consumo_order_verified(division) returns true for each.

## Spec source
#18 fixed and byte-verified DW + DB, but left DX and other divisions on the default (punta,inter,base) UNVERIFIED. consumo_order_verified() flags them and the reconciliation guard (1F+2F+3F != CONSUMO_R -> raise) fails loud on any mismatch, so this is correctness-hardening, not a live bug.

## Artifact (required to close)
- [ ] A real XML per unverified division reconciling to CONSUMO_R
- [ ] consumo_order_verified() true for each verified division

## Hazards
- [ ] No client PII / real RPUs in the repo (synthetic or aggregate only)
