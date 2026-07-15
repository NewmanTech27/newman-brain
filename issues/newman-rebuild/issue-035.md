# #35: OpenRouter name-variant fallback for MiEspacio AgregarServicio name-mismatch

- State: OPEN
- Created: 2026-07-10T15:56:51Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/35

## Body

## Deliverable
When MiEspacio AgregarServicio rejects ALL deterministic name candidates (CFE 'El no coincide'), call OpenRouter with the razón social + the already-failed forms to propose additional plausible registered-titular variants (drop corporate suffix S.A. DE C.V., abbreviations, commercial/short name, CFDI <NOMBRE> style, accent/spacing variants), and retry each. Integrate with name_match's candidate flow; record which form finally matched.

## Spec source
Jesus directive + #19.3: CFE validates against the registered titular, which differs from the full razón social — 'El no coincide' is common, and deterministic candidates alone miss it.

## Constraints
- BOUNDED retries (max N variants) and PACED (respect the CoolDownPacer / WAF pressure); never exceed the account's ≤10-service permaban ceiling.
- OpenRouter key already set; the generator is deterministic-first, LLM-fallback (only call the API on mismatch, not every RPU).
- A matched form should be cached back so the same client isn't re-LLM'd next time.

## Artifact (required to close)
- [ ] name-variant generator (razón social + failed forms -> ordered variants) with a test
- [ ] wired into the drive-loop AgregarServicio retry (on 'El no coincide'), bounded + paced
- [ ] a matched-form log line (no PII values in repo/logs — aggregate/first-4 only)

## Hazards
- [ ] No client name values committed to repo/logs

## Comment by NewmanTech27 (2026-07-10T16:03:08Z)

## Generator + interface delivered — PR #36 (stacked on #34)

**`harvest/name_variants.py`** implements the deterministic-first, LLM-fallback name-variant generator + a paced resolver interface for the drive-loop seat.

**Generator:** `openrouter_name_variants(razon_social, failed_forms, max_n) -> [ordered variants]`
- Deterministic first (suffix-drop / accent-fold / spacing) — **the OpenRouter call fires only when the deterministic set minus already-failed forms is exhausted**, so most RPUs never spend a token.
- Bounded by `max_n`, de-duped, excludes failed forms.

**Paced interface (for #33, the drive-loop AgregarServicio flow — I did NOT edit that file):** `NameVariantResolver`
- `ready(account, ip)` gates on the shared **`CoolDownPacer`**; `next_variants(...)` marks it → mismatch retries are rate-limited (no WAF burst, never toward the ≤10-service permaban ceiling).
- `record_match()` / `cached_match()` cache the matched form (keyed by a **hash**, not the value) so the same client isn't re-LLM'd.
- Exact call contract documented in the resolver docstring for clean wiring.

**PII (charter #6):** `name_tag()` = `first4…len=N#sha1prefix`; every log line uses it. No razón social value is logged or persisted. Confirmed no client names in repo/logs.

**Test:** `harvest/test_name_variants.py` **13/13** — deterministic-first (no API while det available), LLM-only-when-exhausted, `max_n` bounding, failed-form exclusion, pacing per `(account,ip)`, caching + cache-skip-on-prior-fail, PII-safe tags. Opt-in real-call smoke via `OPENROUTER_NAME_SMOKE=1`.

Artifact checklist:
- [x] name-variant generator (razón social + failed forms → ordered variants) with a test
- [ ] wired into the drive-loop AgregarServicio retry — **left to the drive-loop seat (#33)**; interface + contract ready
- [x] matched-form log line, PII-safe (tag/hash only)

Do NOT merge — CTO ≥95.
