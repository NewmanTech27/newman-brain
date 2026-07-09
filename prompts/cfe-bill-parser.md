# Session: cfe-bill-parser

Read `~/prompts/_common.md` first. It defines the phases, the 95/100 committee bar, and the rules. Follow it exactly.

## Your service
The CFE bill ingestion pipeline, end to end:
- **WhatsApp intake** — `~/newman-architecture/supabase/functions/whatsapp-intake`
- **OCR / extraction** — image and PDF bills into structured fields
- **CFE endpoint extraction** — `~/newman-architecture/agents/cfe-collector`; harvesting invoices (CFDI XML + PDF) from CFE portals
- **Bill renaming / normalization** — `~/newman-architecture/supabase/functions/bill-rename`

## Known context, TO BE VERIFIED not assumed
- `docs/cfe-collection.md` **EXISTS on `origin/main`** (95 lines, "CFE Invoice Collection — Architecture & Hard-Won Gotchas", commit `e4c68fe`). It is **missing from `dev`, `staging`, and `crm-platform`** — you are working on `dev`, so you cannot see it in your tree. A copy is at `~/cfe-brain/raw/cfe-collection.md`. **Read it. It is your Part B.** That `main` has docs `dev` never received is itself a finding — hand it to `supabase-devops`.
- Reported gotchas from prior work, all UNVERIFIED — confirm or refute each against the code:
  - The CFE account name must match exactly (`receptor_nombre` plus legal suffix) for the Consulta flow.
  - PDF uploads get bulk-split into many individual bills.
  - There is an `ASSIGNED_ELSEWHERE` block with a Consulta full-drain fallback.
  - Captchas are solved via 2captcha; a WAF sits in front of app.cfe.mx.
  - A `>10 recibo` limit blocks bulk retrieval.
- A Supabase `pg_cron` job is said to trigger a drain on the mac mini. The mini is NOT part of this terminal setup — determine whether that dependency still exists and whether it is healthy.

## Phase 0 focus
Establish: does the pipeline currently run? What is the last bill it successfully parsed? Where does it silently fail? What is the actual extraction accuracy, and how would anyone know? Is there a single test that exercises a real bill end to end?

Assess (Phase 0), write the spec (Phase 1), score against Part B (Phase 2), plan (Phase 3), then work (Phase 4).

## Spec target
`docs/specs/cfe-bill-parser.md`

## Normative sources (Part B) — independent of the code
- CFE portal behaviour itself (what app.cfe.mx actually enforces: WAF, captcha, the >10-recibo block)
- CFDI XML schema — the SAT standard is an external contract you do not get to reinterpret
- Supabase `app.invoice` table constraints and the `invoice_check` reconciliation rules
- Arithmetic invariants that must hold on every parsed bill: multiplier applied exactly once; MEM concepts sum to total; `subtotal * 1.16 ~= total`; blended MXN/kWh derived EXCLUDING DAP and adeudos
- WhatsApp intake contract: image -> OCR, PDF -> bulk split

Each becomes an `NRM-xx` with a verification method. The arithmetic invariants above should be executable assertions, not prose.


## The vault
`~/cfe-brain/vault/` holds 91 compiled wiki pages, including `wiki/billing/` (GDMTH/GDMTO charge structure, demand logic, rates, schedules). The bill-arithmetic invariant is stated there as `(sum(importes) + bonif_FP) x 1.16` vs printed total — note it is **not** the plain `subtotal x 1.16 ~= total` I gave you earlier. **The vault wins.** Verify which is right and file a `finding` if the code implements neither.

## CHARTER OUTCOME 2 — you own `extraction.newman.re`
Read `~/prompts/CHARTER.md`.

RPU invoice extraction must work end to end AND be visible on a dashboard at `extraction.newman.re`.
You own it all: extraction backend, the dashboard, DNS, deploy.

The dashboard is downstream of a working extraction. **Do not build UI over a pipeline you have not proven.**
Prove it first: trace ONE real RPU from intake to a stored, arithmetic-checked invoice. Then build.

Minimum the dashboard shows: per-RPU coverage (months harvested vs target), what failed and why, which bills failed arithmetic validation, queue depth. The monitor view `public.rpu_coverage` already exists — start there.

Deploy pattern: `newman-landing` deploys `dev` to newman-vps via tunnel (commit 787c574, "excalidraw pattern"). Reuse it. Ask `supabase-devops` before inventing a new deploy path.

**Access control**: `extraction.newman.re` is internal. It must sit behind the same Google auth gate restricted to the `newman.re` domain as `ceo.newman.re`. See `~/newman-sso`. Coordinate with `tuesday-inputs`, who owns the auth shell. Do not ship an unauthenticated dashboard exposing client RPUs and invoices.

**No merge to `main` until GATE 0 lands.** Branch off `dev`, PR, wait for the CTO.
