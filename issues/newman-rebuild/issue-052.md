# #52: Vision extraction grabs the service ADDRESS instead of the razón social on some invoice formats

- State: OPEN
- Created: 2026-07-11T00:27:23Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/52

## Body

The edge extract vision prompt returns the service address (e.g. a street/colonia) as receptor_name for a cohort of invoices, instead of the account holder / razón social. Consulta needs a close-enough NOMBRE to unlock the recibo window, so these fail CONSULTA_FAILED. Commercial invoices (SA DE CV names) extract cleanly; the affected cohort has a different bill layout. Fix: tighten the vision prompt to distinguish razón social / titular from the service domicilio; and/or wire the OpenRouter name-variant fallback (issue #35/PR #36) so a near-miss name is retried with variants before giving up. Track alongside a HITL queue for the genuinely-unreadable.

## Comment by NewmanTech27 (2026-07-11T07:22:33Z)

Iteration 1 (extraction-quality loop): sharpened the vision prompt to define nombre as the razón social (company SA DE CV / S. DE R.L. / S.C. / person name) with positive+negative examples, explicitly NOT the service domicilio; added a per-invoice confidence; added a post-process address-heuristic (looksLikeAddress) that nulls a nombre that is really a street/colonia/plaza or mostly-digits with no company suffix; and a review gate needs_human_review = (no 12-digit rpu) OR (no nombre) OR (confidence<0.75). Redeployed. Re-extracted the failing Chiapas cohort: address-only invoices now correctly return nombre=null + needs_human_review=true (routed to a human) instead of leaking the address as the name and causing CONSULTA_FAILED. Remaining: residential invoices with no printed razón social can't auto-harvest (inherent → human review); measuring the review rate needs the accuracy harness. Kept open pending the committee/CTO score >=99.

## Comment by NewmanTech27 (2026-07-11T08:07:17Z)

Now MEASURED (via #55 harness): the Python ocr_identify._name_from_text address-leak is 73.7% on the labeled set — the dominant drag on the extraction score (79.6/100). Fix: adopt the looks_like_address guard in _name_from_text (drop address-like names to null + never return the NO. DE SERVICIO line), matching the edge extract fix.
