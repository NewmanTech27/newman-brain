# #105: Supabase anon key JWT committed in newman-sso login page while the sibling env template redacts the same value per charter §6

- State: OPEN
- Created: 2026-07-12T12:19:40Z  Closed: —
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/105

## Body

**Severity: p2**

`newman-sso/login/index.html:79` ships the anon key inline (`const ANON = "eyJ…"`, JWT length 208, role=anon, exp≈2036) while `newman-sso/newman-sso.env.example:1-9` redacts the identical key citing charter §6 ("secret VALUES never enter git").

The anon key is publishable by design, but the repo is internally inconsistent, and a key rotation now requires a code commit + redeploy of the login page instead of a config change.

**Fix:** template the key into `index.html` at deploy time (apply.sh already copies files), or amend the charter to explicitly exempt anon keys — one rule, applied once.
