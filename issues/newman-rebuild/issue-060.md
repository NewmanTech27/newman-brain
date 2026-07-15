# #60: Extraction deployment/packaging + main-schema completeness

- State: OPEN
- Created: 2026-07-11T07:52:16Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/60

## Body

Committee blocker (9 cites): pdfplumber/pypdfium2 lazy-imported but not packaged/version-pinned (PDF tests fail wholesale on a clean env); and on main the intake/harvest rpc_* + columns appear 'undefined' because migrations 140000-190000 are applied to the DB but their FILES aren't on main. Required: pin+package the PDF deps (flake/requirements), reconcile all applied migrations onto main so a fresh checkout matches the DB, fix the ZeroDivisionError on empty test datasets. (#49)
