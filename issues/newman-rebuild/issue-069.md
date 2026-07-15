# #69: pipeline.twilio media_url: stable api.twilio.com is correct; CDN URL resolved at fetch (never stored)

- State: CLOSED
- Created: 2026-07-11T12:01:59Z  Closed: 2026-07-12T12:28:08Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/69

## Body

## Context
Board flagged that `pipeline.twilio.media_url` looked "wrong" because it's the `api.twilio.com/.../Media/{ME}` form rather than the `mms.twiliocdn.com/...?Expires=&Signature=` CDN URL seen elsewhere.

## Finding (verified empirically)
The stored URL is **correct**. Resolving a stored `media_url` with Twilio Basic auth returns:
```
HTTP/1.1 307 Temporary Redirect
Location: https://mms.twiliocdn.com/AC.../{hash}?Expires=<unix>&Signature=...&Key-Pair-Id=APKAIRUDFXVKPONS3KUA
```
i.e. the api.twilio.com resource URL 307-redirects to exactly the CDN signed URL.

## Design decision
| URL | property | store? |
|---|---|---|
| `api.twilio.com/.../Media/{ME}` | stable, needs Basic auth, 307→CDN | **YES (stored)** |
| `mms.twiliocdn.com/...?Expires=&Signature=` | fetchable directly, expires in ~hours | **NO — resolve on demand** |

- `/pipeline/extract` executor fetches the stored URL with Twilio Basic auth (Vault creds) + follows the 307 → PDF bytes. No change needed.
- CDN URL is short-lived (`Expires` ~hours) → persisting it would break by the next cron tick.

## Optional follow-up
For monitoring/manual review, add a small RPC/endpoint that resolves a **fresh** signed CDN URL on demand (never persisted). Not required for the pipeline to run.

## Status
`pipeline.twilio` (23 rows) is correct as-is. No migration needed.

## Comment by NewmanTech27 (2026-07-12T12:28:07Z)

Closing as resolved decision: stable api.twilio.com URL is stored; CDN URL resolved at fetch time, never persisted. Verified empirically in issue body; enforced by the live twilio-sync enqueue (`b144171`). Branch → main merge tracked in #101.
