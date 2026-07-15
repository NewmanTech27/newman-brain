# #44: eliminar confirm click threw → service LEFT REGISTERED (charter #7 incident)

- State: CLOSED
- Created: 2026-07-10T21:26:33Z  Closed: 2026-07-10T22:11:37Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/44

## Body

The eliminar confirm button (`btnEliminarServicio`, an UpdatePanel AJAX button) is non-clickable via CDP p.click (zero-size/out-of-viewport until the modal paints) → 'Node is either not clickable or not an Element'. The exception escaped harvest_rpu's finally, leaving RPU 999999999999 registered on the shared account (verified live: PRE census ROWS/1-service). Frozen harvest.js has a fallback the rebuild dropped: `page.click(confirm).catch(()=>evaluate .click())`. Fix: bridge `click` op falls back to a DOM .click() (fires __doPostBack). Verified: cleanup → confirmed_removed, account empty. Fixed in bridge.mjs (uncommitted → this PR).


## Comment by NewmanTech27 (2026-07-10T22:11:36Z)

Resolved in main via #47 squash (e80c98f).
