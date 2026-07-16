---
title: "The 58 designs are physically impossible — prod data confirms the inverted engine"
type: analysis
kind: finding
tags: [design-engine, del-5, prod-data, bess, umbral, gate0, provenance]
created: 2026-07-10
updated: 2026-07-10
sources:
  - "prod supabase bwudgrwfwjdbvqhgbwty, client.design, 58 rows, created_at 2026-07-05..2026-07-06"
  - "vault/CLAUDE.md — invariant: PV ⊥ punta; BESS is the only punta lever"
  - "golden test RPU 780881200029 — Ahorro 23.5%"
  - "journalctl -u newman-agent@design-engine.service → 'No entries' (never started on newman-vps)"
  - "systemctl: design-engine disabled/inactive; proposal-builder enabled/ACTIVE (pid 1199)"
  - "/proc/1199/environ → no PROPOSAL_RPUS (watch list empty at runtime)"
verified_against: "live prod SQL + live systemd/proc reads on newman-vps, 2026-07-10, re-run first-hand"
confidence: high
---

# The 58 designs are physically impossible

Companion to [[design-engine-live-or-orphan]], which established the code trace.
That page reasons from **source**. This one reasons from **production data** and
**live process state**, arrived at independently. They agree, which is why this
is worth keeping.

## 1. The output violates the vault's own physics

Aggregated from `client.design` (no RPU or client identifier extracted):

| cohort | n | avg savings_pct | max savings_pct | roof_bound |
|---|---|---|---|---|
| PV only (`bess_kwh = 0`) | 30 | **62.0 %** | 81.0 % | 0 |
| PV + BESS (`bess_kwh > 0`) | 28 | **55.2 %** | 74.0 % | 0 |

The vault holds PV ⊥ punta: solar does not coincide with the punta window
(SIN 20:00–22:00 summer, 18:00–22:00 winter), so PV cannot cut the demand
charge. BESS is the only lever on it. Adding a battery can therefore only
*raise* modelled savings, or leave them flat. **It can never lower them.**

Production says the opposite: the cohort **without** a battery reports savings
**6.8 points higher** than the cohort with one.

Two corroborating anomalies:

1. **Magnitude.** The golden test's answer for RPU `780881200029` is 23.5 %.
   These designs claim 55–81 %. 55 of 58 exceed 40 %.
2. **`roof_bound` is false on all 58.** Across 58 real sites the roof-area cap
   never once binds. `kwp_roof_max` is computed and then not applied. An
   unbounded array inflates `annual_pv_kwh` → inflates savings → consistent
   with anomaly 1.

By `reconciled`: 54 false / 4 true. The bill-arithmetic check
`(Σ importes + bonif_FP) × 1.16` was never run against 54 of them.

## 2. But design-engine has never run on this box

```
systemctl is-enabled newman-agent@design-engine  → disabled
systemctl is-active  newman-agent@design-engine  → inactive
journalctl -u newman-agent@design-engine         → -- No entries --
```

Never started. Not once. **So the 58 designs were not written by the deployed
service.** Their provenance is unaccounted for — most plausibly a manual run
(mario's `tools/optimize_sizing.py`, or an ad-hoc script) on 2026-07-05/06.

This does not soften the finding. It sharpens it: the rows exist, they are
wrong, and **nothing in the deployment graph explains how they got there.**
An unexplained writer to a client-facing table is its own problem.

**Open question, not answered here:** who wrote `client.design`?

## 3. The real hazard is proposal-builder, not design-engine

| unit | enabled | active |
|---|---|---|
| design-engine | disabled | inactive |
| **proposal-builder** | **enabled** | **active (pid 1199)** |
| intake-worker | enabled | active |
| gateway-webhook | enabled | active |

`proposal-builder` polls `get_latest_design(rpu)` for every RPU in
`PROPOSAL_RPUS`, fingerprints it, and **builds + notifies** on change
(`main.py:249-255`). It is running now.

Its only brake is that `PROPOSAL_RPUS` is unset. Verified first-hand at runtime:
`/proc/1199/environ` contains no `PROPOSAL_RPUS`, so `_csv()` yields an empty
list and the loop body never executes.

**So the gate between 58 impossible designs and a client's inbox is one unset
environment variable on a running process.** Not a code path, not a review, not
a feature flag with an audit trail. One env var. Anyone who sets it to ship a
proposal — a reasonable-looking action — fires notifications built on wrong
physics.

`client.refresh_pipeline_stages()` (pg_cron `solar-bess-promote`, every 5 min)
promotes `collected → verified` on invoice counts, not on designs, and
`client.invoice = 0`. That path is inert. It is not the exposure.

## 4. Correction to an earlier reading

An earlier pass by this session flagged `TEAM_ALLOWLIST` in
`gateway-webhook/main.py:40` ("empty list means allow everyone") as an inverted
safety gate. That is true of *that* variable, but it is **not** the allowlist
the DEL-5 assessment rests on. That one is `PROPOSAL_RPUS`, where empty is
correctly restrictive.

Two different gates, opposite emptiness semantics, in the same codebase. That
is itself a defect worth naming: `TEAM_ALLOWLIST=""` admits every WhatsApp
sender; `PROPOSAL_RPUS=""` admits none. A reader who learns one learns the
wrong lesson about the other.

The webhook is nonetheless authenticated: Twilio HMAC-SHA1 is verified before
any work and returns 403 (`main.py:88`). `ufw` allows only OpenSSH, though the
cloudflared tunnel (`wa.newman.re → localhost:8080`) bypasses ufw by design, so
the HMAC is the control that matters, and it is present.

## 5. Recommended, not executed

1. **Do not delete or mutate the 58 rows.** They are the only evidence of what
   the engine did. Quarantine by flag.
2. **Answer the provenance question** before repairing anything.
3. Treat `PROPOSAL_RPUS` as a safety interlock: document it, and make
   `proposal-builder` refuse to build from a design with `reconciled = false`.
   A brake that works by omission is not a brake.
4. Re-run the golden RPU through `sizing.py` and diff against `calc_core`.

Nothing here justifies a prod write. This is a finding.

Relates to [[design-engine-live-or-orphan]], [[cleanroom-sizing-diverges-verified]],
[[the-58-designs]], [[tonight-sizing-fix]].
