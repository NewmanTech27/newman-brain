# Session: tuesday-inputs

Read `~/prompts/_common.md` first. Follow it exactly.

## Your service
Everything feeding **tuesday.newman.re**.

## CRITICAL — scope is unconfirmed
The string "tuesday" appears in this repo ONLY inside build artifacts at `~/newman-architecture/apps/crm-web/.next/`, never in source. Nobody has verified what `tuesday.newman.re` actually serves.

**Your Phase 0 begins by resolving this.** Do not assume it is the CRM. Determine:
- What does `tuesday.newman.re` resolve to, and what is deployed there? (DNS, the `deploy/` dir, any tunnel or CI config)
- Which source tree builds it? If it is `apps/crm-web`, say so with evidence.
- What are its "inputs"? Forms, lead capture, webhooks, `supabase/functions/lead-intake`, the auth shell, something else entirely?
- Who or what writes to it, and what validates that data on the way in?

If it turns out `tuesday.newman.re` does not exist or is dead, that is a finding. Report it and stop rather than inventing work.

## Once scoped
Assess input handling: validation, error paths, dropped submissions, observability. Can you prove a submitted input reaches storage? What happens when it does not?

Assess, write the spec, score against Part B, plan, then work.

## Spec target
`docs/specs/tuesday-inputs.md` — but ONLY after you have confirmed what tuesday.newman.re is.

## Normative sources (Part B)
- The DNS/deploy config: what is actually served
- `supabase/functions/lead-intake` contract and the tables it writes
- Supabase schema constraints + RLS on those tables
- What a dropped input costs the business — ask Jesus if you cannot evidence it

If the service turns out to be dead, write that finding instead of a spec. Do not spec a corpse.

## CHARTER OUTCOME 1 — the CRM
Read `~/prompts/CHARTER.md`.

`tuesday.newman.re` must be a state-of-the-art CRM whose pipeline syncs with **WhatsApp and email**.

**"Text" means WhatsApp text. There is no SMS channel. Two channels, not three.** Do not build SMS.

Existing pieces — verify each before trusting it:
- `supabase/functions/whatsapp-intake` (Twilio-signed; image to OCR, PDF to bulk split)
- `agents/email-intake`
- `supabase/functions/comms-dispatch`, `push-dispatch`
- `apps/crm-web` — Next.js, with an approval inbox ("the bell", commit 8c6536f)

Phase 0 still begins by proving what `tuesday.newman.re` actually serves. Everything above is a hypothesis until DNS and the deploy path confirm it.

"State of the art" is not a requirement, it is a mood. Convert it into `NRM-xx` requirements with verification methods, or it cannot be scored. If you cannot source a requirement, ASK Jesus. Do not invent one.

## You own the shared auth gate
`~/newman-sso` exists on this box. Investigate it.

The CEO reporting page `ceo.newman.re` and the `extraction.newman.re` dashboard must both sit behind **Google auth restricted to the `newman.re` domain**. Build that gate ONCE, as a reusable shell, and let the other agents mount behind it.

Domain restriction is the security control here — an `hd` claim check on the Google token, verified server-side. A client-side check is not a control. Anyone outside `newman.re` must be refused. These pages expose client RPUs, invoices, deal pricing, and margins.

**No merge to `main` until GATE 0 lands.**
