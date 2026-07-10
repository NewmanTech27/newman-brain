---
title: "Decision — edge-function-maximalist architecture"
service: concept
kind: decision
sources: ["newman-architecture/agents/gateway-webhook/main.py", "newman-architecture supabase edge functions (whatsapp intake, claim_media)", "migrations 014/015 (RPU-confirmation gate)", "vault/wiki/analyses/2026-07-09-crmweb-finance-ts-diverges-client-facing.md"]
verified_at: 2026-07-09
verified_against: 74809d0
confidence: verified
---

# Decision — edge-function-maximalist architecture

## The decision

Newman adopts **Supabase edge functions as the primary layer** for invoice/lead
**ingest, orchestration, webhooks, media storage, and the UI-facing surface.**
Standalone Python processes on the droplet are demoted to workers that edge
functions invoke — not the primary path.

Decided by Jesus, 2026-07-09. Rationale in his words: the Supabase UI is good.
Expanded: unified observability and logs, serverless (removes the droplet
"one reboot kills every session" fragility), unified secrets and RLS, and it
aligns with the GATE-4 native-branching environment story.

## Evidence this is already the de-facto live path

On 2026-07-09 a real invoice forwarded over WhatsApp reached the **edge-function
path** (Twilio points at it). The older `gateway-webhook` Flask app
(`agents/gateway-webhook/main.py`, Twilio → Google Drive → `intake_event`)
received **nothing** — its journal showed "No entries." So the edge path is
already where live traffic lands; the Flask gateway is a second, unused
implementation of the same channel. Consolidating onto edge ratifies reality.

## Normative constraints — do not cross these

These bind every future edge build. They are not style preferences; each one is
sourced from a defect that already happened.

1. **Edge functions MUST NOT reimplement the golden math.** `calc_core.py`
   (Python, golden-tested, peso-exact on RPU `780881200029`) is the single
   source of truth for all billing/savings/PPA math. Edge may **call** it (HTTP
   endpoint, job queue, or the worker), never re-express it in TypeScript/Deno.
   *Why:* `crm-web/lib/finance.ts` is exactly a TS reimplementation of the golden
   engine on the nice-UI side — it dropped the umbral, over-valued BESS,
   oversold savings, and on 2026-07-09 had to be frozen with three REVOKEs.
   Edge-maximalist applied to the physics manufactures more `finance.ts`.
   See [[2026-07-09-crmweb-finance-ts-diverges-client-facing]].

2. **The CFE collector CANNOT go edge.** `cfe-collector` is a headless browser
   that logs into the CFE portal and solves a captcha. Edge functions are
   short-lived Deno with no browser and hard CPU/time limits — they cannot drive
   a browser. The collector stays a droplet/container worker; edge **triggers**
   it and **stores** its results, but cannot **be** it. The authoritative bill
   fields therefore always originate from the collector, never from a forwarded
   WhatsApp image (which is used only to read the RPU + titular and archive a
   copy).

3. **Every edge function and its RPCs MUST ship with a test.** *Why:* migrations
   014/015 (the RPU-confirmation gate) shipped a `public.claim_media` type bug
   (`v_inserted` held a ROW_COUNT but was checked as boolean) with no test
   exercising it. The first real WhatsApp invoice tripped it and was **silently
   lost** (claim stuck in `processing`, every Twilio redelivery re-failing
   identically). Edge-maximalist without per-function tests mass-produces silent
   drops.

4. **Build is sequenced behind GATE 0.** Every new edge function is more prod
   surface that must live in git and migrations, and git↔prod fidelity is
   currently **5/75** (DEL-4). Building out edge functions before that is fixed
   deepens the worst number in the company. Order: canonicity ruling → clean
   git↔prod → then build edge functions, **each captured in a migration from day
   one.**

## Rejected alternative

**Keep the standalone Python agents on the droplet (`gateway-webhook` Flask,
etc.) as the primary ingest/orchestration layer.** Rejected for: droplet-process
fragility (a reboot kills every agent session), weaker observability, and split
secret management. Retained **only** for the collector (constraint 2), which edge
cannot replace.

## What edge should own vs. what stays a worker

| Edge functions own | Stays a droplet/container worker |
|---|---|
| WhatsApp + email intake webhooks | `cfe-collector` (browser + captcha) |
| media storage (Supabase Storage) | the golden Python engine (`calc_core`), invoked not reimplemented |
| `collection_request` orchestration + status | any long-running OCR/PDF work exceeding edge time limits |
| the read/render UI surface | |

## Related

- [[2026-07-09-crmweb-finance-ts-diverges-client-facing]] — the reimplementation trap, live
- [[cleanroom-sizing-diverges-verified]] — the same trap in `design-engine/sizing.py`
- [[2026-07-09-crmweb-client-facing-freeze-gates-decision]] — the freeze this constraint set exists to prevent repeating
