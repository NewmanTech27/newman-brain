# #173: calculo P9: offer consumer — expose design.current_offer (review UI / Monday / solucion-deck)

- State: OPEN
- Created: 2026-07-15T08:47:09Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/173

## Body

Offers exist on prod but nothing consumes them. Decision needed (CEO/sales): where do offers surface?
Options, not exclusive:
1. review.newman.re section (existing SECURITY DEFINER RPC pattern, newman-sso gated) — read-only offer cards per client
2. Monday sync — offer columns on the deal item (CRM Redesign board conventions)
3. /solucion-deck + /cfe-proposal input — skill reads current_offer instead of re-running the engine locally

Prereq for any: a read RPC (`rpc_current_offers(client_id?)`) exposing the typed headline + assumptions tier — NEVER raw engine blobs to anon.
Blocked on: product decision. Effort after decision: 0.5-1d for RPC + first consumer.
