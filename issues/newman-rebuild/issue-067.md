# #67: Surface the Twilio doc URL (media_url) on pipeline.twilio + pipeline.flow

- State: CLOSED
- Created: 2026-07-11T11:35:59Z  Closed: 2026-07-12T12:28:03Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/67

## Body

Operator directive. The Twilio document URL (the invoice image/PDF MediaUrl) must be present + VISIBLE:
- pipeline.twilio already has media_url (the fetchable Twilio doc URL) + message_sid + media_sid + from_number + mime_type — confirm it's there.
- ADD media_url (and message_sid) to the pipeline.flow monitoring view so the doc URL is visible per invoice when monitoring the cascade (the old twilio.pipeline view only exposed has_media boolean, not the URL).
Part of #64.

## Comment by NewmanTech27 (2026-07-12T12:28:03Z)

Closing per INT-1. Artifact: `bb03b46` (media_url on pipeline.twilio + pipeline.flow). Branch → main merge tracked in #101.
