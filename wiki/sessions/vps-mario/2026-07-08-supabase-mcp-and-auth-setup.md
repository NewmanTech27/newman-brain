# Supabase MCP + Auth Setup on the VPS

**Summary**: Recurring infrastructure work wiring the VPS Claude session into Supabase (MCP server, CLI token, OAuth) and Google Drive (gcloud) — the auth friction that gated most proposal sessions.
**Tags**: #newman #supabase #mcp #auth #gcloud #infra #vps
**Created**: 2026-07-08
**Source**: newman-vps sessions bef770af, 8178f386, 205f63ad, a56f35a2, edd8c13e, user mario

---

## Content
- **Supabase MCP** added to project config `/home/mario/.mcp.json` scoped to `project_ref` (Newman Data Warehouse `bwudgrwfwjdbvqhgbwty`); project-scoped servers need in-session approval + `/mcp` OAuth in a real terminal. Installed 2 agent skills (Supabase + Postgres Best Practices) to `~/.agents/skills/`.
- **Client data project** `ugjqqezqtnjkzxkcqujz` (dashboard) holds client RPUs; to point the session at it, register a project-scoped `supabase` MCP entry at the same name — it takes precedence, but the live connection only rebinds on `/mcp` reconnect (connections established at session start).
- Recurring auth patterns / gotchas:
  - **Supabase CLI**: automatic login fails in non-TTY / `!` runner ("Cannot use automatic login flow inside non-TTY"). Workaround = `supabase login --token sbp_...` (saved to `~/.supabase/access-token`, persists across sessions). Token format must be `sbp_...` (a double `sbp_sbp_` prefix errors).
  - **Supabase OAuth browser flow** is fragile headless — the `localhost:3118/callback?code=` step confuses users; the token method is the reliable fallback.
  - **gcloud (mario@newman.re)**: `gcloud auth login` crashes with `EOFError` under the `!` runner because it can't feed the verification code back to stdin. Token expires ~hourly; re-auth must be run directly in the user's terminal or via a held-open background login where the user pastes the `4/...` code. Use `--enable-gdrive-access` to get Drive scope.
- Two Google identities coexist: **gcloud mario@newman.re** (Drive write to client folders, supportsAllDrives) vs **MCP Drive newman.jjzo@gmail.com** (read-only sharing, can't reach client folders).
- The `dev` Supabase branch was used to hold client consumption data for calculator evaluation (a56f35a2); avoided touching `main`.
- Model-pin gotcha surfaced repeatedly: `.claude/settings.json` pins **Fable 5** per project and reasserts on restart even after a `/model` switch to Sonnet/Opus.

## Related Notes
- [[newman-warehouse-project]]
- [[newman-data-api-project]]
- [[2026-07-08-cfe-ppa-bess-engine-to-edge-functions]]
- [[newman-secrets-topology]]
