# #93: twilio-sync edge function is LIVE but its source is not in the repo

- State: OPEN
- Created: 2026-07-12T10:13:14Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/93

## Body

## Problem

`twilio-sync` is deployed and live on prod — it is the intake head of the whole pipeline (#73: "twilio-sync LIVE → pipeline.twilio: automatic WhatsApp ingestion wired"). But the repo contains only one edge function:

```
supabase/functions/
└── invoice-intake/index.ts
```

No `supabase/functions/twilio-sync/` exists on any branch. The function that feeds `pipeline.twilio` every tick has no committed source, no review trail, and cannot be redeployed from git.

## Consequence

- Disaster recovery / environment parity gap: dev and staging branches cannot run the intake head from the repo; the new per-environment GitHub-Actions deploy cannot include it.
- Same drift class as the DB-side psql hot-patches (#90), but for compute: the deployed artifact is the only copy.
- Any future edit happens against the deployed version blind.

## Fix

1. `supabase functions download twilio-sync` (or recover the source from the deploy session) and commit it under `supabase/functions/twilio-sync/`.
2. Verify committed source == deployed version (redeploy from repo and confirm behavior, or diff the bundle).
3. Add it to the per-environment function deploy step in the CI/CD being wired now.

## Comment by NewmanTech27 (2026-07-12T14:53:24Z)

Partially addressed by #109: `pipeline/orchestrator` carried `supabase/functions/twilio-sync/index.ts` + `supabase/functions/extract/index.ts`, now on `main` (`b512dfa`). Remaining before close: diff these files against the DEPLOYED edge function versions (per #91's pattern the live code may have drifted — e.g. razon_social seeding). Keep open until live-diff verified.
