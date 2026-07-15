# Tuesday CRM — environments & promotion flow (2026-07-15)

Three web environments for the Tuesday CRM (`apps/crm-web` in
NewmanTech27/newman-architecture), each pinned to its own Supabase branch.

| Env | URL | Git branch | Host | Supabase |
|---|---|---|---|---|
| dev | https://dev-tuesday.newman.re | `develop` | newman-crm-nonprod droplet, :3001 | branch `dev` (`crmrhsvsowjdnjmjbley`) |
| staging | https://staging-tuesday.newman.re | `staging` | newman-crm-nonprod droplet, :3002 | branch `staging` (`ytknnpxeyikttzyboysz`) |
| prod | https://tuesday.newman.re | `dev` (historical name!) | newman-crm droplet, :3000 | parent (`bwudgrwfwjdbvqhgbwty`) |

## newman-crm-nonprod droplet

- DigitalOcean nyc1, `s-1vcpu-2gb` (~$12/mo), Ubuntu 24.04, Node 22, **2G swapfile**
  (`/swapfile`, in fstab — without it `npm ci`/`next build` gets OOM-killed on 2GB).
- IP **137.184.19.31** — SSH as `root`/`deploy` with Vault
  `secret/synaptiq/backend:CRM_NONPROD_SSH_KEY` (this replaces the destroyed
  67.207.89.80 box; new box uses a cloudflared tunnel, not Caddy).
- Clones: `/opt/newman-architecture-dev` (develop) and `-staging` (staging);
  systemd `newman-crm-dev` / `newman-crm-staging`; env files
  `/etc/newman-crm-{dev,staging}.env` (640 root:deploy).
- Dedicated cloudflared tunnel `newman-crm-nonprod`
  (`61575e50-97f8-4948-b864-2d971ef77bab`): dev-tuesday→:3001,
  staging-tuesday→:3002. CNAMEs created via `tunnel route dns`.
- Repo access: read-only deploy key `crm-nonprod-read`.

## CD

Push to `develop` / `staging` touching `apps/crm-web/**` triggers
`.github/workflows/deploy-crm-dev.yml` / `deploy-crm-staging.yml` (mirrors prod
`deploy-crm.yml`; secrets `CRM_NONPROD_HOST`=deploy@137.184.19.31 and
`CRM_NONPROD_SSH_KEY`). Workflows exist on `main`, `dev`, `develop`, `staging`.

## Promotion flow

feature → PR into **develop** (auto-deploys dev env, dev DB branch) → PR into
**staging** (staging env + DB) → PR into **dev** (= PROD, tuesday.newman.re).
Supabase schema follows the same path: branch dev → staging → parent
(`merge_branch`).

## Auth status

Google provider was enabled on both Supabase branches via the management API,
reusing the prod Google client; site_url/uri_allow_list already point at the
*-tuesday hostnames. **Blocker:** the GCP OAuth client
(`300495138622-f2fsvi9lbg03isjnd89t2nobq8t3ksph`) needs the branch callbacks
added as Authorized redirect URIs in the GCP console (no API for this):

- https://crmrhsvsowjdnjmjbley.supabase.co/auth/v1/callback
- https://ytknnpxeyikttzyboysz.supabase.co/auth/v1/callback

Until then Google sign-in on dev/staging returns `redirect_uri_mismatch`. Both
nonprod apps host their own `/login` (NEXT_PUBLIC_LOGIN_URL unset — no shared
SSO cookie with prod).

`REVIEW_PG_CONN` is intentionally unset on nonprod — `/review` shows its
"not configured" card.

Full runbook: `deploy/crm-web-nonprod/README.md` in the repo.
