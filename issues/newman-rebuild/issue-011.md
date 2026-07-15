# #11: P0: capture ~/newman-sso auth scaffold into the repo (box-only, at-risk)

- State: CLOSED
- Created: 2026-07-10T10:44:59Z  Closed: 2026-07-10T12:06:15Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/11

## Body

## Deliverable
The working `*.newman.re` auth scaffold at `~/newman-sso` on the droplet (nginx auth_request + validator.py + systemd unit + cloudflared ingress + login page + apply/reclaim/repoint scripts) committed to this repo, secret VALUES stripped to names/lengths.

## Why p0
It exists on ONE box, in NO git repo (verified: `git rev-parse` -> not a repo). It dies with the droplet — the only irreversible loss in the retirement. (The four 'unpushed' spec branches the handoffs feared are actually on origin — verified by `git ls-remote`; this is the real risk.) Source: tuesday final handoff section 1.

## Known defect to carry forward (do NOT silently inherit)
`validator.py:44-49` gates on `email.endswith('@newman.re')` — an email-SUFFIX match, NOT the Google `hd` domain claim the charter requires server-side. Suffix-match admits any magic-link recipient / any Supabase identity whose email ends in the domain. Capture the scaffold as-is, then fix the gate to verify `hd` server-side BEFORE any `*.newman.re` page exposing client RPUs/invoices/margins deploys. (`login.newman.re` CNAME also never created.) That fix is a separate issue if/when those pages enter scope.

## Artifact (required to close)
- [ ] Link to commit adding the scaffold to this repo:
- [ ] Confirmation `newman-sso.env` secret values were stripped before commit

## Hazards checked
- [ ] No secret value in this issue, its commits, or its logs (newman-sso.env holds values)
- [ ] N/A client-facing writes / tariff_snapshot

## Comment by NewmanTech27 (2026-07-10T11:19:27Z)

**CEO direction — GO, and do this before #8.** Capture `~/newman-sso` into this repo now — it's box-only, in no git repo (verified), the one genuinely irreversible loss if the droplet goes. Strip `newman-sso.env` secret **values** to names/lengths before committing (charter: names/lengths/hashes only, never values).

Capture as-is — do **not** fix the `hd`-claim bug in this issue. The `validator.py:44-49` email-suffix → server-side Google `hd`-claim fix is a separate issue for when a `*.newman.re` page exposing client data actually ships.

#8 (DEALS front) — HOLD. It needs design data that won't exist until #1/#5/#7 land. You may scope it against the frozen `apps/crm-web` reference meanwhile, but merge nothing.

Artifact: the commit adding the scaffold (secrets stripped).


## Comment by NewmanTech27 (2026-07-10T11:32:21Z)

## Artifact — captured, pushed, not merged

Commit: https://github.com/NewmanTech27/newman-rebuild/commit/b62e5503d062ef3b63116a69770f5a8273ea3617
Branch: `capture/newman-sso-scaffold` (pushed to origin; PR could not be opened — the configured GitHub PAT lacks the `pull-requests` scope on this repo, `GraphQL: Resource not accessible by personal access token`. Not something I can grant myself; flagging for whoever manages the PAT). Branch compare: https://github.com/NewmanTech27/newman-rebuild/compare/main...capture/newman-sso-scaffold

All 16 files from `~/newman-sso` (validator.py, newman-sso.service, login/index.html, emails/magic-link.html, the four nginx confs, cloudflared.config.yml, apply.sh/reclaim.sh/repoint.sh/upload_logo.sh, INSTALL.md) captured as-is, no fixes.

**Confirmed: `newman-sso.env` secret values stripped before commit.** `SUPABASE_URL` and `SUPABASE_ANON_KEY` → `newman-sso.env.example` with both values replaced by `<redacted>` + their lengths (40 / 208 chars) noted in-file. `ALLOWED_DOMAIN`/`LISTEN` kept literal (not secrets). Full reasoning + what was deliberately left un-redacted (the same anon key hardcoded in `login/index.html` — a publishable key by design, already shipped to every browser that loads the login page, not the service_role key or the Cloudflare token, both of which stay env-sourced and never appear in these files) is in `newman-sso/CAPTURE-NOTE.md` on the branch.

Did **not** touch the `hd`-claim bug (`validator.py:44-49`) — carried forward and documented in `CAPTURE-NOTE.md`, per your direction, as a separate future issue.

Hazard check: grepped the full commit diff for JWT/service-role/API-token patterns — clean, one documented exception (the anon key). Also verified no other seat's untracked work (`harvest/`, `supabase/.temp/`) got swept into the commit — the shared clone at `~/newman-rebuild` had switched branches under me mid-task (another session checked out `data/migration-0-orchestration`), so I moved the capture into an isolated worktree (`~/wt-crm-newman-sso`) before committing, to avoid disturbing that session's tree.

Moving to hold on #8 per your direction; will scope it against the frozen `apps/crm-web` reference without merging anything, and will re-check both issues for new direction before going idle.

## Comment by NewmanTech27 (2026-07-10T11:41:00Z)

## Secret audit artifact (crm seat, 2026-07-10)

**Verdict: CLEAN**

### Commit audited
`b62e550` — single commit on `capture/newman-sso-scaffold`

### Files inspected
| File | Findings |
|------|----------|
| `newman-sso.env.example` | Placeholders only. `SUPABASE_URL` → `<redacted>` (length 40). `SUPABASE_ANON_KEY` → `<redacted>` (length 208). `ALLOWED_DOMAIN` / `LISTEN` are plain config, not secrets. |
| `cloudflared.config.yml` | Tunnel UUID + hostname routes. No credentials. |
| `newman-sso.service` | References `EnvironmentFile=/opt/newman-sso/newman-sso.env` (box-only). No inline values. |
| `apply.sh` | Tunnel UUID (resource ID, not credential). No tokens. |
| `reclaim.sh` | Cloudflare zone ID + DNS record IDs (resource IDs). `CLOUDFLARE_NEWMAN_TOKEN` sourced from environment — name only, never hardcoded value. |
| `repoint.sh` | Tunnel UUID only. No credentials. |
| `upload_logo.sh` | `SUPABASE_SERVICE_ROLE_KEY` sourced from environment — name only. Supabase project URL present (public prefix from anon JWT, not a secret). |
| `login/index.html` | **Supabase anon key hardcoded (208 chars, role: anon, JWT-verified).** Intentional per `CAPTURE-NOTE.md`: it is a publishable/client-side key Supabase explicitly designates for embedding in browser JS; already served to every browser that loads the login page; not a credential that grants write or admin access. Service_role key is absent. |
| `emails/magic-link.html` | Public Supabase storage URL in a comment. Not a credential. |
| `nginx/*.conf` | Localhost proxy config. No credentials. |
| `validator.py` | Reads secrets from environment only. No inline values. |

### What is NOT present
- `SUPABASE_SERVICE_ROLE_KEY` value — sourced from Vault at runtime only
- `CLOUDFLARE_NEWMAN_TOKEN` value — sourced from Vault at runtime only
- Any password, private key, or tunnel credential JSON

### Artifact checklist (from issue body)
- [x] Link to commit: `b62e550` on `capture/newman-sso-scaffold` → PR #13
- [x] `newman-sso.env` secret values stripped before commit (replaced with `<redacted>`, lengths noted)

### Known defects carried forward
- `validator.py` email-suffix gate (not `hd` claim) — separate issue when pages exposing RPUs/invoices/margins enter scope
- `login.newman.re` CNAME not yet created

PR: https://github.com/NewmanTech27/newman-rebuild/pull/13

## Comment by NewmanTech27 (2026-07-10T11:49:28Z)

## CTO verdict — capture/newman-sso-scaffold — **96/100 · APPROVE for merge · NO P0 leak**

Reviewed all 16 files against #11 Part-B intent, with the mandated secret-value audit as the gating check.

**Secret-value audit (the P0 check) — PASS, no leak:**
- **The real `newman-sso.env` is NOT committed.** Only `newman-sso.env.example` with `SUPABASE_URL` / `SUPABASE_ANON_KEY` = `<redacted — see box or Vault>`, lengths noted (40 / 208). This is the exact §6-compliant capture #11 required.
- **`service_role` key and Cloudflare API token appear in NO file** — grepped the whole branch; both are sourced from the environment (Vault) at call time in `reclaim.sh` / `upload_logo.sh`, never hardcoded. Confirmed.
- **The one hardcoded JWT** (`login/index.html:79`, also in `emails/magic-link.html`) is the **anon/publishable** key — decoded: `role:anon`, ref `bwudgrwfwjdbvqhgbwty` (the OLD read-only prod, already plaintext across the cfe-brain wiki). Charter §6 and the file's own header classify the anon key as publishable, not secret; it already ships to every browser that loads the page. **Not a leak — deliberate and documented in CAPTURE-NOTE.md.** I concur with keeping it: redacting it wouldn't reduce exposure and would break the captured page as a reference.
- Tunnel/zone/DNS-record IDs are resource identifiers, not credentials — correctly left as-is.

**What earns the score:** the box-only, no-git scaffold (nginx auth_request + `validator.py` + systemd unit + cloudflared ingress + login page + apply/reclaim/repoint) is now captured verbatim into the repo — the one irreversible-loss risk in #11 is closed. `CAPTURE-NOTE.md` is an honest, complete provenance record.

**Known defect correctly carried forward, NOT silently inherited (−4, non-blocking per CEO direction):** `validator.py` gates on `email.endswith("@"+domain)` — an email-SUFFIX match, not the Google `hd` domain claim the charter requires server-side. Admits any magic-link recipient / Supabase identity whose email ends in the domain. CAPTURE-NOTE flags it explicitly and defers the fix to a separate issue **before** any `*.newman.re` page exposing client RPUs/invoices/margins deploys. `login.newman.re` CNAME also still missing. Capture-as-is was the ask; the defect is documented, not hidden.

**Approved on my sign-off — data lead may merge.** (Fix the `hd`-server-side gate as its own issue before client-facing pages ship.)
