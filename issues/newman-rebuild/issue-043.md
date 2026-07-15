# #43: Census false-positive: authed EMPTY account misread as 'login bounce' (blocked every live register)

- State: CLOSED
- Created: 2026-07-10T21:26:31Z  Closed: 2026-07-10T22:11:33Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/43

## Body

Live root cause (cost the most time). `classify_census` matched `_LOGIN_BOUNCE` (`login.aspx|iniciar sesión|txtUsuario`) BEFORE the empty-account check. The authed AdministrarServicios page carries a `login.aspx` **logout** link, so a valid authed EMPTY account (lblNoRegistros + 'cerrar sesión', no txtUsuario) was thrown out as UNREADABLE 'login bounce / session expired' → register never ran. Login was working the whole time. Fix: check authed-first (cerrar sesión / administrar servicios) like the frozen gridState; a bounce only counts when NOT authed. Instrumentation proof: `_login`→AgregarServicio (cerrar=True), census page lblNoRegistros=True txtUsuario=False, yet classified UNREADABLE. Fixed in census.py (uncommitted → this PR).

## Comment by NewmanTech27 (2026-07-10T22:11:33Z)

Resolved in main via #47 squash (e80c98f).
