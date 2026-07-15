# #115: Twilio media retention: sync can only pull the current window (36 inbound media msgs)

- State: OPEN
- Created: 2026-07-12T17:44:29Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/115

## Body

## Observation
Suspected >37 invoices, but the Twilio API currently returns **36 inbound messages with media** (single page, complete for the account). The pipeline holds 37 twilio rows — i.e. it already captured everything Twilio still has.

Twilio **purges message bodies/media after its retention window**, so invoices sent months ago are gone from Twilio's side and cannot be re-synced.

## Options to not lose future invoices
- Copy media to durable storage (Drive / a bucket) at sync time, so the source of truth isn't Twilio's retention window.
- Or extend Twilio retention on the account if the plan allows.
Track whichever we want; today's sync is complete relative to what Twilio retains.
