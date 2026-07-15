# #94: CI runs zero harvest tests: 15 pytest files (~3.4k lines) have no workflow; migrations also unvalidated in CI

- State: OPEN
- Created: 2026-07-12T10:13:33Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/94

## Body

## Problem

The only committed workflow is `.github/workflows/golden.yml`, which covers the ENGINE path (golden peso-reconcile + `engine/test/*.test.mjs`). Nothing in CI runs the harvest suite:

- `harvest/test_*.py` — 15 files, ~3,400 lines, covering the load-bearing gates: barcode decode (`test_barcode_identify.py`), census tri-state (`test_census_authed.py`, `test_issue19.py`), leak prevention F1/F2/F3 (`test_drive_leak_prevented.py`), pipeline endpoint orchestration (`test_pipeline_endpoint.py`, 19 tests), recibo reconciliation (`test_recibo_parser.py`, `test_harvest_service.py`), dedup (`test_dedup.py`), intake worker (`test_intake_worker.py`).
- These run only when someone remembers to run pytest in the Nix devshell locally. PR #88 (multi-invoice fan-out) merges on green golden CI even if `extract_all`/fan-out tests are red.

Migrations are equally ungated: no workflow does even a syntax/apply check (`supabase db start` + apply, or apply against a preview branch) before SQL reaches an environment.

## Fix

Add a `harvest-tests` workflow:
1. Trigger on PRs touching `harvest/**` or `supabase/migrations/**`.
2. Run pytest (the suite is designed offline — fakes/subprocess stubs; no live CFE, no secrets needed). Either via the repo's `harvest/flake.nix` devshell (`nix develop -c pytest`) or a pip install of the few deps (pyzbar/pdf2image/pdfplumber need system zbar/poppler — the flake already encodes this).
3. Separate job: apply `supabase/migrations/*.sql` to a throwaway Postgres (supabase CLI local db) so a broken migration fails the PR, not staging.
4. Mark both required checks on the default branch alongside `golden`.

Blocked-by/related: the migration job is only meaningful once #90 (ledger drift) makes the repo migrations authoritative.
