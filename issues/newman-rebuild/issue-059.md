# #59: Fix XML CONSUMO1F/2F/3F division-code ordering (inverted for DW/Peninsular)

- State: OPEN
- Created: 2026-07-11T07:52:14Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/59

## Body

Committee major (11 cites), CTO-verified in test_recibo_parser.py: the CONSUMO1F=base/2F=inter/3F=punta mapping is division-code-dependent and inverted for non-Peninsular divisions (DW/DB); the test currently EXPECTS failure and the XML path is documented untrusted → base/inter/punta mis-classified for a share of commercial accounts. Fix the division-keyed ordering, remove the expect-fail assertion, cross-validate across >=3 divisions. (#49)

## Comment by NewmanTech27 (2026-07-11T08:25:34Z)

Fixed on branch extraction/quality (28e712e): recibo_parser now RE-EXPORTS the golden engine's authoritative division-keyed CONSUMO ordering (cfe_savings.extract._consumo_order, _STD=(punta,inter,base), DW+DB byte-verified) — no fork (harvest must not re-derive parsing). Removed the expect-fail assertion; XML canonical cross-check now a hard gate (5/5 pass). New test_consumo_ordering.py cross-validates >=3 divisions (DW/DB/DGO/DX) on synthetic CFDI, runnable without pdfplumber. 6/6 pass.
