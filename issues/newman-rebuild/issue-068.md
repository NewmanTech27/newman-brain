# #68: Seed pipeline.twilio from the Twilio log (23 media records)

- State: CLOSED
- Created: 2026-07-11T11:54:28Z  Closed: 2026-07-12T12:28:06Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/68

## Body

Operator directive: fill pipeline.twilio with the Twilio log data. DONE — migrated the Twilio media already captured in intake.upload into pipeline.twilio: 23 distinct media rows (message_sid + media_sid parsed from the Twilio MediaUrl, media_url = the doc URL, from_number, mime_type), all status=received, rpu=null → awaiting the /pipeline/extract executor (barcode RPU + OCR receptor_name, #63 contract). Also added public.rpc_enqueue_twilio(message_sid, media_sid, media_url, from_number, mime_type) — dedup on media_sid — for the twilio-sync edge fn to enqueue directly into pipeline.twilio going forward (edge fn re-point + redeploy still TODO). Part of #64.

## Comment by NewmanTech27 (2026-07-12T12:28:05Z)

Closing per INT-1. Artifact: `6338c80` — 23 Twilio media records seeded into pipeline.twilio; edge repoint completed via #73. Branch → main merge tracked in #101.
