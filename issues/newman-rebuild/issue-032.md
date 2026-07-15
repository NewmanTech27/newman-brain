# #32: Server-side Google hd-claim auth gate for internal *.newman.re pages (replace email-suffix)

- State: OPEN
- Created: 2026-07-10T14:50:12Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/32

## Body

## Deliverable
The `*.newman.re` gate verifies the Google **hd** domain claim **server-side**, replacing `~/newman-sso/validator.py:44-49`'s `email.endswith('@newman.re')` suffix match; fails closed; `login.newman.re` CNAME created.

## Spec source
Charter (hd verified server-side, not client-side / not suffix); #11 (newman-sso scaffold captured); flagged again by #8 (DEALS) as a deploy precondition.

## Scope
Required BEFORE any INTERNAL page exposing client RPUs / invoices / margins deploys — ceo.newman.re, extraction.newman.re, the salesman CRM. An under-authenticated deploy of those is a P0.
OUT of scope: the DEALS `/p/[token]` public offer link is anon-by-design (floor-cleared published snapshot only, 256-bit token) — correct as-is.

## Artifact (required to close)
- [ ] validator verifies the Google `hd` claim server-side; a non-hd / wrong-domain token is rejected (test)
- [ ] login.newman.re serves; fails closed on error

## Hazards
- [ ] No secret values in repo/logs
